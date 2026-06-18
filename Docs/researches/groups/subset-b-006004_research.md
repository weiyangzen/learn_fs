# subset-b-006004 Research

Grouped source research for Xen public/kernel integration headers and Linux early init/root-mount files under `sources/distributed-fs/ceph-client`. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/vscsiif.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/vscsiif.h

## Purpose
`vscsiif.h` defines the Xen paravirtual SCSI frontend/backend wire ABI: Xenstore negotiation nodes, SCSI request and response ring payloads, scatter/gather grant descriptors, action codes, and result decoding macros.

## Important APIs, Types, and Functions
The header exports `struct scsiif_request_segment`, `struct vscsiif_request`, `struct vscsiif_response`, constants such as `VSCSIIF_ACT_SCSI_CDB`, `VSCSIIF_ACT_SCSI_ABORT`, `VSCSIIF_ACT_SCSI_RESET`, `VSCSIIF_SG_TABLESIZE`, `VSCSIIF_SG_GRANT`, `VSCSIIF_MAX_COMMAND_SIZE`, and `VSCSIIF_SENSE_BUFFERSIZE`, plus `XEN_VSCSIIF_RSLT_*` macros for SCSI and host status extraction. `DEFINE_RING_TYPES(vscsiif, ...)` creates the shared ring type.

## Control Flow
The frontend publishes `event-channel`, `ring-ref`, and optional protocol data in Xenstore, then sends CDB, abort, or reset requests through the ring. The backend maps grant references, performs the SCSI operation, and posts a response with echoed `rqid`, sense data, result, and residual length. Large I/O can use direct `seg[]` entries or indirect grant pages when `feature-sg-grant` is negotiated.

## State and Persistence Behavior
Persistent coordination state is in Xenstore nodes for vhost/device lifecycle and per-device states. Runtime state is the shared ring page, event channel, grant references, and request IDs; no file-backed persistence is owned by this header.

## Dependencies and Integration Points
It depends on Xen ring and grant-table definitions. It integrates guest SCSI frontend drivers, backend storage drivers, Xenstore tooling/libxl, event channels, grant-table mapping, and Linux SCSI mid-layer result conventions.

## Risks and Test Signals
Risks include ABI size drift, incorrect `nr_segments`/`VSCSIIF_SG_GRANT` interpretation, untrusted grant offsets and lengths, stale Xenstore reconfiguration states, and mismatched SCSI result encoding. Test signals include frontend/backend ring ABI compile checks, direct and indirect SG I/O, hot-add/hot-remove Xenstore state transitions, abort/reset handling, and sense/residual propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/vscsiif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/xenbus.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/xenbus.h

## Purpose
`io/xenbus.h` defines the public Xenbus device-state enumeration used by frontend and backend drivers to coordinate connection, teardown, and reconfiguration through Xenstore.

## Important APIs, Types, and Functions
The key type is `enum xenbus_state` with values from `XenbusStateUnknown` through `XenbusStateReconfigured`, including the normal bring-up sequence `Initialising`, `InitWait`, `Initialised`, `Connected`, the teardown states `Closing` and `Closed`, and reconfiguration states `Reconfiguring` and `Reconfigured`.

## Control Flow
Drivers publish their own state and watch the peer state. A normal device moves from initialization to `Connected`; unplug or error paths move through `Closing` to `Closed`; dynamic changes use `Reconfiguring` and `Reconfigured` before returning to connected operation.

## State and Persistence Behavior
The enum values are persisted as integer Xenstore state nodes for the lifetime of a Xen device. They are a coordination protocol, not kernel memory state by themselves.

## Dependencies and Integration Points
This header is consumed by Linux `xenbus.h`, Xen frontend/backend drivers, and tooling that creates or observes Xenstore device nodes. It must remain stable across guest, backend, and toolstack versions.

## Risks and Test Signals
Risks are state-machine deadlocks, drivers treating a state as stronger than it is, and incompatible tooling assumptions around reconfiguration states. Test signals include Xenbus probe/remove tests, peer-state watch delivery, suspend/resume state replay, and hotplug error-path coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/xenbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/xs_wire.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/xs_wire.h

## Purpose
`xs_wire.h` defines the Xenstore client/server wire protocol: request types, error-string mapping, socket message header layout, shared ring structure, payload/path limits, server feature bits, and reconnect/error status fields.

## Important APIs, Types, and Functions
Important definitions include `enum xsd_sockmsg_type`, `struct xsd_sockmsg`, `struct xsd_errors`, `enum xs_watch_type`, `struct xenstore_domain_interface`, `XENSTORE_RING_SIZE`, `MASK_XENSTORE_IDX`, `XENSTORE_PAYLOAD_MAX`, path length limits, server feature flags, and connection/error status constants.

## Control Flow
Clients send an `xsd_sockmsg` header plus string payload through a socket or shared ring. Xenstored replies with matching `req_id` and may emit asynchronous watch events. Transactions use `XS_TRANSACTION_START` and `XS_TRANSACTION_END`; watches use path/token pairs; reconnect-capable rings use the `connection` and `error` fields.

## State and Persistence Behavior
The ring stores request/response bytes and producer/consumer indices shared between guest and xenstored. Xenstore contents persist in the Xenstore daemon's runtime database, while the ring fields only describe live communication state.

## Dependencies and Integration Points
The header assumes errno names are visible where included and is consumed by Xenstore libraries and guest kernels. It integrates with Linux xenbus operations, Xenstore watches, backend/frontend device discovery, and suspend/resume reconnect handling.

## Risks and Test Signals
Risks include producer/consumer index corruption, payload/path length violations, error-string mismatches, watch-event ordering races, and reconnect support mismatches. Test signals include transaction retry tests, watch delivery/unwatch behavior, ring wraparound, max payload rejection, and feature-bit fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/xs_wire.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/memory.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/memory.h

## Purpose
`memory.h` defines Xen public memory-operation ABI structures and command numbers for changing domain reservations, exchanging pages, mapping foreign or special pages into guest pseudo-physical space, querying memory maps, and acquiring toolstack resources.

## Important APIs, Types, and Functions
Core commands include `XENMEM_increase_reservation`, `decrease_reservation`, `populate_physmap`, `exchange`, `maximum_ram_page`, `current_reservation`, `maximum_reservation`, `machphys_mfn_list`, `machphys_mapping`, `add_to_physmap`, `add_to_physmap_range`, `memory_map`, `machine_memory_map`, `remove_from_physmap`, and `acquire_resource`. Key structs are `xen_memory_reservation`, `xen_memory_exchange`, `xen_machphys_mfn_list`, `xen_add_to_physmap`, `xen_add_to_physmap_range`, `xen_memory_map`, `xen_remove_from_physmap`, and `xen_mem_acquire_resource`.

## Control Flow
Guests or tool domains fill command-specific structures with guest handles and call `HYPERVISOR_memory_op`. Reservation operations allocate/free extents, exchanges atomically replace old extents with new populated extents, physmap operations install or remove mappings, and resource acquisition maps grant-table or ioreq-server frames for a tools domain.

## State and Persistence Behavior
The ABI mutates Xen's domain memory reservation, p2m/m2p mappings, resource ownership, and guest-visible memory maps. State persists until later memory ops, ballooning, hotplug, teardown, or domain destruction.

