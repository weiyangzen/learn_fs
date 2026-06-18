# sources/distributed-fs/ceph-client/drivers/mmc/core/debugfs.c

## Purpose
Debugfs visibility/control for MMC hosts and cards: IOS, capabilities, clock, error stats, fault injection, card state, and quirks.

## Important APIs, Types, And Functions
- `mmc_ios_show()` reports live bus electrical/timing state.
- `mmc_clock_opt_get/set()` reads or changes host clock while claiming the host.
- `mmc_err_state_get()`, `mmc_err_stats_show()`, and `mmc_err_stats_write()` expose/reset error counters.
- `mmc_caps_set()` and `mmc_caps2_set()` whitelist runtime capability toggles.
- `mmc_add_host_debugfs()`/`remove` and `mmc_add_card_debugfs()`/`remove` manage trees.

## Control Flow
Host add creates a debugfs directory and files; card add creates a child directory. Reads format current state. Writes can adjust clock/caps or reset stats. With fault injection enabled, host fault attributes are created.

## State And Persistence
Reflects live host/card fields. Error stats and capability/clock mutations persist for the host lifetime but not across reboot.

## Dependencies And Integration Points
Depends on debugfs, seq_file, fault injection, host claiming, and MMC core clock helpers. Compiled only with `CONFIG_DEBUG_FS`.

## Risks And Edge Cases
Debugfs can destabilize hardware by changing clocks/caps. Fault injection intentionally corrupts requests. Capability changes may diverge from actual board wiring.

## Test Signals
Debugfs host/card directories, successful `ios`/`err_stats`/state reads, valid clock changes, invalid clock rejection, and fault-injected request errors.
