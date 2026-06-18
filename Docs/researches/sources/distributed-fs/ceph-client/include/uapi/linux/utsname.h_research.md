# sources/distributed-fs/ceph-client/include/uapi/linux/utsname.h

## Purpose
Defines historical and current UTS name structures returned by Linux uname-related syscalls. It preserves fixed-size buffers for system name, node name, release, version, machine, and domain name.

## Important APIs, Types, And Constants
`__OLD_UTS_LEN` is 8 and backs `struct oldold_utsname`, which stores five 9-byte strings. `__NEW_UTS_LEN` is 64 and backs `struct old_utsname` and `struct new_utsname`, both using 65-byte null-terminated fields; `new_utsname` adds `domainname`. These are plain char-array ABI structs.

## Control Flow, State, And Persistence
The header contains no logic. Kernel uname handlers copy current UTS namespace values into these layouts. State is owned by the kernel UTS namespace; host/container namespace changes affect future syscall results, but the structs themselves are transient copy-out buffers.

## Dependencies And Integration Points
Integrated with `uname`, older uname variants, libc wrappers, and namespace code. The fixed lengths are part of the syscall ABI and cannot be changed without breaking applications.

## Risks And Test Signals
Risks include truncation, missing NUL termination, and accidentally mixing old/new layouts. Tests should validate field sizes, namespace-specific values, truncation behavior for long hostnames/domain names, and compatibility syscall paths on architectures that expose older structures.
