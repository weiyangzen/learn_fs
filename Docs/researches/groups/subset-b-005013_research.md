# Research: subset-b-005013

Grouped research for PCI core internal PCIe service files. Each section preserves the source path in the title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci.h -->
# sources/distributed-fs/ceph-client/drivers/pci/pci.h

## Purpose
`pci.h` is the private PCI core header used by the PCI and PCIe service implementations. It centralizes internal constants, prototypes, small helpers, capability-search macros, PCIe link-speed conversions, reset/power-management contracts, resource helpers, SR-IOV metadata, AER/DPC/PTM/ASPM hooks, ACPI/OF integration stubs, and config mechanism definitions. It is not a standalone implementation; it is the connective contract between PCI core files such as enumeration, resource assignment, power management, error recovery, and the PCIe port-service drivers under `drivers/pci/pcie/`.

## Important APIs, Types, and Functions
Key macros include `PCI_FIND_NEXT_CAP()` and `PCI_FIND_NEXT_EXT_CAP()`, both TTL-limited config-space capability walkers parameterized by a config read function prefix. Link helpers include `PCIE_LNKCAP_SLS2SPEED()`, `PCIE_LNKCAP2_SLS2SPEED()`, `PCIE_LNKCTL2_TLS2SPEED()`, `PCIE_SPEED2MBS_ENC()`, `pcie_dev_speed_mbps()`, `pcie_update_link_speed()`, and `enum pcie_link_change_reason`.

Important types include `struct pci_cap_saved_state`, `struct pci_sriov`, `struct aer_err_info`, `struct rcec_ea`, `struct pci_eq_presets`, `struct pci_dev_reset_methods`, and `struct pci_reset_fn_method`. Exported internal contracts include AER (`pci_aer_init()`, `pci_aer_clear_status()`, `aer_get_device_error_info()`), DPC (`dpc_process_error()`, `dpc_reset_link()`), RCEC walking/linking, ASPM/LTR save-restore and policy hooks, PTM save/restore hooks, and `pcie_do_recovery()`.

## Control Flow and State
Most routines declared here are invoked by PCI device setup, suspend/resume, hotplug, and error paths. The saved-capability structures support suspend/resume persistence for AER, DPC, PTM, LTR, L1SS, SR-IOV, and PCIe base capability state. `pci_dev_set_io_state()` is a small atomic state machine for PCI error recovery: permanent failure is sticky, frozen can only transition from normal, and normal can only transition from frozen unless permanent failure is already set. `priv_flags` bits record lifecycle and link/error state such as added/removed, DPC recovered/recovering, link changed/changing, LBMS seen, and driver binding allowance.

## Dependencies and Integration Points
This header depends on core kernel PCI definitions, bitfield helpers, tracepoints, and config options. It is heavily conditional: unavailable features compile to no-op or error-returning inline stubs, allowing callers to remain simple across many kernel configurations. It integrates with `pcie/aer.c`, `dpc.c`, `aspm.c`, `bwctrl.c`, `err.c`, `pme.c`, `portdrv.c`, `ptm.c`, ACPI/OF glue, controller drivers, quirks, hotplug, and endpoint drivers that call public PCI APIs backed by these internal implementations.

## Risks and Test Signals
Risks are mostly contract drift: adding fields to saved state without adjusting buffer sizes, changing capability search semantics, weakening ordering around `priv_flags`, or using PCIe helpers on non-PCIe devices. Tests should exercise suspend/resume of AER/DPC/PTM/ASPM-capable devices, error recovery state transitions, config-space capability walking with malformed lists, link speed reporting and retraining, hotplug with DPC, and builds across feature combinations where stubs replace implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/Kconfig

## Purpose
This Kconfig file defines the PCI Express port bus and optional PCIe services built on top of it. It controls whether Linux exposes native PCIe port services such as hotplug, Advanced Error Reporting, error injection, ECRC policy control, ASPM, PME, Downstream Port Containment, Precision Time Measurement, and ACPI Error Disconnect Recover.

## Important APIs, Types, and Functions
There is no C API here, but the configuration symbols directly shape compilation and runtime behavior: `PCIEPORTBUS`, `HOTPLUG_PCI_PCIE`, `PCIEAER`, `PCIEAER_INJECT`, `PCIE_ECRC`, `PCIEASPM`, ASPM policy choices, `PCIE_PME`, `PCIE_DPC`, `PCIE_PTM`, and `PCIE_EDR`. Dependencies express service layering: AER depends on the port bus and selects RAS; AER injection depends on AER and selects generic IRQ injection; DPC depends on both port bus and AER; EDR depends on DPC and ACPI.

