# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_global_state.c

Purpose: implements i915 display global atomic objects, allowing shared display state to participate in DRM atomic transactions with duplicate/destroy callbacks, locking, serialization, commit dependency tracking, swap, and cleanup.

Important APIs/types/functions: private `struct intel_global_objs_state` stores per-atomic-state object entries and `struct intel_global_commit` tracks serialized commit completion with kref/completion. Public functions include `intel_atomic_global_obj_init()`, `intel_atomic_global_obj_cleanup()`, `intel_atomic_get_global_obj_state()`, old/new getters, `intel_atomic_swap_global_state()`, `intel_atomic_clear_global_state()`, `intel_atomic_lock_global_state()`, `intel_atomic_serialize_global_state()`, `intel_atomic_global_state_is_serialized()`, `intel_atomic_global_state_setup_commit()`, `intel_atomic_global_state_wait_for_dependencies()`, and `intel_atomic_global_state_commit_done()`.

Control flow: fetching a global object state asserts at least one CRTC mutex is read-locked, grows the atomic state's global-object array, duplicates current object state, references old/new states, and attaches it to the transaction. Locking all CRTC mutexes marks the object changed; serialization also requests a completion-backed commit. Swap replaces the live object state only for changed objects after write-lock assertion. Setup carries old serialized commits or creates new ones; wait blocks on prior commit completions; commit_done completes serialized commits after hardware programming.

State and persistence: each `intel_global_obj` has a live `state` and list node in `display->global.obj_list`. Each `intel_global_state` carries kref, object pointer, owning atomic state, optional commit, and changed/serialized flags. Commit objects persist until all referenced old/new states drop them.

Dependencies and integration: depends on DRM modeset locking/acquire contexts, i915 atomic state, CRTC mutexes, kref/completion, and object-specific duplicate/destroy callbacks supplied by subsystem users.

Risks: global state correctness relies on broad CRTC locking for read/write safety. Forgetting to mark changed discards new state. Serialized objects can deadlock or timeout if commit_done is not called. Cleanup expects exactly one reference to live object state.

Test signals: atomic tests with global state read-only, changed, and serialized objects; lockdep for modeset locks; dependency timeout injection; cleanup reference warnings; and concurrent commits touching shared watermarks/bandwidth-like state.
