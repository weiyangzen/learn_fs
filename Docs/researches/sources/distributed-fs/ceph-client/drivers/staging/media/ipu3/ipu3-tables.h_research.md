# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-tables.h

## Purpose

This header declares static tuning tables and default image-processing configuration used by the IPU3 CSS parameter code. It is a compile-time contract between `ipu3-tables.c`, `ipu3-css-params.c`, and the UAPI/ABI structures that are copied into firmware parameter buffers.

## Important APIs, Types, and Functions

Key constants describe scaler and lookup dimensions: `IMGU_BDS_CONFIG_LEN`, `IMGU_SCALER_DOWNSCALE_4TAPS_LEN`, `IMGU_SCALER_DOWNSCALE_2TAPS_LEN`, `IMGU_GDC_LUT_LEN`, and `IMGU_XNR3_VMEM_LUT_LEN`. `struct imgu_css_bds_config` holds horizontal/vertical phase arrays, pattern array, sample length, and enable flags for bayer-domain scaling. `struct imgu_css_xnr3_vmem_defaults` carries XNR3 LUT vectors. Externs expose BDS configs, scaler taps, GDC LUTs, XNR3 defaults, and default blocks for BNR, demosaic, CCM, gamma, CSC, CDS, shading, IEFD, YDS, CHNR, edge/noise reduction, TCC, ANR, AWB, AE, AF, and related UAPI objects.

## Control Flow

There is no runtime control flow. The declared tables are selected and copied by the CSS parameter/configuration path when formats, rectangles, and processing parameters are prepared.

## State and Persistence Behavior

The file owns no mutable state. Its extern data is read-only driver state compiled into the module and persists for module lifetime.

## Dependencies and Integration Points

It includes `ipu3-abi.h` and depends on `linux/bitops.h` for `BIT()`. Its declarations are consumed by IPU3 CSS format/parameter setup and must match IPU3 UAPI and firmware ABI layout.

## Risks and Edge Cases

Array length, fixed-point, or default structure drift can break firmware programming without compiler errors if the consumer assumes a different table shape. The BDS granularity and scaler tap constants are hardware-facing.

## Test Signals

Useful signals are IPU3 module build coverage, format negotiation that exercises BDS/GDC/scaler paths, parameter-buffer ABI size checks, and image-quality regressions on raw-to-NV12 capture using default parameter sets.
