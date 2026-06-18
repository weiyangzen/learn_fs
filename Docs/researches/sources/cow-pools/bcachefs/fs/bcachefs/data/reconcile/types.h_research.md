# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/types.h

## Role

`reconcile/types.h` defines in-memory filesystem state for the reconcile subsystem.

## Main Structure

`struct bch_fs_reconcile` contains:
- reconcile thread pointer and kick counter,
- running flag,
- wait timing fields,
- current phase,
- work position and work stats,
- progress indicator,
- scan start/end and scan stats,
- in-flight option-change scan hashtable plus lock,
- battery/power notification state when power-supply support is enabled.

## Use

This state backs the background reconcile worker and option-change scan tracking. It coordinates pending work scans, progress reporting, and power-aware behavior.
