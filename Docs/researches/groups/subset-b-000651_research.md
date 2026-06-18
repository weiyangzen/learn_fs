# Research Group subset-b-000651

Grouped research for OMAP2/3/4/5/DRA7 ARM platform integration files under `sources/distributed-fs/ceph-client/arch/arm/mach-omap2`. Each source file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cpuidle34xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cpuidle34xx.c

## Purpose
`cpuidle34xx.c` registers and implements CPU idle states for OMAP3-class systems. It maps cpuidle C-states to MPU, CORE, and PER powerdomain targets while applying OMAP3-specific constraints for off mode, camera wakeup limitations, and PER wakeup safety.

## Important APIs, Types, and Functions
The exported init API is `omap3_idle_init()`. Key internals are `struct omap3_idle_statedata`, `omap3_idle_data[]`, `omap3_enter_idle()`, `next_valid_state()`, `omap3_enter_idle_bm()`, and two cpuidle driver descriptions: `omap3_idle_driver` and `omap3430_idle_driver`. It uses global PM state such as `enable_off_mode` and erratum checks.

## Control Flow
`omap3_idle_init()` looks up the `mpu_pwrdm`, `core_pwrdm`, `per_pwrdm`, and `cam_pwrdm` powerdomains, then registers the generic OMAP3 driver or the latency-tuned OMAP3430/N900-era driver. On idle entry, `omap3_enter_idle_bm()` downgrades to the safe state if CAM is on, selects the next legal state based on off-mode policy and errata, raises PER minimum power state if needed, and calls `omap3_enter_idle()`. `omap3_enter_idle()` programs next power states, optionally saves CPU PM context for MPU off, enters SRAM idle, and restores CPU PM context if MPU actually reached off.

## State and Persistence Behavior
Mutable state is held in hardware powerdomain next/previous-state registers and clockdomain idle state. The function temporarily changes PER next power state and restores it after idle. CPU/VFP interrupt context is preserved through CPU PM notifiers when MPU off is attempted. No persistent storage exists.

## Dependencies and Integration Points
It depends on cpuidle core, `asm/cpuidle.h`, OMAP PM/SRAM idle code, powerdomain and clockdomain frameworks, SoC/erratum detection, and `control.h`. It integrates with OMAP3 suspend/idle policy and with device wakeup requirements through powerdomain state.

## Risks
Incorrect state selection can disable PER wakeups, enter unsupported CORE off on erratum-affected silicon, or leave clockdomains denied. The CAM active check is critical because CAM lacks wakeup capability. Latency/residency numbers drive governor decisions and can cause power or responsiveness regressions if changed incorrectly.

## Test Signals
Build with `CONFIG_CPU_IDLE` and OMAP3 PM enabled. Runtime checks include `/sys/devices/system/cpu/cpuidle`, powerdomain previous-state counters, wakeup from UART/GPIO/timers, camera active idle behavior, and suspend-idle stress with `enable_off_mode` toggled. Watch for lost wakeups and CPU PM notifier imbalance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cpuidle34xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cpuidle44xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cpuidle44xx.c

## Purpose
`cpuidle44xx.c` implements cpuidle support for OMAP4 and OMAP5 MPUSS idle states. It coordinates per-CPU low-power entry with MPUSS powerdomain programming, timer broadcast, CPU PM notifiers, coupled idle barriers, and OMAP4 GIC-distributor erratum handling.

## Important APIs, Types, and Functions
The public entry is `omap4_idle_init()`. Key internals are `struct idle_statedata`, `omap4_idle_data[]`, `omap5_idle_data[]`, `omap_enter_idle_simple()`, `omap_enter_idle_smp()`, `omap_enter_idle_coupled()`, `omap4_idle_driver`, and `omap5_idle_driver`. Shared state includes `mpu_pd`, `cpu_pd[]`, `cpu_clkdm[]`, `abort_barrier`, `cpu_done[]`, `state_ptr`, and `mpu_lock`.

## Control Flow
Initialization selects OMAP5 data for OMAP54xx and OMAP4 data otherwise, resolves MPU/CPU powerdomains and CPU clockdomains, then registers cpuidle against online CPUs. C1 executes plain WFI. OMAP5 C2 uses a spinlock and per-state vote counter so the MPU state is programmed only when all online CPUs vote for the same state. OMAP4 coupled states wait for CPU1 to enter off, enter timer broadcast, save CPU and cluster PM context, program MPUSS state from CPU0, call `omap4_enter_lowpower()`, wake CPU1 if needed, restore GIC/WakeupGen context, and pass through the coupled abort barrier.

## State and Persistence Behavior
State is powerdomain target state, coupled-idle synchronization flags, timer broadcast state, and CPU/cluster PM saved context. `cpu_done[]` prevents CPU0 from spinning forever if CPU1 attempted and left idle. The driver does not write persistent storage, but it depends on lower MPUSS code to use SAR RAM for context restore.

## Dependencies and Integration Points
It depends on cpuidle, tick broadcast, CPU PM, OMAP PM low-power entry, PRM/powerdomain/clockdomain helpers, SoC detection, GIC erratum helpers from `omap4-common.c`, and `omap4_enter_lowpower()` from `omap-mpuss-lowpower.c`.

## Risks
Coupled idle is concurrency-sensitive. Races around CPU1 off detection, GIC distributor disable/reenable, or CPU PM error fallback can hang SMP resume or lose timer interrupts. Wrong `state_count` or state data can make cpuidle index assumptions invalid. OMAP5 voting must correctly track online CPUs or MPUSS state may be over-programmed.

## Test Signals
Boot SMP OMAP4/OMAP5 with cpuidle enabled, inspect cpuidle state residency, repeatedly offline/online CPU1, run timer wakeup tests, and stress idle under interrupts. On OMAP446x, verify no local-timer loss after GIC erratum handling and no stalls at the coupled barrier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cpuidle44xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ctrl_module_wkup_44xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ctrl_module_wkup_44xx.h

## Purpose
`ctrl_module_wkup_44xx.h` defines OMAP44xx wakeup control-module base addresses, register offsets, and bitfields generated from TI hardware databases. It is a low-level register definition header for the wakeup-side control module.

## Important APIs, Types, and Functions
There are no functions or types. Important constants include `OMAP4_CTRL_MODULE_WKUP`, `OMAP4_CTRL_MODULE_WKUP_IP_REVISION`, `OMAP4_CTRL_MODULE_WKUP_IP_HWINFO`, `OMAP4_CTRL_MODULE_WKUP_IP_SYSCONFIG`, debug select test register offsets, and bit masks/shifts for revision, hardware info, idle mode, and wakeup mode.

## Control Flow
The file has no runtime control flow. Its macros are consumed by C code that maps or addresses OMAP4 wakeup control-module registers and composes read/modify/write masks.

## State and Persistence Behavior
It stores no state. The named registers represent persistent hardware state in always-on or wakeup domains, especially revision/idle/debug selection bits.

## Dependencies and Integration Points
It integrates with mach-omap2 control and low-power code that needs wakeup control-module register addresses. The header is guarded by `__ARCH_ARM_MACH_OMAP2_CTRL_MODULE_WKUP_44XX_H`.

## Risks
The file is autogenerated; manual edits can diverge from hardware database scripts. Wrong offsets or bit masks can affect always-on wakeup-domain programming and are difficult to detect in compile tests.

## Test Signals
Compile OMAP4 platform code that includes this header and boot on OMAP44xx hardware. Runtime validation is register-level: revision reads match expected silicon, idle-mode writes have effect, and wakeup/debug registers are not accessed at invalid offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ctrl_module_wkup_44xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/devices.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/devices.c

## Purpose
`devices.c` contains legacy OMAP2 platform-device setup that remains in this slice only for video-output registration. It registers an `omap_vout` platform device when OMAP2 VOUT support is enabled.

## Important APIs, Types, and Functions
The public function is `omap_init_vout()`. Internals include `omap_vout_resource[]`, `omap_vout_dma_mask`, and `omap_vout_device`. When `CONFIG_VIDEO_OMAP2_VOUT` is disabled, `omap_init_vout()` is a stub returning zero.

## Control Flow
If enabled, `omap_init_vout()` calls `platform_device_register(&omap_vout_device)`. The resource array length depends on `CONFIG_FB_OMAP2` and `CONFIG_FB_OMAP2_NUM_FBS`, matching legacy framebuffer/V4L2 display-device coexistence. The function is called by display initialization after DSS and framebuffer setup.

## State and Persistence Behavior
State is the registered platform device and its 32-bit DMA mask. No persistent data is written. Once registered, driver binding and lifetime are managed by the platform bus.

## Dependencies and Integration Points
It depends on platform-device core, DMA masks, OMAP DMA headers, `display.h`, `control.h`, and OMAP device/hwmod infrastructure. Its main integration point is `display.c` through `omap_init_vout()`.

## Risks
This is legacy platform-data plumbing. Resource-count conditionals can mismatch VOUT/framebuffer expectations. Incorrect DMA masks or registration ordering can break `omap_vout` probe or video overlay buffer allocation.

## Test Signals
Compile with and without `CONFIG_VIDEO_OMAP2_VOUT` and `CONFIG_FB_OMAP2`. On supported OMAP display systems, confirm `omap_vout` platform device appears, binds to the V4L2 output driver, and can allocate/display DMA-backed buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/devices.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/display.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/display.c

## Purpose
`display.c` wires OMAP2+ display subsystem devices into the platform and provides a custom DSS reset sequence. It handles legacy `omapdss`, framebuffer, VRFB, VOUT helper device registration, OMAP4 DSI pad muxing, OF DSS submodule population, and safe DISPC output shutdown before reset.

## Important APIs, Types, and Functions
The externally used API is `omap_dss_reset(struct omap_hwmod *oh)`. Important internals include `omap4_dsi_mux_pads()`, `omap_dsi_enable_pads()`, `omap_dsi_disable_pads()`, `omap_display_get_version()`, `omapdss_init_fbdev()`, `omapdss_find_dss_of_node()`, `omapdss_init_of()`, and `dispc_disable_outputs()`. It uses `struct omap_dss_board_info` callbacks and `struct omap_dss_dispc_dev_attr`.

