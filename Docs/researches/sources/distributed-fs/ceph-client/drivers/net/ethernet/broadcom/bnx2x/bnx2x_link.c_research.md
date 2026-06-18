# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_link.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004362`: lines 1-8682, `Docs/researches/chunks/subset-b-004362_research.md`
- `subset-b-004363`: lines 8683-14065, `Docs/researches/chunks/subset-b-004363_research.md`

## Chunk Research

### subset-b-004362: lines 1-8682

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

### subset-b-004363: lines 8683-14065

# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_link.c lines 8683-14065

## Scope

This chunk covers the second half of the Broadcom `bnx2x` link-management implementation. It starts with SFP/SFP+ module detection for 8726/8727 and E3 Warpcore paths, then implements external PHY support for BCM8706, BCM8726, BCM8727/8722, BCM8481/84823/84833/84834/84858, BCM54618SE, and SFX7101. The latter part defines the `struct bnx2x_phy` templates, populates internal and external PHY instances from shared memory, probes/defaults link settings, initializes loopback and normal link paths, performs link reset/LFA reset/common external-PHY init, and runs periodic fault/over-current/KR2 workaround checks.

This is the final chunk for this source file. Earlier internal PHY, MAC, LED, Warpcore, EEE, SFP helper, and link-status helper definitions are in `subset-b-004362`.

## Purpose and Major Responsibilities

- Detect SFP module insertion/removal, power SFP modules, verify module approval, enforce optical module policy, program module-specific EDC/limiting modes, and control TX laser/fault LEDs.
- Configure and poll multiple external PHY families via Clause 45 or Clause 22 MDIO, including speed advertisement, flow-control advertisement, LASI/interrupt handling, firmware/SPI-ROM version saving, media selection, EEE, pair-swap, and LED behavior.
- Provide static `struct bnx2x_phy` descriptors that bind each supported PHY type to callbacks for config, status, reset, loopback, firmware version formatting, LED setting, and vendor-specific hooks.
- Populate runtime PHY objects from NVRAM/shared-memory configuration, including MDIO bus selection, address, preemphasis values, supported modes, speed capability masks, media type sync, and multi-PHY swapping.
- Initialize and reset link hardware at the driver level, including NIG/BRB filters, MAC selection, loopback setup, external PHY reset, link flap avoidance, management shared-memory status updates, and EEE management state.
- Perform board-wide external PHY common initialization before per-port link init, especially for shared reset pins and PHYs that need firmware boot or synchronized dual-port reset sequencing.
- Periodically detect runtime link hazards such as remote/half-open faults, SFP TX faults, over-current events, KR2 partner compatibility problems, and Warpcore runtime reconfiguration needs.

## Important APIs, Types, and Functions

