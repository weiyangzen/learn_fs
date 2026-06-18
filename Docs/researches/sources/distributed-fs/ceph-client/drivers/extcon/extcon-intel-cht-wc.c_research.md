# sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel-cht-wc.c

## Purpose
`extcon-intel-cht-wc.c` manages USB ID/VBUS, charger detection, data-line muxing, optional VBUS boost, USB role switching, and optional power-supply reporting for Intel Cherry Trail Whiskey Cove PMIC power-source hardware.

## Important APIs, types, and functions
`struct cht_wc_extcon_data` tracks regmap, extcon device, optional role switch/regulator/power-supply, current USB type, previous cable, host state, and regulator state. Important helpers include `cht_wc_extcon_get_id()`, `cht_wc_extcon_get_charger()`, `cht_wc_extcon_pwrsrc_event()`, `cht_wc_extcon_set_phymux()`, `cht_wc_extcon_set_otgmode()`, `cht_wc_extcon_enable_charging()`, `cht_wc_extcon_sw_control()`, and board-specific role/regulator/power-supply setup.

## Control flow
Probe allocates/registers extcon state, applies model-specific quirks from the parent PMIC, optionally obtains the role switch and VBUS regulator, optionally registers a USB power-supply, enables PMIC software control, disables external charging initially, routes D+/D- to the PMIC when no host is detected, processes initial status, requests the power-source IRQ, and unmasks VBUS/USBID IRQs. IRQs read and later clear `CHT_WC_PWRSRC_IRQ`, then call `cht_wc_extcon_pwrsrc_event()`. That event reads ID/VBUS, enables OTG/boost and disables charging in host mode, otherwise enables charging and performs charger-type detection with an 800 ms timeout, updates extcon states, sets USB role, and notifies the power-supply if present.

## State and persistence behavior
The driver keeps `previous_cable`, `usb_host`, `usb_type`, and regulator state in memory while programming PMIC mux/control registers. No state is persisted beyond hardware register side effects during the driver lifetime.

## Dependencies and integration points
It depends on Intel SoC PMIC MFD data, regmap, extcon, power_supply, optional regulators, USB role-switch software nodes, and board model IDs. It reports both extcon cable states and, on selected boards, a USB power-supply used by charger drivers.

## Risks and edge cases
Board-specific quirks are central and regressions can cause battery drain, feedback loops, or wrong USB role. Charger detection falls back to SDP on timeout/failure. Host-mode 5V boost can create false VBUS detections, explicitly handled by skipping charger detection. Error paths after software control must disable it. Role-switch and regulator probe deferral affect selected models.

## Test signals
Test each PMIC model branch, host/device/none role transitions, no-VBUS detach, SDP/CDP/DCP/ACA charger detection and timeout fallback, power-supply property updates, external charger disable pin behavior, IRQ mask/clear behavior, and remove cleanup restoring hardware control.
