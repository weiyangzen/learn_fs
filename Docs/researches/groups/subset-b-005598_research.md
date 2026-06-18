# subset-b-005598 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/privcmd.c -->
# sources/distributed-fs/ceph-client/drivers/xen/privcmd.c

## Purpose
`privcmd.c` implements the Xen privileged command misc device, `/dev/xen/privcmd`, plus optional eventfd helpers for device-model interrupt and MMIO notification. It is the user/kernel boundary used by toolstacks and device models to issue hypercalls, map foreign guest frames or Xen resources into userspace, execute `dm_op` calls, translate PCI SBDFs to GSIs, and set up irqfd/ioeventfd style integrations.

## Important APIs, types, and functions
The exported API is `xen_privcmd_fops`, consumed by Xen filesystem/device registration. Major ioctl handlers are `privcmd_ioctl_hypercall`, `privcmd_ioctl_mmap`, `privcmd_ioctl_mmap_batch`, `privcmd_ioctl_dm_op`, `privcmd_ioctl_restrict`, `privcmd_ioctl_mmap_resource`, `privcmd_ioctl_pcidev_get_gsi`, `privcmd_ioctl_irqfd`, and `privcmd_ioctl_ioeventfd`. `struct privcmd_data` carries per-open domain restriction state. Internal helpers include paged user-array gathering/traversal, `alloc_empty_pages`, user-page pinning for dm-op buffers, VMA range checking, and VM operations for foreign mappings. Under `CONFIG_XEN_PRIVCMD_EVENTFD`, `struct privcmd_kernel_irqfd`, `struct privcmd_kernel_ioreq`, `struct ioreq_port`, and `struct privcmd_kernel_ioeventfd` track eventfd mappings and ioreq pages.

## Control flow
Module initialization refuses non-Xen guests, optionally installs a xenstore-driven target-domain restriction for non-initial domains, registers `xen/privcmd` and `xen/hypercall-buf`, and initializes irqfd support. Open waits for restriction discovery, then stores the allowed domid in `file->private_data`. Ioctls copy user control structures, enforce the per-open domid restriction when present, perform hypercalls or mapping operations, and copy per-frame errors back where required. `mmap` marks VMAs as IO/PFNMAP/noncopyable and later mapping ioctls populate them with foreign GFNs/MFNs or acquired resources. Eventfd paths install wait queue callbacks or event-channel handlers, translate eventfd signals into Xen dm-ops, and translate guest ioreq writes into eventfd notifications.

## State and persistence
State is runtime-only. Per-open `privcmd_data` is freed on release. Foreign mappings store either `PRIV_VMA_LOCKED` or an allocated `struct page **` in `vma->vm_private_data`; auto-translated guests free unpopulated pages in `privcmd_close`. Global restriction state is `target_domain`, `restrict_wait`, and a xenstore notifier. Optional irqfd state is a global SRCU-protected list plus cleanup workqueue; optional ioeventfd state is a mutex-protected list of per-guest ioreq structures. No durable storage is written.

## Dependencies and integration points
This file depends on Xen hypercall, memory, HVM dm-op/ioreq, balloon/unpopulated page allocation, xenbus, event channels, eventfd, Linux MM/VMA APIs, user-copy and page-pinning APIs, lockdown security, ACPI GSI helpers, and the sibling `privcmd.h` declarations for misc registration. It integrates with Xen toolstacks, QEMU-like device models, XenFS/misc devices, and guest resource mapping workflows.

## Risks and test signals
High-risk areas are untrusted user pointers, VMA size/address validation, per-frame error reporting, page pin/unpin accounting, foreign mapping teardown, auto-translated vs PV behavior, eventfd lifetime races, ioreq page assumptions, and the security boundary around unrestricted hypercalls. Test signals should include ioctl ABI tests for all command versions, malformed and partial user arrays, retrying `-ENOENT` mmap batches, non-initial-domain restriction enforcement, lockdown behavior, dm-op buffer limit checks, eventfd assign/deassign races, ioreq event delivery, and module unload with live mappings or eventfds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/privcmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/privcmd.h -->
# sources/distributed-fs/ceph-client/drivers/xen/privcmd.h

## Purpose
`privcmd.h` is the small local header shared by the Xen privcmd implementation and companion buffer device. It publishes file operations and the hypercall-buffer miscdevice for registration from the Xen driver code.

## Important APIs, types, and functions
It declares `xen_privcmd_fops`, `xen_privcmdbuf_fops`, and `xen_privcmdbuf_dev`. There are no local types or inline helpers.

## Control flow
The header has no runtime control flow. It allows `privcmd.c` to register both the privcmd and hypercall-buffer devices, while the buffer implementation supplies the second file-operations table and miscdevice object.

## State and persistence
No state is stored in the header. The declared objects refer to runtime file-operation tables and a miscdevice defined elsewhere.

## Dependencies and integration points
It includes `<linux/fs.h>` for `struct file_operations` and references `struct miscdevice`, relying on users including the normal miscdevice definitions where needed. It is a local integration point between `privcmd.c` and `privcmd-buf.c`.

## Risks and test signals
Risks are build-time only: declaration drift from the defining source files or missing includes in users. Test signals are Xen driver builds with `CONFIG_XEN_PRIVCMD` and symbol/export checks for both device registrations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/privcmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/pvcalls-back.c -->
# sources/distributed-fs/ceph-client/drivers/xen/pvcalls-back.c

