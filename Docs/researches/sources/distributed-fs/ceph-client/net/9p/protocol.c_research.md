<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/protocol.c -->
# sources/distributed-fs/ceph-client/net/9p/protocol.c

This file implements 9P wire-format sizing, marshalling, unmarshalling, and helpers for stat and directory-entry parsing. It is shared by the client RPC layer and filesystem consumers.

`p9_msg_buf_size()` estimates request/response buffer sizes from message type, protocol version, and the same format template used for marshalling. It special-cases variable-size messages such as attach, walk, create, read, write, renameat, symlink, and error responses; small messages default to 4 KiB or 8 KiB. `pdu_read()`, `pdu_write()`, and `pdu_write_u()` operate on `struct p9_fcall` buffers and return the number of bytes not copied.

The format engine is `p9pdu_vreadf()` and `p9pdu_vwritef()`. Format letters encode integers, strings, qids, stats, data blobs, arrays of names/qids, 9P2000.L stat/iattr structures, iterator-backed data, and optional 9P2000.u/L fields via `?`. Reads allocate strings and arrays where needed and free partially parsed structures on failure. Writes convert to little-endian wire values and clamp strings to `USHRT_MAX`.

`p9pdu_prepare()` writes a placeholder header, `p9pdu_finalize()` rewrites the final size and traces the PDU, and `p9pdu_reset()` clears offsets. `p9stat_read()` and `p9dirent_read()` parse standalone stat and dirent records from buffers; `p9dirent_read()` copies the allocated name into a fixed destination and rejects overlong names.

State is transient in fcall offsets, sizes, capacities, and allocated parse results. Dependencies include 9P message constants, user namespace uid/gid conversion, iov_iter, tracepoints, and client protocol version. Risks include buffer-size estimate mismatch, unchecked format/template coupling enforced by `BUG_ON`, allocation cleanup on partial parses, string truncation to 16-bit length, data blob pointers referencing the fcall buffer lifetime, and iterator short copies. Tests should cover every format character, optional fields under each protocol version, malformed/truncated PDUs, oversized strings and dirent names, buffer finalization, and size estimates for large reads/writes/walks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/protocol.c -->
