# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-gpio.c

## Purpose

`mt8186-afe-gpio.c` manages MT8186 audio pinctrl states for ADDA, I2S, TDM, and PCM pins. DAPM events and DAI code call it to switch external audio pins between active and inactive states.

## Important APIs, Types, and Functions

The private `enum mt8186_afe_gpio` enumerates every on/off pinctrl state: ADDA MOSI/MISO clocks and data, I2S0-3, TDM, and PCM. `struct audio_gpio_attr` stores a state name, preparation flag, and `pinctrl_state *`. `aud_gpios[]` maps enum entries to device-tree pinctrl state names. `mt8186_afe_gpio_init()` gets the device pinctrl, looks up each state, marks available states prepared, and initializes supported DAI pins to disabled states. `mt8186_afe_gpio_request()` is the exported switch entry point. It serializes with `gpio_request_mutex`, maps DAI ID plus uplink flag to a pinctrl state, and calls `mt8186_afe_gpio_select()`.

## Control Flow and State

Initialization stores a global `aud_pinctrl` pointer and persistent state descriptors in `aud_gpios[]`. Request flow is `mt8186_afe_gpio_request()` -> ADDA-specific helper or generic state select -> `pinctrl_select_state()`. ADDA toggles clock and data pins in an ordered sequence, with different MOSI/MISO paths for downlink and uplink.

## Dependencies and Integration Points

This file depends on Linux pinctrl and DAI IDs from `mt8186-afe-common.h`. ADDA DAPM events call it before/after playback and capture. I2S, TDM, and PCM DAI implementations use the same request API. Device tree must provide pinctrl state names that match `aud_gpios[]`.

## Risks

`aud_pinctrl` and `aud_gpios[]` are global, so multiple MT8186 AFE instances would share state. Missing pinctrl states are logged at debug level and only fail later if requested. `mt8186_afe_gpio_init()` calls `mt8186_afe_gpio_request()` during initialization even for states that may not exist, intentionally tolerating optional pins but making failures easy to overlook. Header comments mention mt6833, which is cosmetic but can confuse maintenance.

## Test Signals

Probe should show successful pinctrl lookup for expected board states. Runtime testing should verify pin transitions with ADDA playback/capture, each I2S bus, TDM, and PCM paths. Missing or misspelled device-tree state names surface as `gpio type ... not prepared` debug logs and silent audio pin inactivity.