## Control Flow and State
The selected symbols determine which `pcie/*.c` objects are built and which inline stubs from `pci.h` are active. ASPM policy choice controls the initial `aspm_policy` compiled into `aspm.c`: BIOS default, performance, powersave, or powersupersave. `PCIE_PME` is a derived boolean enabled when `PCIEPORTBUS && PM` are true, so native PME service follows PM support.

## Dependencies and Integration Points
`PCIEPORTBUS` is the base service bus consumed by `portdrv.c` and `portdrv.h`. USB4 defaults pull in port bus and native hotplug because tunneled PCIe requires hotplug handling. AER integrates with RAS logging, DPC, EDR, CXL RAS, and PCI error recovery. ASPM integrates with power management and sysfs policy. PTM support backs endpoint and controller drivers that request timing support.

## Risks and Test Signals
Configuration risks include enabling a service without its required native control path, unexpected default behavior on USB4 systems, and build regressions under rare combinations such as `PCIEPORTBUS=n`, `PCIEASPM=y`, or `PCIE_DPC=y`. Test signals are randconfig/allmodconfig builds, boot tests verifying service registration, sysfs visibility for ASPM and AER, and runtime checks that disabled options compile to correct stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/Makefile

## Purpose
The Makefile maps PCIe service Kconfig symbols to compiled objects. It keeps the port driver core, resource/event services, and independent support files in the expected link order.

## Important APIs, Types, and Functions
No APIs are declared here. The main object relationship is `pcieportdrv-y := portdrv.o rcec.o`, so the port bus driver includes RCEC support when `CONFIG_PCIEPORTBUS` builds `pcieportdrv.o`. The object rules include `bwctrl.o` with `PCIEPORTBUS`, always compile `aspm.o`, and gate `aer.o err.o tlp.o`, `aer_cxl_rch.o`, `aer_inject.o`, `pme.o`, `dpc.o`, `ptm.o`, and `edr.o` behind their respective options.

## Control Flow and State
Build composition determines which initialization functions can be reached from `pcie_portdrv_init()` and which stubs are active from headers. ASPM is always compiled because PCI core needs LTR/L1SS save-restore helpers even when full `CONFIG_PCIEASPM` policy control is disabled.

## Dependencies and Integration Points
The file integrates Kconfig with the PCIe service bus. `aer.o` and `err.o` are built together for `CONFIG_PCIEAER`, tying interrupt logging to generic recovery. `aer_cxl_rch.o` follows `CONFIG_CXL_RAS`, and `aer_inject.o` follows `CONFIG_PCIEAER_INJECT`. PTM, PME, DPC, EDR, and bandwidth control are separate service modules/objects that share `portdrv.h`.

## Risks and Test Signals
Risks include accidentally omitting a companion object, especially `err.o` or `tlp.o` for AER, or changing ASPM to conditional compilation and breaking unconditional PCI core callers. Test with representative configs, module/built-in permutations, and link checks for unresolved symbols around AER recovery, PTM debugfs exports, and ASPM save/restore helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aer.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/aer.c

## Purpose
`aer.c` implements the PCIe Advanced Error Reporting root port/RCEC service driver and most AER device support. It initializes AER capability state, manages ECRC policy, exposes AER sysfs counters and ratelimits, handles root-port interrupts, identifies devices that logged errors, prints and traces error details, invokes driver callbacks for correctable errors, and dispatches nonfatal/fatal recovery through `pcie_do_recovery()`.

## Important APIs, Types, and Functions
Important internal types are `struct aer_err_source`, `struct aer_rpc`, and `struct aer_info`. Externally relevant functions include `pci_no_aer()`, `pci_aer_available()`, `pcie_aer_is_native()`, `pci_aer_clear_nonfatal_status()`, `pci_aer_clear_fatal_status()`, `pci_aer_raw_clear_status()`, `pci_aer_clear_status()`, `pci_save_aer_state()`, `pci_restore_aer_state()`, `pci_aer_init()`, `pci_aer_exit()`, `pci_print_aer()`, `pci_aer_unmask_internal_errors()`, `aer_get_device_error_info()`, `aer_print_error()`, `aer_recover_queue()` under APEI, and `pcie_aer_init()`.