## Dependencies and Integration Points
It depends on Xen public base types from `xen.h` and guest-handle macros. Linux balloon, memory hotplug, grant-table, device-model, and PV MMU code use these structures to coordinate with Xen.

## Risks and Test Signals
Risks include confusing MFN/GMFN/GPFN roles, uninitialized `nr_exchanged`, overlapping exchange arrays, per-index error handling in ranged mapping, partial resource acquisition cleanup, and privilege checks on foreign domains. Test signals include balloon increase/decrease, populate/exchange partial failures, add/remove physmap range tests, memory-map query sizing, and HVM/PV `acquire_resource` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/nmi.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/nmi.h

## Purpose
`nmi.h` defines Xen's x86-oriented NMI reason bits and the small `nmi_op` ABI for registering or unregistering an NMI callback.

## Important APIs, Types, and Functions
Important constants are `XEN_NMIREASON_io_error`, `XEN_NMIREASON_pci_serr`, `XEN_NMIREASON_unknown`, `XENNMI_register_callback`, and `XENNMI_unregister_callback`. `struct xennmi_callback` carries the callback handler address.

## Control Flow
A privileged caller, currently meaningful for dom0 VCPU0, registers a handler address through `nmi_op`. Xen records the callback and later invokes it for NMI events with reason bits exposed via architecture shared info. Unregister clears the callback.

## State and Persistence Behavior
Registered callback state lives in Xen for the calling VCPU until unregistered or domain teardown. NMI reason bits are transient diagnostic state in shared info.

## Dependencies and Integration Points
It includes `xen/interface/xen.h` for handle definitions and integrates with x86 Xen low-level trap/NMI handling, dom0 machine-check and hardware-error reporting, and platform interrupt diagnostics.

## Risks and Test Signals
Risks include invalid handler addresses, non-dom0 callers receiving `EINVAL`, architecture-specific reason interpretation, and callback lifetime across CPU hotplug or suspend. Test signals include register/unregister hypercall return paths, injected/observed NMI reason bits, and dom0-only permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/nmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/physdev.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/physdev.h

## Purpose
`physdev.h` defines Xen physical-device hypercall operations for IRQ EOI/status, I/O privilege setup, APIC access, PIRQ/MSI mapping, PCI device management, MSI-X preparation, PCI reset notification, and debug-port reset coordination.

## Important APIs, Types, and Functions
Key command families include `PHYSDEVOP_eoi`, `pirq_eoi_gmfn_v1/v2`, `irq_status_query`, `set_iopl`, `set_iobitmap`, `apic_read/write`, `alloc/free_irq_vector`, `map_pirq`, `unmap_pirq`, PCI add/remove/reset operations, `prepare_msix`, `release_msix`, and `dbgp_op`. Structures include `physdev_eoi`, `physdev_pirq_eoi_gmfn`, `physdev_irq_status_query`, `physdev_map_pirq`, `physdev_pci_device_add`, `physdev_pci_device`, and `pci_device_reset`.

## Control Flow
Privileged guests issue `physdev_op` with a command-specific struct. IRQ paths query whether EOI is required, register shared EOI bitmaps, and signal EOI after interrupt service. Device-management paths map GSIs/MSIs to PIRQs, announce PCI devices or removal, preserve MSI-X resources around assignment, and notify Xen after hardware reset.

## State and Persistence Behavior
The operations mutate Xen's IRQ routing, EOI tracking page, physical device ownership, MSI/PIRQ mappings, and cached PCI state. These are runtime hypervisor state tied to domains and physical devices.

## Dependencies and Integration Points
The header relies on Xen base types and is used by dom0/hardware-domain PCI, IRQ, APIC, and passthrough code. It interacts with Linux PCI reset paths, MSI/MSI-X setup, event channels, and interrupt controllers.

## Risks and Test Signals
Risks include stale PIRQ mappings, incorrect MSI segment/vector fields, mismatched v1/v2 EOI semantics, unsafe I/O privilege exposure, and failing to notify Xen after reset. Test signals include PCI passthrough attach/detach, MSI/MSI-X interrupt delivery, EOI bitmap behavior, APIC access checks, and reset mode coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/physdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/platform.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/platform.h

## Purpose
`platform.h` defines dom0-oriented Xen platform operations for host time, memory type ranges, microcode, EFI runtime services, firmware information, ACPI sleep, CPU frequency and idle data, processor PM tables, CPU/memory hotplug, core parking, symbol lookup, and dom0 console discovery.

## Important APIs, Types, and Functions
The central ABI is `struct xen_platform_op` with `cmd`, `interface_version`, and a union of command payloads. Major payloads include `xenpf_settime32/64`, `xenpf_add_memtype`, `xenpf_del_memtype`, `xenpf_read_memtype`, `xenpf_microcode_update`, `xenpf_efi_runtime_call`, `xenpf_firmware_info`, `xenpf_enter_acpi_sleep`, `xenpf_change_freq`, `xenpf_getidletime`, `xenpf_set_processor_pminfo`, `xenpf_pcpuinfo`, hotplug structs, `xenpf_core_parking`, and `xenpf_symdata`.

## Control Flow
The hardware domain fills a platform op and calls `HYPERVISOR_platform_op`. Xen dispatches by command, reading or updating host-wide platform state such as wallclock, MTRR/memtype setup, firmware tables, EFI variables, ACPI sleep state, CPU PM capabilities, and hotplug state.

## State and Persistence Behavior
Most operations change host or hypervisor platform state rather than guest-local state: time, microcode, memory type handles, EFI variables, CPU online state, PM tables, and hotplug topology. Query operations return snapshots.

## Dependencies and Integration Points
It depends on `xen/interface/xen.h` and `dom0_vga_console_info`. Linux dom0 ACPI, EFI, CPUfreq/cpuidle, microcode, hotplug, firmware, and console code integrate through this ABI.

## Risks and Test Signals
Risks include interface-version mismatch, union padding/size assumptions, unsafe EFI variable buffers, incorrect PM dependency arrays, privilege-sensitive host changes, and 32-bit time limitations. Test signals include EFI get/set variable paths, ACPI sleep entry, CPU online/offline/hotadd, PM table registration, microcode update failure modes, and symbol/console queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/sched.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/sched.h

## Purpose
`sched.h` defines Xen scheduler-operation ABI commands for guest yield/block/shutdown, event-channel polling, remote shutdown, shutdown-code latching, domain watchdogs, and dom0 pin override.

## Important APIs, Types, and Functions
Important commands are `SCHEDOP_yield`, `block`, `shutdown`, `poll`, `remote_shutdown`, `shutdown_code`, `watchdog`, and `pin_override`. Payloads include `sched_shutdown`, `sched_poll`, `sched_remote_shutdown`, `sched_watchdog`, and `sched_pin_override`. Shutdown reasons include poweroff, reboot, suspend, crash, watchdog, and soft reset.

## Control Flow
Guests call `HYPERVISOR_sched_op`. Blocking atomically unmasks event delivery when needed, poll waits for event-channel ports or a timeout, shutdown notifies control software, and watchdog setup/poke/destroy changes hypervisor timers. Suspend has special x86 PV calling conventions for start-info MFN.

## State and Persistence Behavior
Scheduler state is runtime hypervisor state: VCPU runnable/block status, pending shutdown reason, watchdog timer, and optional pin override. Shutdown reason is visible to control tooling until acted on.

## Dependencies and Integration Points
It depends on event-channel port types and Xen base domain types. Linux Xen time/event-channel, suspend/resume, panic/reboot, and watchdog paths use this ABI.

