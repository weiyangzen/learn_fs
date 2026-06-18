# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_ib.c

## Purpose
`ipoib_ib.c` owns the default datagram-mode RDMA datapath and device event flushing. It creates/destroys address handles, posts UD receives and sends, maps/unmaps DMA, handles send/receive CQ completions through NAPI, opens/stops the IB datapath, drains CQs during teardown, reacts to P_Key/GID/LID/port events, and cleans verbs resources.

## Important APIs, Types, And Functions
Address-handle lifecycle is `ipoib_create_ah()`, `ipoib_free_ah()`, `ipoib_reap_ah()`, and reaper helpers. RX uses `ipoib_alloc_rx_skb()`, `ipoib_ib_post_receive()`, `ipoib_ib_post_receives()`, and `ipoib_ib_handle_rx_wc()`. TX uses shared `ipoib_dma_map_tx()`, `ipoib_dma_unmap_tx()`, `ipoib_send()`, `ipoib_ib_handle_tx_wc()`, and `ipoib_qp_state_validate_work()`. CQ entry points are `ipoib_rx_poll()`, `ipoib_tx_poll()`, `ipoib_ib_rx_completion()`, and `ipoib_ib_tx_completion()`. Lifecycle functions include `ipoib_ib_dev_open_default()`, `ipoib_ib_dev_stop_default()`, `ipoib_ib_dev_open()`, `ipoib_ib_dev_stop()`, `ipoib_ib_dev_up()`, `ipoib_ib_dev_down()`, `ipoib_drain_cq()`, `ipoib_queue_work()`, and `ipoib_ib_dev_cleanup()`.

## Control Flow And State
Open checks P_Key presence, starts the AH reaper, initializes the QP, posts receives, opens CM listening if available, enables NAPI, marks initialized, and starts multicast joining. RX completions validate WR IDs/status, replace receive buffers before passing packets up, classify host/broadcast/multicast from GRH DGID, drop multicast loopback from the same QP/LID when appropriate, set checksum state if supported, and deliver through GRO. TX validates GSO, MTU, fragment count, DMA maps the skb, posts either UD SEND or LSO, updates `tx_head`/`global_tx_head`, and uses CQ notifications plus NAPI to reopen stopped queues.

Stop disables NAPI, stops CM, moves the QP to error, drains CQ completions as flush errors, waits up to five seconds for sends/receives, force-frees if hardware is wedged, resets the QP, and re-arms the receive CQ. Flush work has three levels: light invalidates paths and multicast state, normal downs/ups the IB device, and heavy also refreshes P_Key state and restarts QPs. Parent flushes recurse into child interfaces.

## Dependencies And Integration Points
The file integrates with RDMA verbs (`ib_post_recv`, `ib_post_send`, QP/CQ/DMA APIs), netdevice/NAPI/queue APIs, multicast/path/neighbour functions from `ipoib_main.c` and `ipoib_multicast.c`, CM dispatch from `ipoib_cm.c`, and lower-level `rdma_netdev` operations through `priv->rn_ops`. `ipoib_event()` is registered from `ipoib_main.c` and converts RDMA events into flush work.

## Risks And Test Signals
Key risks are CQ drain and teardown races, queue accounting under both UD and CM, DMA unmap correctness on partial failures, AH destruction after last send, multicast loopback filtering, and P_Key/GID change handling while devices are up or down. Test signals include RX/TX under stress, GSO and checksum offload paths, queue stop/wake transitions, TX timeout recovery, port active/error/LID/P_Key/GID events, child interface flush propagation, and simulated CQ/QP errors.
