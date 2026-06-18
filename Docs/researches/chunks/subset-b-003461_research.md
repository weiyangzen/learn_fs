# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_sh_mask.h lines 1-2275

## Scope And Purpose

This chunk is the opening 2,275-line segment of AMD's generated VCN 4.0.3 register shift/mask header. It contains C preprocessor constants only: each hardware field is represented as a `<REGISTER>__<FIELD>__SHIFT` bit position and a matching `<REGISTER>__<FIELD>_MASK` value. It defines no functions, structs, enums, variables, branches, locks, memory allocation, or direct MMIO operations.

The path is inside a `ceph-client` source mirror, but the file is AMDGPU media-engine register metadata, not Ceph filesystem logic. The runtime behavior is in AMDGPU VCN/JPEG driver code that includes this header with the companion VCN 4.0.3 offset header and uses these constants to read, update, and poll ASIC registers.

The chunk starts with the license, include guard, and `aid_uvd0_uvddec` address-block comment. It covers `UVD_TOP_CTRL`, primary UVD clock-gating registers, many SUVD per-subblock gate maps, secondary SUVD gate maps, and the beginning of per-subblock SUVD clock-gating control maps. It ends on the `//SCM_SUVD_CGC_CTRL` marker; the fields for that register are in the following chunk.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low bit of a field, used for left shifts when packing values.
- `<REGISTER>__<FIELD>_MASK`: raw bit mask for clearing, testing, or preserving fields in register values.

Register groups covered in this chunk:

