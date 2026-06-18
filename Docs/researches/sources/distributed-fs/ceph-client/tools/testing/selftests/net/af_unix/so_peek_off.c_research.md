# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/so_peek_off.c

Purpose: Verifies `SO_PEEK_OFF` offset advancement and reset semantics for AF_UNIX stream, datagram, and seqpacket sockets, including blocking receive paths.

Important APIs/types/functions: Uses `SO_PEEK_OFF`, `SO_RCVTIMEO_NEW`, `MSG_PEEK`, `socketpair()`, fork-based async send helper, and kselftest macros wrapping send/recv/getsockopt assertions.

Control flow: Fixture creates a socketpair for each type, sets a receive timeout, and initializes peek offset to zero. Tests send one or two chunks, perform peek reads to advance the offset, verify offset values, consume real data to reset or advance the offset, and use forked delayed sends to exercise blocking paths inside AF_UNIX receive logic.

State and persistence behavior: Only two socket fds. Kernel receive queues and the socket peek offset are the state under test. Child processes exit immediately after delayed sends.

Dependencies and integration points: Requires AF_UNIX `SO_PEEK_OFF` support and recent socket timeout option definitions.

Risks: The `async` macro forks inside tests and can complicate failure reporting. Timing uses `usleep(1000)` plus a 5-second receive timeout, so severe scheduling delays can stretch runtime. Stream and datagram/seqpacket expectations intentionally differ at skb boundaries.

Test signals: Passing cases prove peek offset increments across chunks, blocking receives resume correctly, stream reads fill buffers when possible, datagram/seqpacket preserve skb/message boundaries, and non-peek reads reset offset to zero.
