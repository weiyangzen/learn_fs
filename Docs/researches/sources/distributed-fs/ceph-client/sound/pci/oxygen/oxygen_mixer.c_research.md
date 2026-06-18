
# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_mixer.c

Purpose: shared ALSA mixer/control implementation for Oxygen models, including DAC volume/mute, stereo upmixing, SPDIF playback/capture controls, input monitoring, and AC97 capture/front-panel controls.

Important APIs: control callbacks for DAC volume/mute call model `update_dac_*`; `oxygen_update_dac_routing` maps stereo/multichannel routing and lets models adjust it; `oxygen_update_spdif_source` switches SPDIF between dedicated PCM and mirrored multichannel; IEC958 conversion helpers map ALSA status bytes to Oxygen bits. AC97 switch/volume controls manage CM9780 routing and mutual exclusion between line and mic/CD/aux capture.

Control flow: `oxygen_mixer_init` conditionally adds control arrays based on `device_config`, AC97 presence, model filter, and model mixer init. `add_controls` stores known controls for later notifications and inactive toggling.

State/persistence: shared state lives in `chip->dac_volume`, `dac_mute`, `dac_routing`, `spdif_bits`, `spdif_pcm_bits`, `spdif_playback_enable`, `controls`, and AC97 registers.

Risks: mixer names and private_value encodings are ABI-visible; control_filter can remove or mutate controls; SPDIF and routing updates run under mixed mutex/spinlock contexts. Test signals: `amixer` get/put for all generated controls, SPDIF PCM inactive state during stream open/close, upmix routing by channel count, AC97 capture source exclusivity, and TLV ranges.
