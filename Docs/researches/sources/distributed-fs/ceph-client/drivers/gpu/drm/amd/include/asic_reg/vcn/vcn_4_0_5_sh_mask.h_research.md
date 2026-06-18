# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_5_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003467`: lines 1-2276, `Docs/researches/chunks/subset-b-003467_research.md`
- `subset-b-003468`: lines 2277-4738, `Docs/researches/chunks/subset-b-003468_research.md`
- `subset-b-003469`: lines 4739-7304, `Docs/researches/chunks/subset-b-003469_research.md`
- `subset-b-003470`: lines 7305-8614, `Docs/researches/chunks/subset-b-003470_research.md`

## Chunk Research

### subset-b-003467: lines 1-2276

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

### subset-b-003468: lines 2277-4738

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_5_sh_mask.h lines 2277-4738

## Scope And Purpose

This chunk is a large middle section of the generated AMD VCN 4.0.5 shift/mask header. It defines C preprocessor constants for the bit layout of VCN/UVD decode-side registers, beginning in the tail of `SAOE_SUVD_CGC_CTRL`, covering most of the core `uvd_uvddec`, `uvd_ecpudec`, `uvd_uvd_mpcdec`, `uvd_uvd_rbcdec`, and `uvd_lmi_adpdec` address blocks, and ending at the `UVD_LMI_PERFMON_COUNT_HI` register heading before that register's field definitions.

The file section is not executable code. Its purpose is to provide a generation-specific hardware ABI map: every `__SHIFT` macro gives a field bit offset, and every `_MASK` macro gives the already-shifted 32-bit field mask. AMDGPU VCN 4.0.5 driver code combines these constants with `vcn_4_0_5_offset.h` register offsets and SOC15 register helpers when programming the decode engine, video command processor, ring buffers, memory interface, interrupts, resets, and clock-gating state.

## Register Field Groups