## Control Flow
At `omap_device_initcall`, OF initialization finds an enabled DSS node, populates its child devices, then registers legacy fbdev helpers. OMAP4 DSI pad setup locates `omap4_padconf_global` syscon and updates lane-enable/PIPD masks. During DSS reset, optional clocks are enabled, active LCD/TV managers are detected, relevant framedone IRQs are cleared, managers are disabled, and the code waits up to `FRAMEDONE_IRQ_TIMEOUT` before clearing DSS control/SDI/PLL registers and checking reset-done status.

## State and Persistence Behavior
State includes the registered `omapdss` platform device, `omap4_dsi_mux_syscon`, OF-populated subdevices, and transient DISPC/DSS register programming. The reset path mutates display output enable bits and control registers but writes no persistent storage.

## Dependencies and Integration Points
It depends on OF platform population, syscon/regmap, platform data `linux/platform_data/omapdss.h`, OMAP hwmod accessors, clock APIs, SoC revision checks, `display.h`, `control.h`, and `prm.h`. It integrates with framebuffer, VRFB, VOUT, DSS child drivers, and hwmod reset hooks.

## Risks
Resetting DSS while outputs are active can hang or corrupt display state if framedone IRQ selection is wrong. OMAP4 DSI pad muxing depends on syscon availability and correct lane masks. Version detection by SoC revision affects downstream driver feature selection. Timeout paths continue with warnings and may leave displays partially disabled.

## Test Signals
Boot with enabled DSS DT nodes and verify child devices populate. Exercise framebuffer, VOUT, DSI lane enable/disable, and DSS reset while displays are active. Check for framedone timeout warnings, missing syscon errors, and correct `omapdss_version` selection on OMAP2/3/4/5/AM43xx/DRA7 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/display.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/display.h

## Purpose
`display.h` is the small OMAP2+ display integration header. It shares DISPC device-attribute data and legacy helper registration prototypes between display, framebuffer, and platform-device setup code.

## Important APIs, Types, and Functions
It defines `struct omap_dss_dispc_dev_attr` with `manager_count` and `has_framedonetv_irq`. It declares `omap_init_vrfb()`, `omap_init_fb()`, and `omap_init_vout()`.

## Control Flow
The header has no runtime control flow. It enables compile-time sharing of display helper APIs and the DISPC reset attribute shape used by `display.c`.

## State and Persistence Behavior
No state is stored here. The struct fields describe hardware capability state supplied by hwmod data at runtime.

## Dependencies and Integration Points
It includes `linux/kernel.h` for `bool`/integer types and is consumed by `display.c`, `fb.c`, and `devices.c`.

## Risks
Changing the struct layout breaks assumptions in hwmod `dev_attr` users. Removing prototypes without updating config stubs can break display initialization for legacy framebuffer/VOUT paths.

## Test Signals
Compile display-enabled and display-disabled OMAP builds. Runtime signals are successful `omapdss` initialization, VRFB/fb/VOUT helper registration, and `dispc_disable_outputs()` reading correct manager attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/dma.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/dma.c

## Purpose
`dma.c` supplies OMAP2+ system DMA platform data to the shared OMAP DMA engine driver. It describes register offsets, channel stride, capabilities, OMAP24xx slave mappings, and SoC-specific DMA errata flags.

## Important APIs, Types, and Functions
The main exported data object is `struct omap_system_dma_plat_info dma_plat_info`. Internals include `reg_map[]`, `configure_dma_errata()`, `omap24xx_sdma_dt_map[]`, `dma_attr`, and `omap2_system_dma_init()`.

## Control Flow
At `omap_arch_initcall`, `omap2_system_dma_init()` computes errata from SoC family, revision, and GP/secure type. It adds legacy OMAP24xx MUSB/TUSB DMA slave maps, enables `IS_RW_PRIORITY` on non-OMAP242x, and reserves high-security channels on secure OMAP34xx devices. The DMA engine driver later consumes `dma_plat_info`.

## State and Persistence Behavior
Mutable state is limited to boot-time initialization of `dma_plat_info.errata` and `dma_attr.dev_caps`. No persistent data is written. Runtime DMA channel state is managed by the DMA driver, not this file.

## Dependencies and Integration Points
It depends on `linux/omap-dma.h`, DMA engine types, SoC and revision helpers, and initcall ordering before DMA controller probe. It integrates with platform data for the OMAP SDMA driver and legacy consumers requiring slave maps.

## Risks
Errata bits are safety-critical. Missing one can cause FIFO stalls, hung channels, uncleared IRQs after ROM secure save/restore, or invalid priority programming. Over-broad errata can reduce performance or reserve channels unnecessarily. Slave map drift can break legacy MUSB DMA requests.

## Test Signals
Compile OMAP2/3/4/AM/DRA DMA-enabled builds. Runtime tests include DMA memcpy, cyclic audio, MMC, MUSB, parallel channel stress, channel abort/error paths, and suspend/resume on secure OMAP34xx. Confirm the DMA driver sees expected `dev_caps`, `lch_count`, register stride, and errata flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/fb.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/fb.c

## Purpose
`fb.c` registers legacy OMAP framebuffer and VRFB platform devices. It provides static physical resource definitions for OMAP2/3 VRFB register and remap windows and an `omapfb` platform device with DMA configuration.

## Important APIs, Types, and Functions
Public init helpers are `omap_init_vrfb()` and `omap_init_fb()`, with stubs when config options are disabled. Internal data includes `omap2_vrfb_resources[]`, `omap3_vrfb_resources[]`, `omap_fb_dma_mask`, `omapfb_config`, and `omap_fb_device`.

## Control Flow
`omap_init_vrfb()` selects OMAP24xx or OMAP34xx VRFB resources based on SoC detection and calls `platform_device_register_resndata()`. `omap_init_fb()` registers the static `omapfb` device. Both are called from `display.c` during fbdev display initialization.

## State and Persistence Behavior
State is platform-device registration and associated resource descriptors. No persistent storage is used. The framebuffer driver later owns display buffers and runtime state.

## Dependencies and Integration Points
It depends on platform-device, memblock/MM/DMA headers, `linux/omapfb.h`, SoC detection, and `display.h`. It integrates with legacy DSS/fbdev setup in `display.c` and VRFB/omapfb drivers.

## Risks
Hard-coded VRFB physical windows are SoC-specific and must match memory maps. Wrong resource selection can overlap real memory or make VRFB unusable. DMA mask changes affect framebuffer allocation capability.

## Test Signals
Build with `CONFIG_OMAP2_VRFB` and `CONFIG_FB_OMAP2`. On OMAP2/3 hardware, verify `omapvrfb` and `omapfb` devices register, resources appear correctly, framebuffer opens, rotation/VRFB paths work, and no resource conflict warnings occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/gpmc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/gpmc.h

## Purpose
`gpmc.h` is a compatibility include for the OMAP2 General-Purpose Memory Controller. It intentionally redirects users to the shared `linux/omap-gpmc.h` interface and notes that new code should not include this mach header.

## Important APIs, Types, and Functions
It declares no local APIs. Its only technical content is `#include <linux/omap-gpmc.h>`.

## Control Flow
There is no runtime control flow. It affects preprocessing by exposing the shared GPMC declarations through a legacy include path.

## State and Persistence Behavior
No state is stored or persisted.

## Dependencies and Integration Points
The dependency is `linux/omap-gpmc.h`. Integration is with old mach-omap2 code or board files that still include `arch/arm/mach-omap2/gpmc.h`.

## Risks
Keeping the wrapper can hide legacy dependencies that should migrate to the shared header. Removing it breaks any remaining includes. No hardware risk exists in the wrapper itself.

## Test Signals
Compile all OMAP GPMC users after include cleanup. `rg "mach-omap2/gpmc.h|#include \"gpmc.h\""` should identify remaining legacy dependencies before removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/gpmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/hdq1w.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/hdq1w.c

## Purpose
`hdq1w.c` implements the custom reset sequence for the OMAP HDQ/1-Wire hardware module. The sequence works around the requirement that the module's internal clock gate be enabled after soft reset for reset completion.

## Important APIs, Types, and Functions
The public function is `omap_hdq1w_reset(struct omap_hwmod *oh)`. It uses `HDQ_CTRL_STATUS_OFFSET`, `HDQ_CTRL_STATUS_CLOCKENABLE_SHIFT`, `omap_hwmod_softreset()`, `omap_hwmod_read()`, `omap_hwmod_write()`, `omap_test_timeout()`, and `SYSS_RESETDONE_MASK`.

## Control Flow
The reset function issues a hwmod soft reset, reads `HDQ_CTRL_STATUS`, sets the internal clock-enable bit, writes it back, then polls the module `SYSS` reset-done bit until `MAX_MODULE_SOFTRESET_WAIT`. It logs a warning on timeout and debug output on success, but always returns zero.

## State and Persistence Behavior
State is limited to HDQ module registers. The function mutates the internal clock-enable bit and soft-reset state. No persistent storage exists.

## Dependencies and Integration Points
It depends on OMAP hwmod reset infrastructure, `hdq1w.h`, PRM/common reset constants, and platform-device/hwmod binding data. It integrates with the HDQ/1-Wire master driver through the hwmod class reset hook.

## Risks
Returning zero on reset timeout can allow a driver to probe against a non-reset module. Incorrect register offset or clock bit prevents reset completion. Reset timing regressions may only appear on OMAP34xx-class hardware.

## Test Signals
Boot with an HDQ/1-Wire device, confirm reset debug output and no timeout warning, and verify the `omap_hdq` driver can communicate with attached battery/1-Wire devices after runtime reset and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/hdq1w.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/hdq1w.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/hdq1w.h

## Purpose
`hdq1w.h` shares OMAP HDQ/1-Wire reset constants and the reset helper prototype with hwmod integration code.

