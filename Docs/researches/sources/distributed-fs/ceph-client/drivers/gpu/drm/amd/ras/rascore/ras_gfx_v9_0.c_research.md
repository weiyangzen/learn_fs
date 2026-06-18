# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx_v9_0.c

Purpose: this file implements the GFX v9 subblock mapping and support validation used by RAS TA error injection.

Important data/functions: `enum ta_gfx_v9_subblock` mirrors the TA-facing subblock numbering. `struct ras_gfx_subblock_t` stores name, TA subblock ID, hardware-supported error-type bitmask, and software-supported error-type bitmask. `RAS_GFX_SUB_BLOCK()` builds the large `ras_gfx_v9_0_subblocks[]` table. `gfx_v9_0_get_ta_subblock()` validates that the requested subblock index exists, has a populated table entry, is supported by hardware for the requested error type, and is supported by the driver before returning the TA subblock ID. `gfx_ras_func_v9_0` exports this operation.

Control flow and state: the file is stateless and table-driven. Unsupported entries return `-EINVAL` or `-EPERM`, with diagnostic logs for unsupported error types. There is no persistence.

Dependencies and integration: PSP trigger-error flow calls this through `ras_gfx_get_ta_subblock()` for `RAS_TA_BLOCK__GFX`, then packs the resulting subblock plus instance mask into the TA command. Risks include the driver and TA enums drifting out of sync, sparse table entries with null names, and bitmask interpretation mismatch between `enum ras_ta_error_type` values and the table's packed support flags. Test signals should enumerate every `RAS_GFX_V9__GFX_MAX` index, verify expected TA IDs, verify parity/CE/UE/poison support masks, and include invalid subblock/error-type combinations.
