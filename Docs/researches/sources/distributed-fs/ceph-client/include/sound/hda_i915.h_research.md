# sources/distributed-fs/ceph-client/include/sound/hda_i915.h

Source read summary: 27 lines, Intel i915-specific HDA component wrappers.

Purpose: declares the small compatibility layer for HDA controllers that need i915 display-audio integration, especially BCLK setup and component initialization.

Important APIs, types, and functions: `snd_hdac_i915_set_bclk()` programs or derives the HDA BCLK with i915 help, `snd_hdac_i915_init()` binds to i915 when `CONFIG_SND_HDA_I915` is enabled, and `snd_hdac_i915_exit()` always forwards to `snd_hdac_acomp_exit()`. Disabled builds no-op BCLK and return `-ENODEV` for init.

Control flow: controller probe calls init, then sets BCLK before audio stream use; remove/suspend teardown calls exit through the shared component path.

State and persistence behavior: state is in the `hdac_bus` audio component and hardware clock configuration; no persistent data is owned by this header.

Dependencies and integration points: includes `hda_component.h` and therefore DRM audio component/HDA core declarations. It is used by Intel HDA controller paths tied to i915 display audio.

Risks and edge cases: systems without i915 support must gracefully fall back; failed component init can disable HDMI/DP audio functionality; BCLK setup timing must match controller power state.

Test signals: compile both config paths, Intel HDMI/DP audio probe with i915 present and absent, runtime PM cycles, and stream startup after display power changes.