## Control Flow and State
Device initialization finds `PCI_EXT_CAP_ID_ERR`, allocates `dev->aer_info`, initializes ratelimits, registers a saved extended-cap buffer, clears status, enables device error reporting if native AER is available, and applies ECRC policy. The service probe is limited to Root Ports and RCECs; it allocates `aer_rpc`, requests a threaded IRQ, enables CXL RCH internal errors if needed, clears stale root/downstream status, disables system-error forwarding, and enables root AER interrupts.

The hard IRQ reads root status/source, clears root status, queues an `aer_err_source` in a kfifo, and wakes the threaded handler. The threaded handler processes correctable first, then uncorrectable; `find_source_device()` walks the subordinate bus or RCEC association, `aer_get_device_error_info()` reads status/mask/FEP/TLP log, `aer_print_error()` updates counters, tracepoints, and logs, and `handle_error_source()` invokes CXL RCH handling plus recovery. APEI GHES can queue firmware-reported AER records through a separate kfifo/work item.

## Dependencies and Integration Points
AER depends on PCIe port services, MSI availability, host bridge native AER ownership or `pcie_ports=native`, RAS trace/event infrastructure, optional ACPI APEI/GHES, optional ECRC, optional CXL RAS, and generic PCI error handlers. It collaborates with `err.c` for recovery, `dpc.c` for DPC-sourced AER details, `aer_cxl_rch.c` for CXL internal errors, `aer_inject.c` for synthetic testing, and `portdrv.c` for service device creation and IRQ assignment.

