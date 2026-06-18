# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evsci.c

## Purpose
`evsci.c` owns SCI interrupt installation, dispatch, and removal for non-reduced-hardware ACPICA builds. It bridges the OS interrupt layer to ACPICA fixed-event, GPE, and host-installed SCI handler dispatch.

## Important APIs, Types, And Functions
Key entry points are `acpi_ev_install_sci_handler`, `acpi_ev_remove_all_sci_handlers`, `acpi_ev_sci_dispatch`, and `acpi_ev_gpe_xrupt_handler`. The private interrupt callback `acpi_ev_sci_xrupt_handler` is registered with `acpi_os_install_interrupt_handler`. It works with `struct acpi_gpe_xrupt_info`, `struct acpi_sci_handler_info`, `acpi_gbl_sci_handler_list`, `acpi_gbl_gpe_xrupt_list_head`, and `acpi_gbl_FADT.sci_interrupt`.

## Control Flow
The SCI interrupt path enters `acpi_ev_sci_xrupt_handler`, detects fixed events with `acpi_ev_fixed_event_detect`, detects GPEs with `acpi_ev_gpe_detect`, invokes host SCI callbacks through `acpi_ev_sci_dispatch`, increments `acpi_sci_count`, and returns an interrupt-handled bitmap. GPE block interrupts use `acpi_ev_gpe_xrupt_handler`, which skips fixed events and host SCI callbacks. Installation registers the SCI IRQ using the FADT SCI interrupt number and passes the GPE interrupt list as callback context. Removal unregisters the OS interrupt handler and frees all host SCI callback records.

## State And Persistence
State is process/kernel resident only. `acpi_gbl_sci_handler_list` is protected by `acpi_gbl_gpe_lock` during dispatch and teardown. `acpi_sci_count` is a runtime diagnostic counter. Removal drains the list by freeing each `struct acpi_sci_handler_info`; no persistent table or firmware state is updated here.

## Dependencies And Integration Points
The file depends on OS services for interrupt registration/removal and locks, ACPICA event detection in `acevents.h`, and FADT state. It is compiled out under `ACPI_REDUCED_HARDWARE`, matching platforms where legacy ACPI event hardware is absent.

## Risks
Host SCI handlers run at interrupt level while the GPE lock is held, so callbacks must be short, nonblocking, and careful about lock ordering. Removing handlers while interrupts are active depends on OS interrupt removal semantics. A stale or malformed GPE interrupt context would affect GPE detection for every SCI.

## Test Signals
Useful signals include successful SCI registration/removal, fixed-event dispatch after status bits are set, GPE dispatch from SCI and non-SCI GPE interrupt paths, host SCI callback ordering, no callback after removal, and correct no-op behavior in reduced-hardware builds.
