# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ptp_hw.c

## Purpose

`ice_ptp_hw.c` is the low-level PTP, PHC, PHY timer, timestamp-memory, SMA/GPIO, and CGU/DPLL hardware access layer for Intel `ice` devices. It translates common PTP operations from `ice_ptp.c` and related driver code into register writes, sideband queue transactions, and family-specific calibration flows for E810, E822/E823, E825C/ETH56G, and E830 hardware. The file is hardware-stateful: most functions prepare shadow registers, program PHY blocks, and then execute synchronized timer commands so source timers and port timers change together.

## Important APIs, Types, And Functions

The public device-agnostic entry points are `ice_ptp_init_hw`, `ice_ptp_init_phc`, `ice_ptp_init_time`, `ice_ptp_write_incval`, `ice_ptp_write_incval_locked`, `ice_ptp_adj_clock`, `ice_read_phy_tstamp`, `ice_clear_phy_tstamp`, `ice_get_phy_tx_tstamp_ready`, `ice_check_phy_tx_tstamp_ready`, `ice_ptp_reset_ts_memory`, `ice_ptp_one_port_cmd`, `ice_ptp_lock`, `ice_ptp_unlock`, and `ice_get_ptp_src_clock_index`.

Family-specific exported helpers include E82x calibration and interrupt APIs (`ice_stop_phy_timer_e82x`, `ice_start_phy_timer_e82x`, `ice_phy_cfg_tx_offset_e82x`, `ice_phy_cfg_rx_offset_e82x`, `ice_phy_cfg_intr_e82x`, `ice_ptp_clear_phy_offset_ready_e82x`, quad register helpers), E825C/ETH56G APIs (`ice_stop_phy_timer_eth56g`, `ice_start_phy_timer_eth56g`, `ice_phy_cfg_intr_eth56g`, `ice_phy_cfg_ptp_1step_eth56g`, `ice_ptp_phy_soft_reset_eth56g`, `ice_ptp_read_tx_hwtstamp_status_eth56g`), and E810 CGU/SMA APIs (`ice_read_sma_ctrl`, `ice_write_sma_ctrl`, `ice_ptp_read_sdp_ac`, `ice_cgu_get_num_pins`, `ice_cgu_get_pin_type`, `ice_cgu_get_pin_freq_supp`, `ice_cgu_get_pin_name`, `ice_get_cgu_state`, `ice_get_cgu_rclk_pin_info`, `ice_cgu_get_output_pin_state_caps`).

Core dispatch is keyed by `hw->mac_type`: `ICE_MAC_E810`, `ICE_MAC_E830`, `ICE_MAC_GENERIC` for E82x/E823, and `ICE_MAC_GENERIC_3K_E825` for ETH56G. The code also uses `hw->device_id`, `hw->cgu_part_number`, `hw->func_caps.ts_func_info`, `hw->ptp`, and link state from `hw->port_info->phy.link_info`.

## Control Flow

PTP timer commands follow a common pattern. `ice_ptp_init_time`, `ice_ptp_write_incval`, or `ice_ptp_adj_clock` first write source timer shadow registers such as `GLTSYN_SHTIME_*` or `GLTSYN_SHADJ_*`. They then call family-specific PHY preparation helpers to write matching PHY shadow registers. Finally `ice_ptp_tmr_cmd` calls `ice_ptp_src_cmd`, `ice_ptp_port_cmd`, and `ice_ptp_exec_tmr_cmd` so source and PHY timers apply the command synchronously through `GLTSYN_CMD_SYNC`.

`ice_ptp_src_cmd` and `ice_ptp_exec_tmr_cmd` route non-primary functions to the primary hardware where needed. `ice_ptp_exec_tmr_cmd` serializes access to `GLTSYN_CMD_SYNC` with `pf->adapter->ptp_gltsyn_time_lock`. Wider PTP operations that cannot overlap use the hardware semaphore implemented by `ice_ptp_lock` and `ice_ptp_unlock` through `PFTSYN_SEM`.

For E82x, `ice_start_phy_timer_e82x` stops the PHY timer, configures lane type, UI conversion, PAR/PCS conversion, programs TIMETUS from current source incval, issues `ICE_PTP_INIT_INCVAL`, toggles `P_REG_PS` reset/start/clock/load bits, executes sync commands, and finally calls `ice_sync_phy_timer_e82x`. Vernier calibration is completed later by `ice_phy_cfg_tx_offset_e82x` and `ice_phy_cfg_rx_offset_e82x`, which poll offset-valid registers, calculate fixed and measured offsets, write total offsets, and mark `P_REG_TX_OR`/`P_REG_RX_OR` ready.

