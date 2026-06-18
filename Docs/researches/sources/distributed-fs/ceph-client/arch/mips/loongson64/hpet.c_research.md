<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/hpet.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/hpet.c

Purpose: Provides a Loongson-3 RS780/SBX00 HPET clock event and clocksource setup path.

Important APIs/types/functions: MMIO helpers for SMBus and HPET registers, `setup_hpet_timer()`, `hpet_irq_handler()`, clock-event state callbacks, `hpet_next_event()`, and `init_hpet_clocksource()`.

Control flow: `hpet_setup()` writes HPET base into SMBus PCI config space, enables HPET MMIO decoding and IRQ. Timer setup initializes per-CPU timer0 clockevent, registers it, and requests `HPET_T0_IRQ`. Clocksource init registers a 32-bit continuous HPET counter.

State and persistence: Uses global `hpet_lock` and per-CPU `hpet_clockevent_device`; programs chipset and HPET registers.

Dependencies and integration: Enabled only by `CONFIG_RS780_HPET`; depends on `loongson_sysconf.ht_control_base`, MIPS clockevent/clocksource core, and HPET register constants.

Risks: Kconfig marks this broken/dangerous. It writes host bridge/SMBus registers before normal PCI setup. `hpet_next_event()` races against a near counter and returns `-ETIME` if too close.

Test signals: HPET IRQ should fire and call the clockevent handler; clocksource should register with rating 300; suspend/resume should re-run setup and restart the counter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/hpet.c -->
