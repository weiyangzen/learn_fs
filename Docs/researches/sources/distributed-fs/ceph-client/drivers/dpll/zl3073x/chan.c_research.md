# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/chan.c

## Purpose
This file manages cached DPLL channel state for each ZL3073x channel: reference-selection mode, forced reference, per-reference priorities, monitor lock status, and selected-reference status.

## Important APIs
`zl3073x_chan_state_fetch()` reads initial channel configuration and status from hardware. `zl3073x_chan_state_update()` refreshes dynamic monitor/refsel status. `zl3073x_chan_state_get()` returns the cached state. `zl3073x_chan_state_set()` commits mutable channel configuration back to hardware.

## Control flow
Fetch reads `ZL_REG_DPLL_MODE_REFSEL`, status registers, then takes `multiop_lock`, asks the DPLL mailbox to load the channel configuration, and reads the packed priority registers. Set first skips unchanged configuration, writes `mode_refsel` directly when it changed, and only enters the mailbox path if priorities changed. The mailbox path reads current DPLL config, writes changed priority bytes, commits with `ZL_DPLL_MB_SEM_WR`, and updates the cache after success.

## State and persistence
State is stored in `zldev->chan[index]` as `cfg` and `stat` groups. Hardware state persists in device registers/firmware configuration, but the driver cache is runtime-only and rebuilt by fetch after probe/restart.

## Dependencies and integration points
The file depends on register access and mailbox helpers from `core.c` and bitfield accessors in `chan.h`. `dpll.c` uses it for DPLL mode, manual/automatic reference selection, pin priority, and lock status reporting.

## Risks and tests
Mailbox operations require `multiop_lock`; missing serialization can corrupt page/mailbox access. Partial writes before a later mailbox failure can leave hardware and cache out of sync, though the cache is updated only after successful commit. Test with automatic/manual mode switching, priority changes, lock-status polling, and fault injection on mailbox read/write.
