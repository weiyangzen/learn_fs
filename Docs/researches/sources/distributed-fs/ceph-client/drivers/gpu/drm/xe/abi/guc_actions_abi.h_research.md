# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_actions_abi.h

Purpose: Defines xe GuC action ids, HXG field masks, context registration offsets, status enums, log controls, TLB invalidation modes, and GuC-to-GuC registration fields.

Important APIs/types: `GUC_ACTION_HOST2GUC_SELF_CFG`, `HOST2GUC_SELF_CFG_*`, `GUC_ACTION_HOST2GUC_CONTROL_CTB`, `enum xe_guc_action`, context/multi-LRC offset enums, TLB invalidation type/mode enums, and G2G masks.

Control flow: GuC CT/MMIO code builds action arrays using these constants. Self-config carries KLV data; CTB control toggles command transport; TLB invalidation selects scope and heavy/lite semantics.

State/persistence: Constants define firmware-visible protocol state; persistent state is in GuC firmware, CT buffers, contexts, scheduling policies, and xe GuC structs.

Dependencies/integration: GuC submit, TLB invalidation, page reclaim, context registration, logging, SR-IOV, and firmware communication code.

Risks/test signals: Strict numeric ABI, context offset/length mismatches, lite TLB invalidation safety, action id collisions, GuC CT selftests, context scheduling, TLB completion, and firmware compatibility.
