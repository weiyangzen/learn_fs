# subset-b-005014 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/rcec.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/rcec.c

## Purpose
This file implements PCIe Root Complex Event Collector (RCEC) discovery and association support. It records the RCEC extended capability data on RCEC devices, links associated Root Complex Integrated Endpoints (RCiEPs) back to their collector, and provides a walker so error handling code can visit the RCiEPs associated with a collector.

## Important APIs, types, and functions
`struct walk_rcec_data` carries the RCEC device, a user callback, and user data through `pci_walk_bus()`. `pci_rcec_init()` allocates and fills `dev->rcec_ea` from the RCEC extended capability. `pci_rcec_exit()` releases that per-device allocation. `pcie_link_rcec()` assigns `rciep->rcec` for matching integrated endpoints. `pcie_walk_rcec()` exposes the association walk to callers such as AER/RCEC error paths. `rcec_assoc_rciep()` is the core matching helper: same-bus endpoints are matched against the RCiEP bitmap and endpoints on other buses are accepted when they fall inside the RCEC bus-number association range.

## Control flow
Enumeration calls `pci_rcec_init()` from the PCI capability initialization path after a device has been identified. The function exits unless the device is a PCIe RCEC and advertises the RCEC extended capability. It then reads `PCI_RCEC_RCIEP_BITMAP`, optionally reads the RCEC BUSN register when the capability version supports it, and stores that data in `dev->rcec_ea`. Association walks first scan the RCEC's own bus for bitmap matches, then scan each bus in the advertised `nextbusn..lastbusn` range, skipping the RCEC's own bus because that path is bitmap-based.

## State and persistence
The only persistent state is kernel memory attached to `struct pci_dev`: `dev->rcec_ea` and, for matching RCiEPs, `dev->rcec`. The association is rebuilt during enumeration and cleared only when the device object is released or reinitialized; there is no disk-backed state. The code relies on PCI bus/device lists and config-space reads remaining stable during enumeration or caller-held PCI locking.

## Dependencies and integration points
The file depends on PCI core helpers (`pci_find_ext_capability()`, `pci_read_config_dword()`, `pci_walk_bus()`, `pci_find_bus()`, `pci_domain_nr()`), PCIe type decoding (`pci_pcie_type()`), and RCEC register definitions from PCI headers. It is integrated from `drivers/pci/probe.c` via `pci_rcec_init()` and `pci_rcec_exit()` and by PCIe error/reporting paths through `pcie_walk_rcec()` and the `struct pci_dev::rcec` link.

## Risks
The bus-range walk assumes the RCEC extended capability accurately describes association; malformed firmware or device data can associate too broadly for non-local buses because `rcec_assoc_rciep()` returns true for any RCiEP on a different bus once that bus is in range. Callback return values are ignored by `walk_rcec_helper()`, despite the public comment saying nonzero should break out, so callers cannot currently stop traversal early. The bitmap is copied into an `unsigned long` and walked for 32 bits, which matches device numbers but should be preserved carefully if the bitmap type changes.

## Test signals
Useful signals are boot logs showing RCiEP devices reporting "PME & error events signaled via ..." with the expected collector, AER/RCEC injection or error reporting reaching all and only associated RCiEPs, and hotplug/rescan paths not leaving stale `rcec` links. Unit-level review should exercise same-bus bitmap matches, cross-bus range matches, legacy capability versions without BUSN, empty bus ranges, and callback early-exit expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/rcec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/tlp.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/tlp.c

## Purpose
This file centralizes PCIe Transaction Layer Packet (TLP) log length calculation, config-space reads, and printk formatting for AER and DPC error reporting. It handles both conventional four-DWORD TLP header logs with optional end-to-end prefixes and newer Flit-mode logs whose length is encoded in capability registers.

## Important APIs, types, and functions
`aer_tlp_log_len()` calculates an AER header/prefix length from the AER Capabilities and Control register and `dev->eetlp_prefix_max`. `dpc_tlp_log_len()` is compiled under `CONFIG_PCIE_DPC` and derives DPC RP PIO log length from `dev->dpc_rp_log_size`, excluding the implementation-specific log register. `pcie_read_tlp_log()` reads DWORDs from header and prefix config offsets into `struct pcie_tlp_log`. `pcie_print_tlp_log()` formats the captured DWORDs for kernel logs.