## Risks and Test Signals
Risks include wakeup-wait races if blocking is not used correctly, wrong suspend return interpretation, remote shutdown misuse, watchdog accidentally terminating a domain, and pin override privilege failures. Test signals include event-channel poll/block tests, reboot/poweroff/suspend flows, watchdog expiry/poke/destroy, and soft-reset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/vcpu.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/vcpu.h

## Purpose
`vcpu.h` defines Xen VCPU hypercall operations for VCPU initialization, hotplug, runstate and time accounting, periodic/single-shot timers, per-VCPU info placement, NMI delivery, and physical CPU identity lookup.

## Important APIs, Types, and Functions
Commands include `VCPUOP_initialise`, `up`, `down`, `is_up`, `get_runstate_info`, `register_runstate_memory_area`, timer set/stop operations, `register_vcpu_info`, `send_nmi`, `get_physid`, and `register_vcpu_time_memory_area`. Key structs include `vcpu_runstate_info`, `vcpu_register_runstate_memory_area`, `vcpu_set_periodic_timer`, `vcpu_set_singleshot_timer`, `vcpu_register_vcpu_info`, `vcpu_get_physid`, and `vcpu_register_time_memory_area`.

## Control Flow
The guest initializes VCPUs with architecture context, brings them up, and may later bring them down asynchronously. Runtime code can query or register shared runstate/time areas so Xen updates accounting without hypercalls. Timer operations arm per-VCPU timers, and privileged paths may send NMIs or query physical IDs.

## State and Persistence Behavior
State lives in Xen's VCPU records and in guest-provided shared memory areas. Runstate time accumulates across scheduling transitions, timer settings persist until stopped or fired, and registered `vcpu_info` placement remains active for the VCPU.

## Dependencies and Integration Points
This header is included by Linux Xen CPU hotplug, scheduler accounting, pvclock, event-channel, and suspend/resume code. It depends on Xen base time and VCPU info structures.

## Risks and Test Signals
Risks include registering memory that crosses page boundaries, interpreting asynchronous `VCPUOP_down` as complete too early, stale runstate update flags, timer deadlines in the past, and architecture-specific physical ID assumptions. Test signals include CPU hotplug, stolen-time accounting, vDSO/pvclock time reads, timer interrupt delivery, and NMI/physid privilege checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/vcpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/version.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/version.h

## Purpose
`version.h` defines `HYPERVISOR_xen_version` subcommands and payloads for querying Xen version, build metadata, capabilities, feature submaps, host page size, guest handle, command line, and build ID.

## Important APIs, Types, and Functions
Commands include `XENVER_version`, `extraversion`, `compile_info`, `capabilities`, `changeset`, `platform_parameters`, `get_features`, `pagesize`, `guest_handle`, `commandline`, and `build_id`. Payload structs include `xen_extraversion`, `xen_compile_info`, `xen_capabilities_info`, `xen_changeset_info`, `xen_platform_parameters`, `xen_feature_info`, `xen_commandline`, and variable-length `xen_build_id`.

## Control Flow
Guests call the version hypercall with a subcommand and optional output buffer. Fixed-size queries copy strings or fields into guest memory; `XENVER_build_id` can be called with an empty parameter to discover required size before retrieving bytes.

## State and Persistence Behavior
The file exposes read-only hypervisor build/runtime metadata. No guest state is mutated except output buffers supplied by the caller.

## Dependencies and Integration Points
It includes Xen feature definitions and is used by Linux Xen setup, feature detection, compatibility gating, diagnostics, and user-visible reporting.

## Risks and Test Signals
Risks include buffer-size mistakes, feature submap drift, relying on build strings for logic, and page-size assumptions. Test signals include boot-time feature detection, version compatibility checks, build-id two-step query, and capability string parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/xen-mca.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/xen-mca.h

## Purpose
`xen-mca.h` defines the x86 Xen machine-check architecture ABI for fetching MCA logs, acknowledging entries, notifying affected domains, retrieving physical CPU information, injecting MSRs/MCEs for testing, and sharing Linux-compatible MCE log records.

## Important APIs, Types, and Functions
Important types include `mcinfo_common`, `mcinfo_global`, `mcinfo_bank`, `mcinfo_extended`, `mcinfo_recovery`, `mc_info`, `mcinfo_logical_cpu`, `xen_mc_fetch`, `xen_mc_notifydomain`, `xen_mc_physcpuinfo`, `xen_mc_msrinject`, `xen_mc_mceinject`, `xen_mc`, `xen_mce`, and `xen_mce_log`. Helpers include `x86_mcinfo_nentries`, `x86_mcinfo_first`, `x86_mcinfo_next`, and `x86_mcinfo_lookup`.

## Control Flow
Dom0 receives `VIRQ_MCA`, calls the MCA hypercall to fetch urgent or nonurgent error data, parses typed `mcinfo_*` entries, optionally notifies a guest domain, and acknowledges fetched records. Injection commands target CPUs for validation. The inline lookup helper scans the variable-sized entry list by type.

## State and Persistence Behavior
Xen maintains machine-check records and fetch IDs until acknowledged. `xen_mce_log` is a fixed-length in-memory ring-like log with overflow flag and finished markers; records are not persistent across reboot.

## Dependencies and Integration Points
It depends on x86 Xen arch hypercall numbering, VIRQ definitions, guest-handle macros, and Linux ioctl encoding. It integrates Xen with dom0 machine-check handling, mcelog-compatible consumers, CPU topology reporting, and hardware-error recovery workflows.

## Risks and Test Signals
Risks include parsing malformed or truncated variable-sized entries, failing to ACK fetched data, preserving `xen_mce` field offsets, injection privilege misuse, and recovery-action ambiguity. Test signals include injected MCE/MSR paths, urgent/nonurgent fetch/ack cycles, logical CPU info queries, overflow handling, and mcelog ABI compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/xen-mca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/xen.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/xen.h

## Purpose
`interface/xen.h` is the central public Xen guest ABI header. It assigns hypercall numbers, virtual IRQ numbers, MMU update and extended MMU operation formats, console/vm-assist commands, domain IDs, multicall layout, shared VCPU/time/event-channel structures, boot `start_info`, dom0 console info, and transient memory op layout.

## Important APIs, Types, and Functions
Major definitions include `__HYPERVISOR_*` IDs, `VIRQ_*`, `MMU_*`, `MMUEXT_*`, `UVMF_*`, `CONSOLEIO_*`, `VMASST_*`, `domid_t` and reserved `DOMID_*` values, `struct mmu_update`, `struct mmuext_op`, `struct multicall_entry`, `struct vcpu_time_info`, `struct vcpu_info`, `struct shared_info`, `struct start_info`, `struct xen_multiboot_mod_list`, `struct dom0_vga_console_info`, and `struct tmem_op`.

## Control Flow
Guests use hypercall numbers and command payloads to enter Xen. PV guests use MMU update and mmuext sequences to construct, pin, switch, flush, and update page tables. Event-channel delivery is mediated by `shared_info` bitmaps and per-VCPU pending/mask fields. Boot code consumes `start_info` to find shared info, Xenstore, console, modules/initrd, page tables, command line, and p2m data.

