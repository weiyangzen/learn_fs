# subset-b-005586 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_core.c -->
# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_core.c

## Purpose
`vboxguest_core.c` is the platform-independent core of the VirtualBox Guest Additions kernel driver. It translates Linux-side sessions and ioctls into VMMDev requests, manages host event filtering, guest capability ownership, HGCM client lifetimes, host heartbeat, mouse status, and the VirtualBox memory balloon.

## Important APIs, types, and functions
The exported core entry points are `vbg_core_init`, `vbg_core_exit`, `vbg_core_open_session`, `vbg_core_close_session`, `vbg_core_ioctl`, `vbg_core_set_mouse_status`, and `vbg_core_isr`. Important internal paths include `vbg_query_host_version`, `vbg_report_guest_info`, `vbg_report_driver_status`, `vbg_set_session_event_filter`, `vbg_acquire_session_capabilities`, `vbg_set_session_capabilities`, `vbg_ioctl_vmmrequest`, `vbg_ioctl_hgcm_*`, `vbg_ioctl_wait_for_events`, and `vbg_balloon_work`.

## Control flow
Initialization preallocates host request buffers, queries host features, reports guest version/status, resets host event and capability masks, clears mouse status, optionally reserves guest mapping space, and starts heartbeat. User open creates a `vbg_session`; ioctl dispatch validates the common header, routes VMMDev passthrough, fixed ioctls, HGCM calls, event waits, capability/filter changes, balloon queries, and coredump requests. The ISR acknowledges pending host events, wakes HGCM waiters, schedules balloon work, records normal events, and reports absolute mouse movement to Linux input.

## State and persistence
State is runtime-only in `struct vbg_dev` and `struct vbg_session`: pending events, per-session HGCM client IDs, event/capability usage trackers, host-reported version/features, heartbeat timer/request, preallocated request packets, balloon chunk page arrays, and guest mapping reservation. Synchronization uses `event_spinlock`, `session_mutex`, wait queues, `cancel_req_mutex`, workqueues, and a timer. Nothing is persisted beyond module/device lifetime.

## Dependencies and integration points
This file depends on `vboxguest_core.h`, `vmmdev.h`, `linux/vboxguest.h`, `linux/vbox_err.h`, `linux/vbox_utils.h`, page/vmalloc APIs, wait queues, timers, and MMIO/PIO request submission from `vboxguest_utils.c`. It integrates with the Linux PCI wrapper, miscdevice ioctls, input mouse reporting, VirtualBox HGCM services, and the host VMMDev event protocol.

## Risks and test signals
Primary risks are ioctl size/type validation, user request allowlisting, HGCM client ID ownership, 32-bit compat conversion, event consumption races between sessions, rollback of capability/event masks after host failures, reuse of preallocated request buffers from asynchronous contexts, balloon inflate/deflate error handling, and leaking guest mapping reservation if host cleanup fails. Test signals include VirtualBox boot/probe, `/dev/vboxguest` and `/dev/vboxuser` ioctl matrices, unprivileged denied requests, HGCM async timeout/cancel, event wait cancellation, guest capability contention, host restore events, balloon target changes, heartbeat disable/enable, and IRQ-driven mouse movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_core.h -->
# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_core.h

## Purpose
`vboxguest_core.h` is the private shared interface between the VirtualBox Guest core, the Linux PCI/misc/input wrapper, and the utility/HGCM implementation. It defines the driver state objects, session state, ABI compatibility ioctl constants, and internal function prototypes.

## Important APIs, types, and functions
Key types are `struct vbg_mem_balloon`, `struct vbg_bit_usage_tracker`, `struct vbg_dev`, and `struct vbg_session`. `vbg_dev` owns the VMMDev I/O port/MMIO mapping, host version/features, event/HGCM wait queues, pending event state, request buffers, input device, memory balloon, session/capability tracking, heartbeat timer, and two miscdevices. `vbg_session` tracks per-open HGCM clients, event filters, acquired/set capabilities, requestor flags, and waiter cancellation. Prototypes expose core lifecycle, ioctl dispatch, ISR, Linux mouse callback, request allocation/submission, and compat HGCM calls.

