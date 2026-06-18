# sources/distributed-fs/ceph-client/drivers/vhost/test.h

## Purpose

`test.h` is the private UAPI-style header for the vhost test backend. It defines the ioctl commands used by userspace to start/stop the virtio null-device simulation and to enable or disable the test backend for a vq.

## Important APIs, Types, and Functions

The header defines `VHOST_TEST_RUN` as `_IOW(VHOST_VIRTIO, 0x31, int)` and `VHOST_TEST_SET_BACKEND` as `_IOW(VHOST_VIRTIO, 0x32, int)`. The first passes an integer run flag to `vhost_test_run()`. The second passes a `struct vhost_vring_file` payload in practice, because `test.c` copies that structure before calling `vhost_test_set_backend()`, even though the macro's nominal type argument is `int`.

## Control Flow

The header has no executable control flow. It is included by `test.c`, and ioctl dispatch in `vhost_test_ioctl()` switches on these two command values before falling through to common vhost device and vring ioctls.

## State and Persistence Behavior

The header defines command numbers only. It stores no state and has no persistence behavior. The state changes caused by the commands are implemented in `test.c`: `VHOST_TEST_RUN` toggles the queue backend pointer for all queues, while `VHOST_TEST_SET_BACKEND` stops or starts polling for a selected queue.

## Dependencies and Integration Points

The macros depend on the common vhost ioctl namespace `VHOST_VIRTIO`, supplied by Linux vhost headers included before or alongside this file. The command values are consumed by userspace tests and the kernel-side `vhost-test` miscdevice.

## Risks and Edge Cases

The `_IOW` type annotation for `VHOST_TEST_SET_BACKEND` does not describe the actual structure copied by `test.c`; ioctl number construction on Linux generally depends on encoded size, so this mismatch can matter for tooling, tracing, or strict userspace wrappers. Any userspace caller should follow the implementation and pass `struct vhost_vring_file`, not a plain integer. The header is intentionally tiny, so most behavioral risks live in `test.c` and the shared vhost core.

## Test Signals

The basic signal is that userspace can compile against the header and successfully issue `VHOST_TEST_RUN` and `VHOST_TEST_SET_BACKEND` to `/dev/vhost-test`. Compat-ioctl and ioctl-size checks are especially useful because of the `VHOST_TEST_SET_BACKEND` type annotation mismatch.
