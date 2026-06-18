<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/errors.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/errors.go

Purpose: central error sentinels for BeeMsg read/write transport failures.

Important APIs/types/functions: `ErrBeeMsgWrite` and `ErrBeeMsgRead`.

Control flow: no flow; `io.go` wraps blocking I/O errors with these sentinels and `NodeConns` uses `errors.Is(err, ErrBeeMsgWrite)` to decide whether retrying another connection is safe.

State and persistence: none.

Dependencies and integration points: depends only on `errors`; integrated into transport retry semantics.

Risks: correct wrapping matters. Serialization errors in `WriteTo` intentionally do not wrap `ErrBeeMsgWrite`, so retry logic can distinguish local encoding bugs from broken sockets.

Test signals: `io_test.go` asserts write sentinel behavior and non-wrapping for serialization/deserialization errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/errors.go -->
