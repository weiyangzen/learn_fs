# sources/distributed-fs/ceph-client/arch/sh/kernel/swsusp.c

Purpose: supplies SH hibernation architecture hooks.

Important APIs and control flow: global `swsusp_arch_regs_cpu0` stores CPU0 suspend registers. `pfn_is_nosave()` excludes the `__nosave` section from hibernation images. `save_processor_state()` initializes/saves current FPU state, and `restore_processor_state()` flushes all local TLB entries after resume.

State, dependencies, and risks: state includes saved arch registers, nosave linker section bounds, FPU state, and TLB contents. Dependencies include hibernation core, linker sections, SH FPU helpers, and TLB flush primitives. Risks include missing CPU state beyond FPU/TLB, SMP limitations, and incorrect nosave PFN calculation. Test signals are suspend-to-disk/resume, FPU-using workload across hibernate, and memory image excluding nosave pages.