The opening group covers SUVD clock-gating control registers. The chunk starts inside `SAOE_SUVD_CGC_CTRL`, then defines equivalent field layouts for `SCM_SUVD_CGC_CTRL`, `SDB_SUVD_CGC_CTRL`, `SIT0_NXT_SUVD_CGC_CTRL`, `SIT1_NXT_SUVD_CGC_CTRL`, `SIT2_NXT_SUVD_CGC_CTRL`, `SIT_SUVD_CGC_CTRL`, `SMPA_SUVD_CGC_CTRL`, `SMP_SUVD_CGC_CTRL`, `SRE_SUVD_CGC_CTRL`, `UVD_MPBE0_SUVD_CGC_CTRL`, `UVD_MPBE1_SUVD_CGC_CTRL`, and `UVD_SUVD_CGC_CTRL`. These fields gate or mode-control SUVD subblocks such as `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, `SCLR`, `UVD_SC`, entropy/header paths, `SAOE`, `MPBE0/1`, AV1 paths, `MPC1`, `AVM_0/1`, next-generation SIT common/decode/encode paths, `FBC_PCLK`, `FBC_CCLK`, and `CDEFE`.

Core UVD command and interrupt registers follow. `UVD_GPCOM_VCPU_DATA0/1`, `UVD_GPCOM_SYS_CMD`, and `UVD_GPCOM_SYS_DATA0/1` describe the general-purpose command mailbox between the host/system and VCPU. `UVD_VCPU_INT_EN`, `UVD_VCPU_INT_ACK`, `UVD_VCPU_INT_ROUTE`, `UVD_SUVD_INT_EN`, `UVD_SUVD_INT_STATUS`, `UVD_SUVD_INT_ACK`, `UVD_MASTINT_EN`, `UVD_SYS_INT_EN`, `UVD_SYS_INT_STATUS`, and `UVD_SYS_INT_ACK` define the interrupt enable/status/ack surface for page/interface faults, semaphore timeouts, software ring interrupts, LBSI/UDEC/LMI/SUVD/MPRD/IDCT events, job completion, GPCOM, clock switch, MIF hardware interrupts, and AVM events.

The ring and context group includes `UVD_JOB_DONE`, `UVD_CBUF_ID`, `UVD_CONTEXT_ID`, `UVD_CONTEXT_ID2`, `UVD_NO_OP`, four input ring base/size triplets (`UVD_RB_BASE_LO/HI/SIZE` through `UVD_RB_BASE_LO4/HI4/SIZE4`), one output ring triplet, SR-IOV active-function and mailbox registers, `UVD_RB_ARB_CTRL`, indexed context access via `UVD_CTX_INDEX/DATA`, CXW write/interrupt IDs, MPEG2 decode state, pitch/width/height/picture-count placeholders, MPEG2 control, DXVA buffer sizing, scratch registers, audio ring base/size fields, and secondary SW ring interrupt bits for ring 6.

Status, control, reset, and clock-gating state is represented by `UVD_SUVD_CGC_STATUS2`, second-bank SUVD interrupts, `UVD_STATUS`, `UVD_CNTL`, `UVD_SOFT_RESET`, `UVD_SOFT_RESET2`, `UVD_MMSCH_SOFT_RESET`, `UVD_WIG_CTRL`, `UVD_CGC_STATUS`, `UVD_CGC_UDEC_STATUS`, `UVD_SUVD_CGC_STATUS`, and `UVD_GPCOM_VCPU_CMD`. These registers expose busy/report bits, SUVD enable, reset request and reset-status bits for many UVD/SUVD subblocks, WIG buffer selection, clock-gating status for core and decode pipes, and VCPU-side GPCOM command state.

The `uvd_ecpudec` block maps VCPU cache and non-cache windows. `UVD_VCPU_CACHE_OFFSET0..8` and `UVD_VCPU_CACHE_SIZE0..8` define cached firmware memory windows; `UVD_VCPU_NONCACHE_OFFSET0/1` and `UVD_VCPU_NONCACHE_SIZE0/1` define uncached windows. `UVD_VCPU_CNTL` exposes VCPU error, reset, abort, clock, trace, JTAG, timeout, block reset, runstall, and SRE command-interface reset controls. `UVD_VCPU_PRID`, `UVD_VCPU_TRCE`, `UVD_VCPU_TRCE_RD`, and indirect index/data registers support identification, trace, and indirect VCPU register access.

The `uvd_uvd_mpcdec` block describes the motion/picture cache or MPC programming surface. It includes byte-swap fields for 17 references, luma/chroma search and hit counters, MPC reset/performance/replacement/urgent controls, pitch, mux and ALU setup registers, performance latency counters, and indirect MPC access.

The `uvd_uvd_rbcdec` block defines the ring-buffer controller and semaphore control surface. `UVD_RBC_IB_SIZE`, `UVD_RBC_IB_SIZE_UPDATE`, and `UVD_RBC_RB_CNTL` describe indirect-buffer and ring-buffer sizing/fetch/update controls. `UVD_RBC_RB_RPTR_ADDR`, `UVD_RBC_VCPU_ACCESS`, urgent read priority, write-pointer status and polling registers, semaphore command/address/timeout/control registers, `UVD_ENGINE_CNTL`, `UVD_JOB_START`, `UVD_RBC_BUF_STATUS`, and `UVD_RBC_SWAP_CNTL` together define queue start, semaphore wait/signal behavior, timeout reporting, buffer validity, and endian/swap configuration.

The `uvd_lmi_adpdec` block is the memory-interface and adapter portion. Most of this group is low/high 64-bit BAR field pairs for VCN clients: RE, IT, MP, CM, DB, DBW, IDCT, MPRD S0/S1, MPC, RBC RB/IB, LBSI, VCPU NC0/NC1/cache/cache1-cache8, CENC, SRE, MIF GPGPU/current/ref/DBW/CM colocated/BSP/BSD/SCLR/image-paste/privacy paths, and SPH high bits. It also includes `UVD_LMI_ARB_CTRL2`, cache and non-cache VMID multi-registers, latency control and counters, SPH status, single cache VMID, `UVD_LMI_CTRL2`, urgent controls, `UVD_LMI_CTRL`, `UVD_LMI_STATUS`, `UVD_LMI_PERFMON_CTRL`, and `UVD_LMI_PERFMON_COUNT_LO`.

## Important APIs, Types, And Functions

This chunk exports only preprocessor macros. There are no functions, structs, enums, globals, locks, allocations, or inline helpers. The macro naming convention is the API:

- `<REGISTER>__<FIELD>__SHIFT` is the field shift count.
- `<REGISTER>__<FIELD>_MASK` is the mask at its final bit position.

Consumers normally use these constants through AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, and `SOC15_REG_OFFSET`. For this exact ASIC generation, `vcn_4_0_5_offset.h` supplies offsets such as `regUVD_CGC_CTRL3`, `regUVD_RBC_RB_CNTL`, `regUVD_LMI_CTRL2`, and `regUVD_LMI_PERFMON_COUNT_HI`; this header supplies their bit layouts.

Concrete in-tree consumers include `drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.c`, which uses `UVD_LMI_CTRL2__RE_OFLD_MIF_WR_REQ_NUM__SHIFT` to program RE offload request depth and `UVD_LMI_CTRL2__STALL_ARB_UMC_MASK` to stall or unstall UMC arbitration during VCN setup and teardown. Cross-generation VCN files use the same macro families, but the VCN 4.0.5 offsets and masks must be treated as an ASIC-specific pair.

## Control Flow

The header itself has no runtime control flow; it is a table of constants expanded at compile time. The control flow it supports in driver code is hardware sequencing:

1. Initialize or resume the VCN block by programming clock-gating mode bits, soft-reset controls, VCPU cache windows, LMI BARs, VMIDs, and ring-buffer registers.
2. Start the command/ring path by configuring RBC ring sizing and polling behavior, enabling VCPU/RBC access as needed, and writing job or engine-start command bits.
3. Exchange mailbox commands through GPCOM data/command registers between host/system code and the VCPU firmware.
4. Route and service interrupts by enabling selected VCPU/SUVD/system bits, reading status registers, and acknowledging the matching status bits through the corresponding ack registers.
5. Quiesce or reset the block by stalling LMI arbitration, checking clean/idle/status bits, asserting soft-reset fields, and restoring persistent configuration after reset or power loss.

The field layout encourages paired usage: `*_INT_STATUS` fields should be decoded with their matching status masks and cleared through the corresponding `*_INT_ACK` masks; ring and LMI address halves must be programmed as matching low/high pairs; and reset-status bits should be polled with the masks from the same generation header.

## State And Persistence Behavior

The macros do not store state. They describe hardware register state in the VCN 4.0.5 register file. Configuration fields such as clock-gating modes, ring base/size registers, cache offsets/sizes, LMI BAR low/high pairs, VMIDs, byte-swap controls, urgent controls, and coherency settings persist until the block is reset, power-gated, firmware-reinitialized, or explicitly rewritten by the driver.

Other fields represent transient or latched state. Interrupt status and timeout status bits remain set until acknowledged through the appropriate ack or clear field. `UVD_STATUS`, clock-gating status, reset-status fields, LMI clean/idle state, buffer-valid counters, performance counters, latency counters, and GPCOM request bits are live hardware observations. Command-like fields such as `UVD_JOB_START`, `UVD_ENGINE_CNTL__ENGINE_START`, semaphore commands, reset bits, and interrupt ack bits can have side effects on write.

State split across registers needs careful persistence handling. Low/high BAR pairs are one 64-bit address split over two 32-bit registers; ring and audio ring base/size triplets must remain consistent; VCPU cache offsets/sizes define firmware-visible memory windows; and VMID registers tie those memory windows to GPU virtual-memory context. Suspend/resume, GPU reset, or dynamic power-gating paths must restore the same generation-specific configuration before accepting jobs.

## Dependencies And Integration Points

The immediate dependencies are the generated VCN 4.0.5 companion headers. `vcn_4_0_5_offset.h` maps the register names to addresses and base indices, while this file maps fields to bit positions. Default-value headers, when used by a caller, provide reset defaults. AMDGPU register helpers provide the typed usage pattern around these raw constants.

The primary integration point is the VCN 4.0.5 implementation under `drivers/gpu/drm/amd/amdgpu/`, especially initialization, firmware bring-up, clock/power gating, suspend/resume, reset recovery, ring setup, interrupt handling, and diagnostics. The RBC and LMI fields connect to AMDGPU ring allocation and command submission. GPCOM and VCPU fields connect to firmware command exchange. Interrupt masks connect to the DRM/AMDGPU interrupt handler path. BAR, VMID, coherency, and urgent-control fields connect the video block to GPU memory management and isolation.

This chunk is also part of a cross-generation register family. Similar names appear in VCN 2.x, 3.x, 4.0, and 5.x files, and some legacy UVD headers. That similarity is useful for code sharing, but it is also a risk: the active IP version's offset header and shift/mask header must be included together.

## Risks And Edge Cases

The highest risk is bitfield drift. These values are hardware ABI constants; an incorrect shift or mask can gate the wrong SUVD subblock, acknowledge the wrong interrupt, start or stop the wrong ring behavior, corrupt an LMI address, or leave VCN stuck in reset or arbitration stall.

The chunk boundaries matter. The requested range starts in the middle of `SAOE_SUVD_CGC_CTRL`, so a complete analysis of that register requires the previous chunk. It ends on the `UVD_LMI_PERFMON_COUNT_HI` heading before the `PERFMON_COUNT` field definitions, so complete perfmon high-counter handling requires the next chunk.

Several repeated macro families are easy to misuse. SUVD CGC control registers share similar fields but target different subblocks. `UVD_RB_BASE_LO/HI/SIZE` variants refer to different rings. LMI BAR pairs are numerous and client-specific; crossing low/high halves or programming a BAR for the wrong client can cause memory corruption or firmware faults. `UVD_VCPU_CACHE8` appears before cache2-7 in this chunk's BAR list, which should be preserved as generated rather than "normalized" by hand.

Interrupt and ack semantics are hardware-defined and not encoded in the macro names. Callers must know whether an ack bit is write-one-to-clear/write-one-to-acknowledge and avoid read/modify/write patterns that drop concurrent events. Similarly, reset and start bits may be edge-triggered or have sequencing constraints that are enforced only by the driver and hardware documentation.

Address, VMID, and virtualization fields are security-sensitive. Incorrect VMID or BAR programming can route VCN firmware, ring, or memory-interface traffic through the wrong GPU virtual address space. The SR-IOV active-function and mailbox fields should not be treated as ordinary scratch state.

## Test Signals

Useful validation signals are integration and hardware-facing rather than unit tests for this generated header:

- Kernel build coverage for `vcn_v4_0_5.c` and any files that include `vcn_4_0_5_offset.h` together with `vcn_4_0_5_sh_mask.h`.
- VCN 4.0.5 firmware load and ring bring-up with expected RBC read/write pointer movement and job completion.
- Decode workload tests that exercise the main rings, output ring, audio ring, GPCOM exchange, and interrupt ack paths without stuck status bits.
- Suspend/resume, dynamic power-gating, and GPU reset tests that verify clock-gating, soft-reset, LMI clean/idle, and VCPU cache/window state are restored.
- Fault-injection or negative tests for semaphore timeouts, page/interface faults, unsupported LMI AXI conditions, and system/VCPU/SUVD interrupt routing.
- Memory-management tests that verify LMI BAR low/high pairs, VMIDs, coherency fields, and urgent/stall controls do not cause page faults, data corruption, or isolation violations.
- Performance/diagnostic reads of MPC and LMI counters to ensure perf and latency fields decode as expected for this generation.

### subset-b-003469: lines 4739-7304

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_5_sh_mask.h lines 4739-7304

## Scope

This chunk is a generated register field definition slice for AMD VCN 4.0.5. It does not implement executable code. Instead, it exposes preprocessor constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK` so VCN/JPEG driver code can compose and decode 32-bit MMIO register values without embedding raw bit positions. The slice starts in the late LMI register area, covers JPEG decode/JPEG ring-buffer/JPEG memory-interface blocks, JPEG common interrupt and clock-gating blocks, VCN/UVD power-gating and debug/reporting blocks, VCN ring-buffer doorbell controls, UMSCH scheduler controls, and the beginning of the CPRS64/MES register block.

