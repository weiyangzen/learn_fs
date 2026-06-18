# sources/distributed-fs/ceph-client/kernel/livepatch/core.h

## Purpose
`core.h` is the internal livepatch core contract shared by the livepatch implementation files. It exposes the global serialization lock, active patch list iteration helpers, patch/free/replace helper prototypes, object-loaded predicate, and callback wrappers.

## Important APIs, Types, and Functions
It declares `extern struct mutex klp_mutex` and `extern struct list_head klp_patches`. Iteration macros `klp_for_each_patch()` and `klp_for_each_patch_safe()` abstract traversal of the global patch list. Prototypes include `klp_free_patch_async()`, `klp_free_replaced_patches_async()`, `klp_unpatch_replaced_patches()`, and `klp_discard_nops()`.

The inline `klp_is_object_loaded()` treats vmlinux objects as always loaded and module objects as loaded when `obj->mod` is set. Callback wrappers are `klp_pre_patch_callback()`, `klp_post_patch_callback()`, `klp_pre_unpatch_callback()`, and `klp_post_unpatch_callback()`.

## Control Flow
Consumers include core lifecycle code, ftrace patching, state compatibility, and transition code. The callback wrappers normalize optional object callbacks and maintain `obj->callbacks.post_unpatch_enabled`, ensuring `post_unpatch` only runs after a successful `pre_patch` path.

## State and Persistence Behavior
The header does not store state itself. It defines access to process-wide livepatch state and enforces the callback flag convention used across enable, disable, module load, and rollback paths.

## Dependencies and Integration Points
It includes `<linux/livepatch.h>` and depends on `struct klp_patch`, `struct klp_object`, callback layouts, and kernel list/mutex facilities supplied through livepatch headers. It is consumed by `core.c`, `patch.c`, `state.c`, and `transition.c`.

## Risks and Test Signals
The callback wrappers are deceptively small but define rollback semantics. Regressions can double-run `post_unpatch`, skip it after a successful pre-patch, or treat unloaded module objects as patchable. Test signals include callback order tests around successful enable/disable, pre-patch failure, module unload, and atomic replace cleanup.
