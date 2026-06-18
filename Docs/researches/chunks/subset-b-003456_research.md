# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_0_sh_mask.h lines 1-2275

## Scope And Purpose

This chunk is the opening 2,275-line segment of AMD's generated VCN 4.0.0 shift/mask header. It contains only C preprocessor constants: register-field bit positions exposed as `<REGISTER>__<FIELD>__SHIFT` and raw bit masks exposed as `<REGISTER>__<FIELD>_MASK`. It defines no functions, structs, enums, storage, branches, locks, allocation paths, or direct MMIO operations.

The path is under a `ceph-client` source mirror, but this file is AMDGPU media-engine register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU VCN code that includes this header with `vcn_4_0_0_offset.h`, then uses SOC15 register helpers to read, update, and poll VCN/UVD registers.

This chunk covers the start of the `uvd0_uvddec` address block: top-level VCN/UVD clock-gating control plus many SUVD sub-block clock-gate and clock-gate-mode register aliases. It ends at the `//SCM_SUVD_CGC_CTRL` comment; the actual `SCM_SUVD_CGC_CTRL` field macros start after this chunk.

## Important APIs, Types, And Macros

The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position used when packing or unpacking a field value.
- `<REGISTER>__<FIELD>_MASK`: raw bit mask used for preserving, clearing, setting, or testing a field.

Major register groups in this chunk:

- `UVD_TOP_CTRL`: exposes `STANDARD` and `STD_VERSION`, identifying the VCN/UVD register block standard and version field.
- `UVD_CGC_GATE`: top-level clock gate bits for `SYS`, `UDEC`, `MPEG2`, `REGS`, `RBC`, LMI memory-controller/UMC paths, `IDCT`, `MPRD`, `MPC`, `LBSI`, `LRBBM`, UDEC subunits, `WCB`, `VCPU`, `MMSCH`, `LCM0`, `LCM1`, `MIF`, `VREG`, `PE`, and `PPU`.
- `UVD_CGC_CTRL`: dynamic clock-gating control fields, including `DYN_CLOCK_MODE`, `CLK_GATE_DLY_TIMER`, `CLK_OFF_DELAY`, and per-block mode bits for UDEC, SYS, MPEG2, REGS, RBC, LMI, IDCT, MPRD, MPC, LBSI, LRBBM, WCB, VCPU, and MMSCH.
- First-generation SUVD gate banks: `AVM_SUVD_CGC_GATE`, `CDEFE_SUVD_CGC_GATE`, `EFC_SUVD_CGC_GATE`, `ENT_SUVD_CGC_GATE`, `IME_SUVD_CGC_GATE`, `PPU_SUVD_CGC_GATE`, `SAOE_SUVD_CGC_GATE`, `SCM_SUVD_CGC_GATE`, `SDB_SUVD_CGC_GATE`, `SIT0_NXT_SUVD_CGC_GATE`, `SIT1_NXT_SUVD_CGC_GATE`, `SIT2_NXT_SUVD_CGC_GATE`, `SIT_SUVD_CGC_GATE`, `SMPA_SUVD_CGC_GATE`, `SMP_SUVD_CGC_GATE`, `SRE_SUVD_CGC_GATE`, `UVD_MPBE0_SUVD_CGC_GATE`, `UVD_MPBE1_SUVD_CGC_GATE`, and `UVD_SUVD_CGC_GATE`. Each repeats the same broad field layout for codec and pipeline sub-blocks such as `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, H.264/HEVC-specific sub-blocks, `SCLR`, `UVD_SC`, `ENT`, `IME`, `SITE`, VP9 decode fields, `EFC`, `SAOE`, AV1 decode fields, `FBC_PCLK`, `FBC_CCLK`, `SCM_AV1`, and `SMPA`.
- Second-generation SUVD gate banks: `*_SUVD_CGC_GATE2` for AVM, CDEFE, DBR, ENT, IME, MPC1, SAOE, SDB, SIT0_NXT, SIT1_NXT, SIT2_NXT, SIT, SMPA, SMP, SRE, UVD_MPBE0, UVD_MPBE1, and UVD. These add gates for `MPBE0`, `MPBE1`, `SIT_AV1`, `SDB_AV1`, `MPC1`, `SRE_AV1_ENC`, `CDEFE`, `AVM_0`, `AVM_1`, and next-generation SIT common/decode/encode blocks. The MPBE-specific variants in this range expose only the low seven fields.
- SUVD control banks: `AVM_SUVD_CGC_CTRL`, `CDEFE_SUVD_CGC_CTRL`, `DBR_SUVD_CGC_CTRL`, `EFC_SUVD_CGC_CTRL`, `ENT_SUVD_CGC_CTRL`, `IME_SUVD_CGC_CTRL`, `MPC1_SUVD_CGC_CTRL`, `PPU_SUVD_CGC_CTRL`, and `SAOE_SUVD_CGC_CTRL`. These define mode bits for the same sub-block families, plus `FBC_PCLK`, `FBC_CCLK`, and `CDEFE_MODE`. `SCM_SUVD_CGC_CTRL` is only the next register heading at this chunk boundary.

## Control Flow And Runtime Behavior

There is no control flow in this header. The runtime pattern is indirect:

1. VCN implementation files include `vcn/vcn_4_0_0_offset.h` for register addresses and this header for field masks and shifts.
2. Driver code reads a register with helpers such as `RREG32_SOC15`, changes fields using these masks and shifts, writes back with `WREG32_SOC15`, and sometimes waits with `SOC15_WAIT_ON_RREG`.
3. Dynamic power-gating mode paths can also program the same register values through DPG SRAM helpers rather than direct MMIO writes.

Concrete integration in this tree includes `amdgpu/vcn_v4_0.c`, which includes this exact header and uses `UVD_CGC_CTRL`, `UVD_CGC_GATE`, `UVD_SUVD_CGC_GATE`, and `UVD_SUVD_CGC_CTRL` masks in the VCN 4.0 clock-gating enable/disable paths. Nearby VCN 4.0.5 and older UVD/VCN implementations use the same generated macro contract for comparable clock-gating sequences.

## State And Persistence Behavior

The macros hold no software state and persist nothing by themselves. They describe stateful hardware registers whose values remain in the VCN/UVD block until firmware, the kernel driver, reset, power gating, suspend/resume restore, or hardware-owned sequencing changes them.

State represented by this chunk includes whether top-level VCN/UVD functional blocks are clock-gated, whether each block uses dynamic or software-controlled gating mode, the clock-gate delay/off timers, and whether individual codec pipeline blocks for H.264, HEVC, VP9, AV1, entropy, scaler, motion-estimation/motion-prediction, frame-buffer-compression clocks, MPBE, MPC1, DBR, CDEFE, and next-generation SIT paths are eligible for gating.

The header does not encode access type or sequencing rules. Some fields are configuration bits, while some may be status-sensitive or hardware-sequenced depending on the programming model. Consumers must preserve reserved bits and avoid full-register writes unless the ASIC sequence says they are valid.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_0_offset.h`, which supplies addresses such as `regUVD_TOP_CTRL`, `regUVD_CGC_GATE`, `regUVD_CGC_CTRL`, `regUVD_SUVD_CGC_GATE`, `regUVD_SUVD_CGC_GATE2`, and the aliased per-sub-block SUVD gate/control register names.

