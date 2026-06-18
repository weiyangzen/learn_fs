# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_hw.h

## Purpose
This header defines decoder hardware-subdevice register constants, hardware register indexes, and the subdevice runtime state structure.

## Important APIs, Types, And Functions
Register constants identify active-status and interrupt configuration bits. `IS_SUPPORT_VDEC_HW_IRQ()` excludes LAT_SOC from IRQ use. `enum mtk_vdec_hw_reg_idx` indexes subdevice SYS and MISC register bases. `struct mtk_vdec_hw_dev` stores child platform device, parent decoder device, mapped registers, current context, IRQ number, PM resources, and hardware index.

## Control Flow
No direct execution. Parent/subdevice probe, IRQ handling, PM, and current-context helpers consume these definitions.

## State, Persistence, And Dependencies
State is runtime-only per hardware subdevice. Dependencies include I/O access, platform devices, and decoder driver state.

## Integration Points
Included by child hardware driver, decoder parent driver, decoder PM, and common util code for subdevice lookup.

## Risks
Register offsets and IRQ masks are hardware ABI. Hardware indexes must align with `enum mtk_vdec_hw_id`. LAT_SOC no-IRQ behavior must match device tree and PM requirements.

## Test Signals
Compile coverage, child probe, IRQ clear sequence, and PM enable/disable for LAT/core/SOC blocks.
