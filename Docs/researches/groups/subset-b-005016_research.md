# subset-b-005016 PCI research group

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/search.c -->
# sources/distributed-fs/ceph-client/drivers/pci/search.c

## Purpose
`search.c` provides PCI core lookup and iteration helpers for buses and devices, plus DMA requester-ID alias iteration. It is a shared kernel API surface used by drivers, subsystems, and legacy interfaces that need to locate PCI devices by bus address, ID table, class code, or root-bus topology.

## Important APIs, types, and functions
The file defines `pci_bus_sem`, the read/write semaphore protecting global PCI bus and per-bus device lists. `pci_for_each_dma_alias()` walks a device's real DMA identity, explicit `dma_alias_mask`, and upstream bridge aliasing rules. Bus lookup is implemented by `pci_find_next_bus()`, `pci_find_bus()`, and recursive `pci_do_find_bus()`. Device lookup includes `pci_get_slot()`, `pci_get_domain_bus_and_slot()`, `pci_get_subsys()`, `pci_get_device()`, `pci_get_device_reverse()`, `pci_get_class()`, `pci_get_base_class()`, and `pci_dev_present()`. Public helpers export symbols and consistently return referenced `struct pci_dev *` values where the caller must call `pci_dev_put()`.

## Control flow and behavior
DMA alias iteration starts at `pci_real_dma_dev()`, calls the callback for the primary requester ID, then for any alias mask entries, then walks upstream until a root bus or a bridge marked `PCI_DEV_FLAGS_BRIDGE_XLATE_ROOT`. PCIe bridge type controls whether the alias remains the downstream device, becomes the bridge, or uses subordinate bus 0. Bus lookup walks `pci_root_buses` under `pci_bus_sem`, then searches child lists recursively. Device lookup uses either protected per-bus list traversal or `bus_find_device()`/`bus_find_device_reverse()` against `pci_bus_type`.

## State and persistence
The file does not persist state itself beyond the exported `pci_bus_sem`. It manipulates object lifetimes through `pci_dev_get()` and `pci_dev_put()`. `pci_dev_present()` intentionally returns only a momentary hint with no held reference after it exits.

## Dependencies and integration points
It depends on `linux/pci.h`, the driver core bus model, PCI device ID matching, `pci_root_buses`, bridge flags, and `pci_match_one_device()`. `pci_get_domain_bus_and_slot()` is used by the PCI config syscalls and TSM helpers in this subset.

## Risks
Callers must honor reference-count rules, especially continuation searches where the `from` argument is put by the search helper. `pci_dev_present()` can race hot removal by design. DMA alias rules are architecture and bridge-behavior sensitive, so regressions can break IOMMU grouping or DMA isolation.

## Test signals
Useful signals include hotplug add/remove lookup races, reference leak checks, reverse and forward ID iteration, class matching with wildcard IDs, IOMMU alias tests behind PCIe-to-PCI bridges, and boot logs for devices with `dma_alias_mask` or bridge alias flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/search.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/setup-bus.c -->
# sources/distributed-fs/ceph-client/drivers/pci/setup-bus.c

## Purpose
`setup-bus.c` is the PCI core bridge-window sizing and resource assignment engine. It sizes downstream I/O, MMIO, and prefetchable MMIO windows, assigns device and bridge resources, retries allocation by releasing bridge windows when needed, distributes hotplug headroom, and supports resizing/reassigning resources after enumeration.

## Important APIs, types, and functions
The key local type is `struct pci_dev_resource`, which snapshots a device resource, requested add-on size, minimum alignment, and original flags for retry/restore lists. Important exported or externally used APIs include `pci_flags`, `pci_dev_res_add_to_list()`, `pbus_select_window()`, `pci_resource_is_optional()`, `pci_bus_size_bridges()`, `pci_claim_bridge_resource()`, `pci_bus_assign_resources()`, `pci_bus_claim_resources()`, `pci_realloc_get_opt()`, `pci_assign_unassigned_root_bus_resources()`, `pci_assign_unassigned_resources()`, `pci_assign_unassigned_bridge_resources()`, `pci_do_resource_release_and_resize()`, and `pci_assign_unassigned_bus_resources()`. Weak hooks `pcibios_setup_bridge()` and `pcibios_window_alignment()` let architectures participate.

## Control flow and behavior
Sizing is depth-first. `__pci_bus_size_bridges()` first sizes subordinate buses, handles CardBus separately, checks bridge range support, accounts hotplug reserves, and calls `pbus_size_io()` and `pbus_size_mem()` for appropriate windows. Memory sizing buckets child BAR alignments, computes compact head alignment, treats SR-IOV, ROM, and empty bridge windows as optional, and can record optional growth in a realloc list.

