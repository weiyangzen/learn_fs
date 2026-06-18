# File Research: sources/cow-pools/bcachefs-tools/src/commands/fs_usage.rs

This file implements the `usage` command for detailed filesystem space reporting.

CLI behavior:
- Default field is `rebalance_work`.
- `--fields/-f` accepts comma-separated field names.
- `--all/-a` enables replicas, btree, compression, rebalance/reconcile work, and devices.
- `--human-readable/-h` enables human-readable sizes.
- Defaults mountpoint argument to `.`.

Reported sections:
- Filesystem UUID, size, used, and online reserved.
- Replica/durability summary.
- Optional detailed replica rows.
- Optional compression stats.
- Optional per-btree usage.
- Optional rebalance or reconcile pending work.
- Device summary or full per-device breakdown.

Accounting behavior:
- Queries accounting through `BcachefsHandle::query_accounting()`.
- Chooses old `rebalance_work` or newer `reconcile_work`/`dev_leaving` accounting based on kernel metadata version.
- Sorts accounting entries by bpos before printing.
- Computes durability/degraded matrices for replicated data.
- Groups erasure-coded entries by data+parity configuration.
- Separately tracks cached and persistent reserved sectors.
- Reads device info from sysfs and per-device usage through the handle.

Dependencies:
- Accounting wrappers for decoding `DiskAccountingKind`.
- `Printbuf` for aligned text and size formatting.
- `sysfs` wrappers for device discovery and kernel version.
