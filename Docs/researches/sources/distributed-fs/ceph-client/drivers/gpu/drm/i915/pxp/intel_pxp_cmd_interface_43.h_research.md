# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd_interface_43.h

Purpose: Defines PXP firmware API 4.3 command ids, maximum HECI sizes, HuC authentication payloads, and arb-session init payloads.

Important APIs/types: `PXP43_CMDID_START_HUC_AUTH`, `PXP43_CMDID_NEW_HUC_AUTH`, `PXP43_CMDID_INIT_SESSION`, `PXP43_MAX_HECI_INOUT_SIZE`, `PXP43_HUC_AUTH_INOUT_SIZE`, `pxp43_start_huc_auth_in`, `pxp43_new_huc_auth_in`, `pxp43_huc_auth_out`, `pxp43_create_arb_in/out`, and field masks for stream/session/protection flags.

Control flow: No code. GSC-CS and HuC paths fill these packed structs for firmware.

State/persistence: Payloads encode HuC DMA address/size, arb session id, app type, protection mode, and firmware status.

Dependencies/integration: Includes common command header and Linux size/page macros. Used by GSC-CS backend and HuC load/auth.

Risks: The max HECI size drives buffer allocation; mismatches risk truncation or `-ENOSPC`. Endianness differs between HuC address fields (`__le64` in one command, plain `u64` in another).

Test signals: GSC firmware reply status, HuC authentication result, and PXP session creation logs.
