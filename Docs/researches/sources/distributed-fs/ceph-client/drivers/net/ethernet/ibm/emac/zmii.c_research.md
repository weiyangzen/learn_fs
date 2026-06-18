
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/zmii.c

## Purpose
`zmii.c` implements the IBM EMAC ZMII bridge platform driver. ZMII bridges connect EMAC inputs to MII/RMII/SMII modes, select MDIO routing, update speed bits, and expose bridge registers for ethtool dumps.

## Important APIs, Types, and Functions
Public functions are `zmii_attach()`, `zmii_detach()`, `zmii_get_mdio()`, `zmii_put_mdio()`, `zmii_set_speed()`, `zmii_get_regs_len()`, `zmii_dump_regs()`, `zmii_init()`, and `zmii_exit()`. Helpers `zmii_valid_mode()`, `zmii_mode_name()`, and `zmii_mode_mask()` validate and encode PHY interface modes. `zmii_probe()` maps registers, saves firmware FER for autodetection, clears FER, initializes the mutex, and publishes drvdata.

## Control Flow
EMAC probe calls `zmii_attach()` when a ZMII phandle is configured. Attach permits invalid modes as a non-fatal case for EMACs that may only need ZMII for MDIO, otherwise it autodetects bridge mode from saved firmware FER when no PHY mode is specified, enforces a single mode for all inputs, writes FER bits for the selected input, and increments users. EMAC MDIO transactions call get/put to lock the bridge and route MDIO to one input. Link configuration calls `zmii_set_speed()` to set or clear the 100M speed bit. Detach clears the input mode bit and decrements users.

## State and Persistence
`struct zmii_instance` holds base registers, mutex, selected mode, user count, saved firmware FER, and platform device. Hardware state is FER/SSR/SMIIRS. No disk state exists.

## Dependencies and Integration Points
The file depends on OF platform probing, MMIO, PHY interface constants, and EMAC core ethtool framing. Device-tree compatible strings include `ibm,zmii` and legacy `emac-zmii`.

## Risks
Autodetection from firmware FER is a backward-compatibility fallback and may mis-detect boards without explicit PHY mode. All attached inputs must share a single ZMII mode. MDIO locking spans get/put and requires strict pairing. Attach increments users even when mode is invalid but tolerated for MDIO-only use, making detach behavior dependent on caller consistency.

## Test Signals
Probe logs, bridge mode logs, explicit and autodetected PHY modes, MDIO reads routed through ZMII, 10/100 speed changes, ethtool register dumps, and attach/detach balancing are primary validation points.
