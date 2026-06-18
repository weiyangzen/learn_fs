# Research: subset-b-005599

Grouped research for Xen PCI/SCSI backend and Xenbus support files. Each section title preserves the source path and is wrapped for source-tree-aligned reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/pci_stub.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/pci_stub.c

## Purpose
`pci_stub.c` is the host-side PCI capture and lifetime manager for Xen PCI passthrough. It registers the `pciback` PCI driver early, seizes devices listed by the `hide=` module parameter or driver-override binding, initializes Xen pciback config-space metadata, resets and disables the hardware, and later hands exclusive references to `xen-pciback/xenbus.c` for assignment to guest domains.

## Important APIs, Types, And Functions
The central objects are `struct pcistub_device`, which wraps a real `struct pci_dev` plus a kref and current `xen_pcibk_device *pdev`, and `struct pcistub_device_id`, which records BDFs to seize. Exported integration points are `pcistub_get_pci_dev_by_slot()` and `pcistub_put_pci_dev()`. Initialization flows through `pcistub_init()`, `pcistub_init_devices_late()`, `pcistub_probe()`, `pcistub_seize()`, and `pcistub_init_device()`. Cleanup and rebinding use `pcistub_remove()` and `pcistub_device_release()`. AER support is implemented by `xen_pcibk_error_detected()`, `xen_pcibk_mmio_enabled()`, `xen_pcibk_slot_reset()`, `xen_pcibk_error_resume()`, and shared `common_process()`.

## Control Flow
At boot/module load, `xen_pcibk_init()` requires the initial domain, initializes config-space handling, registers/seizes PCI devices, completes deferred device setup, then registers the Xenbus backend. Device seize allocates a `pcistub_device`, saves PCI config state, prepares MSI-X with Xen when available, resets the device, disables it, and marks it assigned. When xenbus requests a BDF, `pcistub_get_pci_dev_by_slot()` atomically marks the seized device in use by a backend instance. Release takes the device lock, resets hardware, restores the saved state, frees dynamic emulated config fields, clears interrupt-control flags, unregisters Xen domain ownership, and drops the kref. PCIe AER callbacks pause removal/reconfiguration with `pcistub_sem`, notify the frontend through the shared pciback page, and may mark the guest failed in Xenstore if no frontend AER handler responds.

## State And Persistence
Persistent runtime state lives in global lists: `pcistub_device_ids`, `pcistub_devices`, and early `seized_devices`. Per-device persistent state is stored in `xen_pcibk_dev_data`, including saved PCI state, permissive/config flags, fake INTx handler status, and IRQ accounting. Sysfs driver attributes (`new_slot`, `remove_slot`, `slots`, `quirks`, `permissive`, `allow_interrupt_control`, `irq_handlers`, `irq_handler_state`) mutate or expose this state. Xenstore is used only for AER failure notification here.

## Dependencies And Integration Points
The file depends on Linux PCI core, krefs, sysfs driver attributes, Xen event/channel and physdev hypercalls, Xen ACPI/PVH GSI helpers, pciback config-space helpers, and Xen domain ownership helpers. It integrates tightly with `pciback_ops.c` for resets and fake IRQ handling, `xenbus.c` for guest assignment, and `conf_space*.c` for virtual PCI config behavior.

## Risks
This code handles physical devices and guest-controlled state, so ordering is critical. Risks include stale saved PCI state, racing AER with device removal, shared IRQ mis-accounting, unsafe `permissive` config writes, device removal while a guest still has BAR access, and mismatched kref/list ownership around `pcistub_put_pci_dev()`. AER waits have a long timeout and depend on frontend cooperation.

## Test Signals
Useful signals are successful binding to `pciback`, sysfs `slots`/`irq_handlers` output, Xenstore backend device assignment, PCI FLR/reset logs, guest attach/detach cycles, MSI/MSI-X prepare/release warnings, AER recovery logs, and absence of leaked assigned devices after guest shutdown or driver unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/pci_stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/pciback.h -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/pciback.h

## Purpose
`pciback.h` is the private contract for the Xen PCI backend. It defines the shared backend device structure, per-PCI-device state, backend topology abstraction, and cross-file APIs used by pcistub, Xenbus setup, vpci/passthrough mapping, config-space emulation, interrupt/event handling, and AER.

## Important APIs, Types, And Functions
`struct xen_pcibk_device` binds a `xenbus_device` to backend-specific PCI mapping data, a device mutex, backend watch, event-channel IRQ, mapped `xen_pci_sharedinfo`, operation flags, work item, and current `xen_pci_op`. `struct xen_pcibk_dev_data` is attached to each physical `pci_dev` and tracks emulated config fields, saved PCI state, permissive/interrupt-control bits, fake INTx state, IRQ count, and IRQ name. `struct xen_pcibk_backend` abstracts BDF presentation with `init`, `free`, `find`, `publish`, `release`, `add`, and `get` callbacks. Inline wrappers dispatch to the selected backend.

