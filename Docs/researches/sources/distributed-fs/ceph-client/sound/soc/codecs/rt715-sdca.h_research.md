# sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca.h

Purpose: shared header for the RT715 SDCA component and SoundWire bus glue. It defines private driver state, custom kcontrol metadata, register/node IDs, SDCA function/entity/control/channel constants, sample gain scaling, DAI IDs, and the public initialization entry points used by the bus driver.

Important types and APIs: `struct rt715_sdca_priv` carries both regmaps (`regmap` for normal SDCA controls and `mbq_regmap` for 16-bit MBQ/vendor controls), a SoundWire slave pointer, runtime flags (`hw_init`, `first_hw_init`), hardware SoundWire version, and arrays caching previous control values. `struct rt715_sdca_kcontrol_private` is embedded through macro-cast private values for custom ALSA controls and records register base, channel count, max, shift, and invert semantics. Public functions are `rt715_sdca_io_init()` and `rt715_sdca_init()`.

Control and integration role: constants map RT715 legacy NIDs (`RT715_MIC_ADC`, `RT715_MUX_IN*`, `RT715_VENDOR_REG`, `RT715_VENDOR_HDA_CTL`) to the SDCA implementation. The `FUN_*`, `RT715_SDCA_*`, and `CH_*` definitions are consumed by `SDW_SDCA_CTL(...)` in `rt715-sdca.c` and `rt715-sdca-sdw.c` to construct register addresses for frequency, mute, volume, gain, power, and SMPU trigger controls. `RT715_SDCA_DB_STEP` defines the 0.375 dB step conversion used by gain helpers.

State and persistence behavior: the header makes the two-regmap model explicit. Runtime PM and regcache correctness depends on `hw_init` and `first_hw_init`, while mixer change detection depends on the cached arrays in `rt715_sdca_priv`. There is no persistent storage outside kernel memory; values persist across runtime suspend through regcache and through reinitialization code.

Dependencies: includes Linux regmap, SoundWire, SoundWire type definitions, ASoC, workqueue, and device headers. The header does not include a reg-default table; that is supplied by the SDW-specific header/source pair for this driver variant.

Risks: `struct snd_soc_codec *codec` and fields such as `adc_mute_work`, debug IDs, `params`, and `l_is_unmute/r_is_unmute` appear unused by the current implementation, which increases maintenance ambiguity. The macro namespace uses generic channel symbols (`CH_00` etc.) that can collide if headers are combined carelessly. Function prototypes form the contract with the SDW glue, so changing their argument order would break probe.

Test signals: compile coverage should include every user of this header. Static analysis should check for unused state fields and macro collisions. Runtime validation is indirect: successful probe, control registration, and SDCA register access through `rt715-sdca.c` prove the constants and private state layout are coherent.
