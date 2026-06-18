## sources/distributed-fs/ceph-client/arch/mips/kernel/signal_n32.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/signal_n32.c` implements realtime signal frame setup and return for the MIPS n32 ABI. n32 uses 32-bit user pointers and compat signal sets with the native 64-bit `struct sigcontext` register representation.

### Important APIs, Types, And Functions
Important types are `struct ucontextn32` and `struct rt_sigframe_n32`. Entry points are `sysn32_rt_sigreturn()` and `setup_rt_frame_n32()`. The exported ABI descriptor is `struct mips_abi mips_abi_n32`, with `restart` set to `__NR_N32_restart_syscall`, native sigcontext offsets, and `vdso_image_n32`.

### Control Flow
Delivery uses `get_sigframe()` from the native signal core, writes compat siginfo through `copy_siginfo_to_user32()`, stores a compat altstack and signal mask, and delegates register/FPU/MSA save to `setup_sigcontext()`. Return reads the frame from the user stack, converts the compat signal mask, restores the blocked mask, restores native sigcontext, restores the compat altstack, and jumps through `syscall_exit`.

### State, Persistence, And Dependencies
The persistent ABI is the n32 realtime frame layout, including 32-bit `uc_link`, `compat_stack_t`, native `struct sigcontext`, and compat sigset placement. Runtime state is per-task signal mask, altstack, current register state, and current ABI descriptor. Dependencies include `asm/abi.h`, `asm/compat-signal.h`, `asm/ucontext.h`, `asm/fpu.h`, VDSO image declarations, and generic compat siginfo conversion.

### Integration Points
`mips_abi_n32` is selected for n32 tasks by the MIPS ABI layer and consumed by `handle_signal()` in `signal.c`. It shares native FP/MSA save and restore helpers with `signal.c` and shares compat sigset conversion conventions with `signal_o32.c`.

### Risks
The main risk is mixing native and compat layout assumptions: sigcontext offsets are native, while siginfo, stack, links, and masks are compat. Wrong restart syscall numbers or VDSO image offsets would break interrupted syscall restart and sigreturn. Bad frame validation must reliably force `SIGSEGV`.

### Test Signals
Test n32 realtime signal delivery, altstack save/restore, interrupted syscall restart, FPU/MSA context preservation, siginfo conversion, invalid frame pointers, and VDSO n32 `rt_sigreturn`.
