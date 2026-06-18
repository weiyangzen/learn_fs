<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/time.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/time.c

Purpose: Initializes Loongson64 CPU counter frequency and optional HPET timer.

Important APIs/types/functions: `plat_time_init()` handles DTB clock lookup and timer frequency setup.

Control flow: DTB firmware mode initializes OF clocks, gets CPU0 clock, stores `cpu_clock_freq`, and releases the clock. Then the MIPS high-precision timer frequency is set to half CPU clock. Optional HPET setup runs when configured.

State and persistence: Sets global `mips_hpt_frequency` and possibly `cpu_clock_freq`.

Dependencies and integration: Depends on `loongson_sysconf.fw_interface`, OF clock bindings, and optional `setup_hpet_timer()`.

Risks: Missing CPU node or clock leaves the old CPU frequency in place. Assumes counter runs at CPU/2.

Test signals: DTB boot logs should not show CPU clock errors; scheduler clock should match real time; HPET should register when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/time.c -->
