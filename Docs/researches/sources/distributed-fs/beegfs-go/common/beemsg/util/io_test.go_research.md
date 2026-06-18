<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/io_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/io_test.go

Purpose: tests BeeMsg stream I/O helpers and provides `testMsg` used by other utility tests.

Important APIs/types/functions: `testMsg`, `serdeFail`, `TestReadWrite`, `TestGoWithContext`, `blockingReadWriter`, `TestWriteTimeout`, and `TestReadTimeout`.

Control flow: `testMsg` serializes a uint32, C-string bytes, and feature flags; tests round-trip through `WriteTo`/`ReadFrom`, toggle `serdeFail` to force serializer/deserializer failures, and cancel contexts to verify sentinel wrapping. Timeout tests use a read/write stub that sleeps.

State and persistence: in-memory buffers only. `serdeFail` is a package-level mutable test switch, so tests should not be parallelized without isolation.

Dependencies and integration points: depends on `beeserde`, `testify/assert`, and utility read/write functions. `testMsg` is reused by `assemble_test.go` and `comm_test.go`.

Risks: global `serdeFail` can leak between tests if a failing test aborts early. Tests do not cover invalid header lengths or malicious allocation behavior.

Test signals: good coverage for normal stream framing, context returns, and error classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/io_test.go -->
