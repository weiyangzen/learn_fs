# subset-b-000832 research

This grouped report covers the subset B s390 PCI, s390 purgatory/tooling, and SuperH architecture/board files requested for `subset-b-000832`. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_bus.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_bus.c

Purpose: This file binds s390 zPCI function objects (`struct zpci_dev`) to Linux PCI buses, PCI core devices, hotplug slots, MSI domains, and DMA ranges. It is the zPCI bus lifecycle layer: create/find a `struct zpci_bus`, create the root PCI bus, attach functions to devfn slots, scan/remove devices, and free bus state when the last reference drops.

Important APIs/types/functions: Global state is `zbus_list`, `zbus_list_lock`, and `zpci_nb_devices`. Public entry points are `zpci_bus_device_register`, `zpci_bus_device_unregister`, `zpci_bus_scan_device`, `zpci_bus_remove_device`, `zpci_bus_scan_bus`, `zpci_bus_get_next`, and `pcibios_bus_add_device`. Internal helpers include `zpci_bus_prepare_device`, `zpci_bus_create_pci_bus`, `zpci_bus_alloc`, `zpci_bus_get`, `zpci_bus_put`, `zpci_bus_add_device`, `pci_dma_range_setup`, and isolated-VF/multifunction detection helpers.

Control flow: Registration first enforces the zPCI device limit, chooses a topology key from TID or PCHID, reuses an existing multifunction bus when possible, allocates a new bus otherwise, creates the root bus and parent MSI domain if needed, then inserts the function into `zbus->function[devfn]` and initializes its hotplug slot. Scan paths enable the function, set up BAR resources, add resources to the root bus, and call into generic PCI scanning/add-device APIs under `pci_lock_rescan_remove`. Removal finds the PCI core device by slot, optionally marks permanent failure, handles virtual functions through the IOV helper, and otherwise removes the bus device under the PCI lock.

State and persistence: Bus state persists in `struct zpci_bus` until its kref reaches zero. The bus owns the domain number, root `pci_bus`, resource list, parent MSI domain, topology key, function table, and list membership. `struct zpci_dev` stores its bus pointer, devfn, hotplug-slot state, resource setup state, and DMA aperture; registration increments global device count and unregistration clears the function slot. DMA range state is installed into the PCI device with `dma_direct_set_offset`.

Dependencies and integration points: It depends on CLP-discovered zPCI metadata, `asm/pci_dma.h`, generic PCI root-bus/device scanning, IRQ/MSI domain creation from `pci_irq.c`, SR-IOV helpers from `pci_iov.c`, hotplug slot support, and DMA-direct offset mapping. It is called by zPCI discovery/event code when functions are configured, deconfigured, scanned, or removed.

Risks and test signals: Refcount/list locking is central: `zpci_bus_release` intentionally drops `zbus_list_lock` while tearing down resources, and iterator callers must use `zpci_bus_get_next` correctly. Domain allocation, MSI domain removal, and resource-list ownership must stay paired across failure paths. Multifunction RID/devfn assignment and isolated VF bus selection can misplace devices if CLP metadata is stale. Useful tests are zPCI hotplug add/remove, repeated scan/remove cycles, SR-IOV VF probing, multifunction devices with RID enabled/disabled, maximum-device limit, DMA aperture checks, and failure injection around root-bus/MSI-domain allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_bus.h -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_bus.h

Purpose: This private s390 PCI header exposes bus, device-registration, scan/remove, zdev reference, domain, and resource helpers shared by the zPCI implementation files.

Important APIs/types/functions: It declares `zpci_bus_device_register`, `zpci_bus_device_unregister`, `zpci_bus_scan_bus`, `zpci_bus_get_next`, `zpci_bus_scan_device`, `zpci_bus_remove_device`, `zpci_release_device`, `zpci_zdev_put`, `zpci_alloc_domain`, `zpci_free_domain`, and `zpci_setup_bus_resources`. Inline helpers are `zpci_zdev_get` for kref acquisition and `zdev_from_bus` for recovering the root zPCI device from `pci_bus->sysdata`.

Control flow: Discovery, event, and hotplug code include this header to move zPCI functions through allocation, registration, scanning, removal, and final kref release. The `zdev_from_bus` helper maps generic PCI bus callbacks back to the s390-specific bus/function table.

State and persistence: The header defines no storage, but its API contracts control lifetimes for `struct zpci_dev` and `struct zpci_bus`. Kref helpers make zdev references explicit and rely on `zpci_release_device` as the final release callback.

Dependencies and integration points: It depends on `asm/pci.h`/zPCI core definitions and generic PCI `struct pci_bus`. It connects `pci_bus.c` to CLP discovery, event handling, hotplug, resource setup, and PCI core callbacks.

Risks and test signals: Incorrect reference ownership around `zpci_zdev_get`/`zpci_zdev_put` can leak or prematurely free zdevs. Callers must not use `zdev_from_bus` on a bus whose `sysdata` is not a zPCI bus. Build coverage across PCI-enabled s390 configs and hotplug stress tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_clp.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_clp.c

Purpose: This file implements s390 Call Logical Processor access for PCI discovery, PCI function query/group query, function enable/disable/MIO enable, function-handle refresh, state lookup, and the `/dev/clp` misc ioctl interface.

Important APIs/types/functions: Public kernel APIs include `update_uid_checking`, `clp_query_pci_fn`, `clp_setup_writeback_mio`, `clp_enable_fh`, `clp_disable_fh`, `clp_scan_pci_devices`, `clp_refresh_fh`, and `clp_get_state`. Low-level CLP helpers are `clp_get_ilp`, `clp_req`, `clp_alloc_block`, `clp_free_block`, query/store helpers, `clp_set_pci_fn`, list/find callbacks, and ioctl handlers `clp_misc_ioctl`, `clp_normal_command`, and `clp_immediate_command`.

Control flow: Kernel discovery allocates a CLP block, issues `CLP_LIST_PCI` in a resume-token loop, skips empty vendor entries, creates zPCI devices for new functions, and returns them on a scan list. Query flow issues `CLP_QUERY_PCI_FN`, stores BAR/DMA/topology/RID/TID/MIO/util-string data into `struct zpci_dev`, then queries the PCI function group for MSI, DMA mask, FMB, TLB refresh, and bus-speed capability. Enable flow issues `CLP_SET_PCI_FN` with retries on busy responses, and if MIO is usable follows with `CLP_SET_ENABLE_MIO`; failure disables the function again.

State and persistence: `zpci_unique_uid` records firmware UID-checking status and is updated while listing functions. CLP responses populate persistent zPCI device fields such as function handle, DMA limits, PCHID, PFGID, UID, RID, TID, VFN, PFIP, util string, BARs, MSI address/count, max store-block data, and MIO write-back addresses. The CLP blocks are page allocations freed after each request.

Dependencies and integration points: It depends on s390 CLP instruction encoding, exception tables, CLP UAPI structures, zPCI debug logging, `pci_bus.h` device creation/reference helpers, MIO state from PCI I/O code, and the miscdevice subsystem. `/dev/clp` validates user-supplied request blocks before forwarding supported base and PCI CLP commands to firmware.

Risks and test signals: CLP block length, reserved field, response-code, and endian handling are firmware ABI-sensitive. Busy retry loops must avoid unbounded waits, and enabling MIO must roll back correctly if the second command fails. `/dev/clp` exposes privileged firmware command paths, so copy-from/to-user, length limits, and command whitelists are important. Tests include boot-time PCI enumeration, UID-checking sysfs changes, enable/disable under z/VM and LPAR, MIO-capable and non-MIO devices, CLP list resume-token coverage, and ioctl negative tests for malformed request blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_clp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_debug.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_debug.c

Purpose: This file provides s390 zPCI debug buffers and per-device debugfs statistics for firmware measurement blocks and software IOMMU counters.

Important APIs/types/functions: It exports `pci_debug_msg_id` and `pci_debug_err_id`. Public lifecycle hooks are `zpci_debug_init`, `zpci_debug_exit`, `zpci_debug_init_device`, and `zpci_debug_exit_device`. Debugfs file operations are built around `pci_perf_show`, `pci_perf_seq_write`, and `pci_perf_seq_open`; display helpers include `pci_fmb_show` and `pci_sw_counter_show`.

Control flow: Global initialization registers two s390 debug feature buffers, installs sprintf/hex-ascii views, sets debug level, and creates `/sys/kernel/debug/pci`. Per-device initialization creates a device directory and `statistics` file. Reads lock `zdev->fmb_lock`, print FMB header/common counters, dispatch on FMB format-specific counter layout, then append software IOMMU counters under `dom_lock`. Writes parse `0` or `1` to disable or enable FMB collection.

State and persistence: Persistent state is the debug feature handles, debugfs root and per-device dentries, active FMB pointer/data in each zdev, and IOMMU counter atomics. Debugfs state is runtime-only and disappears at module/arch teardown or device exit.

Dependencies and integration points: It depends on Linux debugfs, seq_file, s390 `debug.h`, zPCI FMB enable/disable APIs, and `zpci_get_iommu_ctrs` from PCI DMA support. It integrates with diagnostic tooling and zPCI error/event logging.

Risks and test signals: Locking must prevent FMB teardown while statistics are read or toggled. Counter format interpretation must match firmware-provided FMB format bits, and missing FMB state should report disabled rather than dereferencing NULL. Tests include reading and toggling debugfs statistics, device hot-unplug while statistics are open, FMB formats 0-3, and debug feature registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_event.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_event.c

Purpose: This file handles s390 zPCI firmware event payloads for PCI function errors and availability changes. It translates content-code data fields into PCI error recovery, permanent failure notification, device creation, configuration, deconfiguration, reservation, and rescanning.

