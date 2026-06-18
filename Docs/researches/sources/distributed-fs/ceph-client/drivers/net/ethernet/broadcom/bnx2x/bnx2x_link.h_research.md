# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_link.h

Work item: `subset-b-004364`

## Purpose

`bnx2x_link.h` is the public link-control contract for the Broadcom/QLogic
`bnx2x` Ethernet driver. It defines the PHY abstraction, per-port link input
and output state, loopback modes, flow-control constants, SFP EEPROM offsets,
EEE knobs, DCB/PFC/ETS data structures, and the exported link-management APIs
implemented in `bnx2x_link.c`.

The header is included from `bnx2x.h`, where each device instance embeds
`struct link_params link_params` and `struct link_vars link_vars`. Higher-level
driver code in `bnx2x_main.c`, `bnx2x_ethtool.c`, `bnx2x_dcb.c`,
`bnx2x_cmn.c`, stats, and SR-IOV paths operate through this API rather than
directly coding per-PHY behavior.

## Important Definitions

- PHY topology is fixed by `INT_PHY`, `EXT_PHY1`, `EXT_PHY2`, and `MAX_PHYS`.
  The driver supports one internal PHY and up to two external PHYs. Board media
  shape helpers classify single-media-direct, single-media, and dual-media
  boards from `params->num_phys`.
- `LINK_CONFIG_SIZE` is `MAX_PHYS - 1`, because the internal PHY and first
  external PHY share one link configuration slot. `LINK_CONFIG_IDX()` maps PHY
  index to the corresponding requested configuration entry.
- Flow-control constants (`BNX2X_FLOW_CTRL_*`) are aliases for shared-memory
  port feature constants. This keeps link code, ethtool, and management firmware
  status in the same encoding.
- SerDes and speed definitions include `NET_SERDES_IF_XFI`, `SFI`, `KR`,
  `DXGXS`, `SPEED_AUTO_NEG`, and `SPEED_20000`. The rest of the speed values
  come from surrounding kernel driver headers.
- SFP/SFP+ EEPROM constants describe the A0/A2 I2C device addresses, 16-byte
  page reads, and offsets for vendor identity, OUI, part number, revision,
  serial, date, diagnostic support, and checksums. These are used by SFP module
  validation and ethtool module EEPROM reads.
- `FW_PARAM_*` packs a PHY address, PHY type, and MDIO controller selector into
  a firmware parameter word. `XGXS_EXT_PHY_TYPE()`, `XGXS_EXT_PHY_ADDR()`, and
  `SERDES_EXT_PHY_TYPE()` decode shared hardware configuration words.
- Link feature flags in `struct link_params` include PFC enablement, bootcode
  capabilities for optic module verification and SFP TX disable, remote-fault
  detection suppression, multi-threading MDIO support, AutoGrEEEn, AFEX, and
  boot-from-SAN behavior.
- EEE mode bits in `params->eee_mode` encode whether LPI is enabled,
  advertised, loaded from NVRAM, overridden, and whether timer values are in
  NVRAM units or microseconds.

## Core Types

### `struct bnx2x_phy`

`struct bnx2x_phy` is the per-PHY vtable and persistent PHY descriptor. It holds
the PHY type, MDIO address, default MDIO device, flags, RX/TX preemphasis
values, MDIO controller base, supported link modes, media type, firmware
version register address, default requested speed/duplex/flow-control fields,
and callbacks.

Important callbacks:

- `config_init`: configures LASI, speed, autonegotiation, duplex, and flow
  control during link initialization.
- `read_status`: reads interrupt/status state and reports link, speed, duplex,
  flow control, faults, and EEE state into a `struct link_vars`.
- `link_reset`: resets or powers down the PHY on unload, interface down, or
  reconfiguration.
- `config_loopback`: applies PHY-level loopback.
- `format_fw_ver`: converts a raw PHY firmware value into a printable version.
- `hw_reset`: resets both PHY ports when common hardware reset is needed.
- `set_link_led`: drives PHY-specific LED modes.
- `phy_specific_func`: runs small generic actions such as `DISABLE_TX`,
  `ENABLE_TX`, and `PHY_INIT`.

