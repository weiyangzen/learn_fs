<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sockios.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sockios.h

### Purpose
`sockios.h` defines MIPS socket-related ioctl command numbers for ownership, process groups, out-of-band mark detection, and legacy timestamp retrieval.

### Important APIs, Types, And Functions
The public constants are `FIOGETOWN`, `FIOSETOWN`, `SIOCATMARK`, `SIOCSPGRP`, `SIOCGPGRP`, `SIOCGSTAMP_OLD`, and `SIOCGSTAMPNS_OLD`. The `_IOR` and `_IOW` encodings come from `asm/ioctl.h`.

### Control Flow
There is no runtime logic. The preprocessor expands ioctl encodings with MIPS ioctl layout rules and fixed command numbers.

### State, Persistence, And Dependencies
The persistent state is the ioctl ABI. Dependencies are `asm/ioctl.h` and kernel socket ioctl handlers that decode the same numbers.

### Integration Points
Used by `asm/socket.h`, libc socket headers, old applications using `ioctl()` on sockets, and kernel networking ioctl dispatch.

### Risks
Timestamp values are explicitly old ABI entries; new time64-aware paths live elsewhere. Mixing generic and MIPS ioctl encodings would break userspace compatibility.

### Test Signals
Socket ioctl tests should cover `FIOGETOWN/FIOSETOWN`, `SIOCGPGRP/SIOCSPGRP`, `SIOCATMARK`, and old timestamp ioctl compatibility on 32-bit and 64-bit userlands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sockios.h -->
