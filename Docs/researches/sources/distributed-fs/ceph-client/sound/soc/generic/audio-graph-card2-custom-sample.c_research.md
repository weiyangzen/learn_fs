# sources/distributed-fs/ceph-client/sound/soc/generic/audio-graph-card2-custom-sample.c

Purpose: sample platform driver showing how a custom card can embed `struct simple_util_priv`, reuse `audio_graph2_parse_of()`, override graph-card2 hooks, and replace DAI link ops/card probe behavior. It is documentation-by-code for board-specific customization of `audio-graph-card2`.

Important APIs/types/functions: `struct custom_priv` wraps `simple_util_priv`; `simple_to_custom()` recovers the wrapper; `custom_hooks` provides `.hook_pre`, `.hook_post`, `.custom_normal`, `.custom_dpcm`, and `.custom_c2c`; `custom_ops` overrides startup while reusing `simple_util_shutdown()` and `simple_util_hw_params()`. `custom_probe()` allocates private data, sets a short card name, and delegates OF parsing to `audio_graph2_parse_of()`.

Control flow: platform probe allocates `custom_priv`, initializes `simple_priv->ops`, then calls the generic graph parser. The parser invokes `custom_hook_pre()` before link discovery, the custom link callbacks around each graph link type, and `custom_hook_post()` after parsing. The post hook replaces `card->probe` with `custom_card_probe()`, which sets an example custom parameter and then calls `graph_util_card_probe()` for jack initialization.

State and persistence: all state is devm-managed and tied to the platform device. The only custom state is `custom_params`, set to `1` at card probe time. Runtime stream state is handled by the shared simple-card utilities.

Dependencies/integration: depends on `sound/graph_card.h`, generic graph-card2 exported functions, ASoC card registration performed by `audio_graph2_parse_of()`, and the compatible string `audio-graph-card2-custom-sample`.

Risks: this sample trusts the generic parser for all allocation and registration; a real custom driver would need stricter validation around hook side effects. `custom_startup()` logs then delegates, so it must preserve the shared startup error semantics. The sample compatible is intentionally long and the actual card name is shortened, which can surprise tests that match names.

Test signals: useful smoke tests are module probe with a minimal audio graph DT, log verification that pre/post/link hooks ran, and playback/capture startup confirming custom ops call through to shared clock setup.
