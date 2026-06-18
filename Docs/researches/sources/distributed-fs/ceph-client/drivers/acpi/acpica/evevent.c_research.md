# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evevent.c

## Purpose
Initializes and dispatches fixed ACPI events and coordinates top-level event interrupt handler installation. It disables fixed events during setup, initializes GPEs before SCI delivery, installs SCI and global lock handlers, detects active fixed-event bits, dispatches registered handlers, and exposes a status-set query helper.

## Important APIs, Types, And Functions
- `acpi_ev_initialize_events` initializes fixed events and GPE data structures unless reduced hardware mode is active.
- `acpi_ev_install_xrupt_handlers` installs the SCI handler and global-lock fixed event handler, then marks events initialized.
- `acpi_ev_fixed_event_initialize` clears fixed-event handler slots and disables all fixed events with valid enable registers.
- `acpi_ev_fixed_event_detect` reads PM1 status/enable registers, counts and globally reports active fixed events, and dispatches each enabled status bit.
- `acpi_ev_fixed_event_dispatch` clears status, disables unhandled events, and invokes the installed fixed-event handler.
- `acpi_any_fixed_event_status_set` checks whether any enabled fixed event currently has status set.

## Control Flow
Initialization returns early for reduced hardware. Otherwise, fixed events are disabled before GPE setup to avoid interrupts before handler registration. Interrupt installation starts with SCI, then global lock. During SCI processing, fixed-event detection reads status and enable registers once, iterates all fixed event descriptors, and dispatches only bits with both status and enable set. Dispatch clears the event status before calling the handler, or disables the event permanently if no handler exists.

## State And Persistence
Global state includes `acpi_gbl_fixed_event_handlers`, `acpi_gbl_fixed_event_info`, `acpi_fixed_event_count`, global event handler pointers, and `acpi_gbl_events_initialized`. Hardware PM1 enable/status registers persist event enablement and pending status.

## Dependencies And Integration Points
Depends on hardware register access helpers, fixed-event bit metadata, SCI installation, global-lock initialization, GPE initialization, and global event notification callbacks. The module is compiled out for reduced-hardware builds.

## Risks And Edge Cases
Register read failures silently produce "not handled" for detection. Missing handlers are treated defensively by disabling the event to stop interrupt storms. Events with enable register ID `0xFF` are not disabled during initialization. Ordering matters: enabling SCIs before fixed/GPE setup could deliver events into uninitialized handler tables.

## Test Signals
Signals include fixed events disabled after initialization, no-op behavior in reduced hardware mode, handler dispatch only when both status and enable bits are set, global handler invocation and per-event count increments, unhandled fixed events being disabled, and `acpi_any_fixed_event_status_set` reflecting PM1 register contents.
