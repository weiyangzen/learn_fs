# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_dcb.h

Purpose: Declares the private DCB support structures and helper macros used by `bnxt_dcb.c` to translate Linux DCB configuration into HWRM queue data.

Important APIs, types, and functions: The header defines `bnxt_dcb`, `bnxt_cos2bw_cfg`, `bnxt_dscp2pri_entry`, `BNXT_LLQ()`, `BNXT_CNPQ()`, `BW_VALUE_UNIT_PERCENT1_100`, `HWRM_STRUCT_DATA_SUBTYPE_HOST_OPERATIONAL`, and the `bnxt_dcb_init()`/`bnxt_dcb_free()` prototypes.

Control flow: No executable flow lives here. `bnxt_dcb.c` uses the packed `bnxt_cos2bw_cfg` layout to copy queue bandwidth records into HWRM request slots, uses `BNXT_LLQ()` to decide whether a hardware queue profile is lossless for PFC remapping, and uses `bnxt_dscp2pri_entry` for one-entry DSCP priority updates.

State and persistence behavior: `bnxt_dcb` is a compact DCB state container, but current `struct bnxt` carries the active fields directly under `CONFIG_BNXT_DCB`. The header itself stores no state and defines runtime-only structures.

Dependencies and integration points: It depends on `<net/dcbnl.h>` and HSI queue profile constants included by implementation context. It is private to the bnxt driver DCB path and must align with HWRM queue command layouts.

Risks: The packed group inside `bnxt_cos2bw_cfg` is copied directly into firmware command arrays; layout drift would corrupt queue bandwidth programming. Queue profile macros depend on HSI constant values staying semantically stable.

Test signals: Build with `CONFIG_BNXT_DCB=y`, verify HWRM CoS-to-bandwidth requests for queue 0 and additional queues have correct byte layout, and exercise PFC remap on queue profiles classified by `BNXT_LLQ()`/`BNXT_CNPQ()`.
