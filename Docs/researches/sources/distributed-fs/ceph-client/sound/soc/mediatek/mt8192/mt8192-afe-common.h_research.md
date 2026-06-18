# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-common.h

This is the shared MT8192 AFE contract. It declares FE memory interfaces, backend DAI ids, IRQ ids, MTKAIF protocol modes, MCLK ids, `struct mt8192_afe_private`, and cross-file registration/helper prototypes.

The main enum defines FE memifs from `MT8192_MEMIF_DL1` through `MT8192_MEMIF_HDMI`, followed by backend DAIs such as ADDA, AP DMIC, CONNSYS I2S, I2S ports, PCM, and TDM. `struct mt8192_afe_private` stores clock pointers, syscon regmaps, sidetone gain, runtime-PM bypass state, `dai_on[]`, `dai_priv[]`, MTKAIF protocol/calibration fields, DMIC flags, ADDA6-only state, and MCK rates.

Platform probe allocates the private structure, clock init populates clock/syscon fields, and DAI registration populates `dai_priv[]`. The enum values are ABI-like inside the driver because memif arrays, IRQ maps, DAPM routes, and DAI ids index on them directly. Dependencies are MediaTek base AFE helpers, regmap, ASoC, and `mt8192-reg.h`. Test signals are complete DAI registration, correct ALSA PCM enumeration, and route activation for all major DAI families.
