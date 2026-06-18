<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/time.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/time.c

Purpose: Initializes Loongson2EF timers and reads persistent CMOS time.

Important APIs/types/functions: `plat_time_init()` sets `mips_hpt_frequency` and calls `setup_mfgpt0_timer()`. `read_persistent_clock64()` returns MC146818 CMOS seconds.

Control flow: The R4K counter is assumed to run at half `cpu_clock_freq`; CS5536 MFGPT0 is set up as an additional timer source.

State and persistence: Sets global timer frequency used by the MIPS time subsystem.

Dependencies and integration: Consumes `cpu_clock_freq` from env initialization and CS5536 MFGPT support.

Risks: Wrong CPU clock halves cause timer drift. CMOS reads provide only second precision.

Test signals: Kernel jiffies and clocksource output should match real time; persistent clock should report CMOS time at boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/time.c -->
