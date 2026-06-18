# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copy_mc_64.S

## Purpose
Imported PowerPC machine-check-tolerant copy routine variant used for userspace validation of copy loop behavior.

## Important APIs, Types, and Functions
Defines test-prefixed global copy symbols through `_GLOBAL`/`FUNC_START` macros and uses errno/exception table style fixups from local shims.

## Control Flow
Assembly copies memory in chunks with alignment/size handling and branches to fixup paths on faults, returning remaining byte counts or error-style results matching kernel copy semantics.

## State and Persistence
No persistent state; it mutates destination memory and registers for one call.

## Dependencies and Integration Points
Depends on local `linux/export.h`, `asm/ppc_asm.h`, `asm/errno.h`, and validation C callers in `copyloops`.

## Risks and Test Signals
Risks are exception-table fidelity and mismatch between kernel and userspace fault handling. `exc_validate` and copy validation binaries are the primary test signals.
