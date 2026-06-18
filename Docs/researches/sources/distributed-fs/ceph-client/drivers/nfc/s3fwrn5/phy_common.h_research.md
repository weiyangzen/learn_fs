# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/phy_common.h

## Purpose
`phy_common.h` declares the shared S3FWRN5 physical-layer state and GPIO helper API.

## Important APIs and types
- `S3FWRN5_EN_WAIT_TIME` defines the 20 ms wait used during enable/wake sequencing.
- `struct phy_common` stores the NCI device pointer, enable GPIO, firmware-wake GPIO, mutex, and current S3FWRN5 mode.
- Function prototypes expose wake, power control, mode set, and mode get helpers.

## Control flow and integration
Transport drivers embed `struct phy_common` as their first/common member and pass it directly to helper operations via `phy_id`. The shared core uses these helpers indirectly through `struct s3fwrn5_phy_ops`.

## State, dependencies, and risks
The header depends on GPIO descriptors, mutexes, NCI core types, and `s3fwrn5.h`. The risk is structural coupling: helper implementations cast `void *phy_id` to `struct phy_common *`, so embeddings must keep the common object address compatible with what they pass.

## Test signals
Compile tests for both I2C and UART transports, plus runtime tests of mode/wake paths, provide coverage for this contract.