Important APIs/types/functions: Event payload structures are `struct zpci_ccdf_err` and `struct zpci_ccdf_avail`. Public handlers are `zpci_event_error` and `zpci_event_availability`. Error-recovery helpers include `zpci_event_attempt_error_recovery`, `zpci_event_notify_error_detected`, `zpci_event_do_error_state_clear`, `zpci_event_do_reset`, `zpci_event_io_failure`, `is_passed_through`, and `is_driver_supported`. Availability helpers include `zpci_event_hard_deconfigured` and `zpci_event_reappear`.

Control flow: Error events refresh the current function handle via CLP, ignore stale events, find the PCI device, log the CCDF, and branch on the PCI event code. FMB-related events are informational, permanent-failure events notify the driver, and recoverable events run the PCI error-recovery sequence: lock the device, freeze channel state, reject passthrough/no-driver/no-ERS cases, call `error_detected`, optionally unblock load/store and DMA, optionally hot-reset the zPCI device and call `slot_reset`, then call `resume` and emit ERS uevents on success. Availability events branch by PEC: create/scan configured or standby devices, refresh handles, deconfigure configured devices, hard-remove devices that transitioned to standby/reserved, rescan multiple-device changes, or mark functions reserved.

State and persistence: The file mutates `struct zpci_dev` state (`CONFIGURED`, `STANDBY`, `RESERVED`), function handles, zdev references, PCI device `error_state`, and driver-visible ERS state. It uses `state_lock`, `device_lock`, and PCI device locking to serialize state changes and recovery with probe/remove/userspace access.

Dependencies and integration points: It depends on CLP handle/state lookup, zPCI bus removal/scanning, zPCI enable/disable/reset helpers, PCI ERS driver callbacks, PCI uevents, passthrough KVM/vfio association (`zdev->kzdev`), SCLP event delivery, and `pci_report.c` status reporting.

Risks and test signals: Stale function handles can cause recovery of the wrong function if not filtered. Lock ordering among zdev state locks, PCI device locks, and remove/rescan paths must remain deadlock-free. Driver callback return semantics are subtle, especially `NONE`, `NEED_RESET`, and aborting results. Tests should cover recoverable load/store-blocked events, reset-required events, permanent failures, passthrough devices, unbound drivers, reserved/reappearing functions, queued stale events, multi-device rescan PEC 0x0306, and status reports emitted for each recovery outcome.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_fixup.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_fixup.c

Purpose: This small fixup file applies an s390-specific PCI quirk to IBM ISM devices so their BARs are not mmap-capable.

Important APIs/types/functions: The only helper is `zpci_ism_bar_no_mmap(struct pci_dev *pdev)`, registered with `DECLARE_PCI_FIXUP_HEADER` for IBM vendor/device IDs matching ISM.

Control flow: During PCI header fixup, matching devices iterate over their resources and clear mmap permission flags from BAR resources. This prevents user mappings for device memory that should be accessed through the s390-specific path or not exposed at all.

State and persistence: The persistent effect is mutation of PCI resource flags in the kernel's `pci_dev` resource array. There is no separate state.

Dependencies and integration points: It depends on generic PCI fixup registration and IBM device IDs. It integrates with the resource permission checks used later by sysfs/resource mmap and user-space MMIO paths.

Risks and test signals: Overmatching would unnecessarily block mmap for unrelated devices; undermatching would leave unsafe mappings available for ISM. Tests are PCI enumeration of ISM hardware, inspection of resource mmap permissions, and negative coverage for non-ISM IBM devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_fixup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_insn.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_insn.c

Purpose: This file wraps s390 PCI-specific instructions for function modification, translation refresh, interrupt control, load/store, block store, MIO access, and PCI write barriers.

Important APIs/types/functions: Exported APIs are `zpci_mod_fc`, `zpci_set_irq_ctrl`, `__zpci_load`, `zpci_load`, `__zpci_store`, `zpci_store`, `__zpci_store_block`, `zpci_write_block`, and `zpci_barrier`. Internal instruction wrappers include `__mpcifc`, `__rpcit`, `____pcilg`, `__pcilg`, `zpci_load_fh`, `__pcilg_mio`, `__pcistg`, `zpci_store_fh`, `__pcistg_mio`, `__pcistb`, `zpci_write_block_fh`, `__pcistb_mio`, and `__pciwb_mio`.

Control flow: Callers pass a function-handle request or MIO address/length. The wrapper emits inline assembly, translates s390 condition codes, extracts status bytes, logs failures with request/address context, and returns Linux error codes for instruction failures. Public load/store APIs choose legacy function-handle instructions or MIO instructions depending on whether the I/O address is a zPCI encoded address and the MIO static branch is active. Block writes loop through instruction-sized chunks when needed.

State and persistence: The file itself owns no persistent state. It mutates device/host hardware state by issuing zPCI instructions, refreshes DMA translations with RPCIT, registers interrupt control through SIC, performs MMIO loads/stores, and orders writes with the MIO write barrier.

Dependencies and integration points: It depends on s390 inline-asm instruction encodings, exception-table handling, condition-code helpers, zPCI address encoding, MIO static key state, and zPCI debug logging. It is used by CLP enable paths, MSI setup, DMA translation flushing, PCI config/MMIO accessors, and user-space MMIO syscalls.

Risks and test signals: Instruction operand packing and status interpretation are architecture ABI-sensitive. MIO versus function-handle address selection must be exact, and partial transfer lengths must not cross instruction-imposed boundaries. Tests include config/MMIO reads and writes of 1/2/4/8/block sizes, MIO enabled/disabled systems, RPCIT refresh failures, SIC IRQ mode changes, exception injection, and write-barrier ordering on real or emulated s390 PCI hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_iov.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_iov.c

Purpose: This file provides s390-specific SR-IOV wiring for virtual functions whose platform representation is a zPCI function rather than a normal PCI-discovered child.

Important APIs/types/functions: Public helpers are `zpci_iov_map_resources`, `zpci_iov_remove_virtfn`, `zpci_iov_find_parent_pf`, and `zpci_iov_setup_virtfn`. Internal state includes the synthetic `iov_res` resource and `zpci_iov_link_virtfn`.

Control flow: Resource mapping replaces VF resources with offsets into a synthetic IOV resource window. During `pcibios_bus_add_device`, VFs call `zpci_iov_setup_virtfn`, which finds the parent PF by scanning the zbus function table for a physical function with matching FID parameter, links the VF into the PF's SR-IOV arrays, sets VF fields such as `is_virtfn`, `physfn`, and `no_command_memory`, and arranges sysfs links. Removal tears down the PF/VF relationship.

State and persistence: VF state persists in generic `struct pci_dev` fields and in zPCI metadata (`vfn`, `fidparm`, parent bus table). The synthetic IOV resource describes VF BAR ranges rather than firmware-owned BAR resources.

Dependencies and integration points: It depends on `CONFIG_PCI_IOV`, generic PCI SR-IOV structures, zPCI bus/function tables, sysfs PF/VF links, and s390 PCI BAR resource setup. It is called from bus add/remove code.

Risks and test signals: PF matching by FID parameter must not associate a VF with the wrong physical function. Refcounting on `physfn` and slot lookups must be balanced. Resource remapping must preserve VF BAR sizes and flags. Tests include PF with multiple VFs, isolated VF discovery before PF discovery, VF removal, sysfs virtfn links, driver binding to VFs, and no-IOV build coverage through header stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_iov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_iov.h -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_iov.h

Purpose: This private header exposes zPCI SR-IOV helper APIs with real declarations under `CONFIG_PCI_IOV` and no-op/error stubs otherwise.

Important APIs/types/functions: It declares or stubs `zpci_iov_remove_virtfn`, `zpci_iov_map_resources`, `zpci_iov_setup_virtfn`, and `zpci_iov_find_parent_pf`.

Control flow: Bus code includes this header unconditionally. With IOV enabled, VF setup/removal and resource mapping perform real work; without it, callers compile away VF support and `zpci_iov_setup_virtfn`/`find_parent_pf` report failure/NULL.

State and persistence: The header owns no state. Its stubs define behavior for configurations where SR-IOV is unavailable.

Dependencies and integration points: It depends on `struct pci_dev`, `struct zpci_bus`, and `struct zpci_dev`, and integrates `pci_bus.c` with `pci_iov.c` conditionally.

Risks and test signals: Stub return values must keep non-IOV builds safe: a zPCI VF in such a build should fail setup rather than being partially linked. Build tests should cover `CONFIG_PCI_IOV=y` and `n`; runtime tests should cover VF setup only on IOV builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_iov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_irq.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_irq.c

Purpose: This file implements zPCI MSI delivery over s390 adapter interrupts. It supports floating interruption delivery and CPU-directed interruption delivery, allocates adapter interrupt vectors, creates per-bus parent MSI domains, composes MSI messages, handles adapter interrupt dispatch, and tears down IRQ state.

Important APIs/types/functions: Public APIs are `zpci_set_irq`, `arch_restore_msi_irqs`, `zpci_create_parent_msi_domain`, `zpci_remove_parent_msi_domain`, `zpci_irq_init`, and `zpci_irq_exit`. Key state is `irq_delivery`, `zpci_sbv`, `zpci_ibv`, `zpci_airq`, `zpci_irq_chip`, `zpci_msi_parent_ops`, and per-CPU `struct cpu_irq_data`. Major helpers include floating/directed register/unregister functions, vector allocation/free functions, `zpci_compose_msi_msg`, adapter interrupt handlers, MSI domain alloc/free/prepare/teardown callbacks, and directed-IRQ CPU setup.

Control flow: Init selects directed mode when SCLP advertises it unless forced to floating, registers an adapter interrupt handler, allocates summary and interrupt bit vectors, and enables single IRQ mode. MSI preparation allocates either per-device floating summary/vector bits or directed per-CPU vector bits, stores the first bit/count in the zdev, and registers adapter interrupts via Modify PCI Function Controls. MSI domain allocation maps Linux virqs to encoded hwirqs, stores parent domain pointers and hwirq data in adapter vectors, and generic interrupt handling later uses those vector entries to dispatch. Floating handlers scan summary bits and then per-device interrupt bits; directed handlers process local CPU vectors or schedule remote CPUs from the fallback summary vector.

