# sources/distributed-fs/ceph-client/include/sound/graph_card.h

## Purpose
This header exposes ASoC audio graph card parsing helpers for device-tree described audio links, including graph-card2 customization hooks.

## Important APIs, Types, and Functions
`GRAPH2_CUSTOM` is a callback type taking `simple_util_priv`, a link node, and link info. `struct graph2_custom_hooks` allows pre/post hooks and custom handlers for normal, DPCM, and codec-to-codec links. Functions include `audio_graph_parse_of()`, `audio_graph2_parse_of()`, and built-in link parsers for normal, DPCM, and C2C links.

## Control Flow
Machine drivers call parse helpers during probe. The graph parser walks OF graph links, fills simple-card utilities, optionally invokes hooks before/after parsing, and dispatches link nodes to normal/DPCM/C2C handlers.

## State and Persistence
Parsing populates in-memory ASoC card/link structures from device tree. No persistent state is kept in this header.

## Dependencies and Integration Points
It depends on `sound/simple_card_utils.h` and integrates with OF graph bindings, ASoC simple-card infrastructure, DAI link construction, and machine driver customization.

## Risks and Edge Cases
Hook callbacks can override link behavior and must maintain simple-card invariants. Device-tree graph mistakes can produce partial cards or probe deferral. Link-type dispatch must match binding semantics.

## Test Signals
DT binding examples for normal, DPCM, and C2C links; custom hook invocation; probe deferral; and card registration with multiple links are relevant tests.
