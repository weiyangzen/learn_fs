# sources/cloud-native/containers-storage/pkg/loopback/ioctl.go

Purpose: wraps Linux loop-device ioctls behind small typed Go functions.

Important APIs, types, and functions: `ioctlLoopCtlGetFree`, `ioctlLoopSetFd`, `ioctlLoopSetStatus64`, `ioctlLoopClrFd`, `ioctlLoopGetStatus64`, and `ioctlLoopSetCapacity`.

Control flow: each function invokes `syscall.Syscall` with `SYS_IOCTL`, the fd, an ioctl request constant, and an optional argument. Non-zero errno is returned as an error; successful get-status returns a populated `loopInfo64`.

State and persistence: changes or queries kernel loop device state. `SET_FD`, `SET_STATUS64`, `CLR_FD`, and `SET_CAPACITY` mutate kernel state; `GET_STATUS64` and `CTL_GET_FREE` query it.

Dependencies and integration points: depends on `syscall` and `unsafe`; uses constants and struct layout from `loop_wrapper.go`. Called by attach, find, and capacity helpers.

Risks and edge cases: unsafe pointer layout must match the kernel ABI. `syscall.Syscall` is Linux-specific and build-tagged. Callers must pass valid fds and handle permission failures.

Test signals: indirectly covered by loopback attachment and capacity/find behavior; no direct unit tests mock ioctl results.
