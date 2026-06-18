# sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca-sdw.h

Purpose: Provides RT715 SDCA regmap default tables used by the SoundWire bus driver for RT714/RT715 microphone-array codecs.

Important APIs/types: `rt715_reg_defaults_sdca[]` seeds 8-bit SDCA/control defaults for HDA-like windows, vendor registers, clock selection, ADC FU mute controls, SMPU trigger status, and VAD-related controls. `rt715_mbq_reg_defaults_sdca[]` seeds 16-bit MBQ defaults for vendor blocks and mic-array volume/gain controls across ADC and DMIC channels.

Control flow: Data-only header consumed by `rt715-sdca-sdw.c` regmap configs. The defaults become the cached baseline used before attach and during suspend; resume synchronizes selected portions of these maps back to hardware.

State and persistence: Defaults establish muted ADC/DMIC FUs, zeroed volumes/gains, and initial VAD/SMPU control values. They are critical for preserving known-safe mic capture state through SoundWire enumeration and PM transitions.

Dependencies and integration: Includes SoundWire register macros and relies on function/entity/channel constants from `rt715-sdca.h`, which the C file includes before this header. The address sets must match readable and volatile filters in the bus wrapper.

Risks and test signals: Duplicate or stale defaults can make cache sync replay unexpected mute/volume settings. Test signals include regmap registration without range warnings, capture mixer default readback, VAD status reads, suspend/resume cache replay, and comparison with hardware reset defaults for RT714 and RT715.
