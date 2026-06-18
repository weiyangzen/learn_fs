# sources/distributed-fs/ceph-client/sound/soc/amd/raven/acp3x.h

## Purpose
This header provides Raven ACP3x register constants, memory-window layout, buffer limits, data structures, and inline MMIO/position helpers for the Raven PCI, I2S DAI, and PCM DMA drivers.

## Important APIs, Types, And Functions
It defines instance constants `I2S_SP_INSTANCE` and `I2S_BT_INSTANCE`, platform/device structures `struct acp3x_platform_info`, `struct i2s_dev_data`, and `struct i2s_stream_instance`, MMIO helpers `rv_readl()` and `rv_writel()`, and position helper `acp_get_byte_count()`.

## Control Flow
There is no standalone control flow, but the macros drive all register programming in the C files. `rv_readl()` and `rv_writel()` subtract `ACP3x_PHY_BASE_ADDRESS` because the included register header uses absolute offsets while drivers add offsets to an ioremapped BAR base.

## State And Persistence Behavior
The structures declared here define persistent runtime state for Raven: card-selected I2S instances, per-device TDM and active substream pointers, and per-stream DMA/position metadata. Buffer constants fix min/max ALSA buffer sizes to hardware-supported periods and period sizes.

## Dependencies And Integration Points
The header includes `chip_offset_byte.h` and `<sound/pcm.h>`, and is included by all Raven driver sources. `snd_amd_acp_find_config()` is not declared here because Raven's PCI driver does not use the shared machine-config helper.

## Risks And Edge Cases
`acp_get_byte_count()` combines high and low linear position registers with bitwise OR rather than shifting the high register by 32 bits; this risks wrong positions once the low counter wraps. The read/write helpers depend on absolute register definitions matching the fixed physical base. Any future BAR layout change would require revisiting the subtraction logic.

## Test Signals
Compile all Raven sources with this header, verify MMIO accesses target the intended BAR offsets, and test PCM pointer wrap over long-running streams. Static analysis should flag structure ownership and high/low counter composition issues.
