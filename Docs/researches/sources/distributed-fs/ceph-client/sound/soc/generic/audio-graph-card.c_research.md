# sources/distributed-fs/ceph-client/sound/soc/generic/audio-graph-card.c

## Purpose
Generic ASoC machine driver for OF graph-described audio cards. It parses CPU/codec endpoints listed in `dais`, creates normal or DPCM DAI links, handles conversion properties, link directions, trigger ordering, optional amplifier GPIO control, and card registration.

## APIs, Types, and Functions
Exports `audio_graph_parse_of()`. Key helpers are `graph_outdrv_event()`, `soc_component_is_pcm()`, `graph_parse_convert()`, `graph_parse_node()`, `graph_link_init()`, `graph_dai_link_of()`, `graph_dai_link_of_dpcm()`, `parse_as_dpcm_link()`, `__graph_for_each_link()`, `graph_for_each_link()`, `graph_count_noml()`, `graph_count_dpcm()`, `graph_get_dais_count()`, and `graph_probe()`.

## Control Flow, State, and Persistence
Probe allocates `simple_util_priv`, installs an amplifier DAPM widget, sets card probe to `graph_util_card_probe`, enables DPCM selectability for `audio-graph-scu-card`, and calls `audio_graph_parse_of()`. Parsing first counts normal/DPCM links by walking every CPU port endpoint in the top-level `dais` list. It then initializes private link arrays, gets optional `pa` GPIO, parses widgets/routing, walks links again to populate CPU/codec components, TDM, clocks, DAI format, direction flags, convert-rate/channels/sample-format data, names, DPCM FE/BE flags, codec prefixes, trigger order, and component chaining behavior. Finally it parses the card name and registers the card.

## Dependencies and Integration
Depends on OF graph APIs, GPIO descriptors, `sound/graph_card.h`, and the simple-card utility layer. Compatible strings are `audio-graph-card` and `audio-graph-scu-card`; removal delegates to `simple_util_remove()` and PM to `snd_soc_pm_ops`.

## Risks and Test Signals
Risks include complex OF graph lifetime/refcount handling, DPCM detection based on codec port endpoint count or convert properties, random topology issues if CPU/codec walk ordering changes, `SNDRV_MAX_LINKS` limits, optional pluggable codec endpoint handling, and component-chaining `no_pcm` decisions based on whether the CPU component exposes PCM. Test signals are normal one-link cards, multi-CPU/single-codec DPCM cards, convert-rate/format/channel fixups, link direction properties at top/port/endpoint scopes, PA GPIO toggling on DAPM power events, component chaining BE-to-BE paths, and clean reference cleanup on parse errors.
