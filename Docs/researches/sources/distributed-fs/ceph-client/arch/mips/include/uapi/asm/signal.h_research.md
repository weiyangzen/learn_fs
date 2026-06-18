<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/signal.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/signal.h

### Purpose
`signal.h` defines the MIPS userspace signal ABI: signal numbers, `sigset_t`, legacy signal masks, `sigaction`, alternate signal stack shape, and signal action flags.

### Important APIs, Types, And Functions
Key ABI items are `_NSIG == 128`, `_NSIG_WORDS`, `sigset_t`, `old_sigset_t`, numbered `SIG*` constants, `SIGRTMIN`, `SIGRTMAX`, `SA_*` flags, `MINSIGSTKSZ`, `SIGSTKSZ`, `SIG_BLOCK`, `SIG_UNBLOCK`, `SIG_SETMASK`, `struct sigaction`, and `stack_t`.

### Control Flow
There is no executable logic. Conditional compilation hides `struct sigaction` from kernel builds and includes `asm-generic/signal-defs.h` after MIPS-specific signal numbers and mask operations are defined.

### State, Persistence, And Dependencies
The header persists process-visible ABI numbers and structure layouts. It depends on `linux/types.h` for fixed kernel types and on generic signal helper declarations.

### Integration Points
The signal core, MIPS signal-frame assembly/C code, libc, ptrace tests, and applications using realtime signals or alternate stacks must all agree on this header.

### Risks
The signal numbering differs from some other architectures, and `SA_RESTORER` is intentionally reserved despite removed functionality. Any layout or numeric change is an ABI break.

### Test Signals
Signals tests should validate delivery numbers, mask size, realtime range, alternate stack operation, `sigaction` layout under userspace compilation, and kernel asm offset generation for signal constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/signal.h -->
