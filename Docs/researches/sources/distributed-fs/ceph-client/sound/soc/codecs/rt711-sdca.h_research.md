# sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdca.h

Purpose: Defines the private state and register vocabulary for the RT711 SDCA codec core and its SoundWire wrapper. The header provides SDCA entity/control IDs, vendor index IDs, jack-detect constants, channel IDs, supported sample-rate encodings, DAI IDs, and exported init/detect entry points.

Important APIs/types: `struct rt711_sdca_priv` carries both regmaps, component/slave pointers, SoundWire bus params, runtime init flags, jack and delayed work state, calibration and IRQ mutexes, cached SDCA interrupt status, hardware version, JD source, GE override, and DAPM/mixer mute mirrors. Exported declarations are `rt711_sdca_init()`, `rt711_sdca_io_init()`, and `rt711_sdca_jack_detect()`. Enums identify AIF1/AIF2, JD routing (`JD1`, `JD2`, `JD2_100K`), and hardware versions `VD0`/`VD1`.

Control/data model: Most definitions are not simple offsets but contract values consumed by the C implementation: vendor NIDs select MBQ index spaces, SDCA entity IDs select functions such as jack codec, mic array, HID, FUs, PDEs, clock selectors, and line entities, and control IDs select SDCA mute/volume/sample-rate/current-owner/power-state fields.

State and persistence: The header encodes which state is software-owned versus hardware-owned. Software mirrors mute state, jack state, interrupt disable state, and first-init state because regmap cache and SoundWire attach/resume can outlive a single hardware enumeration.

Dependencies and integration: Includes PM, regmap, SoundWire, ASoC, and workqueue headers because the private structure is shared across core and bus glue. The SoundWire bus file depends on this header for function prototypes and state layout; the core file depends on it for all magic register constants.

Risks and test signals: Renumbering entity/control constants or changing `rt711_sdca_priv` semantics can silently break register writes. Test signals include successful compile coverage across both core and bus wrapper, valid ACPI/property JD source handling, and runtime traces showing expected SDCA addresses for mute, volume, sample-rate, GE, and HID accesses.
