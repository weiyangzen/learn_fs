# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_xgbepcsr.c

## Purpose
`netcp_xgbepcsr.c` initializes the TI KeyStone XGBE PCS-R/SerDes block used by the NetCP 10G Ethernet subsystem. It applies fixed PHY-B CMU, lane, and common-lane register programming sequences, enables the PLL and two XGMII lanes, waits for PLL lock, enables XGMII ports in the switch registers, and performs a short link-lane recovery check.

This is a hardware bring-up helper for `netcp_ethss.c`; it exports only `netcp_xgbe_serdes_init()`.

## Important APIs, Types, And Functions
`struct serdes_cfg` stores register offset, value, and mask triples. Static configuration arrays `cfg_phyb_1p25g_156p25mhz_cmu0`, `cfg_phyb_10p3125g_156p25mhz_cmu1`, `cfg_phyb_10p3125g_16bit_lane`, `cfg_phyb_10p3125g_comlane`, and `cfg_cm_c1_c2` encode the hard-coded SerDes setup.

The public entry point is `netcp_xgbe_serdes_init(void __iomem *serdes_regs, void __iomem *xgbe_regs)`. It checks whether COMLANE appears active, toggles POR reset if needed, and then calls `netcp_xgbe_serdes_config()`.

Configuration helpers include `netcp_xgbe_serdes_cmu_init()`, `netcp_xgbe_serdes_lane_config()`, `netcp_xgbe_serdes_com_enable()`, `netcp_xgbe_serdes_lane_enable()`, `netcp_xgbe_serdes_pll_disable()`, `netcp_xgbe_serdes_pll_enable()`, `netcp_xgbe_wait_pll_locked()`, and `netcp_xgbe_serdes_enable_xgmii_port()`.

Lane diagnostics and recovery helpers include `netcp_xgbe_serdes_read_tbus_val()`, `netcp_xgbe_serdes_write_tbus_addr()`, `netcp_xgbe_serdes_read_select_tbus()`, `netcp_xgbe_serdes_reset_cdr()`, `netcp_xgbe_check_link_status()`, and `netcp_xgbe_serdes_check_lane()`.

## Control Flow
`netcp_xgbe_serdes_init()` reads SerDes offset `0xa00`. If any low COMLANE bits are set, it logs a debug reset message and calls `netcp_xgbe_reset_serdes()`, which toggles `POR_EN` in `PCSR_CPU_CTRL_OFFSET` with short sleeps. It then enters `netcp_xgbe_serdes_config()`.

`netcp_xgbe_serdes_config()` disables the PLL, applies CMU0 and CMU1 arrays, applies the lane configuration array to both lanes with a `0x200 * lane` stride, disables per-lane autonegotiation and link training, applies common-lane configuration, applies CM/C1/C2 setup for both lanes, enables the PLL, writes lane enable/rate values for both lanes, and waits up to 500 ms for both SGMII status lock bits in the XGBE switch register block.

If PLL lock succeeds, the function writes `0x03` to the XGBE control register to enable both XGMII ports, then calls `netcp_xgbe_serdes_check_lane()`. Lane checking calls `netcp_xgbe_check_link_status()` up to two times separated by 100 ms. That routine checks loss, PCS-R block lock, block error saturation, and a small state machine per lane. When block errors are saturated or block lock is missing, it can reset CDR if TBUS DLPF appears out of center; when link is good it forces signal detect on.

`netcp_xgbe_serdes_config()` returns the PLL-lock result. The later lane-check timeout is logged but not propagated because the return value remains the PLL result.

## State And Persistence Behavior
There is no persistent software state. All state is in hardware registers: CMU/lane/common-lane SerDes programming, PLL enable, lane enable/rate registers, XGBE control bits, PCS-R block error counters, signal-detect overrides, CDR reset bits, and POR state.

The lane-check function keeps local `current_state[2]` and `lane_down[2]` arrays only for the duration of initialization. The static configuration tables are immutable driver data.

## Dependencies And Integration Points
The file includes `netcp.h` for MMIO, bit, timing, and logging helpers. It is integrated from `netcp_ethss.c` in the XGBE probe path after XGBE subsystem, switch-module, and SerDes resources are mapped.

The code assumes a two-lane PHY-B layout, 156.25 MHz reference clock, 10.3125G lane configuration, and XGBE switch status offsets at `XGBE_SGMII_1_OFFSET` and `XGBE_SGMII_2_OFFSET`. Comments call out some EVM plus RTM-BOC-specific equalization settings.

## Risks And Edge Cases
The configuration is fixed and board-specific. Different reference clocks, lane counts, PHY variants, or board loss characteristics may need different magic values. `PHY_A(serdes)` is hard-coded to `0`, so only the PHY-B TBUS path is active.

PLL lock failure returns `-ETIMEDOUT`, but lane link failure after PLL lock is not propagated to the caller. This means probe can continue even when `netcp_xgbe_serdes_check_lane()` times out. The lane check itself retries only twice, so it is a weak readiness signal.

`MASK_WID_SH(w, s)` uses `1 << w`, which is safe for the current small widths but would overflow if reused for 32-bit masks. TBUS addressing remaps lane select values for two-lane PHY-B; extending to other layouts requires care.

## Test Signals
Hardware validation should confirm SerDes init on cold boot and after an already-active COMLANE reset, PLL lock within 500 ms, XGMII control enabling both ports, PCS-R block lock on both lanes, block error counter clearing, and stable link after repeated probe/remove cycles. Useful logs include "XGBE serdes not locked: time out", "XGBE: timeout waiting for serdes link up", lane-down debug messages, and CDR centering debug output.
