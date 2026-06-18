# File Research: sources/block-storage/lvm2/lib/metadata/thin_manip.c

This file implements thin-pool metadata helpers, queued thin target messages, pool activation/update logic, sizing policy, and external-origin validation.

Main entry points:
- Thin pool access and checks: `data_lv_from_thin_pool()`, `find_pool_lv()`, `thin_pool_is_active()`, `thin_pool_feature_supported()`.
- Message lifecycle: `attach_thin_pool_message()`, `thin_pool_has_message()`, `update_thin_pool_lv()`.
- External origin handling: `attach_thin_external_origin()`, `detach_thin_external_origin()`, `validate_thin_external_origin()`, `thin_pool_supports_external_origin()`.
- Capacity checks: `thin_pool_metadata_min_threshold()`, `thin_pool_below_threshold()`, `thin_pool_check_overprovisioning()`.
- Metadata sizing and configuration: `get_default_allocation_thin_pool_chunk_size()`, `get_thin_pool_max_metadata_size()`, `get_thin_pool_crop_metadata()`, `thin_pool_set_params()`, `update_thin_pool_params()`.
- Thin identity helpers: `get_free_thin_pool_device_id()`, `lv_is_thin_origin()`, `lv_is_thin_snapshot()`, `lv_is_merging_thin_snapshot()`.
- Metadata initialization: `thin_pool_prepare_metadata()` uses configured `thin_restore` to seed a metadata LV.
- Safety validation: `check_new_thin_pool()`, `validate_thin_pool_chunk_size()`, `estimate_thin_pool_metadata_size()`.

Control flow:
- `attach_thin_pool_message()` queues create/delete messages on a thin pool segment and increments `transaction_id` when adding the first updating message.
- `update_thin_pool_lv()` activates the pool if needed, optionally suppresses dmeventd monitoring, validates create messages against pool thresholds, suspends/resumes the origin to deliver messages, clears the message list, then writes and commits VG metadata.
- `update_thin_pool_params()` derives chunk size, metadata size, discard mode, zeroing mode, crop policy, and max addressable data size from config, target features, and user input.
- `thin_pool_prepare_metadata()` temporarily activates the metadata LV, writes XML metadata into a temporary file, invokes `thin_restore`, and deactivates the LV.

Dependencies:
- Activation/status APIs: `lv_info`, `activate_lv_temporary`, `activate_lv`, `deactivate_lv`, `suspend_lv_origin`, `resume_lv_origin`, `lv_thin_pool_status`.
- VG persistence: `vg_write()`, `vg_commit()`.
- Config keys under allocation, activation, and global thin restore settings.
- Device-mapper thin constants and status structures.

Correctness notes:
- Thin transaction IDs are a core guard against applying stale messages or externally modified pools.
- Clustered VGs check related thin volumes, not just the pool LV itself.
- External origins are forced read-only and rejected if internal, writable, pool-like, active non-external-origin, or incompatible with chunk-size constraints.
- Device ID allocation is a naive max-plus-one search and does not fill holes.

Risks:
- Message delivery depends on activation/suspend/resume ordering while VG locks may be held.
- `thin_pool_prepare_metadata()` shells out through `exec_cmd` with configured tool/options and a proc-fd temporary input; failures must preserve deactivation.
- Metadata/chunk calculations mix sectors, extents, and target block limits, so unit mistakes would directly affect pool addressability.
