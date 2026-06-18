# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/conf.h

## Purpose
Defines the WiLink 8 private configuration ABI layered on top of common `wlcore_conf`. It covers configuration file identity, PHY/MAC board parameters, HT mode, AP sleep, and SoftGemini coexistence parameter indexes.

## Important APIs, types, and functions
- `WL18XX_CONF_MAGIC`, `WL18XX_CONF_VERSION`, `WL18XX_CONF_SIZE`, and `WL18XX_CONF_MASK` validate binary configuration files.
- `struct wl18xx_mac_and_phy_params` is copied wholesale to firmware PHY init memory and includes FEM/antenna/clock/power-limit/trace-loss/board-type fields.
- `enum wl18xx_ht_mode` and `struct wl18xx_ht_settings` choose default, wide SISO40, or SISO20 HT capabilities.
- `struct conf_ap_sleep_settings` and `struct wl18xx_priv_conf` define wl18xx-private configuration blocks.
- `enum wl18xx_sg_params` maps WiLink 8 SoftGemini/BT coexistence parameter indexes.

## Control flow
No executable flow. `wl18xx/main.c` loads this layout from firmware configuration files or defaults, lets module parameters override select fields, and writes the PHY block to firmware.

## State and persistence behavior
Configuration is stored in `struct wl18xx_priv` for a device instance. A binary firmware config file persists outside the driver and is validated by magic/version/size. The PHY subset is copied into device memory during boot.

## Dependencies and integration points
Depends on common `WLCORE_CONF_VERSION`, `WLCORE_CONF_SIZE`, and wlcore SoftGemini parameter capacity. Integrated by `wl18xx_load_conf_file()`, `wl18xx_conf_init()`, `wl18xx_set_mac_and_phy()`, `wl18xx_acx_ap_sleep()`, and debugfs config dump.

## Risks and test signals
Risks include binary config size/version mismatch, invalid board/FEM/antenna parameters, wrong HT mode advertisement, and PHY payload exceeding `WL18XX_PHY_INIT_MEM_SIZE`. Test signals include boot with and without external config file, module parameter overrides, 2.4/5 GHz antenna enablement, AP sleep ACX programming, and debugfs `conf` output matching expected size/magic/version.
