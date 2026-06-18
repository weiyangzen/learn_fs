# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_5_sh_mask.h lines 1-2276

## Scope And Purpose

This chunk is the opening 2,276-line segment of AMD's generated VCN 4.0.5 register shift/mask header. It defines C preprocessor constants only: hardware register fields are exported as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. There are no functions, structs, enums, variables, allocations, branches, locks, or direct MMIO operations in this chunk.

The path is under a `ceph-client` source mirror, but this file is AMDGPU media-engine register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU VCN code that combines these masks and shifts with register offsets from `vcn_4_0_5_offset.h`, then accesses hardware through SOC15 MMIO helpers.

This chunk covers the start of the `uvd_uvddec` address block. It begins with the file license and include guard, then defines clock-gating field layouts for the core UVD/VCN block and many SUVD subblocks. The chunk boundary lands inside `SAOE_SUVD_CGC_CTRL`; the remaining masks for that register and later register families are in following chunks.

## Important APIs, Types, And Macros

The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position used to pack or unpack a field.
- `<REGISTER>__<FIELD>_MASK`: raw 32-bit field mask used for masked reads, writes, or field construction.

Major register families in this chunk:

- Core VCN/UVD clock gating: `UVD_CGC_GATE` and `UVD_CGC_CTRL`. These define gate bits and mode bits for `SYS`, `UDEC`, `MPEG2`, `REGS`, `RBC`, `LMI_MC`, `LMI_UMC`, `IDCT`, `MPRD`, `MPC`, `LBSI`, `LRBBM`, `UDEC_RE`, `UDEC_CM`, `UDEC_IT`, `UDEC_DB`, `UDEC_MP`, `WCB`, `VCPU`, `MMSCH`, `LCM0`, `LCM1`, `MIF`, `VREG`, `PE`, and `PPU`, plus dynamic-clock mode and timing fields `CLK_GATE_DLY_TIMER` and `CLK_OFF_DELAY`.
- First SUVD clock-gate bank: `*_SUVD_CGC_GATE` registers for `AVM`, `CDEFE`, `EFC`, `ENT`, `IME`, `PPU`, `SAOE`, `SCM`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, `SMPA`, `SMP`, `SRE`, `UVD_MPBE0`, `UVD_MPBE1`, and aggregate `UVD_SUVD_CGC_GATE`. Each repeated layout exposes subblock gates such as `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, codec-specific H.264/HEVC/VP9 paths, `SCLR`, `UVD_SC`, `ENT`, `IME`, `SITE`, `EFC`, `SAOE`, `SRE_AV1`, FBC clocks, `SCM_AV1`, and `SMPA`.
- Second SUVD clock-gate bank: `*_SUVD_CGC_GATE2` registers for `AVM`, `CDEFE`, `DBR`, `ENT`, `IME`, `MPC1`, `SAOE`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, `SMPA`, `SMP`, `SRE`, `UVD_MPBE0`, `UVD_MPBE1`, and aggregate `UVD_SUVD_CGC_GATE2`. These add newer subblocks such as `MPBE0`, `MPBE1`, `SIT_AV1`, `SDB_AV1`, `MPC1`, `SRE_AV1_ENC`, `CDEFE`, `AVM_0`, `AVM_1`, `SIT_NXT_CMN`, `SIT_NXT_DEC`, `SIT_NXT_ENC`, and for some per-block registers `SMPN_ENC` and `SMPN_DEC`.
- SUVD clock-gating mode controls: `AVM_SUVD_CGC_CTRL`, `CDEFE_SUVD_CGC_CTRL`, `DBR_SUVD_CGC_CTRL`, `EFC_SUVD_CGC_CTRL`, `ENT_SUVD_CGC_CTRL`, `IME_SUVD_CGC_CTRL`, `MPC1_SUVD_CGC_CTRL`, `PPU_SUVD_CGC_CTRL`, and the first part of `SAOE_SUVD_CGC_CTRL`. These expose software/dynamic mode bits for the same SUVD subblocks, plus `FBC_PCLK`, `FBC_CCLK`, and `CDEFE_MODE`.

Within lines 1-2276 there are 49 commented register sections and about 2,200 generated `#define` entries. Most registers have a full set of matching shift and mask constants; the last visible register, `SAOE_SUVD_CGC_CTRL`, is incomplete at this chunk boundary.

