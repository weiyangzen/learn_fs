# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/out.c

## Purpose
This file fetches, exposes, and commits ZL3073x output configuration state. Outputs are shared by P/N output pin pairs and drive DPLL pin frequency, phase adjustment, signal format, and esync behavior.

## Important APIs
`zl3073x_out_state_fetch()` initializes one output cache from hardware. `zl3073x_out_state_get()` returns the cached state. `zl3073x_out_state_set()` validates and commits mutable output configuration through the output mailbox.

## Control flow
Fetch reads the direct output control register, then under `multiop_lock` loads the output mailbox, reads mode, divisor, width, esync/N-div period and width, and phase compensation. Zero output or esync divisors are rejected. Set rejects invariant `ctrl` changes, skips unchanged configs, loads the mailbox, writes only changed mutable fields, commits with `ZL_OUTPUT_MB_SEM_WR`, and updates the cache after success.

## State and persistence
`zldev->out[index]` caches mutable `cfg` fields and invariant `ctrl`. Hardware output settings persist in device configuration; the cache is rebuilt from hardware on full start.

## Dependencies and integration
The file depends on `core.c` register/mailbox helpers and `out.h` masks. `dpll.c` changes output divisor, esync, phase compensation, and frequency through this API.

## Risks and tests
Zero divisors would cause later frequency helpers to divide by zero, so fetch validation is important. N-div and esync share fields, so callers must avoid incompatible combinations. Tests should cover every signal format, divisor changes, esync enable/disable, phase compensation, and mailbox fault injection.
