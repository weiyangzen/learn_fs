# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-soundcard-driver.h

## Purpose

This header is the shared MediaTek ASoC sound-card contract used by newer machine drivers. It describes platform card data, optional SOF private data, PCM startup constraints, and the common probe/parsing helpers that bind a `snd_soc_card` to platform/codec DAI-link information.

## Important APIs, Types, and Functions

- `enum mtk_pcm_constraint_type` indexes playback, capture, and HDMI/DP constraint slots.
- `struct mtk_pcm_constraints_data` carries optional channel and rate constraint lists for startup.
- `struct mtk_platform_card_data` holds the `snd_soc_card`, jack array, PCM constraints, counts, and flags.
- `struct mtk_soundcard_pdata` exposes board-specific card name/data, SOF integration data, and an optional `soc_probe()` hook.
- `mtk_soundcard_common_playback_ops` and `mtk_soundcard_common_capture_ops` are reusable FE startup ops.
- `mtk_soundcard_startup()`, `parse_dai_link_info()`, `clean_card_reference()`, and `mtk_soundcard_common_probe()` are exported helper entry points.

## Control Flow

The header has no executable flow. Consumers supply a `platform_device` and platform data to `mtk_soundcard_common_probe()`, which is expected to parse DAI-link information, apply card references, run optional SoC-specific probing, and register the ASoC card. Runtime stream startup calls flow through common playback/capture ops into `mtk_soundcard_startup()` to enforce the selected constraint set.

## State and Persistence Behavior

The file defines in-memory card metadata only. State lives in the card data, jack data, constraints, and any SOF/private data that consumers attach. Persistence is handled by ASoC core and platform drivers, not this header.

## Dependencies and Integration Points

It depends on ALSA SoC types, platform devices, and MediaTek-specific SOF/card data declared elsewhere. It is an integration seam between machine drivers, device-tree DAI-link parsing, optional SOF support, and common stream-constraint handling.

## Risks and Edge Cases

Constraint indexes must match `MTK_CONSTRAINT_MAX`; mismatched counts can make startup access the wrong constraint slot. `card_data->card` and jack arrays are borrowed references, so lifetime must outlive probe/registration. Shared parsing helpers need strict cleanup on partial probe failures to avoid stale OF/component references.

## Test Signals

Build all MediaTek machine drivers using this header. Runtime signals are successful card registration, correct DAI-link population from DT, jack creation, and startup failures for intentionally unsupported rates/channels.
