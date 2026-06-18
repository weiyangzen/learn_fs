<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/idma64.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/idma64.h

## Purpose
Provides the platform driver name constant for Intel LPSS iDMA64.

## Important APIs, Types, And Functions
Defines `LPSS_IDMA64_DRIVER_NAME` as `"idma64"`.

## Control Flow
No runtime control flow. Platform or ACPI glue can use the constant to register or match the iDMA64 driver name.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Integrates Intel LPSS platform code and the iDMA64 DMAengine driver through a shared string constant.

## Risks And Edge Cases
Changing the string would break driver binding for consumers that depend on the exact name.

## Test Signals
Build coverage and platform-driver binding tests for LPSS iDMA64 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/idma64.h -->