## Control flow
A caller determines the log size, calls `pcie_read_tlp_log()` with the config offsets for the header and optional prefix areas, then passes the filled `struct pcie_tlp_log` to `pcie_print_tlp_log()`. The reader clamps the requested length to the destination array size, clears the log, reads the standard header first, and then switches to the second offset for prefix DWORDs. It records `header_len` as the full Flit length or four DWORDs for non-Flit mode.

## State and persistence
The file does not retain state. It consumes per-device capability state initialized elsewhere, notably `eetlp_prefix_max` and DPC log size, and writes only into caller-provided `struct pcie_tlp_log`. Output is transient kernel logging.

## Dependencies and integration points
The code depends on PCI config accessors, AER/DPC register definitions, `FIELD_GET()`, `ARRAY_SIZE()`, and the PCI core's `struct pcie_tlp_log` layout. It is used by PCIe AER and DPC paths when reporting captured request/completion headers after errors. It also depends indirectly on `probe.c` configuring E-E Prefix support so prefix length calculation reflects the path capability.

## Risks
For non-Flit mode, `pcie_read_tlp_log()` hard-codes `header_len` to four DWORDs even if the exact packet header length could be shorter; this is acknowledged in the comment and means formatting is conservative rather than parsed. `pcie_print_tlp_log()` only prints non-Flit prefixes until it reaches a zero prefix DWORD, so a valid zero-valued prefix would terminate printing. Length calculations depend on correct capability values; oversized values are clamped silently to the local buffer.

## Test signals
Exercise AER logs with no prefixes, with E-E prefixes, and with Flit-mode `PCI_ERR_CAP_TLP_LOG_FLIT`. DPC builds should validate the implementation-specific register subtraction. Fault injection should show expected DWORD order and offsets in logs, and config-read failure tests should verify `pcibios_err_to_errno()` propagation without partial stale log content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/tlp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/probe.c -->
# sources/distributed-fs/ceph-client/drivers/pci/probe.c

## Purpose
This is the PCI core enumeration and setup implementation. It allocates and registers host bridges and buses, scans devices and bridges, sizes BARs and bridge windows, initializes PCI/PCIe capabilities, configures fabric parameters such as MPS/MRRS and MSI domains, and exposes rescan/hotplug entry points.

## Important APIs, types, and functions
Global state includes `pci_root_buses`, `pci_domain_busn_res_list`, `busn_resource`, and `pci_rescan_remove_lock`. Host bridge APIs include `pci_alloc_host_bridge()`, `devm_pci_alloc_host_bridge()`, `pci_free_host_bridge()`, `pci_register_host_bridge()`, `pci_create_root_bus()`, `pci_scan_root_bus_bridge()`, `pci_scan_root_bus()`, `pci_scan_bus()`, and `pci_host_probe()`. Device and bus scanning uses `pci_alloc_dev()`, `pci_scan_single_device()`, `pci_scan_slot()`, `pci_scan_child_bus()`, `pci_scan_bridge()`, and `pci_hp_add_bridge()`. Resource decoding centers on `__pci_read_base()`, `pci_read_bases()`, bridge-window readers, and bus-number resource helpers. PCIe configuration APIs include `pcie_get_link_speed()`, `pci_speed_string()`, `pcie_update_link_speed()`, `pcie_bus_configure_settings()`, `pci_configure_extended_tags()`, and `pcie_relaxed_ordering_enabled()`.

## Control flow
Host-controller drivers allocate a `struct pci_host_bridge`, populate ops/windows/sysdata, then call `pci_host_probe()` or `pci_scan_root_bus_bridge()`. Registration creates a root `struct pci_bus`, registers the host bridge device and bus device, selects MSI domains, preserves or coalesces window resources, inserts the root bus into `pci_root_buses`, and publishes firmware node metadata. Scanning probes each slot/function by reading vendor/device ID with Retry Status handling, allocates a `pci_dev`, runs `pci_setup_device()`, and adds the device. Bridges are scanned in two passes: first respecting firmware-configured bus numbers, then assigning new numbers to broken or unconfigured bridges while distributing spare bus numbers for hotplug bridges. After scanning, resources are assigned, PCIe settings are configured below each child bus, and devices are added to the driver core.

