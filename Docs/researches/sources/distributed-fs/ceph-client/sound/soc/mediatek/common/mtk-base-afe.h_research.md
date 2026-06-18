# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-base-afe.h

## Purpose
Defines the core MediaTek AFE data model shared by SoC platform drivers, FE DAI helpers, IRQ logic, memif programming, sub-DAI aggregation, and secure monitor operations.

## Important APIs, Types, And Functions
Defines `MTK_STREAM_NUM`, `MTK_SIP_AUDIO_CONTROL`, `enum mtk_audio_smc_call_op`, `struct mtk_base_memif_data`, `struct mtk_base_irq_data`, `struct mtk_base_afe`, `struct mtk_base_afe_memif`, `struct mtk_base_afe_irq`, and `struct mtk_base_afe_dai`.

## Control Flow, State, And Persistence
The header has no execution, but its structs are the persistent runtime state for MediaTek AFE devices. `mtk_base_afe` owns MMIO/regmap, runtime PM callbacks, register backup arrays, memif and IRQ arrays, sub-DAI lists, hardware constraints, rate conversion callbacks, DRAM resource callbacks, and private SoC data.

## Dependencies And Integration Points
Depends on MediaTek SIP service definitions and ASoC/PCM types through include order. It is consumed by common helpers and SoC-specific drivers that populate the register maps and callback tables.

## Risks And Test Signals
Risks include negative register sentinel handling being implicit, many SoC-populated fields without compile-time validation, callback nullability, and secure monitor operation enum drift. Test signals are per-SoC initialization audits, runtime PM suspend/resume, dynamic IRQ allocation, 64-bit DMA address fields, and static checks for uninitialized memif/IRQ fields.