The companion address header for this generation is `vcn_4_0_5_offset.h`; consumers combine `reg...` offsets from that file with these mask/shift constants and access the hardware through AMDGPU MMIO helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and JPEG DPG-mode write helpers.

## Purpose

The chunk provides the hardware contract for programming and observing VCN 4.0.5 video/JPEG engines. Its constants cover:

- LMI byte-swap, VMID, memory-credit, indirect access, prefetch, and reference-surface BAR fields.
- JPEG decode controls: request enable, error reset, ring-buffer base/read/write pointers, ring size, picture dimensions, chroma/output format, timeout, interrupt enable/status, tier/component/sampling/quantization setup, output buffer pointers, pitch, tiling, address mode, command/data windows, and scratch storage.
- JPEG ring-buffer controller controls: write/read pointers, ring enable, indirect-buffer size, urgent control, conditional-read timers, status, buffer status, preemption command and fence fields, and scratch storage.
- JMI/LMI memory-interface controls for JPEG decode, encode, EJRBC, scalar, JPEG2, atomic writes, preemption fences, 64-bit BAR low/high pairs, VMID routing, swap mode, memory clamping, drop controls, latency/performance counters, clean-status reporting, and RAS error controls.
- JPEG common block controls for soft reset, system interrupts, memcheck interrupts, interrupt handler routing, master interrupt overrun state, arbitration drop controls, clock-gating gate/control/status, memory low-power modes, and performance-bank counters.
- VCN/UVD power-management and debug controls: PGFSM config/status, power status, JPEG power status, DPG local-memory access, DPG pause handshakes, scratch registers, free counter, VCPU cache BAR/VMID, register filtering, PF status, VCPU error address/range/error reporting, address configuration, general-purpose counters, deep-sleep controls, timestamp counter, feature capabilities, GPU IOV status, version, doorbell controls, and ring-pointer controls.
- UMSCH and MES controls: scheduler reset/busy state, AGDB write pointers, mailbox and response registers, UTCL1 controls, interrupt enable/status/ack/source, interrupt handler metadata, force-GPUVM controls, MES program/intr vector registers, pipe priority controls, interrupt/scratch/instruction-pointer state, RISC-like machine status/cause/address/counter/ID registers, cache operation controls, data-cache base/invalidate controls, timer compare, general-purpose state registers, data-memory index access, and local instruction/data aperture base/mask registers.

