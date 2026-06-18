# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-setup.c

Purpose: IP30 platform setup for HEART mapping, memory discovery, CPU timer calibration, per-CPU initialization, and I/O base setup.

Important APIs and control flow: global `heart_regs` points at `HEART_XKPHYS_BASE`. `ip30_mem_init()` walks HEART memory-bank config registers, computes base/size, and frees RAM above the PROM-reported 1 GB window into memblock. `ip30_cpu_time_init()` compares CP0 count against HEART count over 0.1 seconds to derive `mips_hpt_frequency`. `ip30_per_cpu_init()` masks interrupts, calibrates CPU time, installs IPIs under SMP, and enables HEART chained IRQs. `plat_mem_setup()` runs memory init, sets `PROM_FLAG_DONT_FREE_TEMP`, registers SMP ops or initializes the boot CPU, and sets the I/O port base.

State, persistence, and integration: state includes HEART MMIO pointer, memblock additions, `mips_hpt_frequency`, per-CPU IRQ state, and MIPS I/O resources. Dependencies include HEART registers, ARCS memory limitations, SMP code, and IRQ setup. Risks include `memblock_phys_free()` assumptions about earlier reserved ranges, busy-wait calibration, and hard lock note if PROM temp memory is freed. Test signals are detected memory log, CPU MHz log, HEART IRQ enablement, and boot with memory above 1 GB.
