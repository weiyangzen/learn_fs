# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp63.c

## Purpose
`acp63.c` is the ACP 6.3 platform driver. It defines SP/BT/HS I2S and PDM DAIs, programs ACP63 master clock PLL/DFS registers through AMD SMN, enables interrupts, registers the shared PCM component, and restores active streams after resume.

## Important APIs, Types, and Functions
Important objects/functions are `acp63_dai[]`, `union clk_pll_req_no`, `acp63_i2s_master_clock_generate()`, `acp63_audio_probe()`, `acp63_audio_remove()`, `acp63_pcm_resume()`, and platform driver `acp63_driver`.

## Control Flow
Probe validates revision `ACP63_PCI_ID`, sets DAI array/count, optionally programs I2S master clock when BIOS selected I2S and the resource requires SoC MCLK, enables ACP interrupts, registers the common platform component, and starts runtime PM. Resume regenerates MCLK when needed, then restores PTE/DMA and I2S/PDM stream parameters for every active stream in `chip->stream_list`.

## State and Persistence
No private state is allocated here. PLL/DFS hardware state and ACP stream registers are volatile and reprogrammed on probe/resume. Stream state is owned by the common platform layer.

## Dependencies and Integration Points
The file depends on AMD SMN read/write helpers, common ACP hardware ops, `asoc_acp_cpu_dai_ops`, `acp_dmic_dai_ops`, `config_pte_for_stream()`, `config_acp_dma()`, and restore helpers. `acp-pci.c` creates the `acp_asoc_acp63` platform device.

## Risks
Clock register programming is sequence-sensitive and has minimal polling compared with Rembrandt. One branch writes `data | PLL_FRANCE_EN` only when the bit is already set, which is hardware-specific and should be verified against clock specs. Probe does not check `acp_platform_register()` return.

## Test Signals
Test ACP63 SP/BT/HS playback/capture, PDM capture, SoC MCLK boards, suspend/resume with active I2S and DMIC streams, unsupported revision rejection, and interrupt disable on remove.
