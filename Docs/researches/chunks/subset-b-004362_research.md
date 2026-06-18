# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_link.c lines 1-8682

## Scope

This chunk covers the first 8,682 lines of `bnx2x_link.c`, the Broadcom/QLogic `bnx2x` link-control implementation. It includes common link helpers, ETS/PFC programming, MAC and PBF setup, MDIO/Clause 22/Clause 45 access, EEE handling, internal SerDes/XGXS/Warpcore setup, link interrupt/status update logic, LED control, SFP EEPROM access and validation, and the beginning of external PHY support through BCM8073/8705 and SFP limiting-mode helpers. The file continues after this chunk with the rest of SFP module detection and additional PHY families, so callback tables and some periodic/error paths are cross-chunk dependencies.

## Purpose

This code is the hardware link management layer for `bnx2x`. It translates driver, firmware/shared-memory, DCBX, and PHY configuration into direct register writes across the NIG, PBF, EMAC/BMAC/UMAC/XMAC, internal SerDes/XGXS/Warpcore, and external PHYs. It also samples link state, resolves speed/duplex/flow control, updates MCP-visible shared memory, controls LEDs and SFP transmitters, and enforces SFP module policy.

The chunk is deliberately hardware-specific. Most functions either:

- program register sequences for a specific block or PHY mode;
- reconcile `struct link_params` input into `struct link_vars` output;
- expose a small public API used by `bnx2x_main.c`, `bnx2x_ethtool.c`, and `bnx2x_dcb.c`.

## Important APIs, Types, And Functions

Main data types come from `bnx2x_link.h`:

- `struct link_params`: per-port input and persistent configuration, including requested speed/duplex/flow control arrays, shared-memory bases, chip id, lane and multi-PHY config, feature flags, EEE mode, LED mode, `lfa_base`, `link_attr_sync`, and the populated `phy[MAX_PHYS]` array.
- `struct link_vars`: current resolved output state, including link flags, active MAC type, internal and full link-up booleans, speed/duplex/flow control, `link_status`, `eee_status`, interrupt mask, KR recovery counters, and periodic flags.
- `struct bnx2x_phy`: per-PHY descriptor with type, MDIO address/control, flags, media type, supported capabilities, requested line settings, firmware version address, and behavior callbacks: `config_init`, `read_status`, `link_reset`, `config_loopback`, `hw_reset`, `set_link_led`, and `phy_specific_func`.
- `struct bnx2x_nig_brb_pfc_port_params`: DCB/PFC NIG parameters such as LLFC/PFC enables, priority-to-COS mapping, RX COS masks, and high/low priority classes.
- `struct bnx2x_ets_params`: ETS COS list where each COS is strict priority or bandwidth weighted.

Public or externally integrated functions visible in this chunk:

- `bnx2x_ets_disabled()`, `bnx2x_ets_bw_limit()`, `bnx2x_ets_strict()`, `bnx2x_ets_e3b0_config()`: configure NIG/PBF arbitration for disabled ETS, two-COS bandwidth limits, strict priority, or E3B0 multi-COS ETS.
- `bnx2x_update_pfc()`: updates shared `LINK_STATUS_PFC_ENABLED`, NIG PFC/LLFC controls, and the active MAC's PFC/pause programming.
- `bnx2x_phy_read()` / `bnx2x_phy_write()`: locate a PHY by MDIO address and issue Clause 45 transactions.
- `bnx2x_link_status_update()`: reloads link state from MCP shared memory and synchronizes media type, interrupt mask, PFC flag, EEE status, and link attributes into `params`/`vars`.
- `bnx2x_get_ext_phy_fw_version()`: formats firmware versions from external PHY shared-memory version addresses.
- `bnx2x_set_led()`: updates external PHY LED callbacks plus NIG/EMAC LED control for off/on/operational modes.
- `bnx2x_test_link()`: directly samples internal and external PHY status to report whether the physical link is actually up.
- `bnx2x_link_update()`: interrupt-time link state reconciliation and MAC reconfiguration.
- `bnx2x_ext_phy_hw_reset()`: GPIO reset helper for external PHYs.
- `bnx2x_read_sfp_module_eeprom()`: exported SFP EEPROM reader used by ethtool and internal module detection.

Key private function groups:

