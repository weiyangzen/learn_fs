# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-ipq806x.c

## Purpose
`lpass-ipq806x.c` is the IPQ806x-specific LPASS CPU DAI platform driver. It supplies the single MI2S DAI definition, IPQ806x register layout, clock bring-up/tear-down, and a simple DMA channel policy to the shared LPASS CPU/platform infrastructure.

## Important APIs, types, and functions
The file defines local enums for IPQ806x I2S ports and DMA channels, then declares `ipq806x_lpass_cpu_dai_driver` with playback-only capability for `IPQ806X_LPAIF_I2S_PORT_MI2S`. Playback supports S16/S24/S32, 8 kHz through 96 kHz selected rates, and 1 to 8 channels.

`ipq806x_lpass_init()` retrieves `ahbix-clk`, sets it to `LPASS_AHBIX_CLOCK_FREQUENCY`, and enables it. `ipq806x_lpass_exit()` disables that clock. `ipq806x_lpass_alloc_dma_channel()` returns the fixed MI2S RDMA channel for playback and rejects capture with `-EINVAL`; `ipq806x_lpass_free_dma_channel()` is a no-op because the allocation is static.

The `ipq806x_data` `struct lpass_variant` is the main integration object. It provides I2S, IRQ, RDMA, WRDMA base offsets/strides, `REG_FIELD_ID` definitions for I2SCTL/RDMA/WRDMA bitfields, DAI clock names, and callbacks consumed by `asoc_qcom_lpass_cpu_platform_probe()` and `asoc_qcom_lpass_platform_register()`.

## Control flow
The platform driver matches `qcom,lpass-cpu`, then delegates probe/remove to the common LPASS CPU platform helpers. During common probe, the variant `init` callback enables the bus clock, the DAI table is registered, and the shared platform component later programs DMA registers according to the variant fields. PCM open asks the variant for a DMA channel; IPQ806x always maps playback to `IPQ806X_LPAIF_RDMA_CHAN_MI2S`.

## State and persistence behavior
Runtime state is minimal and held in common `struct lpass_data`: the `ahbix_clk` pointer and shared DMA/substream arrays. There is no persistent storage. Hardware state is reset/managed through LPASS registers and clock enable state.

## Dependencies and integration points
This file depends on the common LPASS CPU and platform code declared in `lpass.h`, register macros from `lpass-lpaif-reg.h`, Linux clock APIs, platform driver matching, and ASoC DAI registration. It is the IPQ806x provider of `struct lpass_variant`.

## Risks and test signals
The capture path is intentionally unsupported despite WRDMA register fields being present; attempts should fail cleanly. Clock failures abort probe, so board DT clock names must match exactly. Test signals include successful probe with `ahbix-clk`, MI2S playback, expected `-EINVAL` on capture, and period IRQs from the fixed RDMA channel.
