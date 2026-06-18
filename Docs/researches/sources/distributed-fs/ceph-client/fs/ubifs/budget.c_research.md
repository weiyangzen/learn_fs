# sources/distributed-fs/ceph-client/fs/ubifs/budget.c

## Purpose
This file implements UBIFS space budgeting: pessimistic reservation of flash space for data, dirty data, and index growth, plus free-space reporting.

## Important APIs, Types, and Functions
Key APIs are `ubifs_budget_space()`, `ubifs_release_budget()`, `ubifs_convert_page_budget()`, `ubifs_release_dirty_inode_budget()`, `ubifs_calc_min_idx_lebs()`, `ubifs_calc_available()`, `ubifs_reported_space()`, `ubifs_get_free_space_nolock()`, and `ubifs_get_free_space()`. Important helpers include `make_free_space()`, `run_gc()`, `shrink_liability()`, `do_budget_space()`, and growth calculators for index/data/dirty-data.

## Control Flow and State
Budget requests describe new pages/inodes/dentries and dirtied existing objects. `ubifs_budget_space()` validates request shape, computes index/data/dirty growth, adds those values under `space_lock`, and calls `do_budget_space()`. That function reserves enough index LEBs for the in-the-gaps commit method, computes available data space after index, GC, journal-head, deletion, dead, and dark-space reservations, and enforces reserved-pool permissions. On failure and non-fast requests, UBIFS tries to shrink liability by writeback, run GC, and run commit, retrying a bounded number of times.

`ubifs_release_budget()` subtracts reservations after the operation and moves index growth into `uncommitted_idx`, which commit later clears. Page-budget conversion changes a new-page reservation into dirty-page liability. Free-space reporting converts raw available bytes into user-visible capacity after UBIFS node and index overhead.

## Persistence, Dependencies, and Integration
Budget state is in-memory `c->bi`, LEB property stats, reserved pool IDs, and counters protected by `space_lock`, `lp_mutex`, and `commit_sem`. It integrates with writeback, garbage collection, commit, LPT/lprops accounting, VFS statfs, and permission checks (`CAP_SYS_RESOURCE`, fsuid/group).

## Risks and Test Signals
Risks include overcommitting flash, false ENOSPC, reserved-pool bypass, stale `nospace` flags, 64-bit arithmetic errors, and deadlock between writeback/GC/commit paths. Tests should include fill-volume workloads, random writes with compression variance, reserved-pool permission tests, GC/commit stress, power-cut recovery after heavy budgeting, and statfs free-space sanity against actual writable capacity.