## Control flow
The header’s structure mirrors runtime ownership: `vboxguest_linux.c` allocates/fills `vbg_dev`, calls `vbg_core_init`, registers IRQ and miscdevices, then hands per-open ioctls to `vbg_core_ioctl`. `vboxguest_utils.c` uses the declared helpers to allocate DMA32 request packets and execute HGCM calls against the `vbg_dev` transport.

## State and persistence
All state declared here is in-memory driver state. The header documents which fields are protected by `event_spinlock`, `session_mutex`, or `cancel_req_mutex`; the balloon pages and heartbeat request survive only while the PCI device is bound.

## Dependencies and integration points
It includes Linux input, interrupt, miscdevice, wait, workqueue, and list APIs, the UAPI `linux/vboxguest.h`, and the VMMDev protocol header. It is the coupling point for the core, Linux bus wrapper, and HGCM utility code.

## Risks and test signals
Risks are ABI compatibility drift in the `_ALT` ioctl numbers, incorrect lock assumptions around shared fields, stale prototypes when core/helper behavior changes, and lifetime issues for exported `vbg_get_gdev` consumers that dereference `vbg_dev`. Test signals include allmodconfig builds, compat ioctl builds, lockdep under concurrent sessions, and loading related VirtualBox modules such as vboxsf against the exported device handle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_linux.c -->
# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_linux.c

## Purpose
`vboxguest_linux.c` is the Linux-specific VirtualBox guest driver wrapper. It probes the VirtualBox VMMDev PCI device, maps resources, registers `/dev/vboxguest` and `/dev/vboxuser`, exposes host version/features through sysfs, creates the absolute mouse input device, and connects the generic core to Linux IRQ, PCI, miscdevice, and input subsystems.

## Important APIs, types, and functions
Important functions are `vbg_pci_probe`, `vbg_pci_remove`, `vbg_misc_device_ioctl`, `vbg_misc_device_open`, `vbg_misc_device_user_open`, `vbg_create_input_device`, `vbg_input_open`, `vbg_input_close`, `vbg_linux_mouse_event`, `vbg_get_gdev`, and `vbg_put_gdev`. The driver registers a `pci_driver` matching vendor `0x80ee` and device `0xcafe`, sysfs attributes `host_version` and `host_features`, and two file operation tables.

## Control flow
Probe enables PCI, claims I/O and MMIO resources, maps VMMDev memory, validates the MMIO version/size, initializes `vbg_dev`, calls `vbg_core_init`, registers input, IRQ, and misc devices, and publishes the singleton `vbg_gdev`. Opens create sessions with requestor flags derived from uid/gid and whether the public `vboxuser` node was used. Ioctl copies and sizes the user buffer, allocates a DMA32 VMMDev request buffer for raw VMMDev requests or normal kernel memory otherwise, delegates to `vbg_core_ioctl`, then copies back the bounded output.

## State and persistence
Runtime state is devm-managed `vbg_dev`, the singleton `vbg_gdev` protected by `vbg_gdev_mutex`, per-open sessions in `file->private_data`, and input-device state. No persistent storage is used. `vbg_get_gdev` intentionally returns with the global mutex held until `vbg_put_gdev` so short-lived external users cannot race removal.

## Dependencies and integration points
The file depends on PCI, miscdevice, usercopy, credentials, input, IRQ, and the core header. It integrates with userspace device nodes, Linux input reporting, sysfs, VirtualBox shared-folder style in-kernel consumers through exported `vbg_get_gdev`, and the host VMMDev interrupt line.

## Risks and test signals
Risks include usercopy size mistakes, `_IOC_SIZE` compatibility, more than one VMMDev PCI function, stale singleton locking, IRQ teardown ordering, input registration failure unwind, unprivileged access through `vboxuser`, and MMIO validation against hostile or broken virtual hardware. Test signals include PCI probe/remove fault injection, misc ioctl fuzzing, compat ioctl calls, sysfs reads, mouse open/close and absolute events, vboxsf load/unload while removing the PCI device, and udev-created permissions for both nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_linux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_utils.c -->
# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_utils.c

## Purpose
`vboxguest_utils.c` implements low-level VMMDev request allocation/submission, VirtualBox debug logging, HGCM connect/disconnect/call support, user/kernel linear-address conversion to physical page lists, async HGCM cancellation, 32-bit compat conversion, and VirtualBox-status-to-Linux-errno mapping.

