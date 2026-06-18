# sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdw.h

Purpose: Supplies the non-SDCA RT711 logical regmap defaults used by the SoundWire wrapper. The table seeds register cache values for HDA verb windows, decoded vendor/index registers, gain controls, SDCA-like address ranges, and private vendor settings.

Important APIs/types: The primary artifact is `rt711_reg_defaults[]`, a `struct reg_default` array referenced by `rt711_regmap` in `rt711-sdw.c`. It covers normal byte registers, HDA readback windows (`0x2012` etc.), data-port/BRA/debug ranges, amplifier gain defaults, and private-index values such as jack auto-detect and mux controls.

Control flow: There is no executable logic in this header. At probe, regmap uses the table to initialize `REGCACHE_MAPLE`; the bus driver later switches cache-only/cache-bypass modes during attach, suspend, and resume. The defaults determine what values are replayed or compared when the codec is not immediately accessible.

State and persistence: This header is effectively the persisted default-state contract for the RT711 logical regmap. It influences suspend/resume behavior, first attach before hardware init, and ALSA controls that read cached values.

Dependencies and integration: Included only by `rt711-sdw.c`; depends on `struct reg_default` being available from regmap includes in the C file. It is paired with readable/volatile filters in the wrapper, so new defaults must remain inside allowed register ranges.

Risks and test signals: Stale defaults can cause regcache sync to program wrong jack, gain, or mux values after resume. Tests should compare hardware reset values against this table, verify no default falls outside readable ranges, and run suspend/resume plus mixer-control readback tests.