## State and persistence
All state is in kernel objects and resource trees. Host bridges own window and DMA range lists. Buses retain bus-number resources, child/device lists, bridge resources, class devices, MSI domains, firmware-node bindings, and speed metadata. Devices retain decoded IDs, class, header type, resources, IRQs, DMA masks, capability state, flags for CXL/Thunderbolt/untrusted/removable/hotplug, and config-space size. Persistent external effects are limited to kernel device model registration, resource reservations, sysfs/procfs side effects elsewhere, and config-space writes that size BARs, configure bridges, enable features, or clear status.

## Dependencies and integration points
This file is central to the PCI subsystem. It calls architecture hooks (`pcibios_*`, `pcibios_fixup_bus()`), firmware helpers for OF and ACPI, MSI/IRQ domain selection, runtime PM, hotplug, ASPM, AER, DPC, RCEC, DOE, TPH, SR-IOV, ATS/PRI/PASID/ACS/PTM, VPD, reset method initialization, DMA configuration, and device-core registration. It also exports many APIs for host controller drivers, hotplug drivers, and architecture code. The pwrctrl drivers in this subset integrate indirectly through host-controller code that powers devices before this scan path can discover them.

## Risks
BAR sizing temporarily disables IO/MEM decode unless `mmio_always_on` is set, so ordering and "no printk while disabled" constraints matter. Bus-number assignment is sensitive to firmware bugs, EA fixed bus numbers, rescans, and overlapping bridge windows. Several feature writes occur during enumeration, including MPS, Extended Tags, Relaxed Ordering, SERR forwarding, RCB, and bridge bus numbers; regressions can break devices before drivers bind. Lifetime is delicate because device and bus objects move through manual allocation, `device_initialize()`, `device_register()`, list insertion, and release callbacks. Concurrency requires callers to hold `pci_rescan_remove_lock` for rescan/removal paths and uses `pci_bus_sem` around bus/device lists.

## Test signals
Boot and hotplug tests should verify root bridge registration, domain and bus-number resource logs, expected BAR and bridge-window decoding, resource assignment, and successful driver binding. Regression coverage should include firmware-preserved configs, reassignment configs, CardBus, SR-IOV VFs, ARI multifunction devices, RRS-delayed devices, PCIe-to-PCI bridges with no extended config, hotplug bridges with spare bus allocation, Thunderbolt/external-facing removable marking, CXL DVSEC detection, and AER/RCEC/DPC capability init/release. Lockdep and runtime PM traces are useful for rescan/remove and bridge scanning paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/proc.c -->
# sources/distributed-fs/ceph-client/drivers/pci/proc.c

## Purpose
This file implements the legacy `/proc/bus/pci` interface. It exposes per-device config-space files, optional BAR mmap support, and the `/proc/bus/pci/devices` summary used by older userspace tooling.

## Important APIs, types, and functions
`proc_bus_pci_read()` and `proc_bus_pci_write()` perform aligned config-space reads and writes from userspace buffers. `proc_bus_pci_ioctl()` handles controller-domain selection and mmap mode controls. Under `HAVE_PCI_MMAP`, `struct pci_filp_private`, `proc_bus_pci_open()`, `proc_bus_pci_release()`, and `proc_bus_pci_mmap()` track whether userspace requested IO or memory BAR mapping and optional write combining. The seq-file path uses `pci_seq_start()`, `pci_seq_next()`, `pci_seq_stop()`, and `show_device()`. Device/bus attachment entry points are `pci_proc_attach_device()`, `pci_proc_detach_device()`, and `pci_proc_detach_bus()`.

## Control flow
`pci_proc_init()` creates `/proc/bus/pci`, creates the `devices` seq file, marks proc support initialized, and attaches proc entries for already-known devices. Later enumeration calls `pci_proc_attach_device()` to create bus directories and per-device files named by slot/function. Reads clamp non-admin users to standard config space, take a runtime-PM config reference, perform byte/word/dword reads with little-endian conversion, and update the file position. Writes require lockdown permission checks, similarly chunk user data into config writes, and update inode size.

