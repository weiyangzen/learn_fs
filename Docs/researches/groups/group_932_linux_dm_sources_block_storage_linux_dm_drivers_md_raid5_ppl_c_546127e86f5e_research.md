# Group Research: group_932_linux_dm_sources_block_storage_linux_dm_drivers_md_raid5_ppl_c_546127e86f5e

Scope checked against `Docs/research_subset_a.md`: `sources/block-storage/linux-dm` is included in subset A. The listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid5-ppl.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/raid5-ppl.c

Read completely: 1557 lines, 43475 bytes.

## Purpose
Implements Linux MD RAID5 Partial Parity Log support, used to close the RAID5 write hole without the full write journal. The file logs enough partial parity information before writes reach the array so that, after an unclean shutdown, parity can be reconstructed for stripes whose data may have reached disk but whose parity may not have.

## Main Interfaces
- Runtime parity preparation: `ops_run_partial_parity()`.
- Write trapping and log submission: `ppl_write_stripe()`, `ppl_write_stripe_run()`, `ppl_stripe_write_finished()`.
- Quiesce and flush handling: `ppl_quiesce()`, `ppl_handle_flush_request()`.
- Recovery and log loading: `ppl_init_log()`, `ppl_load()`, `ppl_load_distributed()`, `ppl_recover()`, `ppl_recover_entry()`.
- Device membership changes: `ppl_modify_log()`.
- Teardown: `ppl_exit_log()`.
- Sysfs write hint control: `ppl_write_hint`.

## Core Data Model
`struct ppl_conf` is shared by all per-disk logs and is stored in `r5conf->log_private`. It tracks the owning `mddev`, child logs, block size used in header entries, array signature, global log sequence, mempool/biosets, recovery counters, no-memory retry stripes, and block write hint.

`struct ppl_log` represents one log area associated with one RAID member disk. RAID5 writes are logged to the PPL area on the parity disk for the stripe. Each log owns an ordered `io_list`, a `current_io` gathering stripes, the next log sector, entry-space sizing, multi-PPL mode, write-cache state, and a bitmap of member disks that must be flushed before the next unit is considered complete.

`struct ppl_io_unit` represents one PPL write. It owns the header page, entry count, accumulated partial parity size, sequence number, list of associated stripes, pending stripe/flush counters, submission state, and an inline bio with small inline biovec storage.

## Runtime Control Flow
`ops_run_partial_parity()` computes the partial parity page for a stripe. In read-modify-write mode it copies the already pre-xored parity device page. In reconstruct-write mode it XORs all up-to-date, non-updated data pages. Full-stripe writes do not need partial parity entries.

`ppl_write_stripe()` rejects stripes that are already attached to a PPL IO, syncing, missing a PPL page, or lacking a writable/in-sync parity device. Otherwise it selects the child log for the stripe parity disk, traps the stripe, bumps the stripe reference, and calls `ppl_log_stripe()`.

`ppl_log_stripe()` creates or reuses the current IO unit, records modified data sector coverage in a `ppl_header_entry`, appends consecutive compatible stripes to the previous entry when possible, updates `data_size`, `pp_size`, and CRC32C for partial parity pages, then links the stripe into the IO unit. If allocation fails, the stripe is placed on `no_mem_stripes` for later retry.

`ppl_write_stripe_run()` walks all child logs and submits the first unsubmitted IO unit in each log. `ppl_submit_iounit()` finalizes entry/header checksums, converts `data_sector` to the configured log block size, selects the log offset, writes the header plus partial parity pages with `REQ_FUA`, chains extra bios when the inline bio fills, and records which write-cache-enabled disks need a flush.

`ppl_log_endio()` marks the parity-log device faulty on write failure, releases every trapped stripe back to RAID5 handling, and lets normal data/parity writes proceed. `ppl_stripe_write_finished()` decrements the IO unit’s pending stripe count; when all associated stripes have written, it either issues required `REQ_PREFLUSH` bios through `ppl_do_flush()` or frees the IO unit through `ppl_io_unit_finished()`.

