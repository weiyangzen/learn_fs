# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sti.c

## Purpose

`pwm-sti.c` drives STi PWM/capture hardware. PWM outputs share a common period prescaler and common output enable; capture inputs use interrupts to collect edge timestamps.

## APIs, control flow, and state

`struct sti_pwm_chip` stores clocks, regmap fields, channel counts, capture data, configured bitmask, current reference PWM, and enable count. `sti_pwm_config()` enforces shared-period compatibility and exact prescaler representation, writes duty, and disables capture interrupts. `sti_pwm_capture()` arms rising/falling capture and waits for snapshots filled by `sti_pwm_interrupt()`. Enable/disable manage common output enable and clocks through `en_count`.

Software state tracks configured outputs, common enable count, current period reference, and transient capture snapshots.

## Dependencies and integration points

The driver uses OF `st,pwm-num-chan` and `st,capture-num-chan`, MMIO regmap, IRQs, `pwm`/`capture` clocks, wait queues, and PWM capture APIs.

## Risks and test signals

Outputs must share period. Clock leaks appear possible if enabling `cpt_clk` fails after `pwm_clk` succeeds in config/enable. Capture returns zero for no or very slow input and can race edge snapshots. Test shared-period rejection, exact period validation, capture timeout/known waveforms, IRQ ack, and clock failure paths.
