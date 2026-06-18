# sources/distributed-fs/ceph-client/drivers/power/reset/piix4-poweroff.c

## Purpose
Intel PIIX4 PCI southbridge poweroff driver, mainly for MIPS Malta-like systems.

## Important APIs, Types, and Functions
global `pm_dev` and `io_offset`, ACPI PM I/O register enum, PCI probe/remove, and `piix4_poweroff()`.

## Control Flow
probe enables the PCI PM I/O BAR, stores offset, and installs `pm_power_off`; callback programs PMCNTRL for SOff/S5-like state using I/O port accesses.

## State and Persistence Behavior
global PCI device reference, I/O offset, and poweroff hook persist until remove; PM control register state persists for final poweroff.

## Dependencies and Integration Points
PCI core, HAS_IOPORT, MIPS/compile-test, legacy global poweroff.

## Risks and Edge Cases
global singleton; platform-specific ACPI PM semantics; I/O BAR decoding must be enabled; remove must clear hook only when owning it.

## Test Signals
PIIX4 PCI ID probe, I/O resource enable failure, poweroff on Malta, and remove/reprobe.
