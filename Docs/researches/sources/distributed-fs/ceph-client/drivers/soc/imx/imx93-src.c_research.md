
# sources/distributed-fs/ceph-client/drivers/soc/imx/imx93-src.c

## Purpose
Minimal i.MX93 SRC platform driver that populates child devices under the SRC node.

## Important APIs, Types, and Functions
- `imx93_src_probe()` calls `devm_of_platform_populate()`.
- OF match table contains `fsl,imx93-src`.

## Control Flow
On matching platform probe, children of the SRC node are populated with devm cleanup.

## State and Persistence
No private state. Child platform devices persist while the parent device is bound.

## Dependencies and Integration Points
Depends on OF platform population and DT child nodes for SRC-controlled subdevices.

## Risks
Failure to populate children blocks downstream devices. The driver has no remove hook because devm handles child cleanup.

## Test Signals
Probe with matching DT, child device creation, missing/invalid children no-op behavior, and module unload cleanup.