## Risks and Test Signals
Risks include losing errors when the root FIFO overflows, mishandling firmware-owned AER, stale status during probe/resume, incorrect source identification when Requester ID is absent or multiple errors are present, and unsafe reset behavior for RCiEP/RCEC paths. Strong tests include AER injection of correctable/nonfatal/fatal errors, CXL RCH internal-error paths, APEI GHES recovery records, suspend/resume save-restore, sysfs counter and ratelimit behavior, MSI-disabled boot paths, and recovery callback voting through `err.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aer_cxl_rch.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/aer_cxl_rch.c

## Purpose
`aer_cxl_rch.c` adapts PCIe AER handling for CXL Root Complex Hierarchy cases. Internal errors logged by an RCEC may represent protocol errors in CXL downstream ports that are not normal visible PCIe ports, so this file forwards those events to CXL memory device drivers associated with the RCEC.

## Important APIs, Types, and Functions
Key helpers are `is_cxl_mem_dev()`, `cxl_error_is_native()`, `cxl_rch_handle_error_iter()`, `cxl_rch_handle_error()`, `handles_cxl_error_iter()`, `handles_cxl_errors()`, and `cxl_rch_enable_rcec()`. `cxl_rch_handle_error()` and `cxl_rch_enable_rcec()` are declared in `portdrv.h` under `CONFIG_CXL_RAS`.

## Control Flow and State
`cxl_rch_enable_rcec()` is called during AER service probe. If the RCEC is native AER-owned and walking its associated endpoints finds a function 0 CXL memory-class device, it unmasks correctable and uncorrectable internal errors on the RCEC. During AER processing, `cxl_rch_handle_error()` checks whether the reporting device is an RCEC and whether the AER status represents an internal error. If so, it walks associated devices and invokes `cor_error_detected()` or `error_detected()` on CXL memory drivers according to severity.

## Dependencies and Integration Points
The file depends on PCI AER helpers, RCEC association walking from port bus support, CXL memory class codes, and driver `pci_error_handlers`. It is called from `aer.c` before generic PCI AER handling, allowing CXL-specific protocol error notification without replacing the standard recovery path.

## Risks and Test Signals
Risks include missing multi-function CXL devices if class/function assumptions change, invoking callbacks when firmware owns AER, or double-notifying if future CXL topology becomes visible through regular downstream ports. Tests should cover native and firmware-owned RCEC configurations, CXL memory devices behind RCH, internal correctable/nonfatal/fatal AER bits, and absence of err_handler callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aer_cxl_rch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aer_inject.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/aer_inject.c

## Purpose
`aer_inject.c` provides a misc-device based AER software injector for testing AER handling without hardware faults. Userspace writes a packed `struct aer_error_inj` to `/dev/aer_inject`, and the module simulates device and root-port AER config registers before injecting the AER service IRQ.

## Important APIs, Types, and Functions
Important local types are `struct aer_error_inj`, `struct aer_error`, and `struct pci_bus_ops`. Core functions include `aer_inject_write()`, `aer_inject()`, `pci_bus_set_aer_ops()`, `aer_inj_read_config()`, `aer_inj_write_config()`, `find_pci_config_dword()`, and cleanup in `aer_inject_exit()`. The module uses `pcie_port_find_device()` to locate the AER service device and `irq_inject_interrupt()` to trigger its IRQ.

## Control Flow and State
Injection validates `CAP_SYS_ADMIN`, copies userspace payload, finds the target device plus root port or RCEC, checks AER capability positions and current masks, allocates or updates simulated `aer_error` records under `inject_lock`, populates device status/header log fields, synthesizes root status/source ID, overrides bus `pci_ops` for target/root buses, then injects the service IRQ. Reads and writes to relevant AER config dwords are intercepted; write-one-to-clear status semantics are emulated by XOR for RW1C fields. Module exit restores original bus ops and frees injected state.

## Dependencies and Integration Points
The injector depends on `CONFIG_PCIEAER`, generic IRQ injection, miscdevice infrastructure, and a registered AER port service on the root port/RCEC. It integrates with `aer.c` by making its regular IRQ and config-space read paths see the synthetic records.

## Risks and Test Signals
Risks include global bus-ops substitution races, stale injected records if an injection fails after partial setup, limited dword-only config emulation, and the `aer_mask_override` mask updates using logical negation instead of bitwise complement semantics. Test signals include injecting masked/unmasked correctable and uncorrectable errors, multiple errors on one root, RCEC targets, module unload after failures, and verifying original `pci_ops` restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aer_inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aspm.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/aspm.c

## Purpose
`aspm.c` manages PCIe Active State Power Management, Clock Power Management, LTR, and L1 PM substates. It provides always-built save/restore helpers for LTR and L1SS, and under `CONFIG_PCIEASPM` maintains link-state topology, computes supported/capable/default/disabled states, applies global and per-link policies, and exposes sysfs/module controls.

## Important APIs, Types, and Functions
Key always-available functions are `pci_save_ltr_state()`, `pci_restore_ltr_state()`, `pci_configure_aspm_l1ss()`, `pci_save_aspm_l1ss_state()`, and `pci_restore_aspm_l1ss_state()`. With ASPM enabled, `struct pcie_link_state` tracks upstream/downstream devices, root/parent relation, ASPM bitmasks, and Clock PM state. Exported/public functions include `pcie_aspm_init_link_state()`, `pcie_aspm_exit_link_state()`, `pcie_aspm_pm_state_change()`, `pcie_aspm_powersave_config_link()`, `pci_configure_ltr()`, `pci_bridge_reconfigure_ltr()`, `pci_disable_link_state()`, `pci_disable_link_state_locked()`, `pci_enable_link_state()`, `pci_enable_link_state_locked()`, `pcie_aspm_enabled()`, `pcie_no_aspm()`, and `pcie_aspm_support_enabled()`.

## Control Flow and State
Enumeration configures LTR path support, creates link state for downstream ports, validates subordinate devices, optionally configures common clock and retrains, computes L0s/L1/L1SS support from both link partners, applies latency constraints from endpoints, initializes Clock PM, and configures the path according to policy. Runtime policy changes and per-device enable/disable requests take `pci_bus_sem` and `aspm_lock`, update default/disable masks, and write LNKCTL/L1SS registers in spec-defined order. L1SS restore disables ASPM and L1.2 before programming timing fields, then re-enables saved bits.

## Dependencies and Integration Points
ASPM depends on PCI config helpers, OF defaults, PM state, PCI core saved capability buffers, link retraining, and sysfs/module parameter infrastructure. Endpoint drivers call link-state APIs to disable problematic states; controller and VMD paths call locked variants. It updates saved PCIe capability state so suspend/resume restores the most recent kernel-managed link settings.

## Risks and Test Signals
Risks include enabling low-power states without full LTR path support, incorrect L1SS ordering, common-clock retrain failures, stale link state after hot-remove, policy changes racing hotplug, and devices whose advertised latency is wrong. Tests should cover boot parameters `pcie_aspm=off/force`, module policy writes, per-link sysfs attributes, hotplug removal, suspend/resume with L1.2, endpoint drivers disabling states, OF default behavior, and link retraining failure rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aspm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/bwctrl.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/bwctrl.c

## Purpose
`bwctrl.c` implements the PCIe bandwidth notification/control service. It observes Link Bandwidth Management/Autonomous Bandwidth interrupts, updates cached bus link speed, tracks degraded link events, and exposes a controlled helper for changing a downstream port target speed, also used by PCIe thermal cooling support.

## Important APIs, Types, and Functions
The central state type is `struct pcie_bwctrl_data`, containing a speed-change mutex and optional thermal cooling device. Public functionality includes `pcie_set_target_speed()` and `pcie_reset_lbms()`. Service callbacks are `pcie_bwnotif_probe()`, `pcie_bwnotif_remove()`, `pcie_bwnotif_suspend()`, `pcie_bwnotif_resume()`, and `pcie_bwctrl_init()`.

## Control Flow and State
Probe rejects ports with disabled notifications or no subordinate bus, allocates service data, stores it in `port->link_bwctrl` under `pcie_bwctrl_setspeed_rwsem`, requests the shared service IRQ, enables LBMIE/LABIE, clears LBMS/LABS, updates cached link speed, and registers a cooling device if possible. IRQ handling reads LNKSTA, acknowledges LBMS/LABS, records `PCI_LINK_LBMS_SEEN`, and calls `pcie_update_link_speed()`. Speed changes select the highest speed supported by both port and first downstream device at or below the request, write Target Link Speed, retrain, and return `-EAGAIN` if a non-empty bus did not reach the requested speed.

## Dependencies and Integration Points
Bandwidth control depends on PCIe port bus services, `pcie_retrain_link()`, `pci_bus_sem`, PCIe link capability fields, private `pci_dev` fields, and `drivers/thermal/pcie_cooling.c`. `portdrv.c` creates this service when a Root/Downstream Port supports bandwidth notifications and multiple speeds.

## Risks and Test Signals
Risks include selecting speed from only the first child on a bus, races between removal and speed changes, missed LBMS events if status clear/read ordering changes, and thermal cooling registration failures. Tests should cover IRQ delivery, hot-remove during target-speed changes, quirks that call `pcie_set_target_speed()` before service probe, empty downstream bus behavior, and speed downgrade/restore through PCIe cooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/bwctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/dpc.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/dpc.c

## Purpose
`dpc.c` implements the Downstream Port Containment service. DPC contains fatal link errors by hardware-disabling the link, logs the containment reason and optional Root Port PIO detail, coordinates with hotplug for DPC-induced link events, and recovers affected devices via PCI error recovery.

## Important APIs, Types, and Functions
Important functions include `pci_save_dpc_state()`, `pci_restore_dpc_state()`, `pci_dpc_recovered()`, `dpc_reset_link()`, `dpc_process_error()`, `pci_dpc_init()`, and `pcie_dpc_init()`. Service callbacks are `dpc_probe()`, `dpc_suspend()`, `dpc_resume()`, and `dpc_remove()`. Local helpers process RP PIO logs, surprise removal, DPC IRQs, and enable/disable control bits.

## Control Flow and State
`pci_dpc_init()` discovers the DPC extended capability and Root Port extensions/log size. Probe requires native AER or DPC-native ownership, requests a threaded IRQ, enables fatal-error DPC and interrupts, logs capabilities, and registers a saved control-word buffer. On IRQ, the hard handler acknowledges interrupt status and wakes the thread when trigger status is set. The thread treats surprise removal specially; otherwise it logs the error, calls `pcie_do_recovery()` with frozen state and `dpc_reset_link()`. Reset waits for link inactive, waits for RP inactive when needed, clears trigger status, waits for the secondary bus, and updates `PCI_DPC_RECOVERED`/`PCI_DPC_RECOVERING`.

## Dependencies and Integration Points
DPC depends on AER availability, PCIe port service registration, `pcie_do_recovery()` from `err.c`, AER parsing helpers from `aer.c`, hotplug synchronization via `pci_dpc_recovered()`, and EDR firmware recovery in `edr.c`. It uses private PCI saved-capability state and TLP log helpers for RP PIO diagnostics.

## Risks and Test Signals
Risks include recovery deadlock or missed wakeups around hotplug, incorrect handling when firmware owns DPC, surprise-removal false positives, invalid RP PIO log sizes, and failures waiting for link/RP inactive. Tests should exercise DPC fatal interrupts, RP PIO logs, hotplug link-down suppression, ACPI EDR paths, suspend/resume of DPC control, surprise removal on hotplug ports, and timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/dpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/edr.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/edr.c

## Purpose
`edr.c` implements ACPI Error Disconnect Recover support, a hybrid firmware/OS DPC model. Firmware notifies the OS of a disconnect recover event, the OS locates the DPC port, logs and recovers the containment event, then reports success or failure to firmware via `_OST`.

## Important APIs, Types, and Functions
Key helpers are `acpi_enable_dpc()`, `acpi_dpc_port_get()`, `acpi_send_edr_status()`, and `edr_handle_event()`. The externally used functions are `pci_acpi_add_edr_notifier()` and `pci_acpi_remove_edr_notifier()`, declared through PCI ACPI headers and called by PCI ACPI setup/teardown.

## Control Flow and State
Notifier installation checks for an ACPI companion, installs a system notify handler, and optionally evaluates the PCI firmware `_DSM` function to enable DPC. When `ACPI_NOTIFY_DISCONNECT_RECOVER` arrives, `edr_handle_event()` locates the actual DPC port using `_DSM` function 0x0D or defaults to the notified device, verifies DPC capability and trigger status, calls `dpc_process_error()`, clears raw AER status, and runs `pcie_do_recovery()` with `dpc_reset_link()`. It sends `_OST` with success `0x80` or failure `0x81` encoded with the affected BDF.

## Dependencies and Integration Points
EDR depends on `CONFIG_ACPI`, `CONFIG_PCIE_DPC`, PCI firmware DSM GUID support, DPC helpers, AER raw status clearing, and generic PCI error recovery. It is attached from `drivers/pci/pci-acpi.c` for suitable devices and removed when ACPI PCI state is torn down.

## Risks and Test Signals
Risks include firmware returning malformed `_DSM` objects, locating the wrong DPC port, missing trigger status due to races with native DPC, and incorrect `_OST` status causing firmware/OS disagreement. Tests should simulate EDR notifications, absent optional DSMs, failed locate DSM, ports without DPC, recovery success/failure, and notifier removal on device teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/edr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/err.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/err.c

## Purpose
`err.c` implements generic PCIe error recovery shared by AER, DPC, EDR, and firmware-reported AER. It walks the affected bridge subtree, calls driver `pci_error_handlers` in the required order, coordinates resets, updates PCI channel state, and emits uevents.

## Important APIs, Types, and Functions
The central exported function is `pcie_do_recovery(struct pci_dev *dev, pci_channel_state_t state, pci_ers_result_t (*reset_subordinates)(struct pci_dev *pdev))`. Key helpers include `merge_result()`, `report_error_detected()`, `report_mmio_enabled()`, `report_slot_reset()`, `report_resume()`, `report_perm_failure_detected()`, `pci_pm_runtime_get_sync()`, `pci_pm_runtime_put()`, and `pci_walk_bridge()`.

## Control Flow and State
Recovery chooses the affected bridge: Root Port, Downstream Port, RCEC, and RCiEP recover from themselves; endpoints recover via their upstream bridge. It runtime-resumes all affected devices, broadcasts `error_detected()` with frozen or normal channel state, optionally broadcasts `mmio_enabled()`, invokes the supplied subordinate reset function when a reset is needed or state is frozen, broadcasts `slot_reset()` if requested, and finally broadcasts `resume()`. On success, native AER ownership allows clearing device and nonfatal AER status. On failure, it calls `error_detected(...perm_failure)` and leaves devices disconnected.

## Dependencies and Integration Points
The file depends on PCI driver error-handler callbacks, runtime PM, AER status helpers, `pci_dev_set_io_state()` from `pci.h`, RCEC/RCiEP handling, and reset callbacks provided by AER or DPC (`aer_root_reset()` or `dpc_reset_link()`). The PCIe port driver itself provides error handlers so port-service children can be reset.

## Risks and Test Signals
Risks include incorrect result merging, devices without callbacks aborting recovery for an entire subtree, runtime PM imbalance, state transitions blocked by permanent failure, and bridge selection mistakes for RCEC/RCiEP. Tests should inject AER/DPC failures across endpoints and bridges, cover callback result combinations, missing driver handlers, reset failures, runtime-suspended devices, and successful clearing under native AER only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/err.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/pme.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/pme.c

## Purpose
`pme.c` implements native PCIe Power Management Event signaling for Root Ports and Root Complex Event Collectors. It handles PME interrupts, identifies the requesting device, wakes/resumes that device, marks downstream devices wake-capable, and preserves wake behavior over system suspend.

## Important APIs, Types, and Functions
The main state type is `struct pcie_pme_service_data`, containing a spinlock, service pointer, work item, and `noirq` suspend/removal flag. Public helpers include `pcie_pme_interrupt_enable()` and `pcie_pme_init()`, with `pcie_pme_disable_msi()`/`pcie_pme_no_msi()` declared in `portdrv.h`. Core functions include `pcie_pme_irq()`, `pcie_pme_work_fn()`, `pcie_pme_handle_request()`, `pcie_pme_walk_bus()`, `pcie_pme_probe()`, `pcie_pme_suspend()`, `pcie_pme_resume()`, and `pcie_pme_remove()`.

## Control Flow and State
Probe limits the service to Root Ports/RCECs, allocates state, disables and clears PME, requests the IRQ, marks devices wake-capable, then enables PME interrupts. The IRQ disables PME interrupt generation and schedules non-freezable work. The worker loops while PME status or pending bits exist, clears root PME status, handles requester IDs, and re-enables interrupts unless suspended/removed. Suspend either enables IRQ wake if any downstream device may wake, or disables/clears PME and synchronizes the IRQ. Resume re-enables PME or disables IRQ wake depending on the suspend path.

## Dependencies and Integration Points
PME depends on PCIe port services, runtime PM, wakeup framework, RCEC walking, `pci_check_pme_status()`, `pm_request_resume()`, and `portdrv.c` IRQ assignment. DMI and command-line handling in `portdrv.c`/`pme.c` can force INTx instead of MSI because PME wake from sleep has platform quirks.

## Risks and Test Signals
Risks include spurious interrupts from stale status, missed PMEs while interrupts are disabled, requester IDs from PCIe-to-PCI bridges, races with suspend `noirq`, and MSI wake incompatibilities. Tests should cover root-port PME, RCEC PME, bridged PCI devices, wake from system sleep with MSI and INTx, runtime resume requests, spurious requester IDs, and removal while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/pme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/portdrv.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/portdrv.c

## Purpose
`portdrv.c` is the PCIe port bus driver. It binds to PCIe Root/Upstream/Downstream Ports and RCECs, discovers native services, allocates service IRQs, creates child `pcie_device` instances on the `pci_express` bus, registers service drivers, fans out PM callbacks, and integrates port devices with PCI error recovery and runtime PM.

## Important APIs, Types, and Functions
Important types include `struct portdrv_service_data`, `struct pcie_device`, and `struct pcie_port_service_driver`. Exported APIs are `pcie_port_find_device()`, `pcie_port_service_register()`, and `pcie_port_service_unregister()`. Key internals include `pcie_message_numbers()`, `pcie_port_enable_irq_vec()`, `pcie_init_service_irqs()`, `get_port_device_capability()`, `pcie_device_init()`, `pcie_port_device_register()`, `pcie_port_device_remove()`, `pcie_port_bus_match()`, `pcie_port_bus_probe()`, `pcie_port_bus_remove()`, and `pcie_portdrv_probe()`.

## Control Flow and State
At device init, `pcie_portdrv_init()` registers service drivers for AER, PME, DPC, bandwidth control, and hotplug, applies DMI PME MSI quirks, then registers the PCI driver. Probe validates PCIe port/RCEC type, links RCECs, enables the PCI device, discovers service capability based on port type, native ownership, AER availability, DPC capability, hotplug, PME, and bandwidth notification support, allocates MSI-X/MSI or INTx vectors, creates child service devices, saves port state, and enables runtime PM if bridge D3 is possible. Remove/shutdown unregister children, frees vectors, and disables the port device.

## Dependencies and Integration Points
The driver depends on host bridge `_OSC` ownership flags, boot parameters `pcie_ports=compat/native/dpc-native`, PCI IRQ vector allocation, DMI, runtime PM, RCEC support, AER/PME/DPC/bwctrl/hotplug init functions, and PCI core error handlers. Service files under `pcie/` register against `pcie_port_bus_type` and receive their synthetic device plus IRQ from this driver.

## Risks and Test Signals
Risks include incorrect service discovery when firmware retains ownership, bad MSI message number handling, shared-vector interactions among PME/hotplug/bwctrl, leaking child devices or IRQ vectors on partial failure, and runtime D3 breaking config accesses. Tests should cover native and firmware-owned ACPI systems, `pcie_ports` boot options, MSI/MSI-X/INTx fallback, RCEC service creation, runtime suspend/resume, service probe failure paths, and PCI error recovery callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/portdrv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/portdrv.h -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/portdrv.h

## Purpose
`portdrv.h` defines the private PCIe port-service bus ABI shared by `portdrv.c` and service drivers. It identifies service bits, declares service initialization hooks, defines synthetic service device/driver structures, and provides optional-feature stubs.

## Important APIs, Types, and Functions
Service bit definitions are `PCIE_PORT_SERVICE_PME`, `AER`, `HP`, `DPC`, and `BWCTRL`, with `PCIE_PORT_DEVICE_MAXSERVICES` set to five. `struct pcie_device` contains the service IRQ, parent PCI port, service bit, private service data, and embedded `struct device`. `struct pcie_port_service_driver` contains probe/remove/PM/reset callbacks, port type match, service bit, and embedded `device_driver`. Helper APIs include `set_service_data()`, `get_service_data()`, `pcie_port_service_register()`, `pcie_port_service_unregister()`, `pcie_port_find_device()`, PME MSI controls, and CXL RCH AER hooks.

## Control Flow and State
`portdrv.c` allocates one `pcie_device` per detected service and matches it with a `pcie_port_service_driver` by service bit and port type. Each service stores private state through `priv_data`. Configuration stubs make absent services return no-op success or harmless defaults, allowing initialization fan-out in `portdrv.c` to remain unconditional.

## Dependencies and Integration Points
The header is included by AER, AER injection, CXL RCH handling, bandwidth control, DPC, EDR, PME, and port driver code. It also bridges hotplug via `pcie_hp_init()` and provides global policy state `pcie_ports_dpc_native`.

## Risks and Test Signals
Risks include adding a new service without updating `PCIE_PORT_DEVICE_MAXSERVICES`, mismatched shift/bit ordering with IRQ arrays, lifetime mistakes with service `priv_data`, and stub behavior diverging from enabled implementations. Tests should build all service combinations, verify service device names and matching, shared IRQ assignment, and lookup through `pcie_port_find_device()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/portdrv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/ptm.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/ptm.c

