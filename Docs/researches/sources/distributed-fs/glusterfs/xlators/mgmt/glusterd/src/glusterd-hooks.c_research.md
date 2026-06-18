# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-hooks.c

## Purpose
`glusterd-hooks.c` implements GlusterD's commit hook framework. It creates the hook directory hierarchy, maps volume-management operations to hook subdirectories, executes enabled hook scripts with operation-specific command-line arguments, and runs post-commit hooks asynchronously through a worker thread.

## Important APIs, Types, And Functions
The operation-to-directory table `glusterd_hook_dirnames[GD_OP_MAX]` maps selected operations such as create, delete, start, stop, add-brick, remove-brick, set, reset, and gsync-create to hook directory names. `glusterd_hooks_create_hooks_directory()` builds `<workdir>/hooks/1/<op>/{pre,post}` for every operation with a hook directory. `glusterd_hooks_get_hooks_cmd_subdir()` returns the mapped directory name.

Script argument helpers include `glusterd_hooks_add_working_dir()`, `glusterd_hooks_add_op()`, `glusterd_hooks_add_hooks_version()`, `glusterd_hooks_add_custom_args()`, `glusterd_hooks_set_volume_args()`, and the switch-based `glusterd_hooks_add_op_args()`. `glusterd_hooks_run_hooks()` discovers enabled hook scripts, sorts them, builds runner commands, and executes them. Queue/worker APIs are `glusterd_hooks_post_stub_enqueue()`, `glusterd_hooks_stub_init()`, `glusterd_hooks_stub_cleanup()`, `glusterd_hooks_priv_init()`, and `glusterd_hooks_spawn_worker()`.

## Control Flow
Hook setup runs during GlusterD startup: the base hooks directory and versioned pre/post subdirectories are created for every mapped operation. A hook script is enabled only when its filename starts with `S` and does not match rpm backup suffixes such as `*.rpmsave` or `*.rpmnew`.

For synchronous hook execution, callers pass a hook path, operation, op context dict, and pre/post type to `glusterd_hooks_run_hooks()`. It requires `volname` in the op context, opens the directory, collects enabled entries into a growable array, sorts them with `glusterd_compare_lines()`, then runs each script as `<hooks_path>/<script> --volname=<volname> ...`. Operation-specific arguments add flags such as `--first=yes/no` for start-volume, `--last=yes/no` for stop-volume, `-o key=value` for set-volume, hook version, volume operation name, GlusterD workdir, custom `hooks_args`, and special transport address-family data when shared storage is enabled.

For asynchronous post hooks, `glusterd_hooks_post_stub_enqueue()` copies the script directory and op context into a `glusterd_hooks_stub_t`, pushes it to `hooks_priv->list` under a mutex, increments `waitcount`, and signals the worker condition variable. `hooks_worker()` waits indefinitely, removes one stub at a time, decrements `waitcount`, executes post hooks with `GD_COMMIT_HOOK_POST`, and frees the stub.

## State And Persistence Behavior
Persistent filesystem state is the hook directory tree under GlusterD's workdir. Runtime state is held in `glusterd_hooks_private_t`: a linked-list queue, mutex, condition variable, worker thread, and debug wait count. Each queued stub owns a duplicated script path and a referenced copy of the operation context dict. The file does not store durable hook execution history; success and failures are emitted to Gluster logs through `runner_log()`.

## Dependencies And Integration Points
The hooks layer uses Gluster's `runner_t` execution API, dict APIs, `mkdir_p`, syscall wrappers, GlusterD volume lists, and memory types from `glusterd-mem-types.h`. `glusterd.c` creates directories and spawns the worker. `glusterd-mgmt.c` invokes pre and post commit hooks around volume transactions. `glusterd-store.c` uses the header helper for hook-friendly user namespace keys.

## Risks
Hook scripts are external executables and run with GlusterD-supplied arguments, so argument construction and dict contents matter. `glusterd_hooks_add_custom_args()` appends a single `hooks_args` string via runner formatting; callers must ensure this value is safe and expected. The worker thread has no shutdown path in this file and loops forever. Queue growth is unbounded apart from memory availability. Post-hook failures are logged but do not retry or roll back committed operations. Directory creation or path formatting failures at startup can disable hooks for all operations.

## Test Signals
Test coverage should verify hook directory creation for every mapped op, skipping operations with empty directory names; enabled script filtering and deterministic sort order; argument sets for start/stop first/last volume transitions, set-volume key/value pairs, shared-storage transport family injection, add-brick, reset, and gsync-create; failed script logging without aborting later scripts; asynchronous enqueue/dequeue behavior with dict reference cleanup; and behavior when `volname`, `count`, or script directories are missing.