## Important APIs, Types, and Functions
It defines `HDQ_CTRL_STATUS_OFFSET`, `HDQ_CTRL_STATUS_CLOCKENABLE_SHIFT`, and declares `omap_hdq1w_reset(struct omap_hwmod *oh)`.

## Control Flow
No runtime control flow exists. Consumers use the constants during the custom reset flow in `hdq1w.c`.

## State and Persistence Behavior
No state is stored here. The constants describe module register state controlled elsewhere.

## Dependencies and Integration Points
It includes `omap_hwmod.h` and integrates with `hdq1w.c` and OMAP hwmod reset hooks. The comment indicates a future driver cleanup could move these macros to the actual HDQ driver.

## Risks
Changing offsets or bit positions breaks the reset sequence. Moving definitions requires synchronized changes in both mach code and any HDQ driver users.

## Test Signals
Compile HDQ-enabled OMAP builds and verify `omap_hdq1w_reset()` users still see the prototype and constants. Runtime validation is successful HDQ reset and driver probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/hdq1w.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/i2c.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/i2c.c

## Purpose
`i2c.c` provides the OMAP I2C module custom reset sequence used by hwmod integration. Older OMAP2/3 I2C modules require disable, soft reset, re-enable, and reset-done polling.

## Important APIs, Types, and Functions
The public function is `omap_i2c_reset(struct omap_hwmod *oh)`. Important constants are `I2C_EN`, `OMAP2_I2C_CON_OFFSET`, `OMAP4_I2C_CON_OFFSET`, and `MAX_OMAP_I2C_HWMOD_NAME_LEN` (unused in this file).

## Control Flow
The reset helper selects the I2C CON register offset based on SoC generation, clears `I2C_EN`, calls `omap_hwmod_softreset()`, sets `I2C_EN`, and polls the hwmod reset-done bit up to `MAX_MODULE_SOFTRESET_WAIT`. It logs success or timeout and returns zero.

## State and Persistence Behavior
State is the I2C controller enable bit and soft-reset state. It does not persist data and does not own transfer state; the I2C driver owns runtime bus state after reset.

## Dependencies and Integration Points
It depends on SoC detection, OMAP hwmod accessors, PRM/common reset constants, and `i2c.h`. It integrates through hwmod class reset hooks used before I2C controller probe or during module reset.

## Risks
Wrong CON offset can hit unrelated registers on newer SoCs. Returning zero despite reset timeout can mask broken hardware state. Resetting while transfers are active would disrupt the bus, so callers must use it at safe lifecycle points.

## Test Signals
Boot with OMAP I2C controllers, confirm no reset timeout warnings, scan/probe I2C devices, and run suspend/resume plus repeated controller runtime reset where supported. Validate both OMAP2/3 and OMAP4-style offsets in compile/runtime coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/i2c.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/i2c.h

## Purpose
`i2c.h` declares the OMAP I2C hwmod reset helper for board/platform integration code.

## Important APIs, Types, and Functions
It forward-declares `struct omap_hwmod` and declares `int omap_i2c_reset(struct omap_hwmod *oh)`.

## Control Flow
There is no runtime control flow. Including code can assign or call the reset helper defined in `i2c.c`.

## State and Persistence Behavior
No state is stored.

## Dependencies and Integration Points
It integrates `i2c.c` with OMAP hwmod data and any board/hwmod setup code that needs the reset callback.

## Risks
Prototype drift would break reset callback assignment or hide build failures. The header itself is otherwise low risk.

## Test Signals
Compile OMAP I2C/hwmod users and verify `omap_i2c_reset()` remains available for configured SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/id.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/id.c

## Purpose
`id.c` detects OMAP/AM/DRA silicon revision, device type, feature bits, die ID, and optional Linux soc-bus attributes. It is foundational early-boot code used by later platform, PM, erratum, and driver decisions.

## Important APIs, Types, and Functions
Public APIs include `omap_rev()`, `omap_type()`, `omap2xxx_check_revision()`, `omap3xxx_check_revision()`, `omap4xxx_check_revision()`, `omap5xxx_check_revision()`, `dra7xxx_check_revision()`, feature checkers `omap3xxx_check_features()`, `omap4xxx_check_features()`, `ti81xx_check_features()`, `am33xx_check_features()`, `omap2_set_globals_tap()`, and `omap_soc_device_init()` when `CONFIG_SOC_BUS` is enabled. Important state includes `omap_revision`, `soc_name`, `soc_rev`, `omap_features`, `tap_base`, and `tap_prod_id`.

## Control Flow
Early board setup calls `omap2_set_globals_tap()` with the initial class and TAP base. Later revision checkers read TAP IDCODE/die ID/control-module status registers, decode hawkeye/revision/package fields, set `omap_revision`, and format `soc_name`/`soc_rev`. Feature checkers read control status or fuse fields and set `omap_features`. A device initcall feeds die ID into the randomness pool. The optional soc-bus path registers machine/family/revision and a `type` attribute.

## State and Persistence Behavior
The file owns global boot-time identification state. `omap_type()` caches the device type after first detection. The die ID is not persisted by the file, but it is mixed into kernel randomness. soc-bus registration exposes immutable boot-time state through sysfs.

## Dependencies and Integration Points
It depends on CPUID reads, TAP MMIO, control-module accessors, SoC macros from `soc.h`, feature masks from `control.h`, random subsystem, and optional `linux/sys_soc.h`. Nearly every mach-omap2 subsystem depends indirectly on correct revision/type/feature detection.

## Risks
Unknown silicon falls back to latest known revisions, which can enable unsupported errata paths or low-power states. `omap2xxx_check_revision()` formats from `omap_rev()` even though it does not assign from the matched table in this body, so behavior must be checked in context. Wrong feature bits can misclassify SGX/IVA/ISP/NEON and break driver availability or PM workarounds.

## Test Signals
Boot each supported SoC family and check early `pr_info` revision strings, `/sys/devices/soc0` attributes, `omap_type()`, and feature-dependent drivers. Regression tests should cover unknown hawkeye warnings, AM35xx feature fixups, DRA7 package variants, secure/GP type decoding, and randomness feed initcall ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/id.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/id.h

## Purpose
`id.h` defines the shared die-ID data structure used by OMAP2 CPU identification code.

## Important APIs, Types, and Functions
It defines `struct omap_die_id` with four 32-bit ID words: `id_0`, `id_1`, `id_2`, and `id_3`. There are no function declarations.

## Control Flow
There is no runtime control flow. `id.c` fills this struct from TAP die-ID registers.

## State and Persistence Behavior
The struct carries hardware identity values while in memory. It does not persist data by itself; consumers may use values for randomness, package detection, or logging.

## Dependencies and Integration Points
It integrates with `id.c` and any code needing a typed die-ID container. It relies on standard fixed-width integer typedefs being available through included kernel headers in consumers.

## Risks
Changing field order or width breaks die-ID interpretation and randomness/package detection. The header is otherwise stable and minimal.

## Test Signals
Compile `id.c`; boot logs and die-ID debug output should show four correctly read words on OMAP families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/io.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/io.c

## Purpose
`io.c` defines static IO mappings and early/late initialization flows for OMAP2/3/4/5, TI81xx, AM33xx/AM43xx, and DRA7. It maps interconnect windows, initializes clocks, hwmods, control base, SDRC/GPMC memory support, PRM/CM, powerdomains, and late PM/display-related platform state.

## Important APIs, Types, and Functions
Public mapping functions include `omap242x_map_io()`, `omap243x_map_io()`, `omap3_map_io()`, `ti81xx_map_io()`, `am33xx_map_io()`, `omap4_map_io()`, `omap5_map_io()`, and `dra7xx_map_io()`. Public init functions include `omap2420_init_early()`, `omap2430_init_early()`, `omap3430_init_early()`, `omap3630_init_early()`, `am35xx_init_early()`, `ti814x_init_early()`, `ti816x_init_early()`, `am33xx_init_early()`, `am43xx_init_early()`, `omap4430_init_early()`, `omap5_init_early()`, `dra7xx_init_early()`, corresponding late init helpers, and `omap_clk_init()`.

## Control Flow
Map functions call `iotable_init()` with SoC-specific `map_desc` arrays. Early init functions set TAP globals, initialize SoC revision/features, clock/PRM/CM/powerdomain infrastructure, control-module base, hwmods, and SoC-specific PM prerequisites. Late init paths typically perform GPMC/SDRC or control/device PM finalization. `omap_hwmod_init_postsetup()` optionally forces hwmods into a configured postsetup state.

## State and Persistence Behavior
The file establishes permanent static virtual mappings for early MMIO windows and boot-time global subsystem state. It does not write persistent storage, but it configures hardware modules and global framework state that remain active for the kernel lifetime.

## Dependencies and Integration Points
It depends on ARM `map_desc`/`iotable_init`, SoC address headers, clock init, PRM/CM, powerdomain/clockdomain, hwmod, control, SDRC, GPMC, PM, id, and device init helpers. It is integrated from machine descriptors and is upstream of almost every OMAP platform subsystem.

## Risks
Mapping size/base errors can cause early boot aborts or MMIO aliasing. Init ordering is fragile: SoC detection, clocks, PRM/CM, control base, hwmods, and PM must be initialized in the expected sequence. Multi-OMAP builds are especially sensitive to running the wrong SoC path.

## Test Signals
Boot each machine descriptor path with earlycon and dynamic debug enabled. Validate `/proc/iomem`, no early ioremap faults, correct SoC revision output, clock and hwmod registration, working interrupts/timers, and successful late init. Compile coverage should include all configured SoC families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/iomap.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/iomap.h

## Purpose
`iomap.h` defines OMAP2+ static physical-to-virtual IO mapping offsets, base/size constants, and address translation macros for L3/L4/EMU/wakeup/peripheral interconnect windows across OMAP2, OMAP3, AM33xx, OMAP4, OMAP5, and DRA7.

