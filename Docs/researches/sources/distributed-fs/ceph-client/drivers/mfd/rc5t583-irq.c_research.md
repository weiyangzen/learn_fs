# sources/distributed-fs/ceph-client/drivers/mfd/rc5t583-irq.c

## Purpose
`rc5t583-irq.c` is the custom nested IRQ controller for the Ricoh RC5T583 PMIC. It maps PMIC interrupt groups to Linux IRQs, caches mask/edge registers, handles the threaded parent IRQ, clears PMIC status, and dispatches enabled child IRQs.

## Important APIs, Types, And Functions
`struct rc5t583_irq_data` maps each logical IRQ to interrupt type, master bit, group index, enable bit, and mask register index. `rc5t583_irq_mask()`, `rc5t583_irq_unmask()`, `rc5t583_irq_set_type()`, `rc5t583_irq_sync_unlock()`, and `rc5t583_irq_set_wake()` form the IRQ chip. `rc5t583_irq()` is the threaded parent handler. `rc5t583_irq_init()` initializes registers, maps child IRQs, and requests the parent IRQ.

## Control Flow
Init rejects missing `irq_base`, clears cached enable/edge registers in hardware, disables master interrupt enables, clears pending interrupt registers, stores base/parent IRQ, assigns each Linux IRQ a chip and simple handler, marks them nested, and requests the parent threaded IRQ. On interrupt, the handler reads master status, reads only active group status registers, remaps RTC bits to logical order, clears status, merges GPIO falling/rising status, and calls `handle_nested_irq()` for enabled logical IRQs.

## State And Persistence
State is stored in the parent `struct rc5t583`: cached group enable masks, interrupt enable registers, GPIO edge registers, master enable register, base IRQ, parent IRQ, and mutex. Hardware mask and edge registers are synchronized on bus unlock.

## Dependencies And Integration Points
It depends on register helpers and constants from `linux/mfd/rc5t583.h`, the RC5T583 core probe, Linux nested IRQ APIs, and child devices that use contiguous IRQ numbers starting at platform-data `irq_base`.

## Risks
The unmask path updates `group_irq_en[data->grp_index]` but the dispatch path indexes `group_irq_en[data->master_bit]`, so this code relies on the chosen mapping and is fragile. Only GPIO IRQs support edge type changes; other type requests fail. The driver uses legacy fixed IRQ bases rather than irq_domain allocation. Status clear writes use inverted status bytes, requiring hardware-specific semantics.

## Test Signals
Validate every logical IRQ mapping, GPIO rising/falling/both-edge programming, RTC bit remapping, mask/unmask sync writes, wake propagation to parent IRQ, parent threaded IRQ dispatch, `irq_base` absence, and child devices receiving nested interrupts.
