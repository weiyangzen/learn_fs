<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dump.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dump.c

Purpose: prints firmware, ROM/IML, FSEQ, and transport-visible error tables to the kernel log, and provides a lightweight validity probe for firmware error tables.

Important APIs/functions: exported `iwl_fwrt_dump_error_logs()` orchestrates LMAC, UMAC, TCM, RCM, IML/ROM, FSEQ, PC register, and function scratch dumps. `iwl_fwrt_read_err_table()` reads a minimal valid/error-id prefix. Private structs model LMAC, UMAC, TCM, and RCM error table layouts as read with device memory access.

Control flow: each dump helper checks that the relevant base address and TLV status flag exist, reads the table with `iwl_trans_read_mem_bytes()`, records error ids into `fwrt->dump`, and prints selected fields. LMAC handling can detect a hardware error value, reset and reactivate the NIC before retrying. The top-level function aborts if the device is disabled, then conditionally prints family-specific PC and scratch registers.

State and persistence: updates `fwrt->dump.lmac_err_id[]` and `fwrt->dump.umac_err_id` for later inclusion in coredumps. Output persists only in logs. A PNVM-missing assert prints the expected PNVM firmware name.

Dependencies/integration: uses transport memory/PRPH/CSR access, firmware image metadata, PNVM naming, assert description lookup, and device-family constants. Called by firmware assert paths before/around coredump collection.

Risks/test signals: printed strings are script-consumed, so formatting is part of the interface. Test no-table paths, init vs runtime LMAC base selection, multi-LMAC/TCM/RCM devices, PNVM missing asserts, hardware-error reset paths, and BZ scratch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dump.c -->
