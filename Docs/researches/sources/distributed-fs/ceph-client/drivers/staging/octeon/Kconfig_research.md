# sources/distributed-fs/ceph-client/drivers/staging/octeon/Kconfig

## Purpose
Kconfig entry for the Cavium Networks Octeon on-board Ethernet driver.

## Important APIs, Types, And Functions
Defines `OCTEON_ETHERNET` as tristate, depends on `CAVIUM_OCTEON_SOC || COMPILE_TEST` and `NETDEVICES`, and selects `PHYLIB` and `MDIO_OCTEON`.

## Control Flow
Selecting the option builds the multi-file `octeon-ethernet` driver and ensures PHY/MDIO support is available.

## State And Persistence
No runtime state. The symbol persists in the kernel configuration.

## Dependencies And Integration Points
Connects the staging Ethernet driver to Octeon SoC support, netdev core, PHY library, and Cavium MDIO driver.

## Risks
`COMPILE_TEST` is supported through local stubs but real operation requires Octeon hardware and SDK-style CSR helpers. The driver covers older CN3XXX/CN5XXX-era hardware.

## Test Signals
Build under Octeon defconfig, build under `COMPILE_TEST`, dependency selection of `MDIO_OCTEON`, and module name `octeon-ethernet`.
