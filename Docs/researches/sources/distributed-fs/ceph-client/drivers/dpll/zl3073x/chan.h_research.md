# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/chan.h

## Purpose
This header defines the ZL3073x DPLL channel cache layout and inline bitfield helpers for interpreting and mutating channel registers.

## Important APIs and types
`struct zl3073x_chan` groups mutable `mode_refsel` and `ref_prio[]` configuration separately from status fields `mon_status` and `refsel_status`. Inline helpers get/set channel mode, forced reference, per-reference priority, selectability, lock state, holdover-ready bit, selected-reference state, and selected-reference ID.

## Control flow and state
The header has no executable flow beyond inline field access. The grouping is used by `chan.c` to compare mutable config as a block and to avoid treating status changes as configuration changes.

## Dependencies and integration
It depends on `regs.h` for masks and constants. `core.c` refreshes state periodically, and `dpll.c` uses helpers to map hardware modes and priorities to DPLL netlink state.

## Risks and tests
Incorrect bit masks or P/N priority packing would expose wrong pin state or change the wrong reference. Tests should exercise both even/P and odd/N reference priorities plus all hardware mode values.