## Control Flow
The header encodes the module split: pcistub owns captured hardware and exports `pcistub_get_pci_dev_by_slot()`/`pcistub_put_pci_dev()`, Xenbus calls `xen_pcibk_init_devices()`, `xen_pcibk_add_pci_dev()`, `xen_pcibk_publish_pci_roots()`, and `xen_pcibk_release_devices()`, while event handlers call `xen_pcibk_do_op()` and `xen_pcibk_handle_event()`. `xen_pcibk_lateeoi()` centralizes late EOI release for the shared event-channel IRQ.

## State And Persistence
State is all in-kernel and per backend instance or per captured PCI device. The flag bits (`PDEVF_op_active`, `PCIB_op_pending`, `EOI_pending`) coordinate request processing, AER acknowledgements, and late EOI. The externally declared `xen_pcibk_aer_wait_queue` and `xen_pcibk_quirks` couple AER waiters and config quirks across source files.

## Dependencies And Integration Points
It depends on Linux PCI, interrupt, list, mutex/spinlock/workqueue, Xen events, Xenbus, and `xen/interface/io/pciif.h`. It also declares the two topology backends, `xen_pcibk_vpci_backend` and `xen_pcibk_passthrough_backend`; this group includes the vpci backend and the Xenbus selector.

## Risks
Because most helpers silently return `-1` or `NULL` if `xen_pcibk_backend` is unset, initialization ordering matters. Flag bits are shared between interrupt and process context, so call sites must preserve barriers and late-EOI behavior. Any extension of `xen_pcibk_dev_data` must respect allocation of the flexible `irq_name[]`.

## Test Signals
Compile coverage under `CONFIG_XEN_PCIDEV_BACKEND`, successful backend selection logs, correct callback dispatch for vpci/passthrough modes, and interrupt/request processing without EOI warnings validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/pciback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/pciback_ops.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/pciback_ops.c

## Purpose
`pciback_ops.c` services guest PCI backend operations delivered over the pcifront shared page and event channel. It handles virtual config-space reads/writes, MSI/MSI-X enable/disable requests, device reset, fake legacy INTx IRQ management, AER wakeups, and late event-channel EOI.

## Important APIs, Types, And Functions
Public functions are `xen_pcibk_reset_device()`, `xen_pcibk_do_op()`, and `xen_pcibk_handle_event()`. MSI helpers include `xen_pcibk_enable_msi()`, `xen_pcibk_disable_msi()`, `xen_pcibk_enable_msix()`, and `xen_pcibk_disable_msix()` under `CONFIG_PCI_MSI`. `xen_pcibk_control_isr()` installs/removes a fake shared IRQ handler for INTx. `xen_pcibk_do_one_op()` is the core request dispatcher. `xen_pcibk_guest_interrupt()` acknowledges guest-owned INTx interrupts while pciback is mediating them.

## Control Flow
The event-channel IRQ enters `xen_pcibk_handle_event()`, records pending late EOI, and calls `xen_pcibk_test_and_schedule_op()`. If pcifront marked `_XEN_PCIF_active`, the backend sets `_PDEVF_op_active` and schedules `op_work` so config/PCI calls run in process context. `xen_pcibk_do_one_op()` copies the shared op, locates the mapped physical device via the selected backend, dispatches by command, writes result fields back, clears `_XEN_PCIF_active`, notifies the frontend, clears active state, and loops if more work arrived. AER uses `_XEN_PCIB_active`/`_PCIB_op_pending` to wake pcistub waiters when the frontend clears the AER flag.

## State And Persistence
State is held in `xen_pcibk_device.flags`, the shared `xen_pci_sharedinfo`, and each device's `xen_pcibk_dev_data`. MSI transitions disable fake INTx acknowledgment, while MSI disable restores it. `handled` counts fake IRQ observations and may stop ACKing if Xen reports the IRQ line is no longer shared.

## Dependencies And Integration Points
The file depends on Linux PCI/MSI APIs, Xen event-channel notification and PIRQ translation, pciback config-space functions, and the backend BDF mapper. It is called by `xenbus.c` for event setup and by `pci_stub.c` for device reset/release.

## Risks
Important risks are lost event-channel EOI, config-space calls in atomic context, guest-triggered MSI/MSI-X state races, invalid MSI-X vector counts, legacy IRQ handler leaks on abrupt guest death, and inconsistent barriers when sharing `op` fields with the frontend. The fake IRQ path is intentionally heuristic for shared IRQ lines.

## Test Signals
Exercise pcifront config reads/writes, MSI and MSI-X enable/disable, guest shutdown while MSI is active, repeated event-channel operations, AER acknowledgement, and absence of `IRQ while EOI pending` warnings or stale `_XEN_PCIF_active` flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/pciback_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/vpci.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/vpci.c

## Purpose
`vpci.c` implements the default Xen PCI backend topology mode: hide host PCI topology and present exported devices on a synthetic guest bus `0000:00:*.*`. It assigns captured devices to virtual slots, keeps related multifunction devices together, publishes a single root, and maps guest BDFs back to physical `pci_dev` objects.

