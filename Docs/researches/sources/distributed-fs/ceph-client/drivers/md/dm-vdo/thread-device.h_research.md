# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-device.h

## Purpose
`thread-device.h` declares the VDO device-id thread registry wrappers.

## Important APIs, Types, And Functions
The header exposes `vdo_register_thread_device_id()`, `vdo_unregister_thread_device_id()`, `vdo_get_thread_device_id()`, and `vdo_initialize_thread_device_registry()`. It reuses `struct registered_thread` from `thread-registry.h`.

## Control Flow
No runtime flow is defined here; call sites register a `registered_thread` storage object for the current thread, query the id while registered, then unregister before thread exit or context teardown.

## State And Persistence
The header declares access to volatile runtime registration state only. It does not own storage.

## Dependencies And Integration Points
It includes `thread-registry.h`, tying this device-id layer to the generic task-pointer registry.

## Risks
The API requires caller-owned `registered_thread` and id storage. Mismanaged lifetime or missing unregister can leave invalid registry entries.

## Test Signals
Compile-time tests should ensure callers include this header without needing generic internals beyond `struct registered_thread`; runtime tests should check the lifecycle documented by the API.