## Important APIs, Types, And Macros

There are no C types or callable functions in this chunk. The exported API is the macro namespace itself.

Key macro groups:

- `UVD_LMI_*`: local-memory interface fields for byte swapping, VMIDs, credits, prefetching, and 64-bit BAR pieces. These constants are used wherever the VCN block needs to bind GPU virtual memory contexts and memory apertures for firmware, ring, indirect-buffer, or surface traffic.
- `UVD_JPEG_*` and `JPEG_DEC_*`: JPEG decode engine fields. `UVD_JPEG_CNTL__REQUEST_EN_MASK` and `UVD_JPEG_CNTL__ERR_RST_EN_MASK` gate job requests and error reset. Ring pointer and size masks encode 16-byte-aligned values. SPS/tier/output fields describe decoded image geometry, chroma configuration, sampling factors, output pitches, tiling, and command windows.
- `UVD_JRBC_*`: JPEG ring-buffer controller fields. These cover RB/IB state, soft reset, ready/idle/busy status bits, urgent handling, conditional-read timers, preemption command bits (`PREEMPT`, `NO_FENCE`, `PREEMPT_ACK`, `PREEMPT_ON_FENCE`), and fence data.
- `UVD_JMI_*`, `UVD_LMI_J*`, `JPEG_MEMCHECK_*`, and `JPEG_LMI_DROP`: JPEG memory-interface fields. The low/high 64-bit BAR pairs map read/write/preemption/ring/IB/atomic/scalar/JPEG2/fence targets; VMID fields bind those accesses to GPUVM address spaces. Memcheck and clamping masks define bounds-enforcement and error-reporting surfaces.
- `JPEG_SYS_INT_*`, `JPEG_MEMCHECK_SYS_INT_*`, `JPEG_MASTINT_EN`, and `JPEG_IH_CTRL`: interrupt enable/status/ack routing for normal JPEG events and memory check violations. `JPEG_IH_CTRL` provides IH reset/stall/status-clean bits plus VMID, user-data, and ring-id fields sent to the interrupt handler.
- `JPEG_CGC_*` and `JPEG_*_CGC_MEM_CTRL`: clock-gating and memory low-power controls. `jpeg_v4_0_5.c` uses `JPEG_CGC_CTRL__DYN_CLOCK_MODE__SHIFT`, `JPEG_CGC_CTRL__JPEG_DEC_MODE_MASK`, `JPEG_CGC_GATE__JPEG_DEC_MASK`, `JPEG_CGC_GATE__JPEG2_DEC_MASK`, `JPEG_CGC_GATE__JMCIF_MASK`, and `JPEG_CGC_GATE__JRBBM_MASK` to enable and disable JPEG clock gating.
- `UVD_PGFSM_*`, `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `UVD_DPG_*`, and `UVD_IPX_*`-adjacent fields in this range: power-gating, dynamic power-gating, local-memory-access, pause, and power-state observation fields. `vcn_v4_0_5.c` uses `UVD_PGFSM_CONFIG__UVDM_UVDU_PWR_ON` from common VCN declarations together with `UVD_POWER_STATUS__UVD_PG_EN_MASK` and the power-status register.
- `VCN_RB*_DB_CTRL`, `VCN_AGDB_*`, `VCN_RB_ENABLE`, and `VCN_RB_WPTR_CTRL`: doorbell and ring-buffer enable/write-pointer control fields for main VCN rings, JPEG rings, multiple additional RBs, UMSCH, EJPEG, and audio.
- `VCN_UMSCH_*`, `UMSCH_*`, and `UVD_UMSCH_FORCE`: unified micro-scheduler controls for MES pipe selection, reset/busy observation, mailbox communication, AGDB ring write pointers, interrupts, IH context metadata, UTCL1 behavior, and forced GPUVM modes.
- `VCN_MES_*`: MES micro-engine fields, including program-counter/vector start addresses, reset/enable/step/halt/interrupt controls, pipe priority selection, machine interrupt/status/cause/address registers, instruction/data cache operations, timers/counters, general-purpose firmware state, data-memory indexed access, and local aperture configuration.

## Control Flow

This header chunk contains no direct control flow. Runtime control flow is created by driver code that reads a register, masks or shifts selected fields, and writes the updated value back to hardware. Common patterns are:

- Read-modify-write gate control: `jpeg_v4_0_5_disable_clock_gating()` and `jpeg_v4_0_5_enable_clock_gating()` read `regJPEG_CGC_CTRL` and `regJPEG_CGC_GATE`, then set or clear the JPEG/JMCIF/JRBBM masks from this chunk before writing them back.
- Power-gating state transitions: VCN 4.0.5 code writes `regUVD_POWER_STATUS`, waits on DLDO/power-status bits, and uses PGFSM/power-status masks to ensure blocks are powered before programming rings or firmware-visible state.
- Ring programming: ring base, read pointer, write pointer, size, and enable fields are programmed by the VCN/JPEG driver around firmware load, ring startup, command submission, preemption, and teardown. Pointer masks in this chunk enforce hardware alignment and field width.
- Interrupt flow: enable registers select which JPEG or UMSCH events can reach the IH, status registers expose pending bits, and ack registers clear handled bits. `*_IH_CTRL` fields bind interrupt VMID/user-data/ring-id context to the interrupt packet path.
- Memcheck flow: JMI/JPEG memcheck enable/status/ack fields allow high/low range violations on read and write clients to be surfaced and cleared; clamping and safe-address fields determine whether bad accesses are redirected.
- MES/UMSCH firmware flow: mailbox, scratch, program-counter, vector, cache-control, timer, and machine-status fields are observed and controlled by host-side setup, reset, debugging, and recovery paths rather than by ordinary CPU functions in this header.

## State And Persistence

All constants describe volatile hardware state, not persisted kernel data structures. Register values persist only as long as the GPU block retains power and reset state:

- Clock-gating, power-gating, and DPG fields are reset or reinitialized across GPU reset, suspend/resume, power transitions, and IP block bring-up.
- Ring pointers, doorbell controls, and write-pointer control state are live coordination state between the CPU driver, GPU command processor/firmware, and the VCN/JPEG engines. They are not meaningful after ring reset unless reprogrammed.
- VMID and BAR fields bind current GPU virtual-memory contexts and buffer addresses. Incorrect persistence across context switch, GPU reset, SR-IOV partition changes, or firmware restart can point the JPEG/VCN engines at stale memory.
- Scratch, mailbox, machine-status, cause, bad-address, counter, and GP registers provide firmware/debug state. They may be used to diagnose a hang or crash, but they are hardware/firmware state and should not be treated as durable host state.
- Interrupt status and ack registers are edge/state synchronization points. Missing an ack, acking with the wrong mask, or reading stale status can leave the interrupt path wedged or noisy.

## Dependencies

Primary dependencies:

- `vcn_4_0_5_offset.h` for the actual MMIO register offsets corresponding to the `reg...` names.
- AMDGPU SOC15 access helpers (`RREG32_SOC15`, `WREG32_SOC15`, `SOC15_WAIT_ON_RREG`, `SOC15_REG_OFFSET`, and JPEG DPG-mode wrappers) for safe hardware access.
- VCN/JPEG driver implementation files, especially `amdgpu/jpeg_v4_0_5.c` and `amdgpu/vcn_v4_0_5.c`, which include this header directly.
- Firmware and microcode for VCN 4.0.5 (`amdgpu/vcn_4_0_5.bin` in the driver firmware selection path), because many UMSCH/MES/ring/mailbox fields coordinate host setup with firmware behavior.
- AMDGPU power-management, interrupt-handler, GPUVM, ring scheduler, SR-IOV/IOV, and reset/recovery subsystems.

This generated header must remain synchronized with the hardware register specification and with the offset header from the same generation. Mixing masks from one IP version with offsets from another would compile but program the wrong bits.

## Integration Points

Observed local include points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.c` includes `vcn/vcn_4_0_5_offset.h` and `vcn/vcn_4_0_5_sh_mask.h`. It uses this chunk's JPEG clock-gating masks and shifts in the enable/disable and DPG clock-gating paths, along with power-gating status masks from nearby VCN/JPEG register groups.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.c` includes the same offset/mask pair. It uses power-status and PGFSM-related constants during static power-gating setup and reset/bring-up. Other VCN ring, doorbell, scratch, and scheduler constants in the chunk are part of the same IP block programming surface.

