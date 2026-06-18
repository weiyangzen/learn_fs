# sources/distributed-fs/ceph-client/sound/soc/mediatek/Kconfig

## Purpose
Defines the MediaTek ASoC Kconfig hierarchy for common AFE support, SoC platform drivers, machine drivers, and BTCVSD Bluetooth SCO audio.

## Important APIs, Types, And Functions
`SND_SOC_MEDIATEK` selects `REGMAP_MMIO` and is selected by SoC-specific symbols. The file declares MT2701, MT6797, MT7986, MT8173, MT8183, MT8186, MT8188, MT8189, MT8192, MT8195, MT8365 platform support and many board-level codec combinations. `SND_SOC_MTK_BTCVSD` enables the software BTCVSD/MSBC transfer driver.

## Control Flow, State, And Persistence
No runtime state; this controls build inclusion and codec dependency selection.

## Dependencies And Integration Points
Integrates with the MediaTek Makefile and codec subsystem symbols such as MT635x PMIC codecs, HDMI codec, DMIC, BT SCO, and external I2C codec drivers.

## Risks And Test Signals
Risks include stale codec selects, incomplete COMPILE_TEST dependencies, and machine-driver symbols that select many optional codecs. Test signals are randconfig/allmodconfig builds and dependency validation for each SoC machine symbol.
