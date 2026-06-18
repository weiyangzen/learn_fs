<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/Makefile

### Purpose
This Makefile defines the core Linux/MIPS kernel object graph, selecting CPU probing, exception entry, syscall, timer, SMP, FPU, tracing, kexec, VDSO, and platform clocksource/clockevent objects according to configuration.

### Important APIs, Types, And Functions
The base `obj-y` includes fundamental files such as `head.o`, `branch.o`, `cmpxchg.o`, `elf.o`, `entry.o`, `irq.o`, `process.o`, `signal.o`, `syscall.o`, `time.o`, `traps.o`, `vdso.o`, and `cacheinfo.o`. Conditional lines select CPU probe variants, clock event/source drivers, SMP/CPS/BMIPS support, syscall ABI objects, kexec/crash, early printk, perf, PM, and VPE loader objects.

### Control Flow
Kbuild evaluates config symbols to assemble the object list. It also removes ftrace flags from selected low-level objects and probes assembler support for `-mdaddi` for `r4k-bugs64.o`.

### State, Persistence, And Dependencies
The persistent state is the kernel link composition. It depends on architecture Kconfig symbols, generated syscall tables, and compiler/assembler feature detection.

### Integration Points
This is the central integration point for all kernel files in this subset and for generic Linux subsystems that need MIPS implementations.

### Risks
Wrong conditional selection can link incompatible syscall ABIs, duplicate CPU probe paths, or instrument fragile low-level code with ftrace. Conditional clock/timer objects must match platform Kconfig.

### Test Signals
Build matrix coverage for 32/64-bit, CPU_R3K_TLB, MIPS32 compat, CPS, BMIPS, early printk, kexec, perf, and tracing configs catches most integration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/Makefile -->
