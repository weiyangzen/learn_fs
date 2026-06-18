## sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsChunkPageVec.c

**Purpose:** Implements error-completion helpers for `FhgfsChunkPageVec`, a page-vector abstraction used by BeeGFS buffered IO.

**Important APIs/types/functions:** Provides `FhgfsChunkPageVec_iterateAllHandleWritePages` and `FhgfsChunkPageVec_iterateAllHandleReadErr`.

**Control flow:** Both helpers repeatedly call `FhgfsChunkPageVec_iterateGetNextPage`. The write helper ends writeback for each page through `FhgfsOpsPages_endWritePage` with the supplied Linux error code. The read-error helper unmaps, unlocks, and releases each page through `FhgfsPage_unmapUnlockReleaseFhgfsPage`.

**State and persistence behavior:** These functions consume the vector's iterator state. They do not persist data; they finalize page state after failed or remaining IO.

**Dependencies and integration points:** Called by remoting page-vector IO when allocation or communication fails and pages must not remain locked or under writeback. Depends on `FhgfsOpsPages` and `FhgfsPage` helpers.

**Risks:** Because iteration state advances, callers needing another pass must reset the iterator. Passing the wrong error sign to write completion would record incorrect writeback status. Missing these helpers on error paths can leave pages locked or writeback-pending.

**Test signals:** Fault-inject page-vector read/write failures and verify every page is unlocked, unmapped, released, and has expected writeback/error state.
