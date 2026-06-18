# sources/cloud-native/containers-storage/pkg/pools/pools.go

Purpose: centralizes reusable `bufio.Reader` and `bufio.Writer` pools to reduce allocations.

Important APIs, types, and functions: globals `BufioReader32KPool`, `BufioWriter32KPool`; `BufioReaderPool`, `BufioWriterPool`; `Get`, `Put`, `Copy`, `NewReadCloserWrapper`, and `NewWriteCloserWrapper`.

Control flow: `init` creates 32K reader and writer pools. `Get` obtains a pooled buffer and resets it to a new reader/writer. `Put` resets to nil and returns to the pool. `Copy` uses the reader pool with `io.Copy`. Wrapper constructors return closers that flush/close underlying objects where applicable and return buffers to the pool.

State and persistence: in-memory `sync.Pool` state only. No persistence.

Dependencies and integration points: depends on `bufio`, `io`, `sync`, and `ioutils`. Used by performance-sensitive stream paths needing pooled buffered I/O.

Risks and edge cases: callers must not use buffers after `Put`; tests demonstrate such use can panic. `NewReadCloserWrapper` wraps `r`, not the provided `buf`, so passing a separate `buf` requires callers to ensure reads go through the intended object. Close wrappers ignore underlying close errors in the reader case.

Test signals: `pools_test.go` covers get/put behavior, wrapper close behavior, writer flushing, and after-put reset consequences.