## Important APIs, types, and functions
Exported functions include `vbg_info`, `vbg_warn`, `vbg_err`, `vbg_err_ratelimited`, `vbg_req_alloc`, `vbg_req_free`, `vbg_req_perform`, `vbg_hgcm_connect`, `vbg_hgcm_disconnect`, `vbg_hgcm_call`, and `vbg_status_code_to_errno`; `vbg_hgcm_call32` is built for `CONFIG_COMPAT`. Internal helpers include `hgcm_call_preprocess`, `hgcm_call_preprocess_linaddr`, `hgcm_call_init_linaddr`, `hgcm_call_init_call`, `vbg_hgcm_do_call`, `hgcm_cancel_call`, and `hgcm_call_copy_back_result`.

## Control flow
Requests are allocated from DMA32 pages, initialized with a VMMDev header, submitted by writing the physical address to the VMMDev I/O port, and read after a memory barrier. HGCM calls validate parameters, bounce user linear buffers into kernel memory, calculate extra space for physical page lists, construct a host call packet, submit it, wait on `hgcm_wq` for async completion when needed, cancel on timeout/signal, copy scalar and output buffers back, and free or intentionally leak requests only in the unrecoverable cancellation race.

## State and persistence
The file has a global spinlock and small log buffer for serialized debug-port output. HGCM operation state is per request, with temporary bounce buffers and request pages. Cancellation reuses `gdev->cancel_req` under `cancel_req_mutex`. No state persists outside active requests.

## Dependencies and integration points
It depends on I/O port access, page/vmalloc address translation, uaccess, kvmalloc, VirtualBox error codes, VMMDev types, and wait queues owned by `vbg_dev`. It is used by the core and exported for other VirtualBox guest modules that need HGCM services.

## Risks and test signals
Risks include oversized user buffers, partial usercopy, page-list size arithmetic, vmalloc vs direct-map page translation, async completion/cancel races, intentional leaked request buffers after failed cancellation, incorrect errno mapping for unrecognized host statuses, and debug-port output from atomic contexts. Test signals include HGCM services with scalar/input/output/inout parameters, 32-bit compat clients, fault-injected user pointers, large buffer boundary tests, signal and timeout cancellation, host async completion races, unknown status codes, and lockdep around cancel/log locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_version.h -->
# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_version.h

## Purpose
`vboxguest_version.h` defines the VirtualBox Guest Additions version values reported by the in-kernel guest driver to the VirtualBox host. It is a small protocol/versioning header rather than executable logic.

## Important APIs, types, and functions
The exported compile-time constants are `VBG_VERSION_MAJOR`, `VBG_VERSION_MINOR`, `VBG_VERSION_BUILD`, `VBG_SVN_REV`, and `VBG_VERSION_STRING`. `vboxguest_core.c` uses them in `vbg_report_guest_info` to fill `struct vmmdev_guest_info2`.

## Control flow
There is no runtime control flow in this header. During core initialization, the version constants are copied into a VMMDev guest-info request and sent to the host before the driver reports itself active.

## State and persistence
The constants become runtime protocol data only when included in the guest-info request. They do not persist in the guest, but the host can use them to decide which guest-addition features to enable or assume.

## Dependencies and integration points
The header is consumed by the VirtualBox guest core and must stay synchronized with the upstream/out-of-tree VirtualBox versioning expectations when features are ported.

## Risks and test signals
Risks are stale or misleading version values that cause host-side feature gating mismatches, especially if the mainline driver diverges from upstream VirtualBox capabilities. Test signals include host version negotiation across old/new VirtualBox hosts and validating the host sees the expected additions version string and feature behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vmmdev.h -->
# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vmmdev.h

## Purpose
`vmmdev.h` defines the private VirtualBox VMMDev guest-host protocol structures and constants used by the vboxguest driver. It captures MMIO layout, event bits, guest capabilities, request headers, guest information/status packets, memory balloon requests, heartbeat packets, and HGCM request formats.