## Important APIs, Types, and Functions
Key macros include `OMAP2_L3_IO_ADDRESS()`, `OMAP2_L4_IO_ADDRESS()`, `OMAP4_L3_IO_ADDRESS()`, `AM33XX_L4_WK_IO_ADDRESS()`, `OMAP4_L3_PER_IO_ADDRESS()`, and many `*_PHYS`, `*_VIRT`, `*_SIZE` definitions for static `map_desc` arrays.

## Control Flow
There is no runtime control flow. `io.c` consumes the constants to build the early static MMIO map, while register headers use address macros for direct MMIO address formation.

## State and Persistence Behavior
No mutable state exists. The constants define kernel virtual address layout for early and static mappings, which persists for the life of the kernel.

## Dependencies and Integration Points
It depends on SoC base-address headers such as `omap24xx.h`, `omap34xx.h`, `omap44xx.h`, and `omap54xx.h` included by consumers. It integrates with low-level MMIO access, `control.h`, and `io.c`.

## Risks
Wrong offsets or sizes cause overlapping virtual mappings, inaccessible registers, or early boot data aborts. Comments document deliberate overmapping and address holes; cleanup must preserve section-aligned requirements and early users.

## Test Signals
Compile all SoC variants and boot with early MMIO users enabled. Check early access to PRCM/control/GIC/SDRC/GPMC, absence of data aborts, and sane `/proc/vmallocinfo` or debug mapping output where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/iomap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l3_2xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l3_2xxx.h

## Purpose
`l3_2xxx.h` defines OMAP2 L3 firewall connection IDs needed by legacy platform display/security setup.

## Important APIs, Types, and Functions
It defines `OMAP2_L3_CORE_FW_CONNID_DSS` for the display subsystem. There are no functions or types.

## Control Flow
No runtime control flow exists. The macro is used by code that configures or documents L3 firewall initiator/connection permissions.

## State and Persistence Behavior
No local state exists. The macro names a hardware firewall ID whose programmed state lives in L3 firewall registers.

## Dependencies and Integration Points
It integrates with OMAP2 L3/firewall and DSS-related platform code. The include guard is `__ARCH_ARM_PLAT_OMAP_INCLUDE_PLAT_L3_2XXX_H`.

## Risks
Wrong IDs can grant or deny the wrong L3 initiator, causing display access faults or security misconfiguration. Because the file is tiny, stale use sites are the primary maintenance risk.

## Test Signals
Compile OMAP2 DSS/firewall users and boot display-enabled OMAP24xx systems. Runtime signal is DSS access without L3 firewall violations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l3_2xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l3_3xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l3_3xxx.h

## Purpose
`l3_3xxx.h` defines OMAP3 L3 firewall initiator IDs for display subsystem access.

## Important APIs, Types, and Functions
It defines `OMAP3_L3_CORE_FW_INIT_ID_DSS`. There are no functions or structs.

## Control Flow
No runtime control flow exists. The macro feeds firewall setup or documentation code.

## State and Persistence Behavior
No local state exists. The referenced state is hardware firewall configuration.

## Dependencies and Integration Points
It integrates with OMAP3 DSS and L3 firewall definitions under legacy mach/plat include paths.

## Risks
Incorrect initiator ID can break DSS transactions or security policy. Changes require TRM/firewall table validation.

## Test Signals
Compile OMAP3 DSS/firewall users and boot display workloads while watching for L3 interconnect errors or access faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l3_3xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l4_2xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l4_2xxx.h

## Purpose
`l4_2xxx.h` names OMAP2420 L4 firewall regions for DSS submodules. It supports legacy display/firewall configuration.

## Important APIs, Types, and Functions
Macros include `OMAP2420_L4_CORE_FW_DSS_CORE_REGION`, `OMAP2420_L4_CORE_FW_DSS_DISPC_REGION`, `OMAP2420_L4_CORE_FW_DSS_RFBI_REGION`, `OMAP2420_L4_CORE_FW_DSS_VENC_REGION`, and `OMAP2420_L4_CORE_FW_DSS_TA_REGION`.

## Control Flow
There is no runtime control flow. Constants are consumed by any code configuring L4 firewall regions.

## State and Persistence Behavior
No state is stored in the header. Firewall programming state lives in hardware.

## Dependencies and Integration Points
It integrates with OMAP2 DSS and L4 firewall setup. Its values are tied to OMAP2420 region numbering.

## Risks
Wrong region numbers can deny DSS register access or open unrelated regions. Edits should be validated against the OMAP2420 TRM.

## Test Signals
Compile OMAP2420 display/firewall users and run DSS register access tests without L4 firewall faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l4_2xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l4_3xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l4_3xxx.h

## Purpose
`l4_3xxx.h` defines OMAP3 L4 firewall region and protection-group IDs for I2C and DSS modules.

## Important APIs, Types, and Functions
Important macros include `OMAP3_L4_CORE_FW_I2C1_REGION`, `OMAP3_L4_CORE_FW_I2C*_TA_REGION`, `OMAP3_L4_CORE_FW_DSS_PROT_GROUP`, `OMAP3_L4_CORE_FW_DSS_DSI_REGION`, `OMAP3ES1_L4_CORE_FW_DSS_CORE_REGION`, and DSS DISPC/RFBI/VENC/TA region IDs.

## Control Flow
No runtime control flow exists. These constants feed L4 firewall configuration or documentation.

## State and Persistence Behavior
No local state exists. Hardware firewall registers persist the actual access rules.

## Dependencies and Integration Points
It integrates with OMAP3 I2C and display firewall code. The ES1-specific DSS core region constant captures a silicon revision difference.

## Risks
Confusing ES1 and later DSS region IDs can break register access on one revision. I2C firewall mistakes can prevent bus probe or mask security faults.

## Test Signals
Compile OMAP3 I2C/DSS firewall users and boot on ES1 and later where available. Exercise I2C transfers and DSS register access while monitoring interconnect/firewall errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l4_3xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/mcbsp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/mcbsp.c

## Purpose
`mcbsp.c` provides an OMAP3 clock helper for McBSP modules that need interface-clock force-on behavior while using sidetone or register access paths.

## Important APIs, Types, and Functions
The important function is `omap3_mcbsp_force_ick_on(struct clk *clk, bool force_on)`. The file includes McBSP/platform-clock integration headers and manipulates control-module or clock state through OMAP clock helpers.

## Control Flow
The helper is called by clock or McBSP integration code with a clock pointer and a boolean force flag. It toggles the relevant OMAP3 McBSP interface clock handling so the module remains accessible when required, then returns a status code.

## State and Persistence Behavior
State is clockdomain/clock hardware state, not persistent storage. The forced clock setting affects runtime power behavior while active and should be released when no longer needed.

## Dependencies and Integration Points
It depends on OMAP clock infrastructure, McBSP device integration, SoC/control definitions, and platform audio drivers. It integrates with McBSP hwmod/clock data rather than directly registering a device.

## Risks
Keeping ICK forced on wastes power and can block low-power states. Failing to force it on can break McBSP register access or sidetone operation. Because the behavior is OMAP3-specific, broadening it to other SoCs requires hardware validation.

## Test Signals
Build OMAP3 McBSP audio support, run playback/capture including sidetone paths, and check clock/powerdomain idle counters before and after use. Suspend/resume should not leave McBSP clocks permanently forced on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/mcbsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/mmc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/mmc.h

## Purpose
`mmc.h` provides legacy OMAP MMC base/count definitions and a conditional prototype for the OMAP2420 MSDI reset helper.

## Important APIs, Types, and Functions
It defines `OMAP24XX_NR_MMC`, `OMAP2420_MMC_SIZE`, `OMAP2_MMC1_BASE`, and `OMAP4_MMC_REG_OFFSET`. It forward-declares `struct omap_hwmod`. If `CONFIG_SOC_OMAP2420` is enabled it declares `omap_msdi_reset()`, otherwise it provides an inline stub returning zero.

## Control Flow
No direct runtime control flow exists beyond the config-selected inline stub. Callers can invoke `omap_msdi_reset()` without wrapping their own OMAP2420 config conditionals.

## State and Persistence Behavior
No state is stored. The constants describe hardware address and register layout.

## Dependencies and Integration Points
It integrates with OMAP MMC/MSDI hwmod data and reset code in `msdi.c`. `OMAP1_MMC_SIZE` must be defined by included context in users.

## Risks
The stub can hide accidental use on unsupported SoCs. Wrong base or offset values break MMC register access. OMAP2420 MSDI reset behavior is special and must remain config-gated.

## Test Signals
Compile OMAP2420 and non-OMAP2420 configs. On OMAP2420, verify MMC reset and card detection; on other SoCs, confirm callers link against the stub without changing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/mmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/msdi.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/msdi.c

## Purpose
`msdi.c` implements a custom reset sequence for the OMAP2420 MSDI/MMC controller. The sequence powers the controller and sets a target clock divider before waiting for reset completion.

## Important APIs, Types, and Functions
The public function is `omap_msdi_reset(struct omap_hwmod *oh)`. Important constants include `MSDI_CON_OFFSET`, `MSDI_CON_POW_MASK`, `MSDI_CON_CLKD_MASK`, `MSDI_CON_CLKD_SHIFT`, and `MSDI_TARGET_RESET_CLKD`.

## Control Flow
The reset helper soft-resets the hwmod, reads `MSDI_CON`, powers the module, clears and writes the reset clock divider, then polls `SYSS_RESETDONE_MASK` using `omap_test_timeout()`. It warns on timeout and returns zero.

## State and Persistence Behavior
State is the MSDI controller's power and clock-divider bits plus reset state. No persistent data is written.

## Dependencies and Integration Points
It depends on OMAP hwmod accessors, reset constants from `common.h`/`prm.h`, and the `mmc.h` declaration. It integrates with OMAP2420 MMC hwmod reset callbacks.

## Risks
The function returns success even on timeout. Incorrect divider/power programming may prevent reset or leave the controller in an unexpected clock state. This code should remain limited to OMAP2420.

