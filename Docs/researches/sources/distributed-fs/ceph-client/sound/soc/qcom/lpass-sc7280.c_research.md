# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-sc7280.c

## Purpose
`lpass-sc7280.c` is the SC7280 LPASS CPU DAI variant driver. It extends the SC7180-style MI2S/DP support with codec DMA RX, codec DMA TX, and voice-assist DMA capture DAIs, and supplies the register field layout and channel allocation policy needed by the shared LPASS platform component.

## Important APIs, types, and functions
`sc7280_lpass_cpu_dai_driver[]` defines Primary and Secondary MI2S, DP playback, CDC DMA RX playback, CDC DMA TX capture, and CDC DMA VA capture DAIs. CDC DMA DAIs use `asoc_qcom_lpass_cdc_dma_dai_ops`; MI2S and HDMI use the common LPASS CPU/HDMI ops.

`sc7280_lpass_alloc_dma_channel()` dispatches by DAI family: regular MI2S uses `dma_ch_bit_map`, DP uses `hdmi_dma_ch_bit_map`, RXTX CDC uses `rxtx_dma_ch_bit_map`, and VA CDC uses `va_dma_ch_bit_map`. Playback searches from zero for RDMA channels; capture searches from the family-specific WRDMA start. `sc7280_lpass_free_dma_channel()` clears the matching bitmap. Clock initialization and PM mirror SC7180 but with a one-clock `clk_name` array.

The `sc7280_data` variant table defines regular, HDMI, RXTX, and VA IRQ/DMA bases, channel starts/counts, regmap fields for regular and CDC DMA control and codec-interface registers, HDMI metadata/control fields, DAI clock names, and callback pointers.

## Control flow
The platform driver matches `qcom,sc7280-lpass-cpu` and delegates probe/remove/shutdown to common LPASS CPU helpers. During stream open, the shared platform code calls the SC7280 allocator, stores substreams in the right IRQ array, and chooses the correct hardware constraints. During prepare/trigger/IRQ, `lpass-platform.c` uses SC7280's variant fields to program regular, HDMI, RXTX, or VA regmaps.

## State and persistence behavior
SC7280-specific state is held in `struct lpass_data`: clock handles, DMA bitmaps, low-power codec DMA buffer physical addresses, regmaps, and active substream arrays. No disk state is written. PM callbacks gate the variant clocks; component suspend/resume handles regmap cache state.

## Dependencies and integration points
The file depends on SC7180 LPASS DT binding constants for shared IDs, common LPASS infrastructure, codec DMA DAI ops, HDMI DAI ops, and Linux bulk clock/PM APIs. It integrates with `lpass-platform.c` more deeply than SC7180 because codec DMA paths require `rxtx_lpaif_map`, `va_lpaif_map`, codec DMA memory buffers, and CDC DMA IRQ handlers.

## Risks and test signals
One visible risk is that RX CDC DMA allocation finds a free bit but does not call `set_bit()` in the RX case, while free clears the RXTX bitmap for both RX and TX. That can permit duplicate RX channel allocation if multiple RX CDC streams are opened. Other risks include shared register bases between regular and RXTX fields, channel-start arithmetic for WRDMA families, and missing DT memory resources for codec DMA. Tests should include simultaneous CDC RX streams to detect duplicate allocation, WCD playback/capture, DMIC VA capture, DP playback, PM suspend/resume, and IRQ delivery on RXTX/VA maps.
