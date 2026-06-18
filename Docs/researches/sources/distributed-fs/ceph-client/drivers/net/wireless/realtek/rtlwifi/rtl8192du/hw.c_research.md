# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/hw.c

## Purpose
Implements RTL8192DU USB hardware initialization, register get/set callbacks, network-mode and BSSID filtering, beacon/TSF handling, power-off/card-disable sequences, and chip-version reporting. This is the central USB hardware lifecycle file for the DU variant.

## Important APIs, Types, And Functions
Public callbacks include `rtl92du_get_hw_reg()`, `rtl92du_set_hw_reg()`, `rtl92du_hw_init()`, `rtl92du_card_disable()`, `rtl92du_enable_interrupt()`, `rtl92du_disable_interrupt()`, `rtl92du_set_network_type()`, `rtl92du_set_check_bssid()`, `rtl92du_set_beacon_related_registers()`, `rtl92du_set_beacon_interval()`, `rtl92du_update_interrupt_mask()`, `rtl92du_read_chip_version()`, and `rtl92du_linked_set_reg()`. Private helpers cover beacon-control shadowing, queue reserved pages, TX buffer boundary, LLT table setup, USB endpoint queue priority mapping, WMAC/adaptive/EDCA/retry/operation/beacon/AMPDU initialization, MAC power-on, media status, and adapter power-off.

## Control Flow
`rtl92du_hw_init()` locks `mutex_for_hw_init`, resets IQK results, initializes MAC power and coexistence, builds the LLT table, downloads firmware, configures MAC tables, assigns reserved pages based on USB output endpoints and MAC/PHY mode, initializes queue priority and buffer boundaries, configures RX/TX DMA, RCR, adaptive control, EDCA, retry, operation mode, beacon parameters, AMPDU limits, LED hardware blinking, early mode, BB/RF tables, BBRF configuration, security CAM, IQK/LCK/PA bias, and DM. It then sets beacon control shadow state and performs final dual-PHY/scheduler tweaks.

`rtl92du_set_hw_reg()` handles DU-specific AC parameters, ACM control, RCR, join-BSS firmware report with beacon-control sequencing, TSF correction, and keep-alive no-op, delegating unknown variables to common rtl8192d code. Network type changes flow through `_rtl92du_set_media_status()`, which stops/resumes TX beacon, adjusts beacon subfunctions, writes MSR mode bits, controls LED, and sets beacon configuration.

Power-off starts in `rtl92du_card_disable()`: mark no link, set media status unspecified, pause TX, clear CR, disable RF, reset BB/MAC as allowed by MAC/PHY mode, call `rtl92du_phy_check_poweroff()`, then `_rtl92du_poweroff_adapter()` resets firmware/MCU, GPIO, LEDs, analog sequence, and power-control locking.

## State And Persistence
Maintains `rtlusb->reg_bcn_ctrl_val` as a software shadow of `REG_BCN_CTRL`; updates `mac->rx_conf`, link/opmode state, `rtlhal->last_hmeboxnum`, `rtlpriv->psc.fw_current_inpsmode`, `rtlphy->rf_mode`, `rfreg_chnlval[]`, and `ppsc->rfpwr_state`. Hardware-persistent state includes LLT entries, TX page boundaries, queue maps, RCR, MSR, EDCA, beacon timing, firmware, BB/RF registers, CAM security, and power-off markers.

## Dependencies And Integration Points
Depends on rtlwifi USB glue, CAM/security helpers, common rtl8192d firmware, hardware, PHY, and DM helpers, local DU PHY/RF/TRX/DM/FW headers, mac80211 interface types, and USB endpoint topology (`out_ep_nums`, `out_queue_sel`). It is used by DU software operation wiring and interacts heavily with firmware H2C commands.

## Risks
Initialization ordering is critical: LLT, firmware, MAC tables, queue pages, BB/RF, security, and calibration have hardware dependencies. Firmware download failure handling is subtle: hardware init can continue or fail depending on the error and register `0x1c5`. Beacon control is shadowed in software, so direct writes outside `_rtl92du_set_bcn_ctrl_reg()` can desynchronize state. Interrupt functions are no-ops for USB, so callers must not expect PCI-style masks. Power-off resets MCU/MAC/GPIO/LEDs and dual-MAC power markers; wrong interface-index handling can affect the peer MAC.

## Test Signals
Probe with one, two, and three USB OUT endpoint configurations; firmware download; LLT initialization; station/AP/adhoc mode changes; BSSID filtering; join-BSS report; TSF correction; beacon interval programming; 2.4G/5G BB/RF init; IQK/LCK; security CAM use; and card disable/unplug/suspend. Useful logs include "Init MAC failed", "Init LLT failed", firmware readiness, and no hangs during MCU reset or power off.
