# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-mt6370-rgb.c

Purpose: MediaTek/Richtek MT6370/MT6371/MT6372 RGB indicator driver. It supports independent current-sink LEDs and virtual multicolor LEDs with brightness, PWM blink, and breath-pattern modes.

Important APIs, types, and functions: `struct mt6370_priv` stores mutex, parent regmap, regmap fields, chip-specific field/range/pdata tables, active LED bitmap, and LED array. `mt6370_check_vendor_info()` selects MT6372 versus common register maps. Brightness helpers set current, duty, frequency, and mode fields. `mt6370_gen_breath_pattern()` converts six LED pattern entries into three packed bytes. Separate callback families implement multicolor (`mt6370_mc_*`) and single ISINK (`mt6370_isnk_*`) behavior.

Control flow: probe counts child nodes, gets parent regmap, selects chip metadata from vendor ID, bulk-allocates regmap fields, then parses each child. RGB/MULTI colors become virtual multicolor devices with child channels; other nodes become single current sinks. Registration initializes max brightness from `led-max-microamp`, default state, CHRIND software control for ISINK4, and the proper LED class device type.

State and persistence: `leds_active` prevents duplicate channel use across single and multicolor devices. Hardware mode/current/enable state persists in PMIC registers. Default-state keep reads current level and enable bit before programming the LED.

Dependencies and integration points: platform child of MT6370 MFD, parent regmap, regmap fields, linear ranges, LED/multicolor/pattern APIs, fwnode properties, and compatible `mediatek,mt6370-indicator`.

Risks and test signals: test vendor-specific register maps and ranges, multicolor child validation, duplicate channel detection including virtual RGB bit use, frequency out-of-range returning `-EOPNOTSUPP`, breath pattern length handling, enable toggling to synchronize timing, and ISINK4 charger-indicator takeover.
