# sources/distributed-fs/ceph-client/drivers/irqchip/irq-stm32-exti.c

## Purpose
Implements STM32 F4/H7 EXTI edge interrupt controllers using generic irq chips. It supports one-bank F4 and three-bank H7 register layouts, cascaded parent interrupts, wake masks, and trigger configuration.

## Important APIs, Types, And Functions
`stm32_exti_bank` describes per-bank register offsets; `stm32_exti_drv_data` selects the bank table; `stm32_exti_chip_data` caches wake/mask and trigger registers. `stm32_irq_handler()` scans bank pending registers. `stm32_irq_set_type()`, `stm32_irq_ack()`, `stm32_irq_suspend()`, and `stm32_irq_resume()` are installed in generic chip callbacks.

## Control Flow
Early OF init maps MMIO, creates a linear domain covering all banks, allocates one generic chip per bank, clears mask/event registers after hot reboot, assigns register offsets and callbacks, then chains every parent IRQ declared by the node. Dispatch loops over each bank and handles all pending bits. Type setting updates RTSR/FTSR under the generic chip lock.

## State And Persistence
Per-bank chip data caches rising/falling trigger registers during suspend and uses generic chip mask/wake caches to restore interrupt mask state. Hardware state is otherwise the IMR, RTSR, FTSR, SWIER, and pending registers.

## Dependencies And Integration Points
Depends on OF init, chained irqchips, generic irq chips, one/two-cell irqdomain translation, and compatible strings `st,stm32-exti` and `st,stm32h7-exti`.

## Risks
Only edge trigger types are accepted; level requests fail. Parent IRQ count and bank layout must match the SoC. Since the IP has no reset, hot reboot residue is handled by clearing IMR/EMR; missing this can produce stale interrupts.

## Test Signals
Test F4 and H7 DTs, rising/falling/both-edge inputs, multiple pending bits per bank, wake-enabled suspend/resume, and hot reboot without stale pending events.
