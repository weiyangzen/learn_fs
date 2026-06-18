# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-renoir.c

## Purpose
`acp-renoir.c` is the ACP 3.x/Renoir platform driver. It defines Renoir SP/BT I2S and PDM CPU DAIs, enables interrupts, registers the shared PCM component, and restores ACP stream register state after system resume.

## Important APIs, Types, and Functions
Important objects are `acp_renoir_dai[]` and platform driver `renoir_driver`. Main functions are `renoir_audio_probe()`, `renoir_audio_remove()`, and `rn_pcm_resume()`.

## Control Flow
Probe validates platform data and revision `ACP_RN_PCI_ID`, assigns the DAI driver array/count, enables ACP interrupts, registers the common platform component, and enables runtime PM. Remove disables interrupts and unregisters the platform component. Resume iterates active streams under `acp_lock`, reconfigures PTEs/DMA for the ALSA buffer, and restores I2S or PDM parameters depending on `stream->dai_id`.

## State and Persistence
State is held in shared `struct acp_chip_info` and stream objects allocated by `acp-platform.c`. Renoir-specific DAI definitions are static module data. Hardware register state is volatile across sleep and restored from stream/runtime parameters.

## Dependencies and Integration Points
It integrates with platform devices named `acp_asoc_renoir`, common ACP hardware ops, `asoc_acp_cpu_dai_ops`, `acp_dmic_dai_ops`, and machine drivers that reference Renoir platform component names.

## Risks
`acp_platform_register()` return is not checked, so later failures could leave probe appearing successful. Resume assumes active stream runtime data is valid. Renoir capture capabilities differ from later ACP revisions, so machine constraints must avoid unsupported channel/rate formats.

## Test Signals
Test Renoir SP/BT playback and capture, DMIC capture, interrupt delivery, suspend/resume during active streams, unsupported-revision rejection, and removal after active card registration.
