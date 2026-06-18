
# sources/distributed-fs/ceph-client/drivers/soc/lantiq/fpi-bus.c

## Purpose
Lantiq XRX200 FPI bus driver. It configures RCU AHB endianness, disables FPI burst on the xbar, and populates child devices under the FPI bus node.

## Important APIs, Types, and Functions
- `ltq_fpi_probe()` performs all runtime work.
- OF match is `lantiq,xrx200-fpi`.
- Register constants cover xbar burst control and RCU big-endian AHB bit.

## Control Flow
Probe maps xbar resource 0, obtains RCU regmap from `lantiq,rcu` phandle, reads `lantiq,offset-endianness`, sets `RCU_VR9_BE_AHB1S`, disables FPI burst with `ltq_w32_mask()`, and calls `of_platform_populate()` for child nodes.

## State and Persistence
No private state. RCU/xbar register changes persist until reset or reconfiguration. Child platform devices persist while parent remains.

## Dependencies and Integration Points
Depends on Lantiq SoC accessors, syscon/regmap, OF properties, platform resources, and child devices on the FPI bus.

## Risks
Comment says RCU configuration is optional, but `syscon_regmap_lookup_by_phandle()` errors are returned, making it required in practice. Endianness and burst settings are platform-global and can affect all bus children.

## Test Signals
Probe with valid DT, missing RCU phandle, missing offset property, regmap update failure, xbar register write verification, and child population.
