<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_reg.h

## Purpose

`ast_reg.h` names AST VGA I/O register offsets and important bit fields used by the modesetting and output-detection code. It is a small hardware ABI header for VGA sequencer, CRTC, graphics, misc, and DisplayPort-related AST extension registers.

## Important APIs, Types, And Macros

The header exports only macros. Key groups include:

- VGA I/O aperture definitions: `AST_IO_MM_OFFSET`, `AST_IO_MM_LENGTH`, and offsets such as `AST_IO_VGAMR_*`, `AST_IO_VGASRI`, `AST_IO_VGACRI`, and `AST_IO_VGAIR1_R`.
- VGA enable/control bits: `AST_IO_VGAMR_IOSEL`, `AST_IO_VGAER_VGA_ENABLE`, `AST_IO_VGASR1_SD`, and `AST_IO_VGACR17_SYNC_ENABLE`.
- AST extended CRTC bits: password `AST_IO_VGACR80_PASSWORD`, memory-reservation/memory-size masks, VGA I/O disable and MMIO enable bits, DVO enable, cursor format/enable bits, and VRAM initialization status bits.
- Output-detection fields: `AST_IO_VGACRD1_TX_TYPE_MASK` with transmitter type values for no TX, ITE66121, SIL164, CH7003, DP501, ANX9807, embedded DP501 firmware, and ASTDP.
- DisplayPort flags for EDID validity, link success, HPD, video enable, PHY sleep, and 24-bpp mode.

## Control Flow

This file has no control flow. Consumers use the offsets with AST I/O helpers and test or update bit fields to enable VGA/MMIO access, infer display transmitter type, manage sync/video state, and query BMC/firmware status.

## State And Persistence Behavior

The macros describe hardware register state. Writes through consumers persist in AST VGA/DisplayPort control registers until later register writes, reset, or firmware/BMC action. Some fields mirror SoC or firmware state such as VRAM initialization and MCU firmware execution.

## Dependencies And Integration Points

It includes `<linux/bits.h>` for `BIT()` and `GENMASK()`. It is consumed by AST KMS, output, DDC, DP, and initialization code wherever direct VGA-style I/O registers are accessed.

## Risks And Edge Cases

Several fields are mirrors of firmware or BMC-owned state and should be treated as hardware contracts. Output transmitter type values are encoded in shifted/masked register bits, so consumers must apply the mask correctly. Sync/video control bits can blank the display if changed in the wrong sequence.

## Test Signals

Build coverage for AST, register read/write smoke tests during probe, output-type detection on boards with VGA/DVI/DP transmitters, VRAM init status handling, and DP HPD/link/EDID tests validate this header's use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_reg.h -->
