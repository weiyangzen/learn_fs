# sources/distributed-fs/ceph-client/sound/soc/renesas/siu.h

Purpose: Shared header for the Renesas/SuperH SIU ASoC driver and its firmware format. It defines SPB firmware memory layout, SIU register offsets, common runtime structures, and cross-file exports used by `siu_dai.c` and `siu_pcm.c`.

Important APIs, types, and functions: `struct siu_spb_param` describes one SPB routing program entry. `struct siu_firmware` embeds FIR coefficients, PRAM program blocks, YRAM defaults, and up to 32 SPB params. Kernel-only structs include `siu_info` for global device resources, `siu_stream` for one playback/capture DMA stream, and `siu_port` for per-port duplex, PCM, stream, STFIFO, and TRDAT state. Exports include `siu_ports`, `siu_component`, `siu_i2s_data`, `siu_init_port`, and `siu_free_port`.

Control flow: This file has no executable flow, but it establishes the shared data model: DAI probe loads firmware into `siu_info`, PCM component allocates `siu_port`, and stream callbacks use `siu_port_info()` to map a substream to the platform-device id.

State and persistence: State is in global `siu_i2s_data` and `siu_ports[SIU_PORT_NUM]`, making the driver effectively singleton per SIU block. Firmware arrays are copied into `siu_info->fw` and later rewritten before programming PRAM/YRAM.

Dependencies and integration: Depends on ALSA SoC/PCM headers, DMAEngine, SuperH DMA `sh_dma.h`, raw MMIO helpers, and platform ids for SIU port A/B.

Risks and edge cases: The header codifies "only one SIU port can be used at a time"; global state makes multi-device instances unsafe. Firmware structure size and binary `siu_spb.bin` must match exactly. `siu_port_info()` trusts `pdev->id`.

Test signals: Build coverage should catch firmware-layout or register macro mismatches. Runtime validation comes from successful SIU probe, firmware load, PCM creation for the expected port id, and DMA stream start.
