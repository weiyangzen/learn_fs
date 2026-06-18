# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-crypto.c

## Purpose
Provides kernel wrappers for Octeon COP2 crypto hardware so kernel crypto operations do not corrupt task or kernel COP2 state.

## Important APIs, Types, And Functions
Exported APIs are `octeon_crypto_enable(struct octeon_cop2_state *state)` and `octeon_crypto_disable(struct octeon_cop2_state *state, unsigned long crypto_flags)`. They use preemption control, local IRQ save/restore, `ST0_CU2`, `KSTK_STATUS(current)`, `octeon_cop2_save()`, and `octeon_cop2_restore()`.

## Control Flow
Enable disables preemption, enables CU2 with IRQs masked, saves either current task lazy COP2 state or active kernel COP2 state, clears task CU2 ownership when needed, and returns whether CU2 was previously enabled. Disable restores saved state or clears CU2, then reenables preemption.

## State, Persistence, And Dependencies
State passes through the caller-provided `octeon_cop2_state` and returned flags. It mutates current thread COP2 metadata and CP0 status.

## Integration Points
Octeon crypto implementations must wrap hardware COP2 operations with these functions. Symbols are GPL-only exports.

## Risks
Calls must be paired exactly before sleeping or returning to userspace. Local IRQ masking protects only state transitions, not the whole operation. Misuse corrupts COP2 state.

## Test Signals
Verify preserved userspace COP2 state, correct CU2 restoration in both prior states, no preemption warnings, and concurrent task crypto workloads.
