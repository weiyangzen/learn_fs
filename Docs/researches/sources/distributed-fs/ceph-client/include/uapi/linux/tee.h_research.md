# sources/distributed-fs/ceph-client/include/uapi/linux/tee.h

## Purpose
Defines the Trusted Execution Environment driver userspace ABI for version discovery, shared-memory allocation/registration, session management, invocation, cancellation, supplicant messages, and object invocation.

## Important APIs, Types, and Constants
Capabilities include generic GP, privileged, registered memory, null memref, and object-reference support. Implementation IDs include OP-TEE, AMDTEE, TSTEE, and QTEE. Key structs include `tee_ioctl_version_data`, `tee_ioctl_shm_alloc_data`, `tee_ioctl_buf_data`, `tee_ioctl_param`, `tee_ioctl_open_session_arg`, `tee_ioctl_invoke_arg`, `tee_ioctl_cancel_arg`, `tee_ioctl_close_session_arg`, supplicant recv/send args, `tee_ioctl_shm_register_data`, `tee_ioctl_shm_register_fd_data`, and `tee_ioctl_object_invoke_arg`. Ioctls cover version, shared memory allocate/register/register-fd, open session, invoke, cancel, close session, supplicant recv/send, and object invoke. Parameter attribute constants distinguish value, memref, userspace buffer, object reference, meta, null memref, and login methods.

## Control Flow, State, and Persistence
Userspace opens a TEE device, queries version, allocates/registers shared memory, opens a session, invokes TA commands, optionally cancels by cancel ID, and closes the session. Supplicant ioctls service secure-world requests. Kernel/secure OS maintain sessions, shared memory IDs/fds, object references, and pending requests.

## Dependencies and Integration Points
Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with TEE core, OP-TEE/AMDTEE/TSTEE/QTEE drivers, tee-supplicant, dmabuf, mmap, and GlobalPlatform Client API concepts.

## Risks and Test Signals
Risks include variable-length buffer sizing up to `TEE_MAX_ARG_SIZE`, untrusted user pointers, reserved login ranges, null memref/object handling, fd lifetime, and supplicant deadlocks. Test version/capability probing, shared-memory map/unmap, open/invoke/close, cancel races, supplicant request/response, object invoke, invalid attrs, and 32-bit compat.
