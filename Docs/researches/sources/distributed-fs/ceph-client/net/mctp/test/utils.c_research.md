# sources/distributed-fs/ceph-client/net/mctp/test/utils.c

Purpose: shared KUnit infrastructure for MCTP route and socket tests, creating synthetic netdevices, routes, destinations, skbs, and bind scenarios.

Important APIs and functions: `mctp_test_create_dev*()` register ARPHRD_MCTP netdevices and retrieve `mctp_dev`. `mctp_test_destroy_dev()` unregisters and frees queued packets. `mctp_test_create_route_direct/gw()` insert test routes. `mctp_test_dst_setup()` builds a referenced `mctp_dst`. `mctp_test_create_skb*()` build packets. `mctp_test_bind_run()` creates sockets, optional connects, and binds.

Control flow and state: test netdev transmit queues outgoing skbs to `dev->pkts`. Routes are inserted directly into `net->mctp.routes` with test output that calls `dev_direct_xmit()`. Device setup can assign local EIDs and link-layer addresses. Destroy helpers assert route ref balance.

Dependencies and integration: used by both KUnit suites; relies on real MCTP device notifier registration, netdevice registration, RTNL, KUnit assertions, and init-net state.

Risks and test signals: helpers manipulate global route lists directly and require disciplined cleanup. They are not production code, but failures often indicate lifetime/refcount regressions in MCTP core.
