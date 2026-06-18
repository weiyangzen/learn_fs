# sources/distributed-fs/ceph-client/drivers/acpi/acpi_adxl.c

## Purpose
`acpi_adxl.c` implements the ACPI ADXL address-translation interface via `_DSM` calls on `\_SB.ADXL`. It exposes memory-address component names and decodes a system physical address into platform topology component values.

## Important APIs, Types, And Functions
Important constants are `ADXL_REVISION`, `ADXL_IDX_GET_ADDR_PARAMS`, `ADXL_IDX_FORWARD_TRANSLATE`, `ACPI_ADXL_PATH`, and `ADXL_MAX_COMPONENTS`. Exported APIs are `adxl_get_component_names()` and `adxl_decode()`. Internal state includes the ACPI `handle`, retained `_DSM` `params`, `adxl_count`, `adxl_component_names`, and the ADXL GUID. `adxl_dsm()` validates the two-element DSM response package.

## Control Flow
`adxl_init()` finds `\_SB.ADXL`, verifies `_DSM`, checks both required function bits, evaluates the parameter-name DSM, validates a bounded component count, allocates a NULL-terminated string pointer array, and points entries at the retained ACPI object strings. `adxl_decode()` builds a one-element package containing the address, calls the forward-translate DSM, requires the returned package count to match `adxl_count`, copies integer values into the caller-provided array, and frees the result object.

## State And Persistence
ADXL component metadata is retained for the lifetime of the kernel after `subsys_initcall()`. There is no cleanup path because this is built-in ACPI support. The decoded values are per-call outputs only.

## Dependencies And Integration Points
It depends on ACPI DSM helpers and exports the ADXL API declared by `<linux/adxl.h>` for memory error reporting or platform topology consumers. The source references Intel's ADXL specification by URL in comments.

## Risks
`adxl_component_names` points into the retained `params` ACPI object, so freeing `params` would invalidate exported names. `adxl_decode()` assumes returned elements are integers and does not validate each element type. Firmware-provided component counts are bounded, but callers must allocate enough `u64` slots according to the name list.

## Test Signals
Validation should exercise absent ADXL, missing `_DSM`, unsupported DSM bits, excessive component counts, mismatched decode result counts, and successful decode with undefined components represented as `~0ull`.