## State and Persistence Behavior
This header defines shared memory state (`shared_info`, `vcpu_info`, wallclock, event-channel bitmaps), boot-time immutable/resume-updated `start_info`, and hypervisor-managed MMU/domain state changed through hypercalls. Shared state persists while the domain runs and is refreshed on resume.

## Dependencies and Integration Points
It includes architecture-specific Xen interface definitions and is included by most Xen guest, event-channel, memory, time, boot, and driver code. Linux Xen setup, pvclock, event channels, PV MMU, console, Xenstore, and dom0 display paths all depend on this ABI.

## Risks and Test Signals
Risks include breaking struct sizes/offsets, page-table writable/pinning rule violations, event-channel lost-edge handling mistakes, seqlock-style time reads done incorrectly, boot `start_info` interpretation drift, and PAT/cache attribute translation bugs. Test signals include PV boot/resume, event-channel storm/mask tests, pvclock consistency, MMU update negative tests, console I/O, multicall batching, and dom0 console discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/xen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/xenpmu.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/xenpmu.h

## Purpose
`xenpmu.h` defines Xen PMU virtualization operations, version fields, profiling modes/features, operation parameters, and the shared PMU interrupt data structure.

## Important APIs, Types, and Functions
Commands include `XENPMU_mode_get`, `mode_set`, `feature_get`, `feature_set`, `init`, `finish`, `lvtpc_set`, and `flush`. `struct xen_pmu_params` carries version, value, and target VCPU. Modes include `XENPMU_MODE_OFF`, `SELF`, `HV`, and `ALL`; `XENPMU_FEATURE_INTEL_BTS` describes BTS support. `struct xen_pmu_data` stores interrupted VCPU, physical CPU, domain ID, padding, and architecture-specific PMU data.

## Control Flow
Guests or dom0 call `HYPERVISOR_xenpmu_op` to query/set mode and features, initialize shared PMU handling, update LVTPC state, flush PMU state, and finish profiling. On PMU interrupts, Xen fills shared data and notifies the appropriate VCPU.

## State and Persistence Behavior
Mode and feature settings live in Xen PMU virtualization state. `xen_pmu_data` is shared live interrupt state written by Xen and read by the guest; architecture-specific fields may be bidirectionally writable depending on arch rules.

## Dependencies and Integration Points
It includes `xen.h` and relies on `struct xen_pmu_arch` from architecture headers. It integrates with Linux perf/Xen PMU support, VIRQ_XENPMU delivery, dom0 hypervisor profiling, and guest self-profiling.

## Risks and Test Signals
Risks include exposing cross-domain samples in the wrong mode, version mismatch, architecture-specific PMU field races, and LVTPC misprogramming. Test signals include mode transitions, perf sampling in guest/dom0 modes, BTS feature queries, PMU interrupt delivery, and cleanup on finish.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/xenpmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/mem-reservation.h -->
# sources/distributed-fs/ceph-client/include/xen/mem-reservation.h

## Purpose
`mem-reservation.h` declares Linux-side helpers for Xen memory reservation growth/shrink, optional page scrubbing, and PV MMU virtual-address mapping updates after reservation changes.

## Important APIs, Types, and Functions
Important symbols are `xen_scrub_pages`, `xenmem_reservation_scrub_page()`, `xenmem_reservation_va_mapping_update()`, `xenmem_reservation_va_mapping_reset()`, `xenmem_reservation_increase()`, and `xenmem_reservation_decrease()`. PV MMU-specific implementation hooks are declared under `CONFIG_XEN_HAVE_PVMMU`.

## Control Flow
Callers increase or decrease a reservation using frame arrays. Scrubbing clears highmem pages when `xen_scrub_pages` is enabled. On PV domains with PV MMU support, wrapper functions call architecture helpers to update or reset virtual mappings for pages whose machine frames changed.

## State and Persistence Behavior
The helpers mutate domain memory reservation and page-to-frame mappings through implementation code. `xen_scrub_pages` is a runtime policy flag; page contents are cleared only in memory and not persisted.

## Dependencies and Integration Points
It depends on Linux highmem and Xen page helpers. It integrates ballooning, memory hotplug, unpopulated page allocation, and PV MMU mapping consistency.

## Risks and Test Signals
Risks include stale virtual mappings after frame replacement, failing to scrub pages before reuse, PV/HVM domain path confusion, and partial reservation failures. Test signals include balloon inflate/deflate, highmem page scrubbing, PV mapping update/reset coverage, and memory hotplug under Xen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/mem-reservation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/page.h -->
# sources/distributed-fs/ceph-client/include/xen/page.h

## Purpose
`page.h` provides common Linux Xen page-size and PFN conversion helpers, defines the fixed Xen hypercall page size, and declares extra memory tracking state used by Xen memory setup.

## Important APIs, Types, and Functions
Key macros are `XEN_PAGE_SHIFT`, `XEN_PAGE_SIZE`, `XEN_PAGE_MASK`, `xen_offset_in_page`, `xen_pfn_to_page`, `page_to_xen_pfn`, `XEN_PFN_PER_PAGE`, `XEN_PFN_DOWN`, and `XEN_PFN_UP`. `xen_page_to_gfn()` returns the GFN for the first Xen 4K subpage of a Linux page. `struct xen_memory_region`, `xen_extra_mem`, and `xen_released_pages` track memory regions and released pages.

## Control Flow
There is no independent control flow. Callers use the macros when translating Linux pages/PFNs to Xen 4K PFNs or GFNs and when recording memory made available outside the initial reservation.

## State and Persistence Behavior
The header declares boot-time `xen_extra_mem` and runtime `xen_released_pages` counters. Conversion helpers are pure calculations based on Linux `PAGE_SHIFT` and architecture-provided pfn/gfn translation.

## Dependencies and Integration Points
It depends on `asm/page.h` and `asm/xen/page.h`. It is used by ballooning, grant-table, DMA, memory hotplug, and Xen boot memory setup.

## Risks and Test Signals
Risks include assumptions when Linux `PAGE_SIZE` is larger than Xen's 4K ABI page, incorrect subpage conversion, and stale extra-memory accounting. Test signals include builds on non-4K page architectures, balloon page conversions, grant mappings, and memory-region accounting checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/pci.h -->
# sources/distributed-fs/ceph-client/include/xen/pci.h

## Purpose
`pci.h` declares Linux Xen PCI helper functions for dom0 device reset and device-domain ownership tracking, with safe stubs when dom0 support is disabled.

## Important APIs, Types, and Functions
The exported helpers are `xen_reset_device()`, `xen_find_device_domain_owner()`, `xen_register_device_domain_owner()`, and `xen_unregister_device_domain_owner()`. Non-`CONFIG_XEN_DOM0` stubs return `-1`.

## Control Flow
Dom0 PCI code can reset a device through Xen-aware paths and register which domain owns a PCI device. In non-dom0 builds, callers receive failure immediately and should follow non-Xen or unsupported paths.

## State and Persistence Behavior
Real implementations maintain runtime ownership association between PCI devices and Xen domains and may trigger hypervisor reset bookkeeping. This header stores no state itself.

## Dependencies and Integration Points
It depends on `struct pci_dev` declarations from users. It integrates Linux PCI passthrough, dom0 device assignment, Xen physdev reset notification, and hotplug/remove paths.

## Risks and Test Signals
Risks include ownership leaks, reset without hypervisor notification, stubs being treated as success, and races during device removal. Test signals include dom0 passthrough attach/detach, reset paths, owner lookup consistency, and non-dom0 build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/platform_pci.h -->
# sources/distributed-fs/ceph-client/include/xen/platform_pci.h