## Recovery Flow
Recovery scans each member’s PPL area with `ppl_load_distributed()`, validating each header checksum and signature, and selecting the newest valid generation. Multi-PPL areas are walked by advancing over each header and its recorded partial parity payload. If the array is being started dirty, the newest valid log is passed to `ppl_recover()`.

`ppl_recover()` validates each entry’s partial parity checksum before recovery. CRC mismatches increment `mismatch_count` and skip that entry, while valid entries call `ppl_recover_entry()`. After entries are processed it flushes the block device cache.

`ppl_recover_entry()` reconstructs parity block by block. It maps logged RAID sectors back to member disks with `raid5_compute_sector()`, reads every required modified data block, XORs them into a scratch page, optionally XORs the saved partial parity block, then writes the resulting parity block to the parity disk recorded in the log entry. It handles single-disk writes, multi-disk writes, full-stripe writes with no partial parity, and more general layouts that this implementation can recover even if it does not normally generate them.

After load/recovery, `ppl_write_empty_header()` zeroes the PPL space and writes a valid empty header so stale logs do not collide with future recovery.

## Initialization And Validation
`ppl_init_log()` enables PPL only for RAID5, rejects bitmap and journal configurations, requires 4 KiB pages, and refuses arrays wider than the per-log flush bitmap can represent. It allocates `ppl_conf`, the IO mempool, biosets, and one child log per RAID disk.

For internal metadata, the PPL signature is derived from the MD UUID and entries use 512-byte units. For external metadata, the logical queue block size is used and signatures are accepted from userspace-managed headers, with an additional check that all member headers agree.

`ppl_validate_rdev()` ensures the configured PPL area has room for a 4 KiB header plus at least one stripe of log data, rounds log data space down to a stripe multiple, and rejects overlap with array data or the MD superblock. `ppl_init_child_log()` enables multi-PPL cycling when the area is large enough for at least two full log regions and detects member write-cache state from the queue.

## State And Synchronization
Per-log mutation is protected by `ppl_log::io_mutex`; IO list access uses `io_list_lock`. No-memory retry stripes are protected by `no_mem_stripes_lock`. IO completion uses atomic pending counters for stripe writes and flush bios. `ppl_quiesce()` waits until each log has no submitted IO unit at the head of its list, coordinating with `wait_for_quiescent`.

## Integration Points
This file is tightly coupled to MD RAID5 internals: `stripe_head`, `r5conf`, `r5dev` flags, RAID5 geometry helpers, stripe reference handling, MD device fault handling, recovery checkpoints, and MD sysfs attributes. It also uses block-layer bios, biosets, FUA/prefush operations, `sync_page_io()`, async_tx XOR/memcpy helpers, CRC32C checksums, mempools, and Linux page allocation.

## Notable Behaviors
- PPL logs are distributed: a stripe is logged on the same member that holds parity for that stripe.
- Full-stripe writes log metadata only and rely on recovery to recompute parity from all data disks.
- Partial parity checksums are accumulated incrementally as stripes are added to an IO unit.
- If component write-back cache is enabled, completion of an IO unit can require explicit flushes for disks touched by the logged write.
- Multi-PPL mode cycles through several PPL regions when sufficient member space is configured, selecting the newest valid generation during recovery.
- Successful dirty-start recovery with no mismatches can mark the array clean by setting `recovery_cp = MaxSector`.

## Risks And Review Focus
- Correctness depends on log entry coalescing matching the recovery interpretation of `data_sector`, `data_size`, `pp_size`, chunk size, and modified data disk count.
- Recovery is deliberately conservative: missing data disks, read failures, CRC mismatches, or signature mismatches can prevent parity repair or force device errors.
- The log header checksum is computed after zeroing the checksum field, while entry checksums are stored as inverted CRC32C; any format change must preserve this convention.
- `disk_flush_bitmap` is per log but records touched member disks; widening RAID disk count beyond bitmap capacity is explicitly rejected.
- PPL area validation must stay aligned with MD metadata placement rules, because overlap with data or superblock areas would corrupt the array.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid5-ppl.c -->