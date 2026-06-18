<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/head.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/head.S

### Purpose
`head.S` is the primary MIPS kernel entry assembly. It reserves exception-vector space, sets initial CP0 status, clears BSS, records firmware arguments, creates the first kernel stack, optionally relocates the kernel, and transfers control to `start_kernel`. It also defines the SMP secondary entry point.

### Important APIs, Types, And Functions
Important labels and macros are `_stext`, optional `__kernel_entry`, `kernel_entry`, `smp_bootstrap`, `setup_c0_status`, `setup_c0_status_pri`, and `setup_c0_status_sec`. It uses platform-provided `kernel_entry_setup` and `smp_slave_setup` macros from `kernel-entry-init.h`.

### Control Flow
Primary entry runs CPU-specific setup, disables interrupts while configuring kernel mode and 64-bit address support when needed, jumps to the linked address, zeros `.bss`, saves `a0` through `a3` into `fw_arg*`, clears CP0 context registers, initializes `$28` and `sp` from `init_thread_union`, records saved stack pointer, and then either calls `relocate_kernel` or jumps to `start_kernel`. SMP secondaries execute the board slave setup, use secondary CP0 status that clears BEV, and jump to `start_secondary`.

### State, Persistence, And Dependencies
Persistent early state includes `.bss` zeroing, firmware argument globals, CP0 Status/Context/XContext, initial thread stack, and saved kernel stack pointer. The file depends on linker symbols, stackframe offsets, MIPS CP0 hazard sequencing, and optional relocatable kernel support.

### Integration Points
This is the bridge from firmware or raw boot to the generic Linux kernel. It integrates with platform entry setup, relocation code, `start_kernel`, SMP startup, and exception-vector layout expected by `genex.S`.

### Risks
Entry code has no recovery path. Wrong CP0 status bits, stack placement, BSS bounds, or relocation jump target will fail before console diagnostics. The reserved exception fill must match link address and platform vector expectations.

### Test Signals
Validation is architecture boot coverage: raw and ELF boot paths, 32-bit and 64-bit configs, relocatable and non-relocatable kernels, firmware argument parsing, SMP secondary bring-up, and early exception handling before `trap_init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/head.S -->