## Control Flow And Runtime Behavior

There is no executable control flow in this header. Runtime use is indirect:

1. `drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.c` includes `vcn/vcn_4_0_5_offset.h` and this mask header.
2. The VCN implementation reads and writes generation-specific registers such as `regUVD_CGC_CTRL`, `regUVD_CGC_GATE`, `regUVD_SUVD_CGC_GATE`, and `regUVD_SUVD_CGC_CTRL` with `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_WAIT_ON_RREG`, and DPG variants.
3. Driver code builds register values by shifting small integers with `__SHIFT` macros and by setting or clearing groups of `_MASK` bits.
4. Hardware state changes happen only when those computed values are written through the SOC15 access layer.

Concrete integration in `vcn_v4_0_5.c` includes:

- `vcn_v4_0_5_disable_clock_gating()` clears `UVD_CGC_CTRL__DYN_CLOCK_MODE_MASK`, sets `CLK_GATE_DLY_TIMER` and `CLK_OFF_DELAY`, clears a broad set of `UVD_CGC_GATE__*` bits, waits for `regUVD_CGC_GATE` to read back as zero, clears `UVD_CGC_CTRL__*_MODE_MASK` bits, sets many `UVD_SUVD_CGC_GATE__*` bits, and clears selected `UVD_SUVD_CGC_CTRL__*_MODE_MASK` bits.
- `vcn_v4_0_5_disable_clock_gating_dpg_mode()` writes equivalent values through `WREG32_SOC15_DPG_MODE` and `SOC15_DPG_MODE_OFFSET` so dynamic power-gating SRAM programming uses the same field layout.
- `vcn_v4_0_5_enable_clock_gating()` sets the core `UVD_CGC_CTRL__*_MODE_MASK` bits and selected `UVD_SUVD_CGC_CTRL__*_MODE_MASK` bits to enable software-controlled clock gating when medium-grain clock gating is not already handled elsewhere.

Many per-subblock `*_SUVD_CGC_GATE`, `*_GATE2`, and `*_CTRL` macros are not directly referenced by `vcn_v4_0_5.c` in this tree, but they remain part of the generated ABI for diagnostics, register dumps, future driver paths, and parity with the hardware register database.

## State And Persistence Behavior

The macros themselves hold no software state and persist nothing. They describe bitfields in stateful VCN/UVD hardware registers. Values written through these fields persist in the media engine until rewritten, reset, power-gated, or restored by driver resume/reinitialization paths.

The represented hardware state is mostly clock-gating policy and status-control state: which VCN/UVD subblocks may be clock gated, whether gating is software or dynamic mode, how long the block waits before gating clocks, and which decode/encode codec subblocks are included. The fields cover both broad blocks (`SYS`, `RBC`, `LMI`, `VCPU`, `MMSCH`) and fine-grained codec or pipeline blocks for H.264, HEVC, VP9, AV1, FBC, MPBE, AVM, CDEFE, DBR, MPC1, and next-generation SIT/SMP units.

