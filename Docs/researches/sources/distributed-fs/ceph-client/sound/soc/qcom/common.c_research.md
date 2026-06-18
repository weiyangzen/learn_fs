# sources/distributed-fs/ceph-client/sound/soc/qcom/common.c

Purpose: provides shared Qualcomm machine-driver helpers for parsing DT sound cards and setting up WCD/DisplayPort jacks.

Important APIs/types/functions: exports `qcom_snd_parse_of`, `qcom_snd_wcd_jack_setup`, and `qcom_snd_dp_jack_setup`. It defines common jack widgets and headset jack pins.

Control flow: `qcom_snd_parse_of` reads card name/model, optional audio routing/widgets, allocates DAI links from DT children, parses CPU/platform/codec components, assigns names/stream names, and sets link flags. WCD jack setup creates a headset jack, maps button keys, and attaches it to codec components. DP jack setup creates a display/HDMI jack and attaches it to HDMI codec components.

State and persistence: parsed links and component arrays are devm-managed on the card device. Jack objects are stored in machine-driver private data passed by callers or codec components.

Dependencies and integration: used by Qualcomm machine drivers including APQ8016 and APQ8096. Depends on ASoC OF parsing, DAPM widgets/routes, jack APIs, and codec component jack callbacks.

Risks: DT parsing is topology-sensitive; malformed child nodes can produce partial card/link allocations. Link naming uses fixed-size buffers. Jack setup must handle codecs that return `-ENOTSUPP` while still propagating real failures.

Test signals: DT cards with multiple links/codecs/platforms, optional widgets/routing, headset button mapping, DP jack setup, and error paths for malformed OF nodes.
