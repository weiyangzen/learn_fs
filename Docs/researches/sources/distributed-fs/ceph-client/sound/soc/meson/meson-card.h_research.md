# sources/distributed-fs/ceph-client/sound/soc/meson/meson-card.h

Purpose: declares the shared Meson sound-card data structures and helper APIs used by Meson machine drivers.

Important APIs/types/functions: defines `DT_PREFIX`, `struct meson_card_match_data` with an `add_link` callback, and `struct meson_card` containing `snd_soc_card`, match data, and per-link private data. It declares sysclk, link allocation, DAI parse, FE/BE link setup, probe, and remove helpers.

Control flow: this header has no runtime flow but defines the contract: a platform driver supplies match data whose `add_link` callback is invoked by `meson_card_probe`; helper functions then build ASoC links from DT nodes.

State and persistence: `struct meson_card` is the persistent card-level state. `link_data` is an array of machine-specific pointers aligned with `card.dai_link` indices.

Dependencies and integration: includes only forward declarations plus ALSA parameter declarations to keep consumers light. Used by `gx-card.c` and `meson-card-utils.c`.

Risks: the callback API passes a mutable link index, so machine drivers must increment/consume it consistently. The `DT_PREFIX` macro couples CPU identification helpers to `"amlogic,"` compatible strings.

Test signals: compile coverage for all Meson machine drivers, successful link-data indexing, and no ABI drift between declarations and exported helper definitions.
