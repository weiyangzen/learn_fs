# sources/distributed-fs/ceph-client/sound/soc/amd/acp-pcm-dma.c

## Purpose
`acp-pcm-dma.c` implements the legacy AMD ACP 2.x ASoC PCM platform driver. It initializes ACP hardware, configures page tables and SRAM DMA descriptors, manages playback/capture DMA channels for I2S SP/BT/MICSP instances, handles period interrupts, exposes PCM callbacks to ASoC, and supports runtime/system resume.

## Important APIs, Types, And Functions
Private state is `struct audio_drv_data` for device-wide streams/MMIO/ASIC type and `struct audio_substream_data` for per-stream DMA configuration. Important helpers include `acp_reg_read()`, `config_acp_dma_channel()`, `config_dma_descriptor_in_sram()`, `acp_pte_config()`, `config_acp_dma()`, `acp_dma_start()`, `acp_dma_stop()`, `acp_set_sram_bank_state()`, `acp_init()`, `acp_deinit()`, `dma_irq_handler()`, PCM callbacks `acp_dma_open()`, `hw_params()`, `prepare()`, `trigger()`, `pointer()`, `delay()`, `close()`, and platform probe/remove/PM callbacks.

## Control Flow
Probe maps MMIO, requests the ACP IRQ, stores ASIC type from platform data, initializes ACP reset/clock/DAGB/PTE/descriptor state, registers the ASoC platform component, and enables runtime PM. Open allocates per-stream state, selects PCM hardware constraints, enables interrupts on the first stream, and powers SRAM banks. `hw_params()` reads `acp_platform_info` from the machine driver, selects channel numbers, SRAM banks, PTE offsets, descriptor indices, byte-count registers, and writes PTEs/descriptors. Trigger starts circular DMA chains for playback or capture, and stop resets channels. IRQ handling reports period elapsed for playback channels and advances capture SYSRAM descriptors.

## State And Persistence
State persists in ACP MMIO registers, SRAM descriptor/PTE tables, stream pointers in `audio_drv_data`, per-stream byte counters and DMA metadata, SRAM bank power state, runtime PM state, and exported `acp_bt_uart_enable`. Resume reinitializes ACP and reprograms active stream DMA state.

## Dependencies And Integration Points
The driver depends on `acp.h` register/channel constants, AMD ASIC IDs, platform data from ACP PCI/device creation, ASoC component PCM callbacks, machine-driver `acp_platform_info`, IRQ handling, PM runtime, and DesignWare I2S/codec machine links.

## Risks And Edge Cases
The driver has many fixed channel/descriptor mappings and ASIC-specific Stoney exceptions. Interrupt handlers dereference active stream pointers and rely on open/close ordering. DMA stop polls can time out. Capture pointer/delay accounting is descriptor-based and sensitive to byte counter wrap. Global `acp_bt_uart_enable` can affect pad selection across devices.

## Test Signals
Tests should cover each I2S instance and direction, Stoney versus Carrizo constraints, period interrupt cadence, capture descriptor alternation, pause/resume, runtime PM suspend/resume with active streams, SRAM bank power transitions, DMA timeout injection, and machine-driver platform-info combinations.
