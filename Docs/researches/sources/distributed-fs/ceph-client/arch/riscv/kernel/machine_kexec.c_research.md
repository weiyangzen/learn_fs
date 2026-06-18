# sources/distributed-fs/ceph-client/arch/riscv/kernel/machine_kexec.c

Purpose: Implements architecture-level kexec preparation, shutdown, cleanup, and final machine transition for RISC-V.

Important APIs/types/functions: Provides `machine_kexec_prepare()`, `machine_kexec_cleanup()`, `machine_shutdown()`, `machine_crash_shutdown()`, and `machine_kexec()`.

Control flow: Prepare validates and records kexec image state. Shutdown stops secondary CPUs and masks interrupts. Crash shutdown preserves crash state. `machine_kexec()` copies relocation code to a control page, flushes it, prepares hart/FDT/entry arguments, and jumps into `riscv_kexec_relocate` or no-relocate code.

State and persistence: Mutates `struct kimage`, per-CPU shutdown state, crash registers, and physical control pages. No file-local long-lived data beyond setup.

Dependencies and integration points: Depends on kexec core, SMP stop, crash dump, MMU/cache flushing, `kexec_relocate.S`, and RISC-V boot protocol.

Risks and test signals: Secondary CPU shutdown and control-code relocation are critical. Test normal kexec, panic kdump, CPU hotplug before kexec, no-MMU or MMU variants, and repeated kexec cycles.
