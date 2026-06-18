<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/protocol.h -->
# sources/distributed-fs/ceph-client/net/9p/protocol.h

This internal header declares the protocol marshalling helpers used by `client.c` and implemented in `protocol.c`. It exposes buffer sizing, formatted PDU read/write, PDU header prepare/finalize/reset, and raw `pdu_read()`.

No state is defined here. The header is an integration contract between the 9P client RPC layer and the wire-format implementation. Callers must pass format strings and arguments that match the expectations in `protocol.c`, and must respect allocation ownership for parsed strings, stats, qid arrays, and data pointers.

Risks are mostly API misuse: wrong format strings can trigger `BUG()` or produce invalid wire data, and returned data blob pointers are only valid while the fcall buffer remains alive. Tests should compile all users and exercise format helpers through client operations rather than treating the declarations as independent logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/protocol.h -->
