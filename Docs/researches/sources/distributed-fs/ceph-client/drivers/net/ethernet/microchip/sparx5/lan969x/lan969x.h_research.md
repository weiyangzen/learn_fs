# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x.h

## Purpose
This header declares the LAN969x family interface used by the shared Sparx5 driver and LAN969x implementation files. It exposes descriptor data, generated register/VCAP tables, family-specific ops, and inline port classification helpers.

## Important APIs, Types, And Functions
Exports include `lan969x_desc`, `lan969x_vcap_stats`, `lan969x_vcaps`, `lan969x_vcap_inst_cfg`, generated register arrays, `lan969x_dsm_calendar_calc()`, `lan969x_port_config_rgmii()`, and LAN969x FDMA functions. Inline helpers classify port numbers as 2.5G, 5G, 10G, 25G, or RGMII.

## Control Flow
The header has no runtime control flow by itself. It lets `lan969x.c` populate `sparx5_ops` and lets common Sparx5 code call LAN969x-specific implementations through those hooks.

## State And Persistence
There is no storage here. The inline classification functions encode static hardware topology in code.

## Dependencies And Integration Points
It includes common Sparx5 main, register, and VCAP implementation headers. It is the local contract between generated LAN969x tables, family glue, RGMII, calendar, FDMA, and common driver code.

## Risks And Edge Cases
Hard-coded port classification is an ABI with the hardware. `lan969x_port_is_25g()` always returns false, so common code must not infer 25G support for this family. Header include paths reach through `../sparx5/`, so directory moves can break includes.

## Test Signals
Build with `CONFIG_LAN969X_SWITCH`, verify all externs resolve, and test port mode decisions for every physical port number, especially RGMII ports 28 and 29 and 10G ports 24-27.
