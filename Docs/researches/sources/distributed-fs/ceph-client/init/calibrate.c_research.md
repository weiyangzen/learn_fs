# sources/distributed-fs/ceph-client/init/calibrate.c

## Purpose
`calibrate.c` implements generic loops-per-jiffy delay calibration, honoring an `lpj=` boot override, using architecture timer-based calibration when possible, falling back to convergence against jiffies, and publishing per-CPU and global delay-loop calibration.

## Important APIs, Types, and Functions
Important globals are `lpj_fine`, `preset_lpj`, per-CPU `cpu_loops_per_jiffy`, and global `loops_per_jiffy` from delay code. Key functions are `lpj_setup()`, `calibrate_delay_direct()`, `calibrate_delay_converge()`, weak `calibrate_delay_is_known()`, weak `calibration_delay_done()`, and public `calibrate_delay()`.

## Control Flow
Boot parsing records `lpj=`. `calibrate_delay()` first reuses per-CPU calibration, then preset `lpj`, then `lpj_fine`, then architecture-known calibration, then direct current-timer calibration, and finally binary convergence against jiffies. Direct calibration samples multiple jiffy intervals, filters out timer wrap/asynchronous-event noise, and drops outliers before accepting an estimate.

## State and Persistence Behavior
The chosen LPJ is stored per CPU and in global `loops_per_jiffy` for delay primitives. The `printed` static suppresses duplicate calibration banners after the first CPU. Calibration is runtime boot state and is not persisted across boots.

## Dependencies and Integration Points
It depends on jiffies, `__delay`, SMP CPU IDs, optional `read_current_timer`, printk, boot `__setup`, and architecture weak overrides. It integrates with busy-wait delay loops and CPU bring-up.

## Risks and Test Signals
Risks include bad LPJ from SMI/interrupt noise, timer wrap, mismatched CPU frequencies, invalid user `lpj=`, and long boot delays during convergence. Test signals include boots with/without `lpj=`, architectures with direct timer calibration, SMP secondary CPU calibration, noisy timer environments, and delay accuracy checks.
