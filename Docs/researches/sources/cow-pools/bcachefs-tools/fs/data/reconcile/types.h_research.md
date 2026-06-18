# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/types.h

## Purpose
Defines runtime state for the reconcile background subsystem.

## Main Interfaces
- `struct bch_fs_reconcile` stores the reconcile thread pointer/kick counter, running flag, wait timing, current phase, current work position/stats/progress, scan range/stats, in-flight option-change scan tracking, and power-supply state.
- `scans_in_flight` is an rhashtable protected by `scans_in_flight_lock`, with an init-done flag.
- Optional power-supply notifier state is compiled under `CONFIG_POWER_SUPPLY`.

## Dependencies
Includes bbpos types, move stats, progress indicators, mutexes, and rhashtable types.
