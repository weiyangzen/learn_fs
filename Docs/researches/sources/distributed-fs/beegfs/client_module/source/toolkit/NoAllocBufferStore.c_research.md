## sources/distributed-fs/beegfs/client_module/source/toolkit/NoAllocBufferStore.c

**Purpose:** Implements a fixed-size buffer pool that allocates all buffers during initialization and performs no memory allocation during normal get/put operations.

**Important APIs/types/functions:** Implements lifecycle functions, `NoAllocBufferStore_waitForBuf`, `instantBuf`, `addBuf`, internal `__NoAllocBufferStore_initBuffers`, getters for availability/size, and debug-only task tracking helpers.

**Control flow:** Initialization allocates the pointer array and `vmalloc`s each buffer, then marks all buffers available. `waitForBuf` locks, checks debug recursive-use state, waits on a condition while empty, pops a buffer, records debug ownership, and unlocks. `instantBuf` returns NULL if empty without waiting. `addBuf` validates non-NULL, signals waiters, pushes the buffer, removes debug ownership, and unlocks.

**State and persistence behavior:** State includes buffer pointer stack, total count, buffer size, available count, mutex, condition variable, and optional debug RB tree keyed by task PID with stack traces. Buffers exist only for module/runtime lifetime and are freed on uninit.

**Dependencies and integration points:** Used by IO paths that need emergency/no-allocation buffers. Depends on BeeGFS mutex/condition wrappers, `vmalloc`/`vfree`, pointer RB trees, current task PID, and debug stack trace helpers from `OsDeps`.

**Risks:** `addBuf` does not bounds-check `numAvailable` against `numBufs`, so double-return can corrupt the stack. `uninit` frees only currently available buffers; buffers still checked out at teardown leak or worse. `waitForBuf` can deadlock if a task recursively waits while holding a buffer; debug mode detects this. Init error cleanup frees all array entries but leaves pointer array cleanup to caller path.

**Test signals:** Test pool init/uninit with zero and nonzero buffers, blocking wait/wakeup, instant empty behavior, double-add detection expectations, checked-out buffer teardown, debug recursive acquisition warnings, and allocation failure during init.
