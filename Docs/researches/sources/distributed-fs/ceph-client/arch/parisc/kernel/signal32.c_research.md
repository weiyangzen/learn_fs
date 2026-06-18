<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/signal32.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/signal32.c

### Purpose
`signal32.c` translates between 64-bit kernel register state and 32-bit PA-RISC compat signal frames.

### Important APIs, Types, And Functions
It implements `restore_sigcontext32()` and `setup_sigcontext32()`, using `struct compat_sigcontext` plus the hidden `struct compat_regfile`.

### Control Flow
Setup truncates each 64-bit GPR, IAOQ, IASQ, and SAR into the compat sigcontext while storing upper halves in the hidden regfile. It copies 64-bit FP registers unchanged. Restore rebuilds 64-bit registers from lower sigcontext halves and upper regfile halves, then restores FP, queues, spaces, and SAR.

### State, Persistence, And Dependencies
Persistent state is the user signal frame and hidden upper-half regfile. Dependencies are compat accessors, `pt_regs`, `PARISC_SC_FLAG_*`, and the frame layout declared in `signal32.h`.

### Integration Points
Called from `signal.c` whenever a 32-bit task runs on a 64-bit kernel.

### Risks
The hidden regfile is non-ABI and layout-sensitive, but required to preserve full 64-bit kernel register contents. Any mismatch with `PARISC_RT_SIGFRAME_SIZE32` or userspace unwinding breaks compat signal return.

### Test Signals
Compat signal tests should verify high-half preservation, FP register round trips, syscall and non-syscall delivery, altstack restore, and malformed user frame `-EFAULT` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/signal32.c -->
