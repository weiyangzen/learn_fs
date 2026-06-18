
# sources/distributed-fs/ceph-client/lib/test_kmod.c

## Purpose

This misc-device driver stress-tests the kernel module loader through concurrent `request_module()` calls and concurrent filesystem type lookups via `get_fs_type()`.

## Important APIs, Types, And Functions

Core types are `struct test_config`, `struct kmod_test_device_info`, and `struct kmod_test_device`. Config stores target driver, target filesystem, thread count, selected test case, and result. Per-thread info stores return values, filesystem pointers, task pointers, and module-put obligations. Device state includes miscdevice, sysfs attributes, config/trigger/thread locks, completion, and a per-thread info array.

The sysfs interface includes `trigger_config`, `config`, `reset`, `config_test_driver`, `config_test_fs`, `config_num_threads`, `config_test_case`, and `test_result`. `run_request()` dispatches either `request_module()` or `get_fs_type()` in a kthread. `try_requests()` creates all kthreads, waits for completion, and tallies results.

## Control Flow And State

`late_initcall(test_kmod_init)` registers the first `test_kmodN` misc device and optionally runs startup tests if `force_init_test` is set. A trigger locks config/trigger mutexes, starts up to `num_threads` kthreads, waits for `kthreads_done`, then records the first observed error in `test_result`. Reset rebuilds the default config and resizes the info array. Exit stops live threads, unregisters misc devices, frees config strings and arrays, and removes all registered test devices.

## Dependencies And Integration Points

It depends on kmod, module, kthread, filesystem type lookup, miscdevice/sysfs, vmalloc, and the optional `get_kmod_umh_limit()` helper. Userspace selftests drive the sysfs attributes, usually through `tools/testing/selftests/kmod/kmod.sh`.

## Risks And Test Signals

The driver deliberately stresses usermode-helper/module-loader limits and can create many concurrent threads. Risks include OOM during thread setup, stale module references if `module_put()` is missed, and interpreting positive `request_module()` statuses. Signals are `test_result`, per-thread log lines, completion of all threads, and correct cleanup on reset/unload.
