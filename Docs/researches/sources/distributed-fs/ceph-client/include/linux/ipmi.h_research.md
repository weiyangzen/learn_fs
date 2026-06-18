# sources/distributed-fs/ceph-client/include/linux/ipmi.h

## Purpose
`ipmi.h` defines the upper-layer IPMI message handler API used by kernel clients to send BMC messages, receive responses/events, watch SMI interfaces, manage source addressing, enter maintenance mode, and issue panic-time requests.

## Important APIs, types, and functions
Key types are opaque `struct ipmi_user`, `struct ipmi_recv_msg`, `struct ipmi_user_hndl`, `struct ipmi_smi_watcher`, `enum ipmi_addr_src`, `union ipmi_smi_info_union`, and `struct ipmi_smi_info`. Major APIs include user create/destroy, address/LUN setters, `ipmi_request_settime`, `ipmi_request_supply_msgs`, polling, command registration, event enabling, watcher registration, address validation, SMI info lookup, checksum, and panic request helpers.

## Control flow
Clients create a user for an interface, issue requests with message IDs and optional supplied buffers, and receive callbacks through `ipmi_recv_hndl`. Watchers are notified for new/gone SMIs. Panic and watchdog callbacks run under special constraints and must avoid normal IPMI calls where documented.

## State and persistence
Runtime state includes users, interface source addresses/LUNs, command registrations, queued receive messages, event delivery flags, watchers, and maintenance mode. No persistent storage is defined here.

## Dependencies and integration points
It depends on UAPI IPMI structures, list handling, devices, ACPI handles, procfs declarations, watchdog users, firmware update tooling, and low-level SMI drivers.

## Risks and test signals
Risks include callbacks under locks, use-after-destroy, command tuple conflicts, retry timing, panic-context allocation, and interface-wide address changes affecting all users. Tests should cover user destruction while callbacks are pending, duplicate command registration, event subscription handoff, maintenance mode transitions, supplied-message paths, and SMI watcher hotplug.
