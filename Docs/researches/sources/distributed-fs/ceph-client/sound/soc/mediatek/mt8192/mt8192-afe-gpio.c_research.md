# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-gpio.c

This file manages audio pinctrl state selection for ADDA, I2S, TDM, VOW, and clock pins. `enum mt8192_afe_gpio` enumerates on/off pin states, and `aud_gpios[]` maps each enum to a pinctrl state name plus cached `pinctrl_state`. The exported APIs are `mt8192_afe_gpio_init()` and `mt8192_afe_gpio_request()`.

Initialization obtains the device pinctrl, looks up every known state, marks prepared states, enables `aud_clk_mosi_on`, and initializes ADDA playback/capture pins off. Runtime callers enter `mt8192_afe_gpio_request()`, take `gpio_request_mutex`, switch on the DAI id, and select on/off states for ADDA, ADDA_CH34, I2S0/1/2/3/5/6/7/8/9, TDM, or VOW. ADDA helpers distinguish uplink from downlink; VOW toggles both clock and data states.

State is module-static: global `aud_pinctrl`, `aud_gpios[]`, and the mutex. This assumes a single audio pinctrl instance. Dependencies are Linux pinctrl and DAI ids from `mt8192-afe-common.h`. A key risk is that `mt8192_afe_gpio_request()` ignores most inner selection return values and often returns success even if a pin state was missing. Test signals include DT pinctrl lookup coverage, DAPM power path tests for every DAI id, and board-level pin waveform or loopback validation.
