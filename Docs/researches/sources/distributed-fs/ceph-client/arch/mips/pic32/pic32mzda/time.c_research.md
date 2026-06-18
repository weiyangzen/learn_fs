## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/time.c

### Purpose
This file initializes PIC32MZDA timer support and maps the MIPS C0 compare interrupt through device tree infrastructure.

### Important APIs, Types, And Functions
`pic32_infra_match[]` identifies `"microchip,pic32mzda-infra"`. `pic32_xlate_core_timer_irq()` finds that node, maps its first IRQ, and falls back to mapping hardware interrupt 0. `get_c0_compare_int()` returns the translated IRQ. `plat_time_init()` initializes clocks, reports CPU clock, sets `mips_hpt_frequency`, and calls `timer_probe()`.

### Control Flow
Timer init reads PBCLK7 via early clock code, calls `of_clk_init(NULL)`, logs rate, sets high-precision timer frequency to half the rate, and probes timers. Compare IRQ lookup happens when generic MIPS timer code asks for it.

### State, Persistence, And Dependencies
Persistent state is `mips_hpt_frequency` and IRQ mappings created from DT. Dependencies include OF IRQ/clock APIs, PIC32 early clock helpers, and MIPS timer infrastructure.

### Integration Points
This connects PIC32 DT interrupt descriptions and common MIPS clockevent/clocksource setup.

### Risks
Fallback to `irq_create_mapping(NULL, 0)` may be invalid if no default domain exists. The logged "CPU Clock" uses PBCLK7, so naming may be misleading. Bad PB divider values affect scheduler timing.

### Test Signals
Check timer interrupt fires, `mips_hpt_frequency` matches hardware, DT infra IRQ is used, and fallback mapping behaves on minimal DTs.
