# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_vbif.h

Purpose: declares parameter structures and public functions for DPU VBIF programming.

Important APIs and types: `struct dpu_vbif_set_ot_params` carries XIN id, pipe/debug number, dimensions, frame rate, read/write direction, and WFD marker. `struct dpu_vbif_set_memtype_params` describes a XIN/cacheability pair but is not consumed by the adjacent implementation. `struct dpu_vbif_set_qos_params` carries XIN id, debug pipe number, and real-time classification. Public functions configure OT limits, QoS remap, error clearing, memtype initialization, and debugfs setup.

Control flow and integration: DPU plane/performance code can assemble OT and QoS parameters for each hardware client and call into `dpu_vbif.c`; KMS init can call memory type setup and debugfs registration.

State and persistence: the header has no state; hardware register persistence is managed by the implementation and lost on reset or power cycle.

Dependencies: includes `dpu_kms.h`, so users get DPU KMS and catalog types. Debugfs prototype assumes `struct dentry` visibility through included headers or compile context.

Risks: parameter structs must stay aligned with hardware ops and catalog interpretation. Width, height, and frame-rate values directly affect dynamic OT choice, so stale or zero values can underprogram bus limits.

Test signals: compile tests for all users, plus runtime coverage for read and write clients, WFD paths, and RT/NRT QoS table selection.
