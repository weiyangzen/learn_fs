# sources/distributed-fs/ceph-client/include/linux/platform_data/asoc-kirkwood.h

Purpose: provides a small platform-data struct for Kirkwood ASoC audio controller configuration.

Important APIs and types: `struct kirkwood_asoc_platform_data` contains `burst`, likely controlling DMA/audio burst behavior for the controller.

Control flow: platform setup passes the struct to the Kirkwood audio driver, which uses `burst` during controller/DMA configuration.

State and persistence: static boot-time configuration only. Runtime PCM/DMA state lives in the ASoC driver.

Dependencies and integration points: integrates Marvell Kirkwood board files with the ASoC platform driver.

Risks and test signals: risks include unsupported burst values and mismatch with DMA/FIFO capabilities. Test audio playback/capture with configured burst sizes, underrun/overrun behavior, and platform-data absence.
