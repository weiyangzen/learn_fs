<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfiwx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfiwx.c

## Purpose
Implements store floating-point as integer word indexed.

## Important APIs, types, and functions
`int stfiwx(u32 *frS, void *ea)` copies `frS[1]` to user memory.

## Control flow
The handler performs a 32-bit `copy_to_user` and returns zero or `-EFAULT`.

## State and persistence behavior
Mutates user memory only.

## Dependencies and integration points
Dispatched by `do_mathemu` for `STFIWX`.

## Risks and edge cases
Correct low-word selection depends on the emulator FPR image layout.

## Test signals
User memory receives the expected integer word from the FPR image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfiwx.c -->