Assignment is sorted by decreasing alignment. `pdev_sort_resources()` collects unassigned movable resources; `__assign_resources_sorted()` first tries required plus optional growth, then falls back to required resources, releasing same-type allocations when required resources fail. Bridge setup writes base/limit registers via `pci_setup_bridge_io()`, `pci_setup_bridge_mmio()`, and `pci_setup_bridge_mmio_pref()` after resources are assigned. Root assignment can perform multiple tries depending on `pci=realloc` policy and bus depth, releasing leaf or whole-subtree bridge windows before retrying.

Hotplug distribution starts with spare space in a hotplug bridge, subtracts already-needed device resources, and recursively splits surplus among hotplug bridges or normal bridges. Resizable BAR support releases affected BARs and upstream bridge windows, changes the BAR size, reassigns the hierarchy, and restores the old state if any required resource fails.

## State and persistence
The persistent state is the kernel resource tree (`struct resource` parent/child links), `struct pci_dev.resource[]`, bridge config-space windows, `pci_flags`, and the boot-time `pci_realloc_enable` policy. Temporary linked lists store snapshots for retries and are freed after each pass.

## Dependencies and integration points
This file integrates with `setup-res.c` for `pci_assign_resource()`, `pci_release_resource()`, and `pci_update_resource()`, with `setup-cardbus.c` for CardBus sizing/setup, with ACPI for `acpi_ioapic_add()`, with SR-IOV and resizable BAR helpers, and with architecture hooks for resource alignment and bridge programming.

## Risks
Resource sizing has high blast radius: bad alignment or optional-size accounting can leave devices unassigned, overlap bridge windows, or program invalid hardware ranges. Retry paths depend on faithfully restoring saved resource state. Locking matters around subtree resize because bridge reassignment walks global PCI topology under `pci_bus_sem`.

## Test signals
Relevant tests include multi-level bridge enumeration, hotplug bridges with spare capacity, SR-IOV BAR allocation with and without `pci=realloc`, 64-bit prefetchable windows, disabled/empty bridge windows, CardBus bridges, resizable BAR grow/shrink failure recovery, and boot logs containing assignment, release, restore, and "failed to assign" messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/setup-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/setup-cardbus.c -->
# sources/distributed-fs/ceph-client/drivers/pci/setup-cardbus.c

## Purpose
`setup-cardbus.c` handles CardBus bridge resource sizing, config-space programming, kernel-parameter overrides, and two-pass bus-number assignment for CardBus bridges.

## Important APIs, types, and functions
It defines CardBus defaults (`DEFAULT_CARDBUS_IO_SIZE`, `DEFAULT_CARDBUS_MEM_SIZE`), mutable boot-parameter sizes `pci_cardbus_io_size` and `pci_cardbus_mem_size`, and the reserve count `CARDBUS_RESERVE_BUSNR`. Main functions are `pci_cardbus_resource_alignment()`, `pci_bus_size_cardbus_bridge()`, `pci_setup_cardbus_bridge()`, `pci_setup_cardbus()`, and `pci_cardbus_scan_bridge_extend()`.

## Control flow and behavior
Sizing reserves two I/O windows and one or two memory windows on the bridge. It clears `PCI_CB_BRIDGE_CTL_PREFETCH_MEM1`, probes and enables prefetch support for MEM0, and marks bridge resources with `IORESOURCE_STARTALIGN` for later assignment. If a realloc list is provided, it records optional future growth.

`pci_setup_cardbus_bridge()` translates assigned resources into bus-relative addresses and writes the CardBus I/O and memory base/limit registers. `pci_setup_cardbus()` parses `pci=cbiosize=` and `pci=cbmemsize=` options via `memparse()`. Scanning is two-pass: pass 0 disables forwarding with a temporary `PCI_PRIMARY_BUS` write; pass 1 clears status errors, honors Enhanced Allocation fixed bus numbers if present, creates or reuses a child bus, writes primary/secondary/subordinate numbers in one dword, reserves up to three additional bus numbers for future cards, updates the child bus resource, and validates the bus-number range.

## State and persistence
The persistent state is bridge config space, `bus->resource[]`, child `busn_res`, child name, and the global CardBus size tunables set by boot parameters. No private heap state is retained.

## Dependencies and integration points
It is called from `setup-bus.c` during bridge sizing and assignment. It depends on PCI bus-number helpers, resource translation, Enhanced Allocation bus-number discovery, and CardBus config register definitions.

## Risks
Wrong prefetch handling can misroute CardBus memory windows. Bus-number reservation must avoid existing bus numbers and firmware-assigned parent ranges. The fixed resource sizing is conservative but can waste scarce I/O or memory address space.

