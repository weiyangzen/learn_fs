# sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdw.h

Purpose: register-default table for the legacy RT715 SoundWire regmap. It is included by `rt715-sdw.c` to seed `rt715_regmap` with known reset/default values for codec, HDA verb, converter, mux, gain, and private-index registers.

Important data: `rt715_reg_defaults[]` is a static `struct reg_default` array spanning low SoundWire-accessible areas (`0x0000` ranges), function/converter/mux regions (`0x2000`, `0x2200`, `0x2230`), HDA verb addresses (`0x3122..0x3125`, `0x36xx`, `0x37xx`, `0x4c..0x4f`), ADC format registers, gain/mute registers, and the private vendor default `0x752039`. The table is consumed by `rt715_regmap` with `REGCACHE_MAPLE`.

Control flow and integration: the header contains no executable logic. Its defaults inform regcache comparisons, regcache sync after suspend, and initial software-visible state before the physical device is attached. `rt715_sdw.c` separately declares which of these registers are readable or volatile; defaults only matter for cached/nonvolatile addresses.

State and persistence: these defaults are not persisted outside the module image. During runtime, regcache uses them as baseline values and later tracks writes from `rt715.c`. Resume paths sync selected regions from this cache back to hardware after SoundWire detach or suspend.

Dependencies: requires `struct reg_default` from regmap but the header itself relies on being included after suitable Linux headers. It is tightly coupled to address constants and translation behavior in `rt715-sdw.c` and to control addresses in `rt715.h`.

Risks: stale default values can cause regcache to skip writes that hardware actually needs after reset. Defaults for volatile or readback-derived registers have limited value and must match the readable/volatile filters. The large literal table is easy to drift from vendor programming sequences in `rt715.c`.

Test signals: verify regcache sync restores mute, format, mux, and input-selection state across suspend/resume; compare defaults against vendor datasheet or known-good kernel; use regmap debugfs to ensure nonvolatile cached defaults match expected reset state; run ALSA controls before and after resume to catch skipped cache writes.