## Purpose
`ptm.c` implements PCIe Precision Time Measurement support. It discovers PTM capabilities, determines root/requester/responder roles and effective granularity, reference-counts enablement along the upstream PTM path, saves/restores PTM control state, suspends/resumes enabled PTM, and optionally exposes PTM context debugfs files for controller-specific implementations.

## Important APIs, Types, and Functions
Key PCI APIs are `pci_ptm_init()`, `pci_save_ptm_state()`, `pci_restore_ptm_state()`, `pci_enable_ptm()`, `pci_disable_ptm()`, `pci_suspend_ptm()`, `pci_resume_ptm()`, and `pcie_ptm_enabled()`. Debugfs APIs under `CONFIG_DEBUG_FS` are `pcie_ptm_create_debugfs()` and `pcie_ptm_destroy_debugfs()`, driven by `struct pcie_ptm_ops` callbacks for context update, validity, clocks, and timestamps.

## Control Flow and State
Initialization finds `PCI_EXT_CAP_ID_PTM`, records `dev->ptm_cap`, resets `ptm_enable_cnt`, adds a saved-control buffer, reads local granularity, finds the upstream PTM partner while skipping switch downstream ports, determines whether the device is a root, requester, or responder, and propagates effective granularity from the upstream source. `pci_enable_ptm()` recursively enables upstream PTM before the target, increments `ptm_enable_cnt`, writes enable/root/granularity bits, and logs granularity. Disable decrements the counter and recursively disables the upstream partner. Suspend disables hardware while preserving the count; resume re-enables if the count is nonzero.

## Dependencies and Integration Points
PTM depends on PCIe extended capability access, upstream bridge topology, atomic counters in `struct pci_dev`, saved capability buffers, module exports used by network drivers, and debugfs integrations used by DesignWare PCIe controller debug code. Public declarations are in `include/linux/pci.h`, while private save/restore hooks are declared in `pci.h`.

## Risks and Test Signals
Risks include recursive enable/disable imbalance, enabling endpoints without a complete upstream PTM path, ambiguous RCiEP time source granularity, resume failing silently after topology changes, and debugfs callbacks racing hardware context updates. Tests should cover root and endpoint enablement, nested users of `pci_enable_ptm()`, suspend/resume, missing upstream PTM, switch downstream-port skipping, debugfs file visibility and locking, and drivers such as mlx5/igc/ice/idpf requesting PTM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/ptm.c -->