## Test Signals
Build `CONFIG_SOC_OMAP2420`, boot with MMC enabled, verify no reset timeout warning, and exercise card initialization, I/O, and suspend/resume. Confirm non-2420 builds use the stub from `mmc.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/msdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-headsmp.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-headsmp.S

## Purpose
`omap-headsmp.S` provides secondary CPU startup entry points for OMAP4 and OMAP5 SMP boot and hotplug resume. These routines run before normal C environment setup and release secondaries from ROM or hardware holding loops.

## Important APIs, Types, and Functions
Assembly entry points are `omap_secondary_startup`, `omap5_secondary_startup`, `omap5_secondary_hyp_startup`, `omap4_secondary_startup`, and `omap4460_secondary_startup`. Important constants are `AUX_CORE_BOOT0_PA`, `API_HYP_ENTRY`, and `OMAP44XX_GIC_DIST_BASE`.

## Control Flow
`omap_secondary_startup` branches to the ARM common `secondary_startup` when SMP is enabled, otherwise loops in WFI. OMAP5 startup polls AuxCoreBoot0 until the shifted release value matches the core ID, optionally enters HYP mode through an SMC ROM call, then jumps to common startup. OMAP4 startup reads AuxCoreBoot0 through SMC, waits for release, and jumps to common startup. OMAP4460 additionally reenables the GIC distributor as part of the ROM/GIC erratum workaround.

## State and Persistence Behavior
State is CPU register state and hardware release registers. No memory persistence is created. The routines depend on stack setup by the primary CPU and on AuxCoreBoot registers retaining release values.

## Dependencies and Integration Points
It depends on ARM assembly/linkage macros, `secondary_startup`, secure monitor calls, AuxCoreBoot registers, and OMAP SMP C code in `omap-smp.c` and `omap-mpuss-lowpower.c`.

## Risks
Any register clobbering, wrong release-bit shift, or wrong startup physical address can hang CPU1 before console output. HYP-mode startup depends on boot CPU mode and ROM SMC behavior. OMAP4460 GIC erratum handling must match the C-side distributor disable flow.

## Test Signals
Boot SMP OMAP4/OMAP5, online/offline CPU1 repeatedly, kexec, and suspend/resume from CPU-off states. Confirm secondary CPUs reach `smp_secondary_init`, HYP-mode boot works when primary is in HYP, and OMAP4460 does not lose interrupts after CPU1 wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-headsmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-hotplug.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-hotplug.c

## Purpose
`omap-hotplug.c` implements OMAP4 CPU hotplug platform hooks for taking secondary CPUs down and verifying they reached low-power/off state.

## Important APIs, Types, and Functions
Public functions are `omap4_cpu_die(unsigned int cpu)` and `omap4_cpu_kill(unsigned int cpu)`. They call into `omap4_hotplug_cpu()` from MPUSS low-power code and inspect CPU powerdomain state.

## Control Flow
`omap4_cpu_die()` flushes the CPU from coherency as needed and enters the requested CPU low-power path, typically CPU off. `omap4_cpu_kill()` waits/polls for the target CPU powerdomain to report off, returning success only when the hardware state confirms the CPU is down.

## State and Persistence Behavior
State is per-CPU powerdomain state and hotplug lifecycle state managed by the kernel CPU hotplug core. No persistent data is written.

## Dependencies and Integration Points
It depends on SMP/hotplug core, powerdomain helpers, OMAP4 MPUSS low-power functions, and OMAP PM state definitions. It integrates through `omap4_smp_ops.cpu_die` and `.cpu_kill`.

## Risks
If `cpu_die` does not actually place the CPU in a terminal low-power state, CPU hotplug can hang. If `cpu_kill` checks the wrong powerdomain or timeout behavior, the kernel may believe a CPU is dead when it is not, or fail valid hotplug operations.

## Test Signals
Run repeated `echo 0/1 > /sys/devices/system/cpu/cpu1/online` loops under interrupt load. Verify powerdomain previous/current states, no RCU stalls, no GIC wake issues, and successful return to SMP scheduling after re-online.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-hotplug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-iommu.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-iommu.c

## Purpose
`omap-iommu.c` provides platform integration for OMAP IOMMU devices and their powerdomain/clockdomain relationships. It links IOMMU runtime state with the emulation clockdomain and relevant powerdomains.

## Important APIs, Types, and Functions
Important internals include `struct pwrdm_link`, `emu_clkdm`, and helper functions such as `_get_pwrdm(struct device *dev)` plus device link/setup callbacks in the file. It uses device tree or platform device data to locate associated powerdomains.

## Control Flow
The code resolves an IOMMU device's powerdomain from OMAP hwmod or device context, then coordinates clockdomain/powerdomain behavior required for IOMMU access. Setup is invoked during platform/IOMMU initialization and prepares runtime PM relationships before the IOMMU driver manages translations.

## State and Persistence Behavior
State is in clockdomain/powerdomain references and runtime PM-managed hardware state. No filesystem persistence exists. IOMMU page tables and mappings are owned by the IOMMU driver, not this integration layer.

## Dependencies and Integration Points
It depends on OMAP powerdomain and clockdomain frameworks, platform devices, OMAP hwmod/device data, and the OMAP IOMMU driver. It integrates with multimedia/DSP/IVA users that require IOMMU translation.

## Risks
Wrong powerdomain lookup or missing EMU clockdomain handling can leave the IOMMU inaccessible, block idle, or cause faults during device runtime suspend. Because IOMMUs sit between masters and memory, power sequencing errors can surface as unrelated device DMA faults.

## Test Signals
Boot with OMAP IOMMU users enabled, bind remoteproc/DSP or multimedia clients, exercise map/unmap and runtime PM, and check for IOMMU faults during suspend/resume. Inspect clockdomain/powerdomain state transitions while clients are active and idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-mpuss-lowpower.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-mpuss-lowpower.c

## Purpose
`omap-mpuss-lowpower.c` implements OMAP4/OMAP5 MPUSS CPU low-power entry, hotplug powerdown, SAR RAM setup, CPU wakeup-address programming, SCU/L2 context preparation, and early kexec-safe CPU1 startup-address setup.

## Important APIs, Types, and Functions
Public APIs include `omap4_enter_lowpower()`, `omap4_hotplug_cpu()`, `omap4_mpuss_init()`, `omap4_get_cpu1_ns_pa_addr()`, and `omap4_mpuss_early_init()`. Important structs are `struct omap4_cpu_pm_info` and `struct cpu_pm_ops`. Internal helpers include `set_cpu_wakeup_addr()`, `scu_pwrst_prepare()`, `mpuss_clear_prev_logic_pwrst()`, `cpu_clear_prev_logic_pwrst()`, `l2x0_pwrst_prepare()`, `save_l2x0_context()`, and `enable_mercury_retention_mode()`.

## Control Flow
Early init maps SAR RAM and writes CPU1 wakeup physical address for kexec safety. Main MPUSS init initializes per-CPU SAR offsets, looks up CPU and MPU powerdomains, clears previous-state registers, saves L2 context, selects OMAP4-specific suspend/resume/hotplug ops, and handles OMAP5 retention setup. Low-power entry validates the requested state, computes context save level, programs CPU powerdomain next/logic state, enters cpuidle RCU state if requested, writes wakeup address and SCU/L2 SAR data, then calls `cpu_suspend()` or WFI. Hotplug programs a terminal CPU state and does not return when CPU off succeeds.

## State and Persistence Behavior
State includes `sar_base`, per-CPU SAR address pointers, `old_cpu1_ns_pa_addr`, CPU/MPUSS powerdomain next/previous states, L2 saved registers, and SAR scratch values used by ROM/restore code. No filesystem persistence exists, but SAR RAM preserves resume-critical values across low-power transitions.

## Dependencies and Integration Points
It depends on CPU suspend, SCU, L2X0, virtualization boot mode, OMAP PRCM/PRM registers, SAR layout, secure/non-secure startup symbols, powerdomain helpers, and SoC revision/erratum checks. It integrates directly with `cpuidle44xx.c`, `omap-hotplug.c`, `omap-smp.c`, `omap-headsmp.S`, and `omap4-common.c`.

## Risks
This is suspend/hotplug critical. Wrong SAR offsets, wakeup addresses, powerdomain state programming, or context-save levels can hang resume, corrupt cache/GIC state, or wake CPU1 into the wrong kernel after kexec. Erratum gates for OMAP4430 ES1 and CPU OSWR must remain conservative.

## Test Signals
Stress cpuidle, CPU hotplug, suspend/resume, and kexec on OMAP4/OMAP5. Verify CPU1 wakeup address preservation, SAR contents, L2 context restore, no GIC/timer loss, and powerdomain previous states matching requested idle levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-mpuss-lowpower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-secure.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-secure.c

## Purpose
`omap-secure.c` implements secure monitor/ROM/OP-TEE call plumbing for OMAP low-power, cache-controller, SMP, RX-51 PPA, secure RAM save, and secure PM notifier paths.

## Important APIs, Types, and Functions
Public APIs include `omap_secure_dispatcher()`, `omap_smccc_smc()`, `omap_smc1()`, `omap_secure_ram_reserve_memblock()`, `omap3_save_secure_ram()`, `rx51_secure_update_aux_cr()`, `rx51_secure_rng_call()`, and `omap_secure_init()`. Important state is `omap_secure_memblock_base` and `optee_available`.

## Control Flow
`omap_secure_init()` detects an available `/firmware/optee` node. `omap_smc1()` dispatches either ARM SMCCC SiP SMC calls through OP-TEE-compatible calling convention or legacy OMAP ROM `_omap_smc1`. `omap_secure_dispatcher()` builds a per-CPU physical parameter buffer, flushes caches, and calls `omap_smc2()`. RX-51 dispatcher disables IRQ/FIQ, flushes caches, and calls `omap_smc3()`. A secure PM initcall registers a CPU cluster PM exit notifier on non-GP OMAP44xx to refresh ROM return address after OSWR/MPU off.

## State and Persistence Behavior
Reserved secure RAM storage is allocated from memblock. Static parameter buffers are temporary per-call state. Secure-world firmware owns persistent effects such as saved secure RAM, AUX control register updates, cache-controller secure registers, and ROM return addresses.

## Dependencies and Integration Points
It depends on ARM SMCCC, memblock, cache maintenance, OF firmware nodes, CPU PM notifiers, `omap-smc.S`, `omap-secure.h`, and SoC/device-type detection. It integrates with wakeupgen secure context save, SMP ACTLR/ACR programming, L2C310 secure writes, RX-51 RNG/ACR calls, and OMAP3 secure RAM save.

## Risks
Physical parameter buffers must be cache-clean before SMC. Calling the wrong ABI when OP-TEE is present or absent can fail silently or trap. IRQ/FIQ masking in RX-51 paths is sensitive. Secure calls are device-type and firmware-version dependent; failures can break low-power resume or security hardening.

## Test Signals
Boot GP and HS/EMU devices with and without OP-TEE nodes. Verify secure SMC return warnings, L2 secure register writes, OMAP4 GIC save on HS devices, RX-51 RNG/ACR paths where applicable, and suspend/resume after cluster PM exit. Confirm memblock reservation succeeds early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-secure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-secure.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-secure.h

## Purpose
`omap-secure.h` defines secure monitor API indices, flags, return codes, secure RAM sizes, RX-51 PPA IDs, and prototypes for OMAP secure-call infrastructure.

## Important APIs, Types, and Functions
Important constants include `API_HAL_RET_VALUE_*`, `FLAG_START_CRITICAL`, `OMAP_SECURE_RAM_STORAGE`, `OMAP3_SAVE_SECURE_RAM_SZ`, OMAP4 HAL save indices, OMAP4/5 monitor indices, PPA service IDs, and RX-51 PPA IDs. It declares `omap_secure_dispatcher()`, `omap_smccc_smc()`, `omap_smc1()`, `omap_smc2()`, `omap_smc3()`, `omap_secure_ram_reserve_memblock()`, `save_secure_ram_context()`, `omap3_save_secure_ram()`, RX-51 helpers, `optee_available`, `omap_secure_init()`, and `set_cntfreq()`.

## Control Flow
The header has no runtime flow. It conditionally exposes C prototypes outside assembler and provides an inline no-op `set_cntfreq()` when realtime counter support is absent.

## State and Persistence Behavior
It declares `optee_available` but stores no state itself. Constants describe secure-world persistent operations and reserved RAM sizes used elsewhere.

## Dependencies and Integration Points
It depends on `linux/types.h` and, outside assembler, on kernel type definitions. It integrates `omap-secure.c`, `omap-smc.S`, SMP, wakeupgen, L2 cache, and low-power code.

## Risks
Incorrect service IDs or flags can call the wrong secure firmware function. The misspelled `API_HAL_RET_VALUE_SERVICE_UNKNWON` is ABI spelling in code and should not be casually renamed without updating users. Size constants affect reserved memory and secure RAM save compatibility.

## Test Signals
Compile C and assembly users. Runtime tests are secure dispatcher success, OP-TEE detection, L2 secure writes, GIC secure save, RX-51 secure calls, and absence of unresolved symbols for `set_cntfreq()` across configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-secure.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-smc.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-smc.S

## Purpose
`omap-smc.S` provides low-level ARM secure monitor call wrappers for OMAP ROM/HAL/PPA services and AuxCoreBoot register access.

## Important APIs, Types, and Functions
Assembly entry points are `_omap_smc1`, `omap_smc2`, `omap_smc3`, `omap_modify_auxcoreboot0`, `omap_auxcoreboot_addr`, and `omap_read_auxcoreboot0`.

## Control Flow
Each wrapper saves caller registers on the stack, arranges service IDs and arguments in the ROM-expected registers, issues memory barriers, executes `smc #0` or `smc #1`, then restores registers and returns. `omap_smc2()` is for low-power HAL/PPA parameter-list calls; `omap_smc3()` supports RX-51 PPA calls with explicit service/process IDs. AuxCoreBoot helpers use fixed ROM API IDs.

