# sources/distributed-fs/ceph-client/drivers/pwm/pwm-rzg2l-gpt.c

## Purpose

`pwm-rzg2l-gpt.c` drives Renesas RZ/G2L GPT hardware, mapping eight counters to sixteen logical PWM outputs. Each counter has two subchannels with separate compare/output bits but shared mode, prescaler, and period. Only normal polarity is implemented.

## APIs, control flow, and state

`struct rzg2l_gpt_chip` stores MMIO, lock, kHz clock rate, cached period ticks, and request/enable counts. Mapping helpers derive hardware channel, subchannel, and sibling. `rzg2l_gpt_config()` caps period, enforces sibling shared-period constraints, programs saw-wave mode, up counting, prescaler, period, compare, counter reset, and buffer disable. Enable/disable manipulate GTIOR output bits and shared `GTCR_CST`; `get_state()` reads GTCR/GTPR/GTCCR.

Software caches period ticks and counts; hardware registers persist under an always-enabled managed clock.

## Dependencies and integration points

It binds `renesas,rzg2l-gpt`, uses MMIO, reset deassertion, exclusive clock-rate APIs, and scoped mutex guards.

## Risks and test signals

Sibling outputs must share period; shorter conflicting periods return `-EBUSY`, longer requests may be coerced to the cached period. Disabled outputs are inactive. Test all outputs, sibling enable/disable interactions, period conflict behavior, clock-rate validation, and readback conversions.
