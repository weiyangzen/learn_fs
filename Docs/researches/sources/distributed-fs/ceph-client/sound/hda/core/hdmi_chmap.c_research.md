## sources/distributed-fs/ceph-client/sound/hda/core/hdmi_chmap.c

Purpose: implements HDMI/DisplayPort channel allocation and ALSA channel-map controls for the HD-audio core. It bridges three representations: ELD speaker allocation bits, CEA Audio InfoFrame channel allocation indexes, and ALSA `SNDRV_CHMAP_*` positions.

Important APIs, types, and functions: `enum cea_speaker_placement`, `channel_allocations[]`, `hdmi_channel_mapping[][]`, `struct hdac_chmap_ops`, `snd_hdac_channel_allocation()`, `snd_hdac_setup_channel_mapping()`, `snd_hdac_get_active_channels()`, `snd_hdac_add_chmap_ctls()`, `snd_hdac_chmap_to_spk_mask()`, and `snd_hdac_spk_to_chmap()`. The file also supplies default operation callbacks for slot programming and converter channel count verbs.

Control flow: registration copies default callbacks into a caller-owned `struct hdac_chmap` and precomputes channel counts and speaker masks. Runtime allocation either derives a CEA CA from ELD speaker capabilities or validates a user-provided ALSA channel map. Setup then writes slot-to-channel assignments through `AC_VERB_SET_HDMI_CHAN_SLOT`; non-PCM streams use identity-like mapping, while PCM can use manual maps. Mixer TLV callbacks enumerate available maps based on the current sink speaker mask.

State and persistence: static CA tables are partly initialized at registration time; generated `hdmi_channel_mapping[ca]` entries persist globally. Per-pin/per-PCM maps live behind caller-provided ops. User changes are accepted only for open/setup/prepared PCM states and rejected while busy.

Dependencies and integration points: depends on HD-audio codec verbs, ALSA PCM channel-map controls, ELD speaker allocation from HDMI codec code, and caller-provided `hdac_chmap` hooks for per-pin state, validation, and PCM attachment.

Risks: CA selection is order-sensitive and explicitly notes possible wrong choices among multiple valid candidates. Manual maps with unknown positions are silently left unassigned until CA validation catches unsupported layouts. Global lazy initialization of mapping tables assumes stable static data and registration before use.

Test signals: validate stereo, 5.1, 7.1, non-PCM, and user-remapped playback with `amixer` channel-map controls; inspect HDMI InfoFrame CA and slot verbs with verbose HDA debugging; hotplug monitors with different ELD speaker masks; attempt map writes during running playback to confirm `-EBUSY`.