- `struct bnx2x_phy`, `struct link_params`, and `struct link_vars` are the central state carriers. This chunk defines PHY template instances such as `phy_warpcore`, `phy_8727`, `phy_84833`, and `phy_54618se`, then copies and specializes them into `params->phy[]`.
- `bnx2x_sfp_module_detection()` powers and verifies SFP modules, sets the module fault LED, applies enforcement policy from `PORT_FEAT_CFG_OPT_MDL_ENFRCMNT_MASK`, sets limiting/LRM mode, and may disable the TX laser.
- `bnx2x_handle_module_detect_int()` handles MOD_ABS GPIO interrupts. E3 uses the internal Warpcore PHY; older chips use `EXT_PHY1`. On insertion it powers the module, waits for initialization, verifies it, and for initialized E3 links may reset/reconfigure the Warpcore SFI lane.
- `bnx2x_sfp_mask_fault()` masks or enables PMA LASI TX fault events based on latched fault status and is reused by 8706/8726/8727 status paths.
- `bnx2x_8706_8726_read_status()`, `bnx2x_8706_config_init()`, and the 8726-specific helpers configure firmware boot, 1G/10G mode, LASI, preemphasis, SFP module detection, loopback, and status/fault reporting for 8706/8726 PHYs.
- `bnx2x_8727_config_init()`, `bnx2x_8727_handle_mod_abs()`, `bnx2x_8727_read_status()`, `bnx2x_8727_config_speed()`, `bnx2x_8727_link_reset()`, and `bnx2x_8727_set_link_led()` cover 8727/8722 SFP PHY initialization, module presence polarity, EDC/reference-clock behavior, over-current handling, speed selection, dual-media XAUI power, TX laser enable, and NOC LED behavior.
- `bnx2x_848xx_cmn_config_init()`, `bnx2x_848x3_config_init()`, `bnx2x_848xx_read_status()`, `bnx2x_848xx_cmd_hdlr()`, `bnx2x_8483x_enable_eee()`, and `bnx2x_8483x_disable_eee()` implement 848xx copper PHY setup, firmware mailbox commands, dual-media policy, pair swap, EEE advertisement, LED setup, SPI-ROM version capture, and link partner capability reporting.
- `bnx2x_54618se_config_init()`, `bnx2x_54618se_read_status()`, `bnx2x_54618se_link_reset()`, and `bnx2x_54618se_config_loopback()` implement the E3 Clause 22 GPHY path, including reset through configured pins, shadow-register LED/interrupt setup, 10/100/1000 advertisement, 1G EEE, flow control, status decoding, and loopback.
- `bnx2x_7101_config_init()`, `bnx2x_7101_read_status()`, `bnx2x_sfx7101_sp_sw_reset()`, and `bnx2x_7101_set_link_led()` implement SFX7101 10GBase-T setup, LASI, AN restart, firmware version formatting, software reset, low-power GPIO reset, and LED control.
- `bnx2x_populate_preemphasis()`, `bnx2x_populate_int_phy()`, `bnx2x_populate_ext_phy()`, `bnx2x_phy_def_cfg()`, `bnx2x_phy_selection()`, and `bnx2x_phy_probe()` translate board/shared-memory configuration into active PHY objects and default requested link settings.
- `bnx2x_phy_init()`, `bnx2x_link_reset()`, `bnx2x_lfa_reset()`, `bnx2x_set_rx_filter()`, and loopback init helpers are the exported/driver-facing link orchestration surface in this chunk.
- `bnx2x_common_init_phy()` and helpers (`bnx2x_8073_common_init_phy()`, `bnx2x_8726_common_init_phy()`, `bnx2x_8727_common_init_phy()`, `bnx2x_84833_common_init_phy()`) perform one-time shared external-PHY reset/firmware initialization before normal per-port init.
- `bnx2x_period_func()`, `bnx2x_check_half_open_conn()`, `bnx2x_sfp_tx_fault_detection()`, `bnx2x_check_over_curr()`, and `bnx2x_check_kr2_wa()` are periodic maintenance and fault-analysis entry points.

## Control Flow

SFP module handling begins when a MOD_ABS interrupt is configured by `bnx2x_init_mod_abs_int()` and later handled by `bnx2x_handle_module_detect_int()`. The handler reads the configured GPIO, arms the next edge, powers the module on insertion, waits for module initialization, and calls `bnx2x_sfp_module_detection()`. Detection enables the transmitter optimistically, powers the module, reads the EDC mode, verifies module approval, and then applies policy: leave it active, light the fault LED, power it down, or disable only the TX laser. On E3 SFI, a successful module change may cause a Warpcore lane reset/reconfiguration so 1G module limitations are reflected in the lane configuration.

8706/8726 status flow clears RX alarm and LASI status, updates TX fault masking, reads PMA RX signal detect, PCS status, and AN link status twice, and reports either 1G or 10G full-duplex link. For 10G, it also reads TX LASI twice to set `vars->fault_detected`. 8726 overlays this by checking `MDIO_PMA_REG_PHY_IDENTIFIER` bit 15 and suppressing link if TX is disabled.