## Important APIs, Types, And Functions
`struct vpci_dev_data` stores 32 virtual slot lists guarded by a mutex. The `xen_pcibk_vpci_backend` callback table provides `__xen_pcibk_init_devices()`, `__xen_pcibk_release_devices()`, `__xen_pcibk_add_pci_dev()`, `__xen_pcibk_release_pci_dev()`, `__xen_pcibk_get_pci_dev()`, `__xen_pcibk_publish_pci_roots()`, and `__xen_pcibk_get_pcifront_dev()`.

## Control Flow
When a backend instance is allocated, `init` creates empty per-slot lists. Adding a physical device rejects bridges, allocates a `pci_dev_entry`, and searches for an existing virtual slot with a matching physical domain/bus/slot so multifunction devices remain adjacent. SR-IOV virtual functions at function zero are deliberately not treated as multifunction anchors. If no compatible slot exists, the first empty virtual slot is used. The selected virtual BDF is published through the Xenbus callback. Removal finds the entry by physical device, deletes it, and calls `pcistub_put_pci_dev()` under optional `device_lock()`.

## State And Persistence
The only persistent state is the in-memory slot-to-device list in `pdev->pci_dev_data`. It is rebuilt per backend instance and freed on Xenbus device removal. Guest-visible BDFs are persisted to Xenstore by the caller via the publish callback.

## Dependencies And Integration Points
The file depends on Linux PCI helpers for slot/function extraction and on pciback's backend abstraction. `xenbus.c` calls `add`, `release`, `publish`, and `get`; `pci_stub.c` receives returned devices on release; AER uses `find` to translate a physical device back to a pcifront BDF.

## Risks
The fixed 32-slot root bus can exhaust when many devices are exported. Bridge rejection prevents hierarchical topology. Guest drivers that require host BDFs need passthrough mode rather than vpci. Slot grouping for multifunction devices must avoid misleading guests around SR-IOV VFs.

## Test Signals
Attach devices with single-function, multifunction, and SR-IOV layouts; verify Xenstore `vdev-*` paths show expected `0000:00:slot.func` mappings; hot-remove devices and confirm pcistub release; confirm AER reports the same virtual BDF visible to the frontend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/vpci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/xenbus.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/xenbus.c

## Purpose
`xenbus.c` is the Xenbus backend driver for `xen-backend:pci`. It creates `xen_pcibk_device` instances, reads toolstack-provided PCI BDFs, exports pcistub-owned devices to a frontend, publishes guest-visible roots/devices in Xenstore, maps the pcifront shared page, binds the event channel, and drives Xenbus state transitions.

## Important APIs, Types, And Functions
Key lifecycle functions are `alloc_pdev()`, `free_pdev()`, `xen_pcibk_xenbus_probe()`, and `xen_pcibk_xenbus_remove()`. Connection setup is split across `xen_pcibk_setup_backend()`, `xen_pcibk_attach()`, and `xen_pcibk_do_attach()`. Device publication/removal uses `xen_pcibk_export_device()`, `xen_pcibk_remove_device()`, `xen_pcibk_publish_pci_dev()`, and `xen_pcibk_publish_pci_root()`. Hotplug/reconfigure is handled by `xen_pcibk_reconfigure()` and `xen_pcibk_be_watch()`.

## Control Flow
Probe allocates the backend instance, initializes the selected topology backend, switches to `InitWait`, registers a watch on its backend node, and immediately invokes the watch. Backend setup reads `num_devs` and `dev-N`, gets each physical device from pcistub, adds it to the topology backend, marks `state-N` as `Initialised`, publishes PCI roots, and moves to `Initialised`. Once the frontend reaches `Initialised`, `xen_pcibk_attach()` reads `pci-op-ref`, `event-channel`, and `magic`, maps the shared page, binds a late-EOI interdomain IRQ to `xen_pcibk_handle_event()`, and switches to `Connected`. Reconfigure processes per-device substates for add/remove and moves to `Reconfigured`. Closing/closed states disconnect the ring/event channel and may unregister the device.

## State And Persistence
Per-instance state is in `xen_pcibk_device`: mapped shared info, event IRQ, backend watch, dev mutex, and topology mapping data. Xenstore stores `num_devs`, `dev-N`, `vdev-N`, `state-N`, `root-N`, `root_num`, frontend event-channel/grant reference, and driver state. The module parameter `passthrough` selects `vpci` or passthrough topology at registration.

## Dependencies And Integration Points
This file depends on Xenbus, Xen events, grant mapping, Xen PCI ownership helpers, pcistub ownership, `pciback_ops.c` event handling, and the topology backend callback table. It registers via `xenbus_register_backend()`.

## Risks
Risks include mismatched frontend `XEN_PCI_MAGIC`, partial Xenstore reconfiguration, device ownership stealing from another domain, leaking mapped rings on attach failure, hot-remove while operations are active, and state-machine divergence between backend and frontend. The code relies on `dev_lock` and workqueue flushing to serialize disconnect with request processing.

