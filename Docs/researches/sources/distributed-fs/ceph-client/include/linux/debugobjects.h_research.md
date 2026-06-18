# sources/distributed-fs/ceph-client/include/linux/debugobjects.h

Purpose: Declares the debugobjects framework interface for tracking lifecycle state of selected kernel object types and catching init/activate/deactivate/destroy/free misuse.

Important APIs, types, and functions: Defines `enum debug_obj_state`, `struct debug_obj`, and `struct debug_obj_descr`. Public functions include `debug_object_init()`, `debug_object_init_on_stack()`, `debug_object_activate()`, `debug_object_deactivate()`, `debug_object_destroy()`, `debug_object_free()`, `debug_object_assert_init()`, `debug_object_active_state()`, `debug_objects_early_init()`, `debug_objects_mem_init()`, and optional `debug_check_no_obj_freed()`.

Control flow: Instrumented object users describe a type with callbacks for hints, static-object detection, and fixups. Lifecycle sites call debugobjects functions; the framework validates transitions through init, inactive, active, destroyed, and not-available states and may invoke fixups. In disabled builds the calls compile to no-ops.

State and persistence: Debug state is maintained in framework-owned in-memory hash/list entries; `struct debug_obj` references the tracked object address, descriptor, state, and active substate. No persistent state exists.

Dependencies and integration points: Depends on hlist/list and spinlocks. Used by timers, workqueues, RCU, and other debug-instrumented object types, with free-memory checking when enabled.

Risks and test signals: Risks include descriptor callbacks with side effects, false positives for static or stack objects, unbalanced active-state transitions, and build differences hiding bugs when disabled. Test lifecycle misuse injection, object free checking, on-stack objects, static objects, early boot init, and active-state expect/next transitions.
