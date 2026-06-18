# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_types.h

Purpose: central state definition for the Xe GuC object and small GuC managers. It aggregates firmware, logging, ADS, CT, buffer cache, capture, power conservation, doorbells, submission state, hwconfig, SR-IOV relay, engine activity, notify register, and control parameters.

Important types: `struct xe_guc_db_mgr`, `struct xe_guc_id_mgr`, and `struct xe_guc`. Key nested state is `submission_state` with ID manager, `exec_queue_lookup` xarray, `stopped`, `reset_blocked`, lock, `enabled`, `initialized`, and fini waitqueue.

Control flow: fields are initialized across GuC firmware bring-up, submission init, CT setup, ADS setup, hwconfig retrieval, relay setup, and power management. Submission code relies on the xarray and ID manager under `submission_state.lock`.

State/persistence: this structure is long-lived per GT. Several nested objects own BOs or firmware state managed by DRM/devm lifetimes. Atomic fields allow reset and submission stop state to be observed in CT handlers and scheduler paths.

Dependencies/integration: includes many GuC component type headers plus xarray/idr and register definitions. It is referenced by nearly every GuC subsystem.

Risks/test signals: because this type is a shared hub, field lifetime and locking documentation matter. Submission ID manager and doorbell manager both rely on `submission_state.lock`; tests should cover init/fini ordering and reset while queues are live.
