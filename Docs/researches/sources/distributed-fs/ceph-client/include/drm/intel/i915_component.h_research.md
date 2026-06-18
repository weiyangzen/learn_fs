# sources/distributed-fs/ceph-client/include/drm/intel/i915_component.h

Purpose: declares component binding identifiers used between i915 and companion drivers such as HDA audio, HDCP, PXP, GSC proxy, and Intel late-binding services.

Important APIs/types/functions: `enum i915_component_type` assigns component IDs: audio, HDCP, PXP, GSC proxy, and late binding. `MAX_PORTS` is the i915/display port count contract for audio state. `struct i915_audio_component` embeds `struct drm_audio_component` and stores `aud_sample_rate[MAX_PORTS]`.

Control flow: no executable flow. Component framework participants use the enum to bind matching providers/consumers; HDA uses the audio component base and per-port sample-rate array.

State and persistence: the only mutable state described here is per-port audio sample rate inside the component object. It is runtime state owned by the component provider/consumer, not persisted by this header.

Dependencies and integration: depends on `drm_audio_component.h`. Integrated by i915 display audio code and audio drivers that need direct graphics/audio coordination.

Risks and test signals: `MAX_PORTS` must remain synchronized with i915's port definitions. Component ID changes are ABI-like within kernel component matching. Test audio binding, hotplug, sample-rate updates for all ports, and build coverage for every component user.