## Test signals
Test with CardBus bridges that support and do not support prefetchable memory, bridges with EA fixed bus numbers, hotplug scans where target bus numbers already exist, boot overrides for `cbiosize`/`cbmemsize`, and logs showing CardBus window programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/setup-cardbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/setup-res.c -->
# sources/distributed-fs/ceph-client/drivers/pci/setup-res.c

## Purpose
`setup-res.c` provides lower-level PCI resource operations for BAR and bridge-window assignment: programming config-space BARs, claiming resources in parent windows, falling back to firmware addresses, assigning and releasing resources, and enabling device decode bits.

## Important APIs, types, and functions
Important functions include `pci_update_resource()`, `pci_claim_resource()`, `pci_disable_bridge_window()`, weak `pcibios_retrieve_fw_addr()`, `pci_align_resource()`, weak `pcibios_align_resource()`, `pci_assign_resource()`, `pci_reassign_resource()`, `pci_release_resource()`, and `pci_enable_resources()`. Internal `pci_std_update_resource()` programs normal and ROM BARs, while `__pci_assign_resource()` and `_pci_assign_resource()` allocate from the device bus and transparent upstream bridges.

## Control flow and behavior
BAR update skips virtual-function BARs, unimplemented or unset resources, and fixed resources. It converts CPU resources to bus addresses, chooses the right BAR register, optionally disables memory decoding for non-atomic 64-bit BAR updates, writes low and high dwords, mirrors saved config space, verifies reads, and restores the command register.

Claiming finds a compatible parent resource, skips shadow ROMs, calls `request_resource_conflict()`, and marks conflicts or missing windows as `IORESOURCE_UNSET`. Assignment marks the resource unset, computes alignment, allocates from the best matching bridge window, falls back to the firmware address from `pcibios_retrieve_fw_addr()` if no space exists, clears unset/start-align flags, re-enables bridge windows, and updates config-space BARs for endpoint resources. Reassignment expands an already assigned resource; release detaches it from the resource tree and resets start/end to size form. Enabling validates requested required resources and sets `PCI_COMMAND_IO` or `PCI_COMMAND_MEMORY` only when claimed parents exist.

## State and persistence
The file mutates `struct resource` ranges, flags, and parent links, device command register decode bits, BAR registers, ROM enable bits, and `saved_config_space[]`. Firmware-address fallback depends on architecture-provided saved firmware BAR addresses.

## Dependencies and integration points
It is used heavily by `setup-bus.c`. It depends on resource-tree APIs, PCI config accessors, architecture `pcibios_*` hooks, SR-IOV update helpers, bridge-window helpers, and command-register semantics.

## Risks
Programming 64-bit BARs while decode remains enabled can briefly expose bad addresses, hence the decode-disable path. Misclassifying optional resources can allow devices to be enabled with missing required BARs. Firmware fallback on root buses assumes host bridges route all I/O or memory of the appropriate type.

## Test signals
Exercise 32-bit and 64-bit BARs, ROM BARs enabled and disabled, overlapping resources, missing parent bridge windows, transparent bridges, fixed resources, firmware fallback, SR-IOV VF BAR handling, and `pci_enable_resources()` failures for unset or unclaimed required BARs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/setup-res.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/slot.c -->
# sources/distributed-fs/ceph-client/drivers/pci/slot.c

## Purpose
`slot.c` implements sysfs-visible physical PCI slot objects under `/sys/bus/pci/slots`, including naming, default attributes, device-to-slot association, reference management, and hotplug-driver integration.

## Important APIs, types, and functions
It exports `pci_slots_kset`, `pci_create_slot()`, and `pci_destroy_slot()`. It defines the `pci_slot_ktype`, sysfs ops for `struct pci_slot_attribute`, default attributes `address`, `max_bus_speed`, and `cur_bus_speed`, and helpers `make_slot_name()`, `rename_slot()`, `pci_dev_assign_slot()`, and `get_slot()`.

## Control flow and behavior
Initialization creates the global `slots` kset under the PCI bus kset. `pci_create_slot()` serializes on `pci_slot_mutex`, reuses existing `(bus, slot_nr)` slots except placeholder `-1` slots, optionally lets hotplug drivers rename unclaimed slots, allocates and names new slots while avoiding duplicate sysfs names by suffixing `-N`, attaches the kobject, and assigns matching existing devices' `dev->slot` pointers under `pci_bus_sem`. `pci_destroy_slot()` simply drops the kobject reference; `pci_slot_release()` clears matching devices' slot pointers, removes the slot from the bus list, drops the bus reference, and frees memory.

