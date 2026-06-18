# sources/distributed-fs/ceph-client/include/linux/auto_fs.h

## Purpose
Kernel include wrapper for autofs filesystem definitions. It pulls in core filesystem/ioctl declarations plus the exported autofs UAPI header so in-kernel autofs users can see both VFS types and the user-visible ABI.

## Important APIs, Types, And Functions
This file defines no new functions or structures. It exposes `linux/fs.h`, `linux/ioctl.h`, and `uapi/linux/auto_fs.h` to consumers. The effective API includes autofs protocol constants and data structures from the UAPI header.

## Control Flow
There is no executable control flow. The only behavior is include ordering and include guarding.

## State And Persistence
No state is owned by this wrapper. Autofs mount state, daemon communication, and pending-expire/request state are handled by autofs implementation files and userspace protocol participants.

## Dependencies And Integration Points
The wrapper depends on VFS definitions from `linux/fs.h`, ioctl macros from `linux/ioctl.h`, and exported autofs ABI definitions from `uapi/linux/auto_fs.h`. It integrates autofs with VFS and ioctl paths.

## Risks
Because this header is only a bridge, risks are mostly accidental include churn or ABI confusion. Adding kernel-only definitions here could blur the UAPI boundary; changing included UAPI content can affect userspace compatibility.

## Test Signals
Compile tests for autofs code and userspace ABI checks are the relevant signals. Functional coverage comes from automount mount, lookup, expire, and ioctl tests.
