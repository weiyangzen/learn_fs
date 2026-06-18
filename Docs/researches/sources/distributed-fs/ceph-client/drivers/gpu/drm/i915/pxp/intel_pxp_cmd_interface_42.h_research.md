# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd_interface_42.h

Purpose: Defines PXP firmware wire formats for API 4.2 init-session and stream-key invalidation commands.

Important APIs/types: `PXP42_CMDID_INIT_SESSION`, `PXP42_CMDID_INVALIDATE_STREAM_KEY`, `struct pxp42_create_arb_in/out`, `struct pxp42_inv_stream_key_in/out`, and `PXP42_ARB_SESSION_MODE_HEAVY`.

Control flow: No code. Backends populate these packed structs before sending to MEI/GSC firmware.

State/persistence: Wire payloads carry session id, protection mode, stream id, and command status. No driver state.

Dependencies/integration: Includes common PXP command header. Used by TEE backend and by GSC-CS invalidation even when API version is set to 4.3.

Risks: Packed layout and reserved fields must match firmware ABI exactly. Wrong API version/command id causes platform config or protocol failures.

Test signals: Firmware command success/failure status in PXP init/invalidation logs.
