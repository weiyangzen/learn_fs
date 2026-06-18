## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pm_debugfs.c

Purpose: Provides the Gen4 debugfs PM status printer used by the common PM debugfs utilities.

Important APIs/functions: `adf_gen4_init_dev_pm_data()` sets `accel_dev->power_management.print_pm_status` and marks PM present. `adf_gen4_print_pm_status()` allocates a firmware PM info page and output buffer, DMA maps the PM info buffer, calls `adf_get_pm_info()`, formats fuse, PM, SSM, log/event, interrupt counter, host ack/nack counter, and hardware CSR sections, then copies to userspace via `simple_read_from_buffer()`.

Control flow and state: Reads firmware state on each debugfs read. It does not persist the snapshot, but it reports persistent PM counters stored in `accel_dev->power_management`. DMA mapping is always unmapped after admin query.

Dependencies/integration: Depends on `icp_qat_fw_init_admin_pm_info`, admin PM query, DMA mapping, PM debugfs table formatting helpers, Gen4 PM masks, and direct PM CSR reads.

Risks and test signals: Output is PAGE_SIZE-bounded; adding rows can truncate silently through `scnprintf`. Tests should check allocation and DMA mapping failures, admin query errors, `pos` handling for repeated reads, and field decoding for all row tables.
