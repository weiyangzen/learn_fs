<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/socket.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/socket.h

### Purpose
This header defines MIPS socket-level option numbers and timestamp compatibility aliases for userspace `setsockopt`, `getsockopt`, control messages, and socket timestamp ioctls.

### Important APIs, Types, And Functions
It exports `SOL_SOCKET`, legacy and Linux-specific `SO_*` option values, `SCM_*` aliases, timestamp old/new constants, time64-sensitive aliases for `SO_TIMESTAMP`, `SO_TIMESTAMPNS`, `SO_TIMESTAMPING`, `SO_RCVTIMEO`, and `SO_SNDTIMEO`, and includes `asm/sockios.h`.

### Control Flow
The only control flow is preprocessor selection. For non-kernel userspace, 64-bit long builds keep old timeout/timestamp values, while 32-bit userspace chooses old or new values based on `sizeof(time_t)` relative to `__kernel_long_t`.

### State, Persistence, And Dependencies
All state is ABI state in numeric constants. It depends on Linux POSIX types, MIPS sockios values, and libc exposing compatible `time_t` and kernel-long definitions.

### Integration Points
Networking syscalls, cmsg parsing, timestamping, BPF socket filters, zero-copy, busy polling, device-memory socket options, and libc headers consume these values.

### Risks
The MIPS `SOL_SOCKET` value and many option numbers are architecture ABI rather than generic C enum values. Time64 aliasing is easy to break if libc feature macros do not match kernel UAPI expectations.

### Test Signals
Run socket option ABI tests under O32/N32/N64, timestamp old/new tests with 32-bit and 64-bit `time_t`, and userspace header selftests that compare option numbers to kernel behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/socket.h -->
