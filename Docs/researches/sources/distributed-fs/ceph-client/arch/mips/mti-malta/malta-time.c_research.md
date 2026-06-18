<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-time.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-time.c

### Purpose
`malta-time.c` initializes Malta timekeeping, RTC access, CPU/GIC frequency estimation, timer IRQ routing, and performance/FDC interrupt routing.

### Important APIs, Types, And Functions
`plat_time_init()` initializes RTC, estimates frequencies, prints CPU/GIC clocks, starts PIT and timer probing. `estimate_frequencies()` measures CP0 Count and GIC counter against CMOS RTC update edges. `get_c0_compare_int()`, `get_c0_perfcount_int()`, and `get_c0_fdc_int()` choose interrupt lines. `read_persistent_clock64()` reads MC146818 time.

### Control Flow
RTC is set to 32 KHz and run mode. Frequency estimation disables interrupts, synchronizes with RTC update-in-progress edges, samples CP0/GIC counters across elapsed seconds, and restores interrupts. Timer/perf IRQs are routed through VEIC handlers, GIC helpers, or CPU IRQs. If GIC timer is present, the DT `clock-frequency` property is updated before timer probing.

### State, Persistence, And Dependencies
Persistent state includes `mips_hpt_frequency`, `gic_frequency`, selected timer/perf IRQ globals, and optional OF property storage. Dependencies include CMOS RTC, GIC, VEIC, CP0 Count, PIT, timer framework, and Malta interrupt constants.

### Integration Points
Generic MIPS clocksource/clockevent setup calls these platform hooks. Perf event and FDC code use the exported interrupt selectors.

### Risks
RTC polling loops assume functional CMOS and can stall on broken emulation. Frequency rounding and 20KC/25KF count-rate handling must be correct. Some cores advertise FDC routing that Malta bitstreams do not wire, so the function explicitly rejects them.

### Test Signals
Boot with and without GIC, VEIC, PIT, and GIC clocksource; compare measured CPU/GIC frequencies to expected values; read persistent clock; test perf interrupts and FDC IRQ selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-time.c -->
