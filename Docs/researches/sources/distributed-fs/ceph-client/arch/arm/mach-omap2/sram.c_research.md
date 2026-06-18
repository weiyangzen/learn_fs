<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram.c

### Purpose
`sram.c` detects accessible OMAP internal SRAM, maps it executable, and copies small timing-critical routines into SRAM so SDRAM and clock-controller changes can run while external memory is unsafe.

### Important APIs, Types, And Functions
Public APIs are `omap_sram_init()`, `omap_sram_push()`, `omap2_sram_ddr_init()`, `omap2_sram_reprogram_sdrc()`, `omap2_set_prcm()`, and `omap3_sram_restore_context()`. Internal state includes `omap_sram_start`, `omap_sram_size`, `omap_sram_base`, `omap_sram_skip`, and `omap_sram_ceil`.

### Control Flow
`omap_sram_init()` detects public versus full SRAM depending on device type and security/firewall state, maps the region with `__arm_ioremap_exec()`, clears usable SRAM, marks it read-only executable, and pushes SoC-specific assembly functions for OMAP242x or OMAP243x. OMAP3 restore resets the allocator ceiling and repushes idle code through `omap_push_sram_idle()`.

### State, Persistence, And Dependencies
The file keeps a bump allocator that grows downward from the SRAM ceiling. Pushed function pointers persist in static function-pointer variables and are called by wrappers that `BUG_ON()` if initialization failed. Dependencies include `fncpy`, ARM page permission helpers, SoC detection, PRM/SDRC register addresses, and assembly symbols from `sram242x.S` and `sram243x.S`.

### Integration Points
Clock, SDRAM, idle, and power-management code call the wrapper APIs when hardware changes must be executed from SRAM. The code also interacts with OMAP RAM firewall registers to unlock GP-device SRAM.

### Risks
SRAM sizing or firewall mistakes can hang the system because secure SRAM cannot be probed safely. The allocator has no free path and only logs out-of-space failures. Page permission toggling around `fncpy()` must stay correct or copied code may be writable/executable at the wrong time. Calling wrappers before `omap_sram_init()` panics through `BUG_ON()`.

### Test Signals
Boot on OMAP2420, OMAP2430, and OMAP3 should show successful SRAM mapping and no wrapper BUGs. Suspend/resume and DVFS tests should cover OMAP3 SRAM context restore and repeated function repush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram.c -->
