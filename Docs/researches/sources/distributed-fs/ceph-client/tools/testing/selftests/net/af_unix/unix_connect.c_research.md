# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/unix_connect.c

Purpose: Tests AF_UNIX connect visibility across network namespace changes for pathname and abstract socket addresses.

Important APIs/types/functions: Uses `socket()`, `bind()`, `listen()`, `connect()`, `unshare(CLONE_NEWNET)`, `struct sockaddr_un`, pathname and abstract `sun_path`, and kselftest fixture variants.

Control flow: The server is bound in the original namespace. The test optionally unshares the network namespace before creating the client, then attempts to connect to the previously bound address. Pathname sockets are expected to remain reachable across netns because the filesystem path is shared, while abstract sockets in a new netns are expected to fail with `ECONNREFUSED`.

State and persistence behavior: Tracks server/client fds and removes the pathname socket file `test` in teardown. Abstract socket names are namespace-local and not persisted.

Dependencies and integration points: Requires AF_UNIX, network namespace support, and permissions to unshare.

Risks: Relative pathname `test` can collide if the test is run concurrently in the same directory. Abstract namespace behavior depends on network namespace isolation.

Test signals: Passing variants confirm expected connect behavior for stream/datagram, pathname/abstract, and same-netns/new-netns combinations.
