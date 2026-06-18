# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_iucv.c

## Purpose
`hvc_iucv.c` implements a z/VM IUCV-backed HVC terminal driver. It exposes one or more HVC tty lines whose remote peers connect over IUCV paths, supports a first line as the Linux console, filters connection requests by z/VM user ID, and translates IUCV messages into HVC get/put operations.

## Important APIs, Types, and Functions
Important types are `struct iucv_tty_msg`, `enum iucv_state_t`, `enum tty_state_t`, `struct hvc_iucv_private`, and `struct iucv_tty_buffer`. `hvc_iucv_private` owns the HVC pointer, service name, IUCV path state, tty state, send buffer, delayed send work, waitqueue, input/output queues, sysfs device, and peer info.

The HVC ops are `hvc_iucv_get_chars()`, `hvc_iucv_put_chars()`, `hvc_iucv_notifier_add()`, `hvc_iucv_notifier_del()`, `hvc_iucv_notifier_hangup()`, and `hvc_iucv_dtr_rts()`. IUCV callbacks are `hvc_iucv_path_pending()`, `hvc_iucv_path_severed()`, `hvc_iucv_msg_pending()`, and `hvc_iucv_msg_complete()`.

## Control Flow
`hvc_iucv_init()` validates z/VM availability and the `hvc_iucv=` device count, builds the optional allow filter, creates a slab cache and mempool, instantiates console slot 0, allocates each HVC/IUCV line, and registers the IUCV handler. Incoming path requests are matched by service name or wildcard `lnxhvc  `, filtered by VMID, accepted with the IUCV handler, and associated with a disconnected line.

Input messages are queued in `tty_inqueue` by `hvc_iucv_msg_pending()` only when the tty is open. `hvc_iucv_get_chars()` receives message bodies lazily, validates message version/length, copies DATA payload to HVC, applies WINSIZE via `__hvc_resize()`, and schedules another HVC pass when partial data remains. Output is accumulated in `sndbuf` by `hvc_iucv_put_chars()`, then delayed work sends it as an IUCV message and tracks completion in `tty_outqueue`.

## State and Persistence Behavior
The driver keeps global `hvc_iucv_devices`, `hvc_iucv_table[]`, filter state protected by `hvc_iucv_filter_lock`, a slab cache, and a mempool. Each line transitions among `IUCV_DISCONN`, `IUCV_CONNECTED`, and `IUCV_SEVERED`, and between `TTY_CLOSED` and `TTY_OPENED`. No state is persisted beyond module parameters and sysfs views.

## Dependencies and Integration Points
It integrates with the HVC core, z/VM IUCV networking APIs, EBCDIC/ASCII conversion, Linux device attributes, mempools, delayed work, waitqueues, and module/core parameters. Sysfs exposes `termid`, `state`, and `peer`; `hvc_iucv_allow` configures the VMID allow-list.

## Risks and Edge Cases
Path sever is intentionally two-stage: `hvc_iucv_hangup()` sets `IUCV_SEVERED`, then `get_chars()` returns `-EPIPE` so the HVC core performs tty hangup. Console lines are special because console hangups may not call normal HVC notifier cleanup. Buffer allocation uses `GFP_DMA` and mempool elements to satisfy IUCV constraints. Incorrect filter parsing can deny remote access, and oversized or malformed messages are rejected or dropped.

## Test Signals
Signals include successful creation of `hvc_iucvN` devices, VMID filter accept/reject behavior, wildcard and explicit service-name connection, data and winsize message handling, send completion waking `sndbuf_waitq`, DTR/RTS disconnect via `HUPCL`, and `-EPIPE` hangups after remote path sever.
