# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-mt6366-common.h

## Purpose

`mt8186-mt6366-common.h` declares the shared MT8186/MT6366 machine-driver helpers implemented in `mt8186-mt6366-common.c`. The complete 17-line header was read.

## Important APIs, Types, and Functions

It declares `mt8186_mt6366_init(struct snd_soc_pcm_runtime *rtd)` and `mt8186_mt6366_card_set_be_link(struct snd_soc_card *card, struct snd_soc_dai_link *link, struct device_node *node, char *link_name)`. It defines only the include guard `_MT8186_MT6366_COMMON_H_`.

## Control Flow

There is no executable control flow. Including machine drivers compile against these prototypes and call the helpers during card initialization or legacy probe setup.

## State and Persistence Behavior

The header owns no storage. State effects are in the implementation: MTKAIF protocol caching in AFE private data and in-memory DAI-link codec assignment.

## Dependencies and Integration Points

The declarations reference ASoC types `struct snd_soc_pcm_runtime`, `struct snd_soc_card`, and `struct snd_soc_dai_link`, plus `struct device_node`. It is included by `mt8186-mt6366.c` and should remain synchronized with exported function signatures in the implementation.

## Risks and Edge Cases

No direct runtime risk exists, but signature drift between this header and `mt8186-mt6366-common.c` would break builds. The non-const `char *link_name` is more permissive than necessary and can propagate const-correctness warnings if callers use string constants in stricter contexts.

## Test Signals

Build coverage for MT8186 machine drivers is the main signal. Include-order testing should confirm the referenced ASoC structs are declared by included source files before use or accepted as incomplete struct declarations by the compiler.