State and persistence: Persistent IRQ state includes global adapter vectors, per-CPU directed vectors, per-device `aibv`, `aisb`, `msi_first_bit`, and `msi_nr_irqs`, per-bus parent MSI domains and fwnodes, and MSI descriptor hwirq mappings. Teardown clears firmware interrupt registration, vector data/pointers, allocated bits, IRQ domain state, fwnodes, and adapter interrupt registration.

Dependencies and integration points: It depends on s390 adapter interrupt (`airq`) infrastructure, SCLP directed-IRQ capability, SIC instruction wrappers from `pci_insn.c`, Linux MSI parent-domain APIs, generic IRQ domain handling, SMP call-single support, and zPCI bus/domain objects. PCI core restore hooks call back into `zpci_set_irq`.

Risks and test signals: Bit-vector allocation differs by mode and must pair precisely with free paths. Directed mode shares allocation on CPU 0's vector but mirrors data to all CPU vectors; affinity changes affect MSI message address composition. Fallback dispatch schedules remote CPUs asynchronously and relies on atomic coalescing. Tests include boot in floating and directed modes, forced floating, MSI/MSI-X allocation/free, affinity updates, CPU hotplug or possible-CPU variation, adapter interrupt storm handling, device teardown with pending interrupts, and restore-after-reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_kvm_hook.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_kvm_hook.c

Purpose: This file defines and exports the zPCI KVM hook table used to connect the host zPCI layer with optional KVM/vfio passthrough support.

Important APIs/types/functions: It defines `struct zpci_kvm_hook zpci_kvm_hook` and exports it with `EXPORT_SYMBOL_GPL`.

Control flow: There is no local control flow. Other modules install or inspect callbacks through the exported hook object, and zPCI code can use those hooks when passthrough state is present.

State and persistence: The exported `zpci_kvm_hook` object is global kernel state. Its callback fields persist for the lifetime of the module/kernel and must be managed by users of the hook contract.

Dependencies and integration points: It depends on the zPCI KVM hook type from s390 PCI headers and integrates zPCI with KVM/vfio passthrough event/error paths.

Risks and test signals: Because the hook is a global mutable callback table, registration/unregistration ordering and NULL checks in consumers matter. Tests should cover builds with and without KVM/vfio support, passthrough device error events, and module unload paths that clear callbacks before code disappears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_kvm_hook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_mmio.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_mmio.c

Purpose: This file implements the s390-specific user-space PCI MMIO syscalls, including fast MIO in-user access and fallback access through PFN-mapped VMAs.

Important APIs/types/functions: Syscall entry points are `s390_pci_mmio_write` and `s390_pci_mmio_read`. Internal helpers include `__memcpy_toio_inuser`, `__memcpy_fromio_inuser`, `__pcistb_mio_inuser`, `__pcistg_mio_inuser`, `__pcilg_mio_inuser`, and `zpci_err_mmio`.

Control flow: Both syscalls first require zPCI to be enabled and constrain requests to a positive length within one page. On systems with MIO, they directly run PCI load/store instructions while temporarily enabling secondary-address-space user access. Without MIO, writes copy user data into a kernel buffer, validate that the supplied address belongs to a readable/writable `VM_IO|VM_PFNMAP` VMA, fault in and pin the PFN map, translate PFN plus page offset into a zPCI I/O address, verify it is in the zPCI IOMAP range, and call kernel `zpci_memcpy_toio/fromio`. Reads then copy the kernel buffer back to user space.

State and persistence: The file does not maintain persistent state. It temporarily changes SACF access mode during in-user MIO instructions, takes the current process mmap read lock, uses transient buffers, and logs MMIO errors with condition-code/status/offset data.

Dependencies and integration points: It depends on s390 PCI I/O instruction helpers, exception tables, `have_mio` static branch, zPCI address layout, Linux VMA/PFNMAP APIs, user copy helpers, and syscall registration. It is the user-visible path for applications that need raw PCI MMIO on s390.

Risks and test signals: User-address handling is high risk: SACF mode must always be restored, partial copy counts must turn into `-EFAULT`, and VMA permission checks must reject non-MMIO mappings. The one-page length restriction prevents crossing mappings. MIO and fallback paths must agree on error semantics. Tests include read/write sizes 1-64 and larger, invalid pointers, unmapped or wrong-permission VMAs, addresses below `ZPCI_IOMAP_ADDR_BASE`, page-boundary rejection, MIO fast path, fallback path, and fault injection in follow_pfnmap/copy_to_user/copy_from_user.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_report.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_report.c

Purpose: This file reports zPCI recovery/status events into the s390 debug feature using a custom prolog that includes operation, status, PCI channel state, FID, and FH.

Important APIs/types/functions: The exported function is `zpci_report_status(struct zpci_dev *zdev, const char *operation, const char *status)`. Local structures are `struct zpci_report_error_data` and `struct zpci_report_error`; helpers include `zpci_state_str`, `debug_log_header_fn`, `debug_prolog_header`, and `debug_log_view`.

Control flow: A caller supplies zdev plus operation/status strings. The function builds a small packed record containing channel state and function identifiers, then logs it through `debug_event` with a view whose prolog prints a human-readable header.

State and persistence: Report data is persisted only in the in-memory s390 debug log buffer. It snapshots zPCI function handle/id and PCI channel state at report time.

Dependencies and integration points: It depends on s390 `debug.h`, zPCI debug feature registration, PCI channel state enums, and event/recovery code in `pci_event.c`.

Risks and test signals: Operation/status strings are stored as pointers in the debug event data path, so callers should pass static or otherwise long-lived strings. State-string mapping must cover relevant PCI channel states. Tests include recovery success/failure events, debugfs/debug feature output formatting, and NULL or removed-device avoidance by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_report.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_report.h -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_report.h

Purpose: This private header declares the zPCI status-reporting helper used by event/recovery code.

Important APIs/types/functions: It forward-declares `struct zpci_dev` and declares `zpci_report_status`.

Control flow: There is no local control flow; callers include this header to report recovery/status strings against a zPCI device.

State and persistence: The header owns no state. Its function contract snapshots device status into the s390 debug log in the implementation.

Dependencies and integration points: It integrates `pci_event.c` with `pci_report.c` without exposing debug internals.

Risks and test signals: Build failures would catch signature drift. Runtime signal is debug-log entries from zPCI recovery paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_report.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_sysfs.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_sysfs.c

Purpose: This file defines zPCI sysfs attributes for PCI function identity, firmware metadata, MIO state, recovery control, util string, error reporting, UID uniqueness, PFIP segments, slot UID, and firmware-wide CLP UID checking.

Important APIs/types/functions: Generated read-only attributes expose `function_id`, `function_handle`, `pchid`, `pfgid`, `vfn`, `pft`, `port`, `fidparm`, `uid`, and PFIP segments. Other handlers include `mio_enabled_show`, `recover_store`, `util_string_read`, `report_error_write`, `uid_is_unique_show`, `uid_checking_show`, `index_show`, and `zpci_uid_slot_show`. Exported attribute groups include `zpci_attr_group`, `pfip_attr_group`, `zpci_slot_attr_group`, `zpci_ident_attr_group`, and `__zpci_fw_sysfs_init`.

Control flow: Attribute reads format zdev fields directly. The `recover` write breaks sysfs active protection, serializes on `state_lock` and PCI rescan/remove lock, removes the sysfs file to coalesce concurrent calls, removes the PCI core device, disables the zPCI function if needed, reenables it, and rescans the bus. `report_error` forwards a user-provided report header to SCLP for the current FH/FID. Firmware sysfs initialization creates a `clp` group under `firmware_kobj`.

State and persistence: Sysfs reflects persistent zdev CLP metadata and UID-checking state. Recovery mutates the PCI device tree and zPCI enabled state. The `index` attribute is visible only when firmware guarantees unique UIDs.

Dependencies and integration points: It depends on generic PCI sysfs internals, zPCI state locks and reenable/disable helpers, SCLP PCI report support, `zpci_unique_uid` from CLP code, firmware kobjects, and PCI slot attributes.

Risks and test signals: Recovery has delicate lock ordering because sysfs active protection can deadlock with PCI remove/rescan if not broken. `report_error` trusts the binary attribute size and should reject offsets/short writes. Attribute visibility must update correctly with UID-checking state. Tests include reading all attributes after discovery, writing `recover` during normal and error states, concurrent recover writes, bus rescan after recovery, report-error writes with invalid sizes/offsets, and firmware `clp/uid_checking` visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/Makefile -->
# sources/distributed-fs/ceph-client/arch/s390/purgatory/Makefile

Purpose: This Makefile builds the standalone s390 kexec purgatory binary, validates it for unresolved symbols, strips it to a relocatable read-only object, and embeds it into the kernel through `kexec-purgatory.o`.

Important APIs/types/functions: It defines `purgatory-y`, `PURGATORY_OBJS`, custom rules for `sha256.o` from `lib/crypto/sha256.c`, `mem.o` from `arch/s390/lib/mem.S`, targets `purgatory`, `purgatory.chk`, and `purgatory.ro`, and object inclusion `obj-y += kexec-purgatory.o`.

Control flow: Kbuild compiles freestanding purgatory objects with special CFLAGS, links `purgatory` with the linker script and `-r`, links `purgatory.chk` without `-r` to catch unresolved symbols, objcopies `purgatory.ro` while removing debug/comment/note sections, then assembles `kexec-purgatory.o` that incbins the stripped artifact.

State and persistence: The output artifact `purgatory.ro` becomes embedded kernel rodata. The Makefile intentionally avoids normal kernel runtime instrumentation, exports, stack protector, builtins, PIE, and branch profiling so the purgatory can run between kernels.

Dependencies and integration points: It depends on Kbuild, the s390 linker, objcopy, crypto SHA-256 source, s390 mem assembly, `purgatory.lds.S`, and `kexec-purgatory.S`. It integrates with the s390 kexec image loader.