Broader integration:

- JPEG decode and encode rings depend on the JPEG/JRBC/JMI register groups to publish ring memory, IB memory, fence memory, output buffers, and preemption state.
- GPUVM and SR-IOV integration depends on the VMID fields (`*_VMID`) and IOV active-function status to route memory accesses and function context correctly.
- Interrupt handling depends on `JPEG_SYS_INT_*`, `JPEG_MEMCHECK_SYS_INT_*`, `JPEG_IH_CTRL`, `VCN_UMSCH_SYS_INT_*`, and `VCN_UMSCH_IH_CTRL` definitions matching IH packet setup and ack semantics.
- Power management depends on `JPEG_CGC_*`, `UVD_PGFSM_*`, `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, DPG pause/LMA, and deep-sleep control fields to avoid register access while blocks are gated or reset.
- Firmware debug/recovery paths depend on UMSCH/MES mailbox, scratch, busy, machine-state, cache-control, and local-aperture fields to inspect or manipulate scheduler state after hangs.

## Risks And Failure Modes

- Bitfield drift: because the file is generated, hand-editing masks or shifts risks silent hardware misprogramming. A wrong bit in a clock/power/reset field can hang the VCN or JPEG engine.
- Version mismatch: VCN 4.0.5 masks are not interchangeable with nearby VCN generations. Some field names are shared across versions but have different client lists or bit positions.
- Alignment and truncation: many ring pointer and BAR fields mask off low bits or split 64-bit addresses into low/high registers. Callers must shift and align addresses exactly as the hardware expects.
- VMID misuse: wrong VMID fields can cause JPEG/JRBC/EJRBC/scalar/atomic clients to access the wrong GPUVM context, causing faults, data corruption, or security issues under SR-IOV or process isolation.
- Interrupt ack mistakes: the enable/status/ack triplets share similar field names. Writing an enable mask to an ack register or failing to clear memcheck/system interrupt bits can create interrupt storms or lost events.
- Power/clock sequencing: accessing JPEG/VCN registers while `JPEG_CGC_*`, `UVD_PGFSM_*`, DPG pause, or DLDO state indicates the block is gated can return stale data or hang bus accesses.
- Memcheck/clamping policy: disabling clamping or programming an unsafe safe address weakens fault containment for bad JPEG/JMI DMA. Conversely, overbroad clamping can hide address-programming bugs until output corruption appears.
- Duplicated/deprecated field names: `VCN_MES_DC_OP_CNTL` contains both `DEPRECATED` and misspelled `DEPRACATED` field macros. Consumers should avoid assigning new semantics without checking the hardware spec.
- Debug register sensitivity: MES machine-state, local aperture, cache invalidation, and data-memory index registers are low-level firmware controls; accidental writes can perturb running scheduler firmware.

## Test Signals

Useful validation signals after changes that touch consumers of these masks:

- Build coverage for `amdgpu/jpeg_v4_0_5.c` and `amdgpu/vcn_v4_0_5.c` with this header included; compile failures catch renamed or missing macros.
- JPEG decode smoke tests on VCN 4.0.5 hardware: successful ring initialization, command submission, output buffer writeback, fence completion, and no `UVD_JPEG_INT_STAT` error bits such as FIFO overflow, timeout, marker/format/profile errors, or block-count sync errors.
- Clock-gating tests: toggling JPEG clock gating should update `JPEG_CGC_GATE`, `JPEG_CGC_CTRL`, and `JPEG_CGC_STATUS` consistently, with no decode regressions after idle/resume.
- Power-gating tests: suspend/resume, runtime power management, static power-gating enable/disable, and GPU reset should return `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, and PGFSM status to expected values before ring use.
- Interrupt tests: JPEG and UMSCH interrupt enable/status/ack paths should produce one handled interrupt per event, clear status after ack, and avoid overrun bits in `JPEG_MASTINT_EN` or `VCN_UMSCH_MASTINT_EN`.
- Memcheck tests: intentionally invalid or boundary GPU addresses, where supported by validation infrastructure, should set the expected `JPEG_MEMCHECK_SYS_INT_STAT` high/low read/write bits and clear through the matching ack masks.
- GPUVM/SR-IOV tests: multiple VMID contexts and VF/PF configurations should verify JPEG/JMI accesses are attributed to the intended VMID/function and do not leak or fault unexpectedly.
- Firmware recovery tests: forced VCN/JPEG hangs or resets should leave useful UMSCH/MES busy/status/cause/bad-address/scratch evidence and recover after cache invalidation/reset sequencing.

