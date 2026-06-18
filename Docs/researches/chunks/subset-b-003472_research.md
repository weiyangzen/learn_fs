# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_0_0_sh_mask.h lines 1-2274

## Scope And Purpose

This chunk is the opening portion of AMD's generated VCN 5.0.0 register shift/mask header for the `uvd_uvddec` address block. It does not implement executable logic; it publishes C preprocessor constants that downstream AMDGPU VCN code uses to compose, update, and decode MMIO register values without hard-coding bit positions.

The covered range defines the include guard, license, and the first 2,200 register field macros. Each hardware field is generally represented by a `...__SHIFT` constant and a matching `..._MASK` constant. The fields cover top-level VCN/UVD identification, coarse UVD clock-gating controls, and a large set of SUVD clock-gating gate and control registers for decode, encode, AV1, VP9, HEVC, H.264, FBC, and related media sub-blocks.

This is a chunk-level report only. The final per-file report should merge this with later chunks because the file continues beyond line 2274, and this chunk ends inside the `SMP_SUVD_CGC_CTRL` field list.

## Register Groups Covered

The first group, `UVD_TOP_CTRL`, exposes the low bits for the VCN/UVD block standard and standard-version fields. These are likely used for block identification or feature-version reads.

`UVD_CGC_GATE` defines per-subunit clock-gate enable bits for the broader UVD/VCN decode block: `SYS`, `UDEC`, `MPEG2`, `REGS`, `RBC`, memory-interface pieces (`LMI_MC`, `LMI_UMC`), codec datapath units (`IDCT`, `MPRD`, `MPC`, `UDEC_RE`, `UDEC_CM`, `UDEC_IT`, `UDEC_DB`, `UDEC_MP`), and infrastructure units such as `WCB`, `VCPU`, `MMSCH`, `LCM0`, `LCM1`, `MIF`, `VREG`, `PE`, and `PPU`.

`UVD_CGC_CTRL` defines mode and timing fields for the same coarse clock-gating domain. It includes `DYN_CLOCK_MODE`, `CLK_GATE_DLY_TIMER`, `CLK_OFF_DELAY`, mode bits for individual UDEC pieces, and mode bits for system, memory, register, parser, and scheduler units.

The repeated `*_SUVD_CGC_GATE` groups are the largest portion of this chunk. They share a 32-bit layout for sub-block gate bits:

- Common SUVD units: `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, `SCLR`, `UVD_SC`, `ENT`, `IME`, `SITE`, `EFC`, `SAOE`, and `SMPA`.
- Codec-specific decode paths: H.264, HEVC, VP9, and AV1 variants such as `SRE_H264`, `SIT_HEVC`, `SCM_VP9`, `SDB_VP9`, `SRE_AV1`, and `SCM_AV1`.
- HEVC split decode/encode bits: `SIT_HEVC_DEC`, `SIT_HEVC_ENC`, and `IME_HEVC`.
- Frame-buffer compression clocks: `FBC_PCLK` and `FBC_CCLK`.

The identical `*_SUVD_CGC_GATE` layout is instantiated for `AVM`, `EFC`, `ENT`, `IME`, `PPU`, `SAOE`, `SCM`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, `SMPA`, `SMP`, `SRE`, and `UVD`.

The `*_SUVD_CGC_GATE2` groups extend clock-gating coverage for newer blocks. They share a smaller layout with `MPBE0`, `MPBE1`, `SIT_AV1`, `SDB_AV1`, `MPC1`, `SRE_AV1_ENC`, `CDEFE`, `AVM_0`, `AVM_1`, `SIT_NXT_CMN`, `SIT_NXT_DEC`, and `SIT_NXT_ENC`. In this chunk that layout is instantiated for `AVM`, `DBR`, `ENT`, `IME`, `SAOE`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, `SMPA`, `SMP`, `SRE`, and `UVD`.

The `*_SUVD_CGC_CTRL` groups define clock-gating mode bits for the same SUVD domains. Their common layout includes mode bits for `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, `SCLR`, `UVD_SC`, `ENT`, `IME`, `SITE`, `EFC`, `SAOE`, `SMPA`, `MPBE0`, `MPBE1`, `SIT_AV1`, `SDB_AV1`, `MPC1`, `AVM_0`, `AVM_1`, `SIT_NXT_CMN`, `SIT_NXT_DEC`, `SIT_NXT_ENC`, `CDEFE`, plus direct `FBC_PCLK` and `FBC_CCLK` bits. Complete groups in this chunk include `AVM`, `DBR`, `EFC`, `ENT`, `IME`, `PPU`, `SAOE`, `SCM`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, and `SMPA`. The chunk reaches only the first nine shift fields of `SMP_SUVD_CGC_CTRL`.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or callable APIs in this range. The public interface is a set of preprocessor macros consumed by C code in the AMDGPU driver.

The important naming contract is:

