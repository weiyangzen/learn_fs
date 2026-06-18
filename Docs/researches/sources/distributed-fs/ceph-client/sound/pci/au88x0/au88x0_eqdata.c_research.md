# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_eqdata.c

## Purpose
Provides static equalizer coefficient, gain, state, and peak-level initializer data consumed by `au88x0_eq.c`.

## Important APIs, Types, And Functions
Data includes `asEqCoefsZeros`, `asEqCoefsPipes`, `asEqCoefsNormal`, `eq_gains_normal`, `eq_gains_zero`, `eq_gains_current`, `eq_states_zero`, `asEqOutStateZeros`, and `eq_levels`. There are no functions.

## Control Flow
No executable flow. EQ init and reset copy these arrays into MMIO through the EQ hardware writer functions. `asEqCoefsNormal` is selected as the active ten-band coefficient set.

## State And Persistence
All arrays are static constants in module memory. They are immutable and serve as templates for volatile hardware programming.

## Dependencies And Integration Points
Depends on `auxxEqCoeffSet_t` from `au88x0_eq.h` and is directly included by `au88x0_eq.c`, not compiled independently.

## Risks
Coefficient correctness is entirely data-driven and hardware-specific. Comments point to additional coefficient sets in old Windows INF material, so this file likely represents one fixed profile. Array length mismatches would cause hardware programming beyond intended bands, but current loops are bounded by `eqhw->this04`.

## Test Signals
Successful EQ init, pass-through programming, and normal EQ behavior are the primary signals. Static analysis/build checks should confirm array initializers match declared sizes.
