<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ishtp_eclite.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ishtp_eclite.c

## Purpose
ISHTP client driver that exposes ACPI OpRegion handlers for ECLite firmware running on Intel ISH/PSE. It lets AML read/write ECLite data and invoke DSM events for battery, thermal, fan, UCSI, and related platform functions.

## Important APIs, Types, And Functions
`struct ishtp_opregion_dev` stores opregion buffers, ISHTP client handles, ACPI device reference, flags, waitqueue, work items, and lock. `ecl_opregion_cmd_handler()` triggers ISH read/write commands from ACPI command-region writes. `ecl_opregion_data_handler()` reads/writes the shared 384-byte data region. `ecl_ish_cl_read()` sends a read header and waits up to 2 seconds for firmware response. RX callbacks distinguish data responses from event messages; events schedule `_DSM` calls.

## Control Flow
Late init registers an ISHTP client for ECLite UUID. Probe allocates and connects an ISHTP client, finds ACPI device `INTC1035`, registers event callback, installs command and data OpRegion handlers, then clears ACPI dependencies. ACPI writes command fields; writing the command offset sends ISHTP messages. Firmware data responses fill the opregion buffer and wake waiters. Firmware events schedule `ecl_acpi_invoke_dsm()`. Reset work tears down/recreates the ISHTP client and reinstalls opregions if needed.

## State And Persistence
State includes opregion command/data buffers, link readiness, read completion flag, installed-handler flag, DSM event id, and pending work. Suspend to Sx removes opregions and disables firmware events; resume relies on a later reset path.

## Dependencies And Integration Points
Depends on ISHTP client APIs, ACPI address-space handlers, ACPI DSM GUID, waitqueues, workqueues, and suspend state. Firmware and AML must agree on opregion IDs `0x9e` and `0x9f`.

## Risks And Test Signals
Risks include ISHTP reset races, blocking ACPI reads waiting on firmware, missing event disable errors, bitfield message layout, and handler removal during suspend. Test ACPI OpRegion read/write methods, firmware event-to-DSM path, reset recovery, suspend/resume, dependency reprobe of ECLite consumers, and malformed offsets/lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ishtp_eclite.c -->
