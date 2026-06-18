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
