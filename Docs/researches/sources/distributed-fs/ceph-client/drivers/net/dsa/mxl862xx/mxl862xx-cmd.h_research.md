# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-cmd.h

## Purpose
Defines MxL862xx firmware command IDs and MMD register window constants for host-to-firmware API calls.

## Important APIs, Types, and Functions
Constants describe MMD device/register layout (`CTRL`, `LEN_RET`, data register range), API command namespace "magic" bases, common config/register-mod commands, bridge/bridge-port/CTP/QoS/RMON/MAC/extended-VLAN/VLAN-filter/special-tag/STP commands, internal GPY read/write commands, firmware version command, and `MMD_API_MAXIMUM_ID`.

## Control Flow and State
No runtime logic. The constants are the command ABI consumed by `mxl862xx_api_wrap` callers and interpreted by firmware. The data window size constrains payload batching in `mxl862xx-host.c`.

## Dependencies and Integration Points
Used with payload structures from `mxl862xx-api.h` and the MDIO transport in `mxl862xx-host.c`. Main driver code maps DSA operations to these command IDs.

## Risks and Test Signals
Risks include duplicated register constants drifting from `mxl862xx-host.c`, wrong command IDs invoking unintended firmware operations, and namespace collisions. Test signals are command-specific integration tests, firmware version reads, FDB/VLAN/bridge setup, and static checks that transport constants remain consistent.
