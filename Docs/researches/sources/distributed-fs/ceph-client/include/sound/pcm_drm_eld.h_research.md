# sources/distributed-fs/ceph-client/include/sound/pcm_drm_eld.h

Source read summary: 98 lines, DRM ELD to ALSA PCM helper declarations.

Purpose: defines helpers and state for parsing HDMI/DP ELD data and exposing it through PCM/control logic.

Important APIs, types, and functions: `struct snd_pcm_chmap_elem` is referenced for channel maps. `struct snd_pcm_eld` style state stores ELD validity, monitor name, CEA speaker allocation, SAD count/data, and derived channel maps. Helpers update ELD, limit formats/rates/channels based on ELD, and create HDMI ELD controls for PCM devices.

Control flow: HDMI/DP audio code obtains ELD from DRM or codec pins, parses SAD/channel allocation, constrains PCM capabilities, and exposes monitor/ELD state to userspace controls.

State and persistence behavior: parsed ELD is cached per HDMI/PCM path and changes on hotplug or display mode changes. It mirrors sink firmware data and is not persisted by the kernel.

Dependencies and integration points: integrates ALSA PCM/channel-map controls with DRM connector ELD and HDMI audio codec paths.

Risks and edge cases: malformed ELD/SAD lengths, stale ELD after unplug, channel map mismatch, and overly restrictive constraints can break HDMI audio.

Test signals: hotplug ELD updates, invalid/short ELD parsing, SAD rate/format constraints, channel-map control contents, and monitor-name exposure.
