# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x.h

## Purpose
This header defines Vangogh ACP5x constants, memory layout, stream structures, MMIO helpers, byte-count helper, and I2S master clock programming helper for the Vangogh PCI, I2S, DMA, and machine drivers.

## Important APIs, Types, And Functions
Important declarations include `struct i2s_dev_data`, `struct i2s_stream_instance`, `struct acp5x_platform_info`, `union acp_dma_count`, `union acp_i2stdm_mstrclkgen`, inline `acp_readl()`, `acp_writel()`, `acp_get_byte_count()`, and `acp5x_set_i2s_clk()`, plus external `snd_amd_acp_find_config()`.

## Control Flow
Inline helpers perform BAR-relative MMIO by subtracting `ACP5x_PHY_BASE_ADDRESS` from absolute register constants. `acp_get_byte_count()` selects HS or SP playback/capture linear position counters and returns a 64-bit union view. `acp5x_set_i2s_clk()` selects the master clock generator register based on stream instance and writes bitfields for master mode, format mode, BCLK divider, and LRCLK divider.

## State And Persistence Behavior
The structures define persistent per-device and per-stream state used across hw_params, trigger, pointer, and resume. Constants define fixed memory windows for SP/HS playback/capture, PTE offsets, FIFO offsets, DMA sizes, and ALSA buffer limits.

## Dependencies And Integration Points
It includes `vg_chip_offset_byte.h` for register offsets and `<sound/pcm.h>` for stream direction constants. All Vangogh sources include this header. The machine-config declaration connects the PCI parent to global AMD ACP stack selection.

## Risks And Edge Cases
`union acp_i2stdm_mstrclkgen mclkgen` in `acp5x_set_i2s_clk()` is not explicitly zero-initialized before bitfield assignment, so reserved bits may contain stack data unless the compiler clears it by chance; this is a register-programming risk. The helper subtraction requires all accesses to use `acp_readl()`/`acp_writel()` rather than raw `readl(base + absolute_offset)`. DAI rates and divider tables are not perfectly aligned.

## Test Signals
Build all Vangogh sources, trace master clock register values for reserved-bit cleanliness, validate byte-count reads over counter wrap, and verify each SP/HS memory window and PTE offset with DMA playback/capture tests.
