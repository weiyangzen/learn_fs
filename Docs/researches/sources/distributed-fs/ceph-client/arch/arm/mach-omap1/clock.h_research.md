<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock.h

Purpose: OMAP1 clock framework header. It defines `omap_clk`, `clkops`, `omap1_clk`, `arm_idlect1_clk`, `uart_clk`, CPU mask flags, clock flags, and function prototypes for clock operations and init.

Important APIs/types/functions: Important declarations include `CLK`, `CK_*` platform masks, `ENABLE_REG_32BIT`, `CLOCK_IDLE_CONTROL`, `CLOCK_NO_IDLE_PARENT`, `omap1_clk_init`, `omap1_clk_late_init`, rate helpers, and global clock pointers.

Control flow, state, and persistence: The header itself stores no state but describes state fields used by `clock.c` and `clock_data.c`: hardware registers, enable bits, rate offsets, fixed divisors, and idle counters.

Dependencies and integration points: Important declarations include `CLK`, `CK_*` platform masks, `ENABLE_REG_32BIT`, `CLOCK_IDLE_CONTROL`, `CLOCK_NO_IDLE_PARENT`, `omap1_clk_init`, `omap1_clk_late_init`, rate helpers, and global clock pointers. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are struct layout coupling between declarative clock data and operation code, and global pointer use before init. Test compile coverage and clock registration on OMAP15xx/16xx/7xx variants.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 195 lines, 6746 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock.h -->
