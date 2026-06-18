# sources/distributed-fs/ceph/src/rgw/driver/posix/notify.cpp

## Purpose
`notify.cpp` implements the factory for the POSIX driver's filesystem notification abstraction. It currently requires Linux inotify and returns an `Inotify` instance for bucket listing cache invalidation/update.

## Important APIs, Types, and Functions
The only function is `file::listing::Notify::factory(Notifiable* n, const std::string& bucket_root)`. On `__linux__`, it constructs `new Inotify(n, bucket_root)` and wraps it in `std::unique_ptr<Notify>`. On non-Linux platforms it emits a preprocessor error stating that the RGW POSIX driver requires inotify.

## Control Flow
`BucketCache` constructs `Notify::factory(this, bucket_root)` during initialization. The resulting `Inotify` object owns the event loop thread and calls back into `BucketCache::notify()` through the `Notifiable` interface declared in `notify.h`.

## State and Persistence Behavior
This file owns no runtime state. It selects the concrete notification implementation. Notification state is held in `Inotify` fields in `notify.h`.

## Dependencies and Integration Points
It includes `notify.h` and Linux `<sys/inotify.h>` when compiled for Linux. Its integration point is `BucketCache`, which depends on the factory to create a watcher before any bucket cache fills can register watches.

## Risks
The driver is intentionally non-portable here. Any build that includes this source on non-Linux platforms fails at preprocessing. The file has a dead `return nullptr` after the preprocessor branch, but it is unreachable for supported builds.

## Test Signals
Linux build coverage should verify the factory returns a non-null `Inotify`. Non-Linux build jobs should either exclude this driver or intentionally assert that the driver is unsupported.
