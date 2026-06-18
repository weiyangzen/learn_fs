# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-irq.c

## Purpose
This file implements the shared PCI interrupt handler for cx18. It dispatches firmware mailbox commands from CPU/APU to EPU-side driver code and wakes waiters for mailbox acknowledgments.

## Important APIs, Types, and Functions
The exported handler is `cx18_irq_handler()`. Helpers `xpu_ack()` wake CPU/APU mailbox wait queues for SW2 ack bits, and `epu_cmd()` forwards SW1 CPU/APU-to-EPU command interrupts to `cx18_api_epu_cmd_irq()`.

## Control Flow
The IRQ handler reads SW1, SW2, and HW2 status registers masked by cached enable masks, clears any asserted bits, logs high-volume IRQ details when enabled, processes SW1 mailbox commands first because firmware times out incoming mailboxes quickly, leaves HW2 I2C interrupts as a TODO, then processes SW2 acknowledgments. It returns `IRQ_HANDLED` only when at least one masked bit was present.

## State and Persistence
The handler consumes and clears hardware interrupt status bits and wakes wait queues. It relies on `cx->sw1_irq_mask`, `cx->sw2_irq_mask`, and `cx->hw2_irq_mask` maintained by I/O helpers.

## Dependencies and Integration Points
It depends on MMIO helpers, interrupt register constants, mailbox IRQ handling, and SCB mailbox layout. It is registered by `cx18_probe()` and disabled during removal before work queues are drained.

## Risks and Edge Cases
Ordering matters: SW1 command handling before SW2 ack handling prevents firmware-side mailbox timeout. Shared IRQs require returning `IRQ_NONE` for unrelated interrupts. HW2 I2C status is cleared but not otherwise handled. Incorrect masks can drop mailbox completions or cause interrupt storms.

## Test Signals
Capture start/stop and firmware API calls should produce mailbox acks without timeout. Shared IRQ systems should not show spurious handling. High-volume IRQ debug should show SW1/SW2 transitions during DMA and API calls.
