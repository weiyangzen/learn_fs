# sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-sdw.h

Purpose: Provides RT712 SDCA regmap default tables for the main multi-function SoundWire codec instance.

Important APIs/types: `rt712_sdca_reg_defaults[]` seeds 8-bit SDCA controls for sample-frequency indexes, FU mutes, PDE power states, jack/mic/amp function defaults, and amp output vendor control. `rt712_sdca_mbq_defaults[]` seeds 16-bit MBQ/vendor values for analog, calibration, HID, jack, mixer, EAPD, FU volumes, platform gains, and amp volume controls.

Control flow: The header is data-only. `rt712-sdca-sdw.c` references these arrays in `regmap_config` so regcache has known values before attach and while suspended. `rt712-sdca.c` later mutates the same addresses during VA/VB initialization, DAPM events, and mixer-control writes.

State and persistence: These defaults define the baseline restored by regcache. They represent muted FUs, power-down PDEs, 48 kHz default sample-frequency indexes, and zero volume/gain defaults for user controls.

Dependencies and integration: Included by the SoundWire wrapper after `rt712-sdca.h`, because the arrays use shared SDCA function/entity/control IDs and `CH_01`/`CH_02`/etc. The readable/volatile filters in the wrapper must cover all addresses listed here.

Risks and test signals: Incorrect defaults can produce audible pops, muted paths, wrong amp state, or broken resume. Test signals include regmap cache validation, mixer default readback, DAPM power-up from a muted baseline, speaker-present and RT713 no-speaker variants, and resume after autosuspend/system sleep.