Risk note: the flags are a dense compatibility matrix for hardware errata and
board behavior. `FLAGS_MDC_MDIO_WA`, `FLAGS_DUMMY_READ`,
`FLAGS_MDC_MDIO_WA_B0`, and `FLAGS_MDC_MDIO_WA_G` affect MDIO sequencing;
`FLAGS_TX_ERROR_CHECK` drives remote-fault handling; `FLAGS_REARM_LATCH_SIGNAL`
affects interrupt latch rearming; `FLAGS_SFP_NOT_APPROVED` and
`FLAGS_EEE` feed module enforcement and low-power behavior.

### `struct link_params`

`struct link_params` is the input and configuration side of the link contract.
It carries the port number, loopback mode, MAC address, requested duplex,
flow-control, speed, shmem bases, speed capability masks, switch config, lane
config, chip id, feature flags, populated PHY array, number of PHYs, EEE mode,
LED mode, multi-PHY selection config, device pointer, requested auto FC
advertisement, link flags, LFA base, and synchronized link attributes.

`params->bp` is the bridge back to the device object and is passed to all
callbacks. Most implementations use it for register access (`REG_RD`,
`REG_WR`), locks owned by callers, netdev diagnostics, chip revision tests, and
shared-memory offsets.

### `struct link_vars`

`struct link_vars` is the output and current-state side of the link contract.
It records PHY flags, active MAC type (`EMAC`, `BMAC`, `UMAC`, `XMAC`), internal
PHY link state, final link-up state, line speed, duplex, negotiated flow
control, IEEE FC advertisement, firmware-compatible link status, EEE status,
fault flags, KR2 recovery counter, periodic flags, AEU interrupt mask, and
reset/runtime workaround state.

The split between `link_params` and `link_vars` matters: `params` is the desired
configuration and hardware inventory, while `vars` is the runtime result
derived from PHY status and MAC setup.

### DCB/PFC/ETS Types

The header also exposes DCBX support structures:

- `struct bnx2x_nig_brb_pfc_port_params` configures NIG/BRB PFC behavior,
  pause enablement, LLFC outputs, priority-to-COS mapping, and RX COS priority
  masks.
- `struct bnx2x_ets_params` wraps a valid COS count and an array of COS entries.
  Each entry is either bandwidth-limited (`bnx2x_cos_state_bw`) with a BW
  percentage or strict priority (`bnx2x_cos_state_strict`) with a priority value.
- The maximum number of COS entries depends on chip generation and port:
  E2/E3A0 support 2, E3B0 port 0 supports 6, and E3B0 port 1 supports 3.

## Exported API Surface

Link lifecycle:

- `bnx2x_phy_probe()` discovers internal and external PHYs from shared hardware
  config, accounts for swapped PHY order, populates `params->phy[]`, fills
  default requested speed/duplex/flow control from shmem, records media type,
  and sets `params->num_phys`.
- `bnx2x_common_init_phy()` performs one-time external PHY common
  initialization after power-up. It programs MDIO clocks, enables EPIO on E3,
  checks whether shared firmware version state already indicates initialization,
  and runs common init for external PHY slots.
- `bnx2x_phy_init()` starts or restarts link. It clears `vars`, marks the PHY
  initialized, opens RX filters, checks link-flap avoidance, initializes EMAC
  state, handles loopback modes, calls PHY/MAC initialization, enables link
  interrupts, and updates management link and EEE status.
- `bnx2x_link_update()` is called on link interrupt. It reads each external PHY,
  chooses an active PHY according to `bnx2x_phy_selection()`, reads the internal
  PHY, reconciles speed/duplex/flow-control, updates MAC blocks, LEDs, shared
  memory, PBF/EEE, and records link-up or link-down state.
- `bnx2x_link_reset()` clears link status, updates management memory, disables
  link attentions, drains NIG egress, disables MAC RX/TX, optionally resets
  external PHYs, clears latch indications, resets the internal PHY, disables
  ingress, and clears runtime link state.
- `bnx2x_lfa_reset()` is a reset path tailored for link-flap avoidance. It
  drains egress and disables receive paths while preserving enough state for a
  later LFA-aware initialization.

PHY and module helpers:

- `bnx2x_phy_read()` and `bnx2x_phy_write()` locate a PHY by MDIO address in
  `params->phy[]` and dispatch CL45 MDIO operations.
