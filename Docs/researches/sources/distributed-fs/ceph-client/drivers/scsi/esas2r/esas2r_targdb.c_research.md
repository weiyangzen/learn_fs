<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_targdb.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_targdb.c

## Purpose

`esas2r_targdb.c` manages the ESAS2R in-memory target database. It initializes target slots, adds RAID logical devices and passthrough physical devices during discovery, removes targets, reports state transitions to the SCSI integration layer, and provides lookup/count helpers by SAS address, identifier, virtual target ID, and next present target.

## Important APIs, Types, and Functions

Externally used functions include `esas2r_targ_db_initialize()`, `esas2r_targ_db_remove_all()`, `esas2r_targ_db_report_changes()`, `esas2r_targ_db_add_raid()`, `esas2r_targ_db_add_pthru()`, `esas2r_targ_db_remove()`, `esas2r_targ_db_find_by_sas_addr()`, `esas2r_targ_db_find_by_ident()`, `esas2r_targ_db_find_next_present()`, `esas2r_targ_db_find_by_virt_id()`, and `esas2r_targ_db_get_tgt_cnt()`.

The central data type is `struct esas2r_target`, stored in the adapter's `a->targetdb` range. The file manipulates target state fields (`target_state`, `buffered_target_state`, `new_target_state`), addressing fields (`virt_targ_id`, `phys_targ_id`, `sas_addr`, `identifier`), geometry fields (`block_size`, `inter_byte`, `inter_block`), and flags such as `TF_PASS_THRU` and `TF_USED`.

## Control Flow

Initialization walks all target entries, clears them, and sets stable absent/invalid states. Discovery calls either `esas2r_targ_db_add_raid()` for RAID groups or `esas2r_targ_db_add_pthru()` for passthrough devices. RAID add validates the virtual ID and RAID dimensions, rejects already-present slots, fills block/interleave geometry, sets invalid physical ID, clears passthrough state, marks the entry used and present, and returns the target. Passthrough add first tries to find an existing target by device identifier to preserve identity across discovery, otherwise uses the current virtual ID if available, copies the identifier, records physical and virtual IDs, marks passthrough/used, and sets present.

Removal is intentionally minimal: `esas2r_targ_db_remove()` marks `target_state` as `TS_NOT_PRESENT`. `esas2r_targ_db_remove_all()` iterates present targets, calls remove under `mem_lock`, and optionally calls `esas2r_target_state_changed()` so the SCSI layer removes the device. `esas2r_targ_db_report_changes()` skips reporting while discovery is pending, then compares each target's `buffered_target_state` with `target_state` under `mem_lock`; changed states are copied to the buffered field and reported outside the lock.

Lookup helpers do straightforward linear scans over the target database. `find_next_present()` returns the first present target ID after a supplied ID or `ESAS2R_MAX_TARGETS` when no later target exists, which is used by ioctl enumeration.

## State and Persistence Behavior

The target database is volatile runtime state derived from firmware discovery. It persists in memory across command handling until discovery, removal, reset, or driver teardown changes it. `buffered_target_state` acts as a reporting latch so the SCSI layer is notified once per state change. Passthrough identifiers help reuse target slots for devices that were seen before. No disk state is written.

## Dependencies and Integration Points

The file depends on `struct esas2r_adapter`, `struct esas2r_disc_context`, target flags/states, `mem_lock`, debug/trace macros, and `esas2r_target_state_changed()` from `esas2r_main.c`. It is consumed by discovery code, SCSI add/remove event code, CSMI/HBA ioctl address lookup, and passthrough enumeration.

## Risks and Edge Cases

Most lookup helpers are lockless and rely on callers to hold `mem_lock` when needed; the call sites are inconsistent, so discovery or removal races can expose transient target data. `add_pthru()` can reuse a target found by identifier even if discovery's current virtual ID differs, which preserves identity but requires stale fields to be fully overwritten. `remove()` leaves flags and identity data intact, so absent entries can still match identifier/SAS lookups unless callers also check `target_state`. `add_raid()` rejects zero block size/interleave but does not validate interleave divisibility beyond computing `interleave / block_size`.

## Test Signals

Useful signals include initialization clearing all targets, RAID add rejecting invalid dimensions and duplicate present slots, passthrough add preserving identity across rediscovery, remove-all with and without notification, report-changes suppression during `AF_DISC_PENDING`, SCSI add/remove notifications for `TS_PRESENT`, `TS_NOT_PRESENT`, and LUN-change states, CSMI/HBA address lookup while targets are present and absent, and concurrent discovery/reset/ioctl stress around `mem_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_targdb.c -->
