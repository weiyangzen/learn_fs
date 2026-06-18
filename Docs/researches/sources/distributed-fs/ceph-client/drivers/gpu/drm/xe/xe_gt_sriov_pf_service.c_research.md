# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_service.c

Purpose: implements PF GT-level services consumed by VFs over GuC relay: ABI handshake and runtime register query. It also snapshots platform-specific runtime registers that VFs cannot read directly.

Important APIs and functions: public `xe_gt_sriov_pf_service_init`, `xe_gt_sriov_pf_service_update`, `xe_gt_sriov_pf_service_process_request`, and `xe_gt_sriov_pf_service_print_runtime`. Internal register tables select runtime registers by graphics version/platform. Message handlers process `GUC_RELAY_ACTION_VF2PF_HANDSHAKE` and `GUC_RELAY_ACTION_VF2PF_QUERY_RUNTIME`.

Control flow: init allocates the runtime value array and stores a static register table. Update reads all runtime registers from PF MMIO. Handshake validates message length/MBZ and delegates global VF/PF version negotiation to device-level service code. Runtime query validates negotiated ABI >= 1.0, supports chunked reads with start/limit, and writes offset/value pairs to the response.

State and persistence: runtime register state lives in `gt->sriov.pf.service.runtime` with static `regs`, DRM-managed `values`, and count. Values persist until refreshed by `service_update`.

Dependencies and integration: depends on GuC relay ABI, HxG helpers, MMIO register definitions, PF service version negotiation, SR-IOV logging, and debugfs runtime printing. VF-side code uses the matching query protocol to cache inaccessible register values.

Risks: runtime register table selection must match platforms and VF expectations. Values can become stale if not refreshed after hardware state changes. Runtime query response sizing is in dwords and packed `reg_data` units; malformed limits or ABI drift can cause protocol errors.

Test signals: VF/PF ABI handshake, chunked runtime query with small response buffers, unsupported graphics version returning `-ENOPKG`, debugfs runtime dump, and comparing VF cached reads against PF snapshots.
