# sources/distributed-fs/ceph-client/sound/soc/mediatek/Makefile

## Purpose
Routes MediaTek ASoC build symbols into common code and per-SoC subdirectories.

## Important APIs, Types, And Functions
Adds `common/` for `CONFIG_SND_SOC_MEDIATEK` and subdirectories for MT2701, MT6797, MT7986, MT8173, MT8183, MT8186, MT8188, MT8192, MT8195, MT8365, and MT8189.

## Control Flow, State, And Persistence
No runtime behavior; it is directory-level Kbuild metadata.

## Dependencies And Integration Points
The per-SoC Kconfig symbols decide which subdirectory Makefiles are entered.

## Risks And Test Signals
Risks are missing new SoC directories or symbol ordering drift. Test signals are per-symbol builds and allmodconfig traversal.
