# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-dai-hostless.c

## Purpose

This file registers MT6797 hostless DAIs for ADDA loopback and speech routing, allowing internal audio paths to run without a normal CPU memory-interface endpoint.

## Important APIs, Types, and Functions

- `mtk_dai_hostless_routes[]` connects hostless loopback and speech DL/UL streams to ADDA and PCM capture/playback widgets.
- `mtk_dai_hostless_startup()` assigns the platform PCM hardware constraints.
- `mtk_dai_hostless_driver[]` defines `Hostless LPBK DAI` and `Hostless Speech DAI`.
- `mt6797_dai_hostless_register()` appends drivers and routes to the sub-DAI list.

## Control Flow

Platform probe calls the registration helper. At stream startup, hostless DAIs simply apply `afe->mtk_afe_hardware`. DAPM route activation determines which internal ADDA/PCM paths are powered and connected.

## State and Persistence Behavior

No private state. Active route and stream state is managed by ASoC DAPM/DPCM and common PCM runtime structures.

## Dependencies and Integration Points

Depends on ADDA widgets/routes from `mt6797-dai-adda.c`, PCM widgets/routes from `mt6797-dai-pcm.c`, and machine links in `mt6797-mt6351.c`.

## Risks and Edge Cases

Because this is route-only hardware control, route-name drift between files breaks paths at runtime. Hostless DAIs advertise broad high-rate formats, but actual linked ADDA/PCM routes may be narrower.

## Test Signals

Start hostless loopback and speech streams, inspect DAPM route activation, and confirm no external CPU memif DMA is required beyond expected ALSA runtime setup.
