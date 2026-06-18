<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/io.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/io.go

Purpose: context-aware read/write helpers for complete BeeMsg frames over stream-like `io.Reader`/`io.Writer` objects.

Important APIs/types/functions: `goWithContext`, `WriteTo`, `ReadFrom`, and `WriteRead`.

Control flow: `goWithContext` runs a blocking function in a goroutine and returns either its error or context cancellation. `WriteTo` assembles a BeeMsg and writes all bytes through `bytes.Buffer.WriteTo`. `ReadFrom` reads exactly the header, extracts total message length, reads the body, and disassembles it. `WriteRead` writes a request and conditionally reads a response.

State and persistence: no persistence; transient buffers. Blocking goroutines are not forcibly stopped when context cancels; they may continue until the underlying I/O returns.

Dependencies and integration points: depends on `AssembleBeeMsg`, header length extraction, and error sentinels. Used by TCP connection authentication and request/response flow.

Risks: `ReadFrom` computes `make([]byte, msgLen-HeaderLen)` with unsigned arithmetic; a malicious header with `MsgLen < HeaderLen` can underflow to a very large allocation. Context cancellation does not close the underlying reader/writer. Short writes from `WriteTo` are not explicitly checked beyond returned error.

Test signals: `io_test.go` covers round-trip, serialization/deserialization error wrapping, cancellation, and timeout against a blocking read/write stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/io.go -->
