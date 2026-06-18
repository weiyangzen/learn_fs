# sources/distributed-fs/ceph-client/drivers/mtd/ubi/eba.c

## Purpose
`eba.c` implements the Eraseblock Association subsystem: the in-memory mapping from volume logical eraseblocks to physical eraseblocks, per-LEB locking, sequence-number allocation, read/write/unmap/copy operations, bad-block recovery, and EBA initialization from attach information.

## Important APIs, Types, And Functions
Private mapping types are `struct ubi_eba_entry` and `struct ubi_eba_table`. Public functions include `ubi_next_sqnum()`, `ubi_eba_get_ldesc()`, `ubi_eba_create_table()`, `ubi_eba_destroy_table()`, `ubi_eba_copy_table()`, `ubi_eba_replace_table()`, `ubi_eba_is_mapped()`, `ubi_eba_unmap_leb()`, `ubi_eba_read_leb()`, `ubi_eba_read_leb_sg()`, `ubi_eba_write_leb()`, `ubi_eba_write_leb_st()`, `ubi_eba_atomic_leb_change()`, `ubi_eba_copy_leb()`, `self_check_eba()`, and `ubi_eba_init()`.

## Control Flow
The lock tree (`ubi->ltree`) creates an RB-tree entry per currently locked `(vol_id, lnum)`. `leb_read_lock()`, `leb_write_lock()`, and `leb_write_trylock()` increment users and take a per-LEB rwsem; unlock paths remove the entry when users reaches zero. This allows concurrent reads while serializing writes and WL moves.

`ubi_eba_read_leb()` locks the LEB, checks fastmap mappings when needed, returns `0xFF` for unmapped dynamic LEBs, optionally reads and validates VID/data CRC for static volumes, reads data, schedules scrub on bitflips, and returns ECC/CRC errors. `ubi_eba_write_leb()` either writes into an existing mapped dynamic PEB or allocates a new PEB, writes a VID header with a fresh sequence number, writes data, updates the table, and retries bad PEBs. Static writes include used-EB/data-size/CRC metadata and prohibit rewrite by assertion. Atomic LEB change writes a replacement PEB with `copy_flag` and CRC under `alc_mutex`.

WL movement uses `ubi_eba_copy_leb()`: it try-locks the LEB to avoid deadlocks with unmap, verifies the mapping still points at the source PEB, reads data, trims dynamic trailing `0xFF`, writes VID/data to the target, rereads the VID header, and updates the EBA table under `volumes_lock`.

## State And Persistence
EBA tables are RAM-only but are reconstructed from attach scan/fastmap state and persisted indirectly through VID headers and fastmap. `ubi->global_sqnum` is initialized from attach max sequence and written to every new VID header. Mapping updates are paired with WL state: old PEBs are returned for erase/scrub, new PEBs come from `ubi_wl_get_peb()`, and fastmap synchronization uses `fm_eba_sem`.

## Dependencies And Integration Points
EBA depends on UBI I/O helpers for VID/data reads/writes, WL allocation/put/scrub, attach information, volume tables, CRC32, fastmap checkmaps, and bad-block policy. Character devices, gluebi, volume update code, WL, and fastmap call into EBA for user data and mapping state.

## Risks
Lock ordering is delicate: LEB locks, `fm_eba_sem`, `buf_mutex`, `volumes_lock`, and WL move locks must avoid deadlock. Several paths switch the whole device to read-only mode on unexpected write or mapping errors to preserve data. Fastmap cannot observe interrupted unmaps, so `check_mapping()` lazily fixes stale mappings during first access. Recovery from write failure assumes dynamic volumes for partial recovery and may retry only when the error appears recoverable. EBA table copy/replace during resize must not race with WL moves.

## Test Signals
Test unmapped dynamic reads, static CRC mismatch, bitflip scrub scheduling, direct writes to mapped and unmapped LEBs, write failure recovery on bad-block-capable MTDs, atomic LEB change after simulated power loss, WL copy races with unmap/delete, fastmap stale mapping cleanup, bad-block reserve accounting during `ubi_eba_init()`, and `self_check_eba()` against full-scan attach info.