Risks and test signals: Freestanding flags must stay strict because purgatory cannot rely on kernel runtime services. `purgatory.chk` is the unresolved-symbol gate. Tests include `make arch/s390/purgatory/`, kexec/kdump boot paths, objdump/readelf inspection for unwanted sections or relocations, and compiler variation with GCC/Clang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/head.S -->
# sources/distributed-fs/ceph-client/arch/s390/purgatory/head.S

Purpose: This assembly file is the s390 purgatory entry and transition code that verifies the next kernel image, optionally returns to the old kernel for crash-check-only mode, swaps crash memory into address zero, and starts the next kernel with `diag 0x308`.

Important APIs/types/functions: The main exported code symbol is `purgatory_start`. Macros include `MEMCPY`, `MEMSWAP`, and `START_NEXT_KERNEL`. The code references purgatory data symbols such as `kernel_entry`, `load_psw_mask`, `kernel_type`, `crash_start`, `crash_size`, `purgatory_sha_regions`, `purgatory_end`, `stack`, `gprregs`, and `disabled_wait_psw`, and calls `verify_sha256_digest`.

Control flow: Entry sets architecture/addressing mode, saves registers, sets up a stack, and determines whether a crash kernel invocation is checksum-only. It calls SHA-256 verification; checksum-only returns to the old kernel, mismatch loads a disabled wait PSW, normal kexec starts the next kernel directly, and crash kexec relocates purgatory to the end of the target crash-memory destination before swapping memory ranges and starting the crash kernel. The crash path iterates over SHA regions to avoid overwriting active purgatory data during the swap.

State and persistence: It mutates CPU registers, stack/buffer memory, crash-memory contents, PSW state, and the lowcore/kernel entry handoff. Saved GPRs allow checksum-only crash invocations to return. After the point of no return, it uses its own stack area as a temporary copy buffer.

Dependencies and integration points: It depends on s390 assembly ABI, page alignment, SIGP architecture setup, kexec SHA region layout, purgatory C verification code, and the s390 restart `diag 0x308` interface. It is linked by `purgatory.lds.S` and embedded by `kexec-purgatory.S`.

Risks and test signals: Register conventions and self-relocation math are fragile; an off-by-one in crash-memory swapping can corrupt purgatory or the crash kernel. Checksum-only mode must restore registers and return safely. Tests include normal kexec, kdump checksum-only failure/success, crash kernel boot with varied crash memory sizes/segment layouts, and disassembly review of relocation-independent code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/kexec-purgatory.S -->
# sources/distributed-fs/ceph-client/arch/s390/purgatory/kexec-purgatory.S

Purpose: This assembly file embeds the built s390 purgatory image into kernel rodata and exposes start/end/size symbols for kexec code.

Important APIs/types/functions: It defines `kexec_purgatory`, local end label `kexec_purgatory_end`, and data symbol `kexec_purgatory_size`. The image content is included with `.incbin "arch/s390/purgatory/purgatory.ro"`.

Control flow: There is no runtime logic. Assembly-time inclusion places the purgatory binary in a read-only allocatable section aligned to eight bytes.

State and persistence: The embedded byte array persists in the kernel image and is copied into kexec/purgatory memory when building a new kernel image.

Dependencies and integration points: It depends on the `purgatory.ro` build artifact and Linux linkage macros. It integrates with s390 kexec image preparation code that reads these symbols.

Risks and test signals: The incbin path must match the Makefile output location, and size calculation must stay correct for loaders. Tests include successful kernel build, symbol inspection, and kexec image loading that validates the embedded purgatory size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/kexec-purgatory.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/purgatory.c -->
# sources/distributed-fs/ceph-client/arch/s390/purgatory/purgatory.c

Purpose: This freestanding C file verifies the SHA-256 digest of the loaded kexec image regions before the s390 purgatory transfers control to the next kernel.

Important APIs/types/functions: The sole function is `verify_sha256_digest(void)`. It uses `struct kexec_sha_region`, `struct sha256_ctx`, `purgatory_sha_regions`, `purgatory_sha256_digest`, and SHA-256 helpers.

Control flow: The function initializes SHA-256 state, iterates over all fixed-size purgatory SHA regions, hashes each region's `start`/`len`, finalizes into a local digest, compares it with the expected digest, and returns `0` for match or `1` for mismatch.

State and persistence: It owns only stack state. It reads the purgatory SHA region table, the loaded memory regions, and the expected digest prepared by kexec image setup.

Dependencies and integration points: It depends on freestanding SHA-256 code, minimal string/memcmp support, Linux kexec structure definitions, and the assembly entry in `head.S`.

Risks and test signals: The fixed array iteration includes all slots, so unused entries must have safe zero length/start data. Digest mismatch behavior is enforced by assembly, which either returns or enters disabled wait. Tests include digest success/failure, empty/unused segments, and kexec/kdump image mutation before execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/purgatory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/purgatory.lds.S -->
# sources/distributed-fs/ceph-client/arch/s390/purgatory/purgatory.lds.S

Purpose: This linker script defines the layout of the standalone s390 purgatory ELF image.

Important APIs/types/functions: It sets `OUTPUT_FORMAT("elf64-s390")`, `OUTPUT_ARCH(s390:64-bit)`, entry `purgatory_start`, and section symbols `_head`, `_ehead`, `_text`, `_etext`, `_rodata`, `_erodata`, `_data`, `_edata`, `_bss`, `_ebss`, and `_end`.

Control flow: Link-time layout starts at address zero, places head text, text, rodata, data, aligns BSS to 256 bytes and then 8 bytes, and discards unwind/export CRC/ksymtab sections that have no purpose in purgatory.

State and persistence: The layout determines the embedded purgatory binary's offsets and symbols used by assembly for stack, end, and relocation calculations.

Dependencies and integration points: It depends on generic vmlinux linker macros, s390 ELF format, and symbols referenced by `head.S` and kexec loader code.

Risks and test signals: Section placement must match assumptions in self-relocation and BSS zeroing. Unexpected retained sections could bloat or break freestanding execution. Tests include link success, readelf section layout, absence of discarded metadata, and kexec boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/purgatory.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/string.c -->
# sources/distributed-fs/ceph-client/arch/s390/purgatory/string.c

Purpose: This file supplies minimal string/memory routines to the s390 purgatory by reusing the architecture string implementation in a freestanding build context.

Important APIs/types/functions: It defines `__HAVE_ARCH_MEMCMP` and includes `../lib/string.c`, allowing purgatory code to use `memcmp` for digest comparison without linking normal kernel libraries.

Control flow: There is no local control flow beyond inclusion. The included implementation provides the actual routines.

State and persistence: No local persistent state exists. The compiled routines become part of the purgatory binary.

Dependencies and integration points: It depends on the s390 architecture string implementation and the purgatory Makefile flags. It is used by `purgatory.c`.

Risks and test signals: Included code must remain freestanding-compatible and avoid kernel runtime dependencies. Tests include purgatory link checks and digest verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/Makefile -->
# sources/distributed-fs/ceph-client/arch/s390/tools/Makefile

Purpose: This Makefile builds s390 host tools and generated architecture headers for facility masks, disassembler opcode tables, and relocation data.

Important APIs/types/functions: It defines generated headers `arch/s390/include/generated/asm/facility-defs.h` and `dis-defs.h`, host programs `gen_facilities`, `gen_opcode_table`, and `relocs`, filechk commands for generated header content, and phony targets `kapi` and `relocs`.

Control flow: The `kapi` target depends on generated headers. `facility-defs.h` is produced by running `gen_facilities`; `dis-defs.h` runs `gen_opcode_table` with `opcodes.txt` as input. The `relocs` phony target ensures the host relocation scanner is built.

State and persistence: Generated headers persist under the generated asm include directory and are consumed by s390 kernel builds. Host tools are build artifacts.

Dependencies and integration points: It depends on Kbuild hostprogs, Linux include paths for `gen_facilities`, `opcodes.txt`, and s390 build stages that need generated headers before compiling the kernel/disassembler.

Risks and test signals: Generated header changes affect instruction decoding and CPU facility masks. Filechk output must be deterministic. Tests include clean builds, incremental rebuilds when tools/opcodes change, generated-header diff review, and host compiler portability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/gcc-thunk-extern.sh -->
# sources/distributed-fs/ceph-client/arch/s390/tools/gcc-thunk-extern.sh

Purpose: This shell probe checks whether the compiler can build s390 external indirect-branch/function-return thunks without a section type conflict for a cold init-text caller.

Important APIs/types/functions: It is a `/bin/sh` script that feeds a small C translation unit to the compiler command passed as `$@`, using flags `-fno-PIE`, `-march=z10`, `-mindirect-branch=thunk-extern`, `-mfunction-return=thunk-extern`, `-mindirect-branch-table`, `-O2`, and `-c -o /dev/null`.

Control flow: The script writes the C source on stdin via heredoc and exits with the compiler's status. The C sample defines `put_page()` and an `.init.text` cold function calling it twice, reproducing the conflict the probe is meant to detect.

State and persistence: It creates no persistent files because output goes to `/dev/null`. Its result is used by build configuration/probing logic.

Dependencies and integration points: It depends on a GCC-compatible s390 compiler supporting the thunk flags. It integrates with s390 mitigation flag selection.

Risks and test signals: Probe accuracy depends on the sample matching the compiler bug/feature being tested. Tests include running it with supported/unsupported compiler versions and verifying build logic accepts or rejects thunk-extern flags accordingly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/gcc-thunk-extern.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/gen_facilities.c -->
# sources/distributed-fs/ceph-client/arch/s390/tools/gen_facilities.c

Purpose: This host tool generates s390 facility-list macros using the Principles of Operation bit numbering scheme for kernel ALS requirements and KVM facility masks.

Important APIs/types/functions: Core data is `struct facility_def` and the `facility_defs[]` table for `FACILITIES_ALS`, `FACILITIES_KVM`, and `FACILITIES_KVM_CPUMODEL`. Helpers are `print_facility_list`, `print_facility_lists`, and `main`.

