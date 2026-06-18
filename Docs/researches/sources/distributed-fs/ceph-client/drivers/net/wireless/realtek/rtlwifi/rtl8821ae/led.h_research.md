# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/led.h

## Purpose

`led.h` declares the RTL8821AE/RTL8812AE software LED control interface. It is the header boundary between chip hardware code, the chip operations table, and `led.c`. The file contains only an include guard and function prototypes; it stores no state and defines no local types.

## Important APIs, Types, and Functions

The header declares five functions: `rtl8821ae_sw_led_on()`, `rtl8812ae_sw_led_on()`, `rtl8821ae_sw_led_off()`, `rtl8812ae_sw_led_off()`, and `rtl8821ae_led_control()`. The first four are hardware-specific direct LED register controls; `rtl8821ae_led_control()` is the policy-level LED action entry point that receives `enum led_ctl_mode`.

The prototypes depend on `struct ieee80211_hw`, `enum rtl_led_pin`, and `enum led_ctl_mode` being visible from previous includes, normally via rtlwifi `wifi.h`.

## Control Flow

The header itself has no control flow. Its intended flow is that generic rtlwifi or chip hardware code calls `rtl8821ae_led_control()` for action-based LED policy, while chip-local initialization code may call the hardware-specific direct on/off functions after determining `rtlhal->hw_type`. The direct functions should not be treated as generic LED policy because they bypass RF-off filtering.

## State and Persistence Behavior

No state is declared in the header. The functions declared here persist LED state through hardware register writes in `led.c` and depend on runtime state held in `rtlpriv->ledctl`, `rtlhal->hw_type`, and `ppsc->rfoff_reason`.

## Dependencies and Integration Points

`led.h` is included by `led.c` and `hw.c`. It integrates LED control with the broader RTL8821AE hardware lifecycle: media-state changes call the policy function, while MAC initialization refresh can call the direct hardware-specific functions. Like `hw.h`, this header relies on include order for type definitions rather than including the full mac80211/rtlwifi declarations itself.

## Risks and Edge Cases

The API exposes both direct hardware controls and policy-level control without documenting the difference. A caller using direct functions can turn LEDs on even when RF-off policy would suppress that action. There is no lock contract or register-side effect documentation. Signature drift between `led.h` and `led.c` would be caught at build time, but semantic drift in action handling requires hardware tests.

## Test Signals

Build coverage should ensure all declared prototypes match `led.c`. Runtime validation should confirm the chip ops table calls `rtl8821ae_led_control()` for normal LED policy and that direct functions are limited to chip-local refresh paths. Include-order tests or static analysis can catch consumers that include `led.h` before `struct ieee80211_hw` and LED enums are declared.
