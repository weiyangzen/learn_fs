## sources/distributed-fs/beegfs/client_module/source/toolkit/NoAllocBufferStore.h

**Purpose:** Declares the no-allocation buffer pool interface for BeeGFS client code.

**Important APIs/types/functions:** Declares opaque `NoAllocBufferStore`, lifecycle functions, blocking and nonblocking buffer acquisition, buffer return, `getNumAvailable`, and `getBufSize`.

**Control flow:** Callers initialize/construct the store with a fixed buffer count and size, borrow buffers through `waitForBuf` or `instantBuf`, return them through `addBuf`, and destroy the store only when all buffers are returned.

**State and persistence behavior:** The header hides internal state. Runtime state is a finite pool of `vmalloc` buffers with no normal-path allocation.

**Dependencies and integration points:** Includes BeeGFS thread primitives and common definitions. Used by networking/IO code that needs bounded emergency buffers.

**Risks:** The opaque interface cannot enforce return discipline. `waitForBuf` may sleep, so it must not be called from atomic contexts. Callers must not return foreign or duplicate buffers.

**Test signals:** Compile users for sleep-context correctness, validate all borrowed buffers are returned before destruction, and stress concurrent get/put operations.