Control flow: The tool walks each facility bit list until `-1`, maps architectural bit numbers to 64-bit words using most-significant-bit numbering, reallocates the output array when a bit crosses a new doubleword, sets the corresponding bit, and prints `_AC(0x...,UL)` macro initializers inside an include guard. Conditional compilation adds ALS bits according to configured machine-generation features.

State and persistence: Runtime state is a dynamically allocated temporary array per facility definition. Persistent output is the generated `facility-defs.h` header consumed by s390 code.

Dependencies and integration points: It depends on standard C library allocation/stdio/string APIs and kernel build defines passed through `HOSTCFLAGS`. It integrates with s390 CPU feature checks and KVM CPU-model facility masks.

Risks and test signals: Bit-number conversion is the critical contract; reversing bit order or failing to zero newly allocated words would generate invalid masks. Tests include comparing generated macros against known facility bitsets for each `CONFIG_HAVE_MARCH_*` combination, build reproducibility, and KVM guest facility-mask validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/gen_facilities.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/gen_opcode_table.c -->
# sources/distributed-fs/ceph-client/arch/s390/tools/gen_opcode_table.c

Purpose: This host tool converts the s390 opcode list into C initializers for the in-kernel disassembler: instruction format enums, long-name storage, opcode table entries, and opcode group offsets.

Important APIs/types/functions: Data types are `struct insn_type`, `struct insn`, `struct insn_group`, `struct insn_format`, and `struct gen_opcode`. Main helpers include `insn_format_to_type`, `read_instructions`, sorting comparators, `print_formats`, `print_long_insn`, `print_opcode`, `add_to_group`, `print_opcode_table`, `print_opcode_table_offsets`, and `main`.

Control flow: The tool reads `opcode name format` triples from stdin, maps each format to an opcode-position/mask type, stores uppercase names, and then prints generated code in several sorted passes. Formats are sorted to emit unique `INSTR_*` enum entries. Long instruction names are sorted and emitted into a separate initializer. Opcodes are sorted by opcode string; multi-byte opcodes are emitted first and grouped by leading byte/mask/offset/count, followed by one-byte opcodes.

State and persistence: Dynamic arrays of instructions and groups exist only while the tool runs. Persistent output is `dis-defs.h`, used by the kernel disassembler.

Dependencies and integration points: It depends on standard C library scanf/qsort/realloc/string helpers and the format vocabulary in `opcodes.txt`. It integrates with s390 disassembly tables and any tool/tests that decode instruction bytes.

Risks and test signals: Format-to-type mapping must match s390 instruction encoding locations for second/third/fourth opcode nibbles. Grouping by leading opcode and mask drives lookup efficiency and correctness; bad grouping can make the disassembler miss or misidentify instructions. Tests include generated-header golden comparisons, disassembly of representative one-byte/three-nibble/two-byte/six-byte formats, long mnemonic handling, malformed input rejection, and valgrind/ASAN for host-tool memory handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/gen_opcode_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/relocs.c -->
# sources/distributed-fs/ceph-client/arch/s390/tools/relocs.c

Purpose: This host utility scans a 64-bit big-endian s390 ELF executable/shared object and emits relocation offsets for absolute 64-bit relocations into a `.vmlinux.relocs_64` assembly section.

Important APIs/types/functions: Global ELF state is `ehdr`, `shnum`, `shstrndx`, `secs`, and `relocs64`. Core helpers are endian converters, `die`, `read_ehdr`, `read_shdrs`, `read_relocs`, `add_reloc`, `do_reloc`, `walk_relocs`, `sort_relocs`, `emit_relocs`, `process`, and `main`.

Control flow: `main` opens the input ELF, verifies the header class/endian/machine/type, reads section headers including extended section counts, reads all SHT_RELA relocation sections with endian conversion, walks relocations that apply to allocated sections, records offsets only for `R_390_64`, ignores known PC-relative/GOT/no-op relocations, errors on unsupported relocation types, sorts offsets, and prints `.long` directives in the reloc section.

State and persistence: The tool stores parsed section headers and relocation arrays in process memory. Persistent output is assembly text on stdout for later build stages.

Dependencies and integration points: It depends on libc, `<elf.h>`, host endian macros/bswap, and s390 relocation constants. It integrates with kernel relocation handling for s390 vmlinux images.

Risks and test signals: ELF validation and endian conversion must be exact because host endianness may differ from target. Unsupported relocation types intentionally fail the build. Offset truncation to 32-bit must match relocation-section consumer expectations. Tests include ET_EXEC and ET_DYN inputs, extended section counts, unsupported relocation injection, little-endian rejection, sorted output comparison, and build/link tests for relocatable s390 kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/relocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/Kbuild -->
# sources/distributed-fs/ceph-client/arch/sh/Kbuild

Purpose: This Kbuild file selects the core SuperH architecture subdirectories and optional components to build.

Important APIs/types/functions: It adds `kernel/`, `mm/`, and `boards/` to `obj-y`, adds `math-emu/` when `CONFIG_SH_FPU_EMU` is enabled, adds `cchips/hd6446x/` for HD6446x companion chips, and marks `boot` as a clean-only subdirectory.

Control flow: Kbuild includes the listed directories based on configuration symbols during the architecture build. Cleaning descends into `boot` even though normal object traversal is handled elsewhere.

State and persistence: It controls build artifact selection only; no runtime state exists.

Dependencies and integration points: It depends on SuperH Kconfig symbols and Kbuild directory conventions. It integrates the top-level SuperH build with memory management, board support, kernel code, FPU emulation, and companion-chip support.

Risks and test signals: Missing a directory excludes needed objects for a configuration; adding the wrong optional directory can break unrelated builds. Tests are SuperH defconfig/allmodconfig builds with and without FPU emulation and HD6446x support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sh/Kconfig

Purpose: This is the main SuperH architecture Kconfig. It defines the `SUPERH` architecture capabilities, CPU family/subtype choices, timer/clock settings, kernel features, boot options, bus support, and power-management menu inclusion.

Important APIs/types/functions: Key symbols include `SUPERH`, CPU families `CPU_SH2`, `CPU_SH2A`, `CPU_J2`, `CPU_SH3`, `CPU_SH4`, `CPU_SH4A`, `CPU_SH4AL_DSP`, `CPU_SHX2`, `CPU_SHX3`, `ARCH_SHMOBILE`, CPU subtype configs from SH7619/J2 through SHX3/SH772x/SH778x, `SH_PCLK_FREQ`, `SH_CLK_CPG_LEGACY`, `ARCH_SUPPORTS_KEXEC`, `SMP`, `NR_CPUS`, `GUSA`, `GUSA_RB`, `HW_PERF_EVENTS`, builtin DTB options, boot offsets, command-line policy, and `MAPLE`.

Control flow: Kconfig selection starts by declaring SuperH architectural feature support, then presents a processor subtype choice whose entries select CPU families, pinctrl, timers, FPU/DSP, sparsemem, NUMA, USB, and other capabilities. It sources memory-management, CPU, board, driver, cpufreq, kernel HZ, SH driver, power, and cpuidle Kconfigs. Later menus derive default clock rates, image/link offsets, kexec/crash support, SMP limits, user-space atomicity options, command-line behavior, and Dreamcast Maple bus support.

State and persistence: Kconfig state persists in `.config` and drives compiler flags, included source directories, generated headers, boot layout, and runtime feature availability. There is no direct runtime code in this file.

Dependencies and integration points: It integrates with `arch/sh/Makefile`, `arch/sh/boards/Kconfig`, MM/Kconfig, CPU-specific Kconfig, drivers, kernel power/cpufreq/HZ menus, and generic kernel capability symbols.

Risks and test signals: Incorrect `select`/`depends on` relationships can create invalid board/CPU combinations or missing driver prerequisites. Defaults for clock frequency and boot offsets affect bootability on legacy boards. Tests include `make ARCH=sh olddefconfig` for representative board defconfigs, randconfig dependency checks, built-in DTB builds, SMP/J2/SHX3 configs, no-MMU configs, and boot smoke tests on emulators or hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/Makefile

Purpose: This is the SuperH architecture Makefile that configures cross-compiler prefix detection, CPU/ISA/endian compiler flags, linker format, machine include directories, default boot images, boot targets, and architecture preparation/header targets.

Important APIs/types/functions: It sets `KBUILD_DEFCONFIG`, `isa-*`, `cflags-*`, `isaflags-*`, `OBJCOPYFLAGS`, `defaultimage-*`, `KBUILD_IMAGE`, `UTS_MACHINE`, `LDFLAGS_vmlinux`, `KBUILD_LDFLAGS`, `machdir-*`, `cpuincdir-*`, `KBUILD_CPPFLAGS`, `KBUILD_CFLAGS`, `KBUILD_AFLAGS`, `libs-y`, boot target phony rules, `archprepare`, `archheaders`, and `archhelp`.

Control flow: The Makefile picks a cross prefix when needed, derives ISA flags from CPU config and assembler support, falls back to compiler multilib no-FPU flags when explicit CPU flags are unavailable, selects big/little-endian linker output and jiffies symbol offset, builds include paths ordered from most-specific CPU/machine to common, and delegates boot targets to `arch/sh/boot`. `archprepare` generates machine types and `archheaders` generates syscall headers.

State and persistence: Build-state outputs include selected compiler/assembler flags, linker emulation, exported `ld_bfd`, generated headers, and boot images. Runtime effects are indirect through instruction set, endian mode, and link address choices.

Dependencies and integration points: It depends on Kconfig CPU/board symbols, GCC/binutils SH options, Kbuild helper functions, `arch/sh/tools`, `arch/sh/boot`, `arch/sh/drivers`, and `arch/sh/lib`.

