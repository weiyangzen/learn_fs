# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/interrupt.c

## Purpose
`interrupt.c` owns wil6210 interrupt masking, unmasking, moderation setup, hard/threaded IRQ dispatch, HALP wake voting interrupts, firmware-ready/error handling, and IRQ registration/freeing. It supports legacy DMA and enhanced DMA as well as single MSI/INTx and triple-MSI layouts.

## Important APIs, Types, And Functions
Public entry points include `wil_mask_irq()`, `wil_unmask_irq()`, TX/RX unmask helpers, `wil_configure_interrupt_moderation()`, `wil_configure_interrupt_moderation_edma()`, `wil6210_clear_irq()`, `wil6210_set_halp()`, `wil6210_clear_halp()`, `wil6210_init_irq()`, and `wil6210_fini_irq()`. Internal handlers include legacy and EDMA RX/TX IRQ functions, `wil6210_irq_misc()`, `wil6210_irq_misc_thread()`, `wil6210_hardirq()`, and `wil6210_thread_irq()`.

## Control Flow
In single-MSI or INTx mode, the hard IRQ reads the pseudo-cause register, masks pseudo interrupts, then calls RX, TX, and MISC real handlers based on bits. RX/TX handlers mask their own source, read and clear ICR, schedule NAPI when firmware and NAPI are ready, and leave source unmasking to NAPI completion. MISC handles firmware-ready, firmware-error, mailbox, and HALP bits; firmware crash and mailbox receive are completed in thread context. In triple-MSI mode, TX, RX, and MISC have separate IRQ registrations.

## State And Persistence
The file updates `wil->status` bits such as `wil_status_irqen`, `wil_status_fwready`, and `wil_status_mbox_ready`; stores pending misc bits in `wil->isr_misc`; caches mailbox registers in `wil->mbox_ctl`; completes HALP and suspend waiters; and increments ISR counters used by debugfs. Register mask state is persistent in hardware until reprogrammed.

## Dependencies And Integration Points
It depends on register definitions in `wil6210.h`, tracepoints in `trace.h`, TX/RX NAPI handlers in `netdev.c`, WMI mailbox receive, firmware crash dump/recovery paths, platform notifications, and PM suspend synchronization. `main.c` calls clear/mask/unmask during reset and firmware load.

## Risks
IRQ ordering is delicate: real ISR registers must be masked/unmasked correctly or hardware may malfunction. Firmware error handling clears `wil_status_fwready` in hard IRQ and defers recovery/notification; races with reset and suspend need careful status checks. The debug path intentionally detects IRQs arriving while masked. Triple-MSI and pseudo-IRQ paths differ for suspend response completion.

## Test Signals
Exercise legacy DMA versus EDMA, INTx/single MSI/triple MSI, RX/TX interrupt storms, spurious zero causes, firmware-ready mailbox validation, firmware crash events, HALP vote timeouts, suspend response wakeups, and NAPI completion unmasking.
