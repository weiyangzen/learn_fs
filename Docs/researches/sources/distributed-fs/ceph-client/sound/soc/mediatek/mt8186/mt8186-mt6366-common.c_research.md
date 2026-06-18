# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-mt6366-common.c

## Purpose

`mt8186-mt6366-common.c` provides shared helpers for MT8186 machine drivers that use the MT6366/MT6358 codec path. It initializes the MTKAIF protocol for the primary codec runtime and offers a helper to replace backend link codecs from device-tree nodes. The complete 57-line file was read.

## Important APIs, Types, and Functions

Public exported functions are `mt8186_mt6366_init(struct snd_soc_pcm_runtime *rtd)` and `mt8186_mt6366_card_set_be_link(struct snd_soc_card *card, struct snd_soc_dai_link *link, struct device_node *node, char *link_name)`. Both are exported with `EXPORT_SYMBOL_GPL`.

## Control Flow

`mt8186_mt6366_init()` looks up the AFE component by `AFE_PCM_NAME`, obtains the codec component from the runtime, retrieves `mt8186_afe_private`, calls `mt6358_set_mtkaif_protocol()` with `MT6358_MTKAIF_PROTOCOL_1`, stores the selected protocol in `afe_priv->mtkaif_protocol`, and synchronizes DAPM. If `snd_soc_dapm_sync()` fails, it logs and returns the error.

`mt8186_mt6366_card_set_be_link()` checks whether a device-tree node is present and whether the current link name matches the requested backend link name. For matching links it calls `snd_soc_of_get_dai_link_codecs()` to populate the link codec array from the node and returns a probed error on failure.

## State and Persistence Behavior

The only cached state is `afe_priv->mtkaif_protocol`, which persists for the lifetime of the AFE device. Codec link replacement mutates the in-memory `snd_soc_dai_link` before card registration. There is no persistent storage.

## Dependencies and Integration Points

The file includes ASoC headers, codec header `mt6358.h`, common MediaTek platform headers, `mt8186-afe-common.h`, and its companion header. It is used by `mt8186-mt6366.c` for primary codec init and legacy device-tree backend codec assignment.

## Risks and Edge Cases

`snd_soc_rtd_to_codec(rtd, 0)` assumes at least one codec component exists. The helper only updates codecs for exact link-name matches, so renamed backend links in the machine driver or device tree would silently skip replacement. `char *link_name` could be `const char *`; current API permits modification even though no modification is intended.

## Test Signals

Probe logs should show successful primary codec init without DAPM sync errors. Regmap/codec traces should confirm MTKAIF protocol 1 is set. Legacy device-tree cards should bind playback and headset codecs into the intended I2S backend links; missing child nodes should produce probe errors in the caller.
