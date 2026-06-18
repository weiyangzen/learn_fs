# sources/distributed-fs/juicefs/pkg/vfs/handle.go

Purpose: manages VFS file, directory, access-log, and control handles, including locking, operation cancellation, and handle-state persistence for restart recovery.

Important APIs and types: `handle` stores inode/fh, directory handler, file reader/writer, lock owners, active operation contexts, RW lock counters/condition, internal-file buffers, and tier ID. VFS methods include `newHandle`, `findAllHandles`, `findHandle`, `releaseHandle`, `newFileHandle`, `releaseFileHandle`, `invalidateDirHandle`, `dumpAllHandles`, and `loadAllHandles`. `state` and `saveHandle` encode JSON recovery data.

Control flow and state: file handles are allocated with odd/even low bits for read-only/read-write distinction and skip recovered descriptors. `Rlock`/`Wlock` wait with timeout and abort if the operation context is canceled. Active contexts are tracked for cancellation by pid. Release waits for readers/writers before closing reader/writer objects. Dump serializes handles, flushes writers, captures access-log pending data, and writes JSON. Load reconstructs handles, access-log readers, readers, and writers from JSON.

Persistence and integration: handle recovery state is persisted to a JSON file path chosen by callers. It integrates with `reader`, `writer`, `meta.DirHandler`, accesslog globals, and VFS handle maps.

Risks and test signals: the field `hanleM` spelling is inherited but easy to misuse. Recovered read-only handles can be synthesized by `findHandle`. Dump writes directly with `os.Create`, not atomic rename. No dedicated handle tests in this subset.
