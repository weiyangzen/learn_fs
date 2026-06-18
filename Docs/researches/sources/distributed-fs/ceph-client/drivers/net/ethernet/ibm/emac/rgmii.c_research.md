
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/rgmii.c

## Purpose
`rgmii.c` implements the platform driver for IBM EMAC RGMII bridge blocks. It configures bridge inputs for RGMII/RTBI/TBI/GMII/MII modes, updates speed-select registers on link changes, optionally gates MDIO access through the selected input, and supports ethtool register dumps.

## Important APIs, Types, and Functions
Public functions are `rgmii_attach()`, `rgmii_detach()`, `rgmii_get_mdio()`, `rgmii_put_mdio()`, `rgmii_set_speed()`, `rgmii_get_regs_len()`, `rgmii_dump_regs()`, `rgmii_init()`, and `rgmii_exit()`. Internal helpers `rgmii_valid_mode()` and `rgmii_mode_mask()` validate interface modes and compute FER bits. Probe maps the bridge registers, sets `EMAC_RGMII_FLAG_HAS_MDIO` from `has-mdio` or Axon compatibility, disables all inputs, and publishes drvdata.

## Control Flow
EMAC probe calls `rgmii_attach()` after dependency resolution. Attach validates the requested input and PHY mode, sets the input’s function-enable bits, increments users, and logs mode. During EMAC configuration, `rgmii_set_speed()` rewrites the input’s SSR speed bits for 10/100/1000. During MDIO transactions, EMAC calls `rgmii_get_mdio()` before STACR access and `rgmii_put_mdio()` afterward; when MDIO gating is supported, the functions lock the bridge, set/clear the MDIO select bit, and serialize access. Detach clears FER bits and decrements users.

## State and Persistence
State is in `struct rgmii_instance`: mapped registers, flags, mutex, user count, and platform device. Hardware state is the FER/SSR register pair. There is no persistent state.

## Dependencies and Integration Points
The file depends on OF platform probing, MMIO access, PHY mode constants, `emac_ethtool_regs_subhdr`, and EMAC core calls. Device-tree compatibles include `ibm,rgmii`, legacy `emac-rgmii`, and `ibm,rgmii-axon` fixups.

## Risks
MDIO locking is split across get/put, so every caller must pair calls exactly. Unsupported modes fail attach except MII is mapped to GMII bits. User count is protected by a mutex but only checked by `BUG_ON()` at detach. Axon behavior has a FIXME indicating possible register-bit mismatch.

## Test Signals
RGMII probe logs, attach logs with correct PHY mode, link-speed changes updating SSR, successful MDIO reads through RGMII, ethtool register dumps, and attach/detach balancing during EMAC probe/remove are useful signals. Axon hardware needs specific validation.
