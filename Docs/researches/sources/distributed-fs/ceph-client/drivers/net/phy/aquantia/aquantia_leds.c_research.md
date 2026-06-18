# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_leds.c

## Purpose
Implements Aquantia PHY LED class callbacks for forced brightness, hardware netdev trigger rules, and active-low/active-high polarity control.

## Important APIs, Types, and Functions
Exports `aqr_phy_led_brightness_set`, `aqr_phy_led_hw_is_supported`, `aqr_phy_led_hw_control_get`, `aqr_phy_led_hw_control_set`, `aqr_phy_led_active_low_set`, and `aqr_phy_led_polarity_set`. It supports up to `AQR_MAX_LEDS` LEDs and netdev triggers for link, link speeds 100M through 10G, RX, and TX.

## Control Flow and State
Brightness writes clear link/activity hardware rules and optionally force the LED on. Hardware-control set maps requested trigger bits into `AQR_LED_PROV(index)` link and activity bits; get reverses that mapping from hardware. Polarity set validates requested PHY LED modes, records forced active-low/high choices in `aqr107_priv` so `aquantia_main.c` can restore them after reset, and writes the drive register through `aqr_phy_led_active_low_set`.

## Dependencies and Integration Points
Depends on phylib LED callbacks, Aquantia LED provisioning/drive registers from `aquantia.h`, and the `aqr107_priv` LED polarity bitmaps. Driver-table entries in `aquantia_main.c` expose these callbacks for supported AQR devices.

## Risks and Test Signals
Risks include unsupported trigger combinations being accepted in future without hardware support, brightness changes clearing hardware rules, polarity state only persisting when forced modes are set, and off-by-one LED index validation. Test signals include LED class brightness, hardware trigger set/get for each speed/activity bit, active-low/high mode persistence across soft reset, and invalid index/mode rejection.