Access type is not encoded by the macro names. Some fields are configuration bits, some may be tied to hardware-owned clock-gating state, and some bit positions are reserved gaps. Consumers must preserve unrelated bits and follow the VCN clock/power sequence before changing these registers, especially around DPG mode and waits for clock-gate readback.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_5_offset.h`, which supplies the corresponding `regUVD_*` offsets and base indexes. The masks are also tied to AMDGPU's SOC15 register access framework and VCN power-management code.

Primary in-tree integration points are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.c`, which includes this file and uses the early `UVD_CGC_*` and aggregate `UVD_SUVD_CGC_*` constants during VCN clock-gating enable/disable and DPG programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.h`, `amdgpu_vcn.h`, `soc15.h`, and `soc15d.h`, which provide the surrounding VCN instance model and register-access helpers.
- Adjacent generated VCN headers such as VCN 4.x and 5.x mask/offset files, which are useful for mechanical diffs and for spotting intentional layout changes in repeated SUVD clock-gating banks.

The generated macro names are a compile-time contract. Missing or renamed symbols usually fail the build. Incorrect numeric shifts or masks can compile successfully but cause the driver to alter the wrong hardware bit, leave clocks enabled, gate an active subblock, or fail an idle/readback wait.

## Risks And Edge Cases

- This is generated hardware metadata. Manual edits or stale generator inputs are high risk because small numeric errors are not type-checked.
- Clock-gating polarity is subtle. In the matching driver, disabling clock gating clears many `UVD_CGC_GATE` bits but sets many `UVD_SUVD_CGC_GATE` bits; consumers must follow the register programming model rather than infer polarity from macro names alone.
- `UVD_CGC_CTRL` combines dynamic-clock enablement, delay timers, and per-block mode bits in one register. Full-register writes can unintentionally alter timing or mode fields; masked read-modify-write is safer where the hardware permits it.
- `SOC15_WAIT_ON_RREG` after clearing `UVD_CGC_GATE` depends on the masks matching actual hardware readback. A bad field can lead to spurious timeout, un-gated clocks, or subsequent initialization while a block is not in the expected state.
- The SUVD gate and control layouts are highly repetitive across many per-subblock registers. Copy/generator drift can affect only a single codec path, such as AV1 encode, VP9 decode, HEVC decode/encode, FBC clocks, or MPBE, and may evade broad boot testing.
- `*_SUVD_CGC_GATE2` introduces second-bank fields that are not covered by older driver paths. Validation needs to include newer VCN 4.0.5 media workloads or register-database comparison, not only legacy H.264/HEVC decode.
- The chunk ends inside `SAOE_SUVD_CGC_CTRL`; final reports must merge with the next chunk before making complete claims about that register or the full control-register set.
- Reserved bit gaps appear in several registers, including gaps between ordinary mode bits and FBC/CDEFE fields. Code must avoid using adjacent mask arithmetic that assumes dense bit coverage.
- DPG-mode writes use indirect SRAM-oriented paths. A wrong mask or shift there can persist into power-gated restore state and fail only after suspend/resume or dynamic power-gating transitions.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with VCN 4.0.5 support so direct include users and macro expansions catch missing or renamed symbols.
- Mechanically compare `vcn_4_0_5_sh_mask.h` lines 1-2276 against the authoritative generated register database and the companion `vcn_4_0_5_offset.h`.
- Verify every field in this range has the expected mask/shift pair, while accounting for the incomplete `SAOE_SUVD_CGC_CTRL` chunk boundary.
- Exercise VCN 4.0.5 clock-gating enable/disable paths, including `vcn_v4_0_5_disable_clock_gating()`, `vcn_v4_0_5_enable_clock_gating()`, and the DPG-mode variant.
- Watch kernel logs and register traces for `SOC15_WAIT_ON_RREG` timeouts, VCN boot failures, failed suspend/resume, ring startup failures after power-gating transitions, and unexpectedly high media-engine power due to clocks not gating.
- Run media workloads that cover decode and encode paths across H.264, HEVC, VP9, AV1, and FBC-related cases so per-codec SUVD gate bits are exercised.
- Diff against neighboring VCN generation headers and implementation files for intentional additions such as `GATE2`, `MPBE*`, `AVM_*`, `SIT_NXT_*`, `SMPN_*`, `MPC1`, and `CDEFE`.

## Cross-Chunk Notes

This is the first chunk for `vcn_4_0_5_sh_mask.h`, so there is no earlier chunk content for the license, include guard, or first registers. The next chunk is required to complete `SAOE_SUVD_CGC_CTRL` and continue the remaining generated register namespace. The merge/reconciliation lane should combine all chunks before producing the final source-tree-aligned per-file report for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_5_sh_mask.h`.
