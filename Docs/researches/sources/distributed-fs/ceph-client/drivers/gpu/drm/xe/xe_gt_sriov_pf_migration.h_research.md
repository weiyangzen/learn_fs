# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_migration.h

Purpose: declares PF GT-level VF migration helpers and the ring interface between PF control and higher-level migration code.

Important APIs: component save/restore functions for GuC, GGTT, MMIO, VRAM; total size query; ring empty/full/free; save initialization and bitmap helpers; save producer/consumer; restore producer/consumer. Defines `XE_GT_SRIOV_PF_MIGRATION_GUC_DATA_MAX_SIZE` as an 8 MiB TODO-backed upper bound.

Control flow: callers start with `xe_gt_sriov_pf_migration_init`, then `save_init`, then query pending component types and produce packets; restore paths push packets into the ring and notify control processing.

State and persistence: no state in the header, but the API exposes ownership-sensitive `struct xe_sriov_packet *` flows where producers hand packets to rings and consumers must free them.

Dependencies and integration: forward-declares `struct xe_gt`, `struct xe_sriov_packet`, and packet type enum. Used by PF control and device-level migration uAPI code.

Risks: the API mixes synchronous component operations with asynchronous ring backpressure. Misinterpreting `NULL`, `ERR_PTR(-EAGAIN)`, and real packet returns from `save_consume` can break userspace migration loops.

Test signals: compile contract against PF control and migration orchestrator, plus packet ownership tests for all return-value cases.