## Purpose
`platform_pci.h` defines Xen platform PCI I/O port offsets, magic/product/version values, unplug command bits for emulated disks/NICs, and config-dependent helpers for deciding whether PV devices require unplugging legacy emulation.

## Important APIs, Types, and Functions
Constants include `XEN_IOPORT_MAGIC_VAL`, `XEN_IOPORT_LINUX_PRODNUM`, `XEN_IOPORT_LINUX_DRVVER`, `XEN_IOPORT_*` offsets, `XEN_UNPLUG_ALL_IDE_DISKS`, `XEN_UNPLUG_ALL_NICS`, `XEN_UNPLUG_AUX_IDE_DISKS`, `XEN_UNPLUG_ALL`, `XEN_UNPLUG_UNNECESSARY`, and `XEN_UNPLUG_NEVER`. Inline helpers include `xen_must_unplug_nics()`, `xen_must_unplug_disks()`, and PV-device presence stubs/externs.

## Control Flow
PVHVM platform PCI code probes the magic port, writes driver/product version data, and may write unplug bits to remove emulated IDE/NIC devices when Xen PV frontends are available. Inline helpers compile the unplug policy from frontend and PVHVM config options.

## State and Persistence Behavior
I/O port writes change Xen platform-device emulation state during boot. Presence queries report runtime detection of PV and legacy devices; this header itself holds no state.

## Dependencies and Integration Points
It integrates Xen PVHVM boot, platform PCI driver code, blkfront/netfront availability, and legacy device unplug sequencing.

## Risks and Test Signals
Risks include unplugging legacy devices before PV frontends are usable, duplicate disks/NICs if unplug fails, config-dependent helpers returning unexpected defaults, and I/O width mistakes on shared offsets. Test signals include PVHVM boots with block/net frontends built-in and modular, mixed legacy/PV disk detection, and platform PCI magic/version probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/platform_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/swiotlb-xen.h -->
# sources/distributed-fs/ceph-client/include/xen/swiotlb-xen.h

## Purpose
`swiotlb-xen.h` declares Xen-specific SWIOTLB DMA synchronization hooks and DMA map operations used when guest-visible DMA addresses differ from machine addresses or when bounce buffering is required.

## Important APIs, Types, and Functions
The header declares `xen_dma_sync_for_cpu()`, `xen_dma_sync_for_device()`, and `xen_swiotlb_dma_ops`. It includes generic `linux/swiotlb.h` and architecture-specific Xen SWIOTLB definitions.

## Control Flow
Device DMA paths use `xen_swiotlb_dma_ops` for mapping and unmapping; sync helpers transfer ownership/cache visibility between device and CPU for a DMA address, size, and direction.

## State and Persistence Behavior
State is held by the SWIOTLB pool and DMA mappings in implementation code. Sync calls operate on transient DMA buffers and do not persist beyond mapping lifetime.

## Dependencies and Integration Points
It integrates Linux DMA API, SWIOTLB bounce buffering, Xen grant/DMA restrictions, and architecture-specific address translation.

## Risks and Test Signals
Risks include stale CPU/device cache visibility, wrong DMA direction, bounce-buffer size exhaustion, and missing arch support. Test signals include DMA mapping tests on Xen guests, bidirectional sync coverage, high-memory DMA, and restricted-memory virtio/grant DMA configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/swiotlb-xen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/xen-front-pgdir-shbuf.h -->
# sources/distributed-fs/ceph-client/include/xen/xen-front-pgdir-shbuf.h

## Purpose
`xen-front-pgdir-shbuf.h` declares a frontend helper for sharing buffers with a Xen backend through a page-directory grant-reference scheme, supporting frontend-owned buffers and backend-allocated buffers.

## Important APIs, Types, and Functions
Core types are `struct xen_front_pgdir_shbuf` and `struct xen_front_pgdir_shbuf_cfg`. Public helpers are `xen_front_pgdir_shbuf_alloc()`, `xen_front_pgdir_shbuf_get_dir_start()`, `xen_front_pgdir_shbuf_map()`, `xen_front_pgdir_shbuf_unmap()`, and `xen_front_pgdir_shbuf_free()`.

## Control Flow
Callers prepare a config with Xenbus device, page count, optional frontend pages, buffer object, and backend-allocation mode. Allocation creates grant references and page-directory storage. The frontend publishes the directory grant start to the backend, maps backend-provided pages when needed, then unmaps and frees grants/resources during teardown.

## State and Persistence Behavior
`struct xen_front_pgdir_shbuf` tracks grant refs, directory bytes, shared pages, Xenbus device, mode-specific ops, and backend map handles. State persists for the shared buffer lifetime and is released by `free()`.

## Dependencies and Integration Points
It depends on Linux kernel types and Xen grant-table APIs. It integrates frontend drivers needing bulk shared memory with Xenbus negotiation and backend grant mapping.

## Risks and Test Signals
Risks include leaked grant references, mismatched frontend/backend allocation mode, directory layout disagreement, map-handle leaks, and freeing pages while a backend still maps them. Test signals include allocation/map/unmap/free cycles, backend-allocated and frontend-allocated modes, grant-table exhaustion, and Xenbus disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/xen-front-pgdir-shbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/xen-ops.h -->
# sources/distributed-fs/ceph-client/include/xen/xen-ops.h

## Purpose
`xen-ops.h` declares Linux Xen core operations for suspend/resume, timers, reboot, runstate/stolen-time accounting, shutdown events, foreign frame remapping, EFI runtime setup, preemptible hypercall tracking, and grant-DMA/virtio restrictions.

## Important APIs, Types, and Functions
Important symbols include per-CPU `xen_vcpu` and `xen_vcpu_id`, `xen_vcpu_nr()`, `xen_arch_pre_suspend()`, `xen_arch_post_suspend()`, `xen_timer_resume()`, `xen_reboot()`, `xen_resume_notifier_register()`, `xen_vcpu_stolen()`, `xen_setup_runstate_info()`, `xen_time_setup_guest()`, `xen_steal_clock()`, `xen_setup_shutdown_event()`, `xen_remap_pfn()`, `xen_remap_domain_gfn_array()`, `xen_remap_domain_mfn_array()`, `xen_remap_domain_gfn_range()`, `xen_unmap_domain_gfn_range()`, `xen_xlate_map_ballooned_pages()`, and `xen_running_on_version_or_later()`.

## Control Flow
Suspend paths notify architecture code, stop/resume timers, and call registered notifiers. Mapping helpers choose PV or auto-translated GFN paths based on `xen_pv_domain()`, with PV MFN mapping limited to PV domains. Preemptible hypercall markers set a per-CPU flag only for non-preemptible PV builds.

## State and Persistence Behavior
State includes per-CPU Xen VCPU pointers/ids, contiguous bitmap, runstate accounting areas, shutdown event channels, remapped VMA ranges, and optional preemptible hypercall flags. Most state lives for boot/runtime and is refreshed across suspend/resume.

## Dependencies and Integration Points
It depends on Linux percpu/notifier/EFI/virtio APIs and Xen feature/VCPU interfaces. It integrates architecture Xen code, mmu/remap code, event channels, pvclock, scheduler accounting, EFI, virtio grant DMA, and user VMA mappings of foreign pages.

