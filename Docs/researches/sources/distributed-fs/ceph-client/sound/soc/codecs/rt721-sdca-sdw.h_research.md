# sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca-sdw.h

Purpose: regmap default header for the RT721 SDCA SoundWire driver. It defines reset/default values for the normal 8-bit SDCA regmap and the 16-bit MBQ/vendor regmap used by `rt721-sdca-sdw.c`.

Important data: `rt721_sdca_reg_defaults[]` includes SDW/SDCA control defaults for sample-frequency indices, PDE request power states, mute defaults for jack, mic-array, and amplifier functions, vendor controls, and HID-related low register defaults. `rt721_sdca_mbq_defaults[]` includes vendor HDA-float, analog, jack, gain, and volume defaults, including SDCA FU volume/ch-gain registers for jack codec, mic array, and amp functions.

Control flow and integration: no functions are defined. The arrays are wired into `rt721_sdca_regmap` and `rt721_sdca_mbq_regmap` with `REGCACHE_MAPLE`. They define software cache baseline before the device is attached and help resume sync determine what changed from default.

State and persistence: defaults are static module data. Runtime state is maintained by regcache after writes from `rt721-sdca.c`; these arrays only seed initial cache contents. Because RT721 has two cached regmaps, defaults must be correct for both 8-bit and 16-bit address/value domains.

Dependencies: includes regmap and SoundWire register macros and relies on RT721 function/entity/control/channel constants from `rt721-sdca.h` being available in the include order used by the SDW source.

Risks: omissions in this table can lead to incorrect restore after SoundWire reset, while defaults for registers later treated as volatile may be misleading. The MBQ defaults contain many vendor literal addresses, making drift from hardware presets hard to see in review. Any mismatch between default value width and the owning regmap can corrupt cache behavior.

Test signals: verify runtime suspend/resume preserves mute, power-state, sample-rate, volume, and gain settings; compare regcache dumps before/after resume; run jack and audio playback/capture after detach/re-attach; review any added component register access against the readable/volatile filters and defaults.