### subset-b-003470: lines 7305-8614

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_5_sh_mask.h lines 7305-8614

## Scope And Purpose

This chunk is the final 1,310-line segment of AMD's generated VCN 4.0.5 shift/mask header. It contains C preprocessor constants only: each hardware register field is represented as a `<REGISTER>__<FIELD>__SHIFT` macro and, when present in the generated database, a matching `<REGISTER>__<FIELD>_MASK` macro. It defines no functions, structs, enums, branches, locks, allocations, or direct MMIO access.

The path is under a `ceph-client` source mirror, but this file is AMDGPU media-engine register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU VCN and JPEG code that combines these field constants with register addresses from `vcn_4_0_5_offset.h` and accesses hardware through SOC15 register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `SOC15_REG_OFFSET`, and DPG-mode write helpers.

This chunk starts at the tail of `VCN_MES_LOCAL_INSTR_APERTURE`, after the corresponding `__SHIFT` macro that belongs to the previous chunk. It then covers MES scratch and data apertures, hypervisor decode base/bound registers, MMSCH and UMSCH LMI windows, context-indirect clock/memory controls, software scratch registers, performance/cache diagnostics, LMI arbitration/swap/VMID/coherency controls, memory-latency monitoring, extended non-cache/atomic BARs, memcheck interrupt status/acknowledge fields, and the closing include guard.

## Important APIs, Types, And Macros

The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position used to pack or unpack a hardware field.
- `<REGISTER>__<FIELD>_MASK`: raw bit mask for the same field where the generator emitted one.

Major register families in this chunk:

