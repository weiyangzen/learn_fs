## sources/distributed-fs/beegfs/client_module/source/net/filesystem/RemotingIOInfo.h

**Purpose:** Defines `RemotingIOInfo`, the per-open/per-IO context passed through BeeGFS remote file operations. It bundles application context, remote handle state, striping data, path info, access flags, write-tracking state, ownership IDs, and optional NVFS state.

**Important APIs/types/functions:** Public inline routines are `RemotingIOInfo_initOpen`, `RemotingIOInfo_initSpecialClose`, `RemotingIOInfo_freeVals`, `RemotingIOInfo_getNumPagesPerStripe`, and `RemotingIOInfo_getNumPagesPerChunk`. The struct fields include `app`, `fileHandleID`, `pattern`, `pathInfo`, `accessFlags`, `needsAppendLockCleanup`, `maxUsedTargetIndex`, `firstWriteDone`, `userID`, `groupID`, and optional `nvfs`.

**Control flow:** Normal callers initialize an object for open, then `FhgfsOpsRemoting_openfile` fills handle ID, path info, and possibly pattern. Special-close initialization is used after partial atomic-open/lookup-open failures when only a remote close is needed. IO paths read stripe geometry from `pattern`, update `maxUsedTargetIndex`, and consult `firstWriteDone`.

**State and persistence behavior:** The struct is transient in-memory handle state. `freeVals` destroys the stripe pattern, frees the duplicated remote handle ID, and uninitializes path info if present. The max-target and first-write pointers generally point into inode handle state, so this struct may not own them.

**Dependencies and integration points:** Depends on `App`, `PathInfo`, `StripePattern`, and `BitStore`. It is consumed heavily by `FhgfsOpsRemoting.c`, commkit storage messages, inode handle management, and buffered/native IO paths.

**Risks:** Ownership is mixed: `fileHandleID`/`pattern` may be owned by this context in special direct-open flows, while `pathInfo`, bitsets, and atomics are often external. Calling `freeVals` on an inode-managed context could free objects still owned elsewhere. Page count helpers assume a valid stripe pattern and chunk size divisible by `PAGE_SIZE`.

**Test signals:** Cover direct-open cleanup, special close after partial open failures, IO with external inode-managed state, page-per-chunk calculations for supported chunk sizes, and null-pattern guard behavior in callers.
