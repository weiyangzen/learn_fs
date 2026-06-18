# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs_utils.h

Purpose: defines PM status table row descriptors and convenience macros for mapping fields in `icp_qat_fw_init_admin_pm_info` to printable debugfs rows.

Important types and macros: `PM_INFO_MEMBER_OFF` converts a struct member to a `u32` register-array offset. `PM_INFO_REGSET_ENTRY_MASK` and `PM_INFO_REGSET_ENTRY32` build `struct pm_status_row` entries. `struct pm_status_row` stores register offset, field mask, and key.

Control flow and state: header only. Generated tables are static data owned by PM-specific code.

Dependencies and integration: includes firmware admin PM info definition and Linux type/stddef helpers. Formatting functions are implemented in `adf_pm_dbgfs_utils.c`.

Risks and test signals: offset calculation assumes PM info is interpreted as a `u32` array and fields are aligned accordingly. Test generated row offsets against firmware struct layout and verify 32-bit/full-mask and subfield extraction.
