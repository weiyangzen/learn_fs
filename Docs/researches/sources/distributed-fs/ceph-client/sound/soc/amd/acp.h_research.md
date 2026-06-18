# sources/distributed-fs/ceph-client/sound/soc/amd/acp.h

## Purpose
`acp.h` defines register constants, SRAM addresses, DMA channel/descriptor IDs, I2S instance IDs, tile/power masks, and private data structures for the legacy AMD ACP 2.x PCM DMA driver and related machine drivers.

## Important APIs, Types, And Functions
Important definitions include ACP PTE offsets, SRAM bank addresses, DMA timeout constants, I2S route IDs, DMA channel numbers for SP/BT/MICSP instances, descriptor indices, `mmACP_I2S_16BIT_RESOLUTION_EN`, `enum acp_dma_priority_level`, `struct audio_substream_data`, `struct audio_drv_data`, `struct acp_platform_info`, `union acp_dma_count`, tile and DMA attribute enums, `acp_dma_dscr_transfer_t`, and exported `acp_bt_uart_enable`.

## Control Flow
There is no executable flow. `acp-pcm-dma.c` fills `audio_substream_data` from ALSA stream parameters and machine-driver `acp_platform_info`, then uses the constants to program ACP PTEs, descriptors, SRAM banks, byte counters, and DMA channel control.

## State And Persistence
The structures define persistent runtime state for device and stream objects. The macros encode hardware topology and descriptor layout that persists in ACP SRAM/register programming while streams are active.

## Dependencies And Integration Points
The header includes generated ACP 2.2 register definitions and is shared by legacy machine drivers and `acp-pcm-dma.c`. It is the contract through which machine drivers select playback/capture I2S instances and capture channels.

## Risks And Edge Cases
Wrong constants can route DMA to the wrong SRAM bank, I2S instance, descriptor, or byte counter. `acp_platform_info` is small but critical; missing or stale values cause the DMA driver to use defaults. The external `acp_bt_uart_enable` creates global coupling with machine driver properties.

## Test Signals
Tests should validate every constant path indirectly through playback/capture on SP, BT, and MICSP instances, descriptor programming inspection, byte-counter pointer checks, Stoney offsets, and BT pad selection behavior.
