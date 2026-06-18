# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_global_state.h

Purpose: declares the generic i915 display global atomic object/state framework.

Important APIs/types/functions: defines `struct intel_global_state_funcs` with duplicate/destroy callbacks, `struct intel_global_obj` with list node/live state/function table, and `struct intel_global_state` with object pointer, atomic-state owner, commit pointer, kref, and `changed`/`serialized` flags. Declares init/cleanup, state getters, swap/clear, lock/serialize, commit setup/done/wait, and serialization-status helpers.

Control flow: no executable flow except data-shape declaration; callers embed/derive these base structs in subsystem-specific global state.

State and persistence: the structs declared here form the persistent live state and per-transaction duplicated state used by `intel_global_state.c`.

Dependencies and integration: depends on kref/list infrastructure and i915 atomic/display types. Used by shared display resource managers.

Risks: subsystem states must implement duplicate/destroy correctly and preserve the base fields. Mismanaging `changed` or `serialized` flags breaks swap and dependency ordering.

Test signals: compile users of embedded global states, run atomic commits that mutate shared resources, and verify no leaked references during driver unload.
