# sources/distributed-fs/ceph-client/drivers/clocksource/arm_arch_timer_mmio.c

Purpose: supports memory-mapped ARM generic timer frames as clocksource and clockevent devices.

Important APIs/types/functions: `struct arch_timer`, `arch_timer_mmio_write()`, `arch_timer_mmio_read()`, `arch_counter_mmio_get_cnt()`, `find_best_frame()`, `arch_timer_mmio_frame_register()`, `of_populate_gt_block()`, and built-in platform drivers for OF and ACPI GTDT MMIO timers.

Control flow: probe obtains a generic timer block from DT or platform data, maps the control frame, chooses a virtual-capable frame when possible or physical frame otherwise, maps the selected frame, determines the rate, requests IRQ, registers a clockevent, then registers a 56-bit MMIO clocksource.

State and persistence: one `struct arch_timer` per platform device stores frame metadata, MMIO base, access mode, rate, clockevent, and clocksource.

Dependencies and integration points: integrates with `clocksource/arm_arch_timer.h`, OF child frame descriptions, ACPI GTDT platform data, MMIO accessors, and the sysreg arch timer rate as fallback.

Risks: CVAL writes are non-atomic and require disabling the timer first. Frame access is probed by writing `CNTACR`, so firmware permissions must allow it. No failure is allowed after IRQ request/setup. Rate fallback can mask incomplete firmware data.

Test signals: DT frame parsing, virtual-frame preference, physical fallback, IRQ delivery, clocksource monotonicity, and ACPI GTDT MMIO probing.