## Purpose
`pvcalls-back.c` implements the Xen PV Calls backend. It exposes host networking services to a frontend over Xenbus, command rings, event channels, and grant-mapped data rings, translating frontend socket requests into kernel `AF_INET/SOCK_STREAM` sockets.

## Important APIs, types, and functions
Important structures are `struct pvcalls_fedata` for each frontend, `struct sock_mapping` for active connected sockets, `struct sockpass_mapping` for passive listening sockets, and `struct pvcalls_ioworker` for ordered I/O processing. Core functions include `backend_connect`, `backend_disconnect`, `pvcalls_back_work`, `pvcalls_back_handle_cmd`, socket command handlers for socket/connect/release/bind/listen/accept/poll, `pvcalls_new_active_socket`, data movers `pvcalls_conn_back_read` and `pvcalls_conn_back_write`, and xenbus callbacks `pvcalls_back_probe`/`pvcalls_back_changed`.

## Control flow
Probe publishes supported version, maximum ring order, and function-call mode to xenstore, then waits for a frontend. When the frontend connects, the backend reads the frontend event channel and ring grant reference, maps the command ring, binds an IRQ, and moves to `Connected`. Command-ring interrupts copy requests and dispatch them. Connect and accept create host sockets and active grant rings; bind/listen create passive mappings in a radix tree. Per-connection event-channel interrupts and socket callbacks queue ordered work that drains outbound data into `inet_sendmsg` or reads host socket data with `inet_recvmsg`, then updates shared-ring indexes and notifies the frontend. Disconnect releases all active and passive mappings.

## State and persistence
All state is in kernel memory: a global frontend list protected by a semaphore, per-frontend command ring and socket maps, per-active grant mappings, event-channel IRQs, workqueues, atomics for read/write/io/release/eoi scheduling, and saved socket callbacks. State is removed when the Xenbus device disconnects or the module exits; nothing persists across reload or reboot.

## Dependencies and integration points
The backend depends on Xenbus, grant-table mapping, Xen event channels with late EOI, ring macros from `xen/interface/io/pvcalls.h`, Linux socket internals, radix trees, workqueues, semaphores, and inet socket operations. It integrates with the PV Calls frontend protocol and the host network stack.

## Risks and test signals
Risks include shared-ring memory ordering, only-one-inflight accept/poll limitations, callback restoration races, grant mapping cleanup, frontend-provided ring order validation, event-channel EOI handling, socket lifetime under disconnect, and partial send/receive behavior. Test signals include frontend/backend loopback socket tests, nonblocking accept and poll, backend disconnect during active I/O, grant-map failure injection, malformed command IDs/lengths, full ring behavior, and host socket errors reflected in `in_error`/`out_error`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/pvcalls-back.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/pvcalls-front.c -->
# sources/distributed-fs/ceph-client/drivers/xen/pvcalls-front.c

## Purpose
`pvcalls-front.c` implements the Xen PV Calls frontend socket shim. It exports socket-operation helpers that replace selected IPv4 stream socket operations with protocol requests sent to a backend over Xenbus command rings and per-connection grant-backed data rings.

## Important APIs, types, and functions
Public exports are `pvcalls_front_socket`, `pvcalls_front_connect`, `pvcalls_front_bind`, `pvcalls_front_listen`, `pvcalls_front_accept`, `pvcalls_front_sendmsg`, `pvcalls_front_recvmsg`, `pvcalls_front_poll`, and `pvcalls_front_release`. `struct pvcalls_bedata` stores the command ring, grant ref, IRQ, socket list, and response slots. `struct sock_mapping` stores active or passive socket state, including grant refs, data-ring pointers, wait queues, status and inflight flags. Important internals include `pvcalls_front_event_handler`, `alloc_active_ring`, `create_active`, `__write_ring`, `__read_ring`, passive/active poll helpers, and xenbus probe/remove/change callbacks.

## Control flow
Probe validates backend protocol version and capabilities, allocates a shared command ring, grants it to the backend, binds an event channel, writes xenstore keys, and enters `Initialised`. Socket creation allocates a mapping and sends `PVCALLS_SOCKET`. Connect and accept allocate active data rings, grant pages to the backend, send ring references and event channels, then wait for command responses. Send/receive operate directly on the active ring with memory barriers and IRQ notification. Bind/listen/accept/poll operate on passive socket command requests and wait queues. Release sends `PVCALLS_RELEASE`, waits for backend acknowledgement, then tears down mappings after refcounted in-flight operations drain. Remove disconnects the frontend, wakes blocked users, and frees all mappings.

## State and persistence
State is runtime-only and tied to a single supported front/back connection. `pvcalls_front_dev` and `pvcalls_refcount` gate global device lifetime. Each socket stores its `sock_mapping` in `sock->sk->sk_send_head`. Active mappings own grant references, event-channel IRQs, data-ring pages, and mutexes for read/write serialization. Passive mappings track bind/listen state and single inflight accept/poll operations. No persistent storage is written.

## Dependencies and integration points
The frontend depends on Xenbus, grant tables, event channels, Xen flex-ring macros, Linux socket APIs, wait queues, atomics, and the local `pvcalls-front.h` declarations. It integrates with higher-level networking code by exporting socket operation helpers and with the backend through xenstore keys `version`, `ring-ref`, and `port`.

