<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch.h -->
# sources/distributed-fs/ceph-client/include/linux/livepatch.h

## Purpose
This header defines the core kernel livepatch API and data model. It describes patch modules, target objects, replacement functions, system state records, transition states, shadow variables, and module loader hooks.

## Important APIs, Types, and Functions
Key structures are `struct klp_func`, `struct klp_object`, `struct klp_state`, and `struct klp_patch`. Iteration helpers walk static arrays and dynamic lists. APIs include `klp_enable_patch`, `klp_module_coming`, `klp_module_going`, `klp_find_section_by_name`, `klp_copy_process`, `klp_update_patch_state`, `klp_patch_pending`, `klp_have_reliable_stack`, `klp_shadow_get`, `klp_shadow_alloc`, `klp_shadow_get_or_alloc`, `klp_shadow_free`, `klp_get_state`, and `klp_apply_section_relocs`. Disabled livepatch builds provide no-op or false fallbacks.

## Control Flow
A patch module describes objects and functions. Enabling resolves old symbols, applies relocations, stacks ftrace redirections, and moves tasks through patched/unpatched transition states. Module coming/going hooks attach or detach object-specific patches as target modules load or unload.

## State and Persistence Behavior
State is runtime only: global patch lists, object/function patched flags, task `TIF_PATCH_PENDING`, kobjects, completion for cleanup, and shadow variable tables. Patch state does not persist across reboot.

## Dependencies and Integration Points
It depends on modules, ftrace, completions, lists, external livepatch metadata, scheduler transition hooks, reliable stacktrace support, and ELF relocation data.

## Risks and Test Signals
Risks include ambiguous old symbols, unreliable stack transitions, broken relocation sections, module lifetime races, incorrect replace semantics, and leaked shadow data. Test signals include livepatch selftests, sysfs patch state, task transition completion, ftrace redirection checks, module load/unload tests, and shadow allocation/free coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch.h -->
