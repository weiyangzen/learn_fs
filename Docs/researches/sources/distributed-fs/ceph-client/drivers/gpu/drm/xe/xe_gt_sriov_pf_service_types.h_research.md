# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_service_types.h

Purpose: defines PF GT SR-IOV service state for ABI version metadata and runtime register snapshots.

Important types: `struct xe_gt_sriov_pf_service_version` stores major/minor VF/PF ABI values. `struct xe_gt_sriov_pf_service_runtime_regs` stores selected register descriptors, captured values, and count. `struct xe_gt_sriov_pf_service` combines base/latest versions and runtime data.

Control flow: service init fills runtime table/value storage; service update refreshes values; relay response code reads version/runtime fields.

State and persistence: runtime values are cached in memory and are not persistent across driver reload. Version fields are part of PF service state but global negotiation is also coordinated by device-level service code.

Dependencies and integration: forward-declares `struct xe_reg`; embedded in `xe_gt_sriov_pf_types.h`.

Risks: `regs` points to static arrays owned by the implementation, while `values` is allocated; lifetime assumptions must remain valid for the GT lifetime.

Test signals: init/fini lifetime checks, runtime value allocation failure, and response queries after repeated updates.