## Test Signals
Check Xenstore state progression `InitWait -> Initialised -> Connected`, successful guest pci enumeration, reconfigure add/remove transitions, clean close with unmapped ring and unbound IRQ, and logs for root/vdev publication and backend selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/xenbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-scsiback.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-scsiback.c

## Purpose
`xen-scsiback.c` is the Xen paravirtual SCSI backend. It exposes Linux target-core LUNs to Xen frontends through the `vscsi` Xenbus protocol, translates guest virtual SCSI IDs to target portal groups and LUNs, maps guest grant pages into scatterlists, submits SCSI CDBs or task-management requests to target core, and returns responses on the shared ring.

## Important APIs, Types, And Functions
Main structures are `vscsibk_info` for one Xenbus backend instance, `vscsibk_pend` for an in-flight request, `v2p_entry` for virtual-to-physical LUN translation, and target-core objects `scsiback_tport`, `scsiback_tpg`, and `scsiback_nexus`. Request flow uses `scsiback_irq_fn()`, `scsiback_do_cmd_fn()`, `prepare_pending_reqs()`, `scsiback_gnttab_data_map()`, `scsiback_cmd_exec()`, `scsiback_cmd_done()`, and `scsiback_send_response()`. Xenbus lifecycle uses `scsiback_probe()`, `scsiback_frontend_changed()`, `scsiback_map()`, `scsiback_disconnect()`, and `scsiback_remove()`. Target configfs integration is the `target_core_fabric_ops scsiback_ops` table.

## Control Flow
Probe allocates `vscsibk_info`, initializes locks/lists/page cache, advertises `feature-sg-grant`, and enters `InitWait`. When the frontend reaches `Initialised`, the backend reads `ring-ref` and `event-channel`, maps the ring, binds a late-EOI threaded IRQ, processes configured `vscsi-devs`, and switches to `Connected`. IRQ handling drains ring requests until none remain or a ring error occurs. Each CDB maps direct or grant-backed SG descriptors, validates offsets/lengths, obtains a target-core session tag, submits the command, and later completes through `queue_data_in` or `queue_status`. Abort/reset requests become target TMRs. Reconfiguring scans `vscsi-devs` for LUN add/remove and reports `Reconfigured`.

## State And Persistence
Runtime state is per backend instance: mapped ring, IRQ, unreplied request count, v2p translation list, and grant page cache. Translation entries kref target portal groups and increment frontend-use counters so active frontends block nexus deletion. Xenstore persists vSCSI device state under `vscsi-devs/<entry>/state`, physical target strings in `p-dev`, virtual IDs in `v-dev`, feature flags, and Xenbus state. Configfs persists operator-created target ports, portal groups, aliases, nexus, and LUN links through target core.

## Dependencies And Integration Points
The file depends on Xenbus, Xen event channels, grant tables, balloon/page cache helpers, the `vscsiif` ring ABI, Linux SCSI and target core, configfs, and Xen backend registration. It bridges Xen frontends to target-core fabric sessions.

## Risks
Risk areas are guest-provided ring bounds, grant list validation, SG segment overflow, leaked grant mappings on early errors, races between LUN hotplug and in-flight commands, removing a nexus with active frontend references, ring halting on bogus producer indexes, and potential interrupt masking after ring errors. The code relies on request counters before disconnect and krefs on translation entries to prevent premature frees.

## Test Signals
Validate configfs creation of ports/TPGs/nexus/LUNs, Xenstore `vscsi-devs` hotplug state changes, guest SCSI inquiry/read/write, SG grant and direct SG paths, abort and LUN reset requests, frontend shutdown with zero unreplied requests, and grant page cache shrink behavior under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-scsiback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/xen/xenbus/Makefile

## Purpose
This Makefile defines how the Xenbus support objects are built into the kernel. It groups common Xenbus client, communication, Xenstore, and probe code into the `xenbus` composite object, then conditionally adds backend, frontend, and misc-device support based on Xen configuration symbols.

## Important APIs, Types, And Functions
There are no C APIs in this file, but its object selections determine which APIs exist. `xenbus-y` always includes `xenbus_client.o`, `xenbus_comms.o`, `xenbus_xs.o`, and `xenbus_probe.o`. `xenbus-$(CONFIG_XEN_BACKEND)` adds `xenbus_probe_backend.o`. Separate built-in objects are `xenbus_dev_frontend.o`, optional `xenbus_dev_backend.o`, and optional `xenbus_probe_frontend.o`.

## Control Flow
Build control is straightforward: `obj-y += xenbus.o` includes the common composite whenever this directory is part of the Xen build, while frontend/backend probing and backend device nodes are compiled only when their Kconfig symbols are enabled. This affects initcall availability at runtime.

## State And Persistence
The Makefile persists no runtime state, but it is the source of build-time state for feature inclusion. Enabling or disabling `CONFIG_XEN_BACKEND` changes whether backend bus probing and `/dev/xen/xenbus_backend` exist.

## Dependencies And Integration Points
It integrates with Kbuild and the Xen driver directory. Runtime dependencies among the C files assume the common `xenbus.o` exports helper functions needed by frontend and backend modules.

