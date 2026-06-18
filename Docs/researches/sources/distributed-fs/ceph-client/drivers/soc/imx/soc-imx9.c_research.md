
# sources/distributed-fs/ceph-client/drivers/soc/imx/soc-imx9.c

## Purpose
i.MX9 SoC identity driver. It uses an ARM SMCCC call to firmware to retrieve SoC id, revision, and 128-bit UID, then registers a SoC bus device for i.MX93/i.MX94/i.MX95/i.MX952 machines.

## Important APIs, Types, and Functions
- `imx9_soc_probe()` performs SMCCC query and SoC registration.
- `imx9_soc_init()` registers a platform driver and simple platform device at `device_initcall()`.
- Macros decode SoC ID and revision from `res.a1`.

## Control Flow
Init returns unless the OF machine is a supported i.MX9 compatible. It registers the driver and simple platform device. Probe reads root machine, sets family, calls `arm_smccc_smc(IMX_SIP_GET_SOC_INFO)`, checks success, decodes id/revision, formats serial from `a2/a3`, and registers the SoC device.

## State and Persistence
Registers a SoC device with devm-allocated strings. No private long-lived state beyond the registered SoC bus object. UID/revision are firmware-provided.

## Dependencies and Integration Points
Requires ARM SMCCC firmware service, OF machine compatible, platform bus, and SoC bus core.

## Risks
- Failure or absence of the SMCCC service fails probe.
- Revision macro subtracts `0x9` from encoded major; unexpected firmware encodings can produce surprising values.
- No remove/unregister hook is present for registered SoC device.

## Test Signals
Supported compatible matching, SMCCC success/failure, SoC ID decoding for each supported family, UID formatting, missing model property failure, and SoC bus attribute verification.
