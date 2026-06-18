# sources/distributed-fs/ceph-client/drivers/rtc/rtc-imxdi.c

Purpose: implements the Freescale/NXP i.MX DryIce RTC using a security/tamper-aware 47-bit 32 kHz counter truncated to seconds. It handles complex DryIce valid, non-valid, and failure states, synchronized low-power-domain writes, alarms, wake IRQs, and security-violation reporting.

Important APIs/types/functions: `struct imxdi_dev` stores platform device, RTC, MMIO, clock, cached DSR bits, interrupt lock, write waitqueue, write mutex, and alarm work. State handlers `di_handle_state()`, `di_handle_invalid_state()`, `di_handle_failure_state()`, and `di_handle_invalid_and_failure_state()` recover or reject DryIce states. `di_write_wait()` serializes register writes and waits for write-complete/error IRQs. RTC methods are `dryice_rtc_read_time()`, `dryice_rtc_set_time()`, `dryice_rtc_read_alarm()`, `dryice_rtc_set_alarm()`, and `dryice_rtc_alarm_irq_enable()`.

Control flow: probe maps registers, obtains normal and optional security IRQs, enables the input clock, masks interrupts, runs DryIce state recovery, requests IRQs, enables wake IRQ, attaches RTC ops, and registers the RTC. Register writes use write-complete interrupts and a waitqueue. The IRQ handler handles security violations, write completion/error wakeups, and alarm flags. Alarm work clears `DSR_CAF` in sleepable context before reporting `RTC_AF`.

State and persistence: DryIce stores time, alarm, tamper/security state, monotonic configuration, and lock bits in hardware. Runtime state tracks synchronization and work for writes/alarms.

Dependencies and integration: depends on platform/OF match `fsl,imx25-rtc`, clk framework, MMIO, IRQs, workqueues, wake IRQ helpers, RTC core locks, and DryIce security semantics.

Risks and test signals: reading DSR clears WCF, so paths must avoid disrupting write completion; this is carefully guarded in alarm read but remains a central risk. Some failure states require main or battery power cycling and return `-ENODEV`. Test each DryIce state transition, write timeout/error handling, concurrent alarm/write paths, optional security IRQ absence, wake IRQ setup, clock cleanup, and alarm work flushing on remove.
