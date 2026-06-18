<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/signal32.h -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/signal32.h

### Purpose
`signal32.h` defines compat signal-frame data structures and helpers for 32-bit user processes on 64-bit PA-RISC kernels.

### Important APIs, Types, And Functions
It declares `struct compat_ucontext`, `struct compat_regfile`, `struct compat_rt_sigframe`, `PARISC_RT_SIGFRAME_SIZE32`, `restore_sigcontext32()`, and `setup_sigcontext32()`.

### Control Flow
The header has no runtime control flow. It establishes that the visible 32-bit ucontext is followed by a hidden register file storing upper halves of truncated registers.

### State, Persistence, And Dependencies
User stack signal frames persist according to these layouts. Dependencies include Linux compat types, `compat_sigcontext`, and PA-RISC frame-size constants.

### Integration Points
Consumed by `signal.c` and `signal32.c`; offsets are also relevant to VDSO signal trampoline unwind metadata.

### Risks
Frame-size and alignment constants must match assembly and GDB expectations. The hidden regfile must remain last because `uc_sigmask` extensibility can move it.

### Test Signals
Build-time offset checks, compat signal delivery/return, GDB backtrace through compat trampolines, and altstack frame alignment validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/signal32.h -->
