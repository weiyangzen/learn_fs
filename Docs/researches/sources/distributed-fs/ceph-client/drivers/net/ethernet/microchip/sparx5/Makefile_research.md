# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/Makefile

## Purpose
This Makefile assembles the `sparx5-switch.o` composite object and conditionally adds DCB, debugfs, and LAN969x source files based on Kconfig symbols.

## Important APIs, Types, And Functions
`obj-$(CONFIG_SPARX5_SWITCH) += sparx5-switch.o` declares the module object. `sparx5-switch-y` lists the common Sparx5 implementation: main probing, packet path, netdev, phylink, port, MAC table, VLAN, switchdev, calendar, ethtool, FDMA, PTP, PGID, tc, QoS, VCAP, pools, scheduling, policing, PSFP, mirror, and registers. Conditional fragments add `sparx5_dcb.o`, `sparx5_vcap_debugfs.o`, and LAN969x files. Include paths add Microchip VCAP and FDMA headers.

## Control Flow
There is no runtime flow. Build-time object composition determines which functions and descriptor tables are available to the final driver binary.

## State And Persistence
The file contributes to build system state only. It does not define runtime or persistent state.

## Dependencies And Integration Points
It integrates the Sparx5 directory with Kbuild and with shared include directories under `drivers/net/ethernet/microchip/vcap` and `drivers/net/ethernet/microchip/fdma`. The LAN969x conditional block brings in family descriptors, generated registers, generated VCAP metadata, RGMII support, calendar support, and page-pool FDMA.

## Risks And Edge Cases
The LAN969x code is compiled into the same `sparx5-switch.o`, so missing prototypes or object ordering issues appear as link errors in the shared module. Generated API/register files must stay synchronized with headers used by common code. If `CONFIG_DEBUG_FS` is off, VCAP debugfs-specific symbols must not be referenced unconditionally elsewhere.

## Test Signals
Use kernel build targets for `CONFIG_SPARX5_SWITCH`, `CONFIG_SPARX5_DCB`, `CONFIG_DEBUG_FS`, and `CONFIG_LAN969X_SWITCH` combinations. Link success and absence of undefined VCAP/FDMA/generated-register symbols are the key signals.
