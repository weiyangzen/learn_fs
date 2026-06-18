# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_hal.h

## Purpose
`phy_hal.h` is the public PHY hardware-abstraction contract exported from the Broadcom PHY layer to higher `brcmsmac` driver layers. It defines radio ID constants, calibration and hold/mute reason constants, transmit-power structures, channel-vector representation, shared attach parameters, and the callable PHY API used by MAC, channel, regulatory, scan, power-management, and statistics code.

The header hides `struct brcms_phy` internals. Higher layers interact through `struct shared_phy`, `struct brcms_phy_pub`, `struct phy_shim_info`, and D11/bcma handles.

## Important APIs, Types, and Functions
- Radio identity: `IDCODE_*` masks/shifts, `NORADIO_ID`, `BCM2055_ID`, `BCM2056_ID`, `BCM2057_ID`, and `BCM2064_ID`.
- Calibration reasons and modes: `PHY_PERICAL_DRIVERUP`, `PHY_PERICAL_WATCHDOG`, `PHY_PERICAL_PHYINIT`, BSS/channel/full-cal reasons, plus disable/single-phase/multi-phase/manual modes.
- Hold/mute flags: `PHY_HOLD_FOR_ASSOC`, `PHY_HOLD_FOR_SCAN`, `PHY_HOLD_FOR_RM`, `PHY_HOLD_FOR_PLT`, `PHY_HOLD_FOR_MUTE`, `PHY_HOLD_FOR_NOT_ASSOC`, `PHY_MUTE_FOR_PREISM`, and `PHY_MUTE_ALL`.
- Power constants: quarter-dBm scaling via `BRCMS_TXPWR_DB_FACTOR`, sentinel `BRCMS_TXPWR_MAX`, CCK/OFDM/MCS group sizes, and fixed noise-floor values.
- `struct txpwr_limits`: regulatory limits for CCK, OFDM, 20/40 MHz OFDM, SISO/CDD/STBC/MIMO MCS, and MCS32.
- `struct tx_power`: current power report containing flags, chanspecs, local constraints, antenna gain, RF core count, estimated output, user/regulatory/board limits, targets, and max target indexes.
- `struct brcms_chanvec`: bit-vector channel set.
- `struct shared_phy_params`: attach-time chip, board, SROM, core revision, unit, shim, vendor/device identity, and board flags.
- Lifecycle APIs: `wlc_phy_shared_attach()`, `wlc_phy_attach()`, `wlc_phy_detach()`.
- Runtime APIs: version/coreflag getters, hardware clock/up state updates, init/watchdog/down/cal-init, channel/radio/bandwidth operations, RSSI/noise/BIST, TX power get/set/limit/report, chain and antenna controls, hold/mute controls, and feature toggles.

## Control Flow
The header defines the public call graph rather than implementing it. Higher layers allocate shared PHY state, attach a PHY for a D11 core/band, then update hardware clock/up state and drive init, channel, watchdog, power, antenna, mute, and calibration operations through this API. `phy_cmn.c` implements most entry points and dispatches PHY-specific operations through private callbacks.

Regulatory code supplies `struct txpwr_limits` to `wlc_phy_txpower_limit_set()`. User power requests call `wlc_phy_txpower_set()`. RX paths call `wlc_phy_rssi_compute()`. Interrupt paths call `wlc_phy_noise_sample_intr()`. Periodic driver work calls `wlc_phy_watchdog()`.

## State and Persistence Behavior
This header declares exchange structures and opaque handles, but stores nothing. `struct shared_phy_params` is copied into runtime `struct shared_phy`. `struct txpwr_limits`, `struct tx_power`, and `struct brcms_chanvec` are caller-visible transient structures. No disk persistence is implied; PHY identity and power constraints are reconstructed from hardware and board data.

The API can mutate runtime hardware and cached state indirectly: channel, bandwidth, radio/anacore state, chain masks, antenna diversity, calibration mode, TX power limits/targets, hold bits, and mute bits.

## Dependencies and Integration Points
- Includes `brcmu_utils.h`, `brcmu_wifi.h`, and `phy_shim.h`.
- Uses external types such as `struct bcma_device`, `struct wiphy`, `struct d11rxhdr`, `struct d11regs`, and `struct phy_shim_info`.
- Implemented by `phy_cmn.c` with support from private declarations in `phy_int.h`, NPHY code, and LCNPHY code.
- Integrated with MAC/regulatory/channel/scan/power code through this public interface.

## Risks and Edge Cases
- Power units are mostly quarter-dBm but represented as plain integer types, making unit confusion likely.
- `struct tx_power` must remain synchronized with `WL_TX_POWER_RATES` and internal rate layout.
- Hold/mute flags are reason bits; unbalanced set/clear calls can suppress calibration or measurements.
- Some declared APIs are implemented elsewhere, and some implementations are stubs in this codebase, so call sites should verify actual behavior.
- Boolean return values such as `wlc_phy_get_phyversion()` may indicate API success rather than hardware freshness.

## Test Signals
- API compile coverage across all users of `phy_hal.h`.
- Attach/init/watchdog/down lifecycle smoke tests.
- Channel set/get and valid-channel bit-vector tests.
- TX power limit, target, report, and hardware-control flag tests across CCK/OFDM/MCS groups.
- RSSI/noise interrupt tests and hold/mute bit behavior tests.
- Chain/antenna diversity and radio/anacore state transition tests.
