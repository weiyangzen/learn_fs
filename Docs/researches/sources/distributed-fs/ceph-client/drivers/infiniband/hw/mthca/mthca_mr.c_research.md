# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_mr.c

Purpose: manages mthca memory translation tables (MTTs), memory protection table (MPT) entries, memory keys, and memory region lifetime for DMA, physical, user, and fast memory registration paths.

Important APIs/functions: defines firmware-facing `struct mthca_mpt_entry` and private `struct mthca_mtt`; implements MTT buddy allocation (`mthca_buddy_*`), `mthca_alloc_mtt`, `mthca_free_mtt`, `mthca_write_mtt`, `mthca_write_mtt_size`, `mthca_mr_alloc`, `mthca_mr_alloc_notrans`, `mthca_mr_alloc_phys`, `mthca_free_mr`, `mthca_init_mr_table`, and `mthca_cleanup_mr_table`.

Control flow: MTT allocation picks an order large enough for the requested segment count and, on mem-free devices, maps backing ICM ranges. MTT writes either use the firmware `WRITE_MTT` mailbox path or optimized FMR writes directly into ioremapped Tavor/Arbel MTT memory. MR allocation allocates an MPT index, transforms it into the device key format, optionally maps an MPT ICM entry, populates the MPT mailbox, and transitions it with `SW2HW_MPT`. Free reverses with `HW2SW_MPT`, allocator release, table put, and MTT free.

State and persistence: maintains runtime MPT index allocation, MTT buddy bitmaps, optional reserved FMR MTT buddy state, and ioremapped FMR windows. Registered MRs persist only as hardware state until deregistration or device teardown.

Dependencies and integration: used by provider DMA/user MR verbs, PD privileged notrans MR setup, QP/SRQ/CQ buffer registration, and FMR support. Depends on `mthca_cmd`, `mthca_memfree`, PCI BAR ioremap, endian conversions, and mthca key layout quirks for Tavor, Arbel, and Sinai optimization.

Risks: key/index conversion is device-specific; wrong transformation can expose or invalidate memory. Buddy allocation is linear and can fragment under churn. Fast paths use direct MMIO/ioremapped writes with page-size constraints and BUG_ON checks. Cleanup comments note no active-MR leak verification.

Test signals: register/deregister user MRs with varied page counts, stress FMR and regular MTT allocation, validate remote access flags, run RDMA read/write/atomic traffic, and use fault injection for `SW2HW_MPT`, `WRITE_MTT`, and ICM table failures.
