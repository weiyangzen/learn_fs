# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-ic-csc.c

## Purpose
Provides color-space conversion coefficient selection and calculation for the IPUv3 Image Converter. It maps input/output encoding, quantization, and color space to hardware CSC coefficients.

## Important APIs, Types, and Functions
The file is mostly static coefficient tables for identity, RGB full/limited, YUV full/limited, BT.601, and BT.709 conversions. `calc_csc_coeffs()` selects a parameter table and stores coefficients into `struct ipu_ic_csc`. Exported APIs are `__ipu_ic_calc_csc()` for prefilled CSC descriptors and `ipu_ic_calc_csc()` for callers providing V4L2 encodings, quantization, and IPU color spaces.

## Control Flow
Callers set or pass source/destination encoding and quantization. `ipu_ic_calc_csc()` fills the CSC descriptor and delegates to `__ipu_ic_calc_csc()`, which validates the combination and calls `calc_csc_coeffs()`. The resulting descriptor is consumed by `ipu-ic.c` when programming task parameter memory.

## State and Persistence
There is no mutable global state. Coefficient tables are static read-only data; calculated coefficients live in caller-owned `struct ipu_ic_csc`.

## Dependencies and Integration Points
Depends on IPU private color-space definitions, V4L2 ycbcr/quantization enums passed from image conversion and other IC users, and `ipu-ic.c` CSC programming. Kconfig-selected `BITREVERSE` is used elsewhere when these coefficients are packed into hardware.

## Risks
Colorimetry combinations outside the table return errors. Limited/full-range mapping is subtle and can cause washed-out or crushed output if caller metadata is wrong. Future color spaces or encodings require explicit table additions rather than automatic derivation.

## Test Signals
Unit-style tests should cover every RGB/YUV, full/limited, BT.601/BT.709 matrix path and invalid combinations. Hardware validation can compare converted color bars or image CRCs against software conversion references.
