# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-tables.c lines 8066-9609

## Scope

This chunk covers the final part of Intel IPU3 CSS static table definitions in `ipu3-tables.c`. The range starts inside the Bayer Down Scaler (`imgu_css_bds_configs`) entry for scale factor `32 / (32 + 86)` and continues through the final BDS entries for scale factors `32 / (32 + 87)` through `32 / (32 + 96)`. It then defines the exported default tables used by the IPU3 CSS parameter builder:

- Output-system scaler FIR kernels: `imgu_css_downscale_4taps` and `imgu_css_downscale_2taps`.
- Geometric Distortion Correction LUT: `imgu_css_gdc_lut`.
- XNR3 vector-memory defaults: `imgu_css_xnr3_vmem_defaults`.
- Accelerator-cluster defaults for BNR, demosaic, CCM, gamma, CSC, CDS, shading, IEFD, YDS, CHNR, Y edge enhancement/noise reduction, TCC LUTs, ANR, AWB filter response, AE, AE CCM, AF, and AWB.

The chunk contains constant data only. There are no functions, dynamic allocations, locks, or direct control-flow statements in this source range.

## Purpose

`ipu3-tables.c` is the static tuning and hardware-default table file for the IPU3 image-processing pipeline. The data in this chunk gives the driver known-good initial values for fixed-function ISP blocks when userspace has not provided a corresponding `ipu3_uapi_*` parameter section and no previous parameter set is available.

The BDS entries provide precomputed phase arrays and sample patterns for the strongest predefined Bayer downscale ratios in the table. With `IMGU_BDS_GRANULARITY` set to 32 and `IMGU_BDS_CONFIG_LEN` set to 97, `imgu_css_bds_configs[n]` represents scale factor `32 / (32 + n)`. This chunk therefore covers BDS indexes 86 through 96, equivalent to inverse scale values 118 through 128 and output scale factors about 0.271 down to 0.25. These entries are selected later from the effective input height and requested BDS output height.

The remaining constants are defaults for OSYS scaling, geometric correction, XNR/ANR denoise behavior, color correction and conversion, gamma, chroma and luma denoise, statistics grids, and 3A setup. They let the driver synthesize a complete ACC parameter block even when userspace only supplies a subset of tuning controls.

## Important APIs, Types, and Data

The declarations are exported through `ipu3-tables.h`, which defines the local table shapes and constants:

- `struct imgu_css_bds_config` contains horizontal and vertical BDS phase arrays, a shared BDS pattern array, sample-pattern length, and horizontal/vertical downscale-enable bits.
- `IMGU_BDS_GRANULARITY`, `IMGU_BDS_MIN_SF_INV`, and `IMGU_BDS_CONFIG_LEN` define the BDS scale-index contract.
- `IMGU_SCALER_DOWNSCALE_4TAPS_LEN`, `IMGU_SCALER_DOWNSCALE_2TAPS_LEN`, and `IMGU_SCALER_FP` define the OSYS scaler kernel sizes and fixed-point scale where `BIT(31)` represents 1.0.
- `struct imgu_css_xnr3_vmem_defaults` holds 16-entry `x`, `a`, `b`, and `c` default curves for XNR3 vector memory.
- `IMGU_GDC_LUT_UNIT` and `IMGU_GDC_LUT_LEN` describe the 4 by 256 GDC LUT layout.

The BDS section uses `struct imgu_abi_bds_phase_arr` and `struct imgu_abi_bds_ptrn_arr` from `ipu3-abi.h`. Each BDS config has mirrored horizontal and vertical phase arrays with `.even` and `.odd` subarrays plus `.ptrn_arr`, `.sample_patrn_length`, `.hor_ds_en`, and `.ver_ds_en`.

The ACC defaults use UAPI and ABI structures from `include/uapi/intel-ipu3.h` and `ipu3-abi.h`, including:

