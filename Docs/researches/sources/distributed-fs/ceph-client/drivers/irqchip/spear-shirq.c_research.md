# sources/distributed-fs/ceph-client/drivers/irqchip/spear-shirq.c

## Purpose
Implements shared interrupt demultiplexing for ST SPEAr300/310/320 platforms. It maps SoC-specific shared IRQ blocks into legacy Linux IRQ descriptors and dispatches child interrupts from shared status bits.

## Important APIs, Types, And Functions
`struct spear_shirq` describes each block's MMIO base, status/mask registers, bit mask, virtual IRQ base, number of IRQs, bit offset, and chip. Static block tables define SPEAr300/310/320 layouts. `shirq_irq_mask()` and `_unmask()` update mask registers under a global raw spinlock, while `shirq_handler()` dispatches pending child bits.

## Control Flow
Variant OF init calls `shirq_init()`, which maps MMIO, totals child counts, allocates a contiguous descriptor range, creates a legacy domain, assigns each block base and virq base, parses the matching parent IRQ, and registers a chained handler plus per-child chip/handler. Runtime masks status with the block mask, shifts by offset, and calls `generic_handle_irq()` for each pending child virq.

## State And Persistence
Static block descriptors are mutated with base and virq base at init. Hardware mask/status registers persist. There is no PM state, and cleanup exists only for early init failure.

## Dependencies And Integration Points
Depends on OF early irqchip init, legacy irq descriptor allocation, simple legacy irqdomains, chained handlers, and compatibles `st,spear300-shirq`, `st,spear310-shirq`, and `st,spear320-shirq`.

## Risks
Uses legacy virq allocation instead of hierarchical domains, so descriptor base stability matters. Some blocks use `dummy_irq_chip`, meaning mask/unmask is not available for all variants. Parent IRQ count/order must match the static block table. Global spinlock serializes mask changes across all blocks.

## Test Signals
Boot each SPEAr variant, verify contiguous descriptor allocation and domain mappings, trigger every shared block bit, test mask/unmask on SPEAr300, validate dummy-chip blocks dispatch correctly, and check failure cleanup for descriptor/domain allocation errors.
