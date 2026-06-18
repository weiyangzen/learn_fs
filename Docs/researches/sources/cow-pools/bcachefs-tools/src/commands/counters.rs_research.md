# File Research: sources/cow-pools/bcachefs-tools/src/commands/counters.rs

This file implements `reset-counters`, a command for resetting persistent filesystem counters on an unmounted device.

Behavior:
- Accepts optional comma-separated counter names through `--counters` / `--counter`.
- Validates names against `COUNTERS`.
- Scans member devices from the provided device path.
- Opens the filesystem with:
  - `nostart = 1`
  - `degraded = very`
- Calls `bch2_counter_reset()` for either all counters or selected counters.
- Locks and writes the superblock to persist the reset.

Dependencies:
- `bch_bindgen::fs::Fs` for filesystem opening.
- Generated counter metadata from `bch_bindgen::sb::COUNTERS`.
- `crate::device_scan::scan_sbs()` for member discovery.
