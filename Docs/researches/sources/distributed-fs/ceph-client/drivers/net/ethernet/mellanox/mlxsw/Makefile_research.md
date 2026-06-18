# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/Makefile

## Purpose
`mlxsw/Makefile` defines object composition for the Mellanox switch core, bus drivers, Spectrum switch driver, and minimal I2C driver.

## Important APIs, Types, and Functions
It builds `mlxsw_core.o` from core, ACL, environment, and linecard objects plus optional HWMON/thermal objects. It builds `mlxsw_pci.o`, `mlxsw_i2c.o`, `mlxsw_spectrum.o` from a broad list of switchdev/router/ACL/KVDL/MR/qdisc/span/NVE/dpipe/trap/ethtool/policer/PGT/port-range objects, optional DCB and PTP objects, and `mlxsw_minimal.o`.

## Control Flow and State
There is no runtime flow, but link composition defines feature availability inside each module. Optional object additions follow Kconfig symbols, so enabling DCB/PTP pulls corresponding Spectrum objects.

## Dependencies and Integration Points
The Makefile consumes the Kconfig symbols and integrates all mlxsw implementation files with the kernel build system.

## Risks and Test Signals
Risks include omitted source files, stale object names, wrong optional-object guards, and link-order issues for shared symbols. Test signals are module and built-in builds across core-only, PCI/I2C, Spectrum with/without DCB/PTP, and minimal driver configurations.
