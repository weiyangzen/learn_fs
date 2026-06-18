# sources/distributed-fs/ceph-client/sound/soc/generic/simple-card.c

Purpose: generic `simple-audio-card` / `simple-scu-audio-card` machine driver. It parses either DT-described simple card links or legacy platform data into ASoC card/link structures and registers the card.

Important APIs/types/functions: `simple_probe()` is the platform entry point; `simple_get_dais_count()`, `simple_count_noml()`, and `simple_count_dpcm()` size allocations; `simple_parse_of()` handles widgets/routing/pin switches/aux devices; `simple_for_each_link()` and `__simple_for_each_link()` iterate CPU/codec child nodes; `simple_dai_link_of()` handles normal links; `simple_dai_link_of_dpcm()` handles DPCM FE/BE links. `simple_ops` delegates stream ops to simple-card-utils.

Control flow: probe allocates private/card state, counts DAI links, initializes arrays with `simple_util_init_priv()`, then parses DT if present. DT parsing loops CPU-side first and codec-side second to keep stable DPCM numbering. Normal links parse CPU, codec, optional platform, canonicalize CPU/platform, set format/direction/trigger/mclk, and name the link. DPCM links create dynamic FE CPU-dummy links or no-PCM BE dummy-CPU links, parse conversion properties, and attach BE fixups. Legacy platform data fills one link directly.

State and persistence: per-card state is devm-managed in `simple_util_priv`. Link properties persist in `simple_dai_props`; DPCM codec prefixes are stored in codec conf. Additional devices under `simple-audio-card,additional-devs` are populated and depopulated by a devm action.

Dependencies/integration: integrates with `sound/simple_card.h`, `sound/soc-dai.h`, `simple-card-utils`, OF platform population, and DT properties prefixed with `simple-audio-card,`. It can select DPCM behavior only for the `simple-scu-audio-card` compatible via match data.

Risks: DPCM selection is heuristic: many child nodes or convert properties switch behavior, so malformed DT can produce unexpected FE/BE splits. The iterator treats child counts and additional-devs specially; changes to binding layout can affect parsing. Legacy platform-data path requires many non-null fields and has less validation than DT path. Link count must not exceed `SNDRV_MAX_LINKS`.

Test signals: DT probe tests for old top-level syntax, new `dai-link` nodes, optional `plat`, `additional-devs`, `aux-devs`, DPCM conversion, routing/widgets/pin-switches, and legacy platform-data fallback. Runtime tests should verify stable PCM numbering for multi-link DPCM cards.
