# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/core.h

## Purpose
This header is the central internal interface for the ZL3073x driver. It defines chip flags, the per-device state container, register/HW access APIs, and inline helpers that translate pin/output/reference IDs into cached hardware properties.

## Important APIs and types
Important types are `enum zl3073x_flags`, `struct zl3073x_chip_info`, `struct zl3073x_dev`, and `struct zl3073x_hwreg_seq_item`. It declares probe/start/stop, typed register helpers, mailbox operation, HW register helpers, phase averaging, and reference phase measurement refresh. Inline helpers map input pins to refs, output pins to output pairs, check P/N identity, read cached ref/out/synth properties, compute output pin frequency, and test output pin enablement under signal-format constraints.

## Control flow and state
The header’s inline helpers are used throughout DPLL pin registration and callbacks. `struct zl3073x_dev` is the driver’s runtime state root, combining the Linux device, regmap, variant info, mailbox serialization mutex, cached hardware state arrays, DPLL list, monitor worker, devlink clock ID, and phase averaging factor.

## Dependencies and integration
It includes `chan.h`, `out.h`, `ref.h`, `regs.h`, and `synth.h`, so it ties the state submodules together. Transport modules call `zl3073x_devm_alloc()` and `zl3073x_dev_probe()` through this interface.

## Risks and tests
Frequency helpers divide by cached divisors; fetch paths must reject zero divisors before these helpers are used. Output pin enablement and frequency depend on signal-format interpretation, so tests should cover differential, 1P, 1N, two-output, and N-div formats.
