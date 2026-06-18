# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-rembrandt.c

## Purpose
`acp-rembrandt.c` is the ACP 6.x/Rembrandt platform driver. It defines Rembrandt I2S/PDM CPU DAIs, generates SoC master clock when needed, enables ACP interrupts, registers the common PCM component, and restores stream programming after system sleep.

## Important APIs, Types, and Functions
Key objects are `acp_rmb_dai[]` and platform driver `rembrandt_driver`. Important functions are `acp6x_master_clock_generate()`, `rembrandt_audio_probe()`, `rembrandt_audio_remove()`, and `rmb_pcm_resume()`.

## Control Flow
Probe validates platform data and ACP revision `ACP_RMB_PCI_ID`, assigns the Rembrandt DAI array to `chip`, optionally sends SMN messages to generate the SoC MCLK for I2S configs, enables ACP interrupts, registers the common ACP platform component, and enables runtime PM autosuspend. Resume regenerates MCLK when needed, walks `chip->stream_list`, reprograms PTE/DMA, and restores either I2S or PDM parameters for each active stream.

## State and Persistence
The file stores no private state outside `struct acp_chip_info`. Active streams persist in the common `stream_list`. SMN clock state and ACP DMA registers must be restored after sleep.

## Dependencies and Integration Points
It depends on AMD SMN access, ASoC platform registration, `asoc_acp_cpu_dai_ops`, `acp_dmic_dai_ops`, and common restoration helpers. It is instantiated by `acp-pci.c` as platform name `acp_asoc_rembrandt`.

## Risks
SMN register programming is hardware-specific and timeout-sensitive. Probe ignores the return value from `acp_platform_register()`. Resume holds `acp_lock` while calling register programming helpers, so helper behavior must remain non-sleeping. Missing MCLK generation can prevent codecs using SoC MCLK from working.

## Test Signals
Validate Rembrandt SP/BT/HS I2S and PDM DAI registration, SoC MCLK generation, runtime/system PM, suspend/resume playback/capture continuity, and clean removal with interrupts disabled and PM disabled.
