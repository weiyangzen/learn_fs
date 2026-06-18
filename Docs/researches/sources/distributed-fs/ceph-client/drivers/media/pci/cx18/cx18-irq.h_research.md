# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-irq.h

## Purpose
This header defines cx18 interrupt bit masks and register offsets used by IRQ, MMIO, firmware, I2C, and mailbox code.

## Important APIs, Types, and Functions
It defines HW2 I2C interrupt bits, HW2 clear/mask registers, SW1 set/status/PCI-enable registers, SW2 set/status/CPU-enable/PCI-enable registers, and declares `irqreturn_t cx18_irq_handler(int irq, void *dev_id);`.

## Control Flow
There is no executable flow. The constants control how code enables, disables, clears, and sends software interrupts between the host/EPU and firmware CPUs/APU.

## State and Persistence
Interrupt state is hardware-resident and cached in `struct cx18`; this header only names bits and offsets.

## Dependencies and Integration Points
It is consumed by `cx18-irq.c`, `cx18-io.c`, `cx18-i2c.c`, `cx18-firmware.c`, and `cx18-mailbox.c`. It forms the shared contract for mailbox wakeups and firmware signaling.

## Risks and Edge Cases
Wrong register offsets or bit masks can hang firmware API calls, miss DMA completions, or make shared IRQ handling noisy. SW1 and SW2 directionality must remain clear to avoid sending interrupts to the wrong processor.

## Test Signals
Firmware API calls, DMA done notifications, and I2C init stale-interrupt clears should work without timeout. Build errors catch declaration mismatches.
