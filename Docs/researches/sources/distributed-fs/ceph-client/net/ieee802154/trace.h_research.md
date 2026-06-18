# sources/distributed-fs/ceph-client/net/ieee802154/trace.h

## Purpose
`trace.h` declares tracepoints for cfg802154 registered-device operations. It makes WPAN PHY, WPAN device, channel, CCA, scan, beacon, association, and return-value events observable through the Linux tracing subsystem.

## Important APIs, types, and functions
The header sets `TRACE_SYSTEM cfg802154`, defines helper macros such as `WPAN_PHY_ENTRY`, `WPAN_DEV_ENTRY`, `WPAN_CCA_ENTRY`, and `BOOL_TO_STR`, then uses `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `DEFINE_EVENT_PRINT`, and `TRACE_EVENT`. Events include `802154_rdev_suspend`, `802154_rdev_resume`, `802154_rdev_add_virtual_intf`, `802154_rdev_del_virtual_intf`, channel and TX power setters, CCA setters, PAN ID and short address setters, CSMA/backoff/retry/LBT/ack defaults, scan and beacon operations, association/disassociation, and `802154_rdev_return_int`.

## Control flow
The tracepoint macros generate event classes and per-event record/print callbacks. At runtime, cfg802154 rdev wrapper code calls the generated trace hooks when operations are attempted or return. Each event copies stable values into `__entry` fields during `TP_fast_assign()` and formats them through `TP_printk()`.

## State and persistence
The header does not manage subsystem state. Trace records are transient ring-buffer entries controlled by the tracing subsystem. Event payloads intentionally copy names and identifiers so traces do not depend on later object lifetime.

## Dependencies and integration points
It includes `<linux/tracepoint.h>` and `<net/cfg802154.h>`. `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>` integrate with kernel trace generation, while `trace.c` supplies the single `CREATE_TRACE_POINTS` translation unit.

## Risks and invariants
Tracepoint prototypes must match the wrapper call sites and the underlying cfg802154 types. Event names beginning with digits are accepted by the trace macro conventions but should remain consistent for userspace tooling. `WPAN_DEV_ASSIGN` handles null or error `wpan_dev` pointers by recording identifier zero; consumers should treat zero as a sentinel.

## Test signals
Build coverage catches mismatched prototypes. Runtime signals include enabling cfg802154 trace events, invoking nl802154 operations such as virtual-interface creation or channel changes, and verifying printed fields match the requested PHY/device/action.