Risks and test signals: Flag selection is sensitive to old/new GCC and binutils SH multilib behavior. Wrong endian linker format or jiffies offset breaks boot/runtime timekeeping. Include path ordering controls CPU/machine header selection. Tests include build matrix over SH2/SH3/SH4/SH4A/J2, big and little endian, old binutils fallback, boot image targets, and generated machtypes/syscall headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sh/boards/Kconfig

Purpose: This Kconfig menu defines SuperH board and machine support symbols, including legacy board files, machine subdirectories, device-tree mode, and board-specific dependency selections.

Important APIs/types/functions: Major symbols include `SOLUTION_ENGINE`, `SH_CUSTOM_CLK`, `SH_DEVICE_TREE`, `SH_JCORE_SOC`, board symbols such as `SH_DREAMCAST`, `SH_SECUREEDGE5410`, `SH_RSK`, `SH_SH7757LCR`, `SH_SH7785LCR`, `SH_URQUELL`, `SH_AP325RXA`, `SH_ECOVEC`, `SH_ESPT`, `SH_EDOSK7705`, `SH_EDOSK7760`, `SH_TITAN`, `SH_SHMIN`, `SH_MAGIC_PANEL_R2`, `SH_POLARIS`, `SH_SH2007`, `SH_APSH4A3A`, and `SH_APSH4AD0A`, plus included machine Kconfigs for R2D, Highlander, SDK7780, Migo-R, and RSK.

Control flow: Users select a board compatible with the selected CPU subtype. Each board can select platform capabilities such as PCI, GPIOLIB, fixed regulators, IRQ domains, IPR IRQs, legacy clocks, OF/flattree, timers, and sound codec implications. Optional submenus expose board-specific settings such as Magic Panel R2 version.

State and persistence: Board selection persists in `.config` and controls compiled board object files, machine directories, default image type, include paths, platform devices, IRQ setup, and boot options.

Dependencies and integration points: It integrates with `arch/sh/Kconfig`, `arch/sh/boards/Makefile`, individual board source files, machine subdirectory Kconfigs, and driver Kconfigs selected or implied by boards.

Risks and test signals: Dependencies must prevent incompatible CPU/board selections. Overuse of `select` can force drivers/capabilities without prerequisites; missing selections can leave board setup code without required subsystems. Tests include olddefconfig for every listed board, randconfig dependency validation, and boot tests for boards with platform data still in C files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/Makefile

Purpose: This Makefile maps SuperH board configuration symbols to board object files and machine subdirectories.

Important APIs/types/functions: It builds standalone board objects such as `board-magicpanelr2.o`, `board-secureedge5410.o`, `board-sh2007.o`, `board-sh7785lcr.o`, `board-urquell.o`, `board-shmin.o`, EDOSK/ESPT/Polaris/Titan/APSH boards, and `of-generic.o`. It descends into machine directories including Solution Engine, Dreamcast, SH03, R2D, Highlander, Migo-R, AP325RXA, KFR2R09, EcoVec24, SDKs, X3PROTO, Landisk, L-BOX, and RSK.

Control flow: Kbuild includes objects/directories whose `CONFIG_*` symbols are enabled. Device-tree builds include `of-generic.o` in addition to or instead of legacy board code.

State and persistence: It controls build composition only. Runtime board state comes from the selected source files.

Dependencies and integration points: It depends on board Kconfig symbols and the directory layout under `arch/sh/boards`. It integrates board support with top-level `arch/sh/Kbuild`.

Risks and test signals: A missing object mapping means selecting a board produces no machine vector or devices; an incorrect mapping can link incompatible board support. Tests are per-board build coverage and link checks for machine vector definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-apsh4a3a.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-apsh4a3a.c

Purpose: This board file initializes the ALPHAPROJECT AP-SH4A-3A platform, including NOR flash, SMSC911x Ethernet, dummy regulators, clocks, IRQs, mode pins, and the machine vector.

Important APIs/types/functions: It defines NOR flash partitions/data/resources/device, SMSC911x resources/config/device, dummy regulator supplies, device array `apsh4a3a_devices`, initcalls `apsh4a3a_devices_setup` and `apsh4a3a_clk_init`, setup/IRQ functions `apsh4a3a_setup` and `apsh4a3a_init_irq`, mode-pin reader `apsh4a3a_mode_pins`, and `mv_apsh4a3a`.

Control flow: Device init registers fixed dummy regulators and platform devices. Setup configures board-specific I/O base behavior, clock init registers the board clock, IRQ init installs interrupt controller setup, and the machine vector supplies name/setup/IRQ/mode-pin callbacks to the SuperH boot path.

State and persistence: Static platform device/resource tables persist for the kernel lifetime. Flash partition definitions determine MTD layout; mode pins report boot strapping state.

Dependencies and integration points: It depends on SH7785 CPU support, platform devices, physmap flash, fixed regulator framework, SMSC911x, clock framework, and SuperH machvec/IRQ helpers.

Risks and test signals: Hard-coded memory/IRQ resources and flash partitions must match board wiring. Tests include AP-SH4A-3A boot, Ethernet probe, NOR partition visibility, regulator registration, clock rate checks, and mode-pin output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-apsh4a3a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-apsh4ad0a.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-apsh4ad0a.c

Purpose: This board file initializes the ALPHAPROJECT AP-SH4AD-0A platform with SMSC911x Ethernet, dummy regulators, clock setup, IRQ setup, mode-pin decoding, and machine-vector registration.

Important APIs/types/functions: It defines dummy SMSC911x supplies, SMSC911x resources/config/device, `apsh4ad0a_devices`, `apsh4ad0a_devices_setup`, `apsh4ad0a_mode_pins`, `apsh4ad0a_clk_init`, `apsh4ad0a_setup`, `apsh4ad0a_init_irq`, and `mv_apsh4ad0a`.

Control flow: The device initcall registers fixed regulators and the Ethernet platform device. Clock/setup/IRQ/mode-pin callbacks are attached through the machine vector for the SH7786-based board.

State and persistence: Persistent state is static platform data/resources and machine-vector callbacks. Mode-pin reads reflect hardware strap state.

Dependencies and integration points: It depends on SH7786 CPU support, SuperH interrupt and clock setup, fixed regulators, and the SMSC911x platform driver.

Risks and test signals: Ethernet resource windows and IRQ polarity/type must match the board. Tests include board boot, SMSC911x network bring-up, fixed-regulator availability, and mode-pin reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-apsh4ad0a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-edosk7705.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-edosk7705.c

Purpose: This file provides Renesas EDOSK7705 board support, mainly SMC91x Ethernet resources, interrupt initialization, and a machine vector.

Important APIs/types/functions: It defines SMC I/O address/IRQ macros, `sh_edosk7705_init_irq`, SMC91x platform data/resources/device, `edosk7705_devices`, `init_edosk7705_devices`, and `mv_edosk7705`.

Control flow: The device initcall registers the SMC91x Ethernet device. The machine vector supplies the board name and IRQ initialization callback.

State and persistence: Static platform resources persist for Ethernet. No dynamic board-private state is maintained.

Dependencies and integration points: It depends on SH7705 CPU support, SMC91x platform driver, platform-device registration, and SuperH IRQ vector conversion.

Risks and test signals: Hard-coded I/O base/offset and event IRQ must match the evaluation board. Tests include EDOSK7705 boot, Ethernet probe/traffic, and IRQ delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-edosk7705.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-edosk7760.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-edosk7760.c

Purpose: This file supports the EDOSK7760 board by declaring NOR flash, two SH7760 I2C controllers, SMC91x Ethernet, board setup, and the machine vector.

Important APIs/types/functions: It defines BSC register macros, flash partitions/data/resources/device, `sh7760_i2c_platdata`, I2C0/I2C1 resources/devices, SMC91x platform data/resources/device, `edosk7760_devices`, `init_edosk7760_devices`, and `mv_edosk7760`.

Control flow: The initcall configures/registers board platform devices. The board also programs bus-state-controller registers for external devices and supplies machine-vector callbacks.

State and persistence: Persistent state includes flash partition layout, I2C bus resources, Ethernet resource data, and machine-vector data.

Dependencies and integration points: It depends on SH7760 CPU support, physmap flash, SH7760 I2C driver, SMC91x driver, platform devices, and SuperH machine-vector infrastructure.

Risks and test signals: Bus timing registers and memory windows are board-specific and can break flash/Ethernet if wrong. Tests include flash partition detection, I2C adapter registration, Ethernet probe, and boot on EDOSK7760.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-edosk7760.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-espt.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-espt.c

Purpose: This file provides ESPT board support for SH7763 systems, defining NOR flash, SH Ethernet resources/platform data, device registration, and the machine vector.

Important APIs/types/functions: It defines NOR flash partitions/data/resources/device, `sh_eth_resources`, `sh7763_eth_pdata`, `espt_eth_device`, `espt_devices`, `espt_devices_setup`, and `mv_espt`.

Control flow: The device initcall registers flash and Ethernet devices. The machine vector identifies the board for the SuperH platform layer.

State and persistence: Static resource and platform-data tables persist for flash and Ethernet.

Dependencies and integration points: It depends on SH7763 CPU support, physmap flash, Renesas SH Ethernet platform driver, and platform-device registration.

Risks and test signals: Ethernet PHY/interface resources and flash partition offsets must match hardware. Tests include ESPT boot, MTD partition listing, Ethernet link/traffic, and IRQ/resource conflict checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-espt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-magicpanelr2.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-magicpanelr2.c

Purpose: This board file initializes the Magic Panel R2 platform, including Ethernet reset/chip-select setup, port multiplexing, SMSC911x Ethernet, heartbeat LEDs, NOR flash partitions, IRQ initialization, and the machine vector.

Important APIs/types/functions: Key helpers are `ethernet_reset_finished`, `reset_ethernet`, `setup_chip_select`, `setup_port_multiplexing`, `mpr2_setup`, `mpr2_devices_setup`, and `init_mpr2_IRQ`. Static data covers dummy regulators, SMSC911x resources/config/device, heartbeat resources/data/device, flash partitions/data/resource/device, device list `mpr2_devices`, and `mv_mpr2`.

