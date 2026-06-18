# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_actions_slpc_abi.h

Purpose: Defines the GuC SLPC power-control ABI: shared data layout, parameter ids, task/global states, event ids, task status/frequency masks, power profiles, and PC/SLPC request actions.

Important APIs/types: SLPC size macros, `enum slpc_global_state`, `enum slpc_param_id`, event/media/GUCRC enums, `struct slpc_task_state_data`, `struct slpc_shared_data`, `enum slpc_power_profile`, `GUC_ACTION_HOST2GUC_PC_SLPC_REQUEST`, and `GUC_ACTION_HOST2GUC_SETUP_PC_GUCRC`.

Control flow: xe GuC PC code maps/fills shared data, sets/unsets override parameters, sends SLPC events, and configures GUCRC host/firmware control. Firmware updates global/task state and override values.

State/persistence: The packed two-page shared buffer persists while SLPC is active and includes header, task state, override bits/values, and reserved mode-definition storage.

Dependencies/integration: xe GuC power-control/frequency/sysfs paths and GuC HXG message macros.

Risks/test signals: ABI-sensitive padding/sizing, parameter-id drift, frequency mask interpretation, the apparent `HOST2GUC_PC_SLPC_REQUEST_REQUEST_MSG_MIN_LEN` typo in max-len macro, GuC PC init, sysfs frequency tests, power profile changes, and shared-size assertions.
