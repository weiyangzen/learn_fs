<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/control.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/control.h

## Purpose
`control.h` is the central OMAP2/3/4/5/AM/DRA control-module register map and API declaration header. It names control submodules, register offsets, scratchpad addresses, bitfields, feature-detection masks, padconf bits, and function prototypes used by platform setup and power-management code.

## Important APIs, Types, and Functions
Important macros include `OMAP242X_CTRL_REGADDR()`, `OMAP243X_CTRL_REGADDR()`, `OMAP343X_CTRL_REGADDR()`, `AM33XX_CTRL_REGADDR()`, `OMAP2_CONTROL_*`, `OMAP343X_CONTROL_*`, `OMAP4_CTRL_MODULE_*`, `OMAP5XXX_CONTROL_STATUS`, `DRA7_CTRL_CORE_BOOTSTRAP`, and AM33xx/AM43xx control register offsets. It declares `omap_ctrl_read{b,w,l}()`, `omap_ctrl_write{b,w,l}()`, OMAP3 restore symbols, `omap3_arm_context`, OMAP3 control context functions, `omap2_control_base_init()`, and `omap_control_init()`.

## Control Flow
The header itself has no runtime control flow. Compile-time selection depends on `__ASSEMBLY__` and `CONFIG_ARCH_OMAP2PLUS`: real prototypes are emitted for OMAP2+ builds, while stubs return zero or warn for non-OMAP builds. The offsets feed `control.c`, SoC revision detection, display DSI pad muxing, MMC/I2C/McBSP configuration, and PM save/restore code.

## State and Persistence Behavior
It stores no mutable state. Its constants describe persistent hardware ABI: register offsets, bit meanings, scratchpad layout, efuse locations, and feature bits. Any change can alter how runtime code reads SoC status, preserves suspend context, or programs pad mux and control registers.

## Dependencies and Integration Points
It includes `am33xx.h` and relies on address macros from the OMAP static IO map. It integrates with `control.c`, `id.c`, `display.c`, `mcbsp.c`, PM code, and low-level assembly that needs scratchpad or control addresses.

## Risks
Register definitions span several SoC families and some comments note partial coverage. A mistaken offset or mask can silently target the wrong hardware register. The fallback stubs can hide missing config coverage in compile-only builds. Generated or hardware-database-sourced values should be cross-checked against TRMs when edited.

## Test Signals
Compile multi-OMAP ARM builds with OMAP2, OMAP3, OMAP4, AM33xx, AM43xx, OMAP5, and DRA7 options. Runtime signals include correct `omap_type()`, `omap_rev()`, control-module syscon probing, display/DSI pad setup, MMC/I2C boot, and suspend/resume on affected SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/control.h -->
