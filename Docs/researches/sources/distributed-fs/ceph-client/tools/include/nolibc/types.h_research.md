# sources/distributed-fs/ceph-client/tools/include/nolibc/types.h

## Purpose
Defines nolibc's POSIX/Linux structure and constant surface shared by syscall wrappers.

## APIs, Types, and Functions
Defines `struct timespec`, `struct timeval`, file type and permission macros, directory entry type constants, `PATH_MAX`, `MAXPATHLEN`, `MAP_FAILED`, seek constants, reboot command aliases, wait-status macros, `EXIT_SUCCESS`/`EXIT_FAILURE`, `struct linux_dirent64`, nolibc `struct stat`, `clockid_t`, `timer_t`, and `container_of`.

## Control Flow, State, and Persistence
There is no executable control flow. The header fixes ABI layouts for stat, dirent, time, wait, and container calculations. Persistent meaning is compile-time layout and constant values shared with kernel syscalls.

## Dependencies and Integration
Depends on `std.h`, Linux `mman.h`, `stat.h`, `time_types.h`, `wait.h`, and selected time UAPI headers. It integrates with nearly every syscall and compatibility header.

## Risks and Test Signals
Risks include struct layout drift from kernel expectations, 32-bit time compatibility, `container_of` misuse, and incomplete libc constant coverage. Test signals are sizeof/offsetof checks for `stat`, dirent parsing with `getdents64`, time wrapper tests, wait-status decoding, and compile checks for all constants.