## State and persistence
Persistent kernel state includes `pci_slots_kset`, each bus's `slots` list, kobject references, `slot->hotplug`, `slot->number`, and each device's `dev->slot` pointer. Sysfs files expose derived address and bus speed data.

## Dependencies and integration points
It integrates with the PCI bus kset, hotplug drivers, `pci_bus_sem`, `pci_slot_mutex`, kobject/sysfs infrastructure, and optional `ARCH_PCI_SLOT_GROUPS`.

## Risks
Incorrect reference balancing can leak slots or free objects while devices still point at them. Slot name collisions are expected on broken firmware and must remain ABI-compatible. Bus-wide slots using `PCI_SLOT_ALL_DEVICES` must correctly match ARI or multi-device slot semantics.

## Test signals
Use hotplug driver create/destroy cycles, duplicate firmware slot names, placeholder slots, bus-wide PCIe slots, sysfs attribute reads, and device insertion after slot creation to verify `pci_dev_assign_slot()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/slot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/switch/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/switch/Kconfig

## Purpose
This Kconfig fragment defines the PCI switch controller driver menu and the `PCI_SW_SWITCHTEC` option for the MicroSemi Switchtec PCIe switch management driver.

## Important APIs, types, and functions
There are no C APIs. The important symbol is `CONFIG_PCI_SW_SWITCHTEC`, declared as a tristate and gated by `depends on PCI`.

## Control flow and behavior
When enabled built-in or as a module, the option causes `switchtec.o` to be built by the local Makefile. The help text documents that the driver exposes userspace MRPC command submission through `/dev/switchtecX` and points to `Documentation/driver-api/switchtec.rst`.

## State and persistence
The persistent effect is build configuration: `.config` records whether Switchtec support is disabled, built in, or modular.

## Dependencies and integration points
The symbol integrates with the PCI menu hierarchy and `drivers/pci/switch/Makefile`. It indirectly selects the runtime code in `switchtec.c`.

## Risks
Because this option exposes a userspace management device for PCIe switches, enabling it can add a privileged hardware-management ABI. Missing `PCI` dependency would break builds, but this fragment correctly gates it.

## Test signals
Check `olddefconfig` visibility under PCI, module and built-in builds, and that `CONFIG_PCI_SW_SWITCHTEC=m/y` produces the expected `switchtec` driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/switch/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/switch/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/switch/Makefile

## Purpose
This Makefile wires the Switchtec PCIe switch management driver object into the kernel build.

## Important APIs, types, and functions
The only build rule is `obj-$(CONFIG_PCI_SW_SWITCHTEC) += switchtec.o`.

## Control flow and behavior
Kbuild includes `switchtec.o` only when `CONFIG_PCI_SW_SWITCHTEC` is `y` or `m`. The SPDX line declares GPL-2.0 licensing for the build file.

## State and persistence
There is no runtime state. The persistent effect is build output selection, either linking the object into the kernel or producing a module depending on Kconfig.

## Dependencies and integration points
It depends on the Kconfig symbol from the same directory and the source file `switchtec.c`.

## Risks
The file is simple. The main risk is drift between Kconfig symbols and object names, which would silently omit the driver from builds.

## Test signals
Build with `CONFIG_PCI_SW_SWITCHTEC=n`, `m`, and `y`, and confirm object/module presence or absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/switch/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/switch/switchtec.c -->
# sources/distributed-fs/ceph-client/drivers/pci/switch/switchtec.c

## Purpose
`switchtec.c` is the Microsemi/Microchip Switchtec PCIe switch management driver. It binds supported management or bridge-class PCI functions, maps switch MMIO regions, exposes `/dev/switchtecN`, forwards MRPC commands between userspace and firmware, reports flash and event state through ioctls, and handles switch events and link notifications.

## Important APIs, types, and functions
Module parameters are `max_devices`, `use_dma_mrpc`, and `nirqs`. The file exports `switchtec_class`. Important runtime types are `struct switchtec_dev` from shared headers and local `struct switchtec_user`, which tracks one open-file MRPC command, completion waitqueue, data buffer, and event counter. File operations include `switchtec_dev_open()`, `switchtec_dev_release()`, `switchtec_dev_write()`, `switchtec_dev_read()`, `switchtec_dev_poll()`, and `switchtec_dev_ioctl()`. Core helpers include MRPC queue/completion functions, flash/event/PFF ioctl helpers, `switchtec_init_pci()`, `switchtec_init_isr()`, `switchtec_pci_probe()`, and `switchtec_pci_remove()`.

## Control flow and behavior
Probe creates a character device object, enables the PCI device, sets a 64-bit DMA mask, maps BAR0 in write-combining mode for MRPC and normal mode for GAS registers, discovers partition and PFF topology, optionally allocates coherent DMA MRPC memory, registers interrupts, enables event headers, enables DMA MRPC, and adds the cdev/device.

Userspace writes a buffer containing an MRPC command plus payload. The driver validates size, restricts GAS read/write MRPC commands to `CAP_SYS_ADMIN`, copies the command into the per-open `switchtec_user`, queues it, and starts execution if no other command is running. Completion arrives from the MRPC event work item, DMA MRPC IRQ, or timeout polling. The completion path reads status, return code, and output data from either coherent DMA memory or MMIO registers, wakes the waiting file, removes it from the queue, and submits the next command. Reads wait unless nonblocking, copy the return code and response payload to userspace, translate hardware status to errno, and return the user state to idle.

Ioctls expose flash layout for gen3/gen4+, per-partition active/running state, event summaries, event control flags, and PFF-to-port mappings. The event ISR handles MRPC completions, link-state events, masks occurred events, increments `event_cnt`, and wakes poll waiters. Removal deletes the cdev, marks the device dead, wakes queued users, disables DMA MRPC, frees coherent memory, drops the PCI reference, and releases the device object.

## State and persistence
Persistent runtime state includes device minors from an IDA, `alive`, `mrpc_queue`, `mrpc_busy`, work items, waitqueues, coherent DMA MRPC buffer and DMA address, MMIO base pointers, partition/PFF topology, event counters, and per-open `switchtec_user` state. Hardware state includes MRPC registers, event-header masks, DMA MRPC enable/address registers, and PCI bus mastering.

## Dependencies and integration points
It depends on `linux/switchtec.h`, `linux/switchtec_ioctl.h`, PCI core probe/remove, cdev and class infrastructure, DMA APIs, IRQ vector allocation, workqueues, waitqueues, poll, user copy helpers, and NTB/autoload integration via `request_module_nowait("ntb_hw_switchtec")` for bridge-class functions.

## Risks
The user ABI is hardware-management sensitive. MRPC command ordering depends on `mrpc_mutex` and the single active queue head. Firmware reset can make BARs inaccessible; `is_firmware_running()` and `alive` protect many paths but MMIO access remains hardware-sensitive. Event index handling must avoid out-of-range MMIO; the port-to-PFF path uses `array_index_nospec()` for bounds hardening. DMA MRPC setup must be disabled and freed on every failure/removal path.

## Test signals
Test probe/remove, module unload with open files and queued commands, blocking and nonblocking MRPC reads, DMA and non-DMA MRPC modes, firmware-not-running timeout behavior, event poll notifications, all ioctl bounds checks, gen3 versus gen4 flash partition reporting, MSI/MSI-X vector allocation, and hot reset or surprise removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/switch/switchtec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/syscall.c -->
# sources/distributed-fs/ceph-client/drivers/pci/syscall.c

## Purpose
`syscall.c` implements legacy `pciconfig_read` and `pciconfig_write` syscalls for direct PCI configuration-space access on architectures that expose them.

## Important APIs, types, and functions
The file defines `SYSCALL_DEFINE5(pciconfig_read, ...)` and `SYSCALL_DEFINE5(pciconfig_write, ...)`. It uses `pci_get_domain_bus_and_slot()`, `pci_user_read_config_byte/word/dword()`, `pci_user_write_config_byte/word/dword()`, `put_user()`, `get_user()`, `capable(CAP_SYS_ADMIN)`, and `security_locked_down(LOCKDOWN_PCI_ACCESS)`.

## Control flow and behavior
Both syscalls target domain 0 only and locate a device by bus and devfn. Reads require `CAP_SYS_ADMIN`, accept lengths 1, 2, or 4, read through PCI user config helpers, and copy the result to userspace. On errors, read writes all ones of the requested width to the user buffer for legacy XFree86 compatibility before returning the errno. Writes require `CAP_SYS_ADMIN` and must not be blocked by kernel lockdown, copy the value from userspace, perform the corresponding config write, and translate PCI config-access failures to `-EIO`.

## State and persistence
No private state is stored. The syscalls can mutate PCI configuration space on writes. Device references acquired by lookup are released before return.

## Dependencies and integration points
It depends on the PCI search helpers in `search.c`, Linux capability checks, lockdown LSM policy, user-copy APIs, and architecture syscall tables.

## Risks
This is a privileged raw hardware access ABI. Reads do not check lockdown, while writes do. Domain 0 targeting is a limitation. The error path intentionally attempts user writes even after earlier failures for ABI compatibility.

## Test signals
Validate permissions without `CAP_SYS_ADMIN`, lockdown write denial, invalid lengths, nonexistent devices, user-copy faults, config read/write error paths, and compatibility behavior where failed reads return all-ones data for sizes 1/2/4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/tph.c -->
# sources/distributed-fs/ceph-client/drivers/pci/tph.c

## Purpose
`tph.c` implements PCIe TLP Processing Hints support. It discovers requester capability, enables and disables TPH modes, manages Steering Tag table entries in either TPH capability space or MSI-X tables, queries ACPI firmware for CPU-local steering tags, and saves/restores TPH state across device power transitions.

## Important APIs, types, and functions
Key exported APIs are `pcie_tph_get_st_table_loc()`, `pcie_tph_get_st_table_size()`, `pcie_tph_get_cpu_st()`, `pcie_tph_set_st_entry()`, `pcie_disable_tph()`, and `pcie_enable_tph()`. PCI core hooks include `pci_restore_tph_state()`, `pci_save_tph_state()`, `pci_no_tph()`, and `pci_tph_init()`. Under ACPI, `union st_info`, `tph_invoke_dsm()`, and `tph_extract_tag()` parse the PCI firmware DSM result.

## Control flow and behavior
Initialization finds the TPH extended capability and allocates a save buffer sized for the control register plus any in-capability ST table entries. Enabling rejects global `notph`, missing capability, duplicate enable, unsupported ST modes, or missing requester/completer support. It chooses 8-bit or extended TPH request type based on device capability and root-port completer support, writes mode and requester-enable fields, and records `pdev->tph_enabled`, `tph_mode`, and `tph_req_type`.

Setting an ST entry requires TPH enabled. It disables requester TPH while updating, writes either the MSI-X TPH tag or capability-table word, disables TPH on write failure, then restores requester enable. ACPI CPU tag lookup maps a Linux CPU to ACPI UID, invokes the root-port DSM, and extracts volatile or persistent-memory steering tags matching the negotiated request type. Save/restore copy the control register and ST entries to or from the PCI saved-capability buffer.

## State and persistence
Persistent state is in `struct pci_dev` fields `tph_cap`, `tph_enabled`, `tph_mode`, and `tph_req_type`, plus saved extended capability data. Hardware state lives in TPH capability control and ST table fields or MSI-X ST storage. `pci_tph_disabled` is a process-wide boot/runtime switch set by `pci_no_tph()`.

## Dependencies and integration points
The file depends on PCIe extended capabilities, root-port discovery, MSI-X TPH tag helpers, ACPI DSM support, ACPI CPU UID mapping, saved capability buffers, and `pci_add_ext_cap_save_buffer()`.

## Risks
The DSM buffer is interpreted as a 64-bit structure and depends on firmware conformance. ST table index bounds only apply to capability-resident tables; MSI-X table errors are delegated. Updating ST entries requires temporarily disabling TPH to avoid device instability. Request-type negotiation must not enable extended TPH unless both requester and completer support it.

## Test signals
Test devices with no TPH, each ST mode, MSI-X and capability ST tables, invalid ST indices, root ports with reduced completer support, ACPI DSM success/failure, `notph`, suspend/resume save-restore, and write failure rollback that disables TPH.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/tph.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/trace.c -->
# sources/distributed-fs/ceph-client/drivers/pci/trace.c

## Purpose
`trace.c` instantiates PCI tracepoints by defining `CREATE_TRACE_POINTS` before including PCI trace event headers.

## Important APIs, types, and functions
There are no runtime functions. The important includes are `<trace/events/pci.h>` and `<trace/events/pci_controller.h>`.

## Control flow and behavior
At build time, this translation unit causes the tracepoint definitions declared in the headers to emit storage and registration data exactly once. Other files can include the same headers without defining tracepoint storage.

## State and persistence
Tracepoint state is managed by the kernel tracing subsystem. This file does not keep private state.

## Dependencies and integration points
It depends on Linux tracepoint infrastructure and the PCI trace event header definitions. It integrates with ftrace/perf/eBPF consumers that subscribe to PCI trace events.

## Risks
The main risk is build/linkage breakage if another translation unit also defines `CREATE_TRACE_POINTS` for the same events, or if event headers are missing declarations.

## Test signals
Build the PCI subsystem, verify no duplicate tracepoint definitions at link time, and confirm PCI events appear under tracing event directories when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/tsm.c -->
# sources/distributed-fs/ceph-client/drivers/pci/tsm.c

## Purpose
`tsm.c` connects PCI devices to platform TEE Security Manager devices for PCIe TDISP and related link/device-security operations. It manages DSM discovery, sysfs connection controls, TDI bind/unbind for confidential guest assignment flows, guest request forwarding, DOE mailbox transfers, and teardown when PCI devices or TSM providers disappear.

## Important APIs, types, and functions
The file uses global `pci_tsm_rwsem`, counts link and device-security TSM providers, and relies on `struct pci_tsm`, `struct pci_tsm_pf0`, `struct pci_tdi`, `struct tsm_dev`, and `struct pci_tsm_ops`. Exported functions include `pci_tsm_unbind()`, `pci_tsm_bind()`, `pci_tsm_guest_req()`, `pci_tsm_tdi_constructor()`, `pci_tsm_link_constructor()`, `pci_tsm_pf0_constructor()`, `pci_tsm_pf0_destructor()`, `pci_tsm_register()`, `pci_tsm_unregister()`, and `pci_tsm_doe_transfer()`. PCI core lifecycle hooks are `pci_tsm_init()` and `pci_tsm_destroy()`.

## Control flow and behavior
A link TSM provider registers with `pci_tsm_register()`, which increments provider counts and exposes sysfs groups for eligible PF0 devices. Users connect a PF0 DSM by writing a `tsmN` device name to `tsm/connect`; `pci_tsm_connect()` probes provider state, takes the PF0 lock, calls provider `connect()`, then probes dependent functions and VFs with `probe_fn()`. `find_dsm_dev()` resolves the DSM for a device from PF0 or an upstream port. `pci_tsm_init()` later probes newly appearing dependent functions when a DSM already exists.

Binding uses `pci_tsm_bind()` under the read semaphore and PF0 mutex to create a `struct pci_tdi` for a KVM private-memory context. `pci_tsm_guest_req()` validates request scope, verifies a bound TDI, and forwards guest payloads to provider `guest_req()`. Unbind and disconnect walk functions in reverse order, unbind TDIs, remove per-function contexts, call provider disconnect, and hide sysfs when the last provider unregisters. DOE transfer requires a PF0 TSM with a CMA DOE mailbox.

## State and persistence
Persistent state includes `pdev->tsm`, DSM pointers, PF0 locks, TDI pointers, provider counts, sysfs group visibility, and DOE mailbox references. The read/write semaphore serializes provider registration, connect/disconnect, per-device init/destroy, and guest operations.

## Dependencies and integration points
It depends on PCIe TEE capability bits, SR-IOV enumeration helpers, PCI DOE, TSM core device lookup, sysfs visible groups, KVM contexts, xarray-including headers for provider internals, and PCI search helpers for PF/VF walking.

## Risks
This is security-sensitive orchestration. Races between provider unregister, PCI removal, sysfs connect/disconnect, VF creation, and guest requests are mitigated by `pci_tsm_rwsem` and PF0 mutexes but remain the key risk. Provider callbacks are trusted to implement correct security transitions. Scope filtering in `pci_tsm_guest_req()` prevents unrelated guest commands from being proxied.

## Test signals
Test provider register/unregister, PF0 connect/disconnect, sysfs visibility, VF and multifunction probing, bind idempotence and conflicting KVM contexts, guest request scope rejection, teardown while bound, DOE mailbox absence, and reverse-order unbind during PCI removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/tsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/vc.c -->
# sources/distributed-fs/ceph-client/drivers/pci/vc.c

## Purpose
`vc.c` saves, restores, and re-enables PCIe Virtual Channel capabilities across reset and power-management transitions. It supports VC, VC9, and MFVC extended capabilities, including arbitration tables and per-resource control registers.

## Important APIs, types, and functions
Public PCI core hooks are `pci_save_vc_state()`, `pci_restore_vc_state()`, and `pci_allocate_vc_save_buffers()`. Internal helpers include `pci_vc_save_restore_dwords()`, `pci_vc_load_arb_table()`, `pci_vc_load_port_arb_table()`, `pci_vc_enable()`, and `pci_vc_do_save_buffer()`. The `vc_caps[]` table maps extended capability IDs to display names.

## Control flow and behavior
`pci_allocate_vc_save_buffers()` scans for MFVC, VC, and VC9 capabilities, asks `pci_vc_do_save_buffer()` for the exact serialized size, and allocates saved-capability buffers. Save and restore later repeat the scan and serialize or replay state in the same order.

`pci_vc_do_save_buffer()` reads capability metadata, saves/restores the port control register first, handles the VC arbitration table when low-priority VCs and an arbitration offset exist, then iterates each VC resource. For each resource it saves/restores optional port arbitration table data and the resource control register. On restore, it preserves any existing enable bit from FLR-surviving config, reloads arbitration tables when selected, and calls `pci_vc_enable()` when a VC must be re-enabled. `pci_vc_enable()` enables matching VC IDs on both downstream and upstream link ends when possible and waits for negotiation to finish.

## State and persistence
State is persisted in PCI saved extended capability buffers and restored to config space. Hardware state includes VC port control, VC arbitration tables, per-resource arbitration tables, resource control registers, and negotiation status bits.

## Dependencies and integration points
It depends on PCIe extended capability access, `pci_wait_for_pending()`, saved capability buffer management, downstream port detection, and upstream link matching through `dev->bus->self`.

## Risks
The buffer-size calculation must exactly match save/restore layout or restore returns `-ENOMEM`. Negotiation can remain pending and is only logged. Link-end matching by VC ID is best effort and skips root-bus or VC9 cases where the opposite endpoint is unavailable or unclear.

## Test signals
Test devices with VC, VC9, MFVC, multiple VC resources, arbitration table offsets and phase sizes, FLR followed by restore, missing upstream VC capability, stuck negotiation status, and saved-buffer size mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/vc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/vgaarb.c -->
# sources/distributed-fs/ceph-client/drivers/pci/vgaarb.c

## Purpose
`vgaarb.c` implements VGA legacy-resource arbitration for systems with multiple VGA-class PCI devices. It coordinates ownership of legacy VGA I/O and memory ranges, exposes kernel APIs for GPU drivers, provides the `/dev/vga_arbiter` userspace ABI, tracks the default boot VGA device, and reacts to PCI hotplug notifications.

## Important APIs, types, and functions
The central type is `struct vga_device`, which tracks a PCI device, decoded resources, owned resources, locks, per-resource counters, bridge-control eligibility, firmware-default status, and an optional client `set_decode()` callback. Exported APIs include `vga_default_device()`, `vga_set_default_device()`, `vga_remove_vgacon()`, `vga_get()`, `vga_put()`, `vga_set_legacy_decoding()`, and `vga_client_register()`. Userspace state uses `struct vga_arb_private` and `struct vga_arb_user_card`. The miscdevice file operations implement read, write, poll, open, and release.

## Control flow and behavior
Initialization registers `/dev/vga_arbiter`, registers a PCI bus notifier, and scans existing PCI devices for VGA class. Adding a VGA device initializes default decodes, derives owned legacy resources from command bits and bridge VGA forwarding, selects a boot default based on firmware framebuffer, legacy decode, integrated GPU, and enabled non-legacy devices, checks whether bridge VGA forwarding can control the device exclusively, and appends it to `vga_list`.

`vga_get()` calls `vga_check_first_use()` to notify registered clients on first arbitration use, finds the target, and tries to acquire requested resources. `__vga_tryget()` expands normal-resource requests to legacy locks when needed, detects conflicts, disables conflicting owners via `pci_set_vga_state()`, enables the target's decode and bridge routing, updates ownership, and increments lock counters. If a conflicting device holds locks, `vga_get()` waits on `vga_wait_queue`; `vga_tryget()` returns busy. `vga_put()` decrements counters and wakes waiters when lock bits clear.

The userspace ABI parses text commands: `target`, `lock`, `trylock`, `unlock`, `unlock all`, and `decodes`. Open defaults to the current default device and release unwinds all locks held by the file descriptor. Reads return a status line with decode, ownership, and lock counts. PCI add/remove notifications update the arbiter and notify clients.

## State and persistence
Global state includes `vga_list`, `vga_count`, `vga_decode_count`, `vga_arbiter_used`, `vga_default`, `vga_lock`, `vga_wait_queue`, and `vga_user_list`. State is in-memory only, but it directly affects PCI command bits and bridge VGA forwarding through `pci_set_vga_state()`. File descriptors persist per-client lock accounting until release.

## Dependencies and integration points
It integrates with PCI device hotplug notifiers, VGA console removal, sysfb firmware default detection on x86, ACPI integrated-GPU detection, GPU driver decode callbacks, miscdevice registration, waitqueues, spinlocks, and the documented vgaarbiter userspace ABI.

## Risks
This code touches legacy decode routing with global effects. Lock counter mismatches can deadlock users or leave resources owned. Bridge sharing logic is conservative but complex in multi-bridge topologies. Userspace command parsing is string-based and has legacy quirks, including treating `io` or `mem` requests as `io+mem` to avoid deadlocks. Hot removal must wake waiters and invalidate userspace targets.

## Test signals
Test multi-GPU systems across shared and separate bridges, default-device selection, driver `set_decode()` callbacks, `/dev/vga_arbiter` command parsing and release cleanup, blocking and trylock contention, hotplug add/remove, VGA console removal, and wakeups after unlock or device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/vgaarb.c -->
