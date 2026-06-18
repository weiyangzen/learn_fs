# sources/distributed-fs/lizardfs/utils/mfs_pingserv.cc

Purpose: simple LizardFS ping responder for use with `mfs_ping.cc`.

Important APIs/functions: opens a TCP listener on the requested port with `tcpsocket`, `tcpnodelay`, `tcpreuseaddr`, and `tcpstrlisten`. It parses 12-byte ping requests with `deserialize()` and emits replies with `serialize()`.

Control flow: accepts one client at a time. For each client, it reads exactly 12 bytes, expects `ANTOAN_PING` with 4-byte request payload length field, bounds requested reply payload below 2,000,000 bytes, builds an `ANTOAN_PING_REPLY` header, resizes the buffer to include zero-filled payload, and writes it. Read or write failure closes the client and returns to accept.

State and persistence: no persistence. Maintains per-client request/reply vectors and logs accepted connections to stderr.

Dependencies/integration: depends on LizardFS protocol and socket helpers. It is a benchmark/test peer, not production service code.

Risks and test signals: single-threaded accept loop can serve only one client at a time. Assertions abort on malformed input instead of returning protocol errors. Test signals are exact ping/reply framing, size bound enforcement, client disconnect handling, and repeated requests over one connection.
