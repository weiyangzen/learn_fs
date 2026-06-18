## sources/distributed-fs/juicefs/pkg/chunk/chunk.go

Purpose: defines the core chunk storage interfaces used by JuiceFS higher layers.

Important APIs/types/functions: `Reader` exposes context-aware `ReadAt(ctx, *Page, off)`. `Writer` embeds `io.WriterAt` and adds `ID`, `SetID`, `SetWriteback`, `FlushTo`, `Finish`, and `Abort`. `ChunkStore` creates readers/writers and exposes removal, cache fill/evict/check, memory usage, runtime limit updates, and underlying blob storage access.

State and persistence: interface only; implementations decide persistence. In this package `cachedStore` is the main implementation.

Dependencies and integration points: imports `context`, `io`, and JuiceFS `object.ObjectStorage`. This is the boundary between file/chunk logic and object-backed storage/cache implementations.

Risks and test signals: callers rely on `Finish(length)` as write completion and on `Abort` cleanup. `CheckCache` uses a callback rather than returning structured results, so callback semantics are part of the contract.
