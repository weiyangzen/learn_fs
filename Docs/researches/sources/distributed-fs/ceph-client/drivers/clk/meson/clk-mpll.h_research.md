# sources/distributed-fs/ceph-client/drivers/clk/meson/clk-mpll.h

## Purpose
`clk-mpll.h` declares the data structure and flags used by Meson MPLL common-clock operations.

## Important APIs, Types, And Functions
`struct meson_clk_mpll_data` describes SDM, SDM enable, integer divider N2, spread-spectrum enable, misc bit, optional init sequence, init count, and flags. The flags are `CLK_MESON_MPLL_ROUND_CLOSEST` and `CLK_MESON_MPLL_SPREAD_SPECTRUM`. The header declares read-only and mutable `clk_ops` exports.

## Control Flow
The header has no executable logic. SoC files fill the descriptors and choose either `meson_clk_mpll_ops` or `meson_clk_mpll_ro_ops`.

## State, Persistence, And Dependencies
It is stateless by itself and depends on `clk-provider.h`, `spinlock.h`, and `parm.h`. Runtime state persists in the hardware registers addressed by the `parm` fields.

## Integration Points
Included by Meson SoC clock-controller files with MPLL outputs. The optional `reg_sequence` pointer links SoC-specific magic init values to the shared implementation.

## Risks And Edge Cases
Omitting optional fields is valid only when the implementation checks `MESON_PARM_APPLICABLE()`. Incorrect init counts or flag choices can change spread-spectrum behavior or rate rounding across all consumers of an MPLL.

## Test Signals
Build coverage plus SoC-specific clock-rate checks around MPLL consumers are the useful validation signals.
