# sources/distributed-fs/ceph-client/sound/aoa/codecs/tas.h

## Purpose

This header defines TAS3004 register addresses, bit fields, and DRC limits used by the TAS codec driver.

## Important APIs, types, and functions

It defines main control, DRC, volume, treble, bass, left/right mixer, analog control, main control 2, biquad/loudness registers, and `TAS3001_DRC_MAX`/`TAS3004_DRC_MAX`. Bit fields cover serial clock, sport mode, word length, mono/input selection, deemphasis, analog power down, and all-pass.

## Control Flow

There is no executable logic. Macros are consumed by `tas.c`.

## State and Persistence

The values determine TAS register programming and cached `acr` semantics.

## Dependencies and Integration Points

It is private to the TAS driver and included by `tas.c`.

## Risks and Test Signals

Risks include wrong bit shifts or register constants causing hardware misconfiguration. Tests should validate reset-init register writes and ALSA control writes against expected register/value pairs.