## State and persistence
The file maintains `proc_initialized`, the top-level `proc_bus_pci_dir`, each `pci_bus::procdir`, and each `pci_dev::procent`. Optional mmap state is per-open-file private memory. There is no durable storage, but userspace writes can persist by modifying device PCI config registers until reset or driver changes.

## Dependencies and integration points
It depends on procfs, seq_file, Linux capabilities, lockdown LSM checks, PCI config access wrappers, runtime PM config helpers, architecture mmap support, `pci_resource_to_user()`, `pci_mmap_fits()`, `pci_mmap_resource_range()`, and global PCI device iteration. It integrates with PCI enumeration/removal when devices and buses are attached or detached.

## Risks
This interface intentionally exposes low-level config access. Writes and mmap are gated by lockdown and capabilities, but incorrect config writes can destabilize hardware. The read path allows non-admin access only to conventional header space because some hardware locks up on undefined config reads. Mmap depends on accurate resource bounds and exclusivity checks; write-combining is only allowed for prefetchable memory BARs. Error handling ignores individual `__get_user()`/`__put_user()` failures after `access_ok()`, matching legacy style but worth preserving cautiously.

## Test signals
Check that `/proc/bus/pci/devices` lists expected domain/bus/devfn IDs, resources, IRQs, and driver names. Per-device files should expose 64 or 128 bytes to unprivileged readers and full `cfg_size` to `CAP_SYS_ADMIN`. Lockdown mode should reject writes/ioctls/mmap. Mmap tests should cover IO versus MEM mode, non-mappable BARs, exclusive iomem, prefetch-only write combining, and detach cleanup removing proc entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/Kconfig

## Purpose
This Kconfig file defines the PCI power-control subsystem and the provider drivers that can power PCI slots or endpoints before PCI enumeration. It also keeps deprecated `PWRCTL` compatibility symbols mapped to the newer `PWRCTRL` names.

## Important APIs, types, and functions
The symbols are `HAVE_PWRCTRL`, `PCI_PWRCTRL`, `PCI_PWRCTRL_PWRSEQ`, `PCI_PWRCTRL_GENERIC`, and `PCI_PWRCTRL_TC9563`. Deprecated aliases are `HAVE_PWRCTL` and `PCI_PWRCTL_PWRSEQ`. `PCI_PWRCTRL_GENERIC` and `PCI_PWRCTRL_PWRSEQ` select `POWER_SEQUENCING`; `PCI_PWRCTRL_TC9563` selects the core and depends on `I2C`.

## Control flow
There is no runtime control flow. Build configuration selects whether the core object and provider modules are compiled. Selecting a provider also selects the core where needed. `PCI_PWRCTRL_TC9563` defaults to module builds on Qualcomm architectures while still requiring I2C.

## State and persistence
The file contributes build-time state only through Kconfig symbols. Those symbols persist in kernel configuration and determine which objects and module aliases are available.

## Dependencies and integration points
The Kconfig symbols integrate with the pwrctrl Makefile in this directory and with host-controller drivers that include `<linux/pci-pwrctrl.h>`. The generic and pwrseq providers depend on the power sequencing subsystem; the TC9563 provider depends on I2C and regulator/GPIO support in its C file.

## Risks
Because `PCI_PWRCTRL` itself has no prompt, users typically enable it via providers. Missing `POWER_SEQUENCING` or I2C dependencies would produce build or probe gaps, so the select/depends lines are important. Deprecated aliases should not be extended for new code but may be needed for old configs.

## Test signals
Build matrix checks should cover all providers as built-in and modules where valid, `I2C=n` hiding TC9563, and old configs using `PCI_PWRCTL_PWRSEQ` still selecting the modern pwrseq provider. Kconfig dependency tests should verify that provider selection produces the expected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/Makefile

## Purpose
This Makefile maps PCI power-control Kconfig symbols to kernel objects and module names. It builds the shared core and the generic, pwrseq, and TC9563 providers.

## Important APIs, types, and functions
`obj-$(CONFIG_PCI_PWRCTRL)` builds `pci-pwrctrl-core.o` from `core.o`. `obj-$(CONFIG_PCI_PWRCTRL_PWRSEQ)` builds `pci-pwrctrl-pwrseq.o`. `obj-$(CONFIG_PCI_PWRCTRL_GENERIC)` builds `pci-pwrctrl-generic.o` from `generic.o`. `obj-$(CONFIG_PCI_PWRCTRL_TC9563)` builds `pci-pwrctrl-tc9563.o`.

