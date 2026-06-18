# File Research: sources/block-storage/kvdo/vdo/thread-device.c

This file provides a device-id-specific thread registry used for logging context. It owns a static `thread_registry` and wraps generic registry functions.

`uds_register_thread_device_id()` associates the current thread with an unsigned device id pointer. `uds_unregister_thread_device_id()` removes the current thread. `uds_get_thread_device_id()` returns the registered id or `-1` if none exists. `uds_initialize_thread_device_registry()` initializes the static registry.
