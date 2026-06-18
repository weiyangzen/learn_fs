# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp70.c

## Purpose
`acp70.c` is the ACP 7.0/7.1/7.2 platform driver. It defines high-channel-count SP/BT/HS I2S and PDM DAIs, sets the ACP7x master clock divider, enables interrupts, registers the shared PCM component, and restores stream configuration on resume.

## Important APIs, Types, and Functions
Key objects/functions are `acp70_dai[]`, `acp_acp70_audio_probe()`, `acp_acp70_audio_remove()`, `acp70_pcm_resume()`, `acp70_dma_pm_ops`, and platform driver `acp70_driver`.

## Control Flow
Probe accepts ACP revisions `0x70`, `0x71`, and `0x72`, assigns the DAI array/count, writes `CLK7_CLK0_DFS_CNTL_N1` to set the I2S master clock near 196.608 MHz, enables ACP interrupts, registers the common PCM platform, and enables runtime PM. Resume walks live streams and restores PTE/DMA plus I2S/PDM parameters.

## State and Persistence
All runtime state lives in shared `struct acp_chip_info` and common `struct acp_stream` objects. ACP7x clock/divider and DMA registers are volatile across reset/sleep and restored by probe/resume paths.

## Dependencies and Integration Points
The driver depends on AMD SMN write support, common ACP platform registration, common CPU/PDM DAI ops, and ACP7x-specific DMA PTE mapping in `acp-platform.c`. It is instantiated as `acp_asoc_acp70`.

## Risks
The divider is programmed unconditionally for all accepted ACP7x revisions; board-specific clock exceptions would require additional gating. `acp_platform_register()` return is ignored. ACP70 allows up to 32 channels and 192 kHz, so machine/codec constraints must narrow unsupported external codecs.

## Test Signals
Validate ACP70/71/72 probe, SP/BT/HS 2-32 channel playback/capture, PDM capture, master-clock divider programming errors, suspend/resume with active streams, and removal with PM disabled and interrupts off.