## Control flow
There is no runtime logic. During kbuild evaluation, selected config symbols append the appropriate objects to the directory build.

## State and persistence
The file contributes build artifacts only. It does not create runtime state.

## Dependencies and integration points
The Makefile is driven by the sibling Kconfig and by kbuild. The generated module names match the platform driver modules used by devicetree modalias autoloading.

## Risks
Object naming must remain aligned with exported module aliases and Kconfig symbols. A mismatch would result in selected drivers not being built or modules not loading under expected names.

## Test signals
Use `make M=drivers/pci/pwrctrl` or full kernel builds with each symbol enabled as `y` and `m`. Confirm resulting objects/modules include `pci-pwrctrl-core`, `pci-pwrctrl-pwrseq`, `pci-pwrctrl-generic`, and `pci-pwrctrl-tc9563` as configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/core.c

## Purpose
This file is the shared PCI power-control core. It creates platform devices for devicetree PCI children that require pre-enumeration power control, invokes provider power-on/power-off callbacks in a depth-first order, and marks duplicated OF nodes as reused when the actual PCI device appears.

## Important APIs, types, and functions
The public provider API is `pci_pwrctrl_init()`, `pci_pwrctrl_device_set_ready()`, `pci_pwrctrl_device_unset_ready()`, and `devm_pci_pwrctrl_device_set_ready()`. Host-controller-facing APIs are `pci_pwrctrl_create_devices()`, `pci_pwrctrl_destroy_devices()`, `pci_pwrctrl_power_on_devices()`, and `pci_pwrctrl_power_off_devices()`. Internal helpers walk the OF tree, create/destroy platform devices, detect whether a node requires pwrctrl, and invoke `struct pci_pwrctrl::power_on` or `power_off`.

## Control flow
Host controllers call `pci_pwrctrl_create_devices()` before PCI scan. The core recursively traverses available children under the host OF node, skips nodes that already have platform devices, and creates pwrctrl platform devices only for compatible strings beginning with `pci` that have PCI supplies locally or in a remote endpoint parent. Providers bind to those platform devices, initialize `struct pci_pwrctrl`, and register a PCI bus notifier via `devm_pci_pwrctrl_device_set_ready()`. Host controllers then call `pci_pwrctrl_power_on_devices()` before enumeration; the core descends into children first, requires each pwrctrl platform driver to be bound, and rolls back earlier powered devices on error. Power-off and destroy paths mirror the tree traversal.

## State and persistence
State lives in platform devices, their driver data (`struct pci_pwrctrl`), the registered notifier block, and OF node population flags. There is no durable state. The notifier sets `dev->of_node_reused` for the PCI device that shares the same fwnode as the pwrctrl platform device, avoiding duplicate pin binding.

## Dependencies and integration points
The core depends on OF graph helpers, OF platform device creation, fwnode matching, PCI bus notifiers, platform devices, and the public `<linux/pci-pwrctrl.h>` contract. It integrates with host controllers such as Qualcomm DWC and MediaTek Gen3 controllers that create, power, and destroy pwrctrl devices around PCI link bring-up and enumeration. Provider drivers in this directory implement the actual power sequencing.

## Risks
The power-on path currently uses `-EPROBE_DEFER` when a platform device exists but its driver is not bound; the comment notes a blocking wait would be better. Depth-first order must match hardware dependencies, and rollback only powers off earlier siblings before the failed child. `pci_pwrctrl_is_required()` is intentionally selective; incorrect DT compatible strings or missing supply properties silently skip platform-device creation. Destroying devices clears `OF_POPULATED`, so ordering with other OF platform users must remain correct.

## Test signals
Boot tests should show pwrctrl platform devices created only for eligible PCI DT nodes and no duplicate pinctrl binding when PCI devices enumerate. Controller tests should cover deferred provider binding, power-on rollback, recursive child ordering, remote endpoint supply detection, destroy cleanup, and module unload of providers with the devm notifier cleanup path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/generic.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/generic.c

## Purpose
This is a generic PCI slot/endpoint power-control provider. It can power devices either through a named power sequencer from an OF graph topology or directly through all regulators and an optional clock described on the PCI node.