## Risks and test signals
Risks include using `sk_send_head` as private storage, single backend limitation, ring index validation, blocking waits without backend progress, shared-memory ordering, refcount drain loops, nonblocking accept state, grant leak on partial setup, and disconnect while send/receive waits. Test signals include IPv4 stream connect/send/recv, passive bind/listen/accept, `MSG_DONTWAIT`, `poll`, backend removal while operations are active, malformed backend responses, full data rings, unsupported socket flags, and repeated release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/pvcalls-front.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/pvcalls-front.h -->
# sources/distributed-fs/ceph-client/drivers/xen/pvcalls-front.h

## Purpose
`pvcalls-front.h` declares the socket-operation entry points exported by the PV Calls frontend.

## Important APIs, types, and functions
It declares helpers for socket creation, connect, bind, listen, accept, sendmsg, recvmsg, poll, and release. The signatures use `struct socket`, `struct sockaddr`, `struct msghdr`, `struct proto_accept_arg`, `struct file`, and `poll_table`, matching Linux socket operation hooks.

## Control flow
The header has no runtime control flow. Consumers call these functions from socket operation tables when PV Calls is selected for a socket.

## State and persistence
No state is stored here. The implementation in `pvcalls-front.c` owns all per-device and per-socket state.

## Dependencies and integration points
It includes `<linux/net.h>` and is the local contract between PV Calls frontend implementation and code that wires the frontend into networking/socket operations.

## Risks and test signals
Risks are ABI drift between declarations and implementation or kernel socket API signature changes. Test signals are compile coverage and exercising every declared operation through PV Calls sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/pvcalls-front.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/swiotlb-xen.c -->
# sources/distributed-fs/ceph-client/drivers/xen/swiotlb-xen.c

## Purpose
`swiotlb-xen.c` provides Xen-specific DMA mapping operations. It translates Linux physical addresses to Xen bus-frame based DMA addresses and uses SWIOTLB bounce buffers when devices cannot DMA to the translated or contiguous address range safely.

## Important APIs, types, and functions
The exported object is `xen_swiotlb_dma_ops`. Key helpers are `xen_phys_to_bus`, `xen_phys_to_dma`, `xen_dma_to_phys`, `range_straddles_page_boundary`, `range_requires_alignment`, `xen_swiotlb_find_pool`, `xen_swiotlb_map_phys`, `xen_swiotlb_unmap_phys`, sync helpers for single and scatter-gather mappings, and `xen_swiotlb_dma_supported`. On x86 it also implements `xen_swiotlb_fixup`, `xen_swiotlb_alloc_coherent`, and `xen_swiotlb_free_coherent`.

## Control flow
Streaming DMA map converts the physical address to a Xen DMA address, returns it directly when the device can address it and no bounce is required, or allocates a SWIOTLB slot and maps that instead. Unmap and sync convert the DMA address back to the guest physical page, perform architecture or Xen cache synchronization, then unmap/sync the SWIOTLB pool if the address belongs to one. Scatter-gather helpers apply the same operation to each entry and unwind partial failures. Coherent allocation tries normal pages first and, when needed, asks Xen for a contiguous region within the coherent mask.

## State and persistence
The file owns no durable state. It relies on global SWIOTLB pools, Xen PFN/BFN mappings, page flags such as `PageXenRemapped`, device DMA masks, and architecture cache-coherency state.

## Dependencies and integration points
It integrates with Linux `dma_map_ops`, `dma-direct`, SWIOTLB internals, Xen page translation, Xen contiguous-region hypercalls, architecture cache synchronization, and tracing via `trace_swiotlb_bounced`.

## Risks and test signals
Risks include incorrect PFN/BFN translation, page-boundary contiguity checks, DMA mask overflows, bounce pool lookup for foreign bus addresses, cache sync order on noncoherent devices, coherent allocation/free mismatch, and scatter-gather unwind. Test signals include PCI passthrough DMA under PV guests, 32-bit DMA masks, noncontiguous guest memory, forced SWIOTLB bouncing, coherent allocations crossing Xen page boundaries, noncoherent device sync tests, and DMA API debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/swiotlb-xen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/sys-hypervisor.c -->
# sources/distributed-fs/ceph-client/drivers/xen/sys-hypervisor.c

## Purpose
`sys-hypervisor.c` exposes Xen hypervisor metadata and selected runtime controls under `/sys/hypervisor`. It reports guest type, Xen version, build and feature information, start flags, UUID, and optional VPMU settings.

## Important APIs, types, and functions
The central type is `struct hyp_sysfs_attr`, a wrapper around `struct attribute` with show/store callbacks and per-attribute data. Attribute groups cover `version`, `compilation`, `properties`, `start_flags`, and optional `pmu`. Important show/store functions call `HYPERVISOR_xen_version`, xenbus UUID fallback reads, and `HYPERVISOR_xenpmu_op`. Init functions create files and groups from `hyper_sysfs_init`, while `hypervisor_subsys_init` installs custom sysfs ops on `hypervisor_kobj`.

