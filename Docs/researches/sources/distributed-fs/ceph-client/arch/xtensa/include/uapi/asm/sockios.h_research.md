<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sockios.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sockios.h

Purpose: defines Xtensa socket ioctl numbers for ownership, out-of-band mark checks, process group control, and old timestamp ioctls. Important constants are `FIOGETOWN`, `FIOSETOWN`, `SIOCATMARK`, `SIOCSPGRP`, `SIOCGPGRP`, `SIOCGSTAMP_OLD`, and `SIOCGSTAMPNS_OLD`.

Control flow is ioctl command dispatch in socket/file layers. Persistent state affected includes socket owner, process group, and timestamp copyout behavior. Dependencies include `asm/ioctl.h`, `pid_t`, and socket timestamp compatibility code. Integration points are libc socket APIs, networking stack, legacy applications, and strace. Risks are ABI-number mismatch or old timestamp layout compatibility bugs. Test signals include socket ioctl tests, `SIOCATMARK` behavior, timestamp ioctl compatibility, headers_install, and strace decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sockios.h -->
