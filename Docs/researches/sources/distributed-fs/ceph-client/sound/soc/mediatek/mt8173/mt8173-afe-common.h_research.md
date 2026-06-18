# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-afe-common.h

## Purpose

This header defines shared MT8173 AFE IDs for memory interfaces, IO DAIs, IRQs, and clocks.

## Important APIs, Types, and Functions

Memif enum includes DL1, DL2, VUL, DAI, AWB, MOD_DAI, and HDMI, followed by IO IDs for modem PCM, PMIC, I2S, second I2S, hardware gains, merge out/in, DAIBT, and HDMI. IRQ enum gives one IRQ per memif-like stream. Clock enum lists infra/top audio gates, I2S master clocks, I2S3 bit clock, and BCK0/BCK1. There are no function declarations.

## Control Flow

No executable flow. `mt8173-afe-pcm.c` uses these enum values as DAI IDs, memif array indexes, IRQ array indexes, and clock-array indexes.

## State and Persistence Behavior

The header defines IDs only. Actual clock handles and AFE private state are in `mt8173-afe-pcm.c`.

## Dependencies and Integration Points

Includes CCF and regmap headers because the platform file's common structures need those types. Machine drivers depend indirectly on the DAI ID/name mapping created from these IDs.

## Risks and Edge Cases

Enum ordering is critical: changing memif order changes array indexes and IO DAI numeric IDs. `MT8173_AFE_IRQ_MOD_DAI` exists, but the platform file's IRQ data table line for MOD_DAI uses `MT8173_AFE_IRQ_DAI`, so maintainers should verify whether that is intentional hardware sharing or a bug.

## Test Signals

Build MT8173 platform and run stream tests for each memif/IRQ path, especially DAI vs MOD_DAI and HDMI, to validate ID alignment.