- Header and top-level identity: `_vcn_4_0_3_SH_MASK_HEADER` and `UVD_TOP_CTRL`. `UVD_TOP_CTRL` exposes `STANDARD` and `STD_VERSION` fields.
- Primary UVD clock gating: `UVD_CGC_GATE` and `UVD_CGC_CTRL`. These cover the base VCN/UVD block gates and modes for `SYS`, `UDEC`, `MPEG2`, `REGS`, `RBC`, `LMI_MC`, `LMI_UMC`, `IDCT`, `MPRD`, `MPC`, `LBSI`, `LRBBM`, `UDEC_RE`, `UDEC_CM`, `UDEC_IT`, `UDEC_DB`, `UDEC_MP`, `WCB`, `VCPU`, `MMSCH`, `LCM0`, `LCM1`, `MIF`, `VREG`, `PE`, and `PPU`, plus dynamic clock mode and delay fields.
- Full-width SUVD gate registers: `AVM_SUVD_CGC_GATE`, `CDEFE_SUVD_CGC_GATE`, `EFC_SUVD_CGC_GATE`, `ENT_SUVD_CGC_GATE`, `IME_SUVD_CGC_GATE`, `PPU_SUVD_CGC_GATE`, `SAOE_SUVD_CGC_GATE`, `SCM_SUVD_CGC_GATE`, `SDB_SUVD_CGC_GATE`, `SIT0_NXT_SUVD_CGC_GATE`, `SIT1_NXT_SUVD_CGC_GATE`, `SIT2_NXT_SUVD_CGC_GATE`, `SIT_SUVD_CGC_GATE`, `SMPA_SUVD_CGC_GATE`, `SMP_SUVD_CGC_GATE`, `SRE_SUVD_CGC_GATE`, `UVD_MPBE0_SUVD_CGC_GATE`, `UVD_MPBE1_SUVD_CGC_GATE`, and `UVD_SUVD_CGC_GATE`. These repeat a 32-bit layout for decode/encode and codec subblocks such as `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, H.264, HEVC, VP9, AV1, `SCLR`, `UVD_SC`, `ENT`, `IME`, `SITE`, `EFC`, `SAOE`, FBC clocks, and `SMPA`.
- Secondary SUVD gate registers: `AVM_SUVD_CGC_GATE2`, `CDEFE_SUVD_CGC_GATE2`, `DBR_SUVD_CGC_GATE2`, `ENT_SUVD_CGC_GATE2`, `IME_SUVD_CGC_GATE2`, `MPC1_SUVD_CGC_GATE2`, `SAOE_SUVD_CGC_GATE2`, `SDB_SUVD_CGC_GATE2`, `SIT0_NXT_SUVD_CGC_GATE2`, `SIT1_NXT_SUVD_CGC_GATE2`, `SIT2_NXT_SUVD_CGC_GATE2`, `SIT_SUVD_CGC_GATE2`, `SMPA_SUVD_CGC_GATE2`, `SMP_SUVD_CGC_GATE2`, `SRE_SUVD_CGC_GATE2`, `UVD_MPBE0_SUVD_CGC_GATE2`, `UVD_MPBE1_SUVD_CGC_GATE2`, and `UVD_SUVD_CGC_GATE2`. Most expose `MPBE0`, `MPBE1`, `SIT_AV1`, `SDB_AV1`, `MPC1`, `SRE_AV1_ENC`, `CDEFE`, `AVM_0`, `AVM_1`, and SIT-next common/decode/encode gates. The two `UVD_MPBE*_SUVD_CGC_GATE2` groups stop at `CDEFE`, so they have fewer fields.
- SUVD control registers through the chunk boundary: complete definitions for `AVM_SUVD_CGC_CTRL`, `CDEFE_SUVD_CGC_CTRL`, `DBR_SUVD_CGC_CTRL`, `EFC_SUVD_CGC_CTRL`, `ENT_SUVD_CGC_CTRL`, `IME_SUVD_CGC_CTRL`, `MPC1_SUVD_CGC_CTRL`, `PPU_SUVD_CGC_CTRL`, and `SAOE_SUVD_CGC_CTRL`; plus only the marker for `SCM_SUVD_CGC_CTRL`. The complete control groups encode `_MODE` bits for major SUVD subblocks and high-bit FBC/CDEFE controls.

## Control Flow And Runtime Behavior

There is no control flow in this header. Runtime use is indirect:

1. `amdgpu/vcn_v4_0_3.c` includes `vcn_4_0_3_offset.h` for register addresses and this file for field masks/shifts.
2. VCN clock-gating paths read registers with `RREG32_SOC15`, update fields with these masks/shifts, write with `WREG32_SOC15`, and in one path poll `regUVD_CGC_GATE` with `SOC15_WAIT_ON_RREG`.
3. DPG-mode initialization writes the same register fields through `WREG32_SOC15_DPG_MODE` and `SOC15_DPG_MODE_OFFSET`, so the constants are used both for direct register programming and for values staged through dynamic power gating SRAM.
4. `amdgpu/jpeg_v4_0_3.c` includes this header too, but its clock-gating work uses later JPEG macros from the same generated file, outside this chunk.

For this chunk specifically, `vcn_v4_0_3_disable_clock_gating()` clears primary `UVD_CGC_CTRL` and `UVD_CGC_GATE` mode/gate bits, waits for UVD gate state to settle, then programs `UVD_SUVD_CGC_GATE` and `UVD_SUVD_CGC_CTRL` for SUVD subblocks. `vcn_v4_0_3_enable_clock_gating()` sets the primary and SUVD mode bits. `vcn_v4_0_3_disable_clock_gating_dpg_mode()` builds equivalent values for DPG startup.

## State And Persistence Behavior

The macros hold no software state and persist nothing. They describe fields in stateful VCN/UVD/SUVD hardware registers. Values written to those registers remain in the media engine until the driver changes them, the block is reset, a power-gating transition rewrites or loses the state, or suspend/resume reinitializes the device.

State represented by this chunk is mostly clock-gating configuration: whether clocks are dynamically gated, software-vs-hardware gating mode per subblock, clock gate delay timers, clock off delay, and gate enables for codec and support units. Because some of these registers are used during DPG startup, incorrect values can affect both normal runtime register access and firmware-mediated power-gated startup.

Access semantics are not encoded by the macro names. Consumers must know from the ASIC programming guide and surrounding driver code whether a field is writable, read-only, sticky, hardware-owned, or sequencing-sensitive. The driver usually performs masked read-modify-write operations rather than blind full-register writes when preserving unrelated or reserved bits matters.

## Dependencies And Integration Points

This chunk depends on the companion address header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_offset.h`, which supplies register address macros such as `regUVD_CGC_CTRL`, `regUVD_CGC_GATE`, `regUVD_SUVD_CGC_GATE`, and `regUVD_SUVD_CGC_CTRL`.

