# sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca.h

Purpose: shared RT722 SDCA definitions for the component and SoundWire bus driver. It defines the private state structure, custom control metadata, vendor nodes/registers, SDCA function/entity/control/channel IDs, sample-rate indices, function-status flags, jack-detect and hardware-version enums, and public init/index APIs.

Important types and APIs: `struct rt722_sdca_priv` stores the single MBQ-aware regmap, component and slave pointers, bus params, init flags, calibration and interrupt mutexes, suspend interrupt gating, SDCA interrupt snapshots, ASoC jack pointer, delayed works, jack type/source, FU0F/FU1E mute booleans, and `hw_vid`. `struct rt722_sdca_dmic_kctrl_priv` supplies register base/count/max/invert for custom mixer controls. Public functions include `rt722_sdca_init()`, `rt722_sdca_io_init()`, `rt722_sdca_index_write()`, `rt722_sdca_index_read()`, and a declared `rt722_sdca_jack_detect()`.

Control and integration role: constants cover RT722 vendor NIDs (`RT722_VENDOR_REG`, calibration, efuse, IMS/DRE, analog, HDA control), index registers for bias, combo-jack auto detect, calibration, HID/UMP controls, floating power controls, mixer controls, EAPD, and SDCA function controls. SDCA function/entity/control IDs are used in `SDW_SDCA_CTL(...)` address construction across both source files. `FUNCTION_NEEDS_INITIALIZATION` gates preset writes. Enums define DAI IDs and RT722 hardware variants VA/VB.

State and persistence behavior: the header captures all runtime state required for jack handling and PM coordination. Unlike RT721, RT722 has one regmap, so all persistent control state relies on that single cache plus the driver's booleans for mixer/DAPM mute composition. `hw_vid` persists the detected hardware variant for variant-specific initialization.

Dependencies: includes Linux PM, regmap, SoundWire, SoundWire type, ASoC, and workqueue headers. It is coupled to `rt722-sdca-sdw.c`'s MBQ-width classifier and to the component's preset/control code.

Risks: the declared `rt722_sdca_jack_detect()` is not the primary local helper name in the implementation viewed here, suggesting stale API surface. Generic macro names (`FUNC_NUM_*`, `CH_*`) can collide. Hardware constants are numerous and vendor-specific; mistakes are hard to validate without hardware traces.

Test signals: compile all users, verify every public prototype has a matching definition or intentional external provider, validate DAI IDs/port mapping, exercise function-status initialization paths, run jack/button tests, and confirm VA/VB-specific branches are covered on representative hardware or emulation.
