# sources/distributed-fs/ceph-client/net/mctp/test/utils.h

Purpose: declares shared MCTP KUnit test fixtures, constants, setup descriptors, and helper APIs.

Important types and APIs: `MCTP_DEV_TEST_MTU`, `struct mctp_test_dev`, `struct mctp_test_route`, and `struct mctp_test_bind_setup` describe test devices/routes/binds. Function declarations cover device creation/destruction, route creation/destruction, destination setup, skb creation, skb device tagging, and bind execution.

Control flow and state: the header defines the common state contract used by `route-test.c` and `sock-test.c`; test devices hold a real `net_device`, referenced `mctp_dev`, optional lladdr, and TX skb queue.

Dependencies and integration: includes MCTP core/device headers and KUnit. It is test-only and compiled with `CONFIG_MCTP_TEST`.

Risks and test signals: helper contracts must match production struct visibility. Changes to `mctp_route`, `mctp_dst`, or socket bind semantics often require synchronized test utility updates.
