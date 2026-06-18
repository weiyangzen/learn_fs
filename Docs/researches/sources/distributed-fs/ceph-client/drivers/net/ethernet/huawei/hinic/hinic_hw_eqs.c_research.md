# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_eqs.c

## Purpose
Implements HINIC asynchronous and completion event queues. AEQs carry mailbox and management events and are processed through a workqueue; CEQs carry command queue completions and are processed through tasklets. The file allocates DMA pages, programs EQ registers, handles interrupts, dispatches callbacks, and tears queues down safely.

## Important APIs, Types, and Functions
Public APIs are `hinic_aeq_register_hw_cb`, `hinic_aeq_unregister_hw_cb`, `hinic_ceq_register_cb`, `hinic_ceq_unregister_cb`, `hinic_aeqs_init`, `hinic_aeqs_free`, `hinic_ceqs_init`, `hinic_ceqs_free`, `hinic_dump_ceq_info`, and `hinic_dump_aeq_info`. Internal logic centers on `eq_update_ci`, `aeq_irq_handler`, `ceq_irq_handler`, `ceq_event_handler`, `set_eq_ctrls`, `alloc_eq_pages`, `init_eq`, and `remove_eq`.

## Control Flow
Initialization clears hardware CI/PI registers, derives element size and page counts, programs control registers, arms the queue, allocates coherent pages, initializes elements with the current wrapped bit, configures MSI-X attributes, and requests an IRQ. AEQ IRQs clear resend counters and queue work; CEQ IRQs clear counters and schedule a tasklet. Handlers scan elements until the hardware wrapped bit indicates no more events, dispatch registered callbacks with running-state guards, advance consumer index and wrap state, then update the hardware CI with checksum and arm bit.

## State and Persistence Behavior
Each `hinic_eq` stores queue id, type, length, page size, consumer index, wrap bit, element/page geometry, MSI-X entry, IRQ name, coherent DMA addresses, and deferred execution object. Hardware state includes MTT page addresses, queue controls, producer/consumer index registers, and MSI-X resend counters.

## Dependencies and Integration Points
Uses CSR offsets from `hinic_hw_csr.h`, BAR access from `hinic_hw_if.h`, Linux IRQ/workqueue/tasklet APIs, and DMA coherent allocation. AEQ callbacks are registered by mailbox and management code; CEQ callbacks are registered by command queue code.

## Risks
Callback unregister waits for running flags but does not cancel already queued external work created by callbacks. Element wrap handling and endian conversion are critical for not skipping or replaying events. VF CEQ control programming goes through management firmware rather than direct CSR writes. Teardown must disable MSI-X, free IRQ, cancel work/tasklet, clear queue length registers, update CI unarmed, and only then free DMA pages.

## Test Signals
AEQ/CEQ init/free, MSI-X interrupt delivery, mailbox AEQs, management AEQs, command CEQs, callback unregister under traffic, VF CEQ control through firmware, EQ page-count boundary failures, forced unknown event types, and command timeout diagnostics exercise the file.
