## sources/distributed-fs/ceph-client/arch/arm64/kernel/sleep.S

### Purpose
`sleep.S` provides the low-level ARM64 CPU suspend/resume assembly path. It saves callee-saved registers and the stack pointer into `struct sleep_stack_data`, records the per-CPU context pointer in `sleep_save_stash`, and restores CPU state after firmware or platform code resumes the core.

### Important APIs, Types, And Functions
`__cpu_suspend_enter`, `cpu_resume`, `_cpu_resume`, and the local `compute_mpidr_hash` macro are the important entry points. The code depends on `mpidr_hash`, `sleep_save_stash`, `cpu_do_suspend`, `cpu_do_resume`, `init_kernel_el`, `__cpu_setup`, `__enable_mmu`, `finalise_el2`, and optional KASAN stack unpoisoning.

### Control Flow
Suspend enters with `x0` pointing at the sleep stack data, stores frame/callee registers, saves `sp`, hashes `MPIDR_EL1` to select the current CPU stash slot, publishes the context pointer, calls `cpu_do_suspend`, and returns nonzero to tell C code to run the finisher. Resume starts in `.idmap.text`, initializes exception level state, rebuilds early CPU setup, enables the MMU using the idmap and swapper page tables, branches to `_cpu_resume`, restores EL2, recomputes the MPIDR hash, loads the stashed context, restores `sp`, calls `cpu_do_resume`, reloads saved registers, and returns zero to the suspended C frame.

### State, Persistence, And Dependencies
Persistent state is CPU register context in `sleep_stack_data`, per-CPU context addresses in `sleep_save_stash`, and hardware state restored by `cpu_do_resume`. There is no filesystem persistence. Correctness depends on the MPIDR hash matching the C-side topology setup and on the stash memory being visible before firmware powers the CPU down.

### Integration Points
This file is called by `suspend.c` through `__cpu_suspend_enter` and returns into `cpu_suspend()`. It also integrates with boot/idmap code, KASAN, EL2 finalization, CPU feature setup, and the linker-script placement of `.idmap.text` and `.mmuoff` data.

### Risks
The main risks are corrupt stack/context offsets, MPIDR hash mismatches on systems with unusual affinity topology, stale cache visibility across power loss, returning through the wrong path, and breaking early-MMU/idmap assumptions. Assembly register constraints are tight because the hash macro mutates its inputs.

### Test Signals
Exercise CPU idle, suspend-to-RAM, CPU hotplug-style resume paths, KASAN stack builds, EL1/EL2 boot combinations, and systems with sparse MPIDR affinities. Disassembly should confirm context offsets match `asm-offsets.h`.
