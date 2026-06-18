# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_phase.c

## Purpose
`ccu_phase.c` implements phase-only clock ops used for MMC sample/output clock delay controls.

## Important APIs, Types, And Functions
Important callbacks are `ccu_phase_get_phase()` and `ccu_phase_set_phase()` exported through `ccu_phase_ops`.

## Control Flow
Get/set derive phase steps from parent and grandparent clock rates, treating register delay value zero as 180 degrees. Set computes the nearest delay value, updates the phase bitfield under the shared lock, and returns through CCF phase APIs.

## State And Persistence
The only state is the delay bitfield in the module clock register. There is no persistent software state.

## Dependencies And Integration Points
It depends on CCF parent traversal, MMIO, spinlocks, and `ccu_common`. It integrates mainly with MMC host drivers using sample/output phase clocks.

## Risks
Rate assumptions matter: if parent or grandparent rates are unavailable or not an integer divider relationship, phase calculation can fail or be inaccurate. The zero-means-180 hardware convention must be preserved.

## Test Signals
Test with MMC tuning, `clk_get_phase()`/`clk_set_phase()` calls, and card I/O at multiple bus speeds.
