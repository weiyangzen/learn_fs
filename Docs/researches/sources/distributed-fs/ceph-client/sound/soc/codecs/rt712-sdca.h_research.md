# sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca.h

Purpose: Defines the main RT712 SDCA private state, control metadata, vendor/register constants, SDCA function/entity/control IDs, hardware IDs, version IDs, sample-rate encodings, and exported core APIs.

Important APIs/types: `struct rt712_sdca_priv` holds normal and MBQ regmaps, main and DMIC components, slave, bus params, init flags, jack work/state, calibration and IRQ locks, cached SDCA interrupt bits, hardware/version IDs, smart-mic presence, and mute mirrors for FU0F, FU1E, and FU05. `struct rt712_dmic_kctrl_priv` supports variable-count DMIC controls. Exported APIs are `rt712_sdca_init()`, `rt712_sdca_io_init()`, and `rt712_sdca_jack_detect()`.

Control/data model: The header defines vendor index spaces for analog, calibration, ultrasound, IMS/DRE, HDA legacy, and amp control. SDCA definitions cover jack codec, mic array, HID, amp functions, FUs, PDEs, clock selectors, terminals, function-status fields, and sample-frequency indices. Hardware enums distinguish RT712/713/716/717 and VA/VB behavior.

State and persistence: The private state captures software-owned mute and initialization data that must survive runtime PM, delayed work, and SoundWire reattachment. `FUNCTION_NEEDS_INITIALIZATION`, `FUNCTION_HAS_BEEN_RESET`, and `FUNCTION_BUSY` define how VB init decides which function blocks require reprogramming.

Dependencies and integration: Included by both the main RT712 SDCA core and standalone DMIC driver. It pulls in PM, regmap, SoundWire, ASoC, and workqueue types, and its constants are consumed by regmap defaults in the SDW/DMIC headers.

Risks and test signals: The header is a central ABI between multiple C files; changing structure layout or constants can break both integrated and standalone DMIC drivers. Test signals include build coverage of all RT712 variants, correct device ID/version decoding, valid SDCA addresses in regmap logs, smart-mic quirk behavior, and ALSA control readback.
