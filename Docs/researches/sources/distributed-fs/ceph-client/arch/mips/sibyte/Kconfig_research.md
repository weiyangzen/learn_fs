# sources/distributed-fs/ceph-client/arch/mips/sibyte/Kconfig

Purpose: configuration matrix for Broadcom SiByte SB1250/BCM112x/BCM1x80 SoCs and related diagnostics.

Important APIs and control flow: SoC configs select clockevent/clocksource drivers, PCI, CPU IRQs, CFE firmware, SMP support, and common SiByte SoC support. A stepping choice selects SB1 pass/feature options such as prefetch. Additional options enable fatal cache-error policy, CFE console, bus-watcher statistics/trace, and ZBbus profiling.

State, persistence, and integration: no runtime state, but options select object directories and architecture capabilities. Dependencies include matching CPU/SoC stepping to actual hardware and avoiding incompatible tracing/profiling combinations. Risks include wrong pass option causing CPU feature/errata mismatch, bus trace interfering with profiling/JTAG as documented, and CFE console excluding other console strategies. Test signals are Kconfig dependencies, selected objects, and runtime SoC pass logs.
