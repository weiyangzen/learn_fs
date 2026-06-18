# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x.c

Purpose: implements the bus-independent TI PCM179x/PCM1792A stereo DAC ASoC core with regmap defaults, format setup, mute, playback volume and DAC controls, DAPM current outputs, and exported common init/regmap configuration for I2C and SPI wrappers.

Important APIs, types, and functions: private state is `struct pcm179x_private`. Public exports are `pcm179x_regmap_config` and `pcm179x_common_init()`. Core functions are `pcm179x_set_dai_fmt()`, `pcm179x_mute()`, `pcm179x_hw_params()`, `pcm179x_accessible_reg()`, and `pcm179x_writeable_reg()`.

Control flow: bus wrapper creates a regmap and calls common init, which allocates private state, stores the regmap, attaches drvdata, and registers the component/DAI. `set_fmt()` records serial format. `hw_params()` maps right-justified 16/24/32 and I2S 16/24/32 to format bits, enables ATLD, and writes `PCM179X_FMT_CONTROL`. `mute_stream()` updates the soft-mute bit. Controls expose left/right DAC volume, output inversion, and rolloff filter.

State and persistence: private state stores regmap, current format, and current rate. Regmap defaults cover registers 0x10 through 0x17; status registers 0x16 and 0x17 are readable but not writeable. No explicit suspend/resume callbacks or reset resources are present.

Dependencies and integration points: depends on ALSA SoC/TLV/DAPM, regmap, OF declarations, and `pcm179x.h`. DAI name is `pcm179x-hifi`; playback is stereo, continuous 10 kHz to 200 kHz, using the format mask from `PCM1792A_FORMATS`. Bus integration is through `pcm179x-i2c.c` and `pcm179x-spi.c`.

Risks: only I2S and right-justified formats are accepted; left-justified is unsupported despite similar sibling drivers supporting it. No clock-provider validation is performed. Hardware reset and power sequencing are delegated entirely to board design. Format macro names PCM1792A specifically while common driver is generic.

Test signals: probe through both I2C and SPI, verify accepted and rejected serial formats/widths, confirm ATLD and format bits in regmap, test mute polarity, volume TLVs, invert and rolloff controls, and regmap read/write access masks.
