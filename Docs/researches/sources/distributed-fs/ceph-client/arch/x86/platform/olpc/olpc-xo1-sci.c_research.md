<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-sci.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-sci.c

## Purpose
Handles XO-1 System Control Interrupts, EC event queues, lid/ebook/power input devices, and suspend wake policy.

## Important APIs, Types, And Functions
Key paths are `process_sci_queue()`, `xo1_sci_intr()`, `xo1_sci_suspend/resume()`, `setup_sci_interrupt()`, `setup_ec_sci()`, `setup_lid_events()`, and input setup/free helpers. The `lid_wake_mode` sysfs attribute selects always/open/close wake behavior.

## Control Flow
Probe validates OLPC hardware, records ACPI base, creates three input devices, configures lid and EC GPIO/PME routing, clears pending status, synchronizes switch state, requests the SCI IRQ, and enables EC events. IRQ handling clears PM/GPE status, reports power/RTC wake, schedules EC queue work, and updates lid state. Suspend adjusts PM/EC/GPIO wake sources; resume reinitializes lid/EC state and notifies battery/AC supplies.

## State And Persistence
Static state tracks ACPI base, input device pointers, SCI IRQ, lid state/inversion, and lid wake mode. EC wake masks and CS5536 GPIO/PM registers persist in hardware.

## Dependencies And Integration Points
Integrates OLPC EC commands, CS5535 GPIO/PIC helpers, power-supply notifications, input subsystem, platform driver PM callbacks, and XO-1 PM wake-mask exports.

## Risks And Edge Cases
The lid edge workaround depends on GPIO input inversion and must not lose transitions. EC commands can time out in workqueue context. Error unwinding must unregister only initialized devices. Suspend wake policy can miss desired close/open events if `lid_wake_mode` and current lid state are miscomputed.

## Test Signals
Input events for power, lid, and tablet mode; battery/AC refresh on SCI; wake from configured sources; and no stuck SCI/GPIO status bits validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-sci.c -->