- `bnx2x_link_status_update()` reads management shared memory link status and
  EEE status, synchronizes `link_vars`, media type, AEU interrupt mask, and PFC
  flags. It is used to reconstruct link state without reinitializing hardware.
- `bnx2x_get_ext_phy_fw_version()` formats external PHY firmware versions.
- `bnx2x_set_led()` selects PHY-specific or MAC-side LED handling for off, on,
  operational blink, and front-panel-off modes.
- `bnx2x_handle_module_detect_int()` handles SFP module-present interrupts and
  invokes module verification or transmitter control.
- `bnx2x_test_link()` reports actual link health for diagnostics.
- `bnx2x_ext_phy_hw_reset()`, `bnx2x_sfx7101_sp_sw_reset()`, and
  `bnx2x_hw_reset_phy()` provide hardware reset hooks for external PHY families.
- `bnx2x_read_sfp_module_eeprom()` reads SFP EEPROM data through the appropriate
  PHY-specific path and chunks requests into `SFP_EEPROM_PAGE_SIZE`.
- `bnx2x_fan_failure_det_req()` checks whether any PHY requires fan-failure
  detection.
- `bnx2x_set_rx_filter()` opens or closes the NIG-to-BRB gate.

DCB/PFC/ETS:

- `bnx2x_update_pfc()` updates NIG, BRB, EMAC/BMAC/XMAC PFC attributes when
  link is already up or when PFC state changes.
- `bnx2x_ets_disabled()` disables ETS according to chip generation.
- `bnx2x_ets_bw_limit()` configures two-COS bandwidth limiting.
- `bnx2x_ets_strict()` configures strict priority.
- `bnx2x_ets_e3b0_config()` maps E3B0 COS entries into strict-priority or
  WFQ/bandwidth clients and validates port-specific COS limits.
- `bnx2x_period_func()` performs periodic link work for PMF-owned ports,
  including link-event retries, TX fault handling, KR2 recovery, and workaround
  tasks implemented in `bnx2x_link.c`.

## Control Flow

Typical load path:

1. Main initialization populates `bp->link_params` from device, shmem, and NVRAM
   state, then calls `bnx2x_phy_probe()` during function init.
2. Open/load calls `bnx2x_initial_phy_init()`, which sets requested flow-control
   advertisement, acquires the PHY lock, optionally adjusts loopback mode for
   diagnostics, calls `bnx2x_phy_init()`, releases the lock, updates dropless
   FC, reports link if already up, and queues the periodic task.
3. `bnx2x_phy_init()` clears current link output state, opens RX filters, checks
   whether link-flap avoidance can reuse the previous hardware state, otherwise
   resets and initializes MAC/PHY state. Loopback modes short-circuit into
   EMAC/BMAC/UMAC/XMAC/XGXS setup; normal mode initializes PHY callbacks and
   enables link interrupts.
4. Link interrupts call `bnx2x_link_update()`. That function uses temporary
   `link_vars` per PHY, then commits a single resolved result to the device
   `link_vars`. It handles dual external PHY priority, invalid dual-link states,
   internal/external agreement, MAC enablement, LEDs, management shmem, PFC, and
   EEE status.
5. Interface down, unload, firmware upgrade preparation, and some ethtool paths
   call `bnx2x_link_reset()`. Firmware upgrades pass `reset_ext_phy = 0` so the
   external PHY is not reset while firmware operations are in progress.
6. The delayed periodic task calls `bnx2x_period_func()` once per second only
   when the function is PMF, under the PHY lock.

DCB flow:

1. DCB code updates `params->feature_config_flags` for PFC enablement.
2. It calls `bnx2x_update_pfc()` with NIG/BRB PFC parameters.
3. ETS mode changes call one of the ETS exported functions. E3B0 full
   configuration validates COS count and total BW, then writes NIG/PBF maps and
   COS credits.

Ettool and diagnostics flow:

- Link settings mutate `params->req_line_speed[]`, `req_duplex[]`,
  `speed_cap_mask[]`, `req_flow_ctrl[]`, `req_fc_auto_adv`, and
  `multi_phy_config`; changes are applied by resetting or reinitializing link.