Control flow: Early setup configures chip select and port multiplexing registers, resets Ethernet and waits for readiness, then device init registers regulators and platform devices. IRQ setup configures interrupt routing. Machine vector callbacks wire these steps into boot.

State and persistence: Board register writes persist in hardware pinmux/chip-select state. Static platform data persists for Ethernet, heartbeat, and flash. Flash partition layout defines persistent storage mapping.

Dependencies and integration points: It depends on SH7720 board registers, GPIO/regulator support, SMSC911x, heartbeat LED driver, physmap flash, and SuperH IRQ/machvec support.

Risks and test signals: Direct register programming is board-version-sensitive, and Ethernet reset polling can fail if timing or ready-bit definitions are wrong. Tests include Magic Panel R2 boot across supported version settings, Ethernet probe after reset, LED heartbeat, flash partition access, and IRQ delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-magicpanelr2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-polaris.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-polaris.c

Purpose: This file supports the SMSC Polaris SH7709 development board with SMSC911x Ethernet, heartbeat LEDs, wait-state setup, IPR IRQ mapping, and a machine vector.

Important APIs/types/functions: It defines bus-control macros, dummy supplies, SMSC911x resources/config/device, heartbeat data/resource/device, `polaris_devices`, `polaris_initialise`, IPR tables/offsets/descriptor, `init_polaris_irq`, and `mv_polaris`.

Control flow: `polaris_initialise` registers regulators/devices and programs area wait states for Ethernet. IRQ init registers IPR IRQ descriptors. The machine vector supplies the board name and IRQ callback.

State and persistence: Hardware wait-state register updates persist in the bus controller. Static device/platform data persists for Ethernet and LEDs.

Dependencies and integration points: It depends on SH7709, IPR interrupt support, fixed regulators, SMSC911x, heartbeat platform driver, and SuperH machine vectors.

Risks and test signals: Bus wait-state programming is needed for reliable Ethernet access. Tests include Ethernet register access/probe, heartbeat LEDs, IRQ handling, and boot with SH_POLARIS config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-polaris.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-secureedge5410.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-secureedge5410.c

Purpose: This board file supports the SnapGear SecureEdge5410 platform, including an erase-config interrupt hook, IRQ initialization, and the machine vector.

Important APIs/types/functions: It defines `eraseconfig_interrupt`, `eraseconfig_init`, `init_snapgear_IRQ`, and `mv_snapgear`.

Control flow: The device initcall requests the board erase-config IRQ and logs/handles button events. IRQ setup initializes board interrupt routing, and the machine vector names the SnapGear/SecureEdge board.

State and persistence: Minimal runtime state exists; the requested IRQ remains registered. The erase-config behavior can affect persistent configuration depending on higher-level handling.

Dependencies and integration points: It depends on SH7751R board IRQ support, generic IRQ request APIs, and SuperH machvec setup.

Risks and test signals: The erase-config IRQ must not be shared/misnumbered, since it can trigger configuration reset behavior. Tests include boot, button interrupt delivery, and IRQ setup on SecureEdge5410 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-secureedge5410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-sh2007.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-sh2007.c

Purpose: This file supports the SH-2007 SH7780 single-board computer with two SMSC9118 Ethernet devices, CompactFlash resources, dummy regulators, setup/IRQ callbacks, and the machine vector.

Important APIs/types/functions: It defines SMSC911x platform config `smc911x_info`, resources/devices for two Ethernet controllers, CF resources/device, `sh2007_devices`, `sh2007_io_init`, `sh2007_init_irq`, `sh2007_setup`, and `mv_sh2007`.

Control flow: A subsys initcall registers fixed regulators and all platform devices early enough for bus users. Setup configures I/O behavior, and IRQ init installs board interrupt handling.

State and persistence: Static platform resources persist for Ethernet and CF. Board setup may alter persistent bus/register state for I/O routing.

Dependencies and integration points: It depends on SH7780 CPU support, fixed regulators, SMSC911x, pata/CF platform support, platform devices, and SuperH IRQ/machvec infrastructure.

Risks and test signals: Two Ethernet devices need distinct resources/IRQs and correct regulator consumers. CF window/IRQ definitions must match the PC-104/CF wiring. Tests include dual Ethernet probe/traffic, CF detection, IRQ handling, and SH2007 boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-sh2007.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-sh7757lcr.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-sh7757lcr.c

Purpose: This large board file supports the Renesas SH7757LCR board, declaring heartbeat LEDs, multiple Ethernet controllers, MDIO gate helpers, MMCIF/SDHI, USBHS, SPI flash, fixed regulators, device registration, IRQ setup, mode pins, and machine-vector data.

Important APIs/types/functions: It defines heartbeat data/device, Ethernet resources/platform data/devices for SH Ethernet and gigabit Ethernet, MDIO gate helpers `sh7757_eth_set_mdio_gate` and `sh7757_eth_giga_set_mdio_gate`, fixed 3.3V consumers, MMCIF resources/platform data/device, SDHI data/resources/device, USBHS ID/platform/resources/device, board device list `sh7757lcr_devices`, SPI flash data/board info, `sh7757lcr_devices_setup`, `init_sh7757lcr_IRQ`, `sh7757lcr_setup`, `sh7757lcr_mode_pins`, and `mv_sh7757lcr`.

Control flow: The arch initcall registers platform devices and SPI board info, configures board registers for Ethernet/MDIO and possibly pin/function selection, then IRQ/setup/mode callbacks are used through the machine vector. Platform data supplies per-device callbacks such as USB ID and MDIO gate control to drivers.

State and persistence: Static platform data persists for each device. Register writes affect board-level Ethernet gate/control and boot-mode interpretation. Storage platform data maps persistent flash/MMC/SD devices.

Dependencies and integration points: It depends on SH7757 CPU support, Renesas SH Ethernet, MMCIF, TMIO SDHI, Renesas USBHS, SPI flash, fixed regulators, heartbeat LEDs, GPIO/pinctrl where selected, and SuperH machvec/IRQ support.

Risks and test signals: Many hard-coded resources increase conflict risk. MDIO gate callbacks must serialize with Ethernet driver access, and storage/USB resource definitions must match board variants. Tests include boot, all Ethernet ports link/MDIO reads, MMCIF/SDHI card detection, USB host/device behavior, SPI flash probe, heartbeat LEDs, mode-pin output, and IRQ routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-sh7757lcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-sh7785lcr.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-sh7785lcr.c

Purpose: This file supports the Renesas SH7785LCR board with heartbeat LEDs, NOR flash, R8A66597 USB host, SM501 display, GPIO-backed PCA9564 I2C, power-off handling, clock setup, mode pins, and the machine vector.

Important APIs/types/functions: It defines heartbeat, flash partitions/resources/device, USB host platform data/resources/device, SM501 resources/framebuffer modes/platform/init data/device, I2C resources/GPIO lookup/platform data/device, I2C board info, `sh7785lcr_devices_setup`, `init_sh7785lcr_IRQ`, `sh7785lcr_clk_init`, `sh7785lcr_power_off`, `sh7785lcr_setup`, `sh7785lcr_mode_pins`, and `mv_sh7785lcr`.

Control flow: Device init registers platform devices and I2C board info. Setup installs power-off handling and board setup, clock init configures board clocking, IRQ init configures interrupts, and the machine vector exposes all callbacks.

State and persistence: Static platform data persists for flash, USB, display, I2C, and heartbeat. Power-off handler persists as `pm_power_off` style platform behavior. Flash partitions map persistent storage.

Dependencies and integration points: It depends on SH7785 CPU support, physmap flash, R8A66597 USB, SM501 framebuffer, PCA9564 I2C, GPIO lookup tables, heartbeat driver, clock framework, and SuperH machvec.

Risks and test signals: Display timings and SM501 resource windows must match hardware; power-off sequence must not conflict with reboot. Tests include flash/USB/display/I2C device probes, power-off behavior, board clock rate, heartbeat LEDs, and mode-pin output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-sh7785lcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-shmin.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-shmin.c

Purpose: This file supplies minimal SHMIN board support: port/interrupt register setup, command-line/setup callback, and a machine vector.

Important APIs/types/functions: It defines hardware register macros `PFC_PHCR` and `INTC_ICR1`, functions `init_shmin_irq` and `shmin_setup`, and `mv_shmin`.

Control flow: Setup configures board-level I/O assumptions. IRQ init writes interrupt controller settings for the board. The machine vector registers name/setup/IRQ callbacks.

State and persistence: Direct register writes persist in hardware interrupt and pin-function state. No dynamic platform devices are declared here.

Dependencies and integration points: It depends on SH7706/SHMIN hardware, raw I/O access, and SuperH machvec/IRQ initialization.

Risks and test signals: Minimal hard-coded register writes can break boot if applied to the wrong CPU/board. Tests include SHMIN boot, interrupt delivery, and serial/console operation after setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-shmin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-titan.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-titan.c

Purpose: This small file provides Titan board identity and IRQ initialization through a SuperH machine vector.

Important APIs/types/functions: It defines `init_titan_irq` and `mv_titan`.

Control flow: During boot, the machine vector calls Titan IRQ initialization to install board-specific interrupt routing.

State and persistence: No local dynamic state exists beyond machine-vector registration. IRQ controller setup persists in hardware/kernel interrupt state.

Dependencies and integration points: It depends on SH7751R/Titan configuration, CPU IPR IRQ support, PCI selection from Kconfig, and SuperH machvec infrastructure.

Risks and test signals: The file is sparse, so missing platform-device declarations may rely on other generic PCI/board code. Tests include Titan boot, IRQ routing, PCI enumeration, and link/build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-titan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-urquell.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-urquell.c

Purpose: This file supports the Urquell SH7786 board with heartbeat LEDs, SMC91x Ethernet, NOR flash, power-off behavior, IRQ setup, mode pins, clock initialization, and the machine vector.

