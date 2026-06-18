<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-highbank/sysregs.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-highbank/sysregs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-highbank/sysregs.h` belongs to Calxeda Highbank/ECX-2000 platform support in the Ceph-client kernel source snapshot. It exports register definitions, physical/virtual address helpers, IRQ constants, or prototypes consumed by adjacent platform C/assembly files.

### Important APIs, Types, And Functions
Notable functions/entry points: `highbank_set_core_pwr`, `highbank_clear_core_pwr`, `highbank_set_pwr_suspend`, `highbank_set_pwr_shutdown`, `highbank_set_pwr_soft_reset`, `highbank_set_pwr_hard_reset`, `highbank_clear_pwr_request`. Important macros/register names include `_MACH_HIGHBANK__SYSREGS_H_`, `HB_SREG_A9_PWR_REQ`, `HB_SREG_A9_BOOT_STAT`, `HB_SREG_A9_BOOT_DATA`, `HB_PWR_SUSPEND`, `HB_PWR_SOFT_RESET`, `HB_PWR_HARD_RESET`, `HB_PWR_SHUTDOWN`, `SREG_CPU_PWR_CTRL(c)`.

### Control Flow
Suspend paths save selected registers, mask non-wakeup IRQs, enter firmware or CPU suspend callbacks, then restore register state and wake masks during resume.

### State, Persistence, And Dependencies
Dependencies include `linux/io.h`, `linux/smp.h`, `asm/smp_plat.h`, `asm/smp_scu.h`, `core.h`. Local/static state or exported register data includes `int cpu = MPIDR_AFFINITY_LEVEL(cpu_logical_map(smp_processor_id()), 0)`. Compatible strings or firmware/device-tree identifiers observed: none. There is no private runtime persistence in this header; it defines constants and declarations used by compiled platform code.

### Integration Points
Integration points are PM core, syscore, and CPU suspend/resume, ARM SMP, hotplug, and MCPM. Callers should treat `highbank_set_core_pwr`, `highbank_clear_core_pwr`, `highbank_set_pwr_suspend`, `highbank_set_pwr_shutdown`, `highbank_set_pwr_soft_reset`, `highbank_set_pwr_hard_reset`, `highbank_clear_pwr_request` as platform hooks rather than generic APIs when those symbols are visible.

### Risks
Primary risks include MMIO or port-I/O ordering, missing barriers, and incorrect register bit definitions, resume failures, lost wakeups, and low-power state mismatches, CPU bring-up/hotplug races and coherency/cache maintenance bugs.

### Test Signals
Useful test signals include ARM build coverage for the relevant CONFIG symbols, suspend-to-RAM, idle entry/exit, and wake-source validation, secondary CPU online/offline hotplug loops under load. Source reading signal: 75 lines; 5 includes; 7 function/entry points; 9 macro/defines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-highbank/sysregs.h -->
