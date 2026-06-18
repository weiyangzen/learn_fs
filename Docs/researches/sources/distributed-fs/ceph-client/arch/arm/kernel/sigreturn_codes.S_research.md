# sources/distributed-fs/ceph-client/arch/arm/kernel/sigreturn_codes.S

Purpose: defines the small ARM/Thumb/FDPIC signal return trampoline instruction sequences copied to user stacks or the sigpage.

Important APIs/types/functions: exports `sigreturn_codes`, an array consumed by `signal.c` and `get_signal_page`. Variants cover plain `sigreturn`, `rt_sigreturn`, ARM/Thumb mode, and FDPIC descriptor loading.

Control flow: user signal handlers return through these sequences, which load the appropriate syscall number and invoke SWI/SVC to enter `sys_sigreturn` or `sys_rt_sigreturn`.

State and persistence: code is copied into the randomized sigpage and sometimes user stack frames, then executed by userspace.

Dependencies and integration: must match syscall numbers, Thumb/ARM instruction encoding, FDPIC handler setup, and signal frame construction.

Risks: incorrect opcode ordering or cache visibility breaks every signal return path. Test signals include signal return on ARM and Thumb tasks, realtime signals, FDPIC handlers, and sigpage execution checks.