## Important APIs, types, and functions
Important protocol types include `struct vmmdev_memory`, `struct vmmdev_request_header`, `struct vmmdev_mouse_status`, `struct vmmdev_host_version`, `struct vmmdev_mask`, `struct vmmdev_events`, `struct vmmdev_guest_info`, `struct vmmdev_guest_info2`, `struct vmmdev_guest_status`, `struct vmmdev_memballoon_info`, `struct vmmdev_memballoon_change`, `struct vmmdev_heartbeat`, `struct vmmdev_hgcmreq_header`, `struct vmmdev_hgcm_connect`, `struct vmmdev_hgcm_disconnect`, `struct vmmdev_hgcm_call`, and `struct vmmdev_hgcm_cancel2`. Event and capability macros define valid masks.

## Control flow
This header does not execute code. The core and utilities allocate these structures, fill the common request header, write the physical request address to the VMMDev port, and interpret host-mutated output fields. The ISR relies on `vmmdev_memory.have_events` and `VMMDEVREQ_ACKNOWLEDGE_EVENTS` packets to drain host events.

## State and persistence
The structures describe on-wire/in-memory ABI state shared with the host. Driver state persists only as allocated request packets, MMIO content, and host-maintained event/capability state while the VM is running.

## Dependencies and integration points
It depends on Linux types, sizes, bit helpers, and `linux/vbox_vmmdev_types.h` for shared request enums and HGCM parameter definitions. It is tightly integrated with VirtualBox host expectations and the Linux guest core.

## Risks and test signals
Risks are ABI layout drift, incorrect packing/alignment, wrong valid masks, truncation of physical addresses such as the 32-bit cancel field, and changing comments/constants without matching host behavior. Test signals include `VMMDEV_ASSERT_SIZE` build checks, cross-architecture builds, host request compatibility tests, event mask negotiation, HGCM calls, heartbeat, balloon requests, and mouse/status packets against multiple VirtualBox host versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vmmdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vmgenid.c -->
# sources/distributed-fs/ceph-client/drivers/virt/vmgenid.c

## Purpose
`vmgenid.c` is a platform driver for Microsoft Virtual Machine Generation ID. It feeds generation-ID changes into the kernel random subsystem so cloned, forked, or restored VMs can perturb randomness when the hypervisor changes the 16-byte generation identifier.

## Important APIs, types, and functions
The main state is `struct vmgenid_state`, containing the mapped current ID pointer and the last observed ID. Important functions are `setup_vmgenid_state`, `vmgenid_notify`, ACPI-specific `vmgenid_add_acpi` and `vmgenid_acpi_handler`, OF-specific `vmgenid_add_of` and `vmgenid_of_irq_handler`, and platform probe `vmgenid_add`. Match tables cover ACPI IDs `VMGENCTR` and `VM_GEN_COUNTER`, and OF compatible `microsoft,vmgenid`.

## Control flow
Probe allocates state, maps the 16-byte ID either from ACPI `ADDR` or the first OF resource, seeds device randomness with the initial value, and registers a notification mechanism. ACPI notifications and OF interrupts call `vmgenid_notify`, which copies the new ID, compares it with the old ID, and calls `add_vmfork_randomness` only when it changed.

## State and persistence
The driver stores the last seen 16-byte ID in devm-managed memory and maps the hypervisor-owned current ID. No filesystem persistence exists. The random subsystem receives both initial device randomness and later VM-fork randomness.

## Dependencies and integration points
It depends on platform devices, ACPI or devicetree resource discovery, interrupts, `devm_memremap` or `devm_platform_get_and_ioremap_resource`, and `linux/random.h`. It integrates with firmware descriptions and the kernel RNG.

## Risks and test signals
Risks include malformed ACPI `ADDR` packages, incorrect 64-bit physical address composition, missing interrupts, notification before `driver_data` is set, repeated notifications with unchanged IDs, and mapping attributes for hypervisor-provided memory. Test signals include ACPI and OF boot paths, clone/restore notification injection, unchanged-ID notifications, bad firmware packages/resources, IRQ registration failures, and observing `add_vmfork_randomness` effects through RNG selftests or tracepoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vmgenid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/virtio/Kconfig