## Important APIs, types, and functions
`struct slot_pwrctrl` embeds `struct pci_pwrctrl` and stores regulator bulk data, optional clock, and optional `struct pwrseq_desc`. `slot_pwrctrl_probe()` acquires resources and registers the provider. `slot_pwrctrl_power_on()` uses either `pwrseq_power_on()` or regulator/clock enable. `slot_pwrctrl_power_off()` uses the matching pwrseq or regulator/clock disable path. The OF match table supports generic bridge class nodes (`pciclass,0604`) and Renesas UPD720201/UPD720202 (`pci1912,0014`).

## Control flow
When the pwrctrl core creates a platform device for a matching PCI DT node, probe allocates provider state. If the node has an OF graph, it obtains the `pcie` pwrseq handle and skips direct resource acquisition. Otherwise it obtains all regulators on the node and an optional unnamed clock. Probe then installs power callbacks, registers cleanup for regulator bulk data, initializes the core pwrctrl object, and registers readiness/notifier state. Later, the core calls the callbacks during host-controller power sequencing.

## State and persistence
State is per platform device and devm-managed except for regulator bulk data, which is freed by an explicit devm action. Runtime state consists of enabled regulators, prepared/enabled clock, or an active pwrseq. No state is saved across reboot or module unload.

## Dependencies and integration points
The provider depends on regulators, clocks, OF graph, the power sequencing consumer API, platform driver matching, and the pwrctrl core. It is used when hardware can be described generically with supplies/clocks or a pwrseq provider instead of a device-specific register sequence.

## Risks
If `pwrseq_power_on()` fails in graph mode, `slot_pwrctrl_power_on()` ignores its return value and reports success. In direct mode, a clock-enable failure after regulators are enabled is returned without disabling those regulators, leaving cleanup to later power-off or driver removal. Power-off disables regulators before the clock, which may or may not match every device's required sequencing. The generic match table must stay narrow enough to avoid claiming devices that need custom sequencing.

## Test signals
Test graph-based devices with a failing and successful `pcie` pwrseq, direct regulator-only nodes, regulator-plus-clock nodes, probe deferral for missing supplies/clocks, and repeated power-on/off cycles. Runtime checks should verify regulator and clock enable counts are balanced after failure and removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/pci-pwrctrl-pwrseq.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/pci-pwrctrl-pwrseq.c

## Purpose
This provider wraps the power sequencing subsystem for specific PCI endpoints, currently Qualcomm WCN-family WLAN devices. It gives the PCI pwrctrl core a uniform `power_on`/`power_off` callback pair backed by a named pwrseq target.

## Important APIs, types, and functions
`struct pwrseq_pwrctrl` embeds `struct pci_pwrctrl` and stores the pwrseq descriptor. `struct pwrseq_pwrctrl_pdata` supplies the pwrseq target name and an optional device validator. `pwrseq_pwrctrl_qcm_wcn_validate_device()` rejects older/incomplete WCN DT nodes that lack `vddaon-supply`. `pwrseq_pwrctrl_probe()` obtains match data, validates the node, gets the pwrseq, and registers the provider. The OF match table covers QCA6390, WCN6855, and WCN7850 PCI IDs.

## Control flow
The pwrctrl core creates a platform device for a matching PCI node. Probe retrieves per-compatible data, runs the optional validator, allocates provider state, obtains the named pwrseq target (`wlan` for the current devices), installs callbacks, initializes pwrctrl state, and registers readiness with the core. Host-controller pwrctrl calls later invoke `pwrseq_power_on()` and `pwrseq_power_off()`.

## State and persistence
State is devm-managed per platform device: the pwrctrl wrapper and pwrseq handle. Runtime power state is owned by the power sequencing provider. No persistent storage is used.

## Dependencies and integration points
The file depends on platform driver OF matching, generic device properties, the pwrseq consumer API, and the pwrctrl core. It integrates with Qualcomm WLAN DT bindings where the PMU/regulator sequencing is provided separately and the PCI endpoint node needs to be powered before enumeration.

## Risks
The validator prevents indefinite probe deferral on known incomplete WCN nodes, but future compatibles need equivalent validation if old DTs exist. Probe fails with `-EINVAL` if match data is absent or has no target, so OF table data is required. Power sequencing errors propagate through the pwrctrl core and can block host bridge scanning.

