<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo15-sci.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo15-sci.c

## Purpose
Implements XO-1.5 ACPI-backed SCI handling for EC events and custom lid wake-on-close behavior.

## Important APIs, Types, And Functions
`set_lid_wake_behavior()` calls ACPI method `\_SB.PCI0.LID.LIDW`. `xo15_sci_add()` evaluates `_GPE`, installs a GPE handler, creates `lid_wake_on_close` sysfs, drains EC events, enables EC masks and GPE wake. `process_sci_queue()` updates OLPC battery/AC power supplies.

## Control Flow
The ACPI driver binds HID `XO15EC`. Add installs the edge-triggered GPE handler, creates sysfs, drains pending SCI data, enables all EC events, enables the GPE, and marks wake capability. GPE handler schedules work and reenables the GPE. Remove disables GPE, removes handler/sysfs, and cancels work. Resume re-enables EC masks and refreshes power supplies.

## State And Persistence
Stores the GPE number and current lid-wake-on-close flag. The sysfs attribute persists with the ACPI device. ACPI firmware stores the actual wake behavior.

## Dependencies And Integration Points
Depends on ACPI device enumeration, OLPC EC query/mask APIs, power-supply class, and the XO-1.5 DSDT custom method.

## Risks And Edge Cases
Failure to remove a GPE handler can leave callbacks after device removal. `set_lid_wake_behavior()` returns 1 on ACPI failure rather than a negative errno. The custom ACPI method is firmware-specific.

## Test Signals
ACPI driver binding to `XO15EC`, functioning `lid_wake_on_close` sysfs, EC battery/AC updates, and wake from EC GPE validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo15-sci.c -->
