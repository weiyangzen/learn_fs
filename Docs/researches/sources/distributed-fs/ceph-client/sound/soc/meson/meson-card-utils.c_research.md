# sources/distributed-fs/ceph-client/sound/soc/meson/meson-card-utils.c

Purpose: shared helper implementation for Meson machine drivers. It parses DT sound-card links, allocates link arrays, builds FE/BE links, handles optional routing/widgets, and registers/unregisters the card.

Important APIs/types/functions: exports `meson_card_i2s_set_sysclk`, `meson_card_reallocate_links`, `meson_card_parse_dai`, `meson_card_parse_daifmt`, `meson_card_set_be_link`, `meson_card_set_fe_link`, `meson_card_probe`, and `meson_card_remove`.

Control flow: `meson_card_probe` allocates `struct meson_card`, copies match data, sets card owner/device/name, parses optional widgets/routing, calls `meson_card_add_links`, then registers with `devm_snd_soc_register_card`. Link creation reallocates `card.dai_link` and `link_data`, then invokes the machine-specific `add_link` callback for each DT child.

State and persistence: per-card state is devm allocated except link arrays and link-data arrays, which use `krealloc` and are freed by `meson_card_remove` through `meson_card_clean_references`. OF node references acquired in link components are released explicitly.

Dependencies and integration: depends on ASoC OF helpers, DAPM route/widget parsers, `meson-card.h`, and match-data callbacks supplied by concrete machine drivers such as GX.

Risks: `meson_card_reallocate_links` frees the new links allocation if link-data allocation fails, which is dangerous if `krealloc` moved the original pointer and may leave stale card state. Link names use `node->full_name`, so DT path changes affect ALSA stream names. Reference cleanup must stay matched to parsed components.

Test signals: malformed DT with no links or missing codecs returns errors; optional widgets/routing parse correctly; FE links are dynamic with dummy codecs; BE links parse all child codecs; remove releases OF references without leaks.