- Module EEPROM operations call `bnx2x_read_sfp_module_eeprom()`.
- LED identify calls `bnx2x_set_led()`.
- Loopback tests temporarily set `params->loopback_mode`, re-run link init, and
  later restore normal link mode.

## State and Persistence Behavior

This header defines state that persists across link operations but not across a
full driver/device lifetime unless repopulated from firmware or shmem:

- `bp->link_params` stores desired user/default configuration and discovered
  hardware topology. It is populated by probe/common init and later modified by
  ethtool, DCB, loopback, boot-from-SAN clearing, and module handling paths.
- `bp->link_vars` stores current negotiated state. It is cleared by
  `bnx2x_phy_init()` and `bnx2x_link_reset()`, updated by `bnx2x_link_update()`,
  and consumed by stats, common link reporting, VF bulletin/report paths,
  ethtool getters, and DCB decisions.
- Firmware shared memory is the persistent cross-function and management
  boundary. `shmem_base`, `shmem2_base`, `lfa_base`, `link_status`,
  `eee_status`, `link_attr_sync`, media type, AEU mask, and LFA counters are
  read or written through offsets in `struct shmem_region`,
  `struct shmem2_region`, and `struct shmem_lfa`.
- Link-flap avoidance persists requested parameters and counters in LFA shmem so
  a later owner can avoid a disruptive reset when configuration matches.
- SFP module attributes and enforcement status are synchronized through
  `link_attr_sync`, media type fields in shmem, and PHY flags such as
  `FLAGS_SFP_NOT_APPROVED`.
- EEE state is split between requested mode in `params->eee_mode` and negotiated
  runtime status in `vars->eee_status`; management shmem is updated on link
  init, link-up, and link-down transitions.

## Dependencies

The header depends on definitions supplied by the rest of the `bnx2x` driver and
kernel networking stack:

- `struct bnx2x` is forward-referenced and defined in `bnx2x.h`.
- Shared-memory constants and structures such as `PORT_FEATURE_*`,
  `PORT_HW_CFG_*`, `LINK_STATUS_*`, `SHMEM_EEE_*`, and shmem layouts come from
  driver firmware-interface headers.
- Speed, duplex, and advertised/supported link-mode constants come from kernel
  networking/ethtool headers and local driver compatibility definitions.
- Implementations rely heavily on register access macros, chip tests, hardware
  locks, delays, workqueues, and netdev logging provided by the broader driver.
- PHY callbacks are bound to static PHY templates in `bnx2x_link.c` for
  internal SerDes/XGXS/Warpcore and external PHYs such as BCM8073, BCM8705,
  BCM8706, BCM8726, BCM8727, BCM8481, BCM84823, BCM84833/84834/84858,
  BCM54618SE, and SFX7101.

## Integration Points

- `bnx2x.h` embeds `link_params` and `link_vars` in the main device structure.
- `bnx2x_main.c` performs initial PHY probe, link init/reset, interrupt-driven
  updates, and periodic work scheduling around the API in this header.
- `bnx2x_ethtool.c` translates user link settings, pause parameters, EEE
  settings, loopback tests, EEPROM reads, and LED identify operations into
  `link_params` mutations and exported link calls.
- `bnx2x_dcb.c` uses `bnx2x_update_pfc()` and ETS functions to apply DCBX
  negotiated PFC/ETS policy.
- `bnx2x_cmn.c` consumes `link_vars` for link reports, VF-facing link data,
  carrier behavior, media selection, and loopback transitions.
- `bnx2x_stats.c` selects EMAC/BMAC/UMAC/XMAC counters based on
  `vars->mac_type` and suppresses link-dependent statistics when
  `vars->link_up` is false.
- SR-IOV/VF paths translate PF link state into VF link report fields, using
  `link_vars` as the PF-side source of truth.

## Risks and Edge Cases

- Multi-PHY priority and swap handling is subtle. `bnx2x_phy_selection()` must
  match bootcode shmem encoding, and `bnx2x_link_update()` treats impossible
  dual-link combinations as a reason to disable link.
- `LINK_CONFIG_IDX()` means the internal PHY and first external PHY share
  requested link configuration. Mistakes here can apply user settings to the
  wrong media path.
- MDIO access is timing-sensitive and errata-sensitive. Workaround flags can
  change MDIO clocking, force 10 MB status bits, or trigger dummy reads.
  Timeouts return `-EFAULT`; missing PHY address matches return `-EINVAL`.
