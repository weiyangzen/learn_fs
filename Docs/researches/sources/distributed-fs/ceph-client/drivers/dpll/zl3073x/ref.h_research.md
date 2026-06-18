# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/ref.h

## Purpose
This header defines the ZL3073x input-reference cache and inline helpers for frequency, sync mode, paired sync reference, differential/enabled status, and monitor health.

## Important APIs and types
`struct zl3073x_ref` groups mutable config (`phase_comp`, `esync_n_div`, frequency base/mult/ratio, `sync_ctrl`), invariant `config`, and dynamic status (`ffo`, `meas_freq`, `mon_status`). Inline helpers expose FFO, measured frequency, computed reference frequency, frequency set/factorization, sync mode/pair get/set, differential/enabled flags, and status OK.

## Control flow and integration
The header’s helpers are used by property validation, DPLL pin callbacks, periodic notification checks, and state commit logic. `zl3073x_ref_freq_set()` mutates the cache candidate and leaves hardware commit to `zl3073x_ref_state_set()`.

## Risks and tests
Computed frequency multiplies base, multiplier, and ratio with integer math; test high and low frequencies. Sync bitfield helpers affect ref-sync and esync behavior, so connect/disconnect tests should validate the exact register encoding.
