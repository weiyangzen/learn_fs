<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/siginfo.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/siginfo.h

### Purpose
This UAPI header specializes Linux `siginfo_t` layout and `si_code` values for the MIPS user ABI. It preserves IRIX-compatible values where MIPS historically diverged from generic Linux.

### Important APIs, Types, And Functions
It defines `__ARCH_SIGEV_PREAMBLE_SIZE`, advertises `__ARCH_HAS_SWAPPED_SIGINFO`, includes `asm-generic/siginfo.h`, and overrides `SI_ASYNCIO`, `SI_TIMER`, and `SI_MESGQ`.

### Control Flow
There is no runtime control flow. Preprocessor order is the important behavior: the generic header is included first, then selected generic `SI_*` values are undefined and replaced.

### State, Persistence, And Dependencies
The file persists ABI constants compiled into libc, userspace, and kernel signal code. It depends on generic signal-info definitions and on MIPS signal-frame code honoring the swapped layout marker.

### Integration Points
Signal delivery, queued signals, POSIX timers, AIO completion, message queues, and user-space headers all rely on these values matching the kernel ABI.

### Risks
Changing the numeric values or preamble size would break user-space binary compatibility. The swapped siginfo marker is subtle because it affects layout interpretation rather than a callable API.

### Test Signals
Useful checks are UAPI header compilation, signal queue/timer/AIO tests that inspect `si_code`, and ABI layout comparisons against libc on O32, N32, and N64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/siginfo.h -->
