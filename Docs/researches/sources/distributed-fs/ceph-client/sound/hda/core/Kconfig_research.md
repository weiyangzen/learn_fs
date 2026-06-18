# sources/distributed-fs/ceph-client/sound/hda/core/Kconfig

## Purpose
This Kconfig file declares shared HD-audio core symbols and Intel audio support helpers used by controller and codec drivers.

## Important APIs, Types, and Functions
Important symbols include `SND_HDA_CORE`, `SND_HDA_DSP_LOADER`, `SND_HDA_ALIGNED_MMIO`, `SND_HDA_COMPONENT`, `SND_HDA_I915`, `SND_HDA_EXT_CORE`, `SND_INTEL_NHLT`, `SND_INTEL_DSP_CONFIG`, `SND_INTEL_SOUNDWIRE_ACPI`, and `SND_INTEL_BYT_PREFER_SOF`.

## Control Flow
Selections define build inclusion: `SND_HDA_CORE` selects `REGMAP`; `SND_HDA_I915` selects component support; `SND_HDA_EXT_CORE` selects the base core; Intel DSP config selects ACPI NHLT, Intel NHLT, and SoundWire ACPI helpers when ACPI is enabled.

## State and Persistence Behavior
The file provides build-time configuration state. The selected symbols determine whether runtime code for regmap, i915 sync, extended HDA, DSP detection, and SoundWire ACPI is present.

## Dependencies and Integration Points
It integrates controller Kconfigs with shared HDA modules, DRM component sync, Intel DSP/SOF/SST selection, ACPI NHLT parsing, and SoundWire discovery.

## Risks
Incorrect symbol selection can produce link errors or missing runtime handoff. The Bay/Cherry Trail SOF preference option affects driver selection when both old SST and SOF are available.

## Test Signals
Run randconfig/allmodconfig builds around HDA, i915, extended core, ACPI, SoundWire, and Baytrail SOF/SST combinations.
