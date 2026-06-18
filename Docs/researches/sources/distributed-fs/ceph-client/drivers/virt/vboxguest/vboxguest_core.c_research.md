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
