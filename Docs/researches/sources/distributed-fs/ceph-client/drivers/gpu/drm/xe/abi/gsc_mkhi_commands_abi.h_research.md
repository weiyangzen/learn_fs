# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_mkhi_commands_abi.h

Purpose: Defines the MKHI GSC client ABI used by xe to query GSC host compatibility version.

Important APIs/types: `HECI_MEADDRESS_MKHI`, `struct gsc_mkhi_header`, `MKHI_GROUP_ID_GFX_SRV`, `MKHI_GFX_SRV_GET_HOST_COMPATIBILITY_VERSION`, and packed input/output structs.

Control flow: Driver emits a MKHI graphics-service compatibility-version request and reads project/compat version fields from the response.

State/persistence: Request/response packets are transient; compatibility result informs driver/GSC policy elsewhere.

Dependencies/integration: Included by `xe_gsc.c` and transported through the generic GSC command header/submit path.

Risks/test signals: Firmware ABI layout, nonzero result handling, reserved fields, unsupported compatibility versions, GSC probe version query, and packed-size checks.
