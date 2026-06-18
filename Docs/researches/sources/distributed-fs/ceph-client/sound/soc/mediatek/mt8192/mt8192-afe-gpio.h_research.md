# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-gpio.h

This header exposes the MT8192 AFE GPIO/pinctrl interface. `mt8192_afe_gpio_init(struct device *dev)` initializes pinctrl and caches available audio pin states. `mt8192_afe_gpio_request(struct device *dev, bool enable, int dai, int uplink)` toggles the relevant pin state for a backend DAI, with `uplink` selecting capture versus playback for ADDA-like paths.

It forward-declares `struct device`; callers include `mt8192-afe-common.h` for DAI ids. ADDA, I2S, TDM, and the platform probe path are the integration points. Runtime state is implemented in `mt8192-afe-gpio.c` as module-static caches.

Risks are the integer DAI id interface and runtime-only validation for invalid ids. Test signals are successful probe-time pinctrl initialization and DAPM event coverage for each DAI path that requests GPIO changes.
