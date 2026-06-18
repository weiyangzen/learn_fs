# sources/distributed-fs/ceph-client/sound/soc/generic/audio-graph-card2.c

Purpose: generic ASoC machine driver for `audio-graph-card2` DT bindings. It converts OF graph links into `snd_soc_dai_link` arrays for normal CPU-codec links, DPCM front/back ends, codec-to-codec links, and multi-CPU/multi-codec topologies.

Important APIs/types/functions: `enum graph_type` classifies graph nodes; exported `audio_graph2_link_normal()`, `audio_graph2_link_dpcm()`, `audio_graph2_link_c2c()`, and `audio_graph2_parse_of()` are the public extension points. Internal helpers include `graph_get_type()`, `graph_get_next_multi_ep()`, `graph_parse_node()`, `graph_parse_daifmt()`, `graph_parse_bitframe()`, `graph_link_init()`, `graph_count_*()`, and `graph_for_each_link()`. `struct graph2_custom_hooks` allows external hook/callback substitution.

Control flow: probe allocates `simple_util_priv` and calls `audio_graph2_parse_of()`. Parsing sets card metadata, runs optional pre hook, walks the DT `links` phandle list once to count link component cardinalities, allocates arrays via `simple_util_init_priv()`, parses amplifier GPIO/widgets/routing, walks `links` again to populate each DAI link, parses card name and aux devices, then registers the card. Link parsing resolves endpoints, remote endpoints, TDM, clocks, dai names, DAI formats, direction flags, `mclk-fs`, trigger order, and shared ops.

State and persistence: persistent driver state is devm-allocated inside `simple_util_priv`: DAI links, properties, DAIs, DLCs, codec conf, optional PA GPIO, and card drvdata. Runtime stream state is not stored here; the shared ops in simple-card-utils manage clock enable/disable and hw_params. Device-node references are held in link components and released by `simple_util_remove()`.

Dependencies/integration: depends on OF graph APIs, `sound/graph_card.h`, `simple-card-utils`, ASoC DAI/component lookup, GPIO descriptors, and DT properties such as `links`, `routing`, `widgets`, `mclk-fs`, `playback-only`, `capture-only`, bit/frame master flags, and trigger order. It exports symbols used by the custom sample and potential custom machine drivers.

Risks: multi-endpoint mapping is sensitive to OF graph shape; invalid N:M mappings return `-EINVAL`, and the code relies on ordered `port@id` lookup for overlay stability. Reference handling is complex around `__free(device_node)` plus manual `of_node_put()`. `graph_link_init()` parses `port_cpu` trigger order twice and never explicitly parses `port_codec` in that duplicated slot, which is a potential copy/paste defect. `graph_count_c2c()` uses nested `of_node_get()` calls and should be watched for reference balance. DTs with too many links hit `SNDRV_MAX_LINKS`.

Test signals: compile coverage with `CONFIG_SND_AUDIO_GRAPH_CARD2`; DT overlay tests for normal, DPCM, codec-to-codec, 1:N/N:M multi links; probe/unprobe leak checks; runtime tests for `mclk-fs`, trigger order, link direction, and auto-selectable format negotiation.
