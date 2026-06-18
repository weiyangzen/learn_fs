# sources/distributed-fs/ceph-client/sound/aoa/codecs/onyx.h

## Purpose

This header defines PCM3052/Onyx register numbers and bit masks used by the Onyx codec driver.

## Important APIs, types, and functions

It defines registers for DAC attenuation, control, DAC control, deemphasis, filter, output phase, ADC control, ADC high-pass bypass, and digital info bytes. Bit definitions include reset, suspend, mute, S/PDIF enable, word length, input selection, gain mask, and channel status masks. `FIRSTREGISTER` anchors the cache index.

## Control Flow

There is no executable logic. The macros are consumed by `onyx.c`.

## State and Persistence

The macro layout determines the size and indexing of the Onyx register cache in `struct onyx`.

## Dependencies and Integration Points

It includes I2C and PowerMac low-I2C headers and is private to the Onyx driver.

## Risks and Test Signals

Risks include wrong register offsets corrupting cache writes, bit-mask mistakes for mute/SPDIF/status, and cache indexing outside the 65-80 range. Tests should validate register writes from mixer callbacks against expected addresses and masks.