## State and Persistence Behavior
No local persistent state exists. Calls can mutate secure-world state, AuxCoreBoot registers, L2/ACTLR settings, or firmware context depending on service ID.

## Dependencies and Integration Points
It depends on ARMv7 secure extension support, Linux linkage macros, and the calling conventions expected by `omap-secure.c` and `omap-smp.c`. It is used by secure dispatch, SMP secondary release, and secure register programming.

## Risks
Register preservation is critical; clobbering ABI registers can corrupt callers. Wrong SMC immediate or service register placement can hang in secure firmware. These routines require secure extension support and correct CPU mode.

## Test Signals
Boot paths that invoke each wrapper: secure L2 writes, SMP CPU1 release on secure devices, RX-51 secure APIs, and low-power secure context save. Watch for SMC failure warnings, CPU1 startup hangs, and register corruption after calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-smc.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-smp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-smp.c

## Purpose
`omap-smp.c` implements OMAP4/OMAP5/DRA7 SMP bring-up, secondary CPU initialization, CPU1 release, SCU setup, kexec/reset safety checks, and erratum/security hardening for secondary cores.

## Important APIs, Types, and Functions
The exported SMP operations object is `omap4_smp_ops`. Public helper `omap4_get_scu_base()` returns the mapped SCU base. Important internals include `struct omap_smp_config`, SoC-specific config records, `omap5_erratum_workaround_801819()`, `omap5_secondary_harden_predictor()`, `omap4_secondary_init()`, `omap4_boot_secondary()`, `omap4_smp_init_cpus()`, `omap4_smp_cpu1_startup_valid()`, `omap4_smp_maybe_reset_cpu1()`, and `omap4_smp_prepare_cpus()`.

## Control Flow
Early CPU init uses CPUID to discover A9/A15 core count and sets possible CPUs. Prepare selects SoC-specific reset/startup configuration, maps CPU1 reset control, enables SCU, optionally resets CPU1 if it appears parked in the current kernel address range, and writes the secondary startup physical address through secure AuxCoreBoot APIs or wakeupgen MMIO. Booting CPU1 writes release bits, handles OMAP4 SGI wake limitations by forcing CPU1 clockdomain wake after first boot, applies GIC erratum handling, and sends a wakeup IPI. Secondary init applies secure SMP ACTLR setup and OMAP5/DRA7 ACR hardening.

## State and Persistence Behavior
State includes static `cfg`, cached CPU1 clockdomain/powerdomain pointers, and a `booted` flag. Hardware state includes AuxCoreBoot registers, SCU enable, CPU1 reset control, powerdomain next state, and ACR/ACTLR secure settings. No filesystem persistence exists.

## Dependencies and Integration Points
It depends on ARM SMP core, SCU, GIC helpers, secure APIs, wakeupgen base, clockdomain/powerdomain, virtualization boot mode, CPUID, OMAP SoC detection, and assembly startup symbols. It integrates with `omap-headsmp.S`, `omap-mpuss-lowpower.c`, `omap-hotplug.c`, and `omap4-common.c`.

## Risks
CPU1 boot is timing and firmware sensitive. Wrong AuxCoreBoot values, stale kexec startup addresses, missing reset, or incorrect secure API selection can hang secondary bring-up. Erratum/hardening SMCs affect CPU security and performance. GIC distributor workaround must be coordinated with assembly reenable path.

## Test Signals
Boot SMP on OMAP443x/446x/OMAP5/DRA7, verify both CPUs online, run CPU hotplug loops, kexec reboot, suspend/resume, and branch-predictor hardening checks. Confirm no "CPU1 not parked" surprises except expected cases and no lost local-timer warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-wakeupgen.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-wakeupgen.c

## Purpose
`omap-wakeupgen.c` implements the OMAP WakeupGen interrupt-controller extension layered above the ARM GIC. It manages wakeup-enable bits for shared peripheral interrupts, interrupt domain allocation, hotplug masking, CPU cluster PM context save/restore, and secure save paths.

## Important APIs, Types, and Functions
Public functions are `omap_get_wakeupgen_base()` and `omap_secure_apis_support()`. Major internals include `struct omap_wakeupgen_ops`, `wakeupgen_mask()`, `wakeupgen_unmask()`, `wakeupgen_irq_set_type()`, hotplug mask helpers, OMAP4/OMAP5/AM43xx context save/restore functions, `irq_notifier()`, `wakeupgen_chip`, `wakeupgen_domain_translate()`, `wakeupgen_domain_alloc()`, and `wakeupgen_init()`.

## Control Flow
`IRQCHIP_DECLARE` calls `wakeupgen_init()` from DT. It resolves the parent GIC domain, maps WakeupGen registers, selects bank/IRQ counts and context ops by SoC, creates a hierarchical IRQ domain, masks all wakeupgen banks, initializes IRQ target CPU bookkeeping, enables OMAP5/DRA7 ES2 PM mode through SMC, registers hotplug and CPU PM notifiers, and records SAR base. Mask/unmask updates WakeupGen enable bits under a raw spinlock before delegating to the parent GIC chip. CPU cluster PM save writes WakeupGen/AuxCoreBoot/PTMSYNC state to SAR or uses secure dispatcher on HS devices.

## State and Persistence Behavior
State includes `wakeupgen_base`, `sar_base`, `irq_target_cpu[]`, bank/IRQ counts, secure API flag, per-CPU hotplug mask snapshots, and optional CPU PM context arrays. SAR RAM preserves wakeupgen state across MPUSS low-power states; AM43xx restores from in-RAM `wakeupgen_context`.

## Dependencies and Integration Points
It depends on irqchip/irqdomain hierarchy, OF address mapping, CPU hotplug, CPU PM notifiers, OMAP secure APIs, SAR layout, SoC/erratum detection, and GIC parent domains. It integrates with SMP, MPUSS low-power, `omap-smp.c`, and DT compatible `ti,omap4-wugen-mpu`.

