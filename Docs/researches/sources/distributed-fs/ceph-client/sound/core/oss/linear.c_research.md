# sources/distributed-fs/ceph-client/sound/core/oss/linear.c

## Purpose
`linear.c` implements an OSS PCM plugin for converting between linear PCM sample formats while preserving rate and channel count. It handles sample width, endian conversion, and signedness conversion.

## Important APIs, Types, and Functions
`struct linear_priv` stores conversion offsets, copy sizes, endian-conversion flag, destination byte count, and signedness flip mask. `init_data()` derives these fields from source and destination formats. `do_convert()` converts one sample through a temporary 32-bit container. `linear_transfer()` validates areas, clamps frames to destination availability, and calls `convert()`. `snd_pcm_plugin_build_linear()` validates linear formats and installs the transfer callback.

## Control Flow and State
Transfer walks channels and frames. Disabled source channels silence wanted destinations and clear destination enabled state. Enabled channels compute byte pointers from area first/step fields and convert each frame by copying significant bytes into a temporary value, optionally swapping endian, XORing the sign bit when signedness differs, and copying the requested destination bytes out at the destination offset.

## Dependencies and Integration Points
It depends on PCM format helpers for width, physical width, endian, signedness, and linear-format checks, plus OSS plugin chain infrastructure.

## Risks and Test Signals
Risks are subtle offset mistakes for packed versus physical sample widths, endian/sign conversion ordering, and frame clamping. Tests should convert among 8/16/24/32-bit signed and unsigned formats, little and big endian variants, disabled channels, odd area steps, and zero/overlarge frame counts.
