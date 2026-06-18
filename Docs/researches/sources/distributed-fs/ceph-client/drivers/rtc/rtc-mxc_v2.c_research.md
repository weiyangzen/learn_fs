# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mxc_v2.c

Purpose: implements the i.MX53 secure RTC low-power block, using the LP secure counter and alarm registers with CKIL-domain synchronization and wake IRQ support.

Important APIs/types/functions: `struct mxc_rtc_data` tracks RTC device, MMIO, clock, spinlock, and IRQ. `mxc_rtc_sync_lp_locked()` waits for three CKIL cycles by watching `SRTC_LPSCLR`. `mxc_rtc_lock()`/`unlock()` combine the spinlock with clock enable/disable. `mxc_rtc_read_time()`/`set_time()` access `SRTC_LPSCMR`; alarm callbacks access `SRTC_LPSAR`, `SRTC_LPCR`, and `SRTC_LPSR`. `mxc_rtc_wait_for_flag()` handles init/non-valid state transitions.

Control flow: probe maps MMIO, gets the clock and IRQ, initializes wake IRQ, prepares/enables the clock, initializes glitch detect, clears status, exits init state, exits non-valid state with LP enabled, allocates/registers the RTC, disables the clock but leaves it prepared, then requests the IRQ. Runtime register writes take the driver lock, enable the clock, perform the write, synchronize across CKIL cycles, and disable the clock. The IRQ handler enables the clock under lock, checks/clears alarm status, disables further alarm wake bits, synchronizes, and reports `RTC_AF`.

State and persistence: hardware persists the LP secure counter, alarm register, LP control/status bits, non-valid/init state, glitch detector setting, and wake enable. Driver state persists lock, clock preparation, and IRQ.

Dependencies and integration: depends on OF compatible `fsl,imx53-rtc`, platform MMIO, a single RTC clock, one IRQ, `dev_pm_set_wake_irq()`, and the RTC class.

Risks and test signals: `mxc_rtc_read_time()` reads only `SRTC_LPSCMR`, so it treats the counter as a 32-bit seconds value and ignores `SRTC_LPSCLR` fractional/low bits. Synchronization loops have bounded timeouts and log once on stuck counters. Probe must balance prepared/enabled/disabled clock states across multiple error paths. Test init and non-valid state timeout paths, alarm interrupt disable behavior, CKIL sync timeout, clock-enable failure in IRQ and callbacks, wake IRQ setup, and U32 range wrap.
