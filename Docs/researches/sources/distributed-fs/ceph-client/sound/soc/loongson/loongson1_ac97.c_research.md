# sources/distributed-fs/ceph-client/sound/soc/loongson/loongson1_ac97.c

## Purpose
Implements the Loongson-1 AC97 controller driver, including AC97 bus operations, DMA setup, channel/sample-format programming, and suspend/resume handling.

## Important APIs, Types, And Functions
`struct ls1x_ac97` stores register base, regmap, mapped TX/RX DMA base addresses, and DAI DMA data. AC97 bus ops are `ls1x_ac97_reset()`, `write()`, `read()`, and `init()`. DAI ops are `ls1x_ac97_dai_probe()` and `ls1x_ac97_hw_params()`. Probe maps resources including named `audio-tx` and `audio-rx`, registers dmaengine PCM and the ASoC component, and installs global AC97 ops with `snd_soc_set_ac97_ops()`.

## Control Flow, State, And Persistence
The driver uses a file-scope `ls1x_ac97` pointer for AC97 bus callbacks. Reset and codec register access poll raw interrupt bits. Init programs output and input channel FIFO thresholds and VRA bits. `hw_params` modifies DMA address flags for mono/stereo and programs 8-bit or 16-bit sample width. Suspend clears DMA/channel enable bits and asserts resume; resume re-enables channels and waits for resume completion.

## Dependencies And Integration Points
Depends on DT compatible `loongson,ls1b-ac97`, regmap MMIO, Loongson1 APB DMA resources, ASoC AC97 codec support, and generic dmaengine PCM.

## Risks And Test Signals
Risks include the global singleton pointer limiting multiple instances, returning negative error codes as unsigned codec reads on timeout, DMA address flag packing into `addr`, missing `dma_unmap_resource()` cleanup, and poll-timeout behavior during BT/sleep-like low power states. Test signals include AC97 codec enumeration, register read/write timeout logs, mono/stereo 8/16-bit playback/capture, suspend/resume, and resource leak checks.