8727 initialization waits for reset completion, runs the 8727-specific PHY init hook, programs MOD_ABS/OPRXLOS polarity, enables PMD transmit, powers the module, clears message/RX alarm state, configures speed, writes optional TX preemphasis, and sets low-power prevention when TX laser is GPIO0-controlled. Runtime status first validates LASI is enabled, clears RX/LASI/message status, handles over-current when a module is present, handles module absent/present transitions, enables TX laser only for approved modules, reads `MDIO_PMA_REG_8073_SPEED_LINK_STATUS`, sets line speed to 1G or 10G, resolves flow control, and adjusts dual-media XAUI power for forced 1G.

848xx copper PHY initialization is layered. The common config clears PMA control, reads existing 1000T/legacy/MII control advertisement, applies requested speed/duplex/capability masks, advertises pause, enables auto-MDIX for forced 10/100, and configures 10GBase-T AN. The 848x3 wrapper handles reset, optional XGXS preconditioning for 84823, detects 84858 hardware behind older config values, programs dual-media copper/fiber priority, applies pair-swap and AutogrEEEn/EEE firmware commands, optionally powers down the copper core, configures CMS, jumbo-related 1G settings, and exits super-isolate mode. Read status checks 10G PMD signal first, then legacy expansion status for 10/100/1000, sets duplex, reports AN/parallel-detect status, resolves flow control, reports link-partner capabilities, and resolves EEE for 8483x/8485x.

54618SE config uses an E3 configured pin to bring the GPHY out of reset, resets it over Clause 22, configures LED4 as link-change interrupt, flips fiber signal-detect polarity, computes IEEE pause advertisement, sets 10/100/1000 advertisement from `phy->speed_cap_mask`, handles forced 10/100 with auto-MDIX, configures 1G EEE or legacy Auto-GrEEEn, and writes control/advertisement registers. Its read-status path decodes `MDIO_REG_GPHY_AUX_STATUS`, clears the interrupt, maps the encoded speed/duplex into `vars`, sets AN/parallel-detection and link-partner status bits, resolves flow control, and optionally resolves EEE.

Static PHY declarations act as a callback table. `bnx2x_populate_int_phy()` chooses Warpcore on E3-like hardware or SerDes/XGXS on older chips, restricts supported modes by configured serdes interface, sets flags such as `FLAGS_WC_DUAL_MODE`, `FLAGS_4_PORT_MODE`, and MDIO workarounds, and fills address/MDIO control/default devad. `bnx2x_populate_ext_phy()` decodes external PHY type from shared memory, copies the matching template, handles special variants such as `BCM8727_NOC` and 54618SE EEE, selects the MDIO access path, sets the firmware-version shared-memory address, applies preemphasis, and may drop 100M support for older 84833/84834 firmware.

`bnx2x_phy_probe()` walks internal and external PHY slots, accounts for swapped PHY order, populates each PHY, disables remote fault checks if configured, applies the generic MDC/MDIO workaround when MT support is absent, initializes shared media-type fields if empty, calls `bnx2x_phy_def_cfg()` to set requested speed/flow control from NVRAM link config, and increments `params->num_phys`. Any populate failure clears discovery and returns `-EINVAL`.

`bnx2x_phy_init()` resets `link_vars`, marks `PHY_INITIALIZED`, opens NIG/BRB RX filters, increments the link count, then checks link flap avoidance. If LFA can be used, it synchronizes current link state, re-runs PHY-specific init hooks and SFP verification for logging, reenables the active MAC, updates LFA counters, disables NIG drain, and reenables interrupts. Otherwise it records the requested configuration in LFA memory, disables link attentions, initializes EMAC baseline state, sets PFC status if requested, initializes PHY variable state, and either enters one of the loopback setup paths or performs normal link initialization followed by interrupt enable. It always updates management link and EEE status before returning.

Reset flow in `bnx2x_link_reset()` clears management link/EEE state, disables attentions, enables NIG drain, disables egress and MAC RX/TX paths, waits for drain, turns off LEDs, calls external PHY `link_reset` callbacks when requested, rearms/clears latch state for PHYs that require it, resets the internal PHY, disables ingress interfaces, soft-resets XMAC where applicable, and clears `vars->link_up` and `vars->phy_flags`. `bnx2x_lfa_reset()` is a lighter reset path for link flap avoidance that drains, closes RX filters without cutting a packet midstream, reopens the MAC-facing gate, and avoids resetting external PHYs when LFA shared memory is present.

