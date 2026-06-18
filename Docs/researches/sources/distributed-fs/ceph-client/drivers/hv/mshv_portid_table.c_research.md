# sources/distributed-fs/ceph-client/drivers/hv/mshv_portid_table.c

## Purpose

`mshv_portid_table.c` provides an IDR-backed global table for Hyper-V port IDs, primarily used to map SynIC doorbell port IDs back to kernel callback metadata.

## Important APIs, Types, and Functions

- `mshv_portid_alloc()` allocates an ID in `[1, INT_MAX)` for a caller-provided `port_table_info`.
- `mshv_portid_lookup()` copies table info for a port ID under RCU read locking.
- `mshv_portid_free()` removes an ID, waits for RCU readers, and frees the entry.
- `mshv_port_table_fini()` removes and RCU-frees all remaining entries during module exit.

## Control Flow

Doorbell registration allocates and fills `port_table_info`, obtains an ID, then uses that ID as the Hyper-V port/connection ID. SynIC doorbell ISR lookup copies the table entry and invokes the callback if the port type is `HV_PORT_TYPE_DOORBELL`. Unregistration disconnects/deletes the Hyper-V port and frees the ID.

## State and Persistence Behavior

The static `DEFINE_IDR(port_table_idr)` is global module state. Entries persist until explicit free or module finalization. Lookup returns a by-value copy so callbacks can be invoked after dropping RCU, but pointer fields inside the copy remain owned by the original subsystem.

## Dependencies and Integration Points

The file depends on Linux IDR, RCU freeing, Hyper-V definitions, and `mshv_root.h`. It integrates with `mshv_synic.c` doorbell registration and ISR dispatch.

## Risks and Edge Cases

`mshv_portid_lookup()` drops RCU before copying `_info`, so the entry can be freed between `idr_find()` and `*_info = *_info`; this is a use-after-free risk unless external ordering prevents concurrent free. The finalizer uses `kfree_rcu`, while normal free synchronizes then `kfree`s. IDR allocation uses `GFP_KERNEL` while holding the IDR lock via `idr_lock`, which should be reviewed for allocation constraints.

## Test Signals

Exercise concurrent lookup/free under KCSAN/KASAN, repeated allocate/free, module finalization with live entries, lookup of missing IDs, and doorbell callback dispatch while unregistering.
