# sources/distributed-fs/ceph-client/kernel/livepatch/patch.c

## Purpose
`patch.c` implements the ftrace-backed function redirection layer for livepatch. It maps each original function address to one `struct klp_ops` ftrace registration, maintains an RCU-protected stack of replacement `struct klp_func` entries for that original function, and updates function instruction pointers at ftrace time according to the current task's livepatch transition state.

## Important APIs, Types, and Functions
The global `klp_ops` list tracks registered ftrace operations. `klp_find_ops()` locates the ftrace registration for an old function. `klp_patch_object()` patches every function in a loaded object; `klp_unpatch_object()`, `klp_unpatch_objects()`, and `klp_unpatch_objects_dynamic()` remove all or only dynamic NOP entries.

The hot path is `klp_ftrace_handler()`. Internal helpers are `klp_patch_func()`, `klp_unpatch_func()`, and `__klp_unpatch_object()`. `struct klp_ops` itself is declared in `patch.h` and contains a global list node, `func_stack`, and `struct ftrace_ops`.

## Control Flow
When the first livepatch function targets an original function, `klp_patch_func()` allocates `struct klp_ops`, initializes `fops` with the livepatch ftrace handler and IP modification flags, adds the new `klp_func` to `func_stack`, installs an ftrace filter at the original function location, and registers the ftrace function. Later patches for the same original function only push another `klp_func` onto the existing stack.

At runtime, `klp_ftrace_handler()` enters under ftrace recursion protection, reads the top `klp_func` with RCU, observes memory barriers required by transition setup, and decides whether to use the top replacement or a previous stack entry. During patching, tasks that have switched to the patched state use the top replacement. During unpatching, tasks still in the patched state may continue to see the patched entry, while unpatched tasks skip to the previous entry or original function. NOP entries deliberately avoid changing the instruction pointer.

Unpatching removes a function from the stack with `list_del_rcu()`. If the stack becomes singular, it unregisters ftrace, removes the filter, deletes the `klp_ops` node, and frees it; otherwise it only removes the function stack entry.

## State and Persistence Behavior
State is transient kernel memory: one ftrace registration per original function and an RCU-visible stack of active replacement functions. `func->patched` records whether a specific `klp_func` is active. RCU synchronization is delegated to ftrace unregister and transition synchronization so removed stack entries are not observed after freeing.

## Dependencies and Integration Points
This file depends on ftrace IP modification support, RCU list primitives, livepatch task transition state from `transition.c`, and object/function metadata initialized by `core.c`. It is called by core enable/disable and module load/unload paths.

## Risks and Test Signals
The main risks are ftrace registration failure cleanup, stack ordering mistakes during cumulative and atomic replace patches, selecting the wrong function during transition, and missing RCU/ftrace synchronization before freeing entries. Tests should include stacking multiple patches on one function, unpatching the top and final entries, NOP replace entries, concurrent task transitions, forced transitions, and ftrace filter/register failure injection.
