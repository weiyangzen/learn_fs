# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/init.c

## Role

Handles journal bucket allocation, deletion, device journal initialization, filesystem journal startup/shutdown, and journal object allocation.

## Major Responsibilities

- Allocates additional journal buckets on a device and persists them to the superblock.
- Deletes a journal bucket and adjusts ring indices.
- Allocates default journal space per device.
- Stops per-device and filesystem-wide journal activity safely.
- Starts journal runtime state from `journal_start_info`.
- Initializes replay pins and device replica references for journal entries.
- Sets replay-done/running flags after recovery.
- Initializes/exits device journal arrays, biosets, work items, workqueues, FIFOs, and buffers.

## Startup Details

`bch2_fs_journal_start()` clamps `cur_seq` above blacklisted sequences, rejects sequence overflow, sizes the pin FIFO based on the recovery window plus slack, initializes replay pins as `unreplayed`, establishes `seq`, `seq_ondisk`, `last_seq`, rewind bounds, and aligns `in_flight.front/back` with sequence numbering.

For each replayed journal entry, it records the replica device set on the corresponding pin and validates that journal replicas were represented in filesystem replica metadata unless degraded.

## Notable Details

- Default journal size is about 1/128 of device buckets, clamped to at least `BCH_JOURNAL_BUCKETS_MIN` and at most 8192 buckets or 8 GiB worth of sectors.
- `in_flight` starts with 256 slots and is sequence-aligned manually instead of using `init_fifo()`.
- Shutdown waits for reclaim, flushes all pins, writes metadata, quiesces bookkeeping, and verifies the last empty sequence when possible.
