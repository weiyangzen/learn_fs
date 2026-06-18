# sources/distributed-fs/ceph-client/sound/soc/au1x/Kconfig

## Purpose
Kconfig menu for Alchemy Au1x ASoC support. It separates newer PSC/DBDMA-based Au12xx/Au13xx/Au1550 support, older Au1000/Au1500/Au1100 AC97C/I2SC plus DMA support, and DB1000/DB1200-family board machine drivers.

## Important APIs, Types, And Functions
This is configuration data, not C code. Key symbols are `SND_SOC_AU1XPSC`, `SND_SOC_AU1XPSC_I2S`, `SND_SOC_AU1XPSC_AC97`, `SND_SOC_AU1XAUDIO`, `SND_SOC_AU1XAC97C`, `SND_SOC_AU1XI2SC`, `SND_SOC_DB1000`, and `SND_SOC_DB1200`.

## Control Flow
Menu selection controls which objects are built. Board symbols depend on the relevant core family and select CPU DAI, codec, and codec-bus helpers. Hidden tristate DAI symbols are selected by boards or parent options rather than exposed directly.

## State And Persistence
Build-time state only through kernel `.config`.

## Dependencies And Integration Points
Depends on `MIPS_ALCHEMY` for both core driver families. AC97 variants select `AC97_BUS`, `SND_AC97_CODEC`, and `SND_SOC_AC97_BUS`; board symbols select codecs such as generic AC97, WM9712, and WM8731 I2C.

## Risks
Hidden symbols mean direct platform enablement relies on board selections or manual config fragments. `SND_SOC_DB1200` selects both AC97 and I2S paths, so unused drivers/codecs can be pulled into a build. These options are architecture-specific and mostly untested outside MIPS Alchemy.

## Test Signals
Kconfig dependency resolution for `allyesconfig`, module builds for selected board symbols, and ensuring selected codec/helper symbols match the Makefile object names.
