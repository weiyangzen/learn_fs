# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/synth.c

## Purpose
This file fetches and exposes ZL3073x synthesizer state. Synthesizers drive outputs and are associated with DPLL channels.

## Important APIs
`zl3073x_synth_state_fetch()` reads one synthesizer’s control and frequency parameters from hardware. `zl3073x_synth_state_get()` returns the cached state.

## Control flow
Fetch reads the direct synth control register, then under `multiop_lock` loads the synth mailbox and reads base, multiplier, numerator, and denominator. It rejects zero denominator to protect later frequency calculations and logs the computed frequency.

## State and persistence
`zldev->synth[index]` caches invariant synthesizer state. This driver does not provide a synth state setter; synth configuration is treated as hardware/firmware-defined and re-fetched on full start.

## Dependencies and integration
It depends on core mailbox/register helpers and `synth.h`. Output frequency calculations, output pin registration, phase granularity, and DPLL-output association use this cached state.

## Risks and tests
Incorrect frequency components affect every output frequency and pin property. Tests should cover zero denominator rejection, disabled synth handling, DPLL selection decoding, and output registration for synths tied to different channels.
