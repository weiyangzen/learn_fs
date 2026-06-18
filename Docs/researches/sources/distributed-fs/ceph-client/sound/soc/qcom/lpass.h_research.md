# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass.h

## Purpose
`lpass.h` is the shared private header for Qualcomm LPASS ASoC CPU/platform drivers. It defines constants, helper predicates, core state structures, the SoC variant contract, PCM private data, and declarations for the common probe/remove/shutdown, CPU DAI ops, CDC DMA DAI ops, and platform registration entry point.

## Important APIs, types, and functions
`is_cdc_dma_port()` and `is_rxtx_cdc_dma_port()` classify DAI IDs into codec-DMA families. `struct lpaif_i2sctl` and `struct lpaif_dmactl` hold regmap-field pointers for I2S and DMA control registers.

`struct lpass_data` is the central runtime state for the LPASS device: clocks, MI2S SD-line modes, HDMI/codec-DMA enable flags, MMIO bases, regmaps, IRQ numbers, variant pointer, DMA allocation bitmaps, active substream arrays, regmap-field bundles, HDMI field bundles, and codec-DMA low-power memory addresses. `struct lpass_variant` is the SoC-specific contract containing register bases/strides/counts, every reg field used by common code, channel-start offsets, callbacks, DAI tables, and clock lists. `struct lpass_pcm_data` stores per-substream DMA channel and I2S port.

## Control flow and integration
The header does not execute code except inline DAI classifiers. It defines the data contract between SoC files (`lpass-ipq806x.c`, `lpass-sc7180.c`, `lpass-sc7280.c`), common CPU code (not in this work item), common HDMI/CDC DAI ops, and `lpass-platform.c`. SoC probes provide a `struct lpass_variant`; common code fills `struct lpass_data`; platform callbacks consume both.

## State and persistence behavior
All LPASS runtime state is in `struct lpass_data` and per-stream `struct lpass_pcm_data`. The fields are kernel-memory state only and are destroyed with the platform device. Register persistence across PM uses regmap cache behavior in the platform component, not storage declared here.

## Dependencies and integration points
The header includes Linux clock/platform/regmap APIs, Qualcomm sound DT bindings, Q6AFE binding IDs, `common.h`, and HDMI definitions. It is included by most LPASS source files and is therefore sensitive to type changes.

## Risks and test signals
Risks include ABI-like coupling: adding or changing `struct lpass_variant` fields requires all variants and common code to stay aligned. The DMA substream array sizes also need to match channel counts used by variants. Tests should cover all variant probes, all DAI ID classifiers, regular/HDMI/CDC stream open/close, and build coverage for all enabled LPASS SoC drivers.
