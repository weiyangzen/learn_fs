# sources/distributed-fs/ceph-client/include/uapi/linux/blk-crypto.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/blk-crypto.h` exports block-layer crypto key management ioctls. The complete 44-line header was read. It defines userspace argument structures for importing raw keys, generating wrapped keys, preparing ephemeral wrapped keys, and the ioctl numbers allocated in the block device ioctl space.

## Important APIs, Types, and Functions

There are no functions. Exported types are `struct blk_crypto_import_key_arg`, `struct blk_crypto_generate_key_arg`, and `struct blk_crypto_prepare_key_arg`. Exported ioctls are `BLKCRYPTOIMPORTKEY`, `BLKCRYPTOGENERATEKEY`, and `BLKCRYPTOPREPAREKEY`, all using command type `0x12` and numbers 137 through 139. The header notes that numbers 140 and 141 are reserved for future blk-crypto use.

## Control Flow

The header has no executable flow. Userspace opens a block device and issues an ioctl with one of the argument structures. Import flow passes a raw key pointer/size and receives a long-term wrapped key blob. Generate flow requests a newly generated long-term wrapped key. Prepare flow passes a long-term wrapped key and receives an ephemerally wrapped key suitable for immediate use by hardware or the block layer.

## State and Persistence Behavior

The header owns no key storage. It describes transient ioctl arguments and caller-provided buffers. The long-term wrapped key blob may be persisted by userspace or higher-level storage software, while ephemeral keys are intended for shorter-lived operational use. The reserved fields provide ABI extension space and should be zeroed by callers.

## Dependencies and Integration Points

Direct dependencies are `<linux/ioctl.h>` and `<linux/types.h>`. Integration points are the block device ioctl namespace, blk-crypto kernel support, hardware inline encryption engines, filesystem/storage encryption stacks, and userspace key-management utilities that pass pointers as `__u64` for ABI-stable 32/64-bit handling.

## Risks and Edge Cases

Pointer fields are numeric `__u64` values, so compat handling and address validation must be correct in the kernel. Callers must supply valid buffer sizes and expect the kernel to reject unsupported sizes or algorithms. Reserved fields must remain zero for forward compatibility. The shared block ioctl number space is scarce; accidental command collisions would break unrelated block-device ioctls. Raw keys and wrapped blobs are sensitive data and require memory lifetime/scrubbing discipline outside this header.

## Test Signals

Useful tests include ioctl ABI size checks on 32- and 64-bit builds, invalid pointer and short-buffer tests, reserved-field rejection or ignore behavior as implemented by the kernel, successful import/generate/prepare sequences on supported devices, unsupported-device error-path tests, and key-material leak scans in tracing/logging paths.
