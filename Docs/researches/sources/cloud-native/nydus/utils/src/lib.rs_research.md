# sources/cloud-native/nydus/utils/src/lib.rs

Purpose: crate root for `nydus-utils`, exporting utility modules and defining common numeric rounding, delay, and lazy-drop helpers.

Important APIs/types/functions: macro imports for `log`, `serde`, `lazy_static`, and `nydus_api`. Re-exports `exec::*`, `InodeBitmap`, `reader::*`, and `types::*`. Public modules include async, compact, compress, config, crc32, digest, exec, filemap, inode_bitmap, logger, metrics, mpmc, reader, singleflight, trace, types, verity, and feature-gated `crypt`. Helper functions are `div_round_up`, `round_up`, `round_up_usize`, `try_round_up_4k`, `round_down_4k`, and `round_down`. `DelayType` and `Delayer` implement fixed/exponential sleeps. `lazy_drop` defers dropping an object on a spawned thread after 600 seconds.

Control flow: rounding helpers require power-of-two divisors via debug assertions and use `div_ceil` or bit masking. `try_round_up_4k` uses checked addition and fallible conversion to avoid overflow. `Delayer::delay` sleeps fixed duration or `2^attempts * time`, then increments attempts. `lazy_drop` moves a value into a background thread, sleeps ten minutes, then drops it.

State and persistence: no persistent state. `Delayer` tracks attempt count. `lazy_drop` extends object lifetime asynchronously.

Dependencies and integration points: root export surface for many Nydus crates. Rounding helpers are used by storage/readahead/alignment code. `lazy_drop` can help release large objects outside latency-sensitive paths.

Risks: `round_up`/`round_up_usize` can overflow in release builds because only debug assertions guard divisor properties and no checked arithmetic is used. `Delayer::BackOff` can overflow shift or duration multiplication for high attempts. `lazy_drop` spawns an untracked thread per call and requires `unsafe impl Send` wrapper instead of bounding `T: Send`; moving non-Send values across threads is unsound.

Test signals: tests cover 4 KiB rounding overflow/conversion behavior, usize rounding, generic round up/down/div helpers, and delayer attempt increments with zero-duration sleeps.
