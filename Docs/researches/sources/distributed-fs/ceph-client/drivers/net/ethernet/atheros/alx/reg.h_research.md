# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/reg.h

## Purpose
`reg.h` is the register map and bitfield contract for the newer `alx` Atheros/Qualcomm Ethernet driver family. It contains no executable code; its job is to give the driver stable names for PCI device IDs, PCIe capability registers, MAC/DMA/RX/TX queue registers, interrupt bits, Wake-on-LAN controls, RSS/MSI tables, MIB counters, and PHY/MDIO debug and extension registers.

## Important APIs, types, and definitions
The file exports preprocessor constants only. Key groups are `ALX_DEV_ID_*` device IDs, revision constants, PCIe power-management fields such as `ALX_PMCTRL_*`, MAC/DMA reset fields such as `ALX_MASTER_DMA_MAC_RST`, MDIO access fields such as `ALX_MDIO_*` and `ALX_MDIO_EXTN_*`, descriptor queue address/index registers such as `ALX_RFD_ADDR_LO`, `ALX_RRD_ADDR_LO`, `ALX_TPD_PRI*_PIDX`, MAC configuration bits in `ALX_MAC_CTRL_*`, interrupt bits in `ALX_ISR_*`, and MIB offsets under `ALX_MIB_*`.

The PHY section defines standard and vendor-specific MII addresses, including `ALX_MII_GIGA_PSSR` for resolved speed/duplex, debug registers such as `ALX_MIIDBG_*`, and MMD extension register names under `ALX_MIIEXT_*`. These definitions are consumed by low-level MDIO routines, link setup code, power-saving code, stats collection, and WoL programming in the `alx` driver.

## Control flow and state behavior
There is no runtime control flow. The state modeled here is hardware state: MMIO registers, producer/consumer indices, interrupt state, MAC/PHY power modes, and MIB counters. Persistence is in hardware registers and nonvolatile EEPROM/eFuse areas addressed through the named load and MDIO registers. Driver correctness depends on using these masks consistently with read-modify-write operations, because many fields share registers with unrelated hardware controls.

## Dependencies and integration points
This header depends on kernel bit macros such as `BIT()` being available from includers. It is an integration point between the `alx` driver and the Atheros hardware specification. Important external consumers are PCI probe tables, reset sequencing, MAC start/stop, NAPI queue setup, interrupt handling, ethtool stats/register dumps, PHY tuning, WoL, RSS, and MSI/MSI-X setup.

## Risks
The main risks are semantic drift and bitfield mistakes. A wrong mask or offset can silently program link power management, DMA, interrupt, or queue registers incorrectly. Register names also encode hardware-generation quirks, for example B0/C0 WoL and heartbeat fields; using a field on the wrong revision can cause suspend/resume, wake, or link instability. Since constants are not type checked, test coverage must come from compile coverage plus hardware behavior.

## Test signals
Useful signals include successful build of the `alx` driver, probe on all listed PCI IDs, stable link negotiation at 10/100/1000 speeds, clean suspend/resume with and without WoL, ethtool register dump sanity, correct MIB counter increments, RX/TX traffic under interrupt moderation, and no MDIO timeouts during PHY access.
