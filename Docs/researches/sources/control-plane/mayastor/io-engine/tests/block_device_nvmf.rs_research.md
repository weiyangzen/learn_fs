# sources/control-plane/mayastor/io-engine/tests/block_device_nvmf.rs

Purpose: large integration suite for the generic block-device API when the backing device is a remote NVMe-oF namespace. It covers create/destroy, identify, event delivery, synchronous and callback I/O, vectored I/O, flush, stats, admin commands, reset, unmap/write-zeroes, reset-abort semantics, stale handle cleanup, and hot namespace removal.

Important APIs/types/functions: `launch_instance` starts a compose Mayastor target, configures NVMe bdev timeouts/retries, creates/shares `malloc:///disk0`, and returns an NVMf URL. Tests use `device_create`, `device_destroy`, `device_lookup`, `device_open`, `BlockDeviceHandle` methods (`read_at`, `write_at`, `readv_blocks`, `writev_blocks`, `flush_io`, `reset`, `nvme_identify_ctrlr`, `nvme_admin_custom`, `unmap_blocks`, `write_zeroes`), `DeviceEventSink`, `DeviceEventListener`, `IoCompletionStatus`, `DmaBuf`, and `AsIoVecs`. Helpers manage guard/data patterns, callback flags, and ad hoc I/O stats.

Control flow: each test launches a remote target, creates a local NVMe bdev from the NVMf URL, opens descriptors/handles inside `MayastorTest::spawn`, performs one operation pattern, sleeps or waits for callbacks where callback APIs are used, validates data/events/stats, then destroys the device. The vectored tests allocate multiple `DmaBuf`s and verify boundary guards. Reset-abort queues reads/writes and then resets the controller, expecting all queued I/O callbacks to complete with non-success. Hot-remove issues an SPDK JSON-RPC namespace removal on the remote target and expects local device removal notification.

State and persistence: remote target state is per compose container. Local NVMf controller state is created/destroyed per test. Static `OnceCell`s store expected device names for callbacks; global atomic callback flags and counters are reset in relevant tests. No durable disk state beyond temporary malloc device.

Dependencies and integration points: depends on compose orchestration, v0 gRPC bdev share API, SPDK NVMe-oF initiator stack, Mayastor block-device abstraction, async reactor execution, and JSON-RPC passthrough for namespace removal. It also validates `Config::nvme_bdev_opts` application.

Risks and edge cases: callback tests use sleeps rather than explicit completions, making timing sensitive. Some static `OnceCell` device-name storage is per test function but still static; repeated invocations in one process can be brittle. Raw pointers/`AtomicPtr` keep handles alive across async callbacks and require careful drop ordering. Tests depend on network/container startup and NVMf event timing.

Test signals: very strong coverage for NVMf initiator behavior and block-device API contracts, including data integrity, stats accounting, callbacks exactly once, device removal events, failure after cleanup, and no device creation after a namespace is gone.
