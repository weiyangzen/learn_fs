# sources/distributed-fs/ceph-client/include/uapi/linux/string.h

## Purpose
Provides a UAPI-safe wrapper for string definitions. Outside the kernel it includes libc `<string.h>` and intentionally avoids exposing kernel `strings.h`-style helpers to userspace.

## Important APIs, Types, and Constants
No custom APIs are defined. The only exported behavior is conditional inclusion of standard C string declarations for non-kernel builds.

## Control Flow, State, and Persistence
No runtime behavior or state. This header affects include resolution and prevents accidental use of kernel-only string helpers.

## Dependencies and Integration Points
Depends on libc `<string.h>` outside `__KERNEL__`. Used by UAPI headers that need `memcpy`, `memset`, or string declarations in inline helpers, for example TIPC configuration helpers.

## Risks and Test Signals
Risks are include-order surprises and exposing nonportable kernel helpers to userspace. Test by compiling userspace consumers that include `<linux/string.h>` before and after libc headers and by building kernel-side consumers with `__KERNEL__`.
