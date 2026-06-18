# sources/distributed-fs/ceph-client/drivers/clk/meson/clk-phase.h

## Purpose
`clk-phase.h` declares the register-field descriptors and ops for Meson phase-control clocks.

## Important APIs, Types, And Functions
`struct meson_clk_phase_data` contains one phase `parm`. `struct meson_clk_triphase_data` contains `ph0`, `ph1`, and `ph2`. `struct meson_sclk_ws_inv_data` contains a phase field and a word-select field. The header declares `meson_clk_phase_ops`, `meson_clk_triphase_ops`, and `meson_sclk_ws_inv_ops`.

## Control Flow
No executable logic lives in the header. SoC clock descriptions attach these data structs to `clk_regmap` instances and pick the desired ops.

## State, Persistence, And Dependencies
The header is stateless and depends on `clk-provider.h` and `parm.h`. Persistent state is the hardware phase/word-select register state managed by the implementation.

## Integration Points
Included by audio-focused Meson clock-controller files that need phase controls surfaced through common clock phase APIs.

## Risks And Edge Cases
The structures encode semantic contracts that are not type-enforced: triphase fields must be equivalent-width compatible fields, and the SCLK word-select field must represent the inverse phase relation expected by the implementation.

## Test Signals
Compile coverage of users and runtime clock phase get/set tests for each instantiated phase type validate the header contract.
