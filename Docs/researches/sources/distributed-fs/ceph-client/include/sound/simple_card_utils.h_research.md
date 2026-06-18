<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/simple_card_utils.h -->
# sources/distributed-fs/ceph-client/include/sound/simple_card_utils.h

## Purpose
`simple_card_utils.h` is the shared helper interface for ASoC simple-card and audio-graph-card drivers. It centralizes DAI parsing, clock/TDM conversion, jack setup, link allocation, naming, routing/widgets, and debug output.

## Important APIs, types, and functions
Key types are `simple_util_tdm_width_map`, `simple_util_dai`, `simple_util_data`, `simple_util_jack`, `prop_nums`, `simple_util_priv`, and `link_info`. Macros map private data to cards, props, links, DAI link components, DAI structs, and codec configs; iteration macros walk CPUs/codecs/platforms and DAI objects. APIs include parsing helpers for DAI format, TDM width maps, clocks, card names, conversion properties, routing, widgets, pin switches, aux jacks, and graph endpoints; runtime hooks `simple_util_startup()`, `shutdown()`, `hw_params()`, `dai_init()`, and `be_hw_params_fixup()`; canonicalization helpers; private allocation/removal; and debug dump helpers under `DEBUG`.

## Control flow
Probe code initializes `simple_util_priv`, parses firmware nodes into link and DAI property arrays, canonicalizes CPU/platforms, sets link names, initializes jacks and aux devices, then registers the ASoC card. Runtime PCM callbacks apply clocks, TDM, conversion, and backend fixups through the shared hooks.

## State and persistence behavior
`simple_util_priv` owns the runtime card, link/property arrays, DAI descriptors, component arrays, codec configs, jacks, PA GPIO, flags for DPCM selection, and ops pointer. State is in memory and cleaned by `simple_util_remove()`/reference cleanup.

## Dependencies and integration points
It depends on clocks, GPIO descriptors through `soc.h`, ASoC card/link/DAI types, device tree nodes, and graph-card parsing conventions. It is the shared substrate for multiple generic machine drivers.

## Risks and test signals
Risks include array-count mismatches in `link_info`, invalid `rtd->id` use avoided by `runtime_simple_priv_to_props()`, clock leaks, broken TDM width maps, conversion parameters not mirrored into BE fixups, jack GPIO lifetime, and graph endpoint direction parsing errors. Test signals include single and multi-CPU/codec links, DPCM selectable/forced paths, audio graph ports, TDM slots and width maps, mclk-fs ordering, convert-rate/channels/format, aux jacks, pin switches, and debug output correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/simple_card_utils.h -->