## Risks
The main risk is configuration skew: compiling a backend driver without backend Xenbus probe support would prevent devices from binding. The unconditional frontend misc device may exist on Xen domains even when frontend bus probing is configured separately.

## Test Signals
Build matrix checks for `CONFIG_XEN_BACKEND` and `CONFIG_XEN_XENBUS_FRONTEND`, link symbol availability, and boot logs showing the expected frontend/backend bus registration validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus.h -->
# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus.h

## Purpose
`xenbus.h` is the private header for Xenbus internals. It defines the bus-type abstraction for frontend/backend enumeration, Xenstore initialization modes, watch event containers, low-level request state, and declarations shared by Xenbus communications, probe, client, and user-device files.

## Important APIs, Types, And Functions
`struct xen_bus_type` wraps a Linux `bus_type` with Xenstore root, path depth, bus-id generation, probing, and otherend watch handlers. `enum xenstore_init` distinguishes unknown, PV, HVM, and local Xenstore modes. `struct xs_watch_event` carries Xenstore watch callbacks. `enum xb_req_state` and `struct xb_req_data` model queued, wait-reply, got-reply, and aborted Xenstore requests. The header declares shared lists/locks (`xs_reply_list`, `xb_write_list`, `xb_waitq`, `xb_write_mutex`, `xs_response_mutex`) and cross-file functions for communication, probing, suspend/resume, and user replies.

## Control Flow
The header ties the message pump to higher layers: `xenbus_dev_request_and_reply()` queues requests, `xenbus_comms.c` consumes `xb_write_list` and fills replies, `xenbus_dev_queue_reply()` returns replies to `/dev/xen/xenbus`, and probe files call common helpers like `xenbus_probe_devices()` and `xenbus_dev_changed()`.

## State And Persistence
All state declared here is runtime kernel state. `xb_dev_generation_id` invalidates user-space transaction handles across Xenstore reconnect/resume. Shared request and watch structures persist only while open files, watches, or queued Xenstore messages exist.

## Dependencies And Integration Points
The header depends on Linux mutex/uio and public `<xen/xenbus.h>`. It is included by the common communications, client, probe, frontend/backend probe, and misc-device implementations.

## Risks
Because this header exposes shared internal lists and locks, call ordering and lock nesting must remain consistent. Request-state transitions need barriers in implementation files so callbacks do not see partial replies. Path depth in `xen_bus_type.levels` must match frontend/backend Xenstore layouts.

## Test Signals
Build coverage, clean sparse/lockdep behavior, working frontend/backend enumeration, successful user-space Xenstore reads/writes, and stable resume transaction invalidation indicate this contract is sound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_client.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_client.c

## Purpose
`xenbus_client.c` provides exported helper APIs used by Xen frontend and backend drivers: Xenbus state switching and error reporting, watch registration, ring allocation and grant mapping/unmapping, event-channel allocation/free, and state reads. It abstracts PV versus HVM ring mapping details behind `xenbus_ring_ops`.

## Important APIs, Types, And Functions
Exports include `xenbus_strstate()`, `xenbus_watch_path()`, `xenbus_watch_pathfmt()`, `xenbus_switch_state()`, `xenbus_frontend_closed()`, `xenbus_dev_error()`, `xenbus_dev_fatal()`, `xenbus_setup_ring()`, `xenbus_teardown_ring()`, `xenbus_alloc_evtchn()`, `xenbus_free_evtchn()`, `xenbus_map_ring_valloc()`, `xenbus_unmap_ring_vfree()`, and `xenbus_read_driver_state()`. Internal types include `xenbus_map_node`, `map_ring_valloc`, and `xenbus_ring_ops`.

## Control Flow
State switching uses a Xenstore transaction: read current state, avoid duplicate writes, detect vanished nodes, write the new state, retry on `-EAGAIN`, and update cached `dev->state`. Ring setup allocates pages and grant references for outbound rings. Ring mapping allocates virtual address space, maps peer grants with `gnttab_batch_map()`, tracks handles in a global list, and chooses PV PTE-backed mapping or HVM unpopulated-page/vmap mapping. Unmap looks up the virtual address in that list and releases grant handles plus VM/page resources.

## State And Persistence
Xenbus state is persisted in Xenstore under each device node. Error messages are persisted under `error/<nodename>/error`. Ring mappings are in-memory list entries protected by `xenbus_valloc_lock`. Grant references persist until explicitly ended or unmapped.

## Dependencies And Integration Points
The file depends on Linux memory/vmalloc APIs, Xen grant tables, balloon/unpopulated page helpers, Xen event-channel hypercalls, Xen feature/domain mode helpers, and public Xenbus APIs. Every Xen PV driver in the kernel consumes these helpers.

## Risks
Failure paths can leak mapped pages when grant unmap fails, which the code logs explicitly. State switching intentionally returns 0 even after fatal error reporting, so callers must understand the shutdown side effect. Grant count bounds, 32-bit HVM address truncation, and PV/HVM mapping differences are key risk areas.