## Control flow
During device init, the Xen-only initializer creates the basic type and guest-type files, then version, compilation, UUID, property, start-flag, and optional PMU groups, unwinding in reverse order on failure. Sysfs reads dispatch through `hyp_sysfs_show` to the attribute's show function. Writable PMU attributes parse user input and call Xen PMU hypercalls.

## State and persistence
State is mostly sysfs metadata and static attribute arrays. Runtime values are read from the hypervisor on demand. PMU writes affect hypervisor runtime state but are not persisted by this file. UUID may fall back to xenstore if `XENVER_guest_handle` is unavailable.

## Dependencies and integration points
It depends on Xen hypercall interfaces, Xen version structures, xenbus, `hypervisor_kobj`, Linux sysfs/kobject APIs, and optional Xen PMU headers. It integrates with userspace inventory/debug tools that inspect `/sys/hypervisor`.

## Risks and test signals
Risks include init-order coupling with `hypervisor_kobj`, sysfs group unwind mistakes, binary build-id output handling, feature string sizing, xenstored readiness for UUID fallback, and PMU permission/hypervisor support differences. Test signals include booting PV/HVM/PVH/ARM Xen guests, reading all sysfs files, denied build-id behavior, xenstored-delayed UUID fallback, PMU mode/feature read-write tests in dom0, and sysfs error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/sys-hypervisor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/time.c -->
# sources/distributed-fs/ceph-client/drivers/xen/time.c

## Purpose
`time.c` implements Xen runstate and stolen-time accounting. It registers per-VCPU runstate memory with Xen and supplies paravirtual steal-clock data to the Linux scheduler/accounting code.

## Important APIs, types, and functions
Important state is per-CPU `struct vcpu_runstate_info xen_runstate` and `old_runstate_time`. Public functions are `xen_manage_runstate_time`, `xen_vcpu_stolen`, `xen_steal_clock`, `xen_setup_runstate_info`, and `xen_time_setup_guest`. Helpers `get64` and `xen_get_runstate_snapshot_cpu_delta` take consistent hypervisor-updated snapshots.

## Control flow
Setup enables Xen's runstate update flag assist when possible, updates the paravirtual `pv_steal_clock` static call, and enables scheduler static keys. Each CPU registers its runstate memory via `VCPUOP_register_runstate_memory_area`. Steal-clock reads snapshot the current runstate, add accumulated pre-suspend times, and report runnable plus offline time. Suspend/resume handling backs up runstate counters before suspend and accumulates them after resume.

## State and persistence
State is per-CPU runtime memory shared with the hypervisor plus accumulated counters preserved across suspend/resume. It is not durable beyond boot. The snapshot code treats `state_entry_time` and `XEN_RUNSTATE_UPDATE` as synchronization markers.

## Dependencies and integration points
It depends on Xen vcpu and vm-assist hypercalls, paravirt steal-clock static calls, scheduler cputime accounting, static keys, and Xen event/feature definitions.

## Risks and test signals
Risks include inconsistent 64-bit reads on 32-bit kernels, missing memory barriers around hypervisor updates, suspend/resume counter duplication or loss, CPU hotplug registration failures, and differences when remote runstate updates are required. Test signals include stolen-time accounting in busy/oversubscribed guests, 32-bit PV guests, suspend/resume, CPU hotplug, scheduler stat validation, and hypervisor assist unavailable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/unpopulated-alloc.c -->
# sources/distributed-fs/ceph-client/drivers/xen/unpopulated-alloc.c

## Purpose
`unpopulated-alloc.c` provides allocation and free helpers for Xen unpopulated pages: guest physical pages that have `struct page` backing but no real machine memory populated until mapped or granted. These are used by foreign mapping paths such as privcmd and other Xen drivers.

## Important APIs, types, and functions
Exports are `xen_alloc_unpopulated_pages` and `xen_free_unpopulated_pages`. `arch_xen_unpopulated_init` is a weak architecture hook that selects the resource tree for scratch address allocation. Internals include global `page_list`, `list_count`, `target_resource`, `xen_unpopulated_pages`, and `fill_list`, which reserves IOMEM ranges and creates generic device pages through `memremap_pages`.

## Control flow
Early init selects a target resource for scratch ranges. Allocation falls back to ballooned pages if no target resource is available. Otherwise it fills the freelist by allocating a pluggable IOMEM resource, optionally reserving the same range in `iomem_resource`, initializing PV p2m entries to invalid, and using `memremap_pages` to create page structures. Pages are popped under a mutex and, on PV, p2m entries are allocated before returning. Freeing pushes pages back to the global list.

## State and persistence
The module maintains a runtime freelist of unpopulated device pages protected by `list_lock`. Resource reservations and dev_pagemap ownership persist for the boot lifetime, but there is no on-disk persistence.

## Dependencies and integration points
It depends on memory hotplug resource APIs, `memremap_pages`, Xen balloon APIs, Xen p2m operations under PVMMU, and architecture-provided resource selection. It integrates with `privcmd.c` and other Xen code needing placeholder pages for foreign mappings.

## Risks and test signals
Risks include resource leaks on partial `fill_list` failure, p2m invalidation assumptions, fallback differences when no target resource exists, section-size rounding, holding stale device-page metadata in `zone_device_data`, and concurrent allocation/free. Test signals include allocation/free stress, PV and HVM guests, memory hotplug configs, failure injection in resource allocation and `memremap_pages`, privcmd foreign mapping teardown, and balloon fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/unpopulated-alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-acpi-pad.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-acpi-pad.c

