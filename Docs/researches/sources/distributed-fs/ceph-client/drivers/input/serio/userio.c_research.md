# sources/distributed-fs/ceph-client/drivers/input/serio/userio.c

## Purpose
`userio.c` creates `/dev/userio`, a misc character device that lets userspace instantiate a virtual serio port, configure its port type, inject incoming bytes with `serio_interrupt()`, and receive bytes written by the kernel-side serio driver.

## Important APIs, types, and functions
`struct userio_device` stores one open file's `struct serio`, mutex, running flag, 16-byte circular output buffer, spinlock, and waitqueue. File operations are `userio_char_open()`, `release()`, `read()`, `write()`, and `poll()`. `userio_execute_cmd()` handles `USERIO_CMD_REGISTER`, `USERIO_CMD_SET_PORT_TYPE`, and `USERIO_CMD_SEND_INTERRUPT`. `userio_device_write()` is the serio `.write` callback that queues kernel-to-userspace bytes.

## Control flow
Each open allocates an independent device and serio object. Userspace first writes a `USERIO_CMD_SET_PORT_TYPE`, then `USERIO_CMD_REGISTER` to asynchronously register the serio port, and can later inject bytes using `USERIO_CMD_SEND_INTERRUPT`. When a serio protocol driver writes back, `userio_device_write()` appends the byte to the circular buffer and wakes readers. Release unregisters the serio port if it was registered; otherwise it frees the unused serio directly.

## State and persistence
State is per file descriptor. `running` freezes the port type after registration and controls release cleanup. The circular buffer stores pending bytes for userspace reads; overflow logs a warning but still advances `head`, making old data indistinguishable from overwritten data. No state persists after closing the device.

## Dependencies and integration points
The module uses miscdevice minor `USERIO_MINOR`, UAPI command definitions from `uapi/linux/userio.h`, usercopy, poll/waitqueues, and the serio core. It is useful for userspace-emulated input devices and protocol testing.

## Risks
The 16-byte buffer is tiny and overflow only warns; a slow userspace client can lose driver writes. Reads wait only for buffer non-empty and do not check a dead/disconnected state beyond file lifetime. Command ABI requires exact `sizeof(struct userio_cmd)`, so UAPI layout compatibility matters. Register is asynchronous via serio core, so immediate post-register commands may race actual driver binding.

## Test signals
Test command size validation, missing port type rejection, type changes before and after registration, duplicate register returning `-EBUSY`, interrupt injection before registration returning `-ENODEV`, blocking/nonblocking reads, poll readiness, buffer overflow warning, and release cleanup in both registered and unregistered states.
