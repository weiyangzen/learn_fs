# sources/cloud-native/containers-storage/pkg/tarlog/tarlogger_test.go

Purpose: verifies that `tarlog.NewLogger` observes tar headers in stream order.

Important APIs/types/functions: `TestTarLogger` builds 32 test files with increasing names and sizes, writes them through a tar writer backed by the logger, closes both writers, and compares logged names.

Control flow: every test case writes a header and payload; callback appends names; final assertions check count and order.

State/persistence: in-memory buffers and pipe goroutine only.

Dependencies/integration: depends on `stretchr/testify/require` and `tar-split` tar writer/reader.

Risks: does not cover malformed tar streams, concurrent writes, early close, or callback panics.

Test signals: confirms happy-path header logging without corrupting tar writer behavior.
