# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-pdm.c

## Purpose
`acp-pdm.c` implements the ACP PDM/DMIC CPU DAI operations. It configures PDM clocks, channel count, ring buffer registers, interrupts, and start/stop control for digital microphone capture.

## Important APIs, Types, and Functions
The exported object is `acp_dmic_dai_ops` with `.prepare`, `.hw_params`, `.trigger`, `.startup`, and `.shutdown`. Important helpers are `acp_dmic_prepare()`, `acp_dmic_hwparams()`, `acp_dmic_dai_trigger()`, `acp_dmic_dai_startup()`, and `acp_dmic_dai_shutdown()`.

## Control Flow
Startup marks the runtime stream as DMIC, fills IRQ/PTE/register offsets, and enables the PDM DMA interrupt bit. `hw_params` validates channels as 2, 4, or 6, requires `S32_LE`, writes channel mask and decimation factor, and stores `chip->ch_mask`. Prepare enables default PDM clocking, calculates period and buffer sizes, picks the DMIC memory window based on ACP revision, writes ring buffer address/size/watermark, and enables ATU. Trigger start/resume/pause-release enables PDM and DMA and polls for the DMA enable bit; stop/suspend/pause-push disables both and polls for clear.

## State and Persistence
State lives in the PCM runtime private `struct acp_stream` and shared `struct acp_chip_info`. Register programming persists until stream shutdown, trigger stop, suspend, or hardware reset. No software state is persisted beyond runtime fields and `chip->ch_mask`.

## Dependencies and Integration Points
It depends on ACP register offsets from `amd.h`/`chip_offset_byte.h`, Linux `readl_poll_timeout_atomic()`, ASoC DAI callbacks, and the platform PCM open path that allocates `struct acp_stream`. It is referenced by revision DAI driver arrays in Renoir, Rembrandt, ACP63, and ACP70 platform drivers.

## Risks
Only `S32_LE` is accepted, so machine constraints must agree. Incorrect memory-window selection for ACP7x versus older revisions would break capture DMA. Polling is atomic and timeout-sensitive. Interrupt enable/disable must match stream lifetime or capture period notifications can be lost or noisy.

## Test Signals
Validate 2/4/6-channel DMIC capture, rejection of invalid formats/channels, DMA enable/disable timeout handling, period interrupts, suspend/resume restoration, and ACP70 memory-window capture. ALSA capture should show stable positions and no underrun-like stalls.
