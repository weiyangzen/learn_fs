<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnabs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnabs.c

## Purpose
Implements negative absolute value by forcing the double sign bit set.

## Important APIs, types, and functions
`int fnabs(u32 *frD, u32 *frB)` ORs `frB[0]` with `0x80000000` and copies `frB[1]`.

## Control flow
Straight-line bit manipulation with optional DEBUG logging.

## State and persistence behavior
Only destination FPR bits are changed; no exception status is generated.

## Dependencies and integration points
Dispatched by `do_mathemu` for `FNABS`.

## Risks and edge cases
Must preserve NaN payload and low word while setting only the sign bit.

## Test signals
Destination is bit-identical to source except sign set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnabs.c -->
