# sources/distributed-fs/ceph-client/arch/mips/cobalt/time.c

Purpose: initializes Cobalt timer hardware and calibrates the MIPS high-precision timer against the GT641xx timer.

Important APIs: `plat_time_init()` calls `setup_pit_timer()`, sets the GT641xx base clock to 50 MHz, waits for timer0 state transitions, measures CP0 Count over 100 ms, and sets `mips_hpt_frequency`.

State and integration: writes global timer frequency for MIPS timekeeping and relies on PIT/GT641xx timer infrastructure.

Risks and test signals: busy-wait loops assume GT641xx timer state changes; a stuck timer hangs boot. Boot logs should show plausible MIPS counter frequency and stable timekeeping.
