# sources/distributed-fs/ceph-client/drivers/mfd/ti_am335x_tscadc.c

## Purpose
`ti_am335x_tscadc.c` is the MFD parent for TI AM335x touchscreen/ADC and AM437x magnetic-stripe/ADC subsystems. It configures shared sequencer registers, runtime PM, clock divider, child cells, and exports serialized step-enable helpers for ADC and touchscreen children.

## Important APIs, Types, and Functions
Exported sequencer helpers are `am335x_tsc_se_set_cache()`, `am335x_tsc_se_set_once()`, `am335x_tsc_se_adc_done()`, and `am335x_tsc_se_clr()`. Internal synchronization uses `am335x_tscadc_need_adc()` and `reg_se_wait`. `tscadc_idle_config()` programs idle step config. `ti_tscadc_probe()` parses DT, validates channel/step counts, initializes regmap and clocks, enables the subsystem, and registers child cells. PM callbacks are `tscadc_suspend()` and `tscadc_resume()`.

## Control Flow
Probe parses touchscreen wires/readouts or magnetic-stripe defaults, counts ADC channels, validates that total input channels do not exceed 8 and touchscreen steps do not exceed 16, maps registers, creates a 32-bit regmap, enables runtime PM, computes and writes the ADC clock divider, configures control bits, programs idle config, enables the subsystem, creates secondary and ADC child cells as requested, and registers them. Sequencer helpers serialize `REG_SE` access so one-shot ADC operations can wait for an active sequencer to reach an acceptable state before taking over.

## State and Persistence
`struct ti_tscadc_dev` stores regmap, MMIO base/physical base, IRQ, control register cache, clock divider, `REG_SE` cache, spinlock, waitqueue, and flags for ADC use/waiting. Suspend clears step enables, may keep subsystem enabled for wake-capable children, and runtime-suspends the parent. Resume restores clock divider, control, idle config, and subsystem enable.

## Dependencies and Integration Points
It depends on DT child nodes `tsc` and `adc`, regmap MMIO, clocks, runtime PM, MFD children for ADC/TSC/MAG, and public `linux/mfd/ti_am335x_tscadc.h`.

## Risks and Edge Cases
There is compatibility for misspelled `ti,coordiante-readouts`. `pm_runtime_get_sync()` return is not checked. The sequencer wait uses uninterruptible sleep and assumes a wake-up from step-cache updates. Channel and step validation is strict and DT-driven. Clock divider calculation assumes parent clock is at least target rate.

## Test Signals
Validate DT parsing for touchscreen and ADC-only modes, invalid channel rejection, sequencer arbitration under concurrent ADC/TSC users, suspend wake-child behavior, resume register restoration, runtime PM balance, and child platform data correctness.
