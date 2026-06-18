<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ranchu.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-ranchu.c

**Purpose:** Provides support for the virtual MIPS Ranchu board used by Android emulator/QEMU.

**Important APIs/types/functions:** `read_rtc_time()` reads Goldfish RTC low/high registers. `ranchu_measure_hpt_freq()` calibrates CP0 count frequency over one RTC second and rounds to 10 kHz. `MIPS_MACHINE(ranchu)` registers compatible `mti,ranchu` and measure hook.

**Control flow:** Time init calls the machine frequency hook, which finds and maps the RTC DT node, reads CP0 count before/after one nanosecond-resolution second, rounds, unmaps, and returns the frequency.

**State, dependencies, integration:** Depends on OF node lookup, MMIO mapping, CP0 count, and MIPS generic time init.

**Risks and test signals:** Panics if RTC node or mapping is missing; calibration busy-waits for one second. Test DT compatibility, RTC latch semantics, repeatability of rounded frequency, and panic paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ranchu.c -->