- `struct ipu3_uapi_bnr_static_config` for Bayer noise reduction static settings.
- `struct ipu3_uapi_dm_config`, `ipu3_uapi_ccm_mat_config`, `ipu3_uapi_gamma_corr_lut`, `ipu3_uapi_csc_mat_config`, and `ipu3_uapi_cds_params` for demosaic and color pipeline defaults.
- `struct ipu3_uapi_shd_config_static` for lens shading grid and black-level defaults.
- `struct ipu3_uapi_yuvp1_iefd_config`, `ipu3_uapi_yuvp1_yds_config`, `ipu3_uapi_yuvp1_chnr_config`, and `ipu3_uapi_yuvp1_y_ee_nr_config` for YUVP1 enhancement, downscale, chroma denoise, and edge/noise behavior.
- `struct ipu3_uapi_yuvp2_tcc_gain_pcwl_lut_static_config` and `ipu3_uapi_yuvp2_tcc_r_sqr_lut_static_config` for total color correction LUT defaults.
- `struct imgu_abi_anr_config` for advanced noise reduction transform and stitch defaults.
- `struct ipu3_uapi_awb_fr_config_s`, `ipu3_uapi_ae_grid_config`, `ipu3_uapi_ae_ccm`, `ipu3_uapi_af_config_s`, and `ipu3_uapi_awb_config_s` for statistics and 3A defaults.

The macro `X` is defined earlier in the file as `0` and marks hardware fields documented as don't-care or reserved in many initializer rows.

## Control Flow and Use Sites

This chunk has no local control flow, but the constants are consumed by `ipu3-css-params.c` and `ipu3-css.c`.

OSYS scaler setup calls `imgu_css_scaler_setup_lut()` with `imgu_css_downscale_4taps` for luma and `imgu_css_downscale_2taps` for chroma. The scaler calculation retries with a small phase-step correction until the generated output dimensions meet the target and height-alignment constraints. These arrays therefore feed runtime coefficient generation rather than being copied verbatim as a whole hardware block.

ACC parameter construction follows a repeated user/old/default pattern. For each ACC section, `ipu3-css-params.c` first checks the `use->acc_*` flag to accept userspace values, otherwise preserves the old value if an old parameter block exists, otherwise copies the default from this file. Examples include `imgu_css_bnr_defaults`, `imgu_css_dm_defaults`, `imgu_css_ccm_defaults`, `imgu_css_gamma_lut`, `imgu_css_csc_defaults`, `imgu_css_cds_defaults`, `imgu_css_shd_defaults`, `imgu_css_iefd_defaults`, `imgu_css_yds_defaults`, `imgu_css_chnr_defaults`, `imgu_css_y_ee_nr_defaults`, the TCC LUTs, `imgu_css_anr_defaults`, `imgu_css_awb_fr_defaults`, `imgu_css_ae_grid_defaults`, `imgu_css_ae_ccm_defaults`, `imgu_css_af_defaults`, and `imgu_css_awb_defaults`.

The BDS config is selected with:

```c
bds_ds = effective_height * IMGU_BDS_GRANULARITY / bds_height;
cfg_bds = &imgu_css_bds_configs[bds_ds - IMGU_BDS_MIN_SF_INV];
```

The selected table entry is copied into horizontal and vertical BDS ABI fields, including sample pattern length, enable bits, pattern arrays, and phase arrays. The code then computes per-stripe BDS data and marks `acc->bds.enabled` from `hor_ds_en || ver_ds_en`.

The GDC LUT is programmed directly in `ipu3-css.c` during CSS initialization. The driver iterates over 256 entries, masks each of the four signed tables with `IMGU_GDC_LUT_MASK`, packs table pairs into two 32-bit writes, and writes them under `IMGU_REG_GDC_LUT_BASE`.

XNR3 VMEM setup in `ipu3-css-params.c` copies the 16-entry XNR defaults into the larger vector-memory parameter layout using modulo indexing. TNR3 VMEM is nearby but generated separately with sigma defaults.

## State and Persistence Behavior

The data in this chunk is immutable compiled-in driver state. It has static storage duration and is exported as `const`, so it is shared across devices and streams and should not be modified at runtime.

Persistent hardware or per-frame state is created only when consumers copy these defaults into parameter buffers or registers:

- ACC defaults become part of the per-pipe CSS parameter buffer sent to firmware/hardware. Later parameter submissions may preserve previous values through the `acc_old` path rather than copying these defaults again.
- BDS table data becomes per-frame/per-pipe BDS ABI state selected from current effective and BDS rectangle dimensions.
- GDC LUT values are written into hardware registers during CSS initialization and remain hardware state until reset or reprogramming.
- XNR3 VMEM defaults become vector-memory parameter data when the XNR3 VMEM section is built.

Several consumers add runtime-derived fields after copying defaults. BNR gets `column_size` from TNR frame width, demosaic gets `frame_width`, shading derives grid slice and operation data, ANR gets enable bits and frame dimensions and clamps `xreset`/`yreset`, AWB/AF/AE grids derive end coordinates and stripe-specific grids, and TCC defaults are combined with generated identity MACC and inverse-Y tables.

