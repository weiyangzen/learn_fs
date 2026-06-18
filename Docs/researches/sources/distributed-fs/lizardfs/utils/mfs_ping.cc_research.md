# sources/distributed-fs/lizardfs/utils/mfs_ping.cc

Purpose: simple network benchmark client that sends LizardFS/MooseFS `ANTOAN_PING` packets and measures round-trip latency.

Important APIs/functions: uses `tcpresolve`, `tcpsocket`, `tcpnodelay`, `tcpnumconnect`, `tcptowrite`, and `tcptoread` from LizardFS socket helpers. `serializeMooseFsPacket()` builds the ping packet with requested payload size.

Control flow: requires `host port bytes count usleep`. It resolves/connects, constructs one ping message, allocates a reply buffer of payload size plus 8-byte header, then loops `count` times measuring time around write/read with `gettimeofday()`. It prints each latency and an average.

State and persistence: no persistent state. Uses one TCP connection and in-memory buffers.

Dependencies/integration: integrates with `mfs_pingserv.cc` or any endpoint that responds with `ANTOAN_PING_REPLY` of matching size. It depends on protocol constants and serialization helpers.

Risks and test signals: `atoi` lacks robust range checking; `sassert(std::to_string(size) == argv[3])` rejects noncanonical numbers but not all invalid inputs gracefully. `count == 0` would divide by zero. Test signals are payload sizes including zero and large values, timeout behavior, average calculation, and interoperation with ping server.
