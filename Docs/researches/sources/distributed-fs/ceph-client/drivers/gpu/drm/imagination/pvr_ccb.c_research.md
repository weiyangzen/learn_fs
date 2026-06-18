# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_ccb.c

Purpose: implements PowerVR firmware command-control buffers: KCCB for kernel-to-firmware commands and FWCCB for firmware-to-host events, including slot reservation, completion waiting, fences, and wakeup handling.

Important APIs/functions: `pvr_kccb_init()`/`pvr_kccb_fini()` initialize/cleanup the KCCB. `pvr_fwccb_init()` initializes the FWCCB. `pvr_fwccb_process()` consumes firmware commands and dispatches restart, free-list reconstruction/grow, stats, and context-reset notifications. `pvr_kccb_send_cmd()`, `_powered()`, and `_reserved_powered()` submit commands with appropriate PM/slot assumptions. `pvr_kccb_reserve_slot()`, `pvr_kccb_release_slot()`, and `pvr_kccb_wake_up_waiters()` manage async reservation fences. `pvr_kccb_wait_for_completion()` waits for return-slot execution.

Control flow and state: `pvr_ccb_init()` allocates uncached firmware objects for control and command rings, sets wrap masks and command sizes, and records firmware addresses. KCCB capacity is one less than slot count to distinguish full from empty. Reservation state combines firmware read/write offsets with `reserved_count`. Command send copies into the ring, clears return status if a slot is tracked, issues a memory barrier, updates write offset, decrements reservation count, and kicks MTS. FWCCB processing drops the FWCCB lock while handling each command.

Dependencies and integration: depends on firmware object mapping, PowerVR firmware ABI structs, runtime PM, free-list management, reset/power code, dump logging, dma_fence, waitqueues, and workqueue/IRQ paths.

Risks: ring offsets and `reserved_count` must remain consistent or KCCB can deadlock. Missing barriers could let firmware see incomplete commands. Waiter fences must be put exactly once. Unknown FWCCB commands are logged but ignored.

Test signals: interrupt processing should wake KCCB waiters, command return slots should transition from `NO_RESPONSE` to executed, and KCCB idle/reservation accounting should not warn under stress.