## Risks and Test Signals
Risks include wrong PV versus auto-xlate mapping path, missing `err_ptr` for PV GFN arrays, stale VCPU ids after hotplug, suspend/resume ordering bugs, and restricted-memory virtio misclassification. Test signals include suspend/resume, stolen-time accounting, foreign grant mapping/unmapping, version-gated behavior, CPU hotplug, and virtio under Xen grant DMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/xen-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/xen.h -->
# sources/distributed-fs/ceph-client/include/xen/xen.h

## Purpose
`include/xen/xen.h` is the Linux-side Xen environment header. It exposes whether the kernel is native, PV, HVM, PVH, or initial domain, declares Xen boot flags and PVH start info, and provides allocation and mergeability helpers that abstract Xen memory behavior.

## Important APIs, Types, and Functions
Key definitions are `enum xen_domain_type`, `xen_domain_type`, `xen_pvh`, `xen_pv_domain()`, `xen_domain()`, `xen_hvm_domain()`, `xen_pvh_domain()`, `xen_initial_domain()`, `xen_start_flags`, `xen_pv_pci_possible`, `pvh_start_info`, `xen_prepare_pvh()`, `xen_pv_evtchn_do_upcall()`, `xen_biovec_phys_mergeable()`, `xen_alloc_unpopulated_pages()`, `xen_free_unpopulated_pages()`, `arch_xen_unpopulated_init()`, and `xen_processor_present()`.

## Control Flow
Boot code sets domain type and flags; later code branches through inline predicates to select Xen-specific paths. Unpopulated page helpers use dedicated unpopulated allocation when configured, otherwise fall back to ballooned pages. Dom0-only `xen_initial_domain()` checks `SIF_INITDOMAIN`.

## State and Persistence Behavior
Global domain type, PVH flag, start flags, PVH start info, saved max memory, and unpopulated page counters persist for the kernel lifetime. The header primarily exposes state managed elsewhere.

## Dependencies and Integration Points
It depends on Linux types, x86 feature detection, Xen HVM start-info UAPI, ballooning, ACPI/dom0 conditionals, and architecture hypervisor headers. It is included across block, memory, event-channel, ACPI, and Xen driver code.

## Risks and Test Signals
Risks include compile-time stubs masking unsupported paths, `BUG()` in `xen_processor_present()` when called without dom0 ACPI support, wrong domain predicate decisions, and fallback balloon allocation differences. Test signals include native/PV/HVM/PVH boot builds, dom0 detection, unpopulated page allocation, block bio merge behavior, and ACPI processor presence checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/xen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/xenbus.h -->
# sources/distributed-fs/ceph-client/include/xen/xenbus.h

## Purpose
`xenbus.h` declares the Linux Xenbus driver/device API used to discover Xenstore devices, register frontend/backend drivers, read and write Xenstore nodes, manage watches and transactions, transition states, set up grant rings and event channels, and expose xenbus device files.

## Important APIs, Types, and Functions
Key types are `struct xenbus_watch`, `struct xenbus_device`, `struct xenbus_device_id`, `struct xenbus_driver`, and `struct xenbus_transaction`. Important APIs include `xenbus_register_frontend/backend`, `xenbus_unregister_driver`, `xenbus_directory/read/write/exists/rm`, transaction start/end, `xenbus_scanf`, `xenbus_read_unsigned`, `xenbus_printf`, `xenbus_gather`, store notifiers, watch registration, suspend/resume hooks, `xenbus_switch_state`, ring setup/map/unmap helpers, event-channel allocation/free, state reading, and error/fatal reporting.

## Control Flow
Drivers register with the Xenbus core, probe devices discovered in Xenstore, read peer details, set up grant rings and event channels, switch to connected state, and react to peer state changes through watches. Xenstore operations can be grouped in transactions; suspend/resume pauses and restores store communication and watches.

## State and Persistence Behavior
`struct xenbus_device` tracks device path, peer path/id, current state, watches, work, completions, reclaim semaphore, and event statistics. Xenstore nodes persist outside the kernel in xenstored; ring mappings and event channels persist until teardown.

## Dependencies and Integration Points
It depends on Linux device model, notifier, mutex, completion, fs, semaphore, Xen grant table, Xenstore wire protocol, Xenbus state UAPI, and event channels. It is the main integration point for Xen block, net, console, balloon, SCSI, and custom frontend/backend drivers.

## Risks and Test Signals
Risks include transaction retry omissions, watch callback races, peer-state deadlocks, grant ring leaks, event-channel leaks/spurious events, suspend/resume watch loss, and failing to handle vanished devices. Test signals include frontend/backend probe/remove, Xenstore transaction conflict handling, watch queue behavior, ring setup teardown, event-channel allocation, and state-machine error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/xenbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/xenbus_dev.h -->
# sources/distributed-fs/ceph-client/include/xen/xenbus_dev.h

## Purpose
`xenbus_dev.h` defines ioctl command numbers for the `/dev/xen/xenbus_backend` userspace interface used by backend tooling to obtain/setup event-channel based Xenbus communication.

## Important APIs, Types, and Functions
The two exported ioctl numbers are `IOCTL_XENBUS_BACKEND_EVTCHN` and `IOCTL_XENBUS_BACKEND_SETUP`, both using ioctl type `'B'` with command numbers 0 and 1.

## Control Flow
Userspace opens the xenbus backend device and issues these ioctls to coordinate backend Xenbus event-channel setup. The header only defines command IDs; actual argument handling is in the device implementation.

## State and Persistence Behavior
No state is stored here. The ioctls affect runtime backend device state such as event-channel wiring and setup status in implementation code.

## Dependencies and Integration Points
It depends on Linux ioctl encoding and integrates userspace backend daemons/tooling with the kernel Xenbus backend device node.

## Risks and Test Signals
Risks include userspace/kernel ioctl number mismatch, missing permission checks in implementation, and ABI ambiguity due to zero-sized `_IOC_NONE` commands. Test signals include backend device open/ioctl tests, event-channel setup validation, and compatibility with existing backend tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/xenbus_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/Kconfig -->
# sources/distributed-fs/ceph-client/init/Kconfig

## Purpose
`init/Kconfig` is the top-level Linux kernel configuration menu for compiler/toolchain capability probes, general setup, kernel compression, IPC/accounting/scheduler/cgroup/namespace features, initramfs/bootconfig, core syscalls, debugging symbol support, perf, Rust, module/kexec/liveupdate inclusion, and broad architecture/block submenus.

## Important APIs, Types, and Functions
This is Kconfig data rather than C API. Important config symbols include toolchain probes (`CC_IS_GCC`, `CC_IS_CLANG`, `RUST_IS_AVAILABLE`, `CC_HAS_*`, `LD_*`), general boot settings (`LOCALVERSION`, `DEFAULT_INIT`, `DEFAULT_HOSTNAME`, compression choices), resource/accounting features (`PSI`, `TASKSTATS`, `VIRT_CPU_ACCOUNTING`, `NUMA_BALANCING`), cgroups/controllers, namespaces, `BLK_DEV_INITRD`, `BOOT_CONFIG`, optimization choices, `EXPERT`, syscall feature toggles (`FUTEX`, `EPOLL`, `IO_URING`, `RSEQ`, etc.), `KALLSYMS`, `PERF_EVENTS`, `RUST`, and included submenus.

