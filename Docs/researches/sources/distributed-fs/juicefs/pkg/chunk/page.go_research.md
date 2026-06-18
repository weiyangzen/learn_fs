## sources/distributed-fs/juicefs/pkg/chunk/page.go

Purpose: provides a refcounted byte buffer abstraction used throughout chunk cache read/write paths, including off-heap allocation and dependent slices.

Important APIs/types/functions: `Page` stores `refs`, `offheap`, optional dependency, `Data`, and optional debug stack. `NewPage` wraps existing data. `NewOffPage` allocates off-heap memory with `utils.Alloc`, sets a finalizer that logs leaked refcounts, and optionally captures stacks via `JFS_PAGE_STACK`. `Slice` creates a dependent `Page` sharing a subslice and retaining the parent. `Acquire` and `Release` adjust refcounts; release frees off-heap data and releases dependencies when count reaches zero. `pageReader` implements `Read`, `ReadAt`, and `Close` over a retained page.

State and persistence: in-memory/off-heap only. Page lifetime is explicit and refcounted.

Dependencies and integration points: central to `cachedStore`, disk/memory cache, singleflight, and tests. Depends on JuiceFS `utils.Alloc/Free`.

Risks and test signals: double release, missing release, or shared-slice misuse can corrupt reads or leak off-heap memory. Finalizer logging helps diagnose but is not deterministic. Tests cover page slicing and reader behavior.
