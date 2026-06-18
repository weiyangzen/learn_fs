# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-mdio.c

## Purpose
`xgbe-mdio.c` implements the common PHY/MDIO orchestration layer above version-specific PHY implementations. It manages Clause 37 and Clause 73 auto-negotiation, link status transitions, flow-control resolution, PHY start/stop/reset, and function-pointer export through `struct xgbe_phy_if`.

## Important APIs, Types, And Functions
- Module EEPROM wrappers `xgbe_phy_module_info` and `xgbe_phy_module_eeprom` delegate optional SFP support to the implementation.
- AN interrupt helpers configure and clear CL37/CL73 interrupt masks.
- Mode helpers (`xgbe_kr_mode`, `xgbe_kx_2500_mode`, `xgbe_sfi_mode`, etc.) set MAC speed and delegate PHY mode programming to `phy_impl.set_mode`.
- `xgbe_an73_*` and `xgbe_an37_*` functions implement auto-negotiation page handling, incompatible-link fallback, and completion/error handling.
- `xgbe_an_state_machine` serializes AN work under `pdata->an_mutex`.
- `xgbe_phy_config_aneg` and `xgbe_phy_reconfig_aneg` initialize mode, advertisement, interrupts, and AN state.
- `xgbe_phy_status` polls implementation link status, handles AN timeout/restart, sets carrier, and updates flow control and queues.
- `xgbe_phy_init`, `xgbe_phy_start`, `xgbe_phy_stop`, `xgbe_phy_reset`, and `xgbe_phy_exit` provide the generic PHY interface.
- `xgbe_init_function_ptrs_phy` fills `struct xgbe_phy_if`.

## Control Flow
Generic PHY init initializes AN work, reads FEC ability, calls the version-specific PHY init to populate supported link modes, copies supported to advertising, and seeds pause settings. Start calls implementation start, requests a separate AN IRQ when needed, chooses an initial supported mode, initializes AN registers, enables AN interrupts, and starts negotiation. AN IRQs schedule work; the state machine consumes pending AN bits and either completes, retries in another mode, starts KR training, or marks errors. The periodic PHY status path checks link state, waits for AN completion, applies negotiated mode, controls carrier, and stops/wakes TX queues on link changes.

## State And Persistence
The file maintains `pdata->an_result`, `an_state`, `kr_state`, `kx_state`, `an_int`, `an_status`, `an_start`, `kr_start_time`, `parallel_detect`, `fec_ability`, `phy_link`, `phy_speed`, and flow-control fields. It also owns `an_mutex`, `an_work`, `an_irq_work`, and optional `an_bh_work`. All state is runtime and reset on PHY reconfiguration or device teardown.

## Dependencies And Integration Points
This layer depends on version-specific implementations in `xgbe-phy-v1.c` and `xgbe-phy-v2.c` through `phy_impl`, hardware callbacks in `hw_if`, Linux MDIO definitions, netdev carrier/queue APIs, IRQ/workqueue APIs, and ethtool link mode helpers. `xgbe-ethtool.c` calls into `phy_config_aneg` and `phy_valid_speed`; `xgbe-main.c` invokes PHY init/exit; bus probes supply `an_irq`.

## Risks
AN logic is stateful and race-sensitive. IRQ masking, workqueue flushing, and `an_mutex` must prevent concurrent mode changes. Link timeout logic can restart AN; KR training adds a wait loop to avoid premature restart. Incorrect implementation callbacks can leave MAC speed and PHY mode mismatched. Link-down handling stops TX queues without resetting BQL, relying on descriptor cleanup. Failure to re-enable AN interrupts or reissue IRQs can stall negotiation.

## Test Signals
Test CL73 backplane negotiation, CL37 Base-X, CL37 SGMII, fixed-speed operation, incompatible-link fallback between KR/KX, KR training, pause resolution, link flap behavior, and external PHY/SFP modes through the v2 implementation. Kernel link messages, carrier state, queue wake/stop behavior, and `ethtool` link partner advertisement are useful observability points.
