# sources/distributed-fs/ceph-client/drivers/pwm/pwm-bcm-iproc.c

Purpose: implements a four-channel PWM driver for Broadcom iProc PWM hardware.

Important APIs/types/functions: `struct iproc_pwmc` stores MMIO base and clock. `iproc_pwmc_apply()` computes prescaler, period count, and duty count, disables the channel, programs prescale/period/duty/polarity, and conditionally reenables. `iproc_pwmc_get_state()` reads enable, polarity, prescale, period, and duty registers. Probe maps registers, enables the clock, initializes full-drive normal polarity, and registers four PWMs.

Control flow: apply iterates prescale from 0 to 63 until count values fit 16-bit ranges and period is at least 2. It enforces the hardware's 400 ns enable-toggle delay around disable/enable. State read reconstructs nanoseconds from counts, prescaler, and clock rate.

State and persistence: no extra software cache beyond MMIO base and clock. Hardware registers hold active settings; the PWM core caches requested state.

Dependencies and integration: depends on common clock, MMIO, OF compatible `brcm,iproc-pwm`, and PWM core callbacks.

Risks and test signals: arithmetic uses `rate * state->period` in `u64`, so very high rates or periods deserve overflow review. The driver disables before every apply, which may cause visible glitches. Test signals include prescale boundary periods, polarity readback, clock rate zero handling in `get_state`, 400 ns delay compliance, and all four channels.
