# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-lpaif-reg.h

## Purpose
`lpass-lpaif-reg.h` is the central register-address and bit-value macro header for LPASS Low Power Audio Interface register programming. It abstracts I2S control, IRQ registers, regular RDMA/WRDMA, HDMI RDMA, and CDC DMA register address selection across SoC variants.

## Important APIs and constants
The I2S section defines `LPAIF_I2SCTL_REG(v, port)` and values for loopback, speaker/mic enable, SD-line modes, mono/stereo, word-select source, and bit width. The IRQ section defines host-port IRQ registers and bit encodings: `LPAIF_IRQ_PER(chan)`, `LPAIF_IRQ_XRUN(chan)`, `LPAIF_IRQ_ERR(chan)`, `LPAIF_IRQ_ALL(chan)`, plus HDMI-specific preload/metadone/deep-audio bits.

The DMA section exposes address macros for HDMI RDMA, classic RDMA, WRDMA, and CDC DMA. The high-level macros `LPAIF_DMACTL_REG`, `LPAIF_DMABASE_REG`, `LPAIF_DMABUFF_REG`, `LPAIF_DMACURR_REG`, `LPAIF_DMAPER_REG`, and `LPAIF_DMAPERCNT_REG` choose the correct register family based on stream direction and `is_cdc_dma_port(dai_id)`. It also defines DMA control field values for burst, words-per-sample count, FIFO watermark, enable, and dynamic clock.

## Control flow and integration
The header has no executable flow, but it encodes a large amount of runtime branch behavior through macros. `lpass-platform.c` calls these macros while handling `hw_free`, `prepare`, `trigger`, `pointer`, and IRQ clear/enable paths. SoC variant files provide the base offsets, strides, and channel starts that these macros combine into final register addresses.

## State and persistence behavior
No state is stored here. The macros compute register offsets from immutable variant data and runtime PCM state such as channel, direction, and DAI ID. Persistent hardware state is in LPASS registers and may be cached by regmap during suspend.

## Dependencies and integration points
The macros assume `struct lpass_variant` fields from `lpass.h`, DAI IDs from Qualcomm sound DT bindings, and stream constants such as `SNDRV_PCM_STREAM_PLAYBACK`. They also depend on `is_cdc_dma_port()` and `is_rxtx_cdc_dma_port()` being visible via `lpass.h`.

## Risks and test signals
This header is high blast-radius because a bad macro affects all LPASS DMA paths. Risks include off-by-one channel-start handling for WRDMA/CDC WRDMA, incorrect CDC RXTX versus VA register family selection, and IRQ mask collisions if channel counts exceed the encoded bit stride. Tests should cover playback and capture on MI2S, HDMI/DP playback, CDC RX/TX/VA streams, pointer reporting, xrun/error IRQ handling, and suspend/resume regcache sync.
