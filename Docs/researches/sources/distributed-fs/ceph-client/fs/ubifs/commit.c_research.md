# sources/distributed-fs/ceph-client/fs/ubifs/commit.c

## Purpose
This file orchestrates UBIFS commits, which atomically write index and LEB-property updates and make the journal empty/replayable.

## Important APIs, Types, and Functions
Core functions are `ubifs_run_commit()`, `ubifs_bg_thread()`, `ubifs_commit_required()`, `ubifs_request_bg_commit()`, `ubifs_gc_should_commit()`, and internal `do_commit()`, `run_bg_commit()`, `wait_for_commit()`, and `nothing_to_commit()`. Debug support includes `dbg_old_index_check_init()` and `dbg_check_old_index()`.

## Control Flow and State
Commits are split into start and end phases. With `commit_sem` held for writing, `do_commit()` syncs journal heads, increments commit number, starts GC/log/TNC/LPT/orphan commit phases, captures LEB stats, then releases `commit_sem` so normal journal activity can resume while heavier end I/O runs. End phase writes TNC, LPT, and orphan updates, validates the old index in debug builds, updates the master node fields for root, log tail, index head, LPT heads, stats, and orphan flags, then finalizes log, GC, and LPT post-commit processing.

Commit state is tracked under `cs_lock` using states such as resting, background, required, running background, running required, and broken. `ubifs_run_commit()` either waits for an in-progress required commit or promotes/runs one synchronously. The background thread handles write-buffer sync and background commits when `need_bgt` is set.

## Persistence, Dependencies, and Integration
The commit persists UBIFS index root, LPT locations, log tail, orphan state, and master-node statistics. It integrates with journal heads, write buffers, GC, log, TNC, LPT, orphan subsystem, debug index checking, freezer-aware kthread behavior, and RO-error transition handling.

## Risks and Test Signals
Risks are severe: partial commit ordering bugs can break power-cut recovery; state-machine races can wait forever or allow concurrent commit corruption; failures must force read-only mode. Tests should include power-cut/replay simulations, concurrent writers plus background commit, GC-triggered commits, forced I/O errors, freezer suspend/resume with background thread, debug old-index checks, and mount-after-crash validation.
