# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-sc7180.c

## Purpose
`lpass-sc7180.c` provides the SC7180-specific LPASS CPU DAI driver and variant data. It describes the available Primary MI2S, Secondary MI2S, and HDMI/DP playback DAI interfaces, SC7180 register offsets/fields, clock list, PM callbacks, and DMA channel allocation policy.

## Important APIs, types, and functions
`sc7180_lpass_cpu_dai_driver[]` defines three DAIs: Primary MI2S with playback and capture, Secondary MI2S playback, and `LPASS_DP_RX` HDMI playback. The DAI ops are shared LPASS CPU ops or HDMI ops declared in `lpass.h`/`lpass-hdmi.h`.

`sc7180_lpass_alloc_dma_channel()` allocates from either `hdmi_dma_ch_bit_map` for DP playback or `dma_ch_bit_map` for regular RDMA/WRDMA, using `find_first_zero_bit()` for playback and `find_next_zero_bit()` from `wrdma_channel_start` for capture. `sc7180_lpass_free_dma_channel()` clears the corresponding bit. `sc7180_lpass_init()` bulk-gets and enables the variant clock list; `exit`, suspend, and resume disable or re-enable the bulk clocks.

The `sc7180_data` variant table provides register bases/strides, channel counts, I2S and DMA reg fields, HDMI/DP control field addresses, clock names, DAI clock names, and the callback pointers consumed by the common LPASS driver.

## Control flow
On platform match `qcom,sc7180-lpass-cpu`, common LPASS probe receives `sc7180_data`. Initialization allocates `drvdata->clks`, populates IDs from `clk_name`, then enables all clocks. Common PCM open calls the SC7180 allocator to reserve DMA channel bits. Common platform callbacks then use SC7180 register field metadata to program DMA and HDMI blocks. PM suspend/resume gates only the variant clock bulk; regmap cache handling is done in `lpass-platform.c`.

## State and persistence behavior
Runtime state consists of clock handles and DMA channel bitmaps in `struct lpass_data`. No persistent storage is used. The SoC table is static const data. Hardware register state is held by LPASS blocks and regmap caches.

## Dependencies and integration points
The file depends on SC7180 sound DT bindings, common LPASS CPU/platform helpers, HDMI DAI ops, Linux PM macros, bulk clock APIs, and `lpass-lpaif-reg.h` register macros. It is tightly integrated with `lpass-platform.c`, which expects `hdmi_port_enable` and `hdmiif_map` setup from the common CPU probe path when a DP DAI is present.

## Risks and test signals
Risks include mismatched DT clock names, incomplete HDMI field definitions, and DMA bitmap leaks if open/close error paths in shared code mis-handle SC7180 channels. Useful tests include Primary MI2S playback/capture, Secondary playback, DP playback, concurrent stream channel exhaustion returning `-EBUSY`, and system sleep/resume with audio clocks restored.
