# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-reg.h

## Purpose

This header defines MT2701 AFE register offsets and bit masks used by the platform, clock, I2S, DLM, IRQ, and BT merge paths.

## Important APIs, Types, and Functions

It maps top control registers, I2S input/output controls, connection matrix registers, ASYS IRQ registers, DAC/memif controls, DL/UL buffer base/current registers, BT DAI registers, ASRC init values, DLM packet buffer fields, and I2S control fields such as FS, reset, enable, one-heart mode, I2S mode, word length, and input phase fix.

## Control Flow

There is no executable control flow. Constants are consumed by `regmap_update_bits()` and `regmap_write()` in the PCM and clock-control files.

## State and Persistence Behavior

The header describes hardware state layout. Runtime PM and common suspend/resume code use these offsets to save/restore selected registers and reinitialize clocks/ASRC.

## Dependencies and Integration Points

It is included by `mt2701-afe-common.h` and therefore reaches the PCM and clock layers. The values must match the SoC register map and the parent syscon range.

## Risks and Edge Cases

Bitfield mistakes directly corrupt audio routing, clocking, IRQ clear, or memif enable behavior. Some connection registers are sparse (`AFE_CONN41`), so code must not assume contiguous matrix offsets. DLM channel macros do not range-check channel values.

## Test Signals

Regmap traces during playback/capture/BT/runtime PM should show writes to expected offsets. DAPM route toggles validate connection matrix bits, while IRQ tests validate `ASYS_IRQ_*` offsets and clear bits.
