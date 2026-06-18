# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_irq.c

## Purpose
`txgbe_irq.c` implements TXGBE interrupt enablement, queue MSI-X IRQ request, and a nested misc IRQ domain for link, GPIO/module, PTP, and VF mailbox causes.

## Important APIs, Types, and Functions
Exports are `txgbe_irq_enable()`, `txgbe_request_queue_irqs()`, `txgbe_free_misc_irq()`, and `txgbe_setup_misc_irq()`. Internal pieces include `txgbe_request_link_irq()`, `txgbe_request_gpio_irq()`, `txgbe_misc_irq_domain_map()`, `txgbe_misc_irq_handle()`, `txgbe_misc_irq_thread_fn()`, and `txgbe_del_irq_domain()`.

## Control Flow
Open calls `txgbe_setup_misc_irq()` first, creating an irq_domain, mapping hardware sub-IRQs, requesting the top-level threaded misc IRQ, then requesting nested link and optional AML GPIO IRQs. Queue IRQs are requested separately for MSI-X queue vectors. The top-half reads ISB cause registers; in MSI-X mode it handles VF mailbox immediately and wakes the thread. In MSI/legacy mode it also schedules queue NAPI and captures misc causes. The thread dispatches link and GPIO causes through nested IRQs, handles PTP PPS events, and re-enables misc interrupts.

## State and Persistence Behavior
Runtime state is in `struct txgbe`: misc irq domain/chip, top-level irq, link/gpio virqs, and cached `eicr`. `wx->misc_irq_domain` records setup state. Hardware interrupt enable masks persist until disabled or reset. No disk persistence.

## Dependencies and Integration Points
It depends on Linux irqdomain/threaded IRQ APIs, shared queue interrupt handler `wx_msix_clean_rings`, PTP PPS handling, SR-IOV `wx_msg_task()`, TXGBE PHY link IRQ handler from `txgbe_phy`, AML GPIO handler, and shared interrupt enable helpers.

## Risks and Edge Cases
`txgbe_free_misc_irq()` assumes setup completed and frees GPIO only for non-SP devices; callers must avoid double-free on partial setup. VF mailbox handling in MSI-X mode re-enables misc interrupts before threaded sub-IRQ handling. Nested IRQ mappings must be disposed on all failure paths. Legacy/MSI top-half schedules only q_vector 0.

## Test Signals
Test MSI-X, MSI, and legacy interrupt modes; queue IRQ request failure unwinding; misc domain setup failure; link IRQ, AML GPIO module IRQ, VF mailbox, PTP PPS, and shared interrupt not-ours paths. Verify open/close repeatedly does not leak virqs.
