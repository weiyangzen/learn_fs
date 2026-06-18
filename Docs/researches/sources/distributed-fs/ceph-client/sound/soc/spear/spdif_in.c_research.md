# sources/distributed-fs/ceph-client/sound/soc/spear/spdif_in.c

Purpose: ASoC CPU DAI driver for SPEAr S/PDIF input/capture.

Important APIs/functions: probe maps MMIO, obtains FIFO IO resource, IRQ, clock, and platform data, initializes DMA parameters, requests IRQ, registers component/DAI, and registers the shared SPEAr DMAEngine PCM platform. `spdif_in_configure()` enables parity/status/user/valid/block capture and FIFO threshold. DAI ops save requested format, enable clock and hardware on trigger start, program 16-bit extraction versus IEC958 subframe mode, disable and optionally reset peripheral on stop, and mask IRQs on shutdown. IRQ handler logs FIFO/write/out-of-range errors and clears status.

Control flow/state: `struct spdif_in_dev` stores clock, platform DMA data, saved format, MMIO base, optional reset callback, IRQ, and DMAEngine config. Hardware is configured at trigger start and disabled at trigger stop.

Dependencies/integration: depends on legacy `spear_spdif_platform_data`, `spear_dma_data`, shared `spear_pcm` helper, platform clock, IRQ, and IO resources.

Risks/test signals: probe requires platform data and IORESOURCE_IO FIFO resource, so it is not DT-generic. IRQ clear writes zero to the IRQ register, matching this hardware contract but worth validating. Tests should cover S16 and IEC958 capture, start/stop/reset, IRQ error injection, missing platform data/resource failures, and DMA filter behavior.