Primary integration points in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_3.c`, which programs the VCN 4.0.3 media block, start/stop paths, DPG mode, rings, interrupts, memory windows, and clock gating.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_3.c`, which shares the same generated header for JPEG VCN 4.0.3 register fields.
- SOC15 register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `SOC15_REG_OFFSET`, `SOC15_DPG_MODE_OFFSET`, and `WREG32_SOC15_DPG_MODE`.
- Power-management flags such as `AMD_CG_SUPPORT_VCN_MGCG`, which decide whether the driver uses these software clock-gating sequences or returns early.

The generated names are the compile-time contract between ASIC register descriptions and driver code. Missing or renamed macros usually fail at build time. Wrong numeric masks or shifts can compile cleanly and cause runtime hardware misprogramming.

## Risks And Edge Cases

- This chunk ends at the `SCM_SUVD_CGC_CTRL` comment only. A per-file report must merge the next chunk before treating that register group as complete.
- `UVD_CGC_CTRL__DYN_CLOCK_MODE`, `CLK_GATE_DLY_TIMER`, and `CLK_OFF_DELAY` are used during enable, disable, and DPG startup. Incorrect shifts can set the wrong control bits while still producing plausible-looking writes.
- `UVD_CGC_GATE` and `UVD_CGC_CTRL` combine many independent gates/modes. A bad mask may leave one subblock clock-gated during access, or keep clocks ungated and hurt power behavior.
- `SOC15_WAIT_ON_RREG` waits for `regUVD_CGC_GATE` to settle after gate manipulation. Incorrect masks can turn a clock-gating change into timeout, hang, or silent incomplete disable.
- SUVD gate layouts are highly repetitive across many block-prefixed registers. Copy-generation drift or one malformed field can affect only one codec pipeline or sub-instance, which makes failures workload-specific.
- `*_GATE2` layouts are not perfectly uniform: `UVD_MPBE0_SUVD_CGC_GATE2` and `UVD_MPBE1_SUVD_CGC_GATE2` only define through `CDEFE`. Generic code must not assume every gate2 register has the full 12-field layout.
- Some names describe codec-specific hardware such as H.264, HEVC, VP9, and AV1 decode/encode paths. Bad masks may show only under specific media formats or encode/decode combinations.
- The header gives no reserved-bit policy. Full-register writes risk disturbing undocumented or later-generation bits; local code mostly uses read-modify-write or explicitly staged DPG values.

## Test Signals

Useful validation for this chunk includes:

- Build AMDGPU with VCN 4.0.3/JPEG 4.0.3 support so includes and macro references in `vcn_v4_0_3.c` and `jpeg_v4_0_3.c` are checked.
- Mechanically compare `vcn_4_0_3_sh_mask.h` against the authoritative generated register database and against `vcn_4_0_3_offset.h` for matching register names.
- Check that each field in lines 1-2275 has coherent mask/shift pairs: `mask == field_width_mask << shift`, no overlapping single-bit fields within a register unless documented, and expected gaps for reserved bits.
- Diff against neighboring VCN 4.x headers where register layout should match, especially `UVD_CGC_CTRL`, `UVD_CGC_GATE`, `UVD_SUVD_CGC_GATE`, `UVD_SUVD_CGC_GATE2`, and `UVD_SUVD_CGC_CTRL`.
- Runtime exercise should cover VCN clock-gating enable/disable, VCN DPG-mode start, suspend/resume, decode workloads across H.264/HEVC/VP9/AV1, encode paths where available, and simultaneous JPEG/VCN activity.
- Watch for kernel logs reporting VCN register wait timeouts, ring test failures, firmware boot failures, DPG startup failures, media decode hangs, unexpected power draw, or failures that appear only when `AMD_CG_SUPPORT_VCN_MGCG` is absent or disabled.

## Cross-Chunk Notes

This is the first chunk for `vcn_4_0_3_sh_mask.h`, so it includes the file guard and the beginning of the generated namespace. The next chunk is needed for the complete `SCM_SUVD_CGC_CTRL` group and the rest of the VCN/JPEG register field definitions. Final reconciliation should merge all chunks before making complete claims about the full header.
