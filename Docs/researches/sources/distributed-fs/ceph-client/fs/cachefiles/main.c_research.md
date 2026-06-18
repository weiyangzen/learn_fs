# sources/distributed-fs/ceph-client/fs/cachefiles/main.c

## Purpose
`main.c` is the CacheFiles module entry point. It registers the misc device used by cachefilesd, creates the object slab cache, registers optional error injection, defines tracepoints, and provides module metadata.

## Important APIs, Types, and Functions
Important state and functions are `cachefiles_debug`, module parameter `debug`, global `cachefiles_object_jar`, miscdevice `cachefiles_dev`, `cachefiles_init`, and `cachefiles_exit`.

## Control Flow
`cachefiles_init` registers error injection first, registers `/dev/cachefiles` as a misc device backed by `cachefiles_daemon_fops`, creates the `cachefiles_object_jar` slab, and reports loaded state. Failures unwind in reverse order. `cachefiles_exit` destroys the slab, deregisters the misc device, and unregisters error injection.

## State and Persistence Behavior
Runtime state includes the debug mask, miscdevice registration, and object slab cache. It does not persist cache data itself; backing cache state is created later by daemon bind and VFS helpers.

## Dependencies and Integration Points
This file integrates Kbuild/Kconfig output with the daemon interface, `error_inject.c`, tracepoint creation, module parameters, fs initcall ordering, and object allocation in `interface.c`.

## Risks and Edge Cases
Init ordering matters: object allocation cannot occur before the slab exists, and userspace cannot open the device before fops are registered. Error paths must deregister only what succeeded. Exit assumes no live daemon/object users remain.

## Test Signals
Load/unload as a module, built-in boot init, misc device creation, debug parameter read/write, forced init failures through fault injection, and leak checks after open/bind/unbind/unload cycles.
