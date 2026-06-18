# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/init.h

## Purpose
`init.h` declares the wlcore initialization entry points shared between core bring-up, AP/STA setup, and chip-specific code.

## Important APIs
Declarations include `wl1271_hw_init_power_auth()`, `wl1271_init_templates_config()`, `wl1271_init_pta()`, `wl1271_init_energy_detection()`, `wl1271_chip_specific_init()`, `wl1271_hw_init()`, `wl1271_init_vif_specific()`, `wl1271_init_ap_rates()`, `wl1271_ap_init_templates()`, and `wl1271_sta_hw_init()`.

## Control flow and integration
`wl1271_hw_init()` is the common full-hardware init sequence. `wl1271_init_vif_specific()` is called when a mac80211 vif needs firmware configuration. AP and STA helper declarations allow other modules to reuse mode-specific setup. Some declarations are implemented outside `init.c`, preserving a common init interface across wlcore components.

## State and persistence behavior
The header itself does not manage state. Implementations configure firmware state, templates, ACX settings, and per-vif runtime fields.

## Dependencies and risks
It depends on `wlcore.h` and mac80211 `ieee80211_vif` visibility through included wlcore definitions. Risks are stale declarations or missing implementations during chip split changes.

## Test signals
Compile/link coverage, successful probe-time hardware init, and successful STA/AP vif initialization validate this interface.
