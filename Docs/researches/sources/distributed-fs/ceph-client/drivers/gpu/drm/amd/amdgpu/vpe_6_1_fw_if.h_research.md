# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vpe_6_1_fw_if.h

## Purpose
`vpe_6_1_fw_if.h` defines the command ABI between the AMDGPU VPE driver and VPE 6.1 firmware. It supplies opcode enums and bitfield macros for building VPE command stream words.

## Important APIs, Types, And Functions
The main enum is `enum VPE_CMD_OPCODE`, covering NOP, VPE descriptor, plane config, VPEP config, indirect buffer, fence, trap, register write, poll reg/mem, conditional execute, atomic, predicated execute, collaboration sync, and timestamp commands. Subopcode enums cover plane config and VPEP config modes. Key macros include `VPE_CMD_HEADER()`, `VPE_CMD_NOP_HEADER_COUNT()`, `VPE_DESC_CMD_HEADER()`, `VPE_PLANE_CFG_CMD_HEADER()`, `VPE_DIR_CFG_CMD_HEADER()`, `VPE_IND_CFG_CMD_HEADER()`, `VPE_CMD_INDIRECT_HEADER_VMID()`, and poll-regmem interval/retry/function/memory field helpers.

## Control Flow
The header has no direct control flow. Callers such as `amdgpu_vpe.c` use these macros while emitting VPE ring and IB packets for fences, traps, predication, indirect buffers, polling, and register writes. VPE firmware interprets the encoded words and performs the actual control flow.

## State And Persistence
No C state is stored here. The macro output becomes persistent ring/IB data until VPE firmware consumes it. Plane config fields encode source/destination plane counts, swizzle, rotation, pitch, viewport, and element size, so mistakes affect image-processing state in firmware.

## Dependencies And Integration Points
`amdgpu_vpe.h` includes this header, and `amdgpu_vpe.c` uses the command constructors while `vpe_v6_1.c` sets up firmware and rings. The definitions must match the shipped `amdgpu/vpe_6_1_*.bin` firmware interface.

## Risks
The header is a firmware ABI. Any opcode, mask, or shift mismatch can cause silent firmware misinterpretation. Several masks are expressed as field masks but the macros first mask the raw value and then shift; for fields whose mask is already in post-shift position, this pattern can drop valid high bits. `VPE_PLANE_CFG_CMD_HEADER()` appears to use `npd0` for the `NPD1` field, which should be reviewed because it may prevent independent destination-plane count encoding for the second plane.

## Test Signals
Signals include VPE ring tests, successful fence and trap completion, indirect-buffer execution with expected VMID, poll-regmem timeout behavior, and image-processing workloads that cover 1-to-1, 2-to-1, and 2-to-2 plane configurations. Firmware interface changes should be tested with each declared VPE 6.1 firmware binary.
