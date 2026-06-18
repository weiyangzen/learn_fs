## sources/distributed-fs/ceph-client/arch/mips/kernel/smp-bmips.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/smp-bmips.c` provides SMP, hotplug, IPI, reset-vector relocation, and CPU setup support for Broadcom BMIPS processors. It handles BMIPS43xx race-prone software interrupts, BMIPS5000 raceless action-register IPIs, warm restart, and platform vector relocation used by secondary CPU boot.

### Important APIs, Types, And Functions
Platform globals include `bmips_smp_enabled`, `bmips_cpu_offset`, `bmips_booted_mask`, `bmips_tp1_irqs`, `bmips_smp_boot_sp`, and `bmips_smp_boot_gp`. Core functions include `bmips_smp_setup()`, `bmips_prepare_cpus()`, `bmips_boot_secondary()`, `bmips_init_secondary()`, `bmips_smp_finish()`, `bmips_cpu_disable()`, `play_dead()`, `bmips_ebase_setup()`, `bmips_cpu_setup()`, and reset vector helpers. Published `plat_smp_ops` are `bmips43xx_smp_ops` and `bmips5000_smp_ops`.

### Control Flow
Setup detects CPU type, configures CMT or BMIPS5000 mode registers, computes logical CPU maps, sets `board_ebase_setup`, and marks CPUs possible/present. CPU preparation requests two per-CPU software IRQs. Booting a secondary writes the idle task stack and thread_info GP to global handoff variables, programs reset vectors to KSEG0 or KSEG1 paths depending on first boot versus warm boot, and triggers reset or IPI action. The secondary clears pending IPIs, performs BMIPS CPU setup, enables interrupts in `bmips_smp_finish()`, and joins generic `start_secondary()`. Hotplug disables the CPU, migrates IRQs, flushes TLB/icache, enters `play_dead()`, waits for an IPI, and jumps through `bmips_secondary_reentry`.

### State, Persistence, And Dependencies
State is CP0 Broadcom registers, CBR memory-mapped registers, per-CPU IPI action masks, reset vector slots, boot stack globals, and CPU online/present maps. Nothing is persisted outside hardware register state and kernel topology. Dependencies include `asm/bmips.h`, `asm/traps.h`, `asm/cacheflush.h`, `asm/tlbflush.h`, `linux/irq.h`, hotplug, kexec, and assembly vectors such as `bmips_reset_nmi_vec` and `bmips_smp_int_vec`.

### Integration Points
This file registers platform SMP operations consumed by generic `smp.c`. It hooks board exception base setup via `board_ebase_setup`, NMI setup via `board_nmi_handler_setup`, and kexec through `kexec_nonboot_cpu_jump`. It shares interrupt actions with generic scheduler and call-function IPI handlers.

### Risks
Race-prone BMIPS43xx IPI handling depends on `ipi_lock` covering CP0 Cause writes and action masks. Reset vector writes must happen on CPU0 for BMIPS5000 and must use hazards/syncs. Boot stack handoff requires memory barriers. Hotplug must not leave active interrupts or stale cache/TLB state. CPU type conditionals are hardware-specific and easy to regress on older BMIPS variants.

### Test Signals
Test BMIPS43xx and BMIPS5000 boot, repeated CPU offline/online, IPI reschedule and call-function delivery, warm restart after hotplug, kexec nonboot CPU paths, relocated exception vectors, RAC setup, and systems booting on TP0 versus TP1.