## Test Signals
Probe drivers that create rings, map peer rings, switch through Xenbus states, suspend/resume, and tear down cleanly. Look for absent grant leaks, correct Xenstore error nodes on failures, and successful operation in both PV and HVM domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_comms.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_comms.c

## Purpose
`xenbus_comms.c` is the low-level Xenstore transport. It moves `xsd_sockmsg` requests and responses through the shared Xenstore ring, wakes on the Xenstore event channel, runs the `xenbus` kernel thread, dispatches replies to waiting request objects, and forwards watch events to the Xenbus watch layer.

## Important APIs, Types, And Functions
Shared objects are `xs_reply_list`, `xb_write_list`, `xb_waitq`, `xb_write_mutex`, and `xs_response_mutex`. Public functions are `xb_init_comms()` and `xb_deinit_comms()`. Core internal routines are `xb_write()`, `xb_read()`, `process_msg()`, `process_writes()`, `xenbus_thread()`, and IRQ callback `wake_waiting()`.

## Control Flow
`xb_init_comms()` verifies ring quiescence, binds the Xenstore event channel to `wake_waiting()`, and starts the `xenbus` kthread. The thread waits for readable response data or queued writes. `process_msg()` incrementally reads a header and body, protects partial messages across save/restore with `xs_response_mutex`, routes `XS_WATCH_EVENT` bodies to `xs_watch_msg()`, or matches replies by request id from `xs_reply_list` and invokes the request callback. `process_writes()` incrementally writes the request header and iovecs from `xb_write_list`, then moves the request to `xs_reply_list`.

## State And Persistence
Ring producer/consumer indexes in `xen_store_interface` are the persistent shared transport state. Static local state in `process_msg()` and `process_writes()` tracks partially read/written messages. Request state transitions use `xb_req_state_*` and krefs.

## Dependencies And Integration Points
The file depends on Xenstore shared memory from `xenbus_probe.c`, Xen event-channel notification, kthreads, waitqueues, and request/watch helpers from `xenbus_xs.c` and `xenbus_dev_frontend.c`.

## Risks
Risks include corrupt ring indexes, partial messages across suspend/resume, request abort races, allocating large watch events under memory pressure, and deadlocks if response mutex usage changes. The code resets bad ring indexes and rate-limits read/write warnings.

## Test Signals
Exercise Xenstore reads/writes/transactions/watches, suspend/resume, kdump-like non-quiescent rings, user `/dev/xen/xenbus` traffic, and watch floods. Healthy behavior shows matched replies, no stuck `xb_write_list`, and no repeated ring index warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_comms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_dev_backend.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_dev_backend.c

## Purpose
`xenbus_dev_backend.c` exposes a privileged misc device, `/dev/xen/xenbus_backend`, used in the initial domain to set up or inspect the Xenstore shared page and event channel for a user-space xenstored process.

## Important APIs, Types, And Functions
The file defines file operations `xenbus_backend_open()`, `xenbus_backend_ioctl()`, and `xenbus_backend_mmap()`. `xenbus_alloc()` grants the reserved Xenstore page to a xenstored domain and allocates an unbound event channel. IOCTLs are `IOCTL_XENBUS_BACKEND_EVTCHN` and `IOCTL_XENBUS_BACKEND_SETUP`.

## Control Flow
Open and ioctl require `CAP_SYS_ADMIN`. `IOCTL_XENBUS_BACKEND_EVTCHN` returns the current Xenstore event channel if present. `IOCTL_XENBUS_BACKEND_SETUP` calls `xenbus_alloc(domid)`, suspending Xenstore communication, rejecting setup if Xenstore is already running, granting `GNTTAB_RESERVED_XENSTORE`, allocating an event channel from self to the requested domain, deinitializing old comms if needed, storing the new port, and resuming Xenstore. `mmap` maps the single Xenstore interface page to user space.

## State And Persistence
The device mutates global Xenstore transport state: `xen_store_evtchn`, `xen_store_interface`, and Xenstore suspended/resumed status. It also creates a grant-table permission for the reserved Xenstore page.

## Dependencies And Integration Points
It depends on miscdevice, Linux capabilities, Xen grant table, event-channel hypercalls, Xenbus suspend/resume helpers, and the global Xenstore interface created by `xenbus_probe.c`. It registers only in the initial domain.

## Risks
This is privileged control-plane code. Setup after Xenstore has started is rejected because watches would otherwise need a staged resume. Incorrect mmap size/page offset is rejected. Risks include event-channel replacement races and exposing the Xenstore page to the wrong domain if user space passes an incorrect domid.

## Test Signals
In dom0, verify device registration, `CAP_SYS_ADMIN` enforcement, ioctl return values before/after setup, one-page mmap behavior, and that xenstored can communicate after setup without lost watches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_dev_backend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_dev_frontend.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_dev_frontend.c

