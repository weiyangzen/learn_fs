# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpeutil.c

## Purpose
Supplies utility routines for walking GPE block lists, mapping a global GPE index to its device, creating/deleting GPE interrupt descriptors, and freeing installed GPE handlers/notify lists during termination.

## Important APIs, Types, And Functions
- `acpi_ev_walk_gpe_list` iterates every xrupt descriptor and block under `acpi_gbl_gpe_lock`, invoking a callback with shared context.
- `acpi_ev_get_gpe_device` maps an index in the global GPE sequence to the block's device node or null for FADT-defined GPEs.
- `acpi_ev_get_gpe_xrupt_block` finds or allocates an interrupt descriptor and installs an OS interrupt handler for non-SCI GPE interrupts.
- `acpi_ev_delete_gpe_xrupt` removes a non-SCI interrupt handler, unlinks and frees the xrupt descriptor, or preserves the SCI descriptor while clearing its block list.
- `acpi_ev_delete_gpe_handlers` frees per-GPE handler objects and implicit notify node lists.

## Control Flow
List walking holds the GPE spin lock for stable traversal and lets callbacks abort with `AE_CTRL_END`. Xrupt lookup scans the global list without changing it; if absent, it allocates, appends under the spin lock, then installs an OS interrupt handler when the interrupt is not the SCI. Deletion skips handler removal for SCI, but removes non-SCI OS handlers before unlinking. Handler cleanup scans every register and every bit in a block and clears dispatch masks after freeing associated storage.

## State And Persistence
State includes `acpi_gbl_gpe_xrupt_list_head`, doubly linked xrupt descriptors, block list heads, block/device pointers, per-GPE dispatch handler pointers, and implicit notify linked lists. The device-index helper mutates a caller-provided `acpi_gpe_device_info`.

## Dependencies And Integration Points
Uses OS interrupt install/remove callbacks, GPE xrupt handler entry point, spin locks, GPE block structures, event termination, and public GPE device enumeration helpers. It supports block creation/deletion in `evgpeblk.c` and cleanup in `evmisc.c`.

## Risks And Edge Cases
Installing a new xrupt appends it before OS interrupt handler installation; failure returns an error but leaves list state that callers must account for. Walking while holding the spin lock means callbacks must be lightweight and lock-safe. SCI descriptors are never freed by `acpi_ev_delete_gpe_xrupt`, so later cleanup must not expect the same behavior as non-SCI descriptors. Handler lifetime relies on event flushing before free.

## Test Signals
Signals include callback traversal order across multiple interrupt descriptors, `AE_CTRL_END` early exit mapping to success, device mapping for FADT versus device GPE blocks, non-SCI interrupt handler installation/removal, SCI preservation, and handler/notify dispatch masks cleared after termination cleanup.
