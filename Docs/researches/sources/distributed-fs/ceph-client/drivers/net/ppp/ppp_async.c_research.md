# sources/distributed-fs/ceph-client/drivers/net/ppp/ppp_async.c

Purpose: Implements the asynchronous PPP tty line discipline `N_PPP`, framing PPP packets over byte-stream serial lines with flags, octet escaping, FCS, ACCM maps, and PPP protocol/address-control compression.

Important APIs, types, and functions: `struct asyncppp` stores tty state, PPP flags, MRU, ACCM maps, TX/RX locks, current TX/RX SKBs, FCS, output buffer, receive queue, tasklet, refcount/completion, and embedded `ppp_channel`. TTY lifecycle is handled by `ppp_asynctty_open()`, `ppp_asynctty_close()`, and hangup/read/write/ioctl/receive/wakeup callbacks. Channel ops are `ppp_async_send()` and `ppp_async_ioctl()`. Framing and parsing live in `ppp_async_encode()`, `ppp_async_push()`, `ppp_async_input()`, `process_input_packet()`, and `async_lcp_peek()`.

Control flow: Module init registers the line discipline. Opening a tty allocates state, registers a PPP channel, and stores it in `tty->disc_data`. Received bytes are decoded under `recv_lock`, complete/error frames are queued, and a tasklet calls `ppp_input()` or `ppp_input_error()`. Outbound frames arrive from generic PPP, one pending `tpkt` is accepted, encoded into a staging buffer, and written to tty until backpressure requires a later write wakeup. LCP Configure-Request/Ack packets are sent as if options were not negotiated and are peeked to update MRU/ACCM early.

State and persistence behavior: State lasts for the tty line discipline lifetime. Partial escaped input, partial output position/FCS, `xaccm`, `raccm`, MRU, flags, and queued SKBs persist across callbacks. `disc_data_lock` plus refcount/completion prevents close from freeing active state.

Dependencies and integration points: Depends on tty line discipline APIs, CRC-CCITT, SKBs, tasklets, PPP ioctls, spinlocks, and generic PPP channel APIs. It exposes `MODULE_ALIAS_LDISC(N_PPP)` and delegates unit attachment and packet routing to `ppp_generic.c`.

Risks and test signals: Edge cases include escapes split across callbacks, bad FCS, MRU overflow, tty error flags, XON/XOFF handling, LCP bypass rules, write recursion/backpressure, and close racing receive/wakeup. The source snapshot has a duplicated `static ssize_t` line, so compile validation is required. Test pppd over pty/serial, ACCM/MRU ioctls, escaped data, FCS errors, overflow, wakeups, close races, LCP peeking, and module unload.
