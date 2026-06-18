# sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-s3c.h

Purpose: defines Samsung S3C/S5P ASoC platform data for AC97/I2S/PCM GPIO setup, DMA filtering, and I2S controller quirks.

Important APIs and types: `S3C64XX_AC97_GPD` and `S3C64XX_AC97_GPE` identify GPIO banks for AC97 pins. `struct samsung_i2s_type` contains quirk bits such as primary 5.1 channels, secondary DAI, no internal mux/prescaler, reset clear requirement, TDM support, IDMA support, and an IDMA address. `struct s3c_audio_pdata` supplies `cfg_gpio()`, DMA filter function, playback/capture DMA data for primary/secondary/mic paths, and the I2S type descriptor.

Control flow: machine init code selects GPIO bank and passes platform data; the ASoC driver configures pin muxes, chooses DMA channels through `dma_filter`, and adapts register/DAI behavior according to quirks.

State and persistence: static SoC/board description. Runtime DAI, DMA, clock, and register state live in Samsung ASoC drivers.

Dependencies and integration points: depends on dmaengine types and `platform_device`. Integrates Samsung pin configuration, DMA engine channel selection, ASoC DAI setup, AC97/PCM/I2S modes, and SoC-specific I2S variants.

Risks and test signals: risks include wrong quirk bits causing broken clocks/channels, DMA filter data mismatch, GPIO config callback failure, and IDMA address errors. Test playback/capture on primary/secondary/mic paths, TDM/5.1 modes, AC97 GPIO bank setup, DMA allocation failure, and suspend/resume.
