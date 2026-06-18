<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/timex.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/timex.h

**Purpose:** Defines Alpha timer frequency and cycle-counter access.

**Important APIs/types/functions:** `CLOCK_TICK_RATE`, `cycles_t`, and `get_cycles()` using `rpcc`.

**Control flow:** Timekeeping and scheduler code call `get_cycles` to read the low 32 bits of the processor cycle counter; platform timer code uses the 32.768 kHz tick-rate constant.

**State and persistence behavior:** No local state; reads CPU cycle counter.

**Dependencies and integration points:** Depends on Alpha `rpcc` instruction and generic timekeeping expectations.

**Risks:** Only low 32 bits are continuously useful, so wraparound is frequent. Code must treat `cycles_t` accordingly.

**Test signals:** Clocksource/scheduler timing tests, wraparound handling, and boot calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/timex.h -->
