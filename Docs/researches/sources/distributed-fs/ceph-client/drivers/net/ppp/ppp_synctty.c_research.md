# sources/distributed-fs/ceph-client/drivers/net/ppp/ppp_synctty.c

Purpose: Implements the synchronous PPP tty line discipline `N_SYNC_PPP` for frame-oriented tty devices such as synchronous HDLC adapters. It exchanges complete PPP frames without async byte stuffing or FCS handling.

Important APIs, types, and functions: `struct syncppp` stores tty state, flags, MRU, nominal async maps for ioctl compatibility, locks, current TX SKB, receive queue, tasklet, refcount/completion, and embedded `ppp_channel`. TTY callbacks are `ppp_sync_open()`, `ppp_sync_close()`, hangup/read/write/ioctl, `ppp_sync_receive()`, and `ppp_sync_wakeup()`. Channel ops are `ppp_sync_send()` and `ppp_sync_ioctl()`. Data helpers are `ppp_sync_txmunge()`, `ppp_sync_push()`, `ppp_sync_flush_output()`, and `ppp_sync_input()`.

Control flow: Module init registers `pppsync`. Open allocates state, registers a PPP channel with two bytes of header room, and stores it in `tty->disc_data`. TX accepts one pending frame, applies protocol-field compression and address/control insertion unless LCP rules forbid it, then writes the whole SKB to tty, retrying on wakeup. RX treats each callback as a complete frame, checks optional frame error flag, enforces MRU/tailroom, strips address/control when present, validates protocol length, queues the SKB, and tasklet-delivers it to `ppp_input()` or `ppp_input_error()`.

State and persistence behavior: Per-tty state persists until line discipline close. `tpkt` stores a full pending frame under backpressure; `rqueue` stores received frames or zero-length error markers. Refcount/completion and `disc_data_lock` protect close against concurrent callbacks. No durable state exists.

Dependencies and integration points: Depends on tty ldisc APIs, SKBs, tasklets, spinlocks, completions/refcounts, PPP ioctls, unaligned helpers, and generic PPP channel APIs. It exposes `MODULE_ALIAS_LDISC(N_SYNC_PPP)`.

Risks and test signals: Frame boundaries rely on lower tty behavior and partial writes must preserve the SKB until fully sent. Error signaling uses zero-length SKBs. Async-map ioctls exist only for userspace compatibility. The checked-out source has an extra brace in `ppp_sync_read()`, so compile validation is required. Test open/close races, full-frame receive, address/control stripping, invalid short frames, MRU overflow, error flags, PFC, LCP bypass, partial writes/wakeups, TCFLSH, ioctls, and unload with active channels.