Common PHY init runs before per-port link setup. It sets MDIO clocks, enables EPIO on E3, skips work if port 0 already has a saved external PHY firmware version, then dispatches per external PHY slot. 8073/8727 common init performs shared reset, populates both ports' PHY objects with port-swap/path handling, disables attentions, resets both PHYs, waits, orders PHY blocks by address, downloads external ROM firmware, and disables TX or toggles TX power-down as required. 8726 common init enables GPIO3 MOD_ABS events, resets both PHYs, and turns on the fault-module LED. 84833-family common init pulses the reset GPIO mask for both ports.

Periodic flow first searches for the first PHY with `FLAGS_TX_ERROR_CHECK` and runs half-open/remote-fault detection against XMAC or BMAC LSS status. On E3 it also checks KR2 recovery/disable decisions for 20G/KR2 modes, over-current pins, runtime Warpcore reconfiguration after ASIC RX/TX reset, and SFI TX fault state. Fault analysis changes `vars->link_up`, `vars->link_status`, NIG drain, LEDs, management shared memory, and general-attention notification only when the new fault bit differs from the cached `vars->phy_flags` state.

## State and Persistence Behavior

- `params->phy[]` persists the probed PHY topology and callback set after `bnx2x_phy_probe()`. The templates are copied by value, then fields such as `addr`, `mdio_ctrl`, `ver_addr`, `flags`, `supported`, `media_type`, preemphasis, requested speed, and flow control are mutated per board and per port.
- `link_vars` is reset at link init and reset, then updated by status/config paths with `link_up`, `phy_link_up`, `line_speed`, `duplex`, `flow_ctrl`, `mac_type`, `phy_flags`, `fault_detected`, `link_status`, `eee_status`, `periodic_flags`, `check_kr2_recovery_cnt`, and SFP/over-current fault state.
- Shared memory is both input and persistent output. Inputs include external PHY type/address, speed capability masks, link config, preemphasis, SFP control, module enforcement policy, LED mode, reset pins, media type, and LFA requested configuration. Outputs include external PHY firmware versions, media type sync fields, AEU interrupt masks, management link status, EEE status, and LFA counters/reasons.
- Hardware state is persistent in MDIO registers, NIG/MAC registers, GPIO/EPIO pins, LASI masks/status, PMA/AN/PCS control/status, PHY firmware mailbox registers, LED masks, Warpcore lane state, and module power/TX laser pins. Many helpers intentionally leave these programmed until reset or a later link reconfiguration.
- SFP module approval persists in `phy->flags` through helpers outside this chunk, and this chunk consumes `FLAGS_SFP_NOT_APPROVED` to block TX laser enable and preserve fault LED semantics.
- `bnx2x_common_init_phy()` uses saved port 0 external PHY firmware version as a once-per-device guard. If that shared-memory value is nonzero, common init is skipped.
- Link flap avoidance persists requested link parameters and counters in `struct shmem_lfa`; successful avoidance increments the avoidance counter and clears reason, while failure records the new requested settings and increments the flap counter.
- Periodic fault handling uses `vars->phy_flags` as the previous-state cache for remote fault, SFP TX fault, and over-current state. Link and LED updates happen only on edge transitions.

## Dependencies and Integration Points

