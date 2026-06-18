# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_actions_slpc_abi.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_actions_slpc_abi.h

### Purpose
`guc_actions_slpc_abi.h` defines the GuC SLPC shared-data layout, task/frequency/override structures, event IDs, parameter IDs, and H2G request format used for firmware-driven GT power management.

### Important APIs, Types, And Functions
Important definitions include `SLPC_SHARED_DATA_SIZE_*`, `SLPC_MAX_OVERRIDE_PARAMETERS`, `enum slpc_param_id`, `enum slpc_event_id`, task-state flags, `struct slpc_task_state_data`, `struct slpc_shared_data_header`, `struct slpc_override_params`, `struct slpc_shared_data`, `struct slpc_context_frequency_request`, and `GUC_ACTION_HOST2GUC_PC_SLPC_REQUEST` field masks.

### Control Flow
There is no C control flow. The layout describes how host and GuC exchange SLPC state and how host emits SLPC events with an event ID, argument count, and event data dwords.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state lives in the shared data buffer allocated elsewhere and interpreted through these structs. Dependencies are Linux packed types and GuC HXG definitions used by senders. Integration points are `intel_guc_slpc` initialization, frequency controls, RC6/media-ratio policy, and power-profile handling. Risks include packed layout mismatch, size/alignment mistakes, and firmware parameter ID drift. Test signals include SLPC reaching `RUNNING`, valid task-state/frequency fields, accepted parameter set/unset events, and power-management behavior matching requested limits.
