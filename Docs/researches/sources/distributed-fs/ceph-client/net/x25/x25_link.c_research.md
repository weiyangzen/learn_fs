# sources/distributed-fs/ceph-client/net/x25/x25_link.c

Purpose: manages X.25 neighbours and link-level restart/control behavior for X.25 netdevices.

Important APIs/functions: `x25_link_control()`, `x25_transmit_link()`, `x25_link_established()`, `x25_link_terminated()`, `x25_link_device_up()`, `x25_link_device_down()`, `x25_get_neigh()`, `x25_subscr_ioctl()`, and `x25_link_free()` are the main surfaces.

Control flow: neighbour creation initializes link queue, T20 timer, default facility mask, standard sequencing, and device reference. `x25_transmit_link()` queues frames while link state is down/restarting and starts lower-layer establishment; link establishment sends restart request and starts T20; restart confirmations transition to state 3 and flush queued frames; restart requests in established state kill existing virtual calls and reply. Link termination purges queued frames, stops T20, and kills dependent sockets.

State and persistence: global `x25_neigh_list` is protected by `x25_neigh_list_lock`; each neighbour stores device reference, link state, queue, extended-mode flag, global facility mask, T20, timer, and refcount.

Dependencies and integration: integrates netdevice notifier callbacks from `af_x25.c`, device transmit helpers in `x25_dev.c`, socket cleanup via `x25_kill_by_neigh()`, subscriptions ioctls, and sysctl default T20.

Risks and test signals: link state and refcounting interact with device unregister. Tests should cover device up/down, duplicate device registration assumptions, restart request/confirmation state transitions, T20 retransmission, queued-frame flushing, subscription get/set including extended flag validation, and teardown with active sockets/routes/forwards.
