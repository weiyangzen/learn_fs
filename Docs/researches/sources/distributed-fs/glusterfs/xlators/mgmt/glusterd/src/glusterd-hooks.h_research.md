# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-hooks.h

## Purpose
`glusterd-hooks.h` declares the public interface and private data structures for GlusterD's hook subsystem. It is the contract between hook execution code, GlusterD startup, operation commit code, and store code that filters hook-friendly keys.

## Important APIs, Types, And Functions
`GLUSTERD_GET_HOOKS_DIR(path, version, priv)` formats the versioned hooks directory as `<workdir>/hooks/<version>`. `GLUSTERD_HOOK_VER` is currently `1`. `GD_HOOKS_SPECIFIC_KEY` is `user.*`, used by `is_key_glusterd_hooks_friendly()` to identify user-namespace keys that hooks may preserve or expose.

`glusterd_commit_hook_type_t` defines hook phases: none, pre, post, and max. `glusterd_hooks_private_t` owns the asynchronous post-hook queue, mutex, condition variable, worker thread, and wait counter. `glusterd_hooks_stub_t` stores one queued hook run: list node, script directory, operation context dict, and operation id.

Declared functions cover directory creation, command-subdirectory lookup, hook execution, worker spawning, stub allocation/cleanup, post-stub enqueue, and private-state initialization.

## Control Flow
Callers use this header in three main paths. Startup calls `glusterd_hooks_create_hooks_directory()` and `glusterd_hooks_spawn_worker()`. Transaction commit code calls `glusterd_hooks_run_hooks()` for immediate pre hooks and enqueues post hooks through `glusterd_hooks_post_stub_enqueue()`. Store code calls `is_key_glusterd_hooks_friendly()` to permit only `user.*` keys under hook-specific behavior.

## State And Persistence Behavior
The header itself stores no state, but it defines the queue structures that become `glusterd_conf_t.hooks_priv` at runtime. The directory macro encodes the persistent on-disk hook layout and ties it directly to `glusterd_conf_t.workdir`.

## Dependencies And Integration Points
It depends on `fnmatch.h`, Gluster's `gf_boolean_t`, `dict_t`, list primitives, pthreads, `xlator_t`, and `glusterd_op_t` from surrounding headers. Its memory type usage is coordinated with `glusterd-mem-types.h`.

## Risks
The directory macro writes into a caller-provided buffer and sets `path[0] = 0` only if `snprintf()` returns a negative value; truncation is not explicitly handled in the macro. `is_key_glusterd_hooks_friendly()` relies on `THIS->name` for debug logging and assumes a non-null key. Any new hook phase requires updating both enum consumers and directory creation logic.

## Test Signals
Tests should exercise the hooks directory macro with normal and long workdirs, `user.*` matching and nonmatching keys, phase enum assumptions in directory creation, stub lifecycle behavior, and compile-time inclusion from both hook implementation and store/management code.
