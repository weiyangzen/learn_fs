# sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-dmic.h

Purpose: Defines private state, per-control metadata, channel constants, and regmap defaults for the standalone RT712 SDCA DMIC SoundWire function.

Important APIs/types: `struct rt712_sdca_dmic_priv` holds the normal and MBQ regmaps, component, SoundWire slave, bus params, `hw_init`, `first_hw_init`, DAPM mute state, and four-channel mixer mute array. `struct rt712_sdca_dmic_kctrl_priv` describes dynamic ALSA controls with a base register, channel count, max value, and invert flag. The default arrays `rt712_sdca_dmic_reg_defaults[]` and `rt712_sdca_dmic_mbq_defaults[]` seed `REGCACHE_MAPLE` for SDCA and MBQ spaces.

Control/data model: Defaults cover HDA/vendor windows, RC calibration, mic-array sample-frequency controls, FU1E mutes/volumes, platform FU15 channel gain, and entity mapping values needed for DMIC capture. Channel constants `CH_01` through `CH_04` are used for contiguous SDCA controls.

State and persistence: The default arrays define cached power-on state before physical attach and after resume. The private structure mirrors mutable mute state so DAPM and ALSA mixer switches can be combined deterministically when hardware is temporarily inaccessible.

Dependencies and integration: Included by `rt712-sdca-dmic.c`; it relies on shared RT712 constants from `rt712-sdca.h` being included first in the C file and on SoundWire SDCA control macros.

Risks and test signals: Defaults must stay consistent with readable/volatile filters in the C file. Test signals include successful regmap registration, no out-of-range defaults, correct initial mute/readback state for four channels, and cache sync after suspend/resume.