## Purpose
`xen-acpi-pad.c` handles ACPI processor aggregator notifications in Xen dom0 and translates requested idle CPU counts into Xen core-parking platform operations.

## Important APIs, types, and functions
Important functions are `xen_acpi_pad_idle_cpus`, `xen_acpi_pad_idle_cpus_num`, `acpi_pad_pur`, `acpi_pad_handle_notify`, `acpi_pad_notify`, `acpi_pad_probe`, and `acpi_pad_remove`. The driver matches ACPI HID `ACPI000C` and registers a platform driver named `acpi_processor_aggregator`.

## Control flow
Initialization runs only in the Xen initial domain and only on Xen 4.2 or newer. Probe installs an ACPI notify handler. On notification `0x80`, the driver evaluates `_PUR` to get the requested number of idle CPUs, calls `XENPF_core_parking` to set the count, queries the result, and reports status with `_OST`. Remove unparks CPUs and removes the notify handler.

## State and persistence
State is minimal: `xen_cpu_lock` serializes platform operations and ACPI notification handling. Xen core-parking state changes live in the hypervisor until changed again; the driver itself stores no durable state.

## Dependencies and integration points
It depends on ACPI platform devices, `_PUR`/`_OST`, Xen platform hypercalls, Xen version detection, and dom0-only initialization. It integrates firmware power-management events with Xen CPU core parking.

## Risks and test signals
Risks include malformed `_PUR` packages, unsupported Xen versions, concurrent notifications, failure to unpark on remove, and mismatched ACPI status reporting. Test signals include ACPI000C probe, notification injection, `_PUR` failure cases, Xen platform-op errors, remove/unpark behavior, and domU/non-Xen refusal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-acpi-pad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-acpi-processor.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-acpi-processor.c

## Purpose
`xen-acpi-processor.c` uploads ACPI processor power-management data from dom0 to the Xen hypervisor. It sends C-state and P-state information so Xen can manage physical CPU idle and frequency behavior.

## Important APIs, types, and functions
Key functions are `push_cxx_to_hypervisor`, `push_pxx_to_hypervisor`, `xen_copy_pss_data`, `xen_copy_psd_data`, `xen_copy_pct_data`, `upload_pm_data`, `get_max_acpi_id`, `read_acpi_id`, `check_acpi_ids`, `xen_upload_processor_pm_data`, resume work, and module init/exit. Important state includes `nr_acpi_bits`, `acpi_ids_done`, `acpi_id_present`, `acpi_id_cst_present`, `acpi_psd`, and per-CPU `acpi_perf_data`.

## Control flow
Initialization runs only in the Xen initial domain. It sizes bitmaps from Xen physical CPU info, allocates ACPI performance storage, asks ACPI core to preregister performance data, loads per-processor performance info, uploads C/P state data for possible CPUs, walks ACPI namespace to catch physical CPUs not visible as dom0 vCPUs, and registers a syscore resume hook. Resume defers re-upload to a work item because syscore resume context is atomic.

## State and persistence
The driver stores runtime bitmaps of processed and present ACPI IDs, cached PSD packages, and per-CPU performance structures. Uploaded PM state resides in Xen until refreshed or rebooted. The `off` module parameter inhibits hypercalls for testing or disabling upload behavior.

## Dependencies and integration points
It depends on ACPI processor/cpufreq internals, Xen `XENPF_set_processor_pminfo` and `XENPF_get_cpuinfo` platform ops, syscore resume, CPU masks, per-CPU allocations, and dom0 physical CPU enumeration. It intentionally initializes before cpufreq scaling drivers.

## Risks and test signals
Risks include ACPI ID bitmap sizing, virtual CPU vs physical CPU mismatches, malformed ACPI tables, missing P-state components, copy/layout assumptions between ACPI and Xen structures, resume re-upload ordering, and partial allocation cleanup. Test signals include dom0 with limited `xen_max_vcpus`, CPU hotplug-capable ACPI tables, systems with PBLK but no `_CST`, P-state dependency domains, `off=1` dry runs, suspend/resume, and hypercall error handling for invalid ACPI IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-acpi-processor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-balloon.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-balloon.c

## Purpose
`xen-balloon.c` exposes the Xen balloon control device and xenstore target watcher. It lets userspace and xenstore adjust the guest memory target and exposes current balloon stats through sysfs.

## Important APIs, types, and functions
The public entry point is `xen_balloon_init`. Important functions are `watch_target`, `balloon_init_watcher`, `target_kb_show/store`, `target_show/store`, and `register_balloon`. It defines sysfs attributes for target, scheduling/retry controls, scrub-pages, and current/low/high memory information. Under memory hotplug it references `xen_saved_max_mem_size`.

## Control flow
`xen_balloon_init` registers a `xen_memory` bus/device with balloon sysfs groups and registers a xenstore notifier. Once xenstore is available, the notifier installs a watch on `memory/target`. Watch callbacks read the new target in KiB, compensate for static-max differences in HVM/non-dom0 cases, and call `balloon_set_new_target`. Sysfs stores require `CAP_SYS_ADMIN`, parse byte or KiB values, and update the target.

