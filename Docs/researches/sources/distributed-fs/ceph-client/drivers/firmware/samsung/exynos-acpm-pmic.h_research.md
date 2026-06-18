# sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-pmic.h

## Purpose
This private header declares ACPM PMIC helper functions used when wiring the public ACPM protocol ops.

## Important APIs
It declares single-register read/write/update and bulk read/write helpers, all taking `struct acpm_handle *`, ACPM channel ID, PMIC type/register/channel addressing, and operation-specific buffers or values.

## Control Flow And Integration
`exynos-acpm.c` assigns these helpers to `acpm->handle.ops.pmic_ops`, allowing public ACPM clients to perform PMIC operations without depending on this private header.

## State And Persistence
No state is stored here; implementation functions alter firmware/PMIC state.

## Risks
Callers inside the composite object must pass valid buffers and respect the implementation's eight-byte bulk limit.

## Test Signals
Build and ops-table setup validate the header. Runtime PMIC client operations validate the implementation behind these prototypes.