- Link reset and init write many MAC/NIG/PBF/shared-memory registers. Caller
  locking is important; main and periodic paths acquire the PHY lock before
  invoking link operations.
- SFP module EEPROM reads are limited to supported PHY types and A0/A2 device
  addresses. Unsupported types return `-EOPNOTSUPP`; invalid device addresses
  return `-EINVAL`; failed reads affect module detection and media typing.
- `feature_config_flags` combines bootcode capability flags, user/driver feature
  state, and hardware workarounds. Incorrectly preserving or clearing bits can
  disable remote fault detection, PFC, SFP TX disable enforcement, EEE, or MDIO
  workarounds.
- EEE has state in both `params` and `vars`; link-down must clear active/LPI
  status and update shmem, or management and ethtool can report stale state.
- DCB ETS validation is chip-specific. E3B0 port 0 and port 1 have different COS
  limits, and total BW validation must reject invalid bandwidth configurations.
- Link-flap avoidance deliberately preserves hardware state. It depends on
  accurate LFA shmem comparisons; if the requested configuration changes but LFA
  still reuses state, link can be left with stale MAC/PHY programming.
- Loopback modes override normal link semantics and may force `link_up` or line
  speed. Test code must restore `loopback_mode` and requested speeds after
  diagnostics.

## Test Signals

Useful validation signals for changes touching this header or its contract:

- Build the `bnx2x` driver with warnings enabled. Type and prototype drift here
  should fail compile in `bnx2x_link.c`, `bnx2x_main.c`, `bnx2x_ethtool.c`,
  `bnx2x_dcb.c`, and consumers through `bnx2x.h`.
- Exercise probe/init/reset on representative chip families: E1/E1x/E2,
  E3A0/E3B0, Warpcore, and dual external PHY boards. Confirm `params->num_phys`,
  media type shmem fields, default requested speeds, and MDIO controller bases.
- Verify link-up/link-down interrupt handling with autonegotiation, forced
  1G/10G/20G, remote fault, half-open connection detection, SFP TX fault, and
  KR2 recovery.
- Run ethtool set/get link settings, pause settings, EEE settings, module EEPROM
  reads, LED identify, and loopback tests. Watch that `link_params` changes are
  reflected in hardware and restored after diagnostics.
- Test DCBX PFC and ETS transitions while link is up and down. Check management
  `LINK_STATUS_PFC_ENABLED`, NIG/BRB programming, MAC PFC programming, and
  E3B0 COS validation failures.
- Validate SFP module insert/remove interrupts, approved and non-approved optic
  enforcement, A0/A2 EEPROM reads, and TX laser disable behavior.
- Confirm periodic PMF-only work is queued once per second after initial link
  init and that it does not run for non-PMF functions.
- Inspect management shared memory after link transitions: `link_status`,
  `eee_status`, media type, AEU mask, link attributes, LFA status, and link
  counters should match the actual runtime state.

## Key Source Anchors

- Header definitions and PHY indices: `bnx2x_link.h:27`, `bnx2x_link.h:113`.
- `struct bnx2x_phy` and callback contract: `bnx2x_link.h:130`,
  `bnx2x_link.h:150`.
- `struct link_params`: `bnx2x_link.h:237`.
- `struct link_vars`: `bnx2x_link.h:335`.
- Link lifecycle prototypes: `bnx2x_link.h:378`.
- PHY helpers and SFP EEPROM API: `bnx2x_link.h:393`, `bnx2x_link.h:438`.
- DCB/PFC/ETS declarations: `bnx2x_link.h:471`, `bnx2x_link.h:519`.
- Implementation anchors in `bnx2x_link.c`: `bnx2x_phy_probe()` at line 12588,
  `bnx2x_phy_init()` at line 12947, `bnx2x_link_reset()` at line 13036,
  `bnx2x_link_update()` at line 6801, `bnx2x_update_pfc()` at line 2214,
  `bnx2x_ets_e3b0_config()` at line 1128, `bnx2x_read_sfp_module_eeprom()` at
  line 8077, `bnx2x_common_init_phy()` at line 13573, and
  `bnx2x_period_func()` at line 13910.
