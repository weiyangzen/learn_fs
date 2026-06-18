# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp_fw_funcs.c

Purpose: Builds NVMe/TCP firmware task contexts and SQEs for host read, host write, initial connection request, and task cleanup operations.

Important APIs/types/functions: `nvmetcp_is_slow_sgl()` classifies SGLs that require slow-path representation. `init_scsi_sgl_context()` copies SGL address/length metadata and up to four cached SGEs into firmware context. `init_sqe()` fills `struct nvmetcp_wqe` flags, task ID, command/middle-path/cleanup type, continuation length, and SGE count. `init_default_nvmetcp_task()`, `init_ustorm_task_contexts()`, and `init_rw_nvmetcp_task()` initialize E5 storm contexts. Exported functions are `init_nvmetcp_host_read_task()`, `init_nvmetcp_host_write_task()`, `init_nvmetcp_init_conn_req_task()`, and `init_cleanup_task_nvmetcp()`.

Control flow: Read/write setup zeroes the task context while preserving CDU validation, stores opaque and CCCID values, copies/swaps PDU and NVMe command dwords into Y-storm task headers, initializes M-storm/U-storm aggregate/static fields, places SGL metadata in transmit or receive storm context depending on I/O direction, computes expected receive/ack lengths, and optionally marks slow I/O. Login/initial-connection setup uses the non-I/O header size, initializes separate TX/RX SGL contexts if sizes are nonzero, and emits a middle-path SQE. Cleanup only emits a cleanup SQE if an SQE pointer is present.

State and persistence: The functions mutate caller-owned task context and optional SQE memory. They do not allocate or retain resources. Firmware later consumes the initialized context via task IDs and connection ICIDs.

Dependencies/integration: Depends on storage common, NVMe/TCP common HSI layouts, public NVMe/TCP interface task params, endian helpers, `SET_FIELD()` bit macros, and QED-specific header-size constants.

Risks: Header dword copying intentionally byte-swaps command/PDU words for firmware requirements; this is fragile if firmware layout changes. `init_sqe()` may receive `NULL` SGL params for cleanup and must return before dereferencing. Slow-SGL threshold and cached-SGE count must match firmware expectations. Unaligned casts from PDU pointers to `u32 *` assume suitable alignment from callers.

Test signals: Validate read/write/login contexts against firmware HSI golden data, zero-length I/O, incapsule write data, slow-SGL versus cached-SGL paths, IPv-independent header swapping, cleanup with and without SQE, and boundary SGE counts around `SCSI_NUM_SGES_SLOW_SGL_THR` and four cached SGEs.
