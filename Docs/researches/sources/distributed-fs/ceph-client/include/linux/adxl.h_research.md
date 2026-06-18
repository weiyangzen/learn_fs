<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adxl.h -->
# sources/distributed-fs/ceph-client/include/linux/adxl.h

## Purpose
`adxl.h` declares an address translation interface backed by ACPI DSM methods.

## Important APIs, types, and functions
`adxl_get_component_names()` returns a NULL-terminated or implementation-defined list of component names. `adxl_decode(u64 addr, u64 component_values[])` decodes an address into component values.

## Control flow
Callers obtain component labels, allocate/pass a values array, and decode physical addresses through platform ACPI DSM logic implemented elsewhere.

## State and persistence behavior
The header has no state. Decoding reflects firmware/platform topology that is persistent for the boot.

## Dependencies and integration points
It integrates ACPI DSM address decoding with memory/RAS/platform diagnostic code.

## Risks and test signals
Risks include array size mismatches between names and values, firmware DSM failures, and callers assuming names are mutable. Test signals include platform decode tests, invalid address handling, and DSM absence behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adxl.h -->
