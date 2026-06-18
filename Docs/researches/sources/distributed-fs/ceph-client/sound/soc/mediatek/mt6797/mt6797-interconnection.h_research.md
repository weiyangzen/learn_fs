# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-interconnection.h

## Purpose

This header defines MT6797 AFE interconnection input indices used by DAPM mixer controls to program `AFE_CONN*` matrix bits.

## Important APIs, Types, and Functions

It assigns symbolic IDs for I2S, ADDA UL, DL1-DL3, PCM capture, gain outputs, and I2S2 channels. There are no functions or structs.

## Control Flow

No executable flow. The constants are embedded in `SOC_DAPM_SINGLE_AUTODISABLE()` controls across ADDA, PCM, and memif routes.

## State and Persistence Behavior

The header defines the bit positions for persistent connection-matrix register state. DAPM manages the actual register bits as widgets/routes activate.

## Dependencies and Integration Points

Included by MT6797 platform and DAI files. It must match the hardware connection matrix and `mt6797-reg.h` connection register offsets.

## Risks and Edge Cases

A wrong index routes audio to the wrong source or channel. The numbering is sparse and not self-validating, so generated-style updates need hardware-map verification.

## Test Signals

DAPM route tests and regmap traces should confirm intended bits are toggled for ADDA, PCM, hostless, and memif capture routes.
