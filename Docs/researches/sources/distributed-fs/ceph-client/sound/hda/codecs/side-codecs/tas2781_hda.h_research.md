# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda.h

## Purpose
This header defines the common TAS2781 HDA wrapper state, custom ALSA control macros, vendor category ids, calibration constants, and shared function declarations used by the TAS2781 I2C and SPI HDA drivers.

## Important APIs, types, and functions
`ACARD_SINGLE_RANGE_EXT_TLV()` builds CARD-interface volume controls backed by `soc_mixer_control` data and TLV arrays. `ACARD_SINGLE_BOOL_EXT()` builds CARD-interface boolean controls. `enum device_catlog_id` selects EFI calibration GUID families. `struct tas2781_hda` links the Linux device, TAS firmware-library private state, three DSP/profile controls, device category, and transport-private HDA state. The header declares calibration, remove, profile/program/config info/get/put callbacks, and `tasdev_fct_efi_guid[]`.

## Control flow
There is no executable logic except macro expansion. Transport drivers allocate `struct tas2781_hda`, set `priv` and `hda_priv`, then use declared callbacks when constructing controls and when loading calibration.

## State and persistence
`struct tas2781_hda` persists for one component device lifetime. It connects framework resources (`struct device`, ALSA controls), firmware library state (`tasdevice_priv`), category selection for EFI variables, and transport-specific private memory.

## Dependencies and integration points
It depends on ALSA core definitions and on TAS firmware library types included indirectly by C files. The macros integrate ALSA CARD-interface controls with SoC helper callbacks despite these being HDA side-codec devices.

## Risks and edge cases
The control macros create compound-literal `soc_mixer_control` private data; users must keep the declarations static or otherwise ensure the private data remains valid as intended by the macro usage. Category ids must match the exported GUID array order. Transport drivers must initialize `hda_priv` to the correct private struct type before using it.

## Test signals
Build I2C and SPI drivers using the macros, inspect ALSA control names/access flags/TLV behavior, verify category-to-GUID selection in calibration, and test remove/control callbacks through both transports.