## State and persistence
State is mainly the global balloon stats from the Xen balloon subsystem plus static watch-local variables tracking first-fire adjustment. Sysfs changes and xenstore target updates affect runtime balloon target state; persistent policy is external to this file.

## Dependencies and integration points
It depends on Xen balloon core APIs, xenbus watches/notifiers, Linux device/bus/sysfs infrastructure, capability checks, memory hotplug globals, Xen page/features, and mem-reservation helpers. It integrates Xen memory policy with Linux sysfs and xenstore.

## Risks and test signals
Risks include target conversion mistakes, first-watch target adjustment for HVM guests, missing xenstore keys, permission enforcement, sysfs registration cleanup on failure, and interactions with memory hotplug max-memory restoration. Test signals include xenstore target changes, sysfs target writes with and without `CAP_SYS_ADMIN`, dom0/PV/HVM cases, memory hotplug-enabled boots, scrub/retry attribute reads, and balloon target convergence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-balloon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-front-pgdir-shbuf.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-front-pgdir-shbuf.c

## Purpose
`xen-front-pgdir-shbuf.c` is a helper for Xen frontend/backend protocols that share buffers through a page directory containing grant references. It supports buffers allocated locally by the frontend and buffers allocated by the backend.

## Important APIs, types, and functions
Exported APIs are `xen_front_pgdir_shbuf_alloc`, `xen_front_pgdir_shbuf_free`, `xen_front_pgdir_shbuf_get_dir_start`, `xen_front_pgdir_shbuf_map`, and `xen_front_pgdir_shbuf_unmap`. Internal types are `struct xen_page_directory` and `struct xen_front_pgdir_shbuf_ops`. Important helpers compute required grant refs, fill page directories, grant frontend pages, map/unmap backend-provided grant refs, and allocate directory/gref storage.

## Control flow
Allocation chooses backend or local ops from the config, records the Xenbus device and pages, computes grant counts, allocates the gref array and page directory, grants page-directory pages to the other end, optionally grants local buffer pages, and fills the directory. For backend-allocated buffers, later `map` reads grant references from the directory and maps them onto provided pages; `unmap` reverses those mappings. Free ends all grant accesses and frees the directory and gref array.

## State and persistence
The caller-owned `struct xen_front_pgdir_shbuf` stores runtime grants, directory memory, page array, map handles, ops, and Xenbus device pointer. Grant-table state persists only until ended or unmapped; there is no durable storage.

## Dependencies and integration points
It depends on Xen grant tables, Xenbus device IDs, balloon/page helpers, Xen ring protocol directory conventions, and the public `xen-front-pgdir-shbuf.h` interface. It integrates with Xen display and other para-virtual protocols using page-directory shared buffers.

## Risks and test signals
Risks include grant leaks on partial allocation, invalid backend grefs, map/unmap handle mismatches, off-by-one directory chaining, backend ring-order/page-count mismatch, failure paths that do not free grant references, and address conversion assumptions. Test signals include local and backend-allocated buffer setup, multi-page directories, map failure injection, repeated map/unmap/free, backend-provided bad grefs, and protocol-level display/shared-buffer smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-front-pgdir-shbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/Makefile -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/Makefile

## Purpose
This Makefile builds the Xen PCI backend driver and its component objects for either `CONFIG_XEN_PCIDEV_BACKEND` or `CONFIG_XEN_PCIDEV_STUB`.

## Important APIs, types, and functions
It is kbuild metadata, not C code. It maps both backend and stub config symbols to `xen-pciback.o`, whose object list includes `pci_stub.o`, `pciback_ops.o`, `xenbus.o`, `conf_space.o`, `conf_space_header.o`, `conf_space_capability.o`, `conf_space_quirks.o`, `vpci.o`, and `passthrough.o`.

## Control flow
Kbuild selects `xen-pciback.o` when either supported config is enabled. The comment notes that a single `CONFIG_XEN_PCI_STUB` line would not express the needed module behavior because related symbols are mutually exclusive and one may remain built-in.

## State and persistence
Only build graph state exists. Runtime behavior comes from the compiled objects.

## Dependencies and integration points
It integrates Xen PCI backend Kconfig symbols with the implementation files in `drivers/xen/xen-pciback`.

## Risks and test signals
Risks are stale object lists, config-symbol mismatch, and module/built-in selection regressions. Test signals include builds for backend-only, stub-only, built-in, module, and allmodconfig configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space.c

## Purpose
`conf_space.c` implements Xen pciback's virtual PCI configuration space dispatcher. It intercepts guest config reads/writes, overlays selected fields, and blocks unsafe changes to real PCI resources unless explicitly allowed.

## Important APIs, types, and functions
Public functions are generated real-config accessors, `xen_pcibk_config_read`, `xen_pcibk_config_write`, `xen_pcibk_get_interrupt_type`, `xen_pcibk_config_free_dyn_fields`, `xen_pcibk_config_reset_dev`, `xen_pcibk_config_free_dev`, `xen_pcibk_config_add_field_offset`, `xen_pcibk_config_init_dev`, and `xen_pcibk_config_init`. `xen_pcibk_permissive` is a module parameter. It operates on `struct config_field` and `struct config_field_entry` lists stored in `struct xen_pcibk_dev_data`.

