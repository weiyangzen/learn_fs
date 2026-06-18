<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/unistd.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/unistd.h

### Purpose
This header chooses the syscall-number table for the active MIPS userspace ABI and establishes the ABI-specific Linux syscall base.

### Important APIs, Types, And Functions
It includes `asm/sgidefs.h`, tests `_MIPS_SIM`, sets `__NR_Linux` to `4000` for O32, `5000` for N64, or `6000` for N32, and includes `asm/unistd_o32.h`, `asm/unistd_n64.h`, or `asm/unistd_n32.h`.

### Control Flow
The preprocessor selects exactly one syscall table according to the compiler ABI. There is no runtime logic.

### State, Persistence, And Dependencies
The persistent state is syscall numbering. Dependencies are generated syscall headers and MIPS ABI-selection macros.

### Integration Points
Libc syscall wrappers, seccomp filters, strace, audit, ptrace, and the MIPS syscall entry assembly must agree with these numbers.

### Risks
Using the wrong `_MIPS_SIM` during header generation or cross-compilation silently targets the wrong syscall table. The base numbers are part of the ABI and cannot change.

### Test Signals
Syscall ABI tests should compare generated numbers against kernel syscall tables, run simple syscalls under O32/N32/N64, and validate seccomp/audit decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/unistd.h -->
