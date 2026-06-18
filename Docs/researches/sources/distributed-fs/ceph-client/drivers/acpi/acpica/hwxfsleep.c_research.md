<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwxfsleep.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwxfsleep.c

## Purpose
Implements exported ACPI sleep/wake orchestration APIs above the legacy and extended hardware backends. It sets firmware waking vectors, handles S4BIOS, prepares sleep by evaluating control methods, dispatches sleep entry, and dispatches wake cleanup.

## Important APIs, Types, And Functions
Exports `acpi_set_firmware_waking_vector`, `acpi_enter_sleep_state_s4bios`, `acpi_enter_sleep_state_prep`, `acpi_enter_sleep_state`, `acpi_leave_sleep_state_prep`, and `acpi_leave_sleep_state`. Internal helper `acpi_hw_set_firmware_waking_vector` updates FACS wake vector fields.

## Control Flow
Wake vector setup writes the 32-bit FACS vector and conditionally writes or clears the 64-bit vector based on FACS length/version. S4BIOS clears wake/status state, disables GPEs, enables wake GPEs, writes the FADT SMI command request, and polls wake status. Sleep prep obtains target sleep types and S0 sleep types, runs `_PTS`, maps the target sleep state to `_SST`, and invokes `_SST`. Sleep entry validates cached sleep type bounds, then chooses legacy or extended sleep based on reduced-hardware state. Wake prep and final wake similarly dispatch to legacy or extended backend functions.

## State And Persistence
Mutates FACS wake vector fields, global sleep type caches, global awake/running state via backend calls, and platform firmware-visible PM/GPE state. Sleep prep state persists only until entry or wake clears/invalidates it.

## Dependencies And Integration Points
Connects public ACPICA sleep APIs to FACS, FADT SMI fields, namespace methods `_PTS` and `_SST`, legacy sleep in `hwsleep.c`, and extended sleep in reduced-hardware support.

## Risks And Edge Cases
Firmware wake vector handling is compatibility-sensitive, especially systems that fail with 64-bit vectors. Calling entry without successful prep leaves invalid sleep types and returns operand errors. S4BIOS polling can hang if wake status never appears. Optional `_PTS`/`_SST` behavior must distinguish `AE_NOT_FOUND` from real failures.

## Test Signals
Suspend/resume paths for legacy and reduced-hardware systems, FACS vector inspection, S4BIOS request tests, invalid sleep type cache tests, `_PTS` failure propagation, optional `_SST` absence, and backend dispatch under `acpi_gbl_reduced_hardware`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwxfsleep.c -->