## Dependencies and Integration Points

This chunk depends on `ipu3-tables.h`, `ipu3-abi.h`, and the packed IPU3 UAPI structures in `include/uapi/intel-ipu3.h`. Correctness depends on those structures matching the firmware ABI and hardware register packing. Many fields are bitfields or fixed-width packed structures, so positional initializers must stay aligned with the exact UAPI layout.

Important integration points are:

- `ipu3-css-params.c`, which builds CSS/ACC parameter memory and selects between userspace, old, and default values.
- `ipu3-css.c`, which writes the GDC LUT into hardware registers.
- The V4L2 userspace parameter ABI, especially `struct ipu3_uapi_acc_param` and `struct ipu3_uapi_flags`, whose `acc_*`, `tnr3_*`, and `xnr3_*` flags determine whether defaults are used.
- IPU3 firmware/ABI structures under `ipu3-abi.h`, particularly BDS phase/pattern arrays and ANR structures.
- Pipeline rectangle calculation, stripe splitting, and statistics-grid helpers in `ipu3-css-params.c`, which adapt static defaults to frame geometry.

## Risks

- The BDS section begins mid-entry in this chunk. A complete review of the `32 / (32 + 86)` entry requires the preceding chunk; this chunk covers its tail and all later entries through index 96.
- BDS table indexing is geometry-derived. Any mismatch between `IMGU_BDS_CONFIG_LEN`, the number of initializers, and `bds_ds - IMGU_BDS_MIN_SF_INV` can produce invalid scale selection or `-EINVAL`.
- The BDS phase and pattern tables are dense hand/generated numeric data. Single-value drift can cause image-quality issues, aliasing, incorrect sample selection, or hardware-programming failures that are hard to diagnose from normal control-flow tests.
- The scaler kernels use signed fixed-point constants generated from floating-point expressions. Changes to `IMGU_SCALER_FP`, array length, tap count assumptions, or compiler conversion behavior would affect luma/chroma scaler coefficients.
- The GDC LUT is packed into hardware registers after masking signed 16-bit values. Incorrect LUT dimensions, sign handling, or mask width can distort geometric correction globally.
- Positional initializers for packed UAPI structures are fragile. Adding, removing, or reordering fields in `intel-ipu3.h` without converting these defaults to named initializers can silently assign values to the wrong hardware fields.
- Defaults are only a baseline. Runtime code must still fill frame-dependent fields such as BNR column size, DM frame width, SHD operations, ANR dimensions, and AE/AWB/AF stripe grids. Testing only the constants is not enough.
- Statistics grid defaults set fixed 16 by 16 regions and enable bits. Bad stripe splitting or grid end calculation around these defaults can disable the wrong stripe or produce invalid statistic memory layout.

## Test and Validation Signals

Useful validation signals for this chunk include:

- Build coverage for `drivers/staging/media/ipu3`, including `ipu3-tables.c`, `ipu3-css-params.c`, and `ipu3-css.c`, to catch structure-size and symbol mismatches.
- Static checks that `ARRAY_SIZE(imgu_css_bds_configs) == IMGU_BDS_CONFIG_LEN`, `ARRAY_SIZE(imgu_css_downscale_4taps) == IMGU_SCALER_DOWNSCALE_4TAPS_LEN`, `ARRAY_SIZE(imgu_css_downscale_2taps) == IMGU_SCALER_DOWNSCALE_2TAPS_LEN`, and the GDC LUT dimensions match `IMGU_GDC_LUT_UNIT` by `IMGU_GDC_LUT_LEN`.
- Pipeline tests that request BDS ratios near 0.271 and 0.25 so indexes 86 through 96 are selected and copied into ACC BDS fields.
- Image-quality or conformance tests for OSYS luma/chroma downscaling, especially dimensions that exercise the scaler phase-step correction loop.
- Hardware initialization tests that read back or observe GDC LUT programming and verify no CSS initialization error is reported.
- Parameter-submission tests for the user/old/default paths: submit no ACC parameters to force these defaults, submit partial `use->acc_*` flags to verify old/default preservation, and submit explicit userspace values to verify defaults are bypassed.
- 3A statistics tests for AWB filter response, AE, AF, and AWB grids across one-stripe and two-stripe layouts, checking grid enable bits, end coordinates, and height-per-slice derivation.
- Runtime image tests with gamma, CCM/CSC, BNR, ANR, CHNR, Y edge enhancement/noise reduction, and TCC defaults enabled to catch visible regressions from table corruption.
