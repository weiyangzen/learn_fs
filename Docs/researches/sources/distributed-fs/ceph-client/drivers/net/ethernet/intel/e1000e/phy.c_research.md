# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/phy.c

## Purpose
`phy.c` is the e1000e copper PHY service layer. It hides MDIO/Kumeran/HV/BM page-access details behind the PHY operation callbacks used by the e1000e MAC-specific code, and it owns most link setup, autonegotiation, forced speed/duplex, power-state, polarity, cable-length, reset, and PHY identification behavior for M88, IGP, IFE, BM, 82577/82578/82579, and related Intel PHYs.

## Important APIs, types, and functions
The exported functions populate the `struct e1000_phy_operations` style call sites declared in `phy.h`: MDIC access (`e1000e_read_phy_reg_mdic`, `e1000e_write_phy_reg_mdic`), per-PHY wrappers (`*_m88`, `*_igp`, `*_bm`, `*_bm2`, `*_hv`), Kumeran access (`e1000e_read_kmrn_reg*`, `e1000e_write_kmrn_reg*`), link setup (`e1000e_copper_link_setup_m88`, `e1000e_copper_link_setup_igp`, `e1000_copper_link_setup_82577`, `e1000e_setup_copper_link`), forced mode helpers (`e1000e_phy_force_speed_duplex_setup` and per-PHY force functions), state queries (`e1000e_get_phy_info_*`, polarity checks, downshift checks, cable length helpers), reset helpers, wake-register access, and `e1000e_determine_phy_address`. Static helpers cover autoneg wait/setup, BM/HV page routing, wake-register opcode access, and HV debug registers.

## Control flow
Normal copper bring-up runs through per-family setup, then `e1000e_setup_copper_link`. If `hw->mac.autoneg` is set, `e1000_copper_link_autoneg` masks `phy->autoneg_advertised` by `autoneg_mask`, programs MII advertisement and flow-control bits, restarts autoneg, optionally waits, and marks `mac.get_link_status`. If forced mode is requested, the selected `phy->ops.force_speed_duplex` updates both PHY BMCR and MAC CTRL state. Link status is then polled with sticky-safe double reads of `MII_BMSR`; when up, MAC collision distance and flow-control reconciliation run.

Register access flow depends on PHY family. M88 uses direct MDIC after semaphore acquisition. IGP selects `IGP01E1000_PHY_PAGE_SELECT` for high offsets. BM and HV encode page/register in synthetic offsets, choose PHY address 1 or 2, select pages, and special-case wake page 800 through address/data opcodes. HV pages below `HV_INTC_FC_PAGE_START` use vendor debug address/data ports.

## State and persistence behavior
This file mutates persistent driver state in `hw->phy` (`id`, `revision`, `type`, `addr`, `retry_enabled`, `speed_downgraded`, cable metrics, polarity, MDI-X, receiver status, original master/slave mode), `hw->mac` (`get_link_status`, forced speed/duplex effects), and `hw->fc.current_mode`. Hardware state persists in PHY pages, MDIC registers, Kumeran registers, `CTRL`, `PHY_CTRL`, wake-control bits, and power-down/LPLU settings. Semaphore callbacks bracket most MDIO operations; locked variants assume the caller already owns that synchronization.

## Dependencies and integration points
The implementation depends on `e1000.h` for `struct e1000_hw`, `er32`/`ew32`, `e1e_rphy`/`e1e_wphy`, error codes, MAC/PHY enums, and flow-control helpers. Linux MII constants and `FIELD_GET`/`FIELD_PREP` drive register bit extraction. MAC-specific files install these functions into operation tables and call them during probe, reset, open, suspend/resume, link change, ethtool diagnostics, and WoL setup.

## Risks
The major risks are hardware sequencing and concurrency. Page selection and `hw->phy.addr` are mutable global PHY access state, so missing semaphore coverage or incorrect use of locked variants can send MDIO transactions to the wrong page/address. Some status registers are sticky and require double reads; removing those reads can create false link states. BM wake-register access temporarily modifies wake enable bits and must restore them on all paths. Forced speed changes intentionally disable flow control and rewrite MAC CTRL; regressions can break half-duplex, MDI/MDIX, or autoneg behavior. Several paths return success when reset is blocked, which is intentional but easy to misread.

## Test signals
Useful signals include successful probe PHY ID/type detection, link-up/down across autoneg and forced 10/100/1000 modes, MDI/MDIX behavior, cable-length/polarity reporting through ethtool, suspend/resume and WoL wake-filter retention, absence of MDIC timeout/debug messages, and no regressions in PCH/BM/HV-specific reset and power-state transitions.
