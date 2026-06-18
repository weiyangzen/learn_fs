# sources/distributed-fs/ceph-client/drivers/vhost/test.c

## Purpose

`test.c` implements `/dev/vhost-test`, a minimal vhost backend used as a virtio simulator and core exerciser. It does not emulate a real device protocol; it accepts one virtqueue, drains guest output descriptors, immediately publishes them used with length zero, and exposes small ioctls to start/stop the test backend. The file is useful because it demonstrates the smallest backend built on top of `vhost.c`.

## Important APIs, Types, and Functions

`struct vhost_test` contains a shared `struct vhost_dev` and a single `struct vhost_virtqueue`. The supported features are `VHOST_FEATURES` through `VHOST_TEST_FEATURES`. The data path is `handle_vq()`, scheduled through `handle_vq_kick()`. Lifecycle and control are `vhost_test_open()`, `vhost_test_release()`, `vhost_test_run()`, `vhost_test_set_backend()`, `vhost_test_set_features()`, `vhost_test_reset_owner()`, and `vhost_test_ioctl()`. File operations are exposed through `vhost_test_fops` and a dynamically allocated miscdevice named `vhost-test`.

## Control Flow

Open allocates `struct vhost_test`, allocates the vq pointer array, installs the kick handler, initializes the shared vhost device with one queue, and stores it in the file. Userspace configures the common vhost owner, memory, and vring state. `VHOST_TEST_RUN` validates ownership and ring access, then sets each vq backend pointer to the device itself when enabled or to `NULL` when disabled, initializes vq access, and flushes if a backend was already present. `VHOST_TEST_SET_BACKEND` is a second enable/disable path that stores a static backend token, stops or starts polling on the queue kick file, and initializes access when re-enabled.

When a kick arrives, `handle_vq()` locks the vq, verifies the backend pointer, disables notifications, and loops over `vhost_get_vq_desc()`. It stops on parser errors, no available descriptor, unexpected input descriptors, zero-length output, or weight exhaustion. Each valid output-only descriptor chain is completed with `vhost_add_used_and_signal()` and a used length of zero. If the available ring becomes empty, notifications are re-enabled, with the standard race check that disables again and continues if the guest added a descriptor concurrently.

## State and Persistence Behavior

All state is per-open and in memory. The queue backend pointer acts as the running flag. Feature state is stored in `vq->acked_features`. The static local `backend` in `vhost_test_set_backend()` is only an opaque token used to restore a non-NULL backend pointer after disable. Release clears the backend, flushes workers, stops and cleans up the shared vhost device, and frees allocations. No data is persisted beyond the open file.

## Dependencies and Integration Points

The file depends on `test.h` for private ioctl numbers and on `vhost.c` for owner, memory, vring, worker, descriptor, notification, and reset behavior. It uses standard kernel miscdevice, compat ioctl, eventfd, and file APIs. It is a local simulator backend for testing vhost behavior rather than a production device implementation.

## Risks and Edge Cases

Because this backend discards payload contents and returns zero length, it only validates descriptor mechanics and notification behavior. It rejects any descriptor chain with input descriptors and any zero-length output chain. `VHOST_TEST_SET_BACKEND` uses a static backend token rather than a per-device object; that is acceptable for an opaque test pointer but would be unsafe as a real shared backend. As with other vhost devices, all operations after owner setup must come from the owner mm. Poll start/stop must be paired with vhost flushes to avoid using stale kick file references.

## Test Signals

Useful signals include opening `/dev/vhost-test`, configuring one vring, running `VHOST_TEST_RUN`, submitting output-only descriptors, verifying used-ring advancement and eventfd signaling, testing notification enable races, resetting owner, and running lockdep/KASAN around repeated open/release and backend toggles. Since this is itself a test backend, broader validation comes from userspace tests that drive the vhost UAPI against it.
