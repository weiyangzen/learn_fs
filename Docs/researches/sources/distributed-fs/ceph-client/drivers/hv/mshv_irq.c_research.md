# sources/distributed-fs/ceph-client/drivers/hv/mshv_irq.c

## Purpose

`mshv_irq.c` manages userspace-provided guest IRQ routing tables for MSHV partitions and translates routing entries into Hyper-V virtual interrupt descriptors.

## Important APIs, Types, and Functions

- `mshv_update_routing_table()` validates and installs a new RCU-protected `mshv_girq_routing_table`.
- `mshv_free_routing_table()` frees the current table at partition teardown.
- `mshv_ret_girq_entry()` returns a routing entry for an IRQ number under SRCU/lock protection.
- `mshv_copy_girq_info()` converts a `mshv_guest_irq_ent` MSI-style entry into `struct mshv_lapic_irq`.

## Control Flow

The set-MSI-routing ioctl copies user entries and calls `mshv_update_routing_table()`. The function validates GSI bounds and rejects non-zero high MSI address, sizes the table to the maximum GSI plus one, rejects duplicate GSI mappings, fills entries, swaps the table under `pt_irq_lock`, notifies irqfds to refresh cached routes, then waits for SRCU readers before freeing the old table.

## State and Persistence Behavior

`partition->pt_girq_tbl` is an RCU pointer to the active flexible-array routing table. IRQFDs cache translated entries and are refreshed on each route swap. Route entries persist until replaced or the partition is destroyed.

## Dependencies and Integration Points

The file depends on slab allocation, RCU/SRCU, `mshv_eventfd.h`, `mshv_root.h`, and tracepoints. It feeds `mshv_eventfd.c` interrupt injection and is driven by `MSHV_SET_MSI_ROUTING`.

## Risks and Edge Cases

GSI zero is ambiguous because duplicate detection tests `guest_irq_num != 0`, so duplicate GSI 0 entries may not be rejected as intended. Only one-to-one GSI/MSI routing is supported. x86 and arm64 fill different `hv_interrupt_control` fields. Premature irqfd registration before routes exist yields an invalid entry that is intentionally ignored.

## Test Signals

Test empty table swaps, maximum GSI bounds, duplicate GSI handling including GSI 0, non-zero `address_hi` rejection, irqfd route refresh after swaps, SRCU readers during replacement, and architecture-specific conversion of vector/APIC/interrupt control fields.
