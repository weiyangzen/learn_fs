<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_core.c -->
# sources/distributed-fs/ceph-client/drivers/tee/tee_core.c

## Purpose

`tee_core.c` implements the generic Linux TEE character-device core and in-kernel client API. It manages `/dev/tee*` and `/dev/teepriv*` devices, TEE contexts, ioctl decoding/validation, shared-memory parameter resolution, supplicant request forwarding, TEE client bus registration, and exported helper APIs used by TEE drivers and kernel clients.

## Important APIs, Types, and Functions

Device/context lifecycle functions include `teedev_open()`, `teedev_close_context()`, `teedev_ctx_get()/put()`, `tee_device_alloc()`, `tee_device_register()`, `tee_device_unregister()`, `tee_device_get()/put()`, and `tee_get_drvdata()`. User ioctl handlers cover version, SHM alloc/register/register-fd, open session, invoke, object invoke, cancel, close session, supplicant recv, and supplicant send. Parameter conversion is handled by `params_from_user()`, `params_to_user()`, `params_to_supp()`, `params_from_supp()`, and `param_from_user_memref()`.

The file also implements `tee_session_calc_client_uuid()` using UUIDv5 over Linux uid/gid identities, the exported in-kernel client API (`tee_client_open_context()`, `tee_client_open_session()`, `tee_client_invoke_func()`, etc.), and the `tee_bus_type` plus `tee_client_driver` registration helpers.

## Control Flow

At subsystem init, the TEE class, character-device major range, and client bus are registered. A concrete TEE driver allocates a `tee_device` with mandatory operations, registers it, and userspace opens the character device. Each open creates a `tee_context` and calls the driver's `.open()`. Ioctls copy an argument header from userspace, validate total buffer length against `TEE_MAX_ARG_SIZE`, allocate `struct tee_param` arrays, convert user parameters, call the driver's operation, copy result fields and output parameter sizes/IDs back, then release any retained shared-memory references.

For object invocation, `tee_ioctl_object_invoke()` mirrors classic session invoke but dispatches to `.object_invoke_func` and supports OBJREF parameter types. Supplicant ioctls convert between normal TEE parameter representation and the lighter userspace supplicant format, then call driver `.supp_recv`/`.supp_send`.

## State and Persistence Behavior

Global runtime state includes a 32-device bitmap, global class, device number range, and TEE bus. Each `tee_device` tracks ID, name, device/cdev, descriptor, pool, IDR of shared-memory objects, mutex, user count, and unregister completion. Each `tee_context` tracks the driver context, refcount, release state, and supplicant waiting policy. There is no durable storage.

## Dependencies and Integration Points

The core depends on Linux char-device, driver core, IDR, credentials, uaccess, DMA-buf shared-memory support, SHA-1 for UUIDv5, and public `linux/tee_core.h`/ioctl ABI definitions. Concrete integrations in this work item include qcomtee's object-invoke/supplicant callbacks, tstee's classic open-session/invoke functions, and shared-memory support in `tee_shm.c`, `tee_heap.c`, and `tee_shm_pool.c`.

## Risks and Edge Cases

Length validation relies on overflow-aware `size_add()`/`size_mul()` in most paths; object invoke uses a direct equality with `sizeof(arg) + TEE_IOCTL_PARAM_SIZE()` that should be reviewed for overflow parity. `teedev_ctx_get()` silently returns when `ctx->releasing`, which can make misuse hard to detect. `match_dev()` dereferences `teedev->desc` during class iteration without taking `tee_device_get()`, relying on device lifetime and unregister sequencing. Shared-memory memref conversion must unwind references on any later ioctl error. Object and OBJREF parameter types increase the attack surface for drivers that did not historically handle user-controlled object IDs.

## Test Signals

Tests should cover all ioctl buffer length boundaries and overflow cases, bad user pointers, every supported parameter type, MEMREF null capability, shared-memory ID ownership and refcount cleanup, open-session failure after session creation, object-invoke OBJREF output copying, supplicant recv/send conversions, device unregister with open contexts, class/client-bus probing, and KASAN/refcount checks for context release races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_core.c -->