## Control flow
Device initialization creates a config-field list, adds header fields, capability fields, and quirk entries. Reads first read the real PCI config value, then merge any overlapping virtual fields into the returned value. Writes walk overlapping fields, read the virtual field value, merge the guest write, and call field-specific write callbacks. Unhandled writes are ignored with a warning unless device or module permissive mode allows direct writes. Reset/free paths call field callbacks and release list entries.

## State and persistence
Per-device state is the config field list and callback data owned by `xen_pcibk_dev_data`. The global permissive flag affects all devices at runtime. PCI config writes change hardware state when allowed, but the overlay itself is in memory only.

## Dependencies and integration points
It depends on Linux PCI config accessors, `pciback.h`, `conf_space.h`, and quirks/header/capability providers. It integrates with pciback operation handling that services frontend PCI config-space requests.

## Risks and test signals
Risks include incorrect overlap merging for partial reads/writes, duplicate field handling, permissive-mode safety, interrupt type detection when qemu bypasses MSI helpers, callback data lifetime, and mapping PCIBIOS errors to Xen ABI values. Test signals include guest config reads/writes of BARs, command register, MSI/MSI-X, unaligned invalid requests, permissive toggles, reset/free cycles, and frontend PCI passthrough boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space.h -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space.h

## Purpose
`conf_space.h` defines the virtual PCI configuration-space field abstraction used by Xen pciback.

## Important APIs, types, and functions
It defines callback typedefs for field init/reset/free/read/write operations, `struct config_field`, `struct config_field_entry`, interrupt-type constants, `xen_pcibk_permissive`, and the `OFFSET` macro. Inline helpers add one field, an array of fields, or offset-adjusted fields. It declares real config accessors, capability/header initialization, and interrupt-type detection.

## Control flow
The header's inline add helpers iterate sentinel-terminated field arrays and call `xen_pcibk_config_add_field_offset`. Actual control flow is implemented in the C files.

## State and persistence
The structures describe runtime per-device field list entries and per-field private data. No state is stored in the header itself.

## Dependencies and integration points
It depends on Linux lists and errno helpers and is shared by `conf_space.c`, header/capability/quirk modules, and pciback code.

## Risks and test signals
Risks include field array sentinel mistakes, callback signature drift, size/read/write union misuse, and offset arithmetic errors. Test signals are compile coverage, config-field registration tests, and pciback config-space operations crossing field boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_capability.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_capability.c

## Purpose
`conf_space_capability.c` registers virtual overlays for selected PCI capability-list entries so a pciback guest can inspect capabilities while unsafe writes are blocked or constrained.

## Important APIs, types, and functions
The key type is `struct xen_pcibk_config_capability`, stored in a global capability list. Public functions are `xen_pcibk_config_capability_init` and `xen_pcibk_config_capability_add_fields`. Capability handlers cover VPD, PM, MSI, and MSI-X. Important callbacks include `vpd_address_write`, `pm_caps_read`, `pm_ctrl_write`, `pm_ctrl_init`, `msi_field_init`, `msix_field_init`, and `msi_msix_flags_write`.

## Control flow
Initialization registers supported capabilities. Per-device setup scans for each capability using `pci_find_capability`, adds the common capability header overlay at the discovered offset, then adds capability-specific fields. PM init disables PME, PM writes allow only safe bits and delegate state transitions to `pci_set_power_state`. MSI/MSI-X writes are rejected unless permissive mode or device `allow_interrupt_control` permits them, and they prevent enabling conflicting interrupt modes.

## State and persistence
State includes the global list of supported capability descriptors and per-device config field entries. Field init for MSI/MSI-X returns static configuration descriptors; PM init may change hardware PME state. Persistent storage is not used.

## Dependencies and integration points
It depends on Linux PCI capability definitions and helpers, pciback device policy flags, and the config-field dispatcher. It integrates with pciback's virtual config-space initialization.

## Risks and test signals
Risks include exposing unsafe capability writes, interrupt-mode conflicts, permissive bypass behavior, PM state transition failures, VPD write restrictions, and duplicate capability field offsets. Test signals include guests enabling/disabling MSI and MSI-X, INTx/MSI exclusivity cases, PM state changes, VPD reads/writes, permissive and allow-interrupt-control toggles, and devices with absent or malformed capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_capability.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_header.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_header.c

## Purpose
`conf_space_header.c` defines pciback overlays for the standard PCI configuration header. It makes identity, command, interrupt, BAR, ROM, and selected header fields safe for a guest driver domain.

## Important APIs, types, and functions
The public entry point is `xen_pcibk_config_header_add_fields`. Internal types `struct pci_cmd_info` and `struct pci_bar_info` cache command and BAR state. Key callbacks are `command_init/read/write`, `bar_init/read/write/reset/release`, `rom_write`, vendor/device/interrupt readers, and `bist_write`. Field arrays `header_common`, `header_0`, and `header_1` describe common, normal-device, and bridge overlays.

## Control flow
Header initialization adds common fields, then adds BAR/ROM fields based on PCI header type. Command writes translate selected guest bits into `pci_enable_device`, `pci_disable_device`, bus-master changes, MWI changes, and optional INTx control; direct config writes happen only in permissive mode and only for guest-controlled bits. BAR writes allow sizing probes and restoration of cached values, while reads return either cached BAR value or length value depending on the last sizing write. Unsupported header types fail initialization.

