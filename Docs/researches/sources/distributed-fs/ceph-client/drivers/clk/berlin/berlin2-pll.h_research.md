# sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-pll.h

## Purpose
Declares the Berlin2 PLL descriptor map and registration API used by SoC clock setup code.

## Important APIs, Types, And Functions
`struct berlin2_pll_map` contains the VCO divider lookup table, multiplier, and bit shifts for feedback, reference, and divider-select fields. `berlin2_pll_register` registers a simple PLL clock from a map, base, name, parent name, and flags.

## Control Flow
The header is declarative. SoC files create `__initconst` maps and pass them to the implementation.

## State And Persistence
Map data is copied by the implementation into the permanent clock object at registration time.

## Dependencies And Integration Points
Consumed by `bg2.c`, `bg2q.c`, and `berlin2-pll.c`.

## Risks And Edge Cases
The 16-entry `vcodiv` table may contain zero holes, so the implementation must defend against selected invalid entries. Incorrect shift values produce wrong clock tree rates.

## Test Signals
Compile/link coverage and rate-recalc tests for BG2 and BG2Q maps are the main signals.