## Purpose
`xenbus_dev_frontend.c` implements `/dev/xen/xenbus`, a user-space access path to the kernel Xenstore connection. It accepts raw Xenstore messages, buffers partial writes, supports transactions and watches per open file, queues replies/watch events for reads, and cleans up outstanding operations safely on close.

## Important APIs, Types, And Functions
Important types are `xenbus_file_priv`, `xenbus_transaction_holder`, `read_buffer`, and `watch_adapter`. File operations are `xenbus_file_read()`, `xenbus_file_write()`, `xenbus_file_open()`, `xenbus_file_release()`, and `xenbus_file_poll()`, exported as `xen_xenbus_fops`. Reply plumbing includes `queue_reply()`, `watch_fired()`, `xenbus_dev_queue_reply()`, `xenbus_write_transaction()`, `xenbus_write_watch()`, and async cleanup `xenbus_worker()`.

## Control Flow
Open initializes per-file lists, locks, waitqueue, kref, and cleanup work. Writes accumulate bytes until a full `xsd_sockmsg` plus body is present. Watch/unwatch messages are handled locally by registering or removing `xenbus_watch` adapters and synthesizing `OK` replies. Other messages are queued to the Xenstore transport; transaction start/end additionally update the per-file transaction list. `xenbus_dev_queue_reply()` is called on transport completion and enqueues header/body buffers for read. Reads drain queued `read_buffer` nodes, blocking unless `O_NONBLOCK`.

## State And Persistence
Per-open state includes active transactions, active watches, partial write buffer, queued read buffers, and kref lifetime. `xb_dev_generation_id` invalidates transaction handles across Xenstore reconnects; committing an old generation returns `EAGAIN`, while aborting returns `OK`.

## Dependencies And Integration Points
The file depends on miscdevice, user copy helpers, waitqueues, workqueues, Xenbus watch registration, and the low-level request path in `xenbus_comms.c`/`xenbus_xs.c`. It registers in Xen domains when a Xenstore event channel exists.

## Risks
Risks include malformed user messages, multiple writers interleaving partial messages, reply allocation failures in watch callbacks, transaction leaks on process close, and deadlock if cleanup ran directly in the Xenbus thread. The code uses mutex separation and workqueue cleanup to reduce those risks.

## Test Signals
Use xenstore user tools through `/dev/xen/xenbus`, test partial writes, nonblocking reads, watch/unwatch events, transaction start/end, close with active watches/transactions, and suspend/resume transaction generation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_dev_frontend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_probe.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_probe.c

## Purpose
`xenbus_probe.c` is the common Xenbus probe and Xenstore initialization layer. It initializes access to the Xenstore shared interface for PV, HVM, and local xenstored modes, exposes global Xenstore state, registers readiness notifiers, provides common Linux device probe/remove helpers, handles otherend watches, and creates/destroys `xenbus_device` instances from Xenstore paths.

## Important APIs, Types, And Functions
Exports include `xen_store_evtchn`, `xen_store_interface`, `xen_store_domain_type`, `xenbus_match()`, `xenbus_read_otherend_details()`, `xenbus_otherend_changed()`, `xenbus_dev_probe()`, `xenbus_dev_remove()`, `xenbus_register_driver_common()`, `xenbus_unregister_driver()`, `xenbus_probe_node()`, `xenbus_probe_devices()`, `xenbus_dev_changed()`, suspend/resume helpers, and Xenstore notifier registration. Init functions include `xenbus_init()` and `xenbus_probe_initcall()`.

## Control Flow
Early init determines Xenstore mode: PV start-info event channel/page, HVM hvm_params, or local dom0 allocation. It initializes ring ops, maps the interface, binds late-init IRQs if HVM Xenstore is not ready, calls `xs_init()` when safe, and registers resume notifiers. When Xenstore becomes ready, `xenbus_probe()` marks readiness, maps late HVM interface if needed, frees temporary IRQs, initializes XS for deferred HVM, and notifies frontend/backend probe modules. Device probing allocates `xenbus_device`, derives bus id, registers with the Linux device model, calls the matched Xenbus driver's probe under reclaim semaphore, and installs otherend state watches.

## State And Persistence
Global state includes Xenstore event channel, interface pointer, store GFN, store domain type, readiness flag, and notifier chain. Each `xenbus_device` stores nodename, devicetype, otherend path/id, state, vanished flag, completion, reclaim semaphore, and sysfs attributes/stat counters.

## Dependencies And Integration Points
It depends on Xen HVM/PV platform data, event channels, memory remapping, Xenstore XS helpers, Linux bus/device model, notifiers, PM callbacks, and frontend/backend probe files.

## Risks
Risks include HVM Xenstore not yet ready, invalid store PFN values, backend crash causing frontend state reset, vanished Xenstore nodes, shutdown-time watch events, and stale otherend details after resume. The code handles these with deferred probe threads, vanished flags, re-reading otherend details, and state checks.

## Test Signals
Boot PV, HVM, and dom0/local Xenstore cases; verify frontend/backend buses populate after Xenstore readiness, sysfs device attributes exist, suspend/resume restores watches, backend restart triggers reconnect, and Xenstore notifier callbacks fire exactly once when ready.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_probe_backend.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_probe_backend.c