## Control Flow
Kconfig evaluates compiler/linker/rust shell tests, dependencies, defaults, choices, and `select`/`imply` relations to produce `.config` and generated headers. Build and runtime code then compile or branch according to the selected symbols.

## State and Persistence Behavior
The persistent output is the kernel configuration and generated `include/config/*` dependency state. Several symbols intentionally force rebuilds when compiler or Rust versions change. Runtime behavior is affected indirectly by compiled-in options and boot parameters described by help text.

## Dependencies and Integration Points
It sources many subsystem Kconfig files and coordinates with scripts such as compiler probes, Rust availability checks, `setlocalversion`, initramfs config, and architecture Kconfig. It drives `init/Makefile`, initramfs extraction, bootconfig handling, cgroup/syscall availability, perf, module, block, and architecture builds.

## Risks and Test Signals
Risks include wrong toolchain feature detection, dependency cycles, defaults enabling costly features unexpectedly, stale rebuild triggers, and options whose help warns about compatibility or security tradeoffs. Test signals include `olddefconfig`, `randconfig`, compiler upgrade rebuild checks, KUnit initramfs tests, cgroup/namespace config matrices, and build coverage with GCC/Clang/Rust availability combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/Makefile -->
# sources/distributed-fs/ceph-client/init/Makefile

## Purpose
`init/Makefile` controls compilation of early kernel initialization objects, mount/initramfs support, delay calibration, init task, initramfs tests, and generated UTS version headers.

## Important APIs, Types, and Functions
Important build variables include `obj-y`, `obj-$(CONFIG_BLK_DEV_INITRD)`, `obj-$(CONFIG_GENERIC_CALIBRATE_DELAY)`, `mounts-y`, `mounts-$(CONFIG_BLK_DEV_RAM)`, `mounts-$(CONFIG_BLK_DEV_INITRD)`, `smp-flag-*`, `preempt-flag-*`, `build-version`, `build-timestamp`, and `filechk_uts_version`. It generates `utsversion-tmp.h` and `include/generated/utsversion.h`.

## Control Flow
Kbuild compiles `main.o`, `version.o`, `mounts.o`, optional `initramfs.o` or `noinitramfs.o`, optional `calibrate.o`, optional `initramfs_test.o`, and `init_task.o`. The `mounts.o` composite pulls in root-mount helpers according to block RAM/initrd config. Version object builds include generated UTS headers with temporary or final timestamps.

## State and Persistence Behavior
Generated UTS version headers persist in the build tree and encode build version, SMP/preempt flags, and timestamp truncated to 64 bytes. Clean rules remove `utsversion-tmp.h`.

## Dependencies and Integration Points
It integrates Kconfig options with early init source compilation and Kbuild `filechk`. It depends on `scripts/build-version`, `date`, generated headers, and object composition conventions.

## Risks and Test Signals
Risks include non-reproducible timestamps, UTS version truncation, mismatched initrd/noinitramfs object selection, and missing mount composite members. Test signals include builds with and without `BLK_DEV_INITRD`, `BLK_DEV_RAM`, `GENERIC_CALIBRATE_DELAY`, `INITRAMFS_TEST`, SMP/preempt variants, and reproducible build environment variables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/calibrate.c -->
# sources/distributed-fs/ceph-client/init/calibrate.c

## Purpose
`calibrate.c` implements generic loops-per-jiffy delay calibration, honoring an `lpj=` boot override, using architecture timer-based calibration when possible, falling back to convergence against jiffies, and publishing per-CPU and global delay-loop calibration.

## Important APIs, Types, and Functions
Important globals are `lpj_fine`, `preset_lpj`, per-CPU `cpu_loops_per_jiffy`, and global `loops_per_jiffy` from delay code. Key functions are `lpj_setup()`, `calibrate_delay_direct()`, `calibrate_delay_converge()`, weak `calibrate_delay_is_known()`, weak `calibration_delay_done()`, and public `calibrate_delay()`.

## Control Flow
Boot parsing records `lpj=`. `calibrate_delay()` first reuses per-CPU calibration, then preset `lpj`, then `lpj_fine`, then architecture-known calibration, then direct current-timer calibration, and finally binary convergence against jiffies. Direct calibration samples multiple jiffy intervals, filters out timer wrap/asynchronous-event noise, and drops outliers before accepting an estimate.

## State and Persistence Behavior
The chosen LPJ is stored per CPU and in global `loops_per_jiffy` for delay primitives. The `printed` static suppresses duplicate calibration banners after the first CPU. Calibration is runtime boot state and is not persisted across boots.

## Dependencies and Integration Points
It depends on jiffies, `__delay`, SMP CPU IDs, optional `read_current_timer`, printk, boot `__setup`, and architecture weak overrides. It integrates with busy-wait delay loops and CPU bring-up.

## Risks and Test Signals
Risks include bad LPJ from SMI/interrupt noise, timer wrap, mismatched CPU frequencies, invalid user `lpj=`, and long boot delays during convergence. Test signals include boots with/without `lpj=`, architectures with direct timer calibration, SMP secondary CPU calibration, noisy timer environments, and delay accuracy checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/calibrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/do_mounts.c -->
# sources/distributed-fs/ceph-client/init/do_mounts.c

## Purpose
`do_mounts.c` implements early root filesystem selection and mounting. It parses root-related boot parameters, waits for devices, loads initrd when configured, mounts NFS/CIFS/generic/block/nodev roots, mounts devtmpfs, pivots into the new rootfs, and selects ramfs versus tmpfs rootfs backing.

## Important APIs, Types, and Functions
Important state includes `root_mountflags`, `saved_root_name`, `root_wait`, `root_mount_data`, `root_fs_names`, `root_delay`, and `ROOT_DEV`. Key functions include boot parsers for `ro`, `rw`, `root=`, `rootwait`, `rootwait=`, `rootflags=`, `rootfstype=`, and `rootdelay=`, plus `split_fs_names()`, `do_mount_root()`, `mount_root_generic()`, `mount_nfs_root()`, `mount_cifs_root()`, `mount_nodev_root()`, `mount_block_root()`, `mount_root()`, `wait_for_root()`, `parse_root_device()`, `prepare_namespace()`, `rootfs_init_fs_context()`, and `init_rootfs()`.

## Control Flow
`prepare_namespace()` applies root delay, waits for probe completion, runs RAID setup, parses `root=`, calls `initrd_load()`, optionally waits for root device discovery, mounts the selected root type, mounts devtmpfs, then pivots and unmounts old rootfs. Generic mounting tries requested or known block filesystems, retries read-only after writable failures, and panics with partition/filesystem diagnostics if no mount succeeds.

## State and Persistence Behavior
Boot parameter state lives in `__initdata` until init memory is freed. Successful mount updates `ROOT_DEV`, current working directory, root mount state, and rootfs backing choice. No durable storage is written except filesystem mount effects.

## Dependencies and Integration Points
It depends on init syscalls, VFS mount APIs, block device lookup, async/device probe completion, devtmpfs, RAID autodetect, NFS/CIFS root helpers, initrd loader, filesystem type registry, and rootfs ramfs/tmpfs implementations.

## Risks and Test Signals
Risks include invalid `root=` disabling `rootwait`, indefinite waits, root filesystem list handling with empty names, nodev root misclassification, panic diagnostics masking the original error, initrd interactions with `ROOT_DEV`, and pivot/unmount failures. Test signals include boots with block root, `rootfstype` lists, NFS/CIFS root retries, `rootwait` timeout, `rootdelay`, initrd present/absent, tmpfs rootfs selection, and missing-root panic output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/do_mounts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/do_mounts.h -->
# sources/distributed-fs/ceph-client/init/do_mounts.h