- Register helpers: `bnx2x_bits_en()`, `bnx2x_bits_dis()`, `bnx2x_set_cfg_pin()`, `bnx2x_get_cfg_pin()`, EPIO/GPIO wrappers.
- MDIO helpers: `bnx2x_get_emac_base()`, `bnx2x_set_mdio_clk()`, `bnx2x_cl22_read/write()`, `bnx2x_cl45_read/write()`, and read-modify-write wrappers.
- MAC helpers: `bnx2x_emac_init()`, `bnx2x_emac_enable()`, `bnx2x_bmac_enable()`, `bnx2x_umac_enable()`, `bnx2x_xmac_enable()`, `bnx2x_set_xumac_nig()`, `bnx2x_set_xmac_rxtx()`, `bnx2x_set_bmac_rx()`.
- Internal PHY/Warpcore helpers: `bnx2x_xgxs_deassert()`, `bnx2x_prepare_xgxs()`, `bnx2x_xgxs_config_init()`, `bnx2x_warpcore_config_init()`, `bnx2x_warpcore_read_status()`, `bnx2x_link_settings_status()`, lane/AER helpers, KR/KR2/XFI/SFI/SGMII/DXGXS programming routines.
- Link-state helpers: `bnx2x_sync_link()`, `bnx2x_get_link_speed_duplex()`, `bnx2x_flow_ctrl_resolve()`, `bnx2x_ext_phy_resolve_fc()`, `bnx2x_update_link_up()`, `bnx2x_update_link_down()`, `bnx2x_link_int_enable()`, `bnx2x_link_int_ack()`, `bnx2x_rearm_latch_signal()`.
- SFP helpers: transmitter control, PHY-specific EEPROM readers, EDC/limiting-mode selection, module approval, fault LED, and module power.

## Control Flow

Initialization path in this chunk begins with the already populated `link_params` and PHY callback descriptors. `set_phy_vars()` copies requested speed, duplex, flow control, and speed capabilities from `link_params` into each `bnx2x_phy`, respecting swapped external-PHY configurations. `bnx2x_link_initialize()` chooses whether the internal PHY is configured before external PHYs, prepares XGXS where needed, configures direct/internal paths, then invokes external PHY `config_init` callbacks. The complete `bnx2x_phy_init()` wrapper is later in the file outside this chunk, but this chunk contains most of the actual setup it calls.

Link interrupt flow centers on `bnx2x_link_update()`:

1. Clear transient link bits in `vars->link_status` and initialize temporary `phy_vars` for each PHY.
2. Set Warpcore AER if applicable and read NIG interrupt status.
3. Disable EMAC on pre-E3 chips before re-evaluating the link.
4. Iterate external PHYs, calling `read_status()` callbacks and selecting the active external PHY according to `bnx2x_phy_selection()`.
5. Read internal PHY status through its `read_status()` callback.
6. If an external PHY is active, copy its flow control, link-status bits, duplex, EEE status, media type, and line speed into the aggregate `vars`.
7. Rearm latch-style external PHY interrupts where required.
8. Validate that internal and external speeds agree for non-direct boards; if not, force `phy_link_up` down.
9. Acknowledge the appropriate NIG link interrupt line.
10. If an external PHY is up but the internal link is down and the board does not initialize XGXS first, re-run internal PHY config at the external speed.
11. Compute full `vars->link_up` from internal link, external/direct link, and fault status.
12. Update PFC bit, call `bnx2x_update_link_up()` or `bnx2x_update_link_down()`, bump `link_change_count` when supported, and notify firmware for AFEX.

`bnx2x_update_link_up()` selects and enables the MAC based on chip generation and speed. Warpcore chips use XMAC for 10G+ and UMAC below 10G; E1/E2 use BMAC for 10G+ and EMAC below 10G. It also updates LEDs, PBF on E1x, disables NIG drain, writes link and EEE state to shared memory, and performs half-open/remote-fault checks for PHYs with `FLAGS_TX_ERROR_CHECK`. `bnx2x_update_link_down()` clears link bits, turns LEDs off, enables NIG drain, disables active MAC RX/TX paths, clears EEE active bits, and writes shared memory.

Internal PHY control splits by hardware:

