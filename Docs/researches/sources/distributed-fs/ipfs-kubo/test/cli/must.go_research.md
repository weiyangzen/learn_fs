# sources/distributed-fs/ipfs-kubo/test/cli/must.go

Purpose: tiny generic helper for tests that want to unwrap `(value, error)` expressions inline.

Important APIs/functions: `MustVal[V any](val V, err error) V` panics if `err` is non-nil and otherwise returns `val`.

Control flow: single branch checks the error and panics immediately, leaving caller code concise.

State and persistence: no state or persistence.

Dependencies/integration: standard Go generics only. It is available in package `cli` for tests in this directory.

Risks: panic-based error handling is appropriate for setup helpers but can obscure which assertion failed if overused in test logic. Test signals are indirect: callers either receive the value or the test process panics.
