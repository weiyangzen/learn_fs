# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_pxp_commands_abi.h

Purpose: Defines xe's GSC PXP command ABI for protected content, HuC authentication, session initialization, and stream-key invalidation.

Important APIs/types: `HECI_MEADDRESS_PXP`, `PXP_APIVER()`, `PXP_MAX_PACKET_SIZE`, `enum pxp_status`, `struct pxp_cmd_header`, `PXP43_*` command ids, and packed request/response structs.

Control flow: Consumers build a PXP header with API version, command id, session/stream fields, and payload length; firmware returns status in the same union. Init-session encodes valid/app/session bits and ARB protection mode.

State/persistence: PXP session state lives in firmware and xe PXP code; this header defines transient packet layout and ids.

Dependencies/integration: GSC PXP/HuC submit paths and Linux size/type macros.

Risks/test signals: Direction-dependent header union, packet-size accounting excluding top GSC header, retryable vs fatal status handling, HuC auth, session create, invalidate key, bad API version, and packed layout checks.
