# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/ref.c

## Purpose
This file manages ZL3073x input reference state: frequency encoding, monitor status, reference configuration, reference-sync/esync/N-div settings, and phase compensation.

## Important APIs
`zl3073x_ref_freq_factorize()` maps a requested frequency into base and multiplier values supported by the device. `zl3073x_ref_state_fetch()` reads one reference’s state from hardware. `zl3073x_ref_state_update()` refreshes monitor status. `zl3073x_ref_state_get()` returns cached state. `zl3073x_ref_state_set()` validates and commits mutable reference configuration.

## Control flow
Fetch handles differential N pins by copying the P pin’s shared config and invariants. For normal refs it reads monitor status, locks `multiop_lock`, loads the reference mailbox, reads config, frequency base/mult/ratio, esync divider, sync control, and phase compensation. Set rejects invariant changes, skips unchanged mutable config, loads the mailbox, writes changed fields, chooses 32-bit or 48-bit phase-comp register based on chip flag, commits through the reference mailbox, and updates the cache.

## State and persistence
`zldev->ref[index]` stores mutable config, invariant config bits, dynamic FFO/measured-frequency fields, and monitor status. Hardware configuration persists in device firmware/register state; dynamic measurements are refreshed by `core.c` periodic work.

## Dependencies and integration
The file depends on `core.c` mailbox/register helpers and `regs.h`. `dpll.c` uses it for input pin frequency, phase adjust, ref-sync, esync, status, and notification comparisons.

## Risks and tests
Frequency factorization accepts only frequencies divisible by known bases with 16-bit multipliers. Differential N pins assume P pin state was fetched first. Invariant rejection prevents accidental enable/differential changes through DPLL ops. Tests should cover factorization boundaries, 32-bit vs 48-bit phase compensation, differential copy behavior, mailbox failures, and monitor status transitions.