- MES local memory and interrupt data: `VCN_MES_LOCAL_SCRATCH_APERTURE`, `VCN_MES_LOCAL_SCRATCH_BASE_LO`, `VCN_MES_LOCAL_SCRATCH_BASE_HI`, `VCN_MES_PERFCOUNT_CNTL`, `VCN_MES_PENDING_INTERRUPT`, `VCN_MES_PRGRM_CNTR_START_HI`, and `VCN_MES_INTERRUPT_DATA_16` through `_31`. These describe aperture selectors, scratch base address halves, performance event selection, pending interrupt bits, program-counter start high bits, and 16 generic interrupt data dwords.
- MES data apertures: `VCN_MES_DC_APERTURE0_BASE/MASK/CNTL` through `VCN_MES_DC_APERTURE15_BASE/MASK/CNTL`. Each aperture has a 32-bit base, 32-bit mask, a 4-bit `VMID`, and a `BYPASS_MODE` bit.
- `uvd_vcn_hypdec` decode registers: `VCN_MES_IC_BASE_*`, `VCN_MES_MIBASE_*`, `VCN_MES_IC_BASE_CNTL`, `VCN_MES_DC_BASE_*`, `VCN_MES_MDBASE_*`, `VCN_MES_MIBOUND_*`, and `VCN_MES_MDBOUND_*`. These describe instruction/data base and bound windows, VMID selection, execute-disable, and cache-policy fields for VCN MES/hypervisor decode.
- `uvd_slmi_adpdec` MMSCH/UMSCH LMI registers: `UVD_LMI_MMSCH_NC0_64BIT_BAR_LOW/HIGH` through `NC7`, `UVD_LMI_MMSCH_NC_VMID`, `UVD_LMI_MMSCH_CTRL`, `UVD_MMSCH_LMI_STATUS`, `UMSCH_IOV_ACTIVE_FCN_ID`, and `UVD_UMSCH_LMI_STATUS`. These expose 64-bit non-cache BARs, per-window VMIDs, coherency and VM enablement, read/write/drop mode bits, unsupported AXI transaction status, active VF/PF selection, and scheduler LMI clean indicators.
- `uvdctxind` context-indirect controls: `UVD_CGC_MEM_CTRL`, `UVD_CGC_CTRL2`, `UVD_CGC_MEM_DS_CTRL`, and `UVD_CGC_MEM_SD_CTRL` cover memory light-sleep, deep-sleep, and shutdown enables for LMI/MC, MPC, MPRD, WCB, UDEC subblocks, SYS, VCPU, MIF, LCM, MMSCH, and MPC1, plus memory sleep entry/exit delays and OCLK/RCLK ramp controls. `UVD_SW_SCRATCH_00` through `_15` expose full 32-bit scratch data slots. `UVD_IH_SEM_CTRL` configures interrupt-handler and semaphore stall/clean state, VMID, user data, and ring ID. `UVD_MISC_FEATURE_CTL` controls row preemption and block-interface preemption behavior.
- `uvd_pg_indirect` counters: `UVD_GPCNT0_*` and `UVD_GPCNT1_*` define control, target, and status fields for two general-purpose counters.
- `ecpu_indirect` diagnostics: `UVD_VCPU_CACHE_MISS_COUNTER_CTL`, `UVD_VCPU_ICACHE_MISS_COUNTER`, `UVD_VCPU_DCACHE_MISS_COUNTER`, `UVD_VCPU_ICMISS_ADDR`, `UVD_VCPU_DCMISS_ADDR`, `UVD_VCPU_CACHE_MISS_CTRL1`, `UVD_VCPU_CACHE_MISS_CTRL2`, `UVD_VCPU_INSTR_CACHE_MISS_COUNT`, `UVD_VCPU_CACHE_MISS1` through `_3`, `UVD_VCPU_DATA_CACHE_MISS_COUNT`, and `UVD_LMI_VCPU_EXT40_MODE`. These describe VCPU cache-miss collection, address capture, loop/repeat tracking, reset controls, and 40-bit address mode.
- `lmi_adp_indirect` data-path controls: `UVD_LMI_CRC0` through `_15`, `UVD_LMI_UVD_SWAP_RD`, `UVD_LMI_UVD_SWAP_WR`, `UVD_LMI_VMID_INTERNAL*`, `UVD_LMI_CACHE_CTRL`, `UVD_LMI_ARB_CTRL`, `UVD_LMI_RD_BURST_CTRL`, `UVD_LMI_WR_BURST_CTRL`, `UVD_LMI_WR_COMB_CTRL*`, `UVD_LMI_ISOC_CTRL`, `UVD_LMI_CLEAN_STATUS*`, `UVD_LMI_SCPU_VM*`, `UVD_LMI_SWAP_CNTL2`, and `UVD_LMI_ADDR_EXT2`. These fields govern CRC readback, read/write byte swapping, internal VMID assignment, cache enable/flush, arbitration wait timers, burst sizing, write combining, isochronous prefetch ranges, clean-status bits, SCPU VM ranges, and address-extension bits.
- MIF windows and coherency controls: `UVD_LMI_MIF_BSP*_40BIT_BAR`, `UVD_LMI_MIF_BSD*_40BIT_BAR`, `UVD_LMI_MIF_REF_40BIT_BAR`, `UVD_LMI_MIF_GPGPU_40BIT_BAR`, `UVD_LMI_MIF_DBW_40BIT_BAR`, `UVD_LMI_VCPU_CACHE_40BIT_BAR`, `UVD_LMI_VCPU_NONCACHE_40BIT_BAR0` through `_7`, `UVD_LMI_MIF_RD_SWAP_CNTL*`, `UVD_LMI_MIF_WR_SWAP_CNTL*`, `UVD_LMI_MIF_SWAP_RD`, `UVD_LMI_MIF_SWAP_WR`, `UVD_LMI_MIF_RD_COMB_EN`, `UVD_LMI_DROP`, and `UVD_LMI_MIF_RD_COHERENCY`. These encode decode/writeback/reference/GPGPU/BSP/BSD BARs, swap and privilege/transaction/urgent attributes, read-combine enablement, explicit read/write drop controls, and per-client coherency disable/clean selection.
- Extended addressing, atomics, and latency monitoring: `UVD_LMI_ISOC_PREF_*_64BIT`, `UVD_LMI_PREF_64BIT_BAR_*`, `UVD_LMI_RDCOMB`, `UVD_LMI_MC_LAT_MON0` through `_7`, `UVD_LMI_MC_LAT_CFG0` through `_3`, `UVD_LMI_VCPU_NC2_64BIT_BAR_*` through `NC7`, `UVD_LMI_ATOMIC_USER0_WRITE_64BIT_BAR_*` through `USER3`, and `UVD_LMI_EXT40_MODE`. These describe 64-bit prefetch windows, read-combine timing/bandwidth controls, memory-controller latency histogram bins and configuration, additional VCPU non-cache BARs, atomic write-user BARs, and extended 40-bit LMI mode.
- Memcheck interrupt reporting: `UVD_MEMCHECK2_SYS_INT_STAT`, `UVD_MEMCHECK2_SYS_INT_ACK`, `UVD_MEMCHECK2_VCPU_INT_STAT`, and `UVD_MEMCHECK2_VCPU_INT_ACK`. These define low/high address-range error bits and acknowledge bits for CM, DB, MIF, IDCT, MPC, LBSI, RBC, BSP2, BSP3, SCLR, SCLR2, and PREF clients, with different bit placement between SYS and VCPU status/ack registers for the later clients.

## Control Flow And Runtime Behavior

There is no control flow in this header. Runtime use is indirect:

1. VCN 4.0.5-specific AMDGPU files include `vcn_4_0_5_offset.h` for register addresses and this file for field masks/shifts.
2. The driver initializes and tears down VCN/JPEG instances with SOC15 MMIO helpers, programs firmware/cache/non-cache BARs, configures ring buffers and doorbells, toggles clock/power-gating controls, and waits on status registers.
3. When a register field is narrower than a full register, masks and shifts from this header are used to construct read-modify-write values or to test status bits.

Concrete include users in this tree are `amdgpu/vcn_v4_0_5.c` and `amdgpu/jpeg_v4_0_5.c`. The source chunk's address families also match offsets in `vcn_4_0_5_offset.h`, including `regVCN_MES_DC_APERTURE0_BASE` and `regUVD_LMI_MMSCH_NC0_64BIT_BAR_LOW`. Older UVD generation files show the same style for shared context-indirect names such as `UVD_CGC_MEM_CTRL`: the driver reads `ixUVD_CGC_MEM_CTRL`, adjusts sleep-enable bits, and writes it back through UVD context-register helpers.

## State And Persistence Behavior

