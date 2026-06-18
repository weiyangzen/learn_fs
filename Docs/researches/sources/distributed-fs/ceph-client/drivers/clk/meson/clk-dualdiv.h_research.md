# sources/distributed-fs/ceph-client/drivers/clk/meson/clk-dualdiv.h

## Purpose
`clk-dualdiv.h` defines the table and register-field contract for Meson dual-divider clocks and declares the mutable/read-only ops exported by the implementation.

## Important APIs, Types, And Functions
`struct meson_clk_dualdiv_param` stores one table setting: `n1`, `n2`, `m1`, `m2`, and `dual`. `struct meson_clk_dualdiv_data` describes the five hardware fields as `struct parm` values plus a pointer to the settings table. The header declares `meson_clk_dualdiv_ops` and `meson_clk_dualdiv_ro_ops`.

## Control Flow
There is no runtime logic in the header. SoC files provide static table data and field descriptors; `clk-dualdiv.c` interprets them during recalc, determine-rate, and set-rate calls.

## State, Persistence, And Dependencies
The header itself is stateless. It depends on `clk-provider.h` and `parm.h`. Persistent state is the hardware register state represented by consumers' `parm` descriptors and the static table lifetime of the parameter arrays.

## Integration Points
Included by AO/peripheral clock-controller files that need precise low-frequency generation. The read-only ops let SoC files expose firmware-programmed dual dividers without allowing Linux to modify them.

## Risks And Edge Cases
The table sentinel convention is implicit in the C implementation. If a consumer omits the terminating zero entry or uses raw encodings instead of natural values, rate calculations and register writes will be wrong.

## Test Signals
Compile coverage for all users, table-sentinel checks in review, and runtime rate checks for every dual-divider consumer validate this contract.