The primary integration point is AMDGPU's VCN 4.0 block implementation:

- `amdgpu/vcn_v4_0.c` includes `vcn_4_0_0_offset.h`, `vcn_4_0_0_sh_mask.h`, and `irqsrcs_vcn_4_0.h`.
- Its clock-gating paths program `UVD_CGC_CTRL` delay/mode fields, clear or set `UVD_CGC_GATE` fields, set `UVD_SUVD_CGC_GATE` fields, and toggle `UVD_SUVD_CGC_CTRL` mode bits.
- Its DPG-mode paths write equivalent register values through indirect DPG SRAM update helpers.

The generated names are the compile-time contract. Missing or renamed macros usually fail at build time, but incorrect numeric masks or shifts can compile cleanly and produce media-engine hangs, power-management regressions, or codec-specific failures at runtime.

## Risks And Edge Cases

- This is generated hardware metadata. Manual edits or generator drift are high risk because the C compiler cannot detect a numerically wrong mask that still has the right name.
- `UVD_CGC_GATE` and `UVD_CGC_CTRL` are central to VCN bring-up and clock gating. Bad masks can leave clocks disabled while firmware, rings, or MMIO paths are active, or can prevent low-power entry entirely.
- The many `*_SUVD_CGC_GATE` groups are repetitive and often share the same underlying offset aliases. A one-register or one-field copy error can affect only a single codec path, such as VP9, AV1, HEVC encode/decode, MPBE, or frame-buffer-compression clocks.
- `*_SUVD_CGC_GATE2` extends the gate model for AV1, MPBE, MPC1, DBR/CDEFE, AVM instances, and next-generation SIT blocks. Missing these fields in programming sequences can cause incomplete power savings or block wake failures on newer media paths.
- Some aliases in `vcn_4_0_0_offset.h` intentionally map many named sub-block registers to the same offset. Consumers must treat those aliases as hardware views of a shared register layout, not independent persistent software variables.
- Full-register writes risk disturbing reserved bits or hardware-owned fields. Masked read-modify-write is safer where the programming sequence permits it.
- The chunk boundary cuts off `SCM_SUVD_CGC_CTRL`: line 2275 is only the register heading, so any final per-file report must merge the next chunk before describing the full SUVD control-bank set.

## Test Signals

Useful validation for this chunk includes:

- Build AMDGPU with VCN 4.0 support enabled so include paths and macro expansions in `vcn_v4_0.c` catch missing symbols.
- Mechanically compare `vcn_4_0_0_sh_mask.h` against the authoritative register database and its companion `vcn_4_0_0_offset.h`.
- Check mask/shift consistency for every field in lines 1-2275: each field should have the expected low-bit shift and a mask that covers the intended width at that position.
- Diff against neighboring generated VCN headers, especially `vcn_4_0_3_sh_mask.h` and `vcn_4_0_5_sh_mask.h`, where layout parity is expected and ASIC-specific differences are intentional.
- Runtime exercise should include VCN firmware load, decode and encode ring tests, JPEG/VCN interrupt paths, clock-gating enable/disable, dynamic power-gating mode, suspend/resume, and mixed H.264/HEVC/VP9/AV1 workloads where supported.
- Watch for `SOC15_WAIT_ON_RREG` timeouts, VCN ring-test failures, firmware boot failures, media decode/encode hangs, unexpected power-state transitions, resume-only failures, and regressions that appear only under a particular codec or VCN instance.

## Cross-Chunk Notes

This is the first chunk of the file and includes the license, include guard opening, and the beginning of the `uvd0_uvddec` address block. The next chunk is required for the `SCM_SUVD_CGC_CTRL` definitions introduced at line 2275 and for the rest of the generated VCN 4.0.0 register field namespace. Final reconciliation should merge all chunks before making complete claims about the header.
