<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/msghelpers/MsgHelperIO.h -->
## sources/distributed-fs/beegfs/storage/source/net/msghelpers/MsgHelperIO.h

### Purpose
Provides a central inline wrapper layer for storage-server POSIX IO syscalls and a compatibility wrapper for timestamp updates.

### Important APIs, Types, And Functions
APIs include open/openat/close/read/pread/write/pwrite/lseek/fsync, syncFileRange(), readAhead(), truncateAt(), and utimensat(). It defines MAX_KERNEL_READAHEAD, MsgHelperIO_ATIME_POS, MsgHelperIO_MTIME_POS, UTIME_OMIT fallback, and feature detection for real utimensat.

### Control Flow
Most methods directly call the matching syscall. readAhead() chunks posix_fadvise(POSIX_FADV_WILLNEED) calls into MAX_KERNEL_READAHEAD pieces. truncateAt() emulates truncateat by openat + ftruncate + close. utimensat() calls the real syscall when available, otherwise maps timespec to timeval and uses futimesat.

### State, Persistence, And Dependencies
No state is stored. Persistent effects are exactly the wrapped syscall effects on filesystem objects and kernel cache hints. Depends on Config/App includes, Program singleton for broader context, POSIX/Linux syscalls, compile-time CONFIG_DISTRO_HAS_SYNC_FILE_RANGE, and BeeGFS utility macros.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include the futimesat fallback approximating UTIME_OMIT by copying the other timestamp rather than preserving the current value, syncFileRange becoming a no-op on unsupported builds, and truncateAt close failures collapsing into generic -1.

### Test Signals
Test signals include syscall error propagation, partial readAhead ranges, UTIME_OMIT behavior on platforms with and without utimensat, truncateAt on missing and existing files, and syncFileRange compile variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/msghelpers/MsgHelperIO.h -->
