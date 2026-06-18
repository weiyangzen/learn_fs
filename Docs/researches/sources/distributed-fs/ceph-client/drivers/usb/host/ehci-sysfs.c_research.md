# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-sysfs.c

## Purpose
Sysfs support included by the EHCI core. It exposes companion-controller port ownership and the maximum periodic microframe bandwidth setting for runtime inspection/tuning.

## Important APIs, types, and functions
`companion_show()` lists ports dedicated to a companion controller. `companion_store()` parses `portnum` or `-portnum`, updates `ehci->companion_ports`, and calls `set_owner()`. `uframe_periodic_max_show()` displays `ehci->uframe_periodic_max`. `uframe_periodic_max_store()` validates and updates the limit under `ehci->lock`. `create_sysfs_files()` and `remove_sysfs_files()` install/remove attributes.

## Control flow
On EHCI initialization, sysfs creation adds `companion` unless the controller has an integrated TT, then adds `uframe_periodic_max`. Writes to `companion` validate the port range and immediately program ownership. Writes to `uframe_periodic_max` parse an integer, require 100 through 124 usec/uframe, and refuse decreases below already allocated periodic bandwidth.

## State and persistence behavior
State is `ehci->companion_ports`, hardware PORT_OWNER bits, `ehci->uframe_periodic_max`, and current `bandwidth[]` accounting. Values persist only for the HCD lifetime and can affect subsequent periodic scheduling.

## Dependencies and integration points
Depends on device sysfs, EHCI root-hub helpers, `set_owner()`, `ehci_is_TDI()`, and scheduler bandwidth accounting.

## Risks and edge cases
Changing port ownership at runtime can disconnect or hand devices to companion controllers. Lowering bandwidth is protected by a lock and allocation scan, but raising to non-standard limits is allowed with a warning. The `companion` file is absent for integrated-TT controllers.

## Test signals
Sysfs file presence/absence, valid and invalid companion port writes, owner bit changes, `uframe_periodic_max` invalid values, refusal below allocated bandwidth, successful increase/decrease, and concurrent periodic URB submission are important tests.