## Risks
WakeupGen and GIC masks must remain synchronized or interrupts can be lost. IRQ type inversion for `sys_nirq` can surprise board DTS authors. Wrong bank counts or SAR offsets break wake from deep idle. Secure-vs-GP save path mistakes can fail HS resume. Affinity is tracked simplistically and notes missing full support.

## Test Signals
Boot with WakeupGen DT node and parent GIC, allocate SPIs through the hierarchical domain, test GPIO/peripheral wake from idle, CPU hotplug, MPUSS OSWR, and suspend/resume on GP and HS devices. Watch for lost interrupts, polarity warnings, and SAR backup status behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-wakeupgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-wakeupgen.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-wakeupgen.h

## Purpose
`omap-wakeupgen.h` declares WakeupGen register offsets and small public helpers for OMAP4/5 wakeup interrupt integration.

## Important APIs, Types, and Functions
It defines `OMAP_WKUPGEN_BASE`, enable bank offsets `OMAP_WKG_ENB_*`, `OMAP_AUX_CORE_BOOT_0`, `OMAP_AUX_CORE_BOOT_1`, `OMAP_AMBA_IF_MODE`, PTM sync/timestamp offsets, and declares `omap_get_wakeupgen_base()` and `omap_secure_apis_support()`.

## Control Flow
No runtime control flow exists. C and assembly-side users consume constants for MMIO offsets and public helper prototypes.

## State and Persistence Behavior
No local state exists. The constants point to WakeupGen hardware state and AuxCoreBoot release/startup registers.

## Dependencies and Integration Points
It integrates `omap-wakeupgen.c`, `omap-smp.c`, and MPUSS low-power code. It is part of the DT irqchip and SMP release path contract.

## Risks
Offset mistakes can break CPU1 boot or interrupt wake. Constants are shared across OMAP4 and OMAP5 but not all registers are equally valid on every SoC.

