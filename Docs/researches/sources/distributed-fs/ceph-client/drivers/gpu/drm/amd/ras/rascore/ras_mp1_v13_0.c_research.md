# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1_v13_0.c

Purpose: this file implements MP1 v13 RAS bank-query commands by mapping generic RAS error types to firmware message IDs.

Important functions: `mp1_v13_0_get_bank_count()` maps UE to `RAS_MP1_MSG_QueryValidMcaCount` and CE/DE to `RAS_MP1_MSG_QueryValidMcaCeCount`, then calls `mp1_get_valid_bank_count`. It validates the output pointer and rejects counts at or above the per-query maximum. `mp1_v13_0_dump_bank()` maps UE to `RAS_MP1_MSG_McaBankDumpDW` and CE/DE to `RAS_MP1_MSG_McaBankCeDumpDW`, then calls `mp1_dump_valid_bank`. `mp1_ras_func_v13_0` exports these operations.

Control flow and state: this file is stateless. It relies entirely on `ras_core->ras_mp1.sys_func` and returns `-RAS_CORE_NOT_SUPPORTED` when required callbacks are missing.

Dependencies and integration: ACA/ECC collection uses these operations to retrieve valid MCA bank data. Firmware message constants are hard-coded for MP1 v13. Risks include off-by-one treatment of `MAX_UE_BANKS_PER_QUERY`/`MAX_CE_BANKS_PER_QUERY`, DE count validation using the CE limit only through the CE/DE branch, and error propagation mixing RAS status with Linux errno. Test signals should mock MP1 callbacks for UE, CE, DE, unsupported types, null output pointers, missing callbacks, maximum count boundary, and register dump indexing.
