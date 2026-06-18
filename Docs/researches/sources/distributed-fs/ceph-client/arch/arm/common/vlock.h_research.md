<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/vlock.h -->
# sources/distributed-fs/ceph-client/arch/arm/common/vlock.h

## Purpose
Shared layout constants for the ARM MCPM voting lock structure used by `vlock.S` and `mcpm_head.S`.

## Important APIs/types/functions
- `VLOCK_OWNER_OFFSET`
- `VLOCK_VOTING_OFFSET`
- `VLOCK_VOTING_SIZE`
- `VLOCK_SIZE`
- `VLOCK_OWNER_NONE`

## Control flow
No executable flow. The constants drive assembler offsets and allocation sizes.

## State and persistence behavior
Defines the memory layout of lock state: owner byte at offset zero and a word-rounded per-CPU voting region after offset four.

## Dependencies and integration points
Depends on `asm/mcpm.h` for `MAX_CPUS_PER_CLUSTER`. Included by `vlock.S` and `mcpm_head.S`.

## Risks and edge cases
Changing these constants without updating assembly users breaks low-level locking. Size rounding must remain compatible with word-wide scans in the `MANY` case.

## Test signals
Assembler builds should pass layout expectations; MCPM multi-CPU bring-up stress tests validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/vlock.h -->