## Purpose
`do_mounts.h` shares declarations and small helpers among the early root-mount source files for root mounting, device-node creation, optional ramdisk/initrd loading, and delayed file-close flushing.

## Important APIs, Types, and Functions
It declares `mount_root_generic()`, `mount_root()`, and `root_mountflags`. `create_dev()` removes an existing path and creates a block device node using `init_mknod()`. Config stubs wrap `rd_load_image()` and `initrd_load()`. `init_flush_fput()` runs delayed fput and task work to avoid stale file references during mount retries.

## Control Flow
Root mount code calls `create_dev()` before mounting block roots or ramdisk roots. `do_mounts.c` calls `initrd_load()` unconditionally through a config-safe wrapper; `do_mounts_initrd.c` calls `rd_load_image()` through a similar wrapper when ramdisk support exists.

## State and Persistence Behavior
The helper mutates early rootfs namespace by unlinking and creating device nodes. The header itself stores no state beyond exposing `root_mountflags`.

## Dependencies and Integration Points
It depends on init syscall wrappers, block device encoding, root device constants, task work, delayed fput, and mount/initrd source files. It is the private contract among `do_mounts*.c`.

## Risks and Test Signals
Risks include creating wrong device-node modes, missing delayed fput flush before retrying filesystems, and config stubs causing silent no-op behavior. Test signals include builds with/without `BLK_DEV_RAM` and `BLK_DEV_INITRD`, device node creation failures, and root mount retry paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/do_mounts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/do_mounts_initrd.c -->
# sources/distributed-fs/ceph-client/init/do_mounts_initrd.c

## Purpose
`do_mounts_initrd.c` handles deprecated block initrd loading support: it records physical initrd locations from early parameters, honors `noinitrd`, creates `/dev/ram`, asks the ramdisk loader to populate it, warns about deprecation, and removes `/initrd.image`.

## Important APIs, Types, and Functions
Important globals are `initrd_start`, `initrd_end`, `initrd_below_start_ok`, `mount_initrd`, `phys_initrd_start`, and `phys_initrd_size`. Key functions are `no_initrd()`, `early_initrdmem()`, `early_initrd()`, and `initrd_load()`.

## Control Flow
Early parameters `initrdmem=` and `initrd=` parse a physical start and size. The `noinitrd` setup parameter disables mounting. During namespace preparation, `initrd_load()` creates `/dev/ram`, calls `rd_load_image()` to copy/decompress `/initrd.image` into ramdisk, emits a deprecation warning on use, and unlinks `/initrd.image`.

## State and Persistence Behavior
Physical initrd location and size are `__initdata`; ramdisk contents persist only in memory as `/dev/ram0`. Temporary namespace paths `/dev/ram` and `/initrd.image` are removed during the load path.

## Dependencies and Integration Points
It depends on `do_mounts.h`, initrd globals used by architecture boot setup, `memparse`, early parameter registration, and ramdisk image loading in `do_mounts_rd.c`.

## Risks and Test Signals
Risks include malformed `initrdmem`, deprecated `noinitrd` behavior, missing ramdisk support, failure to remove temporary initrd image, and reliance on deprecated block initrd instead of initramfs. Test signals include boots with `initrd=`, `initrdmem=`, `noinitrd`, compressed and filesystem initrd images, and absence of `BLK_DEV_RAM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/do_mounts_initrd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/do_mounts_rd.c -->
# sources/distributed-fs/ceph-client/init/do_mounts_rd.c

## Purpose
`do_mounts_rd.c` identifies and loads legacy initial ramdisk images into `/dev/ram`, supporting raw filesystem images and compressed images with configured decompressors.

## Important APIs, Types, and Functions
Important globals are `in_file`, `out_file`, `in_pos`, `out_pos`, `rd_image_start`, `exit_code`, and `decompress_error`. Key functions are `ramdisk_start_setup()`, `identify_ramdisk_image()`, `nr_blocks()`, `rd_load_image()`, `compr_fill()`, `compr_flush()`, `error()`, and `crd_load()`.

## Control Flow
`rd_load_image()` opens `/dev/ram` and `/initrd.image`, identifies the image by checking compression signatures and filesystem magic for romfs, cramfs, squashfs, minix, and ext2, then either invokes decompression callbacks or copies block-sized chunks into the ramdisk. It checks ramdisk capacity and unlinks `/dev/ram` at exit.

## State and Persistence Behavior
State is transient file pointers, offsets, decompressor error flags, and the in-memory ramdisk contents. `rd_image_start` from `ramdisk_start=` selects a starting block and is `__initdata`.

## Dependencies and Integration Points
It depends on kernel file I/O, filesystem magic headers, SquashFS private header, generic decompressor selection, ramdisk block device sizing, and `do_mounts_initrd.c`.

## Risks and Test Signals
Risks include magic detection false positives, unavailable decompressor panics, short reads/writes, oversized images, stale static error flags, and deprecated `ramdisk_start=` use. Test signals include each supported filesystem magic, each compression method enabled/disabled, too-large images, read/write error injection, and successful load followed by root mount from ramdisk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/do_mounts_rd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/init_task.c -->
# sources/distributed-fs/ceph-client/init/init_task.c

## Purpose
`init_task.c` defines the statically allocated initial task, signal/sighand/credential/group state, optional shadow call stack, and initial thread_info for the primordial kernel task.

## Important APIs, Types, and Functions
Important objects are `init_signals`, `init_sighand`, optional `init_shadow_call_stack`, `init_groups`, `init_cred`, exported `init_task`, and optional `init_thread_info`. The initializer covers scheduler entities, CPU masks, mm/files/fs/nsproxy, credentials, signal state, timers, audit/perf/RCU/cpuset/RT mutex/NUMA/KASAN/KCSAN/lockdep/tracing/livepatch/security/seccomp/SCHED_MM_CID fields depending on config.

## Control Flow
There are no runtime functions. The compiler and linker place fully initialized objects into the kernel image. Early boot starts from this task context; later fork/exec/scheduler code treats it as PID 0/kthreadd lineage root and a never-freed anchor for shared initial structures.

## State and Persistence Behavior
This file defines persistent kernel-lifetime state. Reference counts are initialized so the initial task, credentials, and groups are not freed. The task starts as `PF_KTHREAD`, uses `init_mm`, root credentials with full capabilities, default signal dispositions, and root namespace/filesystem structures.

## Dependencies and Integration Points
It depends on many subsystem initializer macros and config blocks: scheduler, credentials, namespace, files, signals, POSIX timers, cgroups, RCU, perf, audit, tracing, security, seccomp, and architecture thread initialization. `EXPORT_SYMBOL(init_task)` makes the object available to modules/core code.

## Risks and Test Signals
Risks include missing initializer fields after `task_struct` changes, config-conditional layout drift, incorrect reference counts, wrong root credentials/capabilities, lockdep/tracing initial state mistakes, and linker alignment requirements for `thread_info`. Test signals include compile-time designated-initializer coverage across config matrices, early boot smoke tests, lockdep/RCU/perf/audit enabled boots, and static checks for new `task_struct` fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/init_task.c -->
