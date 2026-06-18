# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/led.h

Purpose: `led.h` declares the RTL8723AE software LED operations used by the hardware layer and operation table.

Important APIs/types: the header exposes `rtl8723e_sw_led_on`, `rtl8723e_sw_led_off`, and `rtl8723e_led_control`, parameterized by `struct ieee80211_hw`, `enum rtl_led_pin`, and `enum led_ctl_mode`.

Control flow: no executable flow; it is a declaration boundary between `led.c`, `hw.c`, and `sw.c`.

State and persistence: no state is declared. Implementations use `rtlpriv->ledctl` and device LED registers.

Dependencies/integration: relies on prior inclusion of rtlwifi/mac80211 types. `sw.c` assigns `rtl8723e_led_control` to `.led_control`; `hw.c` calls the low-level on/off helpers during LED refresh.

Risks: include guard name says `RTL92CE`, not `RTL8723E`, which is harmless functionally but can confuse maintenance. Prototype drift would break builds.

Test signals: compile coverage plus runtime LED state transitions through the HAL operation table.