## Test signals
Validate matching for each supported compatible, successful and failed `devm_pwrseq_get()`, missing `vddaon-supply` rejection, and balanced power-on/off through host-controller probe/remove. DT compatibility tests should cover old WCN nodes without PMU supplies and new nodes with complete pwrseq wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/pci-pwrctrl-pwrseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/pci-pwrctrl-tc9563.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/pci-pwrctrl-tc9563.c

## Purpose
This is a device-specific PCI power-control provider for the Toshiba TC9563 PCIe switch. It enables switch power rails, controls reset, creates an auxiliary I2C client, and programs TC9563 registers for port disable, ASPM entry delays, TX amplitude, N_FTS, and DFE behavior before allowing PCI enumeration.

## Important APIs, types, and functions
`struct tc9563_pwrctrl` embeds `struct pci_pwrctrl` and stores regulators, per-port configuration, reset GPIO, I2C adapter, and dummy I2C client. `struct tc9563_pwrctrl_cfg` stores DT-derived settings for each port. I2C access helpers are `tc9563_pwrctrl_i2c_write()`, `tc9563_pwrctrl_i2c_read()`, and `tc9563_pwrctrl_i2c_bulk_write()`. Configuration helpers include `tc9563_pwrctrl_disable_port()`, `tc9563_pwrctrl_set_l0s_l1_entry_delay()`, `tc9563_pwrctrl_set_tx_amplitude()`, `tc9563_pwrctrl_disable_dfe()`, `tc9563_pwrctrl_set_nfts()`, and `tc9563_pwrctrl_assert_deassert_reset()`. `tc9563_pwrctrl_probe()` wires DT, supplies, GPIO, I2C, and pwrctrl registration.

## Control flow
Probe allocates state, reads the `i2c-parent` phandle and address, obtains the I2C adapter, creates a dummy I2C client, gets six named regulators, gets the `resx` reset GPIO asserted high, initializes pwrctrl, parses upstream and downstream port DT nodes into the per-port config array, and registers readiness. On power-on, it enables all regulators, deasserts the external GPIO reset, waits for oscillator stability, asserts internal reset over I2C, iterates all port configs applying disable/delay/amplitude/N_FTS/DFE programming, then deasserts internal reset. On any error it powers the device off. Removal powers off, unregisters the dummy I2C device, and releases the adapter reference.

## State and persistence
All state is per platform device. Runtime hardware state persists in TC9563 registers and power/reset lines until power-off or reset. DT properties are cached in `cfg[]`; disabled child nodes become `disable_port=true`. There is no filesystem persistence.

## Dependencies and integration points
The driver depends on regulators, GPIO descriptors, OF/platform matching, I2C transfer APIs, unaligned endian helpers, bitfield helpers, and the PCI pwrctrl core. It matches `pci1179,0623` and is intended to run before PCI enumeration so the switch is configured and released from reset when the PCI core scans the bus.

## Risks
I2C transfer failures abort power-on, but `tc9563_pwrctrl_i2c_write()` returns the raw negative or unexpected transfer count except for success; callers treat any nonzero as failure. Port parsing assumes child order maps to DSP1, DSP2, DSP3 and embedded Ethernet under DSP3; unexpected DT topology could overflow or misassign `port` because the loop increments without an explicit `TC9563_MAX` guard. Only DSP1 and DSP2 have disable sequences; a disabled DSP3 or Ethernet node will flow into the DSP2-style `else` path. Probe error cleanup calls `tc9563_pwrctrl_power_off()` after a failed readiness registration even though power-on may not have occurred. Register sequences include hardcoded offsets from vendor documentation, so review requires hardware validation.

## Test signals
Hardware bring-up should verify regulator order, reset polarity, oscillator delay, I2C endianness, and register values with a logic analyzer or I2C trace. DT tests should cover missing `i2c-parent`, unavailable adapter deferral, bad regulator/GPIO acquisition, each per-port property, disabled ports, embedded Ethernet child parsing, and removal cleanup. PCI enumeration after power-on should show the TC9563 switch and downstream devices with expected ASPM/link behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/pci-pwrctrl-tc9563.c -->
