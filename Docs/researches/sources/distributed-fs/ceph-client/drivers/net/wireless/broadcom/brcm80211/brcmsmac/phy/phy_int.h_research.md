# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_int.h

## Purpose
`phy_int.h` is the private internal contract for the `brcmsmac` PHY subsystem. It exposes common PHY constants, rate-index layouts, calibration states, noise/interference structures, shared and per-PHY state structures, backend dispatch callbacks, table/radio descriptor formats, register helper prototypes, and NPHY/LCNPHY internal function prototypes.

Unlike `phy_hal.h`, this header exposes `struct brcms_phy` internals and is intended for common PHY code, NPHY code, LCNPHY code, table code, and radio code.

## Important APIs, Types, and Data
- PHY selection/version: `PHY_VERSION`, `LCNXN_BASEREV`, `ISNPHY(pi)`, and `ISLCNPHY(pi)`.
- Math and gain helpers: `PHY_GET_RFATTN()`, `PHY_GET_PADMIX()`, `PHY_GET_RFGAINID()`, `PHY_SAT()`, `PHY_SHIFT_ROUND()`, and `PHY_HW_ROUND()`.
- Channel/rate layout: 2G/5G frequency macros, 5 GHz band group constants, `TXP_FIRST_*`, `TXP_LAST_*`, `TXP_MCS_32`, `TXP_NUM_RATES`, and `ADJ_PWR_TBL_LEN`.
- Noise/calibration constants: noise sample modes/windows/log sizes, TSSI table sizes, PAPD table size, power minima, spur-avoidance modes, software timers, periodic-calibration delays, and multi-phase calibration state IDs.
- Hold-state query macros: `SCAN_INPROG_PHY()`, `PLT_INPROG_PHY()`, `ASSOC_INPROG_PHY()`, `SCAN_RM_IN_PROGRESS()`, `PHY_MUTED()`, and `PUB_NOT_ASSOC()`.
- Data descriptors: `struct phytbl_info`, `struct phy_table_info`, `struct radio_regs`, `struct radio_20xx_regs`, and `struct lcnphy_radio_regs`.
- Runtime state: `struct shared_phy`, `struct brcms_phy_pub`, `struct phy_func_ptr`, and the large `struct brcms_phy`.
- Calibration state structures: `struct nphy_iq_comp`, `struct nphy_txpwrindex`, `struct txiqcal_cache`, `struct nphy_pwrctrl`, `struct nphy_txgains`, `struct nphy_noisevar_buf`, `struct rssical_cache`, and `struct lcnphy_cal_results`.
- Internal prototypes: common register/table helpers, radio init helpers, dummy TX, PAPD epsilon decode, calibration timer reset/restart, NPHY attach/init/channel/TX-power/RSSI/calibration helpers, and LCNPHY attach/init/channel/TX-power/TSSI/temperature/IQ/LO/tone/RX-power helpers.
- LCN constants: LCN power table IDs, table size, max power index, and `LCNPHY_TX_PWR_CTRL_OFF/SW/HW/TEMPBASED`.

## Control Flow
The header defines the internal control model. Common attach code allocates `struct brcms_phy`, fills public identity, initializes common fields, and calls a backend attach routine. The backend attach routine allocates type-specific state, fills `pi->pi_fptr`, and reads board data. Later common HAL entry points perform shared preconditions and dispatch to function pointers such as `init`, `calinit`, `chanset`, `txpwrrecalc`, `txiqccget`, `txiqccset`, `txloccget`, `radioloftget`, `rxsigpwr`, and `detach`.

PHY table IO flows through `struct phytbl_info`: callers specify table ID, offset, width, length, and buffer, then common table helpers write or read hardware table registers. Calibration flows use state fields in `struct brcms_phy`, NPHY caches, and LCN private state to preserve coefficients across recalibration.

## State and Persistence Behavior
`struct shared_phy` and `struct brcms_phy` are runtime-only objects. They cache chip and board identity, PHY/radio identity, shim, clock/up state, channel/bandwidth, chain masks, antenna diversity, calibration flags, noise windows, SROM-derived power limits, regulatory/user/target power arrays, backend-specific calibration state, and table scratch fields.

No state is persisted outside the driver lifetime. Board data comes from SPROM/SROM and is cached in memory. Hardware mirror fields can become stale after failed register writes or hardware reset until reinitialized.

## Dependencies and Integration Points
- Includes `types.h`, `brcmu_utils.h`, and `brcmu_wifi.h`.
- Depends on Broadcom channel, rate, board flag, and PHY-type macros from included headers and surrounding implementation includes.
- Used by `phy_cmn.c`, `phy_lcn.c`, NPHY sources, PHY table sources, and radio code.
- Connects to Linux/bus types such as `struct bcma_device`, `struct wiphy`, `struct d11rxhdr`, and `struct wlapi_timer`.

## Risks and Edge Cases
- `struct brcms_phy` mixes common, NPHY, LCN, and legacy state, making stale-field and wrong-PHY-type access risks high.
- Rate-table constants must remain aligned with public `WL_TX_POWER_RATES` and firmware/shared-memory ordering.
- Several macros perform shifts and can evaluate inputs in ways that are unsafe with side effects or invalid ranges.
- Backend callbacks are optional and must be null-checked by common code; missing callbacks can turn requests into silent no-ops.
- Hardware-derived indices for cores, rates, channels, and gain tables need implementation-level bounds checks.
- Multi-phase calibration progress is represented by small state fields; incorrect reset or timer scheduling can leave calibration pending.

## Test Signals
- Full PHY build matrix to catch signature, include-order, and layout drift.
- Static analysis for array indexing, signed shifts, optional callback handling, and PHY-type-specific field access.
- Attach tests verifying `pi_fptr` population for NPHY and LCNPHY.
- Calibration tests for NPHY multi-phase states and LCN calibration caches.
- TX power tests across all `TXP_*` boundaries, including MCS32 and CDD/STBC/MIMO groups.
- Noise/RSSI tests for per-core window wrap and measurement state.
