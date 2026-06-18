# sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/Kconfig

## Purpose
`davicom/Kconfig` exposes Davicom Ethernet driver configuration options for DM9000 parallel-bus and DM9051 SPI Ethernet controllers.

## Important APIs, types, and functions
- `NET_VENDOR_DAVICOM` is the vendor menu gate boolean defaulting to `y`.
- `DM9000` is a tristate driver option depending on `ARM || MIPS || COLDFIRE || NIOS2 || COMPILE_TEST`, selecting `CRC32` and `MII`.
- `DM9000_FORCE_SIMPLE_PHY_POLL` is a boolean under `DM9000` that forces NSR LinkStatus polling instead of MII PHY reads.
- `DM9051` is a tristate SPI driver option depending on `SPI`, selecting `CRC32`, `MDIO`, `PHYLIB`, and `REGMAP_SPI`.

## Control flow and state
Kconfig symbols determine whether `dm9000.o` and `dm9051.o` are built. The simple PHY polling option changes DM9000 runtime link-detection behavior at compile time.

## Dependencies and integration points
This file integrates Davicom drivers with architecture, SPI, MDIO/PHYLIB, MII, regmap, and CRC32 subsystems. Build output is wired by the Davicom Makefile.

## Risks and test signals
Risks include insufficient dependencies for buildability and compile-time PHY polling option misuse on external PHY designs. Test signals are allmodconfig/COMPILE_TEST builds, architecture-specific DM9000 builds, SPI DM9051 module builds, and link detection validation with and without simple polling.
