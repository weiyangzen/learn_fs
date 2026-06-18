# sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/zcrypt.h

## Purpose
Defines the s390 zcrypt userspace ABI for AP crypto adapters. It covers legacy ICA RSA requests, CCA CPRB passthrough, EP11 request blocks, device status matrices, autoselect constants, supported ioctl numbers, and deprecated compatibility commands.

## Important APIs, Types, And Functions
Important request structs are `ica_rsa_modexpo`, `ica_rsa_modexpo_crt`, `CPRBX`, `ica_xcRB`, `ep11_cprb`, `ep11_target_dev`, and `ep11_urb`. Device inventory uses `zcrypt_device_status_ext` and `zcrypt_device_matrix_ext`; deprecated variants remain for old callers. Ioctls include `ICARSAMODEXPO`, `ICARSACRT`, `ZSECSENDCPRB`, `ZSENDEP11CPRB`, `ZCRYPT_DEVICE_STATUS`, `ZCRYPT_STATUS_MASK`, `ZCRYPT_QDEPTH_MASK`, and `ZCRYPT_PERDEV_REQCNT`.

## Control Flow
The header defines the payloads passed to the zcrypt misc device. Userspace fills request structs with user pointers and lengths; the kernel zcrypt layer validates, copies, routes to AP queues/domains or autoselects targets, waits for adapter completion, then copies reply data and status back.

## State And Persistence
No code state is held here, but the ABI persists. Some request fields represent big-endian hardware control blocks, 16-byte padded pointer slots, or per-device counters exposed since adapter discovery.

## Dependencies And Integration Points
Depends on ioctl, compiler, and integer UAPI headers. Integrates libica, EP11/CCA userspace, AP bus drivers, zcrypt device nodes, sysfs status, and compatibility paths for old z90stat-style applications.

## Risks And Edge Cases
The highest risks are ABI layout and bitfield packing, user pointer validation, 32/64-bit compat behavior, AP/domain autoselect semantics, and preserving deprecated ioctl numbers. CPRB comments note big-endian shorts/ints and pointer padding, which are common sources of bad requests.

## Test Signals
Signals include UAPI `sizeof`/`offsetof` tests, libica/zcrypt ioctl selftests, AP queue emulation, CCA and EP11 passthrough tests, deprecated ioctl compatibility checks, large status matrix reads, and error-path tests for invalid user buffers and unsupported adapters.