## Test Signals
Compile WakeupGen, SMP, and low-power users. Runtime validation includes secondary CPU boot, interrupt wake from idle, and SMC programming of `OMAP_AMBA_IF_MODE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-wakeupgen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap2-restart.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap2-restart.c

## Purpose
`omap2-restart.c` implements OMAP2xxx software restart by temporarily reparenting/resetting PRCM clocks and waiting for reset to occur.

## Important APIs, Types, and Functions
The public restart function is `omap2xxx_restart(enum reboot_mode mode, const char *cmd)`. Internal state includes `reset_virt_prcm_set_ck` and `reset_sys_ck`. The init helper `omap2xxx_common_look_up_clks_for_reset()` runs as an initcall to cache clock handles.

## Control Flow
The init helper looks up clocks needed for reset. The restart function programs the reset clock path, invokes PRCM reset behavior, then loops waiting for hardware reset. The `cmd` parameter is not persisted.

## State and Persistence Behavior
State is cached clock pointers and PRCM reset hardware state. No filesystem persistence exists; successful operation terminates the running kernel via SoC reset.

## Dependencies and Integration Points
It depends on clock framework, PRM/CM reset helpers, reboot core, and OMAP2xxx clock names. It is registered as the machine restart callback for OMAP2xxx platforms.

## Risks
Missing clock lookup or wrong clock parent prevents reset. Since restart should not return, any failure leaves the system running in a partially modified clock state. Lack of scratchpad `cmd` persistence means reboot mode strings are ignored.

## Test Signals
On OMAP2xxx hardware, run `reboot`, watchdog-adjacent reset tests, and verify the system resets promptly. Check boot logs for clock lookup failures and confirm reset path does not return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap2-restart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap24xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap24xx.h

## Purpose
`omap24xx.h` defines base physical addresses for OMAP2420/2430 interconnects and major peripherals. It supplies the address constants consumed by static IO mapping, control, PRCM, SDRC, GPMC, DSP, mailbox, camera, and security code.

## Important APIs, Types, and Functions
Macros include `L4_24XX_BASE`, `L4_WK_243X_BASE`, `L3_24XX_BASE`, interrupt-controller bases, `OMAP242X_CTRL_BASE`, PRCM/CM/PRM bases, SDRC/SMS/GPMC bases, DSP subsystem bases, mailbox/camera bases, and security accelerator bases. No functions or types are defined.

## Control Flow
No runtime control flow exists. The constants are used by mapping and register-address macros during early boot and driver setup.

## State and Persistence Behavior
No mutable state exists. The constants define the hardware address map.

## Dependencies and Integration Points
It integrates with `iomap.h`, `control.h`, `io.c`, and peripheral platform code for OMAP24xx.

## Risks
Wrong base addresses cause early MMIO failures or devices probing at invalid locations. Some constants are needed for OMAP1 compile compatibility per the file comment, so cleanup must consider cross-family includes.

## Test Signals
Compile and boot OMAP2420/2430 configurations. Verify early PRCM/control access, interrupt controller, SDRC/GPMC, and any enabled DSP/mailbox/camera/security device probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap24xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap3-restart.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap3-restart.c

## Purpose
`omap3-restart.c` implements OMAP3 software restart through the PRM reset path and optional scratchpad boot-mode communication.

## Important APIs, Types, and Functions
The public function is `omap3xxx_restart(enum reboot_mode mode, const char *cmd)`.

## Control Flow
On restart, the function may interpret or pass restart mode information through OMAP3 control scratchpad helpers, then calls `omap_prm_reset_system()` to trigger SoC reset. Like other restart hooks, it is expected not to return.

## State and Persistence Behavior
State is limited to scratchpad boot-mode data and PRM reset hardware state. No filesystem persistence exists.

## Dependencies and Integration Points
It depends on reboot core, PRM reset functions, and OMAP3 control scratchpad helper declarations. It integrates as the machine restart callback for OMAP3-class SoCs.

## Risks
If scratchpad values are wrong, bootloader or ROM-visible reboot mode can be miscommunicated. If PRM reset fails, the system remains running after a restart request.

## Test Signals
Run reboot on OMAP3 boards with normal and bootloader-specific reboot commands if supported. Confirm reset occurs and any boot-mode scratchpad behavior is interpreted by downstream firmware as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap3-restart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap34xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap34xx.h

## Purpose
`omap34xx.h` defines base physical addresses for OMAP34xx/AM35xx-era interconnects and core peripherals.

## Important APIs, Types, and Functions
Key constants include `L4_34XX_BASE`, `L4_WK_34XX_BASE`, `L4_PER_34XX_BASE`, `L4_EMU_34XX_BASE`, `L3_34XX_BASE`, `L4_WK_AM33XX_BASE`, 32K sync, CM/PRM, SMS/SDRC/GPMC, SCM/control, interrupt controller, ISP, USB, SmartReflex, mailbox, and security accelerator bases.

## Control Flow
No runtime control flow exists. The constants are consumed by IO mapping and register-address code.

## State and Persistence Behavior
No state is stored; the header describes fixed hardware address state.

## Dependencies and Integration Points
It integrates with `iomap.h`, `control.h`, `io.c`, and many OMAP3 platform subsystems.

## Risks
Address changes are high risk and can break early boot, PRCM/control access, USB, ISP, SDRC/GPMC, or interrupt controller setup. AM33xx wakeup base sharing also makes this header relevant outside pure OMAP34xx paths.

## Test Signals
Compile and boot OMAP3430/3630/AM35xx/AM33xx-related configs. Confirm early MMIO, PRM/CM, control, interrupt, USB, ISP, and mailbox users access valid addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap34xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-common.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-common.c

## Purpose
`omap4-common.c` provides common OMAP4/5 platform support for DRAM barriers, SRAM low-power code copy, GIC distributor erratum helpers, L2 cache secure register writes, SAR RAM mapping, and GIC/WakeupGen OF initialization.

## Important APIs, Types, and Functions
Public functions include `omap_interconnect_sync()`, `omap_barrier_reserve_memblock()`, `omap_barriers_init()`, `gic_dist_disable()`, `gic_dist_enable()`, `gic_dist_disabled()`, `gic_timer_retrigger()`, `omap4_get_l2cache_base()`, `omap4_l2c310_write_sec()`, `omap_l2_cache_init()`, `omap4_get_sar_ram_base()`, `omap4_sar_ram_init()`, and `omap_gic_of_init()`.

## Control Flow
Memblock reservation sets aside a DRAM barrier page and initialization maps it, flushes it, and stores a pointer used by the custom memory barrier routine. SRAM init copies OMAP4 low-power code into SRAM. GIC erratum helpers directly disable/enable distributor and retrigger a lost local timer if needed. L2 cache secure writes map public L2 registers to secure monitor service IDs. SAR init maps OMAP4/OMAP5 SAR RAM early. GIC OF init locates WakeupGen, maps GIC/TWD bases for OMAP446x erratum, and calls `irqchip_init()`.

## State and Persistence Behavior
State includes mapped barrier memory, `dram_sync`, GIC distributor/TWD bases, L2 cache base, and SAR RAM base. SAR RAM persists low-power context across MPUSS transitions; other mappings persist for kernel lifetime.

## Dependencies and Integration Points
It depends on memblock, ioremap, cache flush APIs, GIC/TWD register definitions, secure APIs, L2X0, OF irqchip, SAR layout/base headers, SRAM helpers, and SoC detection. It integrates with cpuidle/SMP, MPUSS low-power, WakeupGen, and L2 cache drivers.

## Risks
Barrier reservation/mapping errors can break interconnect synchronization. GIC distributor erratum handling can lose interrupts if timer retrigger logic is wrong. Secure L2 write mapping must match ROM API support. Missing WakeupGen DT node is explicitly warned as system-misbehaving.

## Test Signals
Boot OMAP4/5 with OF irqchips, verify WakeupGen/GIC init, run SMP and idle stress, exercise OMAP446x timer erratum path, initialize L2 cache, and enter/exit MPUSS low-power states. Check for missing DT warnings, lost localtimer warnings, and SAR base availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-restart.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-restart.c

## Purpose
`omap4-restart.c` implements the common OMAP4/OMAP5 restart hook using PRM system reset.

## Important APIs, Types, and Functions
The public function is `omap44xx_restart(enum reboot_mode mode, const char *cmd)`.

## Control Flow
The restart hook ignores `mode` and `cmd` except for a comment noting that `cmd` could be saved to scratchpad later. It calls `omap_prm_reset_system()` and expects hardware reset.

## State and Persistence Behavior
No local state is stored. The only state transition is PRM reset hardware state; reboot command persistence is not implemented.

## Dependencies and Integration Points
It depends on reboot type definitions and `prm.h`. It integrates as the machine restart callback for OMAP4/5-like systems.

## Risks
If PRM reset fails, restart returns unexpectedly. Not preserving `cmd` means bootloader-specific reboot modes are unavailable through this path.

## Test Signals
Run `reboot` on OMAP4/OMAP5/DRA7 systems using this hook and confirm immediate SoC reset. Test reboot command variants if platform firmware expects scratchpad data and verify they are not accidentally relied upon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-restart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-sar-layout.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-sar-layout.h

## Purpose
`omap4-sar-layout.h` defines the Save-And-Restore RAM layout used by OMAP4/OMAP5 low-power code, WakeupGen context save, L2/SCU context, CPU wakeup physical addresses, and secure RAM metadata.

## Important APIs, Types, and Functions
Important constants include SAR bank offsets, `SCU_OFFSET*`, `OMAP_TYPE_OFFSET`, `L2X0_*` offsets, CPU wakeup NS PA offsets for OMAP4 and OMAP5, secure RAM metadata offsets, WakeupGen save offsets for OMAP4 and OMAP5, AuxCoreBoot offsets, PTM sync offsets, and `SAR_BACKUP_STATUS_WAKEUPGEN`.

## Control Flow
There is no runtime control flow. Low-power C and assembly code write/read SAR addresses based on these offsets before and after MPUSS context loss.

## State and Persistence Behavior
The header defines persistent-in-low-power SAR locations. SAR RAM contents survive the relevant retention/off transitions and are consumed by ROM or restore code.

## Dependencies and Integration Points
It integrates with `omap-mpuss-lowpower.c`, `omap-wakeupgen.c`, `omap4-common.c`, and secure/ROM restore paths.

## Risks
Offset mistakes directly corrupt low-power restore data and can hang resume. OMAP4 and OMAP5 layouts differ, so sharing constants incorrectly is high risk.

## Test Signals
Suspend/resume and cpuidle OSWR/CSWR tests on OMAP4 and OMAP5 should restore CPU, GIC, WakeupGen, SCU, and L2 state. Debug SAR dumps can verify values at documented offsets before idle entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-sar-layout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap44xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap44xx.h

## Purpose
`omap44xx.h` defines OMAP4 interconnect and peripheral base addresses for static mapping, SMP, GIC, L2, WakeupGen, SAR, USB, mailbox, and MMU integration.

## Important APIs, Types, and Functions
Key constants include `L4_44XX_BASE`, `L4_WK_44XX_BASE`, `L4_PER_44XX_BASE`, `L3_44XX_BASE`, EMIF/DMM bases, PRCM/CM/PRM bases, GPMC, SCM/control bases, GIC distributor/CPU bases, local timer base, L2 cache base, WakeupGen base, MCPDM, SAR RAM, mailbox, USB, and MMU bases.

## Control Flow
No runtime control flow exists. Constants feed IO mapping, SMP, interrupt, cache, and peripheral setup code.

## State and Persistence Behavior
No mutable state exists. Constants describe the fixed OMAP4 hardware address map.

## Dependencies and Integration Points
It integrates with `iomap.h`, `omap-headsmp.S`, `omap4-common.c`, `omap-smp.c`, `omap-mpuss-lowpower.c`, and OMAP4 peripheral drivers.

## Risks
Wrong base addresses can break early boot, interrupts, SMP, cache setup, or peripheral probes. Address definitions are shared between C and assembly, so type-safe checks are limited.

## Test Signals
Compile and boot OMAP443x/446x/4470 configurations. Validate GIC/TWD, L2 cache, WakeupGen, SAR, PRCM, USB, mailbox, and SMP secondary boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap44xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap54xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap54xx.h

## Purpose
`omap54xx.h` defines OMAP5 and DRA7 base addresses for interconnects, PRCM/control, SAR RAM, and DRA7-specific L3/L4/PRCM/TAP regions.

## Important APIs, Types, and Functions
OMAP5 constants include `L4_54XX_BASE`, `L4_WK_54XX_BASE`, `L4_PER_54XX_BASE`, `L3_54XX_BASE`, `OMAP54XX_32KSYNCT_BASE`, CM/PRM/PRCM MPU bases, SCM/control bases, and `OMAP54XX_SAR_RAM_BASE`. DRA7 constants include L3 main, L4 PER/CFG/WKUP bases, `DRA7XX_CM_CORE_AON_BASE`, `DRA7XX_CTRL_BASE`, and `DRA7XX_TAP_BASE`.

## Control Flow
No runtime control flow exists. The constants are consumed by IO mapping and early platform setup.

## State and Persistence Behavior
No state is stored; this is a fixed hardware address map.

## Dependencies and Integration Points
It integrates with `iomap.h`, `io.c`, OMAP5/DRA7 PRCM/control setup, SAR low-power code, and revision detection through DRA7 TAP base.

## Risks
The closing comment has a typo in the guard name, but the actual guard macro is consistent. Wrong DRA7 mapping bases can break early boot because DRA7 has multiple L4 peripheral windows and address holes.

## Test Signals
Compile and boot OMAP543x and DRA7xx configs. Validate PRCM/control/TAP access, SAR mapping, GIC/WakeupGen, and peripheral probes under all DRA7 L4 windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap54xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_device.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_device.c

## Purpose
`omap_device.c` bridges Linux platform devices to OMAP hwmod power/clock/reset metadata. It builds `struct omap_device` wrappers from DT `ti,hwmods`, creates clkdev aliases, attaches PM domains, handles runtime/system PM, exposes reset helpers, and idles unbound devices late in boot.

## Important APIs, Types, and Functions
Public APIs are `omap_device_enable()`, `omap_device_idle()`, `omap_device_assert_hardreset()`, and `omap_device_deassert_hardreset()`. Important internals include `omap_device_build_from_dt()`, `_omap_device_notifier_call()`, `_omap_device_enable_hwmods()`, `_omap_device_idle_hwmods()`, `omap_device_alloc()`, `omap_device_delete()`, `_od_runtime_suspend()`, `_od_runtime_resume()`, `_od_suspend_noirq()`, `_od_resume_noirq()`, `omap_device_pm_domain`, `omap_device_fail_pm_domain`, and late idle initcalls.

## Control Flow
A postcore initcall registers a platform-bus notifier. On device add, DT nodes with `ti,hwmods` are converted into `omap_device` wrappers unless the node is handled by `ti-sysc` or is special SDMA. The builder looks up hwmods, allocates wrapper state, fixes resource names, creates clock aliases, and attaches a PM domain. Runtime resume enables all hwmods before generic resume; runtime suspend runs generic suspend then idles hwmods. Noirq suspend idles still-active bound devices and marks them suspended for resume. On driver unbind or late init, enabled devices without drivers are idled unless marked `HWMOD_INIT_NO_IDLE`.

## State and Persistence Behavior
State is stored in `pdev->archdata.od`, hwmod back-pointers, `_state`, `_driver_status`, and `OMAP_DEVICE_SUSPENDED` flags. It mutates hwmod clock/reset/power state but writes no persistent data.

## Dependencies and Integration Points
It depends on platform bus notifiers, PM domains/runtime PM, OF `ti,hwmods`, clock/clkdev APIs, OMAP hwmod, `omap_device.h`, and SoC/sysc integration. Drivers interact indirectly through runtime PM and direct hardreset helper calls.

## Risks
Notifier ordering and PM state transitions are fragile. Missing `ti,hwmods` attaches a fail PM domain that makes runtime PM return `-ENODEV`. Incorrect skip logic can conflict with `ti-sysc`. State validation returns `-EINVAL` on double enable/idle, which can expose driver runtime PM misuse. Clock alias creation has mixed legacy and OF paths.

## Test Signals
Boot DT OMAP systems and inspect platform devices for attached `archdata.od`. Exercise runtime PM get/put on hwmod-backed drivers, driver unbind/rebind, noirq suspend/resume, hardreset helpers, and late-idle warnings. Verify SDMA and ti-sysc-managed nodes are not incorrectly wrapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_device.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_device.h

## Purpose
`omap_device.h` declares the OMAP device wrapper that connects platform devices to hwmod metadata and exposes the small driver-facing enable/idle/reset interface.

## Important APIs, Types, and Functions
It defines device states `OMAP_DEVICE_STATE_UNKNOWN`, `ENABLED`, `IDLE`, and `SHUTDOWN`, flag `OMAP_DEVICE_SUSPENDED`, and `struct omap_device` with platform device, hwmod list, driver status, state, and flags. It declares `omap_device_enable()`, `omap_device_idle()`, hardreset assert/deassert helpers, and inline `to_omap_device()`.

## Control Flow
The header has no runtime control flow. The inline helper returns `pdev->archdata.od` when the platform device pointer is non-null.

## State and Persistence Behavior
The struct fields are runtime state owned by `omap_device.c`. No persistent data is defined.

## Dependencies and Integration Points
It depends on platform-device and OMAP hwmod definitions. It is consumed by OMAP platform drivers, reset helpers, and PM integration code.

## Risks
Changing state values, struct layout assumptions, or `to_omap_device()` semantics affects all hwmod-backed platform devices. The comment notes this should ideally be a proper bus, so legacy platform-data coupling is a maintenance risk.

## Test Signals
Compile all OMAP hwmod users. Runtime validation is successful `to_omap_device()` lookup, runtime PM enable/idle, hardreset calls, and no invalid-state warnings for correctly written drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_device.h -->
