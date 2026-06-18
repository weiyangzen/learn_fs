# sources/distributed-fs/ceph-client/sound/soc/meson/axg-card.c

Purpose: Implements the AXG sound-card machine driver glue that builds FE/BE DAI links from device tree, handles TDM slot parsing, configures codec and CPU TDM masks, adds loopback links, and delegates common card parsing to Meson card utilities.

Important APIs and functions: The platform driver probes with `meson_card_probe()` using `axg_card_match_data`. `axg_card_add_link()` classifies each CPU node as playback FE, capture FE, TDM interface, codec-control, or generic backend. `axg_card_parse_tdm()` allocates per-link TDM data, parses format/mclk/slot masks, sets link ops/init, and adds loopback when playback exists. `axg_card_tdm_dai_init()` programs codec DAI slots and calls `axg_tdm_set_tdm_slots()` for the CPU DAI. `axg_card_tdm_be_hw_params()` sets sysclk from `mclk-fs`.

Control flow: Common Meson card parsing calls `add_link` for each DT link. FRDDR/TODDR nodes become dynamic FE links. Codec-control backends get codec-to-codec params. TDM interface backends parse per-lane CPU masks (`dai-tdm-slot-tx-mask-N`/`rx-mask-N`), codec child masks, slot count/width, and optional `mclk-fs`; if playback slots exist, a synthetic capture-only `TDM Loopback` backend link is inserted immediately after the pad link.

State and persistence: `struct axg_dai_link_tdm_data` persists in `priv->link_data[rtd->id]`, holding mclk ratio, slot count/width, lane masks, and per-codec masks. DAI link arrays may be reallocated when loopback links are inserted. Slot settings persist in CPU and codec DAIs.

Dependencies and integration points: Depends on `meson-card` utilities, `axg-tdm.h` interface APIs, device-tree compatible prefixes, ASoC DPCM, and codec drivers supporting `snd_soc_dai_set_tdm_slot()`.

Risks: Slot-mask parsing uses max mask value to infer direction and slot count, so malformed masks can disable playback/capture or produce bad slot totals. Link insertion must keep `link_data` aligned with reallocated DAI links and balance OF node references. Codec mask order follows child-node order and must match codec DAI order. TDM slot count is capped at 32.

Test signals: AXG card probe with FRDDR/TODDR/TDM/SPDIF/PDM links, DT validation for TDM masks, loopback DAI visibility, multicodec TDM links, DPCM hw_params setting mclk, and error tests for no CPU slots or undersized slot counts.
