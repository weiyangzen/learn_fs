# sources/distributed-fs/ceph-client/sound/hda/core/Makefile

## Purpose
This Makefile assembles the shared `snd-hda-core` module, optional component/i915 helpers, the extended HDA submodule, and Intel DSP/SoundWire ACPI helper modules.

## Important APIs, Types, and Functions
Object lists define module composition: `snd-hda-core-y` includes bus, device, sysfs, regmap, controller, stream, array, HDMI channel-map, and trace support. Conditional objects add `component.o` and `i915.o`. Separate modules are `snd-intel-dspcfg` and `snd-intel-sdw-acpi`.

## Control Flow
Kbuild includes objects according to `CONFIG_SND_HDA_CORE`, `CONFIG_SND_HDA_COMPONENT`, `CONFIG_SND_HDA_I915`, `CONFIG_SND_HDA_EXT_CORE`, `CONFIG_SND_INTEL_DSP_CONFIG`, `CONFIG_SND_INTEL_NHLT`, and `CONFIG_SND_INTEL_SOUNDWIRE_ACPI`.

## State and Persistence Behavior
Build-only state. Runtime module boundaries affect symbol export availability and module load order.

## Dependencies and Integration Points
The file integrates base HDA code, tracepoint generation (`CFLAGS_trace.o := -I$(src)`), extended core under `ext/`, Intel DSP config, and SoundWire ACPI helper modules.

## Risks
Changing object composition can omit exported helpers used by controllers/codecs. Trace include paths must remain valid for generated trace definitions.

## Test Signals
Build with optional component/i915/ext/DSP/SoundWire combinations and verify exported symbols resolve for controller modules.
