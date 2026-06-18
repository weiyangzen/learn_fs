# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc_types.h

Purpose: defines the persistent HuC object embedded in Xe uC/GT state.

Important type: `struct xe_huc` containing `struct xe_uc_fw fw` and optional `struct xe_bo *gsc_pkt`.

Control flow/state: firmware lifecycle helpers update `fw` status, BO placement, load/auth state, and use `gsc_pkt` when authentication is routed through GSC/GSCCS.

Dependencies/integration: depends on generic uC firmware types and forward-declares `struct xe_bo`.

Risks/test signals: `gsc_pkt` lifetime must match managed BO lifetime and only be used when allocated. Tests should verify GSC-auth platforms allocate it and GuC-auth or VF paths do not require it.
