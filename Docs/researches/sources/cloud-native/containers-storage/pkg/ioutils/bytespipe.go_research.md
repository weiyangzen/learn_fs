## sources/cloud-native/containers-storage/pkg/ioutils/bytespipe.go

Purpose: dynamically buffered in-memory `io.ReadWriteCloser` pipe with reusable fixed-size buffer slices and backpressure.

Important APIs/types/functions: constants `maxCap`, `minCap`, `blockThreshold`; `ErrClosed`; global `bufPools`; `BytesPipe`; `NewBytesPipe`; `Write`; `CloseWithError`; `Close`; `Read`; `returnBuffer`; and `getBuffer`.

Control flow: writes append to the last fixed buffer, allocate geometrically larger buffers up to `maxCap`, and block while total buffered bytes exceed `blockThreshold`. Reads wait for data or close error, drain buffers in order, return empty buffers to size-specific sync pools, and broadcast waiters. Close sets `closeErr` to supplied error or EOF and wakes readers/writers.

State and persistence: in-memory synchronized queue, condition variable, close state, total buffered length, and process-global sync.Pool map keyed by capacity.

Dependencies and integration points: used where producer/consumer byte streaming needs elastic buffering without retaining peak allocations permanently.

Risks: `Read` uses a single `Cond.Wait` instead of a loop before checking close/data, so spurious wakeups could return `0, nil`. Writers blocked on threshold wake on reads or close. Global pools are guarded for map access but pooled buffers retain allocated memory by size class.

Test signals: `bytespipe_test.go` exists outside the required output list and covers reads, writes, random chunks, and benchmarks. Local package tests could not run because `go` is unavailable.