- XGXS/SerDes path uses Clause 22-over-Clause 45 banked access, `bnx2x_prepare_xgxs()`, CL37/CL73/BAM advertisement, SGMII setup, forced SerDes speed programming, parallel detection, lane swapping, and preemphasis.
- Warpcore path uses native Clause 45 register sequences. `bnx2x_warpcore_config_init()` branches on NVRAM serdes interface type: SGMII, KR, XFI, SFI, DXGXS, or KR2. It resets the lane, programs mode-specific registers, optionally runs SFP module detection/configuration, and releases the lane reset. Runtime recovery in `bnx2x_warpcore_config_runtime()` periodically resets KR lanes and restarts AN if link does not come up.

SFP flow in this chunk starts with EEPROM access and module classification. `bnx2x_read_sfp_module_eeprom()` dispatches to BCM8726, BCM8727/8722, or direct Warpcore I2C/BSC readers. `bnx2x_get_edc_mode()` reads connector and compliance bytes, classifies passive DAC, active DAC, 1G fiber, 10G optic, or unknown modules, may force `phy->req_line_speed` to 1G for non-10G SFP modules, updates media type in shared memory, reads options to choose linear vs limiting mode, and updates `link_attr_sync` with SFP compatibility code. `bnx2x_verify_sfp_module()` asks firmware to approve the module, logs vendor/part number on rejection, and sets `FLAGS_SFP_NOT_APPROVED` unless policy is warning-only.

## State And Persistence Behavior

The central in-memory state is `struct link_params` plus `struct link_vars`, but the code also persists status into device shared memory consumed by management firmware:

- `bnx2x_update_mng()` writes `port_mb[port].link_status` in `shmem_region`.
- `bnx2x_update_link_attr()` writes `shmem2_region.link_attr_sync[port]` when supported.
- `bnx2x_update_mng_eee()` writes `shmem2_region.eee_status[port]` when the field exists.
- `bnx2x_chng_link_count()` updates `shmem2_region.link_change_count[port]`.
- `bnx2x_link_status_update()` reads shared-memory link status, EEE status, media type, AEU mask, and link attributes back into the driver.
- SFP media type updates rewrite `dev_info.port_hw_config[port].media_type` so non-PMF functions can observe module classification.

`link_vars` is reset and rebuilt frequently. Link-up bits, speed/duplex, flow-control flags, MAC type, EEE active/LP advertisement bits, and half-open/fault flags are recalculated from PHY status reads and persisted back to shared memory. Some counters and toggles survive across calls in `vars`, including `rx_tx_asic_rst`, `turn_to_run_wc_rt`, and `check_kr2_recovery_cnt`.

Hardware state is persistent until reset or reprogramming. This chunk writes many NIG/PBF/MAC/PHY registers directly, including reset controls, interrupt masks/status latches, PFC/ETS arbitration registers, MDIO mode, MAC enable bits, Warpcore firmware mode, SFP power/laser pins, and EEE CPMU registers. Several routines use read-modify-write and restore prior register modes, but many mode programming functions assume ownership of the block and overwrite known hardware sequences.

## Dependencies And Integration Points

Internal dependencies:

- Register macros, chip predicates, `REG_RD/REG_WR`, `REG_RD_DMAE/REG_WR_DMAE`, `EMAC_RD/EMAC_WR`, `DP`, `BNX2X_ERR`, `SHMEM2_HAS`, `SHMEM2_RD`, and firmware command helpers come from `bnx2x.h`, `bnx2x_cmn.h`, and generated register/hsi headers included by them.
- Public declarations, structs, constants, flow-control flags, media types, callback typedefs, and DCB structures are in `bnx2x_link.h`.
- DCB/PFC/ETS callers are in `bnx2x_dcb.c`, which calls `bnx2x_update_pfc()` and `bnx2x_ets_e3b0_config()`.
- Link initialization/update callers are in `bnx2x_main.c`; ethtool paths call `bnx2x_phy_init()` and `bnx2x_read_sfp_module_eeprom()`.
- Firmware and management integration uses `bnx2x_fw_command()` with messages such as SFP module verification and AFEX link status changed.

Hardware/firmware dependencies:

