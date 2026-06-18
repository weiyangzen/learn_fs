# sources/distributed-fs/ceph-client/sound/soc/codecs/rt721-sdca.h

Purpose: shared RT721 SDCA definitions for the ASoC component and SoundWire transport. It describes private state, custom DMIC-control metadata, vendor node/index constants, SDCA function/entity/control/channel IDs, sample-frequency codes, HID IDs, DAI IDs, and public init entry points.

Important types and APIs: `struct rt721_sdca_priv` carries the normal and MBQ regmaps, component and slave pointers, SoundWire bus params, init flags, calibration and interrupt mutexes, suspend interrupt gating (`disable_irq`), SDCA interrupt snapshots, ASoC jack pointer, delayed works, jack type/source, and DAPM/mixer mute state for headset capture and DMIC capture. `struct rt721_sdca_dmic_kctrl_priv` provides register base, count, max, and invert parameters for custom controls. Public functions are `rt721_sdca_io_init()` and `rt721_sdca_init()`.

Control and integration role: register constants organize vendor NIDs for analog power, DAC, jack detect, combo jack, class-D amp, boost, calibration, efuse, analog control, and HDA SDCA float controls. SDCA function/entity/control constants construct addresses for jack codec, mic array, HID, and amp functions. Sample-rate constants map ALSA rates to SDCA frequency indices. `RT721_BUF_ADDR_HID*` and `RT721_SDCA_HID_ID` support HID button-message reads.

State and persistence behavior: header-defined fields are the authoritative in-memory persistence for jack state, pending SDCA interrupt status, and user mute settings. Regcache persistence is implemented by source files, but the header's split between `regmap` and `mbq_regmap` is central to cache restore. `first_hw_init` and `hw_init` separate probe-time allocation from attach-time programming.

Dependencies: includes Linux PM, regmap, SoundWire, SoundWire type, ASoC, and workqueue headers. It is also implicitly coupled to `rt-sdw-common.h` helper semantics used by the implementation, though that common header is included in the `.c` file.

Risks: large macro surface can drift from vendor datasheet or SDCA address construction. Generic names such as `CH_L` and `FUNC_NUM_*` can collide if included in broader compilation scopes. Fields such as `params` and `jd_src` are lightly used or only parsed, so future behavior may require clearer validation.

Test signals: compile all RT721 users; validate all DAI IDs route to expected ports; test sample-rate index writes; verify HID button paths use the correct buffer/report ID; exercise jack state and mute-state persistence across detach, runtime suspend, and system suspend.