- `REGISTER__FIELD__SHIFT` for fields named with a doubled separator before `SHIFT`, for example `UVD_CGC_GATE__SYS__SHIFT`.
- `REGISTER__FIELD_MASK` for the corresponding bit mask, for example `UVD_CGC_GATE__SYS_MASK`.
- Register comment markers such as `//UVD_CGC_GATE` and `//AVM_SUVD_CGC_CTRL`, which mirror generated register names and make this header navigable.

Callers normally combine these constants with helper macros or inline bit manipulation, for example by clearing `FIELD_MASK` and inserting `(value << FIELD__SHIFT) & FIELD_MASK`. Single-bit fields have masks that are powers of two; multi-bit fields such as `UVD_TOP_CTRL__STANDARD_MASK`, `UVD_CGC_CTRL__CLK_GATE_DLY_TIMER_MASK`, and `UVD_CGC_CTRL__CLK_OFF_DELAY_MASK` cover wider ranges.

## Control Flow

This header has no runtime control flow. Its effect is at compile time: inclusion makes symbolic register bit definitions available to the VCN 5.0 driver code. Runtime control flow lives in the code that includes this file and writes hardware registers.

The practical write pattern is still important:

1. Driver code selects a register address from the matching VCN 5.0 register offset header.
2. It computes a new register value using the shift and mask constants in this file.
3. It writes the value through AMDGPU register accessors.
4. Hardware interprets the selected bits as clock-gating gates, clock-gating modes, delay timers, or version fields.

Because the macros are generated constants, the main "flow" risk is not branching behavior but whether each macro accurately maps to the VCN 5.0 hardware specification.

## State And Persistence Behavior

The file stores no software state and has no persistence behavior of its own. It describes persistent hardware register layout. Values written using these masks affect GPU media-engine state until changed by later driver operations, reset, power management transitions, suspend/resume handling, or firmware-controlled sequencing.

The most stateful users are expected to be VCN initialization, power-gating, clock-gating, suspend/resume, reset, and firmware boot paths. Incorrect values can persist in hardware registers across portions of the driver lifecycle and can surface as decode/encode hangs, broken power saving, or inability to wake sub-blocks.

## Dependencies And Integration Points

This header depends only on the C preprocessor and its include guard. In practice it is coupled to the rest of AMDGPU's generated VCN 5.0 register headers, especially the companion register-offset header for `vcn_5_0_0` and any VCN 5.0 driver source that references these symbols.

Integration points include:

- AMDGPU VCN/UVD initialization paths that configure top-level block state.
- Dynamic clock-gating and power-management code that enables or disables gates for UVD and SUVD sub-blocks.
- Codec block setup for H.264, HEVC, VP9, AV1, encode/decode split paths, and frame-buffer compression clocks.
- Debug or bring-up code that reads registers and decodes bitfields for tracing or register dumps.
- Generated-header synchronization with AMD hardware register databases; manual divergence from those sources would be risky.

Although this repository path is under `ceph-client`, the source itself is Linux AMDGPU DRM code. It is unrelated to Ceph filesystem logic except by repository aggregation.

## Risks And Edge Cases

The highest risk is silent hardware misconfiguration from a wrong bit position or mask. A one-bit shift error in a clock-gating field can enable, disable, or put the wrong media sub-block into dynamic mode.

The repeated SUVD layouts reduce conceptual complexity but increase generated-header review risk. Many registers intentionally share identical field layouts, so accidental copy/paste or generator skew may not be obvious unless compared against the hardware register database or runtime traces.

The chunk boundary is an edge case for documentation and automated analysis: `SMP_SUVD_CGC_CTRL` begins at line 2265, but this chunk includes only `SRE_MODE` through `IME_MODE` shifts and none of its masks. Later chunks must complete that register group before any file-level summary treats it as fully covered.

Clock-gating fields are power-management sensitive. Setting gate bits without matching control-mode bits, sequencing requirements, or firmware expectations can cause hangs that may only appear under suspend/resume, video playback, encode workloads, or low-power transitions.

Several fields represent codec-specific sub-blocks. A failure in an AV1, VP9, HEVC, or FBC-specific gate may not be caught by generic boot or display tests, so media workload coverage matters.

## Test Signals

There are no direct unit tests for this header in the chunk. Useful validation signals are compile-time and hardware/runtime oriented:

- Full kernel or AMDGPU build succeeds with all VCN 5.0 users including this header.
- Static checks find no undefined generated macros in VCN 5.0 clock-gating and power-management code.
- Register write/readback traces show expected masks and shifts for `UVD_CGC_GATE`, `UVD_CGC_CTRL`, `*_SUVD_CGC_GATE`, `*_SUVD_CGC_GATE2`, and `*_SUVD_CGC_CTRL`.
- VCN 5.0 video decode and encode workloads pass for H.264, HEVC, VP9, and AV1 where supported.
- Suspend/resume, GPU reset, runtime power management, and dynamic clock-gating tests do not produce media-engine hangs.
- Power measurements or clock-gating debug counters show intended blocks entering and leaving gated states.
- Generated-header diff checks against the authoritative AMD register database catch accidental manual edits or stale generated output.