## Purpose
`xenbus_probe_backend.c` implements the Xen backend bus (`xen-backend`). It enumerates backend Xenstore nodes, generates backend device IDs, emits backend uevents, registers backend drivers, watches the `backend` tree, and offers a memory-pressure reclaim hook for backend drivers.

## Important APIs, Types, And Functions
Key routines are `backend_bus_id()`, `xenbus_uevent_backend()`, `xenbus_probe_backend()`, `xenbus_probe_backend_unit()`, `backend_changed()`, `read_frontend_details()`, `xenbus_dev_is_online()`, `__xenbus_register_backend()`, `backend_probe_and_watch()`, and `backend_shrink_memory_count()`. The static `xenbus_backend` `xen_bus_type` defines root `backend`, depth 3, Linux bus name `xen-backend`, and common probe/remove handlers.

## Control Flow
On subsystem init the backend bus is registered, a Xenstore readiness notifier is installed, and a shrinker is registered. Once Xenstore is ready, `backend_probe_and_watch()` enumerates all backend devices and registers a watch on `backend`. Directory traversal follows `backend/<type>/<frontend>/<id>`, then calls common `xenbus_probe_node()`. Driver registration sets `read_otherend_details` to read `frontend-id` and `frontend`, then uses `xenbus_register_driver_common()`.

## State And Persistence
Backend device state is represented by Linux device objects and Xenstore nodes. `xenbus_dev_is_online()` reads the backend node `online` flag, which influences removal behavior in backend drivers. The shrinker holds no object count; it only triggers backend driver `reclaim_memory()` callbacks opportunistically.

## Dependencies And Integration Points
It depends on common Xenbus probe/client helpers, Linux bus and shrinker APIs, Xenstore directory reads, and backend drivers such as pciback and scsiback.

## Risks
Backend bus IDs depend on valid `frontend-id` and existing frontend path; malformed Xenstore nodes fail enumeration. The watch filter permits only one pending frontend state event per watch, which avoids queue buildup but can coalesce transitions. Shrinker callbacks must avoid blocking if a device is already in probe/remove due to `down_trylock()`.

## Test Signals
Create backend nodes for multiple device types/frontends, verify `MODALIAS=xen-backend:<type>` uevents, driver binding through `xenbus_register_backend()`, online-flag removal behavior, and reclaim callbacks under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_probe_backend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_probe_frontend.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_probe_frontend.c

## Purpose
`xenbus_probe_frontend.c` implements the Xen frontend bus (`xen`). It enumerates frontend device nodes under `device`, registers frontend drivers, watches backend state changes, handles frontend shutdown and PM restore, waits for boot-critical PV devices, and resets stale frontend/backend state after kexec/kdump-style transitions.

## Important APIs, Types, And Functions
Key functions include `frontend_bus_id()`, `xenbus_probe_frontend()`, `xenbus_uevent_frontend()`, `xenbus_frontend_dev_probe()`, `xenbus_frontend_dev_shutdown()`, `read_backend_details()`, `wait_for_devices()`, `__xenbus_register_frontend()`, `xenbus_reset_state()`, and `frontend_probe_and_watch()`. The static `xenbus_frontend` bus uses root `device`, depth 2, Linux bus name `xen`, common probe/remove handlers, shutdown, and PM ops.

## Control Flow
Subsystem init registers the frontend bus and a Xenstore readiness notifier. Once ready, it optionally resets HVM frontend state, enumerates `device/<type>/<id>`, and watches `device`. Probe ignores legacy `console/0`, creates bus IDs as `<type>-<id>`, reads backend details, probes the matched driver, and watches the backend state. Shutdown moves connected devices to `Closing` and waits briefly for `xenbus_frontend_closed()`. Late init waits for nonessential devices up to 30 seconds and essential devices up to a total 270 seconds before warning.

## State And Persistence
Frontend state is stored both in `xenbus_device.state` and Xenstore node `state`. `ready_to_wait_for_devices` gates boot waiting. `backend_state` plus `backend_state_wq` coordinate reset-state waits. Device readiness can also depend on a driver's optional `is_ready()` callback.

## Dependencies And Integration Points
It depends on common Xenbus probe helpers, Xenstore directory/watch APIs, Linux bus/PM/shutdown model, platform PCI callback readiness for HVM, and frontend drivers registered through `xenbus_register_frontend()`.

## Risks
Boot can stall on devices that never connect, though bounded by timeouts. Resetting frontend state must coordinate with backend transitions to avoid stale `Connected` or `Closed` nodes. Local Xenstore restore is deferred via workqueue because backend state is temporarily inaccessible. Shutdown ignores non-connected devices.

## Test Signals
Boot with PV block/net/input frontends, module-load a frontend driver and observe wait behavior, simulate backend state changes, test kexec/kdump reconnect paths, suspend/resume with local Xenstore, and verify `MODALIAS=xen:<type>` uevents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_probe_frontend.c -->
