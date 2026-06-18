# sources/distributed-fs/ceph-client/drivers/net/can/slcan/slcan-core.c

Purpose: SocketCAN tty line discipline for SLCAN ASCII protocol. It creates a CAN netdev per attached tty, converts ASCII SLCAN frames/errors/states to `struct can_frame`/error skbs, converts outgoing CAN frames to ASCII, and sends setup commands to the adapter on open.

Important APIs/types/functions: `struct slcan` embeds `can_priv`, tty/netdev pointers, spinlock, TX work, RX/TX buffers, parser counters, command flags, and command waitqueue. `slcan_open()`/`slcan_close()` are line discipline lifecycle hooks. `slcan_receive_buf()` receives tty bytes; `slcan_unesc()` frames packets; `slcan_bump_frame()`, `slcan_bump_err()`, and `slcan_bump_state()` decode SLCAN messages. Netdev ops are `slcan_netdev_open()`, `slcan_netdev_close()`, and `slcan_netdev_xmit()`. `slcan_transmit_cmd()` synchronously sends adapter commands. Exported-to-compilation-unit helpers support ethtool private flag `err-rst-on-open`.

Control flow: ldisc open requires `CAP_NET_ADMIN`, allocates/registers a CAN netdev, initializes buffers/workqueue, assigns tty `disc_data`, and exposes ethtool ops. Netdev open fakes `CAN_BITRATE_UNKNOWN` if userspace did not request a bitrate, otherwise sends `C`, `S<n>`, optional `F`, and `L` or `O` commands. RX bytes accumulate until CR or BEL, then dispatch based on first byte. TX netdev path stops the queue, encodes one frame into `xbuff`, writes to tty, and relies on write wakeup/workqueue to drain the remainder and wake the queue. Close sends `C` when configured, flushes work, resets counters, and closes CAN state.

State and persistence: all state is per ldisc/netdev lifetime. `rbuff` and `rcount` hold partial input; `xbuff`, `xhead`, and `xleft` hold partial output or command; `SLF_ERROR` drops malformed overlong/tty-error packets until delimiter; `SLF_XCMD` tracks synchronous command completion; `CF_ERR_RST` persists as a private flag while the netdev exists. No disk persistence.

Dependencies/integration: tty line discipline `N_SLCAN`, SocketCAN core, rtnetlink/netdevice lifecycle, ethtool ops in `slcan-ethtool.c`, and userspace tools that set line discipline and CAN bitrate.

Risks: parser mutates `rbuff` to NUL-terminate ID/counter fields, so malformed messages must be carefully bounded by `SLCAN_MTU`. Command completion uses tty write wakeups and a one-second timeout; adapters that do not drain promptly fail open. `receive_buf` ignores input while the netdev is down. Only classic CAN length 0..8 is supported. Locking spans tty pointer and TX state, but ldisc close must flush work before freeing.

Test signals: attach ldisc to pty/serial, open netdev with supported bitrates, verify emitted command strings, inject SFF/EFF/RTR/error/state messages, test malformed hex and overlong input, verify ethtool private flag cannot change while running, and exercise close/hangup with pending TX work.
