# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd_interface_cmn.h

Purpose: Provides common PXP firmware ABI definitions shared by multiple API versions.

Important APIs/types: `PXP_APIVER()`, `enum pxp_status`, `struct pxp_cmd_header`, and stream id bit masks for session-valid, app-type, and session-id fields.

Control flow: None.

State/persistence: The packed header carries API version, command id, either status or stream id, and payload length excluding the header.

Dependencies/integration: Used by all PXP command-interface headers and both firmware backends.

Risks: Only status codes handled by the kernel are named; unknown codes must be logged and treated conservatively. ABI packing and bit masks must remain firmware-compatible.

Test signals: Backend error logs translate selected status codes to readable strings and set `platform_cfg_is_bad` for platform configuration failures.
