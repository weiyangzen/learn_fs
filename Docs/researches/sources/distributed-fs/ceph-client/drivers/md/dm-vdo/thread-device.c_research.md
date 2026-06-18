# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-device.c

## Purpose
`thread-device.c` provides a process-thread-local registry mapping the current kernel thread to a VDO device id pointer.

## Important APIs, Types, And Functions
It owns a static `struct thread_registry device_id_thread_registry`. `vdo_register_thread_device_id()` registers the current thread with a supplied `unsigned int *`. `vdo_unregister_thread_device_id()` removes the current thread. `vdo_get_thread_device_id()` returns the registered id or `-1`. `vdo_initialize_thread_device_registry()` initializes the registry.

## Control Flow
Each public wrapper delegates to the generic thread registry in `thread-registry.c`. Lookup returns a typed integer by dereferencing the stored pointer when present.

## State And Persistence
State is in the static registry only and is not persistent. The registered id pointer must outlive the thread registration.

## Dependencies And Integration Points
The file integrates generic `thread-registry` with VDO device identity, likely for logging, allocation tracking, or per-device context lookup from code that only knows `current`.

## Risks
Forgetting to unregister leaves stale task-to-pointer mappings. Registering a pointer with too short a lifetime can cause lookup use-after-free. Lookup returns `-1`, so callers must handle "not registered".

## Test Signals
Tests should cover initialization, register/lookup/unregister on the same thread, duplicate registration behavior inherited from `thread-registry`, and unregistered lookup.
