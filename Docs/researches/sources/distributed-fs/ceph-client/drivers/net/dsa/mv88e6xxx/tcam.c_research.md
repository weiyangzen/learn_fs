# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcam.c

## Purpose
Implements TCAM hardware programming and ordered rule management for mv88e6xxx chips with TCAM support, backing tc flower offload.

## Important APIs, Types, and Functions
Exports `mv88e6xxx_tcam_entry_find`, `mv88e6xxx_tcam_entry_add`, `mv88e6xxx_tcam_entry_del`, and ops descriptors `mv88e6390_tcam_ops` and `mv88e6393_tcam_ops`. Static helpers write TCAM registers, wait for BUSY clear, read/load pages, flush entries, flush all entries, and program 6390/6393 entry pages.

## Control Flow and State
Software state is `chip->tcam.entries`, an ordered list keyed by priority and cookie with hardware index tracking. Insertions walk from the tail, move lower-priority entries down by flushing/re-adding them, assign the new index, and program the entry. Deletes flush the removed index, shift following entries up, flush the final stale slot, remove the list node, and free it. Hardware state is page-based TCAM key/action content plus DPV action registers.

## Dependencies and Integration Points
Depends on `chip->info->tcam_addr`, `chip->info->num_tcam_entries`, `chip->info->ops->tcam_ops`, list management, `mv88e6xxx_write`, `mv88e6xxx_wait_bit`, and port masks. `tcflower.c` constructs entries and calls these APIs under the register lock.

## Risks and Test Signals
Risks include list/hardware divergence on partial insert failure, not rolling back moved entries, off-by-one capacity/index errors, masked frame byte programming mistakes, and 6393 extension selection assumptions. Test signals include priority ordering tests, add/delete churn, ENOSPC behavior, hardware packet matches, trap DPV validation, and teardown after partial failures.
