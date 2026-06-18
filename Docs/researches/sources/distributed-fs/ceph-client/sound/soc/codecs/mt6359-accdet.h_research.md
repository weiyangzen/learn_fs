# sources/distributed-fs/ceph-client/sound/soc/codecs/mt6359-accdet.h

## Purpose

This header defines the public and private data contract for the MT6359 accessory detector. It provides jack/button masks, headset mode constants, state enums, device-tree configuration structures, private driver state, and the exported jack-detection enable API used when the ACCDET component is enabled.

## Important APIs, types, and functions

Constants include `ACCDET_DEVNAME`, headset modes `HEADSET_MODE_1`, `HEADSET_MODE_2`, `HEADSET_MODE_6`, `MT6359_ACCDET_NUM_BUTTONS`, `MT6359_ACCDET_JACK_MASK`, and `MT6359_ACCDET_BTN_MASK`. `enum eint_moisture_status` names EINT plug/moisture states such as `M_PLUG_IN`, `M_WATER_IN`, `M_HP_PLUG_IN`, `M_PLUG_OUT`, `M_NO_ACT`, and `M_UNKNOWN`. The anonymous state enum names ACCDET debounce states, EINT debounce states, auxadc debounce, and inverter debounce slots consumed by `accdet_set_debounce()`.

Configuration structures are `struct three_key_threshold`, `struct four_key_threshold`, `struct pwm_deb_settings`, and `struct dts_data`. `struct mt6359_accdet` is the main runtime object with ALSA jack/device/regmap pointers, parsed data, capability flags, IRQ ids, mutex, jack/button status fields, ACCDET calibration/status fields, and workqueue/work structs. The public function is `mt6359_accdet_enable_jack_detect()`, with an inline `-EOPNOTSUPP` stub when `CONFIG_SND_SOC_MT6359_ACCDET` is disabled.

## Control flow

There is no executable control flow in the header. It shapes C-file control flow by defining the state identifiers passed to debounce programming, the moisture/jack-detect status values interpreted by IRQ work, the threshold structures used by button classification, and the conditional API availability controlled by Kconfig.

## State and persistence behavior

The header declares the in-memory state layout used by `mt6359-accdet.c`. `struct dts_data` persists parsed board configuration for the lifetime of the platform device. `struct mt6359_accdet` persists current jack state, previous ACCDET state, button state, calibration voltage, jack-detect status, IRQ registrations, and deferred work objects. No storage is allocated here; allocation is done by the probe function.

## Dependencies and integration points

It includes Linux string/ctype headers and uses ALSA jack bit constants and ASoC component types through the C file's include context. The exported API is the integration point for codec or machine code that owns the `snd_soc_component` and creates the `snd_soc_jack`. The Kconfig guard lets callers compile even when ACCDET support is disabled, receiving `-EOPNOTSUPP` from the inline stub.

## Risks and test signals

Risks include the generic include guard `_ACCDET_H_` being collision-prone, hidden dependency on ALSA declarations because this header itself does not include `<sound/soc.h>` or `<sound/jack.h>`, structure layout coupling to `mt6359-accdet.c`, and threshold arrays whose first DTS element is skipped by the parser. Test signals are clean builds with `CONFIG_SND_SOC_MT6359_ACCDET=y/m/n`, callers correctly handling the disabled stub, all jack/button mask bits reaching ALSA jack reports, and DTS threshold data producing expected `three_key` or `four_key` fields.
