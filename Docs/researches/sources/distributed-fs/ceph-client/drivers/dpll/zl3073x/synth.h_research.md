# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/synth.h

## Purpose
This header defines cached synthesizer state and inline helpers for synthesizer DPLL ownership, frequency, and enablement.

## Important APIs and types
`struct zl3073x_synth` stores frequency multiplier/base/numerator/denominator and control as invariants. Inline helpers decode the driving DPLL channel, compute frequency, and test enablement. It declares fetch/get APIs.

## Integration, risks, and tests
The core fetches all synths during full start; output and property helpers consume the cache. Frequency computation is central to output pin frequency and phase granularity, so denominator validation in `synth.c` plus output-frequency tests are important.
