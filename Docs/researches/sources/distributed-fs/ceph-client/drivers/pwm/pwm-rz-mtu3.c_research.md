# sources/distributed-fs/ceph-client/drivers/pwm/pwm-rz-mtu3.c

## Purpose

`pwm-rz-mtu3.c` exposes Renesas RZ/G2L MTU3a timer outputs as twelve logical PWMs across seven hardware channels. Dual-output hardware channels share timer state; MTU1 and MTU2 have one output. Only normal polarity is currently supported and disabled output is Hi-Z.

## APIs, control flow, and state

`struct rz_mtu3_pwm_chip` stores the parent clock, lock, rate, per-hardware-channel user and enable counts, cached prescaler, and channel maps. `rz_mtu3_pwm_request()` claims a parent MTU channel only for the first user. `rz_mtu3_pwm_config()` computes cycles, selects prescale 1/4/16/64, enforces shared-prescaler constraints, writes `TCR` and TGR pairs, and temporarily resumes PM for disabled channels. `get_state()` reads TGR/TCR when enabled.

Enable count controls the shared counter. Prescale and ownership are persistent software state; register values persist while powered.

## Dependencies and integration points

This is an MFD child using `linux/mfd/rz-mtu3.h` helpers, parent channel data, runtime PM, and the PWM core.

## Risks and test signals

Sibling outputs cannot freely choose different prescalers; conflicts can return `-EBUSY` or reuse lower resolution. Disable decrements enable counts without explicit underflow guard. Test logical-to-hardware mapping, sibling conflicts, runtime PM transitions, normal-polarity rejection of inverted requests, and get_state while enabled/disabled.
