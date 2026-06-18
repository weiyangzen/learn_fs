# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_kprobe.c

## Purpose

`test_klp_kprobe.c` registers a kprobe on `cmdline_proc_show` so livepatch tests can verify conflict behavior with kprobes that do or do not use a post handler.

## Important APIs, Types, and Functions

It defines bool parameter `has_post_handler`, an optional `post_handler()`, `struct kprobe kp` with `.symbol_name = "cmdline_proc_show"`, and init/exit functions calling `register_kprobe()` and `unregister_kprobe()`.

## Control Flow and State

On load, the module conditionally assigns `kp.post_handler` then registers the kprobe. On unload it unregisters the probe. The persistent state is the active kprobe registration.

## Dependencies and Integration Points

It depends on kprobes, the target symbol, and `test-kprobe.sh`.

## Risks and Test Signals

Risks are symbol drift or post-handler semantics changing. Signals are livepatch load failure only when `has_post_handler=true` and success when false.