The macros hold no software state and persist nothing by themselves. They describe stateful hardware registers whose values remain in VCN/MES/LMI/context-indirect blocks until rewritten, reset, power-gated, or restored during resume and DPG transitions.

State represented by this chunk includes scratch apertures and scratch data, interrupt payloads, DC and instruction/data decode aperture programming, MMSCH and VCPU non-cache BARs, VMID routing, LMI coherency and byte-swap policy, clock-gating memory-sleep policy, scratch mailboxes, performance counter targets and counts, VCPU cache-miss diagnostic counters, CRC and latency-monitor accumulators, read/write clean status, explicit drop controls, 40-bit and 64-bit address-window state, atomic write BARs, and memcheck error/acknowledge latches.

Access type is not encoded by the macro names. Some fields are persistent configuration bits, some are read-only status, some are counters or histogram accumulators, and some are write-one-to-clear or acknowledge fields. Consumers must follow the ASIC programming guide and preserve reserved fields when using full-register writes.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_5_offset.h`, which supplies addresses for the field names in this shift/mask header. It also needs to remain consistent with sibling VCN 4.x/5.x generated headers where the hardware layout is intentionally shared.

Primary functional integration is in AMDGPU VCN/JPEG initialization, suspend/resume, DPG, clock-gating, firmware load, ring setup, and status-wait paths. `vcn_v4_0_5.c` writes VCN firmware cache BARs, VCPU non-cache BARs, LMI control/status fields, clock-gating fields, ring buffer registers, soft reset fields, power status fields, and interrupt enables. `jpeg_v4_0_5.c` includes the same generated header for JPEG-side power, clock, ring, and interrupt setup.

Several macro groups in this chunk are more diagnostic or firmware-facing than directly used by the visible C code. MES apertures, MMSCH/UMSCH NC windows, cache-miss counters, LMI latency histograms, atomic BARs, and memcheck status/ack fields may be programmed by firmware, debug tooling, virtualization paths, or future driver paths. The generated names are still the compile-time contract for any such code.

## Risks And Edge Cases

- The chunk starts mid-register: `VCN_MES_LOCAL_INSTR_APERTURE__APERTURE_MASK` appears here, while its `__SHIFT` definition is in the previous chunk. Final per-file reconciliation should merge the boundary before describing that register as complete.
- Many register groups are repetitive arrays, especially `VCN_MES_DC_APERTURE0` through `_15`, MMSCH `NC0` through `NC7`, scratch `00` through `15`, VCPU non-cache BARs, atomic user BARs, and memcheck bitfields. Copy-generation or offset drift can affect one lane while nearby lanes still work.
- Address-window fields split 40-bit and 64-bit GPU addresses across low/high registers or encode only high-aligned bits. Wrong shifts or masks can point firmware, VCPU, MMSCH, MIF, or atomic traffic at the wrong memory.
- VMID fields control isolation for MES, MMSCH, MIF, SCPU, VCPU, and internal clients. Incorrect VMID packing can cause GPUVM faults, data exposure across virtualization contexts, or firmware-visible address translation failures.
- `BYPASS_MODE`, coherency-disable, cache-enable/flush, byte-swap, privilege, transaction, urgent, and drop fields affect memory ordering and interpretation. Bad constants can present as data corruption, stale reads, endian/swap errors, or hangs under decode workloads.
- Clock-gating memory light-sleep/deep-sleep/shutdown fields touch many media subblocks. Incorrect masks can block power savings or gate RAM while a subblock is still active.
- Status and acknowledge registers such as `UVD_MMSCH_LMI_STATUS`, `UVD_UMSCH_LMI_STATUS`, `UVD_LMI_CLEAN_STATUS*`, `UVD_LMI_MC_LAT_MON*`, and `UVD_MEMCHECK2_*` may be read-only, latched, counter-like, or write-one-to-clear. Treating them as normal writable configuration registers is unsafe.
- The SYS and VCPU memcheck status/ack registers use different bit positions for the BSP/SCLR/PREF tail fields. Reusing one mask set for the other would acknowledge or test the wrong condition.
- Several generated entries have only `__SHIFT` and no `_MASK` in this chunk. Consumers should not infer a full-width mask unless the companion generated database or programming model says so.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with VCN 4.0.5 and JPEG 4.0.5 support so include users and field-helper expressions catch missing or renamed symbols.
- Mechanically compare `vcn_4_0_5_sh_mask.h` against the authoritative generated register database and the companion `vcn_4_0_5_offset.h` address header.
- Check that repetitive register arrays have consistent numbering, masks, and shifts: MES DC apertures, MMSCH NC BARs and VMIDs, scratch registers, VCPU NC BARs, atomic write BARs, latency monitor/config registers, and memcheck status/ack pairs.
- Diff against nearby VCN generated headers (`vcn_4_0_0`, `vcn_4_0_3`, `vcn_5_0_0`, and `vcn_5_3_0`) where parity is expected, while allowing intentional ASIC revisions.
- Runtime exercise should cover VCN firmware loading, VCPU cache and non-cache BAR programming, ring initialization, JPEG ring initialization, suspend/resume, DPG pause/resume, clock-gating mode changes, power-gating transitions, and decode/encode/JPEG workloads under GPUVM.
- Debug or bring-up validation should inspect LMI clean waits, VMID routing, memory coherency, byte-swap behavior, cache-miss counters, MC latency histograms, and memcheck error/ack paths when hardware support and tooling are available.
- Watch for kernel logs reporting VCN firmware boot failures, `SOC15_WAIT_ON_RREG` timeouts, GPUVM faults, ring write-pointer stalls, failed JPEG/VCN idle checks, unexpected memcheck interrupts, and regressions that appear only under virtualization, DPG, suspend/resume, or high memory-pressure media workloads.

## Cross-Chunk Notes

The previous chunk is needed for the start of `VCN_MES_LOCAL_INSTR_APERTURE` and other earlier VCN register groups. This chunk closes the file with the include guard `#endif`, so there is no following `vcn_4_0_5_sh_mask.h` content to merge after it, but the final per-file report should reconcile all chunks before making complete claims about the generated header namespace.
