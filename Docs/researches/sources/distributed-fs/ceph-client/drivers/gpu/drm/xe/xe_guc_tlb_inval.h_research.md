# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_tlb_inval.h

Purpose: public header for binding a generic Xe TLB invalidation client to GuC-backed operations and for receiving GuC invalidation completion messages.

Important APIs: `xe_guc_tlb_inval_init_early` and `xe_guc_tlb_inval_done_handler`.

Control flow/state: init is called during GT/GuC setup before runtime invalidations, while the done handler is called from GuC CT G2H dispatch. The header carries no storage and uses forward declarations for `struct xe_guc` and `struct xe_tlb_inval`.

Dependencies/integration: bridges GuC submission/CT with the generic TLB invalidation subsystem.

Risks/test signals: malformed G2H length should return `-EPROTO`; initialization must select the correct backend ops for context versus ASID invalidation platforms.
