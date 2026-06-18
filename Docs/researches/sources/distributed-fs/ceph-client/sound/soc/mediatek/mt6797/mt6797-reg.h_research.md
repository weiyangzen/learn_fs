# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-reg.h

## Purpose

This large register header maps the MT6797 AFE register space and bitfields for top clocks, memifs, ADDA, IRQs, connection matrices, ASRC, PCM modem interfaces, gains, and debug/monitor registers.

## Important APIs, Types, and Functions

It defines register offsets from `AUDIO_TOP_CON0` through `AFE_CBIP_SLV_DECODER_MON0`, `AFE_MAX_REGISTER`, `AFE_IRQ_STATUS_BITS`, and detailed `_SFT`, `_MASK`, and `_MASK_SFT` macros for fields consumed by platform, ADDA, PCM, and runtime PM code.

## Control Flow

No executable flow. The macros are used in regmap configuration, runtime resume/suspend, IRQ clear/status handling, memif setup, ADDA source programming, DAPM supplies, and PCM interface setup.

## State and Persistence Behavior

The file describes persistent hardware state. Some state is reprogrammed on runtime resume, while stream-specific fields remain active during a stream. Monitor/status registers are read by runtime or debug paths and should not be cached as normal state.

## Dependencies and Integration Points

Included by MT6797 platform and DAI files. It must remain consistent with `memif_data[]`, `irq_data[]`, DAPM controls, and the MMIO resource size.

## Risks and Edge Cases

Mask/shift errors are high impact because many fields are programmed through generic helpers. The header includes IRQ5 fields even the driver uses IRQ1/2/3/4/7. Sparse connection and ASRC registers make contiguous assumptions unsafe. Runtime PM relies on retention and AFE-on bits matching hardware.

## Test Signals

Compile coverage, regmap traces for memif/IRQ/ADDA/PCM writes, IRQ period tests, and comparison to the vendor register map are the strongest checks.
