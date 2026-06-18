<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/wrperfmon.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/wrperfmon.h

**Purpose:** Defines Alpha performance-monitor PAL command codes, counter masks, shifts, and event selections for EV5/EV6/EV67 processors.

**Important APIs/types/functions:** `PERFMON_CMD_*`, EV5/EV6/EV67 counter bit masks, count shifts/masks, mode/event masks, and event encodings such as cycles, instructions, branches, ITB/DTB misses, and traps.

**Control flow:** Perf or low-level monitor code composes PAL `wrperfmon` command values from these constants and interprets packed counter fields.

**State and persistence behavior:** No local state; hardware performance counters hold runtime state.

**Dependencies and integration points:** Depends on PAL `wrperfmon` support, CPU family detection, and perf-event implementation.

**Risks:** Event encodings differ by CPU family; using EV6 constants on EV5 or EV67 can program the wrong counter. Command value overlap is intentional and context-dependent.

**Test signals:** Perf event smoke tests on EV5/EV6/EV67 hardware or emulator support, counter overflow/read/write tests, and event sanity comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/wrperfmon.h -->
