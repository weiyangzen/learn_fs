# sources/distributed-fs/ceph-client/drivers/pwm/pwm-clps711x.c

Purpose: implements PWM support for Cirrus Logic CLPS711X/EP7209 style hardware with two fixed-period outputs controlled by PMP configuration bits.

Important APIs/types/functions: `struct clps711x_chip` stores the PMP control MMIO address and clock. `clps711x_pwm_request()` computes and stores the fixed period from the clock rate in `pwm->args.period`. `clps711x_pwm_apply()` checks period/polarity, converts duty to a 4-bit level, and updates the proper bitfield.

Control flow: probe maps the control register, gets the clock, and registers two PWMs. On request the fixed period is derived. Apply rejects inverted polarity and any period different from the fixed argument; disabled output writes a zero duty nibble.

State and persistence: no private runtime cache besides MMIO and clock. Hardware bitfields hold duty levels. The fixed period is stored in per-PWM args during request.

Dependencies and integration: depends on MMIO, clock framework, OF compatible `cirrus,ep7209-pwm`, and PWM core request/apply callbacks.

Risks and test signals: duty resolution is only 4 bits, and there is no `get_state`. Clock rate zero is rejected only at request time. Test signals include both channels, fixed-period enforcement, disabled output level, duty quantization from 0 to 15, and invalid polarity.
