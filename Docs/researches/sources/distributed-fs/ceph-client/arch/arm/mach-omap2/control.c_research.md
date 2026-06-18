<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/control.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/control.c

## Purpose
`control.c` implements OMAP2/3 and AM33xx/AM43xx system-control-module access and selected low-power context handling. It provides the common byte/word/long MMIO accessors for the control module, OMAP3 scratchpad preparation for ROM-assisted resume, OMAP3 control-register save/restore, OMAP3 padconf save triggering, OMAP3 boot-mode programming, and AM43xx control-module CPU PM context save/restore.

## Important APIs, Types, and Functions
The public APIs are `omap_ctrl_readb()`, `omap_ctrl_readw()`, `omap_ctrl_readl()`, `omap_ctrl_writeb()`, `omap_ctrl_writew()`, `omap_ctrl_writel()`, `omap3_ctrl_write_boot_mode()`, `omap3_save_scratchpad_contents()`, `omap3_control_save_context()`, `omap3_control_restore_context()`, `omap3630_ctrl_disable_rta()`, `omap3_ctrl_save_padconf()`, `omap3_ctrl_init()`, `omap2_control_base_init()`, and `omap_control_init()`. Internal data includes OMAP3 scratchpad PRCM/SDRC block layouts, `omap3_arm_context`, `control_context`, AM43xx register offset/value arrays, and `control_init_data`.

## Control Flow
The accessors align subword offsets to 32-bit registers and mask/shift byte or halfword values. OMAP3 suspend support builds ROM scratchpad contents by selecting the correct restore entry point, copying PRCM and SDRC state, and appending the physical ARM context address. OMAP3 init enables control-module autoidle, idles IVA2 boot mode, and sets D2D pad pulls. AM43xx CPU PM notifiers save selected control registers on `CPU_CLUSTER_PM_ENTER` and restore them on exit. Base initialization maps legacy physical bases or looks up syscon/regmap data from OF match entries.

## State and Persistence Behavior
State is hardware register state plus static cached restore data. OMAP3 stores control-register snapshots in `control_context`, scratchpad resume data in SCM scratchpad RAM, and ARM register storage in `omap3_arm_context`. AM43xx stores register values in `am33xx_control_vals` across CPU cluster power transitions. No filesystem persistence exists; persistence is across low-power transitions and reset paths through scratchpad/control-module registers.

## Dependencies and Integration Points
The file depends on `control.h`, SoC detection, PRM/CM helpers, SDRC helpers, SRAM resume symbols, CPU PM notifiers, OF syscon/regmap, and low-level MMIO. It is consumed by revision detection, PM, display DSI pad muxing, secure resume, and many mach-omap2 helpers that call `omap_ctrl_*()`.

## Risks
The biggest risks are wrong control-module base selection, unbounded wait in `omap3_ctrl_save_padconf()`, register-list drift for AM43xx context save, invalid scratchpad layout for ROM resume, and accidental subword writes to shared 32-bit registers. Errors here can prevent resume, lose wakeup/pad state, or misidentify secure/GP device type.

## Test Signals
Boot OMAP3/AM33xx/AM43xx kernels with early console and confirm control base initialization, SoC type detection, and no WARNs. Exercise suspend/resume, MPU off/OSWR, padconf save, reboot boot-mode paths, and AM43xx CPU cluster PM. Useful checks are register traces around `CPU_CLUSTER_PM_ENTER/EXIT`, successful return from ROM resume, and absence of timeout or stuck loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/control.c -->
