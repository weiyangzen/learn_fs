# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/debug.h

## Purpose
`debug.h` defines the ath5k debug-level bitmask, the per-device debug state, and the conditional debug logging/dump API. It provides no-op inline replacements when debug support is disabled.

## Important APIs and types
- `struct ath5k_dbg_info`: stores the active debug bitmask.
- `enum ath5k_debug_level`: bits for reset, interrupt, mode, transmit, beacon, calibration, txpower, LED, band dumps, DMA, ANI, descriptor dumps, and all-level output.
- `ATH5K_DBG` and `ATH5K_DBG_UNLIMIT`: conditional debug print macros. The first is net-ratelimited, the second is not.
- Functions declared under `CONFIG_ATH5K_DEBUG`: `ath5k_debug_init_device`, `ath5k_debug_printrxbuffs`, `ath5k_debug_dump_bands`, and `ath5k_debug_printtxbuf`.
- Disabled-debug inline stubs keep callers compiled without runtime work.

## Control flow and integration
Implementation files call `ATH5K_DBG` at reset, interrupt, TX, beacon, calibration, DMA, ANI, and descriptor points. When enabled, the macros check `ah->debug.level` and call `ATH5K_PRINTK`; when disabled, the compiler sees empty inline functions. `ath5k_debug_init_device` is invoked after attach, while dump helpers are invoked from band setup, RX stop, and TX drain paths.

## State and persistence behavior
Only a per-device runtime bitmask is modeled here. The initial value comes from the `debug` module parameter in `debug.c`, and debugfs writes may toggle it. There is no persistent state.

## Dependencies
The header forward declares ath5k and SKB structures and depends on `ATH5K_PRINTK` from `ath5k.h` when debug is enabled. In the disabled path it includes `linux/compiler.h` for printf attributes.

## Risks and edge cases
- `ATH5K_DBG_UNLIMIT` can produce high log volume if enabled in hot paths such as beacon handling.
- Debug logging references `ah->debug.level`; callers must pass a valid `struct ath5k_hw *`.
- The no-op implementation changes observability substantially between debug and non-debug builds, so tests that rely on debugfs/log output must account for config.

## Test signals
Build both with and without `CONFIG_ATH5K_DEBUG`. In debug builds, enabling individual levels via debugfs should emit matching logs and dumps. In non-debug builds, callers should compile cleanly and produce no debugfs-dependent symbols or output.