Important APIs/types/functions: It defines heartbeat resource/device, SMC91x platform data/resources/device, NOR flash partitions/data/resources/device, `urquell_devices`, `urquell_devices_setup`, `urquell_power_off`, `urquell_init_irq`, `urquell_mode_pins`, `urquell_clk_init`, `urquell_setup`, and `mv_urquell`.

Control flow: Device init registers board devices. Setup installs power-off handling and board-specific initialization. Clock/IRQ/mode-pin callbacks are provided through the machine vector.

State and persistence: Static platform tables persist for Ethernet, flash, and heartbeat. Power-off handler and clock setup affect global platform behavior. Flash partitions define persistent storage layout.

Dependencies and integration points: It depends on SH7786 CPU support, SMC91x Ethernet, physmap flash, heartbeat driver, clock and IRQ helpers, PCI/no-ioport-map behavior from Kconfig, and SuperH machvec.

Risks and test signals: Ethernet/flash hard-coded resource windows and power-off register behavior must match board wiring. Tests include boot, Ethernet traffic, flash partition visibility, heartbeat, power-off, clock setup, and mode-pin reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-urquell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/Makefile

Purpose: This Makefile builds AP325RXA machine support objects.

Important APIs/types/functions: It sets `obj-y := setup.o sdram.o`.

Control flow: When the AP325RXA machine directory is selected, Kbuild compiles both the C platform setup and SDRAM suspend/resume assembly.

State and persistence: It controls build inclusion only.

Dependencies and integration points: It depends on `CONFIG_SH_AP325RXA` selecting this directory from the board Makefile and integrates `setup.c` with `sdram.S`.

Risks and test signals: Omitting `sdram.o` would break suspend self-refresh support; omitting `setup.o` would lose board devices. Tests are AP325RXA build and suspend/resume boot coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/sdram.S -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/sdram.S

Purpose: This assembly file provides AP325RXA SDRAM self-refresh enter/leave snippets for suspend, designed to be copied to and executed from on-chip memory.

Important APIs/types/functions: It exports `ap325rxa_sdram_enter_start`, `ap325rxa_sdram_enter_end`, `ap325rxa_sdram_leave_start`, and `ap325rxa_sdram_leave_end`.

Control flow: Enter code reads SDCR0, sets self-refresh and clears power-down bits, writes SDCR0, and returns. Leave code clears self-refresh, adjusts refresh timer registers RTCOR/RTCNT with the required key value, and returns.

State and persistence: It directly mutates SDRAM controller registers at fixed physical addresses. The code bytes are used as a relocatable low-level suspend routine.

Dependencies and integration points: It depends on SH7723/AP325RXA SDRAM controller addresses, SuperH assembly ABI, suspend infrastructure, and `setup.c` registering the copied code with suspend support.

Risks and test signals: The routine must be fully self-contained, position-safe, and run from memory that remains accessible while SDRAM is in self-refresh. Tests include suspend/resume cycles, register-value inspection, and ensuring code-size boundaries match exported start/end symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/sdram.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/setup.c

Purpose: This large board setup file initializes the Renesas AP-325RXA/AP-320A-compatible platform with Ethernet, NOR/NAND flash, LCDC/backlight, camera/CEU memory, MMC/SD, regulators, GPIO mappings, suspend SDRAM hooks, and other SH7723 peripherals.

Important APIs/types/functions: It defines `ceu_dma_membase`, dummy supplies, SMSC911x device, NOR and NAND partition/platform data, LCD/backlight helpers `ap320_wvga_set_brightness`, `ap320_wvga_power_on`, `ap320_wvga_power_off`, LCDC modes/info/resources/device, plus many platform resources/devices for camera, MMC/SD, GPIO/regulator/I2C/video integration, and board init/setup callbacks later in the file.

Control flow: Early setup reserves DMA memory for CEU, configures GPIO/pinmux and board FPGA registers, registers fixed regulators and platform devices, supplies LCD power/backlight callbacks to the framebuffer driver, and installs suspend SDRAM enter/leave code. Device registration is static platform-data driven rather than device-tree driven.

State and persistence: Persistent state includes reserved CEU DMA memory, flash partition layouts, platform-device/resource tables, GPIO lookup/regulator mappings, LCD/backlight register state, and SDRAM suspend code ranges.

Dependencies and integration points: It depends on SH7723 CPU headers, DMA memblock APIs, GPIO and gpiod lookup, fixed regulators, SMSC911x, physmap and SH flash controller MTD, TMIO/MMC, Renesas CEU/camera sensor data, SH Mobile LCDC, I2C, and SuperH suspend/machvec support.

Risks and test signals: Static platform data spans many devices, so resource overlap and incorrect GPIO polarity are common risks. Reserved CEU memory must be aligned and excluded from normal allocation. LCD/backlight callbacks directly touch FPGA/GPIO registers. Tests include AP325RXA boot, Ethernet, NOR/NAND partitions, LCD/backlight, camera capture, MMC/SD, suspend/resume SDRAM self-refresh, and regulator/GPIO lookup validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/Makefile

Purpose: This Makefile builds Sega Dreamcast-specific machine support.

Important APIs/types/functions: It sets `obj-y := setup.o irq.o` and conditionally adds `rtc.o` for `CONFIG_RTC_DRV_GENERIC`.

Control flow: Dreamcast builds always include setup and System ASIC IRQ handling; generic RTC support additionally includes AICA RTC registration.

State and persistence: Build selection only.

Dependencies and integration points: It depends on `CONFIG_SH_DREAMCAST`, generic RTC config, and the Dreamcast machine directory selected from the board Makefile.

Risks and test signals: Missing `irq.o` would prevent Maple/System ASIC device interrupts; missing `rtc.o` only affects timekeeping. Tests include Dreamcast build with and without `RTC_DRV_GENERIC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/irq.c

Purpose: This file implements Sega Dreamcast Holly/System ASIC hardware event interrupt masking, acknowledgment, demultiplexing, and virtual IRQ setup.

Important APIs/types/functions: It defines ESR/EMR register bases, `LEVEL` and `EVENT_BIT` macros, IRQ-chip callbacks `disable_systemasic_irq`, `enable_systemasic_irq`, `mask_ack_systemasic_irq`, exported `systemasic_int`, demux function `systemasic_irq_demux`, and initializer `systemasic_irq_init`.

Control flow: System ASIC events are grouped into three 32-bit status/mask register sets corresponding to SH IRQ levels 13, 11, and 9. Demux maps the processor IRQ to a group, masks status with enabled bits, scans for the first set event bit, and returns the virtual event IRQ. IRQ chip callbacks update EMR bits and acknowledge by writing the event bit to ESR. Init allocates descriptors for the hardware event range and assigns the chip/level handler.

State and persistence: Hardware EMR/ESR state persists in the ASIC. Kernel IRQ descriptors persist for the hardware event range.

Dependencies and integration points: It depends on Dreamcast `mach/sysasic.h` event ranges, raw I/O accessors, generic IRQ descriptor APIs, and the Dreamcast machine vector's IRQ demux/init callbacks.

Risks and test signals: Event-to-IRQ mapping must match the ASIC register grouping. Acknowledgment must write the correct ESR bit or events will retrigger/latch. Tests include Maple/peripheral interrupts, masking/unmasking behavior, spurious IRQ handling, and descriptor allocation failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/rtc.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/rtc.c

Purpose: This file registers the Dreamcast AICA RTC through the generic RTC platform driver, translating between the AICA 1950 epoch and Unix time.

Important APIs/types/functions: It defines `TWENTY_YEARS`, AICA high/low seconds register addresses, `aica_rtc_gettimeofday`, `aica_rtc_settimeofday`, `rtc_generic_ops`, and initcall `aica_time_init`.

Control flow: Read loops until two consecutive 32-bit seconds reads from high/low 16-bit registers match, subtracts the 20-year epoch offset, casts into the 1970-2106 range, and converts to `rtc_time`. Set adds the offset, writes high and low halves, and repeats until readback is stable. Init registers a `rtc-generic` platform device with these ops.

State and persistence: Persistent state is the hardware RTC seconds counter. Kernel platform-device registration persists for RTC driver binding.

Dependencies and integration points: It depends on raw I/O accessors, generic RTC class ops, and Dreamcast hardware addresses.

Risks and test signals: The 32-bit counter and epoch conversion limit valid time range. Split-register reads/writes require stable double-read loops. Tests include RTC read/set, rollover around low-half changes, dates near 1970 and 2106, and driver registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/setup.c

Purpose: This file supplies the Dreamcast machine-vector setup, including I/O port base configuration and System ASIC IRQ integration.

Important APIs/types/functions: It defines `dreamcast_setup` and `mv_dreamcast`.

Control flow: Setup sets the I/O port base to `P2SEG` because the GAPS PCI bridge uses P2-area relative addresses. The machine vector names the board and installs `systemasic_irq_demux` and `systemasic_irq_init`.

State and persistence: I/O port base configuration persists globally for port I/O translation. Machine-vector callbacks persist through boot.

Dependencies and integration points: It depends on SH address-space macros, generic I/O base setup, Dreamcast System ASIC IRQ functions, and SuperH machvec.

Risks and test signals: Incorrect I/O base breaks Dreamcast PCI/GAPS access. Tests include Dreamcast boot, PCI/device I/O access, System ASIC event IRQs, and machine-vector selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ecovec24/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-ecovec24/Makefile

Purpose: This Makefile builds EcoVec24 machine support objects.

Important APIs/types/functions: It sets `obj-y := setup.o sdram.o`.

Control flow: When EcoVec support is selected, Kbuild includes both platform setup and SDRAM suspend/resume support.

State and persistence: Build selection only; runtime state is implemented in the referenced source files.

Dependencies and integration points: It depends on `CONFIG_SH_ECOVEC` selecting the machine directory from `arch/sh/boards/Makefile`.

Risks and test signals: Missing either object can break board boot or suspend. Tests include EcoVec24 build, setup object linkage, and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ecovec24/Makefile -->
