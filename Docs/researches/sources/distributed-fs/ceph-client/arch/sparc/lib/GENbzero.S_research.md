<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENbzero.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/GENbzero.S

## Purpose
Provides generic SPARC64 implementations of `memset`, `bzero`, and `clear_user`, plus a runtime patch helper that redirects generic symbol names to these optimized routines.

## Important APIs, Types, And Functions
Exports `GENmemset`, `GENbzero`, `GENclear_user`, and `generic_patch_bzero`. Internal labels include `GENbzero_from_clear_user`, `GENbzero_pre_loop`, `GENbzero_loop`, `GENbzero_medium`, `GENbzero_tiny`, `GENbzero_done`, and `GENbzero_return`. The `EX_ST` macro emits faultable stores and exception-table entries to `__retl_o1_asi`.

## Control Flow
`GENmemset` expands the byte pattern across a 64-bit word and falls into the zeroing core. `GENbzero` handles zero length, saves `%asi`, selects primary ASI, aligns to 8 and then 64 bytes, uses unrolled 64-byte `stxa` loops for large ranges, handles medium 8-byte chunks and tiny byte tails, restores `%asi`, and returns the original buffer. `GENclear_user` uses `ASI_AIUS` when called from user-clear context. `generic_patch_bzero` writes branch-always instructions at `memset`, `__bzero`, and `__clear_user`, followed by NOPs and instruction flushes.

## State And Persistence
The routines temporarily change `%asi` and restore it. Faultable user clears persist exception-table metadata. `generic_patch_bzero` permanently patches kernel text for the running image.

## Dependencies And Integration Points
Used by SPARC64 memory/string routines and clear-user paths. Depends on ASI constants, exception-table fixup `__retl_o1_asi`, writable/patchable early kernel text, and instruction-cache flush semantics.

## Risks And Edge Cases
Fault handling must return the expected uncleared byte count conventions through the shared fixup path. `%asi` preservation is mandatory. Runtime patch offsets must fit SPARC branch encoding and be flushed before execution. Partial stores before a user fault are normal for clear-user semantics but must be accounted for by callers.

## Test Signals
Signals include memset/bzero correctness across zero, tiny, unaligned, medium, and large buffers; clear_user fault injection; `%asi` preservation checks; and verification that patched `memset`, `__bzero`, and `__clear_user` branch to the generic routines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENbzero.S -->
