# sources/distributed-fs/ceph-client/net/mctp/test/sock-test.c

Purpose: KUnit suite for AF_MCTP socket behavior, compiled into `af_mctp.c` to reach static socket functions.

Important tests and helpers: `mctp_test_sock_sendmsg_extaddr()` stubs `mctp_local_output()` and verifies direct hardware addressing from `sockaddr_mctp_ext`. `mctp_test_sock_recvmsg_extaddr()` verifies extended receive sockaddr metadata. Parameterized bind tests assert conflict rules across local address, network, type, and connected peer. `mctp_test_bind_invalid()` checks bind/connect network mismatch.

Control flow and state: tests create kernel sockets, configure test devices/routes, manipulate `mctp_sock.addr_ext`, call `mctp_sendmsg()`/`mctp_recvmsg()` or `kernel_bind()`, and assert returned lengths/errors and socket address fields.

Dependencies and integration: included from `af_mctp.c` under `CONFIG_MCTP_TEST`; uses `utils.c`, KUnit static stubs, kernel socket APIs, and init-net default network.

Risks and test signals: bind tests rely on cleanup through `sock_release()` and default net being 1. They provide direct coverage for user-visible socket ABI validation and conflict behavior.
