<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_serio.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_serio.c

## Purpose
Adapts BMC-side KCS channels to Linux serio ports, allowing host-written KCS data bytes to be delivered through the serio subsystem.

## Important APIs, Types, and Functions
- `struct kcs_bmc_serio` stores client linkage, serio port pointer, lock, and instance list entry.
- `kcs_bmc_serio_event()` reads status and data on IBF and calls `serio_interrupt()`.
- `kcs_bmc_serio_open()` and `kcs_bmc_serio_close()` enable/disable the KCS device for this client.
- `kcs_bmc_serio_add_device()` allocates a serio port of type `SERIO_8042`, registers it, and tracks the instance.
- `kcs_bmc_serio_remove_device()` unregisters the serio port and disables the client.

## Control Flow
The module registers a KCS BMC consumer driver. For each channel it creates a serio port whose open/close controls active KCS ownership. When a KCS event arrives and IBF is set, the byte is passed to the serio core.

## State and Persistence
Instances are tracked in `kcs_bmc_serio_instances` under a spinlock. The serio core owns the port lifetime after registration; the private state is device-managed except for the serio port allocation.

## Dependencies and Integration Points
Depends on the generic KCS BMC client API and Linux serio subsystem. It competes with the IPMI cdev client for exclusive channel ownership when opened.

## Risks
It treats KCS input as raw serio bytes and does not implement full IPMI KCS protocol phases. Because `SERIO_8042` is used, downstream interpretation depends on serio consumers. Removal must account for `serio_unregister_port()` freeing the port.

## Test Signals
Register/remove with active and inactive KCS channels, open exclusivity against other clients, IBF event byte delivery, and close disabling events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_serio.c -->
