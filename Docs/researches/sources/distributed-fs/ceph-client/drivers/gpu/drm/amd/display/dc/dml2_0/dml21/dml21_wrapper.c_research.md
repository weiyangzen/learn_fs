# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper.c

## Purpose
`dml21_wrapper.c` owns non-FPU DML2.1 context allocation, destruction, and copy semantics. It allocates the persistent DML2.1 context, embedded DML instance, and programming buffer used by validation and programming flows.

## Important APIs, types, and functions
Public APIs are `dml21_create()`, `dml21_destroy()`, `dml21_copy()`, and `dml21_create_copy()`. The internal `dml21_allocate_memory()` allocates `struct dml2_context`, `struct dml2_instance`, and `struct dml2_display_cfg_programming`, then wires mode-support and mode-programming pointers to the shared instance/display config.

## Control flow
Creation allocates memory and then calls FPU-side `dml21_init()`. Destroy frees the inner DML instance and programming buffer. Copy preserves destination-owned internal allocation pointers, memcpy-copies the source context and nested objects into destination allocations, restores all internal self-references, and reinitializes the copied instance with `dml2_initialize_instance()`. Create-copy combines allocation and copy.

## State and persistence behavior
The persistent state is heap-allocated kernel memory for the DML context and its nested DML instance/programming output. No on-disk persistence exists. The destroy path frees nested allocations but does not free the outer `struct dml2_context`, implying ownership remains with the caller or a higher wrapper.

## Dependencies and integration points
It depends on `vzalloc()`, `vfree()`, optional `DC_RUN_WITH_PREEMPTION_ENABLED`, DML top-level initialization, DML2 internal types, wrapper FPU functions, and DC FPU infrastructure. It is called during DC state/context lifecycle management.

## Risks and edge cases
Allocation failure after earlier successful allocations leaks memory because `dml21_allocate_memory()` returns false without cleanup. `dml21_destroy()` does not null-check or free the outer context. Copy relies on deep-copying only two nested allocations; new internal pointers added to `struct dml2_context` would need explicit restoration. Reinitialization after copy is required for internal references and is a key regression point.

## Test signals
Fault-injection tests for each allocation, create/destroy leak checks, create-copy equivalence tests, copied-context validation tests, and FPU/preemption wrapper build coverage are the main signals.
