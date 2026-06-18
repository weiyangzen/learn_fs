# sources/distributed-fs/ceph-client/kernel/livepatch/core.c

## Purpose
`core.c` is the central Kernel Live Patching coordinator. It owns the global livepatch mutex, active patch list, `/sys/kernel/livepatch` kobject tree, patch enable/disable paths, symbol and relocation resolution, dynamic NOP generation for atomic replace, object lifecycle handling, and module load/unload integration. It wires patch metadata from `struct klp_patch` into ftrace redirection via `patch.c` and task consistency transitions via `transition.c`.

## Important APIs, Types, and Functions
Global state is `klp_mutex`, `klp_patches`, and the root kobject `klp_root_kobj`. `klp_enable_patch()` is the exported entry point used by livepatch module init code. Module hooks are `klp_module_coming()` and `klp_module_going()`. Relocation APIs include `klp_apply_section_relocs()`, `clear_relocate_add()`, `klp_find_section_by_name()`, `klp_write_object_relocs()`, and `klp_apply_object_relocs()`.

Symbol resolution centers on `klp_find_object_symbol()`, `klp_resolve_symbols()`, and `klp_write_section_relocs()`, which parse `.klp.sym.<object>.<symbol>,<sympos>` and `.klp.rela.<object>.*` sections and support unexported symbol references. Lifecycle helpers include `klp_init_patch_early()`, `klp_init_patch()`, `klp_init_object()`, `klp_init_object_loaded()`, `klp_free_patch_start()`, `klp_free_patch_finish()`, `klp_free_patch_async()`, `klp_free_replaced_patches_async()`, `klp_unpatch_replaced_patches()`, and `klp_discard_nops()`.

The sysfs interface exposes per-patch `enabled`, `transition`, `force`, `replace`, and `stack_order`; per-object `patched`; and per-function kobjects named `<old_name>,<sympos>`. Attribute handlers include `enabled_store()`, `enabled_show()`, `transition_show()`, `force_store()`, `replace_show()`, `stack_order_show()`, and `patched_show()`.

## Control Flow
Patch enable starts in `klp_enable_patch()`: validate the patch/module/object/function metadata, require the module to be marked as a livepatch module, verify livepatch subsystem initialization, check state compatibility, take a module reference, initialize early list/kobject state, create sysfs nodes, resolve currently loaded objects, and call `__klp_enable_patch()`. `__klp_enable_patch()` initializes a transition to `KLP_TRANSITION_PATCHED`, runs pre-patch callbacks for loaded objects, registers function redirections via `klp_patch_object()`, starts the transition, marks the patch enabled, and attempts immediate completion.

Disable flows through the `enabled` sysfs attribute to `__klp_disable_patch()`. It rejects concurrent transitions, initializes an unpatch transition, runs pre-unpatch callbacks, starts task migration to the unpatched state, clears `patch->enabled`, and asks transition code to complete. If the sysfs write targets the currently transitioning patch, `enabled_store()` reverses the transition instead.

Module arrival is handled by `klp_module_coming()`: mark the module `klp_alive`, find matching patch objects, apply module-specific livepatch relocations, resolve function addresses and sizes, run pre-patch callbacks, and patch the object before module init completes. Module departure via `klp_module_going()` clears `klp_alive` and calls `klp_cleanup_module_patches_limited()` to unpatch objects, run callbacks, clear relocations, and null loaded-object pointers.

## State and Persistence Behavior
Livepatch state is in memory and exposed through sysfs. `klp_patches` contains enabled or transitioning patches; replaced and disabled patch modules may still be loaded but are not active in the list after cleanup. Patch/object/function structures track `enabled`, `forced`, `replace`, `patched`, `transition`, `dynamic`, `nop`, `old_func`, `new_func`, and symbol sizes. Module object state is intentionally not refcounted through `obj->mod`; removal is coordinated by `klp_module_going()` and the module `klp_alive` flag.

Atomic replace persistence is handled by dynamically adding NOP functions and objects to the new patch for old functions no longer present. After a successful replace transition, replaced patches and dynamic NOPs are unpatched and asynchronously freed. Forced transitions mark patch modules as `forced` so module references are not dropped too early.

## Dependencies and Integration Points
This file depends on module/kallsyms/ELF/moduleloader APIs, ftrace patching through `patch.c`, state compatibility in `state.c`, transition consistency in `transition.c`, sysfs/kobject infrastructure, RCU, and architecture relocation helpers. It integrates with module loader livepatch relocation sections, the module coming/going notifier path, reboot/module lifetime through module references, and `/sys/kernel/livepatch` administration.

## Risks and Test Signals
Relocation parsing is strict and ABI-sensitive; incorrect symbol names, duplicate symbols without `old_sympos`, or module-specific access to vmlinux livepatch symbols produce load failures. Memory barriers between transition flag writes, ftrace stack publication, and task state updates are correctness-critical. Module unload races rely on `klp_alive` and no extra module reference for target modules. Tests should cover livepatch module load/unload, ambiguous symbol failures, vmlinux and module-specific `.klp.rela.*` sections, atomic replace with removed functions, sysfs disable/reverse/force paths, late module patching, callback rollback, and reliable cleanup after failed enable.