## State and persistence
Per-field callback data caches original command and BAR/ROM values. Hardware state may change when enabling/disabling devices, bus mastering, MWI, INTx, BIST, cache line size, or restored BAR values. The overlay state is per-device runtime memory.

## Dependencies and integration points
It depends on Linux PCI core helpers, pciback policy flags, and the config-space field abstraction. It integrates with pciback config initialization to prevent guest drivers from moving host resources while preserving expected PCI probing semantics.

## Risks and test signals
Risks include BAR sizing emulation errors, 64-bit BAR high-half handling, command-bit masking, permissive writes to unsafe fields, interrupt control policy, device enable/disable side effects, and bridge header differences. Test signals include guest BAR probing, 64-bit memory BARs, ROM BAR reads/writes, command register toggles, bus-master enable/disable, INTx disable control, BIST writes, bridge passthrough, and reset/free of field data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_header.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_quirks.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_quirks.c

## Purpose
`conf_space_quirks.c` manages dynamically registered pciback configuration-space quirks for devices needing additional writable or overridden fields.

## Important APIs, types, and functions
It defines global `xen_pcibk_quirks`, match helper `match_one_device`, lookup `xen_pcibk_find_quirk`, duplicate check `xen_pcibk_field_is_dup`, `xen_pcibk_config_quirks_add_field`, `xen_pcibk_config_quirks_init`, `xen_pcibk_config_field_free`, and `xen_pcibk_config_quirk_release`.

## Control flow
Per-device quirk initialization allocates a quirk descriptor containing the device's IDs and adds it to the global quirk list. Adding a quirk field fills default read/write callbacks according to field size and delegates to the config-space dispatcher. Release finds the matching quirk by PCI IDs, removes it from the list, and frees it.

## State and persistence
State is the global in-memory quirk list and any dynamically allocated config fields attached to devices. There is no durable persistence.

## Dependencies and integration points
It depends on Linux PCI ID matching, pciback device data, `conf_space.h`, and the shared `xen_pcibk_quirks` declaration in `pciback.h`. It integrates with sysfs or other pciback paths that add per-device quirk fields.

## Risks and test signals
Risks include broad ID matching removing the wrong quirk, duplicate field suppression hiding intended overrides, dynamic field cleanup, unsupported field sizes, and global list concurrency assumptions. Test signals include adding and removing quirks for multiple devices, duplicate offsets, byte/word/dword fields, release after device removal, and config reads/writes through dynamic fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_quirks.h -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_quirks.h

## Purpose
`conf_space_quirks.h` declares pciback's dynamic configuration-space quirk interface.

## Important APIs, types, and functions
It defines `struct xen_pcibk_config_quirk`, containing list linkage, PCI device ID match data, and the associated `struct pci_dev`. It declares functions to add quirk fields, initialize quirks, free dynamic config fields, release a quirk, and test whether a field offset is already present.

## Control flow
The header itself has no runtime flow. Callers initialize per-device quirk records and add fields through the declared functions.

## State and persistence
The structure describes runtime quirk list entries. No state is stored by the header.

## Dependencies and integration points
It depends on Linux PCI and list definitions plus `struct config_field` from `conf_space.h` via users that include both. It is shared by quirk implementation and config-space setup code.

## Risks and test signals
Risks are declaration drift, missing include ordering for `struct config_field`, and mismatched quirk lifecycle assumptions. Test signals are pciback builds and dynamic quirk add/remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_quirks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/passthrough.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/passthrough.c

## Purpose
`passthrough.c` implements the pciback backend mode that exposes PCI devices to the frontend using their real host domain/bus/devfn topology rather than virtualized BDF numbering.

## Important APIs, types, and functions
The key local type is `struct passthrough_dev_data`, containing a device list and mutex. Backend callbacks are implemented by `__xen_pcibk_init_devices`, `__xen_pcibk_add_pci_dev`, `__xen_pcibk_get_pci_dev`, `__xen_pcibk_publish_pci_roots`, `__xen_pcibk_release_pci_dev`, `__xen_pcibk_release_devices`, and `__xen_pcibk_get_pcifront_dev`. They are published through `xen_pcibk_passthrough_backend`.

## Control flow
Backend init allocates the list container. Adding a PCI device appends it to the protected list and publishes its real domain/bus/devfn through the provided callback. Lookup scans the list for the requested BDF. Publishing roots walks exported devices and publishes only those whose parent bridges are not also exported. Release removes entries and returns devices to pcistub. Full teardown releases every tracked device and frees backend data.

## State and persistence
State is a per-`xen_pcibk_device` list of exported `pci_dev` pointers protected by a mutex. Device ownership is returned to pcistub on release. No state persists beyond backend lifetime.

## Dependencies and integration points
It depends on Linux PCI structures, pciback backend callback definitions, and pcistub get/put ownership. It integrates with xenbus publishing and pciback operation paths via `xen_pcibk_backend`.

## Risks and test signals
Risks include duplicate devices, publishing incorrect roots when parent bridges are also exported, locking around device release, stale `pci_dev` pointers, and frontend requests for unexported BDFs. Test signals include passthrough mode with single devices and bridge hierarchies, add/release cycles, lookup for missing devices, frontend AER mapping, and concurrent publish/release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/passthrough.c -->
