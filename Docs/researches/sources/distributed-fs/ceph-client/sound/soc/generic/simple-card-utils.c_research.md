# sources/distributed-fs/ceph-client/sound/soc/generic/simple-card-utils.c

Purpose: shared helper library for generic simple-card and audio-graph-card drivers. It centralizes DT parsing, DAI link allocation, clock/TDM setup, conversion constraints, jack helpers, codec-to-codec defaults, and cleanup.

Important APIs/types/functions: exported helpers include `simple_util_parse_convert()`, `simple_util_is_convert_required()`, `simple_util_parse_daifmt()`, `simple_util_parse_tdm_width_map()`, `simple_util_set_dailink_name()`, `simple_util_parse_card_name()`, `simple_util_parse_clk()`, `simple_util_startup()`, `simple_util_shutdown()`, `simple_util_hw_params()`, `simple_util_be_hw_params_fixup()`, `simple_util_dai_init()`, canonicalization helpers, widget/routing/pin/jack parsers, `simple_util_init_priv()`, `simple_util_remove()`, `graph_util_card_probe()`, `graph_util_parse_dai()`, link direction, and trigger-order parsing.

Control flow: probe users first count link component cardinalities, call `simple_util_init_priv()` to allocate contiguous link/property/DAI/DLC arrays, then fill those arrays. At PCM startup, clocks are enabled for all CPU and codec DAIs and fixed sysclk constraints are applied. At hw_params, `mclk-fs` drives clock rate programming and `snd_soc_dai_set_sysclk()`, then TDM slot maps are applied. Shutdown reverses non-fixed sysclk and disables clocks. DAI init programs static sysclk/TDM and auto-populates codec-to-codec params when all runtime components are codecs.

State and persistence: `simple_util_priv` owns devm arrays for DAI links, DAI props, DAIs, link components, codec conf, optional aux jacks, and GPIO jack state. `simple_util_data` stores requested convert-rate/channels/sample-format and is used during DPCM BE fixup. Clocks and OF nodes remain associated with DAI props until card removal.

Dependencies/integration: depends on ASoC core, OF/OF graph parsing, common clock framework, GPIO consumer API, jack helpers, PCM params, and DT bindings from `dt-bindings/sound/audio-graph.h`. It is the shared dependency for `simple-card.c`, `audio-graph-card2.c`, and custom graph-card drivers.

Risks: clock enable error unwinding must stay aligned with loop indices; fixed sysclk plus `mclk-fs` rejects non-divisible rates at startup. DAI lookup has two paths, direct DAI args and fallback DLC resolution, and mishandled node references can leak or underflow. `graph_util_parse_trigger_order()` uses a static local `order`, which is harmless for sequential use but unnecessary shared state. Conversion sample format parsing accepts only a small string table.

Test signals: unit-like DT probes for convert properties, TDM width maps, fixed clocks, missing/legacy clock provider flags, jack GPIOs, aux jack components, and codec-to-codec links. Runtime PCM tests should verify startup failure unwinds all clocks and hw_params applies sysclk/TDM in CPU-first and codec-first modes.
