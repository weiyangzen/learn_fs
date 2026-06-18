# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-api.h

## Purpose
Defines the packed firmware API data structures and enums used by the MxL862xx host command layer and main DSA driver.

## Important APIs, Types, and Functions
Major ABI groups include `mdio_relay_data`, direct register modification, MAC table add/remove/read/query/clear, bridge allocation/config, bridge-port allocation/config, QoS meter config, extended VLAN filter/treatment/allocation/config, VLAN filter allocation/config, special tag settings, CTP/logical port assignment, STP port config, firmware version, port type enums, and RMON counters. Fields use `__le16`, `__le32`, `__le64`, and `__packed`.

## Control Flow and State
No executable control flow. The header describes command payloads exchanged with firmware. Persistent switch state represented here includes learned/static MAC entries, allocated bridge and bridge-port IDs, VLAN block IDs, meter IDs, port maps, special tag modes, STP states, and hardware counters.

## Dependencies and Integration Points
Depends on kernel bit macros and Ethernet address length. It pairs with command IDs in `mxl862xx-cmd.h` and transport in `mxl862xx-host.c`; higher-level `mxl862xx.o` fills these structures before calling `mxl862xx_api_wrap`.

## Risks and Test Signals
Risks are ABI packing/alignment mistakes, endian conversion omissions, firmware-version drift, invalid block/handle lifecycle, and large structures exceeding transport limits. Test signals include `pahole`/sizeof checks against firmware ABI, command round trips for each structure family, VLAN/bridge/FDB behavior, and RMON counter sanity.
