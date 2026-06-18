## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_pm_dbgfs.c

Purpose: Provides Gen6 PM debugfs status printing.

Important APIs/functions: `adf_gen6_init_dev_pm_data()` installs `adf_gen6_print_pm_status()` and marks PM present. The printer allocates zeroed PM info and output pages, DMA maps the info page, calls `adf_get_pm_info()`, formats PM fuse, PM info, SSM PM info, and hardware CSR sections, reads `ADF_GEN6_PM_INTERRUPT`, and returns data via `simple_read_from_buffer()`.

Control flow and state: Each read captures fresh firmware PM info. It stores only the print callback and `present` flag in `accel_dev->power_management`; no counters are maintained here.

Dependencies/integration: Depends on Gen6 PM masks, admin PM info query, DMA mapping, PM debugfs formatting helpers, and PMISC CSR access.

Risks and test signals: PAGE_SIZE output limits and DMA/admin failures are the main operational risks. Tests should validate allocation failure paths, DMA mapping error handling, admin query failure, repeated reads with offsets, and field decoding versus known firmware PM info.
