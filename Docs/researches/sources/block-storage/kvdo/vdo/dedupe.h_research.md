# File Research: sources/block-storage/kvdo/vdo/dedupe.h

## Purpose
Declares public dedupe/hash-zone APIs and tunables used by VDO write, compression, statistics, sysfs, and admin paths.

## Forward Declarations
- `struct hash_lock`
- `struct hash_zone`
- `struct hash_zones`

## Public API Groups
### Hash Lock Operations
- `vdo_get_duplicate_lock()`
- `vdo_acquire_hash_lock()`
- `vdo_enter_hash_lock()`
- `vdo_continue_hash_lock()`
- `vdo_continue_hash_lock_on_error()`
- `vdo_release_hash_lock()`
- `vdo_share_compressed_write_lock()`

### Hash Zone Lifecycle/Admin
- `vdo_make_hash_zones()`
- `vdo_free_hash_zones()`
- `vdo_get_hash_zone_thread_id()`
- `vdo_drain_hash_zones()`
- `vdo_resume_hash_zones()`
- `vdo_finish_dedupe_index()`

### Statistics/Selection/Diagnostics
- `vdo_get_dedupe_statistics()`
- `vdo_select_hash_zone()`
- `vdo_dump_hash_zones()`
- `vdo_get_dedupe_index_state_name()`
- `vdo_get_dedupe_index_timeout_count()`

### Sysfs and Messages
- `vdo_message_dedupe_index()`
- `vdo_add_dedupe_index_sysfs()`
- `vdo_start_dedupe_index()`

### Tunables
- `vdo_dedupe_index_timeout_interval`
- `vdo_dedupe_index_min_timer_interval`
- `vdo_set_dedupe_index_timeout_interval()`
- `vdo_set_dedupe_index_min_timer_interval()`

## Research Notes
Most declarations are implemented in `dedupe.c`. The timeout-count accessor is declared here but is not implemented in the paired `dedupe.c` file read for this group.