- Register access depends on driver-local MMIO and MDIO helpers such as `REG_RD`, `REG_WR`, `REG_RD_DMAE`, `bnx2x_cl45_read/write`, `bnx2x_cl22_read/write`, `bnx2x_bits_en/dis`, `bnx2x_set_gpio`, `bnx2x_set_cfg_pin`, `bnx2x_set_mult_gpio`, and `bnx2x_get_emac_base`.
- Shared-memory layout comes from `struct shmem_region`, `struct shmem2_region`, and `struct shmem_lfa`; the chunk relies on many `PORT_HW_CFG_*`, `PORT_FEATURE_*`, `SHARED_HW_CFG_*`, `LINK_STATUS_*`, and `LINK_ATTR_*` constants.
- Link/MAC helpers from the earlier chunk or nearby code are required: `bnx2x_link_initialize()`, `bnx2x_link_status_update()`, `bnx2x_sync_link()`, `bnx2x_update_mng()`, `bnx2x_update_mng_eee()`, `bnx2x_set_led()`, `bnx2x_emac_enable()`, `bnx2x_bmac_enable()`, `bnx2x_xmac_enable()`, `bnx2x_umac_enable()`, `bnx2x_xgxs_deassert()`, `bnx2x_serdes_deassert()`, and EEE helpers.
- SFP-specific behavior depends on helper routines outside this chunk for module power, transmitter control, EDC mode, approval verification, limiting mode, module presence, and fault LEDs.
- Warpcore integration appears in E3 internal PHY population, SFI module reconfiguration, loopback, KR2 workaround, runtime reconfiguration, over-current power control, and link reset.
- Linux kernel integration appears through delay/logging primitives and netdev reporting: `msleep()`, `usleep_range()`, `udelay()`, `netdev_err()`, and debug `DP(NETIF_MSG_LINK, ...)`.
- Hardware integration is board-specific: GPIO reset pins, MOD_ABS pins, TX_FAULT pins, over-current pins, PHY address swapping, port swapping, external PHY MDIO access mode, and LED wiring all come from shared/NVRAM configuration.

## Risks and Edge Cases

- The code is heavily register-sequenced and mostly assumes MDIO/MMIO writes succeed. Many helper calls do not return status, so a failed transaction can leave a PHY, GPIO, LASI mask, or MAC gate partially configured without a propagated error.
- `bnx2x_sfp_module_detection()` enables the transmitter before module verification. Enforcement can later power down or disable TX laser, but there is a window where an unapproved or faulty module may have TX enabled.
- 8727 over-current handling logs a fatal-style message, masks all RX alarms except MOD_ABS, waits for module absent, powers the module down, and returns link down. Recovery requires physical removal/system restart according to the message; automated recovery is intentionally limited.
- Common init skip is based on one shared firmware-version field. If that field is stale or partially written, shared PHY reset/firmware boot may be skipped even when hardware needs it.
- `bnx2x_populate_preemphasis()` reads `xgxs_config2_rx` for both RX and TX in the EXT_PHY2 path. That may be intentional due to layout naming, but it is suspicious because the EXT_PHY1 path uses separate RX/TX offsets.
- In `bnx2x_phy_probe()` failure cleanup loops over all PHY indices but assigns `*phy = phy_null` to the last selected pointer rather than `params->phy[phy_index]`; that looks like an incomplete cleanup of previously populated entries.
- `bnx2x_phy_selection()` swaps only recognized selection values. Unknown `multi_phy_config` priority values pass through as `prio_cfg`, leaving later switch statements to treat them as hardware default or do nothing.
- Several reset/common-init loops use signed `s8 port` with descending loops over `PORT_MAX - 1` to `PORT_0`; this is intentional but fragile if constants or types change.
- `bnx2x_get_ext_phy_reset_gpio()` switches on the full `default_cfg` value rather than a masked field. If unrelated bits are present, it may fail to override the default GPIO/port.
- `bnx2x_848xx_cmd_hdlr()` chooses the 84858 mailbox protocol either by PHY type or by `LINK_ATTR_84858` in shared memory. Misdetected hardware revision can route commands through the wrong mailbox protocol.
- EEE configuration has several board/firmware gates. Missing capability bits, invalid timers, half-duplex requests, or firmware revisions below thresholds will silently disable advertised EEE in `vars->eee_status`.
- LED control for BCM84834 temporarily disables `NIG_MASK_MI_INT` and stores `LINK_FLAGS_INT_DISABLED`; if later mode transitions do not return to `LED_MODE_OPER`, interrupts can remain disabled longer than expected.
- Fault analysis intentionally avoids changing link state when `PHY_PHYSICAL_LINK_FLAG` is not set, but still returns "changed"; callers using only the return value may treat this as a handled transition even though management link state was not updated.
- Periodic remote-fault detection breaks after the first `FLAGS_TX_ERROR_CHECK` PHY. On multi-PHY boards, later PHYs with the flag are not checked in that periodic pass.
- `bnx2x_init_mod_abs_int()` computes `vars->aeu_int_mask` using GPIO and swapped port position. Bad pin configuration can enable the wrong attention bit and make module interrupts appear missing or attributed to the wrong function.

