# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-apq8016.c

Purpose: supplies APQ8016-specific LPASS CPU DAI definitions, register layout, clock initialization, and DMA channel allocation hooks for the generic LPASS CPU/platform code.

Important APIs/types/functions: defines `apq8016_lpass_cpu_dai_driver[]`, `apq8016_lpass_alloc_dma_channel`, `apq8016_lpass_free_dma_channel`, `apq8016_lpass_init`, `apq8016_lpass_exit`, and `apq8016_data` as `struct lpass_variant`.

Control flow: platform driver matches APQ8016 compatibles and delegates probe/remove to generic LPASS CPU functions. Variant init bulk-gets/enables PCNOC clocks, gets `ahbix-clk`, sets its rate, and enables it. DMA allocation chooses RDMA channels for playback and WRDMA channels for capture using a bitmap.

State and persistence: variant data is static. Runtime clock handles, clock bulk arrays, and DMA bitmap are stored in generic `struct lpass_data`.

Dependencies and integration: depends on APQ8016 LPASS dt-bindings, `lpass.h`, register macros, generic `asoc_qcom_lpass_cpu_platform_probe`, and LPASS platform PCM registration.

Risks: DAI names include historical spelling `"Quatenary"`, which may be ABI-visible. Bitmap allocation must match RDMA/WRDMA channel ranges. Clock enable errors must unwind bulk clocks correctly.

Test signals: APQ8016 LPASS probe, all four MI2S DAIs, playback/capture DMA allocation exhaustion, clock rate setup for `ahbix-clk`, and remove/shutdown clock disable.