## Purpose
This Kconfig file defines the build configuration menu for the Linux virtio bus and many virtio transport/device drivers. It controls core virtio availability, PCI/MMIO/vDPA transports, memory, input, balloon, DMA buffer, debug, and RTC support.

## Important APIs, types, and functions
It is declarative Kconfig. Key symbols include `VIRTIO_ANCHOR`, `VIRTIO`, `VIRTIO_PCI_LIB`, `VIRTIO_PCI_LIB_LEGACY`, `VIRTIO_MENU`, `VIRTIO_HARDEN_NOTIFICATION`, `VIRTIO_PCI`, `VIRTIO_PCI_ADMIN_LEGACY`, `VIRTIO_PCI_LEGACY`, `VIRTIO_VDPA`, `VIRTIO_PMEM`, `VIRTIO_BALLOON`, `VIRTIO_MEM`, `VIRTIO_INPUT`, `VIRTIO_MMIO`, `VIRTIO_MMIO_CMDLINE_DEVICES`, `VIRTIO_DMA_SHARED_BUFFER`, `VIRTIO_DEBUG`, and `VIRTIO_RTC` with its PTP/ARM/RTC-class suboptions.

## Control flow
`VIRTIO` is selected by transports and selects `VIRTIO_ANCHOR`. The visible `VIRTIO_MENU` gates most user-facing options. Per-driver dependencies ensure required subsystems are present, such as PCI, VDPA, LIBNVDIMM, BALLOON, PAGE_REPORTING, INPUT, HAS_IOMEM/HAS_DMA, DMA_SHARED_BUFFER, PTP clocks, ARM arch timer, and RTC class.

## State and persistence
State is build-time only in `.config`; selected symbols drive Makefile object inclusion and preprocessor conditionals. There is no runtime state.

## Dependencies and integration points
This file integrates virtio with kbuild, transport subsystems, memory hotplug, input, DMA-buf, debugfs, page reporting, and timekeeping/PTP/RTC options.

## Risks and test signals
Risks are missing dependencies, stale selects, options visible on unsupported architectures, and feature combinations that compile but cannot operate. Test signals include randconfig/allmodconfig builds, minimal configs for each transport, `VIRTIO_BALLOON` with page reporting, `VIRTIO_INPUT` without INPUT rejected, RTC suboption dependency checks, and legacy PCI enable/disable combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/virtio/Makefile

## Purpose
The virtio Makefile maps Kconfig symbols to compiled virtio core, transport, and device-driver objects.

## Important APIs, types, and functions
Important mappings include `CONFIG_VIRTIO -> virtio.o virtio_ring.o`, `CONFIG_VIRTIO_ANCHOR -> virtio_anchor.o`, `CONFIG_VIRTIO_PCI_LIB -> virtio_pci_modern_dev.o`, `CONFIG_VIRTIO_PCI_LIB_LEGACY -> virtio_pci_legacy_dev.o`, `CONFIG_VIRTIO_MMIO -> virtio_mmio.o`, `CONFIG_VIRTIO_PCI -> virtio_pci.o`, `CONFIG_VIRTIO_BALLOON -> virtio_balloon.o`, `CONFIG_VIRTIO_INPUT -> virtio_input.o`, `CONFIG_VIRTIO_VDPA -> virtio_vdpa.o`, `CONFIG_VIRTIO_MEM -> virtio_mem.o`, `CONFIG_VIRTIO_DMA_SHARED_BUFFER -> virtio_dma_buf.o`, `CONFIG_VIRTIO_DEBUG -> virtio_debug.o`, and `CONFIG_VIRTIO_RTC -> virtio_rtc.o`.

## Control flow
Kbuild evaluates the selected config values and builds objects either built-in or modular. Composite objects such as `virtio_pci-y` and `virtio_rtc-y` add feature-specific implementation files based on suboptions.

## State and persistence
Only build graph state exists. The resulting objects determine which runtime drivers and exported symbols are present.

## Dependencies and integration points
The file is synchronized with `drivers/virtio/Kconfig` and source filenames. It connects virtio bus core, rings, PCI/MMIO/vDPA transports, balloon, input, memory, dma-buf, debug, and RTC drivers to the kernel build.

