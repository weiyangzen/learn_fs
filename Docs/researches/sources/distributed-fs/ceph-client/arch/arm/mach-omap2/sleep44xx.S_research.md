# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep44xx.S

## Purpose
Implements OMAP44xx SMP/PM low-level suspend finisher, CPU resume entry, and common WFI helper for MPUSS low-power states.

## APIs, Flow, And State
Exports `omap4_finish_suspend`, `omap4_cpu_resume`, and `omap_do_wfi` when SMP/PM conditions apply, with `omap_do_wfi` always present. `omap4_finish_suspend(cpu_state)` handles cache flush/invalidate, secure L1 clean on HS devices, disables data cache, moves CPU out of coherency through SCU power mode or secure monitor, clears SMP bit when allowed, optionally cleans/invalidates L2X0 when the SAR-saved L2 state requires it, then executes WFI. If WFI returns without dormant/off transition, it re-enables cache/coherency and normal SCU state. `omap4_cpu_resume` is ROM-entered from dormant/off, enables NS SMP access on HS CPU1 when needed, restores/enables L2X0 from SAR RAM through secure monitor calls, then branches to `cpu_resume`. `omap_do_wfi` drains interconnect when configured, executes barriers, WFI, and post-WFI NOPs.

## Dependencies And Integration
Depends on OMAP secure monitor APIs, SAR RAM layout, SCU, PL310/L2X0 registers, generic ARM `cpu_resume`, and optional interconnect barrier support. Integrated with OMAP4 CPU idle/suspend and ROM wakeup programming.

## Risks And Test Signals
The code runs with caches/coherency disabled and cannot use ordinary locking. GP vs HS device paths differ, and secure monitor API availability is required for HS/L2 paths. Test signals are OMAP4 MPUSS CSWR/OSWR/OFF transitions, CPU1 resume, L2 cache restoration, no deadlocks in non-coherent mode, and correct fallback when WFI returns.
