# sources/distributed-fs/ceph-client/net/bluetooth/bnep/core.c

## Purpose
This file implements the BNEP session engine: PAN session creation/deletion, packet header compression/decompression, BNEP control handling, optional filters, the per-session kernel thread, and module init/exit.

## Important APIs, Types, And Functions
Public functions are `bnep_add_connection()`, `bnep_del_connection()`, `bnep_get_connlist()`, and `bnep_get_conninfo()`. Internal core functions include `bnep_rx_frame()`, `bnep_tx_frame()`, `bnep_rx_control()`, `bnep_rx_extension()`, `bnep_ctrl_set_netfilter()`, `bnep_ctrl_set_mcfilter()`, `bnep_session()`, session list helpers, and `bnep_send_rsp()`. Module parameters `compress_src` and `compress_dst` control transmit header compression.

## Control Flow
Adding a connection validates the socket is L2CAP and connected, derives local/remote Ethernet addresses from L2CAP addresses, allocates a net_device with `bnep_session` private data, registers it, links the session under `bnep_session_sem`, pins the module, and starts `kbnepd`. The session thread drains the socket receive queue into `bnep_rx_frame()`, drains the socket write queue into `bnep_tx_frame()`, wakes the netdev queue, and sleeps on the socket waitqueue until termination or disconnect. RX validates BNEP type, handles control frames, parses extensions, decompresses Ethernet headers, strips VLAN tag metadata when needed, builds an aligned Ethernet skb, and injects it via `netif_rx()`. TX chooses compressed header type based on cached peer addresses, sends via `kernel_sendmsg()`, updates stats, and frees the skb. Deleting a connection sets `terminate` and wakes the thread; thread cleanup unregisters the netdev, signals socket error, releases the socket file, unlinks the session, frees the netdev, and exits with module put.

## State, Persistence, And Dependencies
The global `bnep_session_list` is protected by `bnep_session_sem`. Each session persists while its kernel thread and netdev are alive and owns a referenced userspace-provided L2CAP socket file. Optional filter state lives in `proto_filter` and `mc_filter`. State is runtime-only and disappears on session teardown or module unload.

## Integration Points
The file integrates with L2CAP sockets, virtual Ethernet netdev setup from `netdev.c`, user ioctls from `sock.c`, the Bluetooth core module alias `bt-proto-4`, and BlueZ PAN setup. It uses `register_netdev()`, socket queues, kernel threads, `kernel_sendmsg()`, and Ethernet helpers.

## Risks
BNEP parsing is byte-sensitive and must reject truncated frames; several branches rely on `skb_pull()`/`skb_pull_data()` checks to avoid overruns. The session thread owns cleanup, so failed kthread creation and unregister paths must avoid double-freeing the netdev. User-supplied socket FDs are held until thread cleanup; error paths must `sockfd_put()` in `sock.c` or `fput()` in the thread. Filter parsing accepts ranges and can be CPU-heavy for large multicast ranges, bounded by filter limits and a 64-bit hash saturation check.

## Test Signals
Signals include creating a `bnep%d` netdev from a connected L2CAP socket, duplicate destination rejection, Ethernet frames passing both directions, compressed and uncompressed header formats decoding correctly, control filter requests producing expected responses, connection list/info ioctls reflecting state, and teardown releasing socket/netdev/module refs under disconnect and module unload.
