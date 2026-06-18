# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-hostless.c

## Purpose

`mt8186-dai-hostless.c` registers virtual/hostless DAIs and DAPM routes for internal audio paths that do not represent direct CPU memory-interface playback/capture. These paths connect ADDA loopback, FM, SRC, barge-in, hardware gain, and AAudio-style internal routes.

## Important APIs, Types, and Functions

`mt8186_hostless_hardware` defines PCM constraints for hostless streams. `mtk_dai_hostless_routes[]` connects hostless stream endpoints to existing DAPM widgets: ADDA UL to ADDA/I2S playback for loopback, connsys I2S through HW gain to ADDA/I2S for FM, SRC outputs to ADDA/I2S, I2S0 into SRC for barge-in, and HW gain 2 into SRC 2 for AAudio. `mtk_dai_hostless_startup()` applies hostless hardware constraints and requires integer periods. `mtk_dai_hostless_driver[]` defines FE hostless DAIs for LPBK, FM, SRC_1, SRC_Bargein, AAudio HW gain/SRC, and BE capture-only DAIs for UL1/UL2/UL3/UL5/UL6.

`mt8186_dai_hostless_register()` allocates an AFE sub-DAI group, adds it to `afe->sub_dais`, and attaches the hostless DAI-driver and route arrays.

## Control Flow and State

There is no direct hardware register programming in this file. Probe-time registration publishes DAI and route definitions. Runtime startup only applies ALSA constraints; actual audio routing and hardware enablement happens through the DAPM widgets and DAIs supplied by ADDA, I2S, SRC, gain, and memif files.

## Dependencies and Integration Points

The file depends on `mt8186-afe-common.h` for DAI IDs and MediaTek base AFE list structures. It integrates tightly with route names from ADDA, I2S, SRC, gain, connsys I2S, and memif DAPM definitions; route-name mismatches prevent DAPM graph construction.

## Risks

Because routes are string-based, renaming a widget or stream in another DAI file can silently break hostless paths at runtime. Hostless startup does not program rates into hardware itself, so the backing BE DAIs must receive compatible hw_params through normal ASoC routing. The comment typo "Hostelss" is harmless but should not propagate into user-visible stream names.

## Test Signals

Test DAPM graph creation with no unresolved routes, then exercise hostless loopback, FM, SRC, barge-in, and AAudio paths. `aplay`/`arecord` or machine-driver path tests should confirm constraints, route power-up, and audio movement through the corresponding hardware blocks.
