# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs_utils.c

Purpose: provides shared formatting helpers for PM debugfs status tables backed by firmware PM info register arrays.

Important APIs: `adf_pm_scnprint_table_upper_keys` and `adf_pm_scnprint_table_lower_keys`. Both call `pm_scnprint_table`, which formats table rows as `KEY: value` after extracting masked bitfields from register words.

Control flow and state: no persistent state. For each `pm_status_row`, it uppercases or lowercases the row key, extracts `field_mask` from `pm_info_regs[reg_offset]` with `field_get`, and appends to a caller buffer using `scnprintf`.

Dependencies and integration: uses Linux bitfield and string case helpers; depends on table entries created with macros from `adf_pm_dbgfs_utils.h`. Consumed by device-specific PM status printers.

Risks and test signals: `wr` accumulation assumes `buff_size - wr` remains valid; callers must size buffers sufficiently. Test mixed masks, upper/lower formatting, table lengths, and boundary buffer sizes.