## Risks and test signals
Risks include missing object mappings after Kconfig additions, stale filenames, composite object omissions, and building transport pieces without their required core. Test signals include per-symbol module and built-in builds, `make W=1`, checking module names against help text, and config combinations for PCI legacy/admin legacy and RTC subfeatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio.c

## Purpose
`virtio.c` implements the Linux virtio bus core. It registers the bus, matches virtio devices to virtio drivers, negotiates features, manages status transitions, exposes sysfs attributes, handles config-change delivery, registers/unregisters devices and drivers, and supports power-management freeze/restore and device reset prepare/done flows.

## Important APIs, types, and functions
Exported APIs include `__register_virtio_driver`, `unregister_virtio_driver`, `register_virtio_device`, `unregister_virtio_device`, `is_virtio_device`, `virtio_add_status`, `virtio_reset_device`, `virtio_config_changed`, `virtio_config_driver_disable`, `virtio_config_driver_enable`, `virtio_check_driver_offered_feature`, `virtio_device_freeze`, `virtio_device_restore`, `virtio_device_reset_prepare`, and `virtio_device_reset_done`. Important internal functions are `virtio_dev_probe`, `virtio_dev_remove`, `virtio_features_ok`, `virtio_device_restore_priv`, and `virtio_device_of_init`.

## Control flow
Core init registers the `virtio` bus and debugfs root. Device registration initializes `struct device`, assigns an `ida` index/name, optionally attaches a devicetree child, resets the device, acknowledges it, initializes debugfs, and calls `device_add`. Probe sets DRIVER status, intersects device and driver feature sets, applies debugfs feature filtering, preserves transport features, finalizes features, runs optional validation, sets FEATURES_OK for modern devices, calls driver probe, marks DRIVER_OK if needed, runs scan, and enables config callbacks.

## State and persistence
Runtime state lives in each `struct virtio_device`: feature arrays, status bits in transport config space, config callback flags, virtqueue list, OF node reference, debugfs directory, and assigned index. The global `virtio_index_ida` persists while the bus module is loaded.

## Dependencies and integration points
It depends on the driver core, virtio config/ring helpers, OF, IDA, debugfs hooks, status/feature UAPI definitions, and `virtio_anchor` restricted-memory callback. It is the central integration point for all virtio transports and device drivers.

## Risks and test signals
Risks include feature negotiation regressions, transport feature preservation, config-change races while drivers disable callbacks, status ordering around FAILED/DRIVER_OK, OF child reference leaks, reset/shutdown ordering while virtqueues are active, and restricted-memory requirements for confidential-computing transports. Test signals include virtio-pci/mmio/vdpa probe/remove, feature validation failures, debugfs feature filtering before probe, PM freeze/restore, reset_prepare/reset_done, shutdown with active queues, OF child matching, and sysfs/modalias checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_anchor.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_anchor.c

## Purpose
`virtio_anchor.c` provides a small anchor module and exported callback used to decide whether a virtio device must negotiate restricted memory access. It lets external code replace the global check while keeping a default no-restriction behavior.

## Important APIs, types, and functions
The exports are `virtio_require_restricted_mem_acc`, which always returns true, and `virtio_check_mem_acc_cb`, a function pointer initialized to `virtio_no_restricted_mem_acc`. `virtio.c` calls `virtio_check_mem_acc_cb` during feature validation.

## Control flow
By default, virtio feature validation does not require restricted memory access. If another subsystem assigns `virtio_check_mem_acc_cb` to a stricter callback, `virtio_features_ok` requires `VIRTIO_F_VERSION_1` and `VIRTIO_F_ACCESS_PLATFORM` for matching devices.

## State and persistence
The only state is the exported global callback pointer. It persists while the anchor object is loaded and affects all future virtio feature checks.

## Dependencies and integration points
The file depends on `linux/virtio.h` and `linux/virtio_anchor.h`. Its integration point is the virtio core feature negotiation path, especially platforms that require device DMA to go through restricted or translated memory access.

## Risks and test signals
Risks include unsynchronized callback replacement, global policy affecting unrelated devices, and failing legacy devices when a strict callback is installed. Test signals include booting with default callback, installing a restricted-memory callback, validating rejection of devices lacking `VERSION_1` or `ACCESS_PLATFORM`, and module dependency/load-order checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_anchor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_balloon.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_balloon.c

