<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/timex.h

Source read size: 22 lines, 403 bytes.

Purpose: exposes PA-RISC cycle counter support for generic kernel time code. Important APIs: `CLOCK_TICK_RATE`, `cycles_t`, and `get_cycles()` which reads control register 16 through `mfctl(16)`. Control flow: callers inline one register read and receive the current architectural interval timer/cycle value. State and persistence: no persistent state is stored here; the value comes from processor control state. Dependencies and integration points: depends on `asm/special_insns.h` and is used by timing code such as cache/TLB calibration in `cache.c`. Risks: wraparound width follows `unsigned long`, so 32-bit callers must tolerate shorter wrap periods; the register semantics are hardware-specific. Test signals: validate boot-time timing calibration, delay loops, scheduler clock behavior, and monotonic cycle reads on PA-RISC hardware or QEMU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/timex.h -->
