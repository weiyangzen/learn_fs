# sources/distributed-fs/ceph-client/include/uapi/linux/blkdev.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/blkdev.h` exports a small io_uring block command identifier. The complete 14-line header was read. It defines the block-layer uring command for discard operations, separate from normal ioctl numbering while reusing the block ioctl command type value.

## Important APIs, Types, and Functions

There are no functions or structs. The exported macro is `BLOCK_URING_CMD_DISCARD`, defined with `_IO(0x12, 0)`. The comment ties the command to `IORING_OP_URING_CMD` and states that this command number space is different from `ioctl()`.

## Control Flow

The header has no executable flow. Runtime flow is through io_uring: userspace submits `IORING_OP_URING_CMD` against a block file and identifies the operation with `BLOCK_URING_CMD_DISCARD`; the block layer dispatches the command to discard handling rather than treating it as a traditional ioctl.

## State and Persistence Behavior

No state is owned by this header. Discard commands can affect persistent media allocation state by informing the device/filesystem that sectors are unused, but the header only names the command.

## Dependencies and Integration Points

Direct dependencies are `<linux/ioctl.h>` and `<linux/types.h>`. Integration points are io_uring command submission, block-device file operations, discard/TRIM handling, and userspace libraries that need the stable command value.

## Risks and Edge Cases

The most important distinction is namespace: although `_IO(0x12, 0)` is used, this is for uring commands, not `ioctl()`. Userspace that issues it through the wrong syscall path will not exercise the intended interface. Runtime discard behavior depends on block-device support, alignment, range validation, permissions, and filesystem/device policy outside this header.

## Test Signals

Useful signals include io_uring block discard smoke tests, unsupported-device and permission error tests, namespace tests that confirm the command is not treated as a regular ioctl contract, and end-to-end discard verification with devices that expose deterministic trim behavior.
