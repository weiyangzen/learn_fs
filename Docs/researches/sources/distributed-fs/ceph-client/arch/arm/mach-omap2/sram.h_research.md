<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram.h

### Purpose
`sram.h` declares OMAP2/3 SRAM-resident routine interfaces and physical SRAM base addresses shared between C setup code and assembly implementations.

### Important APIs, Types, And Functions
It declares generic wrappers such as `omap2_sram_ddr_init()`, `omap2_sram_reprogram_sdrc()`, `omap2_set_prcm()`, `omap_sram_init()`, and `omap_sram_push()`, plus the raw OMAP242x/243x assembly symbols and their `_sz` size labels. It also exposes `omap_push_sram_idle()` when power management is enabled.

### Control Flow
There is no runtime flow in the header. The declarations let `sram.c` copy assembly routines and let callers invoke the copied wrappers instead of directly calling code in normal memory.

### State, Persistence, And Dependencies
The header itself has no state. It depends on callers including suitable integer and init annotations, and it defines `OMAP2_SRAM_PA` and `OMAP3_SRAM_PA` as shared constants.

### Integration Points
The header is the contract between OMAP SRAM management, SDRAM/PRCM assembly, and idle/power-management code.

### Risks
Size symbols must continue to match the assembly entry ranges; otherwise `omap_sram_push()` can copy too little or too much code. The `CONFIG_PM` stub means callers must not assume idle code is pushed when PM is disabled.

### Test Signals
Build coverage should include OMAP2420, OMAP2430, OMAP3 with PM, and OMAP3 without PM to validate conditional declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram.h -->
