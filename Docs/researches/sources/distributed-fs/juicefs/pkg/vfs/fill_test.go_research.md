# sources/distributed-fs/juicefs/pkg/vfs/fill_test.go

Purpose: smoke-tests cache filling over normal and problematic path inputs.

Important APIs and types: `TestFill` uses `createTestVFS`, VFS mkdir/create/write/flush/release/symlink methods, and `v.cacheFiller.Cache`.

Control flow and state: the test creates `/test/file`, writes data, creates relative and absolute symlinks, warms cache for a direct file, directory, symlink, and root path, then removes backing chunk objects and invokes warmup on paths expected to hit bad cases (`/test/file`, absolute symlink, relative missing symlink, internal `.stats`, and nonexistent path).

Persistence and integration: uses memory VFS/object components and real cache filler paths. It exercises metadata resolution, recursive walking, symlink handling, and chunk-store errors.

Risks and test signals: the test mainly ensures no panic and broad path coverage; it does not assert `CacheResponse` counters, cache locations, or error logs. It does not cover evict/check modes.
