# sources/distributed-fs/ceph-client/drivers/pwm/pwm-stm32.c

## Purpose

`pwm-stm32.c` drives STM32 timer PWM outputs through the waveform API and optional DMA-backed capture. It supports shared timer period/prescaler, complementary outputs, break inputs, and capture using paired channels.

## APIs, control flow, and state

`struct stm32_pwm` stores lock, parent clock/regmap, max ARR, complementary support, breakinputs, and DMA capture buffer. `round_waveform_tohw/fromhw`, `read_waveform`, and `write_waveform` convert and program CCER/PSC/ARR/CCR state. Active channels constrain PSC/ARR for later channels. Capture configures PWM input mode, uses `stm32_timers_dma_burst_read()` for CCR snapshots, corrects overflow/races, and converts ticks to nanoseconds. Probe detects channels/complementary outputs, applies breakinputs, locks clock rate, and initializes clock refs for already enabled channels.

Hardware registers are primary state; software keeps breakinput config and active clock refs.

## Dependencies and integration points

It is an `stm32-timers` MFD child using parent regmap/clock/DMA helper, OF breakinput properties, pinctrl PM states, PWM waveform ops, and optional capture when DMA is enabled.

## Risks and test signals

Active channels cannot use independent periods. Clock refcounting in waveform writes is subtle. Capture requires no active outputs and at least two capture units for duty. Test waveform round trips, conflicts, complementary outputs, breakinput restore, DMA capture, refcounts, and suspend active-channel rejection.
