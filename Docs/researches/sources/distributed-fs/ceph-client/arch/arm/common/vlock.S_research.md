<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/vlock.S -->
# sources/distributed-fs/ceph-client/arch/arm/common/vlock.S

## Purpose
ARM assembly implementation of the MCPM voting lock used for first-man cluster setup coordination during low-level power transitions.

## Important APIs/types/functions
- `vlock_trylock(base, cpu)` returns zero on success and nonzero on loss.
- `vlock_unlock(base)` releases ownership.
- Macros `voting_begin` and `voting_end` maintain per-CPU voting bytes with barriers and SEV.

## Control flow
`vlock_trylock()` marks the calling CPU as voting, checks whether owner is empty, writes its owner vote, clears its voting byte, waits until all voting bytes are zero, then checks whether its vote won. If owner was already set, it clears its vote and fails. `vlock_unlock()` clears owner and sends SEV.

## State and persistence behavior
The lock structure stores an owner byte and per-CPU voting bytes. It must reside in Strongly-Ordered or Device memory as the algorithm relies on neighboring byte writes not interfering and on explicit barriers.

## Dependencies and integration points
Depends on `vlock.h`, ARMv7-A WFE/SEV/DMB/DSB behavior, MCPM `MAX_CPUS_PER_CLUSTER`, and `mcpm_head.S` first-man lock arrays.

## Risks and edge cases
Using cacheable normal memory violates assumptions. Incorrect `VLOCK_VOTING_SIZE` or CPU IDs outside the cluster range corrupt lock state. Lost SEV or memory-ordering bugs can deadlock cluster bring-up.

## Test signals
Stress MCPM cluster power-up with multiple CPUs racing to enter; verify only one first-man executes cluster setup and non-winners wait/retry correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/vlock.S -->
