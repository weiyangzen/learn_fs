# sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-imx-ssi.h

Purpose: declares platform data and FIQ-related symbols for Freescale/NXP i.MX SSI ASoC support.

Important APIs and types: extern FIQ symbols expose `imx_ssi_fiq_start/end/base/tx_buffer/rx_buffer`. `struct imx_ssi_platform_data` carries mode flags (`IMX_SSI_DMA`, `IMX_SSI_USE_AC97`, `IMX_SSI_NET`, `IMX_SSI_SYN`, `IMX_SSI_USE_I2S_SLAVE`) and AC97 reset/warm-reset callbacks. `mxc_set_irq_fiq()` configures an IRQ as FIQ.

Control flow: machine/platform code supplies SSI flags and AC97 callbacks; the ASoC SSI driver chooses DMA or FIQ paths, AC97/I2S/network/synchronous modes, and configures FIQ interrupt handling when needed.

State and persistence: platform data is static audio-interface configuration. Runtime audio buffers, FIQ code/data, DMA channels, and codec state live in driver/platform code.

Dependencies and integration points: integrates i.MX SSI controller drivers, ASoC, AC97 codec handling, FIQ assembly code, IRQ configuration, and optional DMA.

Risks and test signals: risks include incompatible mode flags, FIQ buffer symbol/linkage issues, AC97 reset callback lifetime, and IRQ/FIQ misconfiguration. Test playback/capture with DMA and FIQ, AC97 cold/warm reset, I2S slave mode, network/synchronous modes, and build/link coverage for FIQ symbols.
