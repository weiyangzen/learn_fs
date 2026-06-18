# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-audsys-clkid.h

## Purpose

This header defines numeric IDs for the MT8186 audsys gate-clock table.

## Important APIs, Types, and Data

The enum starts at `CLK_AUD_AFE` and lists gate IDs for AFE, 22/24 MHz APLL outputs, APLL tuners, TDM, ADC/DAC, DAC pre-distortion, TML, NLE, I2S1-4 BCLKs, connsys/general ASRC gates, hi-res ADC/DAC gates, ADDA6 gates, third DAC gates, ETDM input/output BCLKs, and terminates with `CLK_AUD_NR_CLK`.

## Control Flow and State

No runtime flow or data exists. The enum values index `aud_clks[]` and `afe_priv->lookup[]` in `mt8186-audsys-clk.c`.

## Dependencies and Integration Points

The IDs are consumed by audsys gate registration and must remain aligned with `CLK_AUD_NR_CLK` sizing. Names produced from these IDs are later consumed by `mt8186-afe-clk.c` through CCF lookup.

## Risks

Changing enum order or inserting IDs without updating the gate table can mismatch names, bits, and cleanup entries. The enum declaration style lacks a space after `enum`, which is harmless but nonstandard.

## Test Signals

Build catches missing IDs; runtime clock debug and full AFE probe catch table-size and gate-name mismatches.
