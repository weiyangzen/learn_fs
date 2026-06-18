# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-lpass-ports.c

Purpose: `q6dsp-lpass-ports.c` provides the common ALSA SoC DAI driver table for QDSP6 LPASS ports and helpers to assign backend-specific DAI ops. It is shared by AudioReach/APM and other LPASS DAI drivers.

Important APIs and types: macros build repeated DAI descriptors for TDM playback/capture, codec DMA RX/TX, DisplayPort RX, and MI2S RX/TX. `q6dsp_audio_fe_dais[]` is the central static table covering USB, HDMI, Slimbus 0-6, primary through senary MI2S, LPI MI2S, primary through quinary TDM slots, DP RX 0-7, WSA/VA/RX/TX codec DMA ports. Exported helpers are `q6dsp_audio_ports_of_xlate_dai_name` and `q6dsp_audio_ports_set_config`.

Control flow: platform DAI probes call `q6dsp_audio_ports_set_config` with a config struct holding ops pointers. The helper walks the static table and assigns ops by ID range: HDMI/DP, Slimbus, MI2S/LPI MI2S, TDM, codec DMA, and USB. It returns the table pointer and count. Device-tree DAI name translation calls `q6dsp_audio_ports_of_xlate_dai_name`, scans the table by ID, and returns the matching name.

State and persistence: the DAI table is static mutable global state because ops pointers are patched in place. Once configured, all users see the same ops assignments. There is no per-device copy in this helper.

Dependencies and integration points: depends on ALSA SoC DAI structs, PCM rate/format flags, q6afe dt-bindings for port IDs, and the companion header defining the config struct. APM LPASS DAIs consume it directly.

Risks: because the table is global and mutable, two different platform drivers using different ops configs could overwrite each other. ID range matching must stay aligned with dt-bindings; adding new ports outside existing ranges will silently leave ops unset. `DISPLAY_PORT_RX` and `DISPLAY_PORT_RX_0` naming/range handling must match binding IDs.

Test signals: verify every table entry gets non-null ops for the intended backend, OF xlate returns correct names for all IDs, unsupported IDs return `-EINVAL`, and global table behavior is safe when multiple compatible drivers probe.
