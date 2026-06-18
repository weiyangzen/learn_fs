# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-hevc-common.h

## Purpose
This header defines shared HEVC hardware-table structures and helper prototypes for Rockchip RKVDEC-family HEVC decoder backends.

## Important APIs, Types, And Data
- `struct rkvdec_rps_refs` describes one packed long-term RPS reference.
- `struct rkvdec_rps_short_term_ref_set` stores up to 15 delta POCs and used flags in hardware bitfield layout.
- `struct rkvdec_rps` combines long-term references and up to 64 short-term reference sets.
- `struct rkvdec_hevc_run` extends `struct rkvdec_run` with HEVC slice, decode, SPS, PPS, scaling, extended RPS controls, and `num_slices`.
- `struct scaling_factor` defines the hardware scaling-list layout.

## Control Flow
Backends include this header, allocate private tables containing `struct scaling_factor` and sometimes `struct rkvdec_rps`, populate a per-frame `rkvdec_hevc_run`, then call helpers before register programming.

## State And Persistence
`rkvdec_hevc_run` is per decode submission. `scaling_factor` and `rkvdec_rps` usually persist in coherent per-context private tables and are updated when controls change.

## Dependencies And Integration Points
The header depends on Linux integer types, V4L2 mem2mem types, and `rkvdec.h`. It is shared by the base HEVC backend and VDPU381/VDPU383 HEVC variants.

## Risks
- Packed bitfields encode a hardware ABI; field-width or ordering changes can silently break decoding.
- Raw V4L2 control pointers require valid controls before helper invocation.
- `struct scaling_factor` sizes and comments are hardware-specific and must remain aligned with backend private-table offsets.

## Test Signals
Build coverage across all HEVC backends catches prototype drift. Runtime coverage should include tile, scaling-list, RPS, reference-buffer, and bit-depth combinations on each backend variant.
