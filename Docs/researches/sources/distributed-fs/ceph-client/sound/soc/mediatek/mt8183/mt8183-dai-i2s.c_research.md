# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-i2s.c

Purpose: implements MT8183 I2S DAI support for I2S0/I2S1/I2S2/I2S3/I2S5, including interconnect mixers, low-jitter and MCLK DAPM supplies, APLL selection, shared-clock routing, format selection, sysclk handling, and per-port register programming.

Important APIs/types/functions: `struct mtk_afe_i2s_priv` stores per-I2S rate, low-jitter flag, shared-clock source, MCLK id/rate/APLL, and EIAJ format flag; low-jitter kcontrols expose `I2S*_HD_Mux`; DAPM mixers connect DL/ADDA/PCM sources to playback I2S ports; APLL/MCLK DAPM event handlers call the clock layer; route predicate callbacks decide shared I2S, HD, APLL, and MCLK paths; `mtk_dai_i2s_config` writes rate/format/word-length registers for each I2S id and recursively configures shared ports; `set_sysclk` records desired MCLK; `set_fmt` selects I2S or left-justified/EIAJ; `mt8183_dai_i2s_set_share` exports shared-clock setup to machine drivers; `mt8183_dai_i2s_register` allocates private state and registers DAIs/routes/controls.

Control flow: AFE probe registers I2S DAIs and initializes private state. Machine drivers call `mt8183_dai_i2s_set_share` during BE init for pairs like I2S2/I2S3 and I2S5/I2S0. hw_params records the rate, programs the selected I2S register fields, and configures any shared I2S source. set_sysclk validates output direction and APLL divisibility before saving MCLK state. DAPM routes turn on the matching APLL, MCLK divider, low-jitter supply, and I2S enable bits when audio paths become active.

State and persistence: per-DAI private state persists in `afe_priv->dai_priv`. Low-jitter kcontrol values and MCLK settings persist until changed or powered down; MCLK event clears `mclk_rate` on POST_PMD. Register settings are cached by the AFE regmap across runtime PM.

Dependencies and integration: depends on MT8183 clock helpers, register definitions, interconnection IDs, AFE private state, ALSA DAPM, and machine-driver init hooks. It integrates with memif routes for I2S capture/playback and external codecs via machine DAI links.

Risks: route predicates and private lookup rely on string prefixes like `I2S0`. `set_sysclk` propagates MCLK state only when `share_i2s_id > 0`, so sharing from or to ID 0 may not mirror state as intended. Recursive shared configuration could misbehave if cycles are introduced. Only I2S and left-justified formats are supported.

Test signals: all I2S ports at 8k-192k with S16/S24/S32, low-jitter control toggles, MCLK sysclk validation for 44.1k/48k families, shared I2S pairs used by machine drivers, left-justified variant cards, and DAPM/clock parent checks.
