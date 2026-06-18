# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-soundcard-driver.c

## Purpose
Provides common MediaTek machine-driver probe and DAI-link parsing logic, including codec binding, DAI format parsing, PCM constraints, accessory-detect lookup, platform/ADSP node assignment, and SOF setup.

## Important APIs, Types, And Functions
Exports `parse_dai_link_info()`, `clean_card_reference()`, `mtk_soundcard_startup()`, `mtk_soundcard_common_playback_ops`, `mtk_soundcard_common_capture_ops`, and `mtk_soundcard_common_probe()`. Private helpers parse codec child nodes and DAI formats including `mediatek,clk-provider`.

## Control Flow, State, And Persistence
Common probe obtains platform data from match data, sets the card device/name, chooses legacy or audio-routing mode, allocates `mtk_soc_card_data` and jack storage, optionally locates an accdet component, resolves `mediatek,platform`, optionally parses ADSP/SOF configuration and selected DAI links, assigns platform nodes to links, parses per-link codec/format data, invokes optional SoC-specific probe, attaches card drvdata, registers the card, and restores DAI arrays on errors.

## Dependencies And Integration Points
Depends on MediaTek machine pdata definitions from `mtk-soundcard-driver.h`, OF graph/child-node conventions, ASoC codec parsing, SOF helpers, and optional accessory-detect components referenced by `mediatek,accdet`.

## Risks And Test Signals
Risks include static card templates being mutated and restored on error, codec references cleaned immediately after card registration, legacy probe dependence on SoC callbacks, `unlikely(!mpc)` on an address that is normally non-null, name-based DAI-link lookup, and platform-node ownership. Test signals include DTs with and without `audio-routing`, codec-less dummy links, multiple `mediatek,dai-link` selections, ADSP/SOF and non-SOF cards, accdet phandle resolution, and startup rate/channel constraints.
