# sources/cloud-native/moby/pkg/pools/pools.go

Purpose: shared allocation-reduction helpers for Moby packages. It exposes 32 KiB `BufioReader32KPool` and `BufioWriter32KPool`, an internal 32 KiB byte-slice pool, and `Copy` as an `io.CopyBuffer` convenience wrapper.

APIs and flow: `Get` resets a pooled bufio object onto the caller's reader/writer; `Put` resets it to nil before returning it. `NewReadCloserWrapper` and `NewWriteCloserWrapper` combine pooled object release with optional underlying close, with writer close flushing first.

State and dependencies: state is process-local `sync.Pool`; objects may disappear under GC. It depends on stdlib bufio/io/sync and Moby `ioutils` wrappers.

Risks and tests: callers must not use a reader/writer after `Put`/wrapper close. Flush errors are ignored during close. Tests cover pooling, reset behavior, wrappers, and buffer reuse.
