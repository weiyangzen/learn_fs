<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/stat.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/stat.h

### Purpose
This header defines the MIPS `stat` and `stat64` userspace layouts for O32, N32, and N64. It preserves historic padding and nanosecond timestamp fields.

### Important APIs, Types, And Functions
For ABI32/NABI32 it defines `struct stat` and `struct stat64`; for ABI64 it defines `struct stat`. It uses `__kernel_ino_t`, `__kernel_mode_t`, `__kernel_uid32_t`, `__kernel_gid32_t`, and fixed padding around device and inode fields. `STAT_HAVE_NSEC` declares nanosecond timestamp availability.

### Control Flow
Preprocessor branches on `_MIPS_SIM` from `asm/sgidefs.h`. There is no runtime logic, but the chosen structure differs by ABI.

### State, Persistence, And Dependencies
The file is persistent syscall ABI state for `stat`, `fstat`, `lstat`, and related compat conversions. It depends on Linux UAPI integer types and MIPS ABI-selection macros.

### Integration Points
VFS stat syscall copying, libc `struct stat`, filesystem tests, strace decoders, and cross-ABI compat code all depend on these layouts.

### Risks
The padding is deliberate and non-obvious. Changing field sizes, signedness, or ABI conditionals would corrupt file metadata observed by existing binaries.

### Test Signals
ABI tests should compare `sizeof`, offsets, nanosecond fields, large inode/file-size behavior, and syscall output across O32, N32, and N64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/stat.h -->
