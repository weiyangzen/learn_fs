# sources/distributed-fs/ceph-client/kernel/module/kmod.c

## Purpose
Implements the in-kernel autoload path that calls userspace `modprobe` for `request_module()` consumers.

## Important APIs, Types, And Functions
Exports `__request_module`. Internal helpers are `call_modprobe` and `free_modprobe_argv`. Global state includes `modprobe_path`, the `kmod_concurrent_max` semaphore, `MAX_KMOD_CONCURRENT`, and `MAX_KMOD_ALL_BUSY_TIMEOUT`.

## Control Flow
`__request_module` rejects synchronous requests from async context with a warning, checks that `modprobe_path` is enabled, formats the module name, applies LSM `security_kernel_module_request`, and acquires a bounded concurrency semaphore. It emits a tracepoint, consults duplicate suppression, and if needed calls `call_modprobe`, which builds argv/envp and runs `call_usermodehelper_exec` with either wait-for-process or wait-for-exec behavior. Completion is announced to duplicate waiters.

## State And Persistence
The modprobe path is a runtime sysctl-backed buffer declared here and initialized from `CONFIG_MODPROBE_PATH`. The concurrency semaphore limits live helpers. No durable module state is modified directly.

## Dependencies And Integration Points
Depends on usermode helper infrastructure, LSM hooks, tracepoints, duplicate suppression in `dups.c`, async subsystem rules, and sysctl exposure from `main.c`.

## Risks And Edge Cases
Recursive module dependencies can exhaust all helper slots; the timeout fails new requests. Synchronous autoload from async workers can deadlock module init and is warned. Overlong names fail with `-ENAMETOOLONG`; disabled modprobe path fails with `-ENOENT`. Callers must verify the requested facility appeared after success.

## Test Signals
Exercise `request_module()` success/failure, disabled modprobe path, LSM denial, duplicate request suppression, nowait versus wait behavior, concurrency saturation, and tracepoint output.