## Purpose
`virtio_balloon.c` implements the virtio memory balloon driver. It lets the host reclaim or return guest memory, reports memory statistics, supports free-page hinting and page reporting, handles OOM deflation, and participates in PM freeze/restore.

## Important APIs, types, and functions
The central type is `struct virtio_balloon`, holding virtqueues, work items, balloon page accounting, free-page hint state, stats, shrinker, OOM notifier, page-reporting device, locks, and wakeup state. Important functions include `virtballoon_probe`, `virtballoon_remove`, `virtballoon_changed`, `fill_balloon`, `leak_balloon`, `tell_host`, `update_balloon_size_func`, `stats_request`, `stats_handle_request`, `init_vqs`, `virtio_balloon_report_free_page`, `report_free_page_func`, `virtballoon_free_page_report`, `virtio_balloon_oom_notify`, `virtballoon_validate`, and PM `virtballoon_freeze`/`virtballoon_restore`.

## Control flow
Probe validates config access, allocates state, initializes work/locks, creates virtqueues based on negotiated features, registers optional shrinker/OOM/page-reporting hooks, sets page-poison config, marks the device ready, and schedules adjustment if the host target differs. Config changes queue freezable work that reads the target, inflates by allocating balloon pages and sending PFNs on the inflate queue, or deflates by dequeuing pages and sending PFNs on the deflate queue. Stats are host-request driven through a primed stats queue. Free-page hinting sends command IDs and page blocks on a dedicated queue; page reporting uses the generic page-reporting callback.

## State and persistence
State is runtime only: `num_pages`, `vb_dev_info` page list, PFN buffer, stats buffer, free-page list and command IDs, workqueue state, and negotiated feature hooks. Host-visible config fields include actual balloon size and page poison value. No storage persistence exists.

## Dependencies and integration points
It depends on virtio config/queues, balloon core, MM/page allocation, page reporting, OOM notifier, shrinker API, PM wakeup sources, and optional balloon migration. It integrates with host memory management and guest reclaim paths.

## Risks and test signals
Risks include deadlocks around `balloon_lock`, host notification ordering with `MUST_TELL_HOST`, stalled waits for virtqueue acknowledgements, races with removal/freeze via `stop_update`, free-page hint command ID transitions, shrinker accounting, OOM notifier side effects, page poisoning/reporting compatibility, and feature validation clearing `ACCESS_PLATFORM`. Test signals include target inflate/deflate loops, OOM deflation, stats queue requests, free-page hint start/stop/done, page reporting capacity checks, PM freeze/restore, migration of balloon pages, removal with nonzero balloon, and host feature combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_balloon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_debug.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_debug.c

## Purpose
`virtio_debug.c` exposes debugfs controls for observing device-advertised virtio features and filtering negotiated features before driver probe finalizes them.

## Important APIs, types, and functions
Exports are `virtio_debug_init`, `virtio_debug_exit`, `virtio_debug_device_init`, `virtio_debug_device_exit`, and `virtio_debug_device_filter_features`. Debugfs files per device are `device_features`, `filter_features`, `filter_features_clear`, `filter_feature_add`, and `filter_feature_del`.

## Control flow
Virtio core creates the root debugfs directory at bus init. Device registration creates a per-device directory and files. Before feature finalization in probe, `virtio_debug_device_filter_features` removes any bits present in `dev->debugfs_filter_features` from the negotiated feature array. Removing a device recursively removes its debugfs directory.

## State and persistence
The root `dentry` is global runtime state. Each device stores debugfs directory and filter feature bitmap in `struct virtio_device`. Debugfs state is not persistent and only matters before or during probe/reprobe.

## Dependencies and integration points
It depends on debugfs, seq_file helpers, virtio feature bitmap helpers, and virtio core. It is compiled only with `CONFIG_VIRTIO_DEBUG`.

## Risks and test signals
Risks include filtering mandatory transport/device features into invalid combinations, concurrent writes while probing, debugfs lifetime during unregister, and invalid feature numbers. Test signals include reading advertised features, adding/deleting/clearing filters, reprobe with a filtered feature, invalid large bit writes returning `-EINVAL`, and debugfs cleanup after device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_dma_buf.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_dma_buf.c

