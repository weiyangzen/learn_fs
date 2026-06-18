<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_drv.h

## Purpose

This header is the central register and private-state contract for the FSL DCU DRM driver. It defines DCU global register offsets, interrupt bits, timing/background/threshold fields, layer descriptor address calculations and bit encodings, supported DCU pixel format IDs, LS1021A SCFG pixel-clock control bits, SoC layer layout constants, and the private device structures consumed by the driver, KMS, output, and plane files.

## Important APIs, Types, And Macros

Important register macros cover `DCU_DCU_MODE`, `DCU_BGND`, `DCU_DISP_SIZE`, `DCU_HSYN_PARA`, `DCU_VSYN_PARA`, `DCU_SYN_POL`, `DCU_THRESHOLD`, `DCU_INT_STATUS`, `DCU_INT_MASK`, `DCU_DIV_RATIO`, `DCU_UPDATE_MODE`, and `DCU_CTRLDESCLN(layer, reg)`. Layer macros encode height/width, position, enable, tiling, alpha blending, BPP, chroma-key bounds, colors, and pre/post skip. `struct fsl_dcu_soc_data` describes per-SoC layer counts and descriptor register count. `struct fsl_dcu_drm_device` stores device, node, regmap, IRQ, clocks, optional TCON, DRM objects, connector, and SoC data. It declares `fsl_dcu_drm_modeset_init()`.

## Control Flow

The header has no executable control flow. It shapes runtime control by giving other files the register contract. The platform driver selects a `fsl_dcu_soc_data`, KMS uses mode/timing macros to program the CRTC, planes compute descriptor offsets through `DCU_CTRLDESCLN()`, and IRQ code uses `DCU_INT_STATUS_VBLANK` and masks to reset/ack interrupts.

## State And Persistence

The structures define driver-owned persistent state across probe, modeset, and PM. The register macros describe persistent hardware state in the DCU and SCFG blocks. Layer descriptor registers remain programmed until explicitly reset, overwritten by atomic updates, or lost through clock/power reset.

## Dependencies And Integration Points

It includes DRM encoder and local CRTC/output/plane headers, and forward-declares kernel/DRM types. Integration points are the platform driver, CRTC programming, plane programming, output connector storage, optional TCON handling, regmap register access, syscon PIXCLK enable, and DRM private data.

## Risks And Test Signals

Risks are incorrect descriptor stride math between LS1021A and VF610, format-code mismatches with DRM fourcc selection, bitfield overflow from unchecked mode geometry, and stale register definitions if SoC variants diverge. Test by building all FSL DCU objects, probing both compatibles, exercising every advertised pixel format, validating 16-layer and 64-layer reset loops, and checking that horizontal display widths obey the DCU 16-pixel granularity used by the output code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_drv.h -->