- MCP shared memory layout: `struct shmem_region`, `struct shmem2_region`, `struct shmem_lfa`, `port_hw_config`, `port_feature_config`, `link_status`, `eee_status`, and `link_attr_sync`.
- NIG/PBF/MAC register blocks and chip generation differences: E1/E1x/E2/E3A0/E3B0 paths differ substantially.
- External PHY behavior through callback descriptors defined later in the file. This chunk defines BCM8073 and BCM8705 handlers and shared 8073/8727 helpers, but later chunks define additional external PHYs and static `bnx2x_phy` templates.
- SFP module I2C through BCM8726/8727 PHY two-wire engines or E3 Warpcore BSC/IMC registers.

## Risks And Edge Cases

- Register sequencing is brittle. Many routines depend on exact ordering, delays, double reads of latched status registers, and temporary AER changes. Missing a restore, delay, or status clear can leave MDIO, AN, or MAC blocks in an inconsistent state.
- Error propagation is uneven. Some MDIO failures return `-EFAULT`/`-EINVAL`, but many callers ignore return values from individual reads/writes and proceed with default or stale values.
- Shared-memory field availability is version dependent. Some paths guard with `SHMEM2_HAS`, while other shmem reads assume offsets exist. LFA and EEE behavior depends on firmware layout and feature flags.
- Link-up reconciliation can intentionally force link down when internal and external speeds disagree. That protects against transient mismatches but may cause flaps if a PHY reports intermediate speeds during negotiation.
- `bnx2x_ets_e3b0_get_total_bw()` mutates a zero bandwidth to 1 to prevent blocked ramrods, so caller-provided ETS parameters are not purely input.
- Some register selection switches have invalid COS cases only for port 1 and no explicit default for out-of-range values, relying on prior validation of `num_of_cos`.
- SFP EEPROM readers cap transfer size but differ in return codes and wait loops. Warpcore BSC retries can power-cycle the module on non-init reads, which is disruptive but intentional as an I2C workaround.
- Module enforcement depends on bootcode feature flags. If firmware lacks verification support, strict enforcement paths fail and may disable approved-module handling on dual-media setups.
- `bnx2x_get_edc_mode()` can force a 1G SFP module to `SPEED_1000` by modifying `phy->req_line_speed`, which changes later link initialization behavior.
- PFC and pause are treated as orthogonal modes: enabling PFC disables normal pause handling in several blocks. Transitions between PFC and SAFC/LLFC require NIG and MAC updates to stay aligned.
- Warpcore KR/KR2 recovery and `link_attr_sync` KR2 enable bits interact with later periodic functions outside this chunk; incomplete handling can strand recovery timers.

## Test Signals

Useful validation signals from this chunk:

- Link init/update: exercise direct media, single external PHY, and dual-media paths; verify `link_status`, `phy_link_up`, `link_up`, speed, duplex, flow control, `mac_type`, `media_type`, and MCP shared memory match the physical link.
- MAC selection: verify E1/E2 use EMAC below 10G and BMAC at 10G; E3/Warpcore use UMAC below 10G and XMAC at 10G/20G.
- Interrupt behavior: after link transitions, NIG status bits should be acknowledged and latch-style external PHY interrupts rearmed without losing subsequent events.
- DCB/PFC: from `bnx2x_dcb.c`, update PFC and ETS configurations and confirm NIG/PBF/MAC register state, `LINK_STATUS_PFC_ENABLED`, and pause/PFC traffic behavior.
- EEE: verify NVRAM and override timer modes, `eee_status` propagation, LPI enable on active negotiated EEE, and LPI disable on link down.
- SFP: use ethtool EEPROM reads through BCM8726, BCM8727/8722, and direct Warpcore paths; test invalid device addresses, multi-page reads, 1G SFP forced-speed behavior, passive/active DAC, linear/limiting optic modes, and rejected-module fault LEDs/transmitter gating.
- MDIO robustness: simulate MDIO timeout paths to ensure errors are logged and callers do not dereference uninitialized status.
- KR/KR2: verify AN advertisement, FEC advertisement, CL37 fallback, lane reset/retry counters, and `link_attr_sync` updates.

## Cross-Chunk Notes

- `bnx2x_sfp_module_detection()` is only forward-declared and begins at line 8683, just outside this chunk. The SFP helpers here feed into that function, but the final module-detect control flow must be reconciled with the next chunk.
- Full PHY callback tables, probe/populate logic, `bnx2x_phy_init()`, reset/LFA wrappers, periodic error detection, and later external PHY families are outside this chunk. This report should be merged with later chunk reports before drawing whole-file conclusions.
