# sources/distributed-fs/ceph-client/include/sound/hda_component.h

Source read summary: 67 lines, HD-audio to DRM audio-component bridge helpers.

Purpose: declares the component interface that lets HDA audio drivers coordinate display power, wake, rate synchronization, ELD reads, and notifier registration with DRM display drivers.

Important APIs, types, and functions: `HDA_CODEC_IDX_CONTROLLER` reserves a virtual codec index for controller-level display power. When `CONFIG_SND_HDA_COMPONENT` is enabled, APIs include `snd_hdac_set_codec_wakeup()`, `snd_hdac_display_power()`, `snd_hdac_sync_audio_rate()`, `snd_hdac_acomp_get_eld()`, `snd_hdac_acomp_init()`, `snd_hdac_acomp_exit()`, and `snd_hdac_acomp_register_notifier()`. Disabled builds return success for harmless operations and `-ENODEV` for component-dependent setup/ELD/notifier calls.

Control flow: HDA HDMI/DP code initializes the audio component against a DRM master, toggles display power around codec access, asks DRM for ELD/audio-enabled state, synchronizes sample rates where supported, and unregisters at teardown.

State and persistence behavior: no independent persistent state is defined here; state lives in `hdac_bus->audio_component`, display power bitmaps, and DRM component binding. Stub paths intentionally persist nothing.

Dependencies and integration points: includes DRM audio component APIs and `hdaudio.h`. It integrates HDA codec/controller code with i915/DRM display pipelines and HDMI/DP hotplug notification.

Risks and edge cases: missing component support can silently no-op display power and wake transitions while ELD reads fail; mismatched codec indexes or unbalanced power calls can break HDMI audio on runtime PM systems.

Test signals: build with and without `CONFIG_SND_HDA_COMPONENT`, probe HDMI audio with DRM bind/unbind, verify ELD retrieval after hotplug, check display power reference balance, and exercise rate sync across suspend/resume.