For ETH56G/E825C, `ice_start_phy_timer_eth56g` stops timestamp readiness, configures PAR/PCS, one-step PTP, MAC TSU config, writes incval into `PHY_REG_TIMETUS_*`, issues init-incval for the port, syncs the PHY timer against the PHC, and sets Tx/Rx offset-ready registers. ETH56G also supports sideband access to PTP, memory, XPCS, MAC, and GPCS resource spaces, one-step peer delay, bitslip/deskew offset computation, timestamp interrupt status, and PHY soft reset.

For E810, the code accesses an external PHY over SBQ, or through low-latency firmware proxy registers when capabilities advertise low-latency timestamp read or timer update. E810 PHC init enables PHY time sync with `ETH_GLTSYN_ENA`, timestamp reads come from external PHY timestamp banks, and PHY commands are written through `E810_ETH_GLTSYN_CMD`. E830 is simpler for several operations: PHC time and incval are written directly, timestamp readiness is read from E830 MAC registers, and port commands use `E830_ETH_GLTSYN_CMD`.

CGU/DPLL control flow is table-driven. Device IDs select board-specific pin description arrays. `ice_get_cgu_state` fetches raw DPLL status from firmware, maps it to Linux DPLL lock states, and preserves holdover semantics based on the previously reported state. Recovered clock pin discovery is device-specific and may inspect E810 C827 topology.

## State And Persistence Behavior

The file persists no disk state. It mutates device state in MMIO registers, PHY registers reachable through sideband queue messages, NVM-read-derived configuration, GPIO expanders, timestamp memory banks, PHY offset-ready flags, and DPLL state reported by firmware. Timestamp memory is explicitly reset for E82x quads and ETH56G ports; E810 reset is a no-op in the generic reset entry point.

`hw->ptp` stores family parameters such as number of logical ports, ports per PHY, ETH56G one-step flags, peer delay, SFD mode, and E810 low-latency waitqueue state. `hw->func_caps.ts_func_info` determines the owned and associated PHC timer indices. E82x `time_ref` in capabilities is mutable through inline helpers in the header and feeds PLL frequency/incval calculations.

Concurrency state is important. `PFTSYN_SEM` is a hardware semaphore, `ptp_gltsyn_time_lock` serializes sync-command writes, and E810 low-latency proxy access waits on `ptp.phy.e810.atqbal_wq` while `ATQBAL_FLAGS_INTR_IN_PROGRESS` is set. Failure to respect these locks risks corrupt timer updates or racing firmware-assisted timestamp reads.

## Dependencies And Integration Points

The file depends on `ice_common.h` for register helpers, admin queue helpers, NVM/GPIO/CGU commands, and `ice_sbq_rw_reg`; on `ice_ptp_hw.h` for exported prototypes and register macros; and on `ice_ptp_consts.h` for timing and calibration tables such as `e82x_time_ref`, `e822_vernier`, `eth56g_phy_res`, and `eth56g_mac_cfg`.

Main callers are PTP control code in `ice_ptp.c`, timestamp transmit/interrupt paths, E82x calibration work, DPLL integration, and board feature code for SMA/SDP/recovered clock support. The sideband message ABI is defined by `ice_sbq_cmd.h` and implemented in `ice_common.c`.

## Risks And Edge Cases

The largest risk is hardware-family divergence. E810, E830, E82x, and ETH56G differ in timestamp layout, command registers, PHY access mechanism, valid-bit behavior, and shadow-register semantics. A generic entry point must route to the correct implementation or return `-EOPNOTSUPP`.

Timer updates are sensitive to ordering. Source and PHY shadow registers must be prepared before the sync command, and stale port commands are avoided by `ice_ptp_one_port_cmd` programming non-target ports to `ICE_PTP_NOP`. Bugs here can desynchronize PHC and PHY timers or apply old commands to unrelated ports.

Calibration arithmetic is overflow-prone. The E82x Vernier functions intentionally divide before multiplying in several places. ETH56G fixed-point Q9 offset logic masks and combines integer/fractional fields. Small mistakes in masks, shifts, link-speed classification, FEC handling, or PMD alignment can cause timestamp bias without obvious functional failures.

Sideband and firmware paths can fail or time out. Many functions propagate errors from `ice_sbq_rw_reg`, NVM reads, GPIO access, and `read_poll_timeout*`; callers must handle `-EBUSY`, `-EINVAL`, `-EIO`, and `-EOPNOTSUPP`. E82x Tx/Rx offset calibration can legitimately return `-EBUSY` until packets have exercised the PHY.

## Test Signals

Useful signals include PHC initialization success for every supported `mac_type`, successful `ice_ptp_init_time`/`ice_ptp_write_incval`/`ice_ptp_adj_clock` cycles, absence of Tx/Rx PHY timer mismatch warnings after sync, E82x offset calibration eventually logging completion after traffic, correct `ice_get_phy_tx_tstamp_ready` bitmaps by family, timestamp reads clearing/reusing memory indices, and DPLL pin enumeration matching the board. Fault injection around SBQ, NVM, low-latency proxy timeouts, invalid ports/quads, and unsupported device IDs should return documented errors without leaving locks held.