## Test Signals

- Build the `bnx2x` driver with this file enabled. Compile-time signals include correct callback prototypes, `fallthrough` handling, static descriptor initializers, and availability of all MDIO/register constants from headers.
- Probe representative boards for each populated PHY family: direct SerDes/XGXS, Warpcore SFI/KR/KR2/DXGXS, BCM8706, BCM8726, BCM8727/NOC, BCM8481/84823/84833/84834/84858, BCM54618SE, and SFX7101. Expected logs include successful PHY population, nonzero `num_phys`, correct MDIO address/control, and firmware-version save where supported.
- Exercise SFP insertion/removal on 8726/8727 and E3 SFI. Signals are MOD_ABS GPIO/AEU interrupts, module power enable, initialization wait success/failure logs, module approval/fault LED behavior, TX laser policy, media-type changes, and Warpcore SFI reconfiguration for 1G modules.
- Test optical module enforcement modes: no enforcement, disable TX laser, and power down. Verify `FLAGS_SFP_NOT_APPROVED`, fault LEDs, module power state, and link status behave as configured.
- Validate link modes for copper PHYs: forced 10/100, autonegotiated 10/100/1000, 10GBase-T, advertised pause/asymmetric pause, full/half duplex where supported, pair-swap, and link-partner capability reporting.
- Validate EEE on 54618SE and 84833/84858-class PHYs with supported firmware and valid timers. Signals are `vars->eee_status`, management EEE shared memory, EEE advertisement registers/mailbox commands, and negotiated EEE status after link.
- Exercise loopback modes `LOOPBACK_BMAC`, `LOOPBACK_EMAC`, `LOOPBACK_XMAC`, `LOOPBACK_UMAC`, `LOOPBACK_XGXS`, and `LOOPBACK_EXT_PHY`. Expected outcomes are forced `vars->link_up`, appropriate MAC type/speed, NIG drain disabled, LED operational mode, and traffic passing through the selected loopback.
- Trigger link reset and LFA reset while traffic is active. Useful signals are NIG drain transitions, BRB RX filter closure/opening, MAC RX/TX disable/enable, no partial packets forwarded during LFA reset, management link status cleared, and external PHY callbacks invoked only when requested.
- Test board-wide common init after cold boot and after a saved firmware version exists. Confirm reset GPIO pulses, external ROM boot, TX disable/power-down steps, and skip behavior are all visible and correct.
- Inject or simulate remote fault, SFP TX fault, over-current, and KR2 non-compatible partner cases. Expected signals are `vars->phy_flags` edge transitions, NIG drain on fault, LED off/fault LED updates, management link status updates, general attention notification, module power down on over-current, and KR2 disable/recovery only after the configured delay.
- Verify MOD_ABS interrupt initialization by checking `vars->aeu_int_mask`, shared `aeu_int_mask`, AEU enable register, and GPIO event enable bits for both swapped and non-swapped port configurations.

## Chunk Notes for Merge Lane

Merge this chunk with `subset-b-004362` to form the final `bnx2x_link.c` research document. The earlier chunk should provide the internal MAC/Warpcore/EEE/SFP helper context that this chunk consumes. This chunk should be treated as the external-PHY and top-level orchestration half: it owns most vendor PHY callback implementations, PHY descriptor tables, PHY population/probe/defaulting, exported link init/reset/common-init entry points, and periodic runtime fault handling.