## Purpose
`virtio_dma_buf.c` provides helpers for dma-bufs that represent virtio exported objects. It enforces a virtio-specific dma-buf ops wrapper so other virtio drivers can identify such buffers and query their exported object UUID.

## Important APIs, types, and functions
Exported functions are `virtio_dma_buf_export`, `virtio_dma_buf_attach`, `is_virtio_dma_buf`, and `virtio_dma_buf_get_uuid`. The implementation expects `struct virtio_dma_buf_ops`, whose embedded `dma_buf_ops` must use `virtio_dma_buf_attach` as `attach` and provide `get_uuid`; optional `device_attach` is called from the mandatory attach wrapper.

## Control flow
Export validates the ops shape and UUID callback before calling `dma_buf_export`. Attach recovers the virtio ops wrapper and delegates to optional device-specific attach logic. Type checking is implemented by comparing the dma-buf attach op pointer. UUID lookup first verifies the buffer is virtio-backed, then calls the ops `get_uuid`.

## State and persistence
This file owns no global state. State resides in the dma-buf object and exporter-provided private data/ops. UUID identity persists only as long as the dma-buf and underlying virtio object exist.

## Dependencies and integration points
It depends on the dma-buf framework and `linux/virtio_dma_buf.h`, imports the `DMA_BUF` namespace, and is intended for virtio devices such as GPU or media exporters/importers that need cross-device object identity.

## Risks and test signals
Risks include ops pointer spoofing assumptions, exporters bypassing the required attach wrapper, missing `get_uuid`, attach callback failures, and UUID lifetime mismatches with the underlying object. Test signals include valid export/import, invalid ops rejection, `is_virtio_dma_buf` on normal dma-bufs, UUID retrieval, optional `device_attach` failure propagation, and module namespace/build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_dma_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_input.c -->
# sources/distributed-fs/ceph-client/drivers/virtio/virtio_input.c

## Purpose
`virtio_input.c` implements the virtio input device driver. It maps a virtio input device into the Linux input subsystem, receives input events from the host, sends status events such as LED/sound updates back to the host, and supports suspend/resume.

## Important APIs, types, and functions
The main state is `struct virtio_input`, containing the virtio device, input device, identity strings, event and status virtqueues, a fixed event-buffer array, lock, and ready flag. Important functions are `virtinput_probe`, `virtinput_remove`, `virtinput_init_vqs`, `virtinput_fill_evt`, `virtinput_recv_events`, `virtinput_send_status`, `virtinput_recv_status`, `virtinput_status`, `virtinput_cfg_select`, `virtinput_cfg_bits`, `virtinput_cfg_abs`, and PM `virtinput_freeze`/`virtinput_restore`.

## Control flow
Probe requires modern virtio, allocates state, creates event/status queues, allocates an input device, reads name/serial/device IDs/properties/event bitmaps/absolute axis metadata from config space, initializes multitouch slots when advertised, marks the virtio device ready, registers the input device, and fills the event queue. Event callbacks drain host-provided event buffers, emit Linux `input_event` calls, recycle buffers, and kick the queue. Input core status callbacks allocate one status event, queue it to the host, and free it when the status queue completes.

## State and persistence
Runtime state includes config-derived input capabilities, queued event buffers, heap-allocated status buffers awaiting completion, and the `ready` flag protecting queue use during remove/freeze. No persistent state exists.

## Dependencies and integration points
It depends on virtio config/queues, Linux input and multitouch helpers, DMA cache-clean queue helper for device-written event buffers, and virtio input UAPI structures. It integrates host virtual keyboards, mice, tablets, and touch devices with evdev.

## Risks and test signals
Risks include malformed config bitmaps/axis sizes, event queue starvation, status buffer leaks on reset, races around `ready`, forwarding `MSC_TIMESTAMP` loops for multitouch, restore without re-registering capabilities, and host devices lacking `VIRTIO_F_VERSION_1`. Test signals include keyboard/mouse/tablet event streams, LED status updates, multitouch with timestamp filtering, config fuzzing, suspend/resume, remove with outstanding status buffers, and queue size larger than the fixed 64-event buffer pool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_input.c -->
