# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003461`: lines 1-2275, `Docs/researches/chunks/subset-b-003461_research.md`
- `subset-b-003462`: lines 2276-4736, `Docs/researches/chunks/subset-b-003462_research.md`
- `subset-b-003463`: lines 4737-7119, `Docs/researches/chunks/subset-b-003463_research.md`
- `subset-b-003464`: lines 7120-9714, `Docs/researches/chunks/subset-b-003464_research.md`
- `subset-b-003465`: lines 9715-10919, `Docs/researches/chunks/subset-b-003465_research.md`

## Chunk Research

### subset-b-003461: lines 1-2275

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

### subset-b-003462: lines 2276-4736

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_sh_mask.h lines 2276-4736

## Scope And Purpose

This chunk is a generated shift/mask description for the AMD VCN 4.0.3 UVD/VCN register blocks. It is not executable driver logic. Its job is to provide stable C preprocessor names for bit positions and already-shifted masks used by VCN 4.0.3 decode/encode, firmware, interrupt, ring-buffer, clock-gating, reset, and local-memory-interface programming code.

The range starts in the middle of the `SCM_SUVD_CGC_CTRL` field list, then covers the rest of the `aid_uvd0_uvddec` block through `UVD_GPCOM_VCPU_CMD`, the full `aid_uvd0_ecpudec` VCPU cache/control block, the `aid_uvd0_uvd_mpcdec` motion-prediction-cache block, the `aid_uvd0_uvd_rbcdec` ring-buffer-controller/semaphore block, and the start of the `aid_uvd0_lmi_adpdec` local-memory-interface/address-programming block. It ends inside `UVD_LMI_VCPU_CACHE_VMIDS_MULTI`, after the shift fields and the first VMID mask.

The source file pairs with `vcn_4_0_3_offset.h`: the offset header names register addresses such as `regUVD_RB_BASE_LO`, while this header names fields such as `UVD_RB_BASE_LO__RB_BASE_LO_MASK`. VCN 4.0.3 code includes both headers and uses AMDGPU register helpers to compose and decode hardware register values.

## Register Field Groups

The opening CGC control section describes submodule clock-gating mode bits for the secondary UVD path. The repeated `*_SUVD_CGC_CTRL` registers cover blocks including `SCM`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, `SMPA`, `SMP`, `SRE`, `UVD_MPBE0`, `UVD_MPBE1`, and `UVD_SUVD`. Most share the same field layout: one-bit mode fields for `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, `SCLR`, `UVD_SC`, `ENT`, `IME`, `SITE`, `EFC`, `SAOE`, `SMPA`, `MPBE0`, `MPBE1`, `SIT_AV1`, `SDB_AV1`, and `MPC1`, plus newer `AVM_0`, `AVM_1`, and `SIT_NXT_*` fields where applicable. `FBC_PCLK`, `FBC_CCLK`, and `CDEFE_MODE` occupy high bits. `UVD_MPBE0_SUVD_CGC_CTRL` and `UVD_MPBE1_SUVD_CGC_CTRL` are narrower than the fully populated groups and omit some later AVM/SIT_NXT fields.

`UVD_CGC_CTRL3` adds global clock-gating delay and mode controls for `LCM0`, `LCM1`, `MIF`, `VREG`, `PE`, and `PPU`. `UVD_CGC_STATUS`, `UVD_CGC_UDEC_STATUS`, `UVD_SUVD_CGC_STATUS`, and `UVD_SUVD_CGC_STATUS2` later expose clock-active/status bits for SYS/UDEC/MPEG2/REGS/RBC/LMI/IDCT/MPRD/MPC/LBSI/LRBBM/WCB/VCPU/MMSCH plus codec-specific SUVD paths such as H.264, HEVC, VP9, AV1, FBC, SMPA, CDEFE, and SIT0-2.

The GPCOM and firmware-message registers describe mailbox-style communication between host/system code and the VCPU firmware. `UVD_GPCOM_VCPU_DATA0/1` and `UVD_GPCOM_SYS_DATA0/1` are full 32-bit payload fields. `UVD_GPCOM_SYS_CMD` and `UVD_GPCOM_VCPU_CMD` split command words into `CMD_SEND`, a 30-bit `CMD`, and `CMD_SOURCE`. `UVD_DRV_FW_MSG`, `UVD_FW_DRV_MSG_ACK`, and `UVD_VCPU_INT_ROUTE` define driver/firmware message and acknowledgement routing bits.

The interrupt fields cover VCPU, SUVD, encoder, master, and system interrupt paths. `UVD_VCPU_INT_EN`, `UVD_VCPU_INT_STATUS`, and `UVD_VCPU_INT_ACK` use matching low/high layouts for errors and events such as PIF address errors, semaphore timeouts, software ring-buffer interrupts, RBC privilege faults, LBSI/UDEC/SUVD events, read-pointer writes, job start, nested page faults, IDCT/MPRD/AVM/clock-switch/MIF hardware interrupts, and driver/firmware request/ack events. `UVD_VCPU_INT_STATUS` includes `GPCOM_INT` at bit 20, while the enable and ack registers do not expose a matching enable/ack field in this first bank. `UVD_VCPU_INT_STATUS2`, `UVD_VCPU_INT_ACK2`, and `UVD_VCPU_INT_EN2` add `SW_RB6` and `RASCNTL_VCPU_VCODEC`; note that `RASCNTL_VCPU_VCODEC` appears at different bit positions in status, ack, and enable.

`UVD_SUVD_INT_EN`, `UVD_SUVD_INT_STATUS`, and `UVD_SUVD_INT_ACK` define packed function-interrupt fields and one-bit error fields for `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, and `FBC`. The `*_INT_*2` bank extends this for `SMPA` and `SDB_AV1`. `UVD_ENC_VCPU_INT_EN/STATUS/ACK` defines three scan-in buffer-manager interrupt bits. `UVD_MASTINT_EN` gates VCPU and system interrupts and reports interrupt overrun state, while `UVD_SYS_INT_EN/STATUS/ACK` mirrors many VCPU interrupt sources for the system path and adds `CXW_WR`, `JOB_DONE`, `GPCOM`, and `RASCNTL_VCPU_VCODEC` handling.

The ring and context section defines software-visible job identity, no-op, and ring-buffer programming fields. `UVD_JOB_DONE`, `UVD_CBUF_ID`, `UVD_CONTEXT_ID`, `UVD_CONTEXT_ID2`, and `UVD_NO_OP` are simple payload/status registers. `UVD_RB_BASE_LO/HI`, `UVD_RB_SIZE`, and their `2`, `3`, and `4` variants define four input ring buffers; low base fields are aligned at bit 6 and size fields at bit 4. `UVD_OUT_RB_*` and `UVD_AUDIO_RB_*` use the same base/size pattern. `UVD_RB_ARB_CTRL` controls whether SRBM, VCPU, RBC, and firmware-offload paths drop or disable access, and includes fast-path/debug bits. `UVD_CTX_INDEX/DATA`, `UVD_CXW_WR`, `UVD_CXW_WR_INT_ID`, `UVD_CXW_WR_INT_CTX_ID`, and `UVD_CXW_INT_ID` provide indexed context and CXW interrupt metadata.

The decode/control diagnostics include MPEG2 and picture-buffer fields. `UVD_MPEG2_ERROR`, `UVD_YBASE`, `UVD_UVBASE`, `UVD_PITCH`, `UVD_WIDTH`, `UVD_HEIGHT`, `UVD_PICCOUNT`, `UVD_MB_CTL_BUF_BASE`, `UVD_PIC_CTL_BUF_BASE`, and `UVD_SCRATCH_NP` are full-width payload registers. `UVD_MPRD_INITIAL_XY`, `UVD_MPEG2_CTRL`, and `UVD_DXVA_BUF_SIZE` pack screen coordinates, enable/trick-mode/job size, and picture/macroblock buffer sizes. `UVD_CLK_SWT_HANDSHAKE` names clock-switch type and domain bits. `UVD_GP_SCRATCH0` through `UVD_GP_SCRATCH23` are full-width general scratch registers.

The power/reset/status group defines block state and reset controls. `UVD_STATUS` reports RBC busy, VCPU report, RBC GPCOM access, DRM busy, and system GPCOM request. `UVD_ENC_PIPE_BUSY` exposes many encoder datapath busy bits, including IME/SMP/SIT/SDB/ENT/LCM/MDM/EFC/CDEFE/MIF/BSP/BSD/SAOE. `UVD_FW_POWER_STATUS` reports VCPU power state, read/write values, software data, and handshake bits. `UVD_CNTL` holds multiple clock-enable flags, timeout controls, dynamic clock gating and mem power controls, stall bits, and soft-disconnect controls. `UVD_SOFT_RESET`, `UVD_SOFT_RESET2`, `UVD_MMSCH_SOFT_RESET`, and `UVD_WIG_CTRL` define reset request and reset-status bits for RBC, LBSI, LMI, VCPU, UDEC, CXW, TAP, MPC, EFC, IH, MPRD, IDCT, UMC, SPH, MIF, LCM, SUVD, atomic/PPU/MMSCH, AVM/ACAP/WIG, and related clock domains.

The `aid_uvd0_ecpudec` block describes VCPU memory windows and VCPU control. `UVD_VCPU_CACHE_OFFSET0..8` and `UVD_VCPU_CACHE_SIZE0..8` use 21-bit fields. `UVD_VCPU_NONCACHE_OFFSET0/1` use 25-bit offsets and `UVD_VCPU_NONCACHE_SIZE0/1` use 21-bit sizes. `UVD_VCPU_CNTL` defines IRQ error, burst, PMB, reset, abort, clock, trace, debug, JTAG, timeout, block reset, runstall, and SRE command-interface reset fields. `UVD_VCPU_PRID`, `UVD_VCPU_TRCE`, `UVD_VCPU_TRCE_RD`, `UVD_VCPU_IND_INDEX`, and `UVD_VCPU_IND_DATA` provide processor identity, trace, and indirect-index/data access fields.

The `aid_uvd0_uvd_mpcdec` block describes motion-prediction-cache control and instrumentation. `UVD_MP_SWAP_CNTL` provides two-bit MC swap selectors for reference slots 0-15 and `UVD_MP_SWAP_CNTL2` adds reference slot 16. Luma/chroma search, hit, and hit-pending counters are full-width. `UVD_MPC_CNTL` includes block reset, performance selection/reset, replacement mode, debug mux, averaging weight, urgency, speed-up, and test mode fields. The mux/ALU registers (`UVD_MPC_SET_MUXA0/1`, `UVD_MPC_SET_MUXB0/1`, `UVD_MPC_SET_MUX`, `UVD_MPC_SET_ALU`) pack small selector/function fields, and `UVD_MPC_PERF0/1` expose max/average latency fields. `UVD_MPC_IND_INDEX/DATA` implement indirect access.

The `aid_uvd0_uvd_rbcdec` block defines ring-buffer-controller and semaphore fields. `UVD_RBC_IB_SIZE` and `UVD_RBC_IB_SIZE_UPDATE` encode indirect-buffer sizes at bit 4. `UVD_RBC_RB_CNTL` sets ring-buffer size, block size, no-fetch, write-pointer polling, no-update, read-pointer-write enable, and block reset. The remaining RBC fields provide read-pointer address, VCPU access enable, firmware semaphore status, urgent read priority, write-pointer prewrite timing, write-pointer status, write-pointer polling frequency/address, job start, buffer-valid/read/write address status, and MC swap fields. The semaphore registers split request command, write phase, mode, VMID enable/VMID, low/high address pieces, timeout status/clear, semaphore enable, and timeout counter/resend timer fields.

The `aid_uvd0_lmi_adpdec` block begins a long sequence of 64-bit base-address registers. Each low register exposes `BITS_31_0` and each high register exposes `BITS_63_32`, normally with full 32-bit masks. Covered clients include RE, IT, MP, CM, DB, DBW, IDCT, MPRD S0/S1/DBW, MPC, RBC RB/IB, LBSI, VCPU non-cache and cache windows, CENC, SRE, MIF GPGPU, current luma/chroma, references, DBW, CM coloc, BSP0-3, BSD0-4, VCPU cache1-8, SCLR/SCLR2, SPH high, imagepaste luma/chroma, and privacy luma/chroma. `UVD_ADP_ATOMIC_CONFIG` then defines four 4-bit atomic write-cache user fields and a 4-bit atomic read urgency field. `UVD_LMI_ARB_CTRL2` defines wait-enable, max-burst, and read/write request-return limits. The chunk ends at `UVD_LMI_VCPU_CACHE_VMIDS_MULTI`, which packs 4-bit VMIDs for VCPU cache windows 1-8 but only includes the first mask before the line-range boundary.

## Important APIs, Types, And Functions

This chunk exports only C preprocessor constants. There are no C functions, structs, enums, inline helpers, global variables, locks, or allocation paths. The API surface follows the generated AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` is the bit offset to use when inserting or extracting a field.
- `<REGISTER>__<FIELD>_MASK` is the already-positioned 32-bit mask used by `REG_SET_FIELD`, `REG_GET_FIELD`, direct bit tests, or masked writes.

The primary consumers are VCN 4.0.3 driver files that include both `vcn/vcn_4_0_3_offset.h` and `vcn/vcn_4_0_3_sh_mask.h`, especially `drivers/gpu/drm/amd/amdgpu/vcn_v4_0_3.c`. That implementation lists many of the registers in `vcn_reg_list_4_0_3`, programs VCPU cache/LMI base registers during firmware setup, handles IRQ registration, and uses SOC15 register helpers such as `WREG32_SOC15`, `RREG32_SOC15`, and DPG-mode variants. `jpeg_v4_0_3.c` includes the same generated VCN header set for generation-consistent masks and offsets, although its main register use is in JPEG-specific blocks.

## Control Flow

There is no runtime control flow inside the header. The driver control flow implied by these definitions is hardware-programming flow:

1. During VCN initialization or resume, driver code programs clocks, resets, VCPU cache windows, non-cache windows, LMI BARs, ring-buffer bases/sizes, ring-control bits, and interrupt enables using the masks in this chunk.
2. Firmware and hardware exchange messages through GPCOM and driver/firmware message registers; the command/data masks define how the 32-bit words are packed and decoded.
3. During command submission, ring-buffer base, size, pointer, and RBC control fields define how VCPU/RBC fetch work from GPU memory.
4. During interrupts, hardware latches bits in VCPU, system, SUVD, encoder, and second-bank status registers; handlers decode those status registers and write matching ack masks where the hardware expects acknowledgement.
5. During reset, power-gating, DPG, suspend/resume, or error recovery, reset/status/clock-gating fields are polled or rewritten to return VCN blocks to a known state.

The important control-flow constraint is that similarly named enable/status/ack registers are not universally interchangeable. Several banks intentionally have different field coverage or bit positions, for example `GPCOM_INT` exists in status without a first-bank enable/ack field, and `RASCNTL_VCPU_VCODEC` differs across `UVD_VCPU_INT_STATUS2`, `UVD_VCPU_INT_ACK2`, and `UVD_VCPU_INT_EN2`.

## State And Persistence Behavior

The macros themselves hold no state. They describe persistent hardware register state in the VCN block. Ring-buffer base/size registers, VCPU cache and non-cache window registers, LMI 64-bit BARs, clock-gating controls, interrupt enables, reset controls, semaphore controls, and arbitration controls remain programmed until reset, power loss, power-gating, firmware reinitialization, or an explicit driver rewrite.

Status and interrupt registers describe latched or live hardware state. Busy/status fields such as `UVD_STATUS`, `UVD_ENC_PIPE_BUSY`, `UVD_CGC_STATUS`, and `UVD_SUVD_CGC_STATUS*` reflect current hardware activity or clock state. Interrupt status fields can remain asserted until cleared through matching ack bits. Timeout status and semaphore status can also persist long enough to affect later bring-up or job handling if not cleared according to the hardware semantics.

Address fields are particularly persistent and security-sensitive. VCPU cache/non-cache windows and LMI BARs point the VCN firmware and functional subblocks at GPU-visible memory. They must be reprogrammed after GPU reset or VCN power collapse, and they must match the VMID, address alignment, and memory layout expected by firmware and ring setup.

## Dependencies And Integration Points

The direct dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_offset.h`, which supplies the corresponding `reg...` addresses and base-index metadata. The masks are meaningful only when paired with the matching VCN 4.0.3 offsets.

The main integration points are AMDGPU's SOC15 register-access helpers (`RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_DPG_MODE`, `SOC15_REG_OFFSET`, `SOC15_WAIT_ON_RREG`, `REG_SET_FIELD`, `REG_GET_FIELD`) and the VCN/JPEG generation files. `vcn_v4_0_3.c` uses this generated header for firmware memory-window setup, DPG-mode programming, interrupt wiring, debug register listing, ring initialization, and power/reset sequencing. `jpeg_v4_0_3.c` includes the same generation header set and integrates VCN-generation register definitions with JPEG power, interrupt, and ring setup paths.

Firmware integration is central. The VCPU cache/non-cache registers map firmware, stack, context, and shared memory buffers; GPCOM and driver/firmware message registers are mailbox surfaces; interrupt fields route firmware-visible and host-visible events. Ring-buffer and semaphore fields integrate VCN command submission with GPU memory, VMIDs, and synchronization.

The file is generation-specific. Similar `UVD_*` names appear in VCN 4.0.5, VCN 5.x, and older UVD/VCN headers, but field positions and available bits are not guaranteed to match. Code should include and use the header for the active IP version instead of sharing masks across generations by name.

## Risks And Edge Cases

The primary risk is hardware ABI drift or a single incorrect bit value. These constants encode hardware register contracts; a wrong shift or mask can enable the wrong interrupt, fail to clear a latched interrupt, gate the wrong clock, reset the wrong block, misprogram a ring address, or point firmware at the wrong memory window.

Boundary blocks are easy to mishandle in chunked review. This line range begins after the `SCM_SUVD_CGC_CTRL` comment and ends before the complete `UVD_LMI_VCPU_CACHE_VMIDS_MULTI` definition. Any merged per-file document should reconcile the adjacent chunks so partial blocks are not mistaken for incomplete generated code.

The repeated CGC control definitions look mechanically identical, but some blocks intentionally omit newer fields. A reviewer should not "normalize" `UVD_MPBE0_SUVD_CGC_CTRL` or `UVD_MPBE1_SUVD_CGC_CTRL` to the fuller SUVD layout without checking the hardware source.

Interrupt layouts have sparse bits and bank-specific differences. Reusing a mask from an enable register for an ack or status register solely because the field names look similar can be wrong for second-bank or special fields. Acknowledgement registers also depend on hardware write semantics that are not documented by these masks.

Address and size fields have alignment and width constraints. Ring-buffer low base fields drop the low six bits, ring sizes start at bit four, VCPU cache offsets/sizes are 21-bit fields, non-cache offsets are 25-bit fields, and semaphore addresses are split into non-byte-aligned ranges. Callers must pass already-valid hardware addresses and sizes; the masks do not validate them.

Generated headers provide no type safety. All fields are preprocessor constants, so mixing `vcn_4_0_3` masks with a different generation's offsets, using a `_STATUS` mask in a `_CNTL` register, or writing a full-width payload register through the wrong address can compile cleanly and fail only on hardware.

## Test Signals

There are no direct unit tests for this header. Useful validation comes from build, integration, and hardware behavior:

- A kernel build covering `vcn_v4_0_3.c` and `jpeg_v4_0_3.c` catches missing or renamed macros from this generated header.
- VCN firmware load and boot should correctly program `UVD_LMI_VCPU_CACHE*_64BIT_BAR_*`, `UVD_VCPU_CACHE_OFFSET*`, and `UVD_VCPU_CACHE_SIZE*` registers and reach the expected VCPU status.
- Ring tests should submit decode/encode work through all configured rings without stuck `UVD_RBC_RB_CNTL`, bad read/write pointers, or malformed ring base/size programming.
- Interrupt tests should show expected VCPU, system, SUVD, encoder, and second-bank status bits and should clear them with the matching ack registers without interrupt storms.
- Suspend/resume, DPG, power-gating, GPU reset, and recovery tests should reprogram persistent VCN state and observe sane clock-gating/reset status bits.
- Memory-window and VMID-sensitive tests should verify firmware, stack, context, non-cache, semaphore, and LMI BAR programming does not produce page faults, poison interrupts, or data corruption.
- Cross-generation review should verify VCN 4.0.3 code includes `vcn_4_0_3_offset.h` with `vcn_4_0_3_sh_mask.h`, not sibling VCN 4.0.5 or VCN 5.x definitions with similar names.

### subset-b-003463: lines 4737-7119

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_sh_mask.h lines 4737-7119

## Scope And Purpose

This chunk is a large middle section of the generated VCN 4.0.3 shift/mask header for AMDGPU. It starts in the tail of the `UVD_LMI_VCPU_CACHE_VMIDS_MULTI` masks, covers late core VCN/UVD memory-interface fields, then defines the JPEG decode, JPEG memory-interface, JPEG common interrupt/memcheck, JPEG clock-gating/performance, and the beginning of power-gating FSM field layouts.

The file is a hardware register ABI map. It contains only preprocessor constants:

- `<REGISTER>__<FIELD>__SHIFT` gives a bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted 32-bit mask.

There are no functions, structs, allocations, locks, or executable branches in this range. Runtime behavior comes from AMDGPU code that combines these masks with matching VCN 4.0.3 register offsets and helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_DPG_MODE`, `WREG32_P`, `SOC15_REG_OFFSET`, and `SOC15_WAIT_ON_RREG`.

## Register Field Groups

### Late UVD LMI

The first block defines memory-interface fields used by VCN firmware, rings, and decoder/encoder clients:

- VMID selectors for VCPU cache and non-cache windows, including packed multi-VMID fields for cache slots and NC slots.
- LMI latency and performance controls: `UVD_LMI_LAT_CTRL`, `UVD_LMI_LAT_CNTR`, `UVD_LMI_AVG_LAT_CNTR`, `UVD_LMI_PERFMON_CTRL`, and 48-bit-ish counter low/high fields.
- SPH status/address fields and a single-cache `UVD_LMI_VCPU_CACHE_VMID`.
- `UVD_LMI_CTRL2`, including arbitration stalls, UMC urgent controls, CRC controls, read/write ID selection, VCPU NC extension enables, SPU extra CID, RE offload enable and request count, page-fault bypass clearing, and MIF gating.
- `UVD_LMI_URGENT_CTRL` and `UVD_LMI_CTRL`, which expose MC/UMC urgency, write-clean timer, coherency bits, request mode, CRC reset/selection, firmware-fail behavior, per-client data-coherency enables, and MC/UMC block reset bits.
- `UVD_LMI_STATUS`, which reports read/write clean state, raw clean state, VCPU LMI write clean, UMC read/write clean, pending MC writes, UMC idle, ADP read-clean status, BSP write-clean status, and CENC read-clean state.
- VMID fields for RBC ring/IB, MC credit fields, ADP indirect-index/data access, ADP page-fault enables, prefetch control, and MIF reference luma 64-bit BAR low/high fields.
- `VCN_RAS_CNTL` fields for VCPU VCODEC RAS interrupt/PMI enable, rearm, stall, and ready reporting.

These definitions directly support VCN bring-up, shutdown quiesce, cache/BAR programming, virtualization VMID assignment, page-fault behavior, and diagnostics.

### JPEG Decode Core

The `aid_uvd0_uvd_jpeg0_jpegnpdec` and `aid_uvd0_uvd_jpeg_sclk0_jpegnpsclkdec` address blocks map the first JPEG decode engine and its SCLK-side output/layout state. They include:

- `UVD_JPEG_CNTL` request enable, error-reset enable, debug mux, format conversion, VUP mode, timeout, and ROI crop controls.
- JPEG ring-buffer base, write pointer, read pointer, size, decode count, SPS picture width/height, chroma/subformat fields, RE timeout, scratch, and GPCOM command/data registers.
- `UVD_JPEG_INT_EN` and `UVD_JPEG_INT_STAT` bits for output-buffer pointer increments, job available, fence value, FIFO overflow, block count sync, EOI, HFM, reset, ECS marker, timeout, marker, format, profile, format-converter timeout/source/format, and crop-size errors.
- Tier table/control/status fields for component IDs, sampling factors, quantization-table selection, Huffman/table metadata, DRI value, bitstream fetch completion, and decode completion.
- Output-buffer count, write/read pointers, pitch/UV pitch, GFX8 and GFX10 tiling/address configuration, address mode, output XY, and decoder soft reset/status bits.

This is the software-visible contract for JPEG decode queue setup, output surface layout, decode progress reporting, interrupt/error handling, and reset.

### EDCC / RAS Status

The `aid_uvd0_vcn_edcc_dec` block defines repeated correctable and uncorrectable error status layouts:

- Uncorrectable error status pairs for `VIDD`, `VIDV`, and JPEG stream/data memories `JPEG0S/JPEG0D` through `JPEG7S/JPEG7D`.
- A correctable error status pair for `MMSCHD`.

The low registers carry valid flags, address-valid flag, address, and memory id. The high registers carry ECC/parity or other/poison classification, error-info validity and payload, UE/CE/FED counters, reserved bits, and `Err_clr`. These fields are important for RAS reporting and for clearing latched VCN/JPEG memory error state without confusing memory instances.

### JPEG JRBC And JMI

The `aid_uvd0_uvd_jrbc0_uvd_jrbc_dec` block defines the JPEG ring-buffer controller:

- Ring and IB write/read pointers, ring control, ring and IB sizes, remaining IB size, reference data, conditional-read timers, urgent read-priority control, and scratch.
- Soft reset and reset-status bits.
- Status bits for RB/IB job done, illegal command, conditional-register-read timeout, memory read/write timeout, trap status, preemption status, interrupt enable, and interrupt acknowledge.
- JPEG preemption command and fence-data fields.

The `aid_uvd0_uvd_jmi0_uvd_jmi_dec` block maps the JPEG memory interface:

- Page-fault handling gates for JPEG decode.
- JRBC and JPEG LMI controls for read/write arbitration waits, maximum bursts, and swap settings.
- Drop controls for JPEG/JRBC read/write and atomic writes.
- VMID assignment for JRBC IB/RB read/write/memory-read paths, JPEG read/write, atomic user writes, and JPEG preemption.
- 64-bit BAR low/high pairs for preemption fence, JRBC RB/IB, JRBC memory read/write, JPEG read/write, and atomic user writes.
- Decode swap control and atomic control/atomic swap fields.

Together these fields bind JPEG command submission to GPU virtual memory, memory byte ordering, preemption fencing, fault handling, and memory-interface arbitration.

### JMI Common, JPEG Common Interrupts, And Memcheck

The `aid_uvd0_uvd_jmi_common_dec` block adds shared memory-interface and diagnostic fields: MCIF urgent/QoS watermarks, JMI urgent/stall controls, memcheck clamp-to-safe-address control and safe address, JMI latency/performance counters, `UVD_JMI_CLEAN_STATUS` for LMI read/write and per-DJPEG-core clean state, and `UVD_JMI_CNTL` soft reset/read-request return limit.

The `aid_uvd0_uvd_jpeg_common_dec` block defines shared JPEG reset and interrupt routing:

- `JPEG_SOFT_RESET_STATUS` for eight decode cores, eight DJRBC controllers, JPEG encoder, EJRBC, and JMCIF.
- `JPEG_SYS_INT_EN`, `JPEG_SYS_INT_EN1`, `JPEG_SYS_INT_STATUS`, `JPEG_SYS_INT_STATUS1`, `JPEG_SYS_INT_ACK`, and `JPEG_SYS_INT_ACK1` for DJPEG cores, DJRBCs, encoder, EJRBC, JMCIF, and memory/protection interrupt sources.
- `JPEG_MEMCHECK_SYS_INT_EN`, `EN1`, `STAT`, `STAT1`, `STAT2`, and matching `ACK`, `ACK1`, `ACK2` fields. These split high/low read/write error sources across bitstream fetchers, output buffers, DJRBCs, encoder JRBC, pixel fetch, scalar, bitstream writes, and other JPEG memory clients.
- `JPEG_MASTINT_EN`, `JPEG_IH_CTRL`, and `JRBBM_ARB_CTRL` for master interrupt overrun/reset, interrupt-handler VMID/user-data/ring metadata, stall/clean controls, and command-source drop controls.

The status/ack pairs are especially sensitive because they are often used with write-one-to-acknowledge semantics in hardware. The masks name the bits but do not encode the side-effect semantics.

### JPEG Clock Gating, Memory Power, Perf Counters, And Power-Gating FSM Start

The `aid_uvd0_uvd_jpeg_common_sclk_dec` block describes JPEG clock and memory power controls:

- `JPEG_CGC_GATE` gates JPEG0-7 decode blocks, JPEG encoder, JMCIF, and JRBBM.
- `JPEG_CGC_CTRL` selects dynamic clock mode, delay timers, and per-block mode bits.
- `JPEG_CGC_STATUS` reports active VCLK/SCLK for decode cores, encoder, JMCIF, and JRBBM.
- Common, decode, and encoder CGC memory control registers expose light sleep, deep sleep, shutdown, and software-enable bits.
- `JPEG_PERF_BANK_CONF`, event selection, and four count registers support JPEG performance-counter banks.

The chunk then enters `aid_uvd0_uvd_pg_dec` and covers all of `UVD_PGFSM_CONFIG` plus the first shifts of `UVD_PGFSM_STATUS`. `UVD_PGFSM_CONFIG` packs two-bit power configuration fields for many VCN subblocks (`UVDM`, `UVDS`, `UVDF`, `UVDTC`, `UVDB`, `UVDTA`, `UVDLM`, `UVDTD`, `UVDTE`, `UVDE`, `UVDAB`, `UVDJ`, `UVDTB`, `UVDNA`, `UVDNB`). The matching status masks continue after this chunk.

## Important APIs, Types, And Functions

This header chunk exports only macro constants. The important "API" is the generated naming convention consumed by generation-specific AMDGPU code. Examples of integration observed in sibling VCN/JPEG code include:

- `vcn_v4_0_5.c` builds `UVD_LMI_CTRL` values with `WRITE_CLEAN_TIMER`, coherency, request-mode, and urgent masks during VCN start, then programs `UVD_LMI_CTRL2__RE_OFLD_MIF_WR_REQ_NUM__SHIFT` and enables `UVD_MASTINT_EN__VCPU_EN_MASK`.
- VCN shutdown paths wait on `UVD_LMI_STATUS__VCPU_LMI_WRITE_CLEAN_MASK`, `READ_CLEAN`, `WRITE_CLEAN`, and raw clean masks, then set `UVD_LMI_CTRL2__STALL_ARB_UMC_MASK` and wait for UMC raw clean state before reset.
- `jpeg_v4_0_5.c` uses `JPEG_CGC_CTRL__DYN_CLOCK_MODE__SHIFT`, clock-delay shifts, `JPEG_CGC_CTRL__JPEG_DEC_MODE_MASK`, and `JPEG_CGC_GATE` masks to enable/disable JPEG clock gating and DPG clock-gating mode.

The exact file under research is VCN 4.0.3, so consumers must pair these masks with the matching VCN 4.0.3 offset/header set. Same-looking VCN 4.0.5 or VCN 5.x code is useful for behavior inference, but the bit layout is generation-specific.

## Control Flow

There is no control flow in the header itself. Downstream control flow typically follows hardware state-machine sequences:

1. Program VMID, BAR, swap, coherency, arbitration, urgent, page-fault, clock-gating, and memcheck-enable registers.
2. Submit VCN or JPEG work through firmware-visible rings, JRBC RB/IB state, or GPCOM-like command registers.
3. Hardware updates pointer, status, interrupt, clean, latency/perf, and RAS/memcheck registers.
4. Driver interrupt, reset, suspend/resume, or diagnostic paths read status masks, acknowledge latched bits, wait for clean state, stall arbiters, and assert resets as needed.
5. Power/clock gating paths program CGC and PGFSM fields, then poll matching status fields in adjacent registers.

Because this chunk ends inside `UVD_PGFSM_STATUS`, the full PGFSM polling contract spans the next chunk.

## State And Persistence Behavior

The macros do not hold software state. They describe hardware and firmware-visible state in memory-mapped or indirect VCN/JPEG registers.

Persistent configuration state includes VMID mappings, BAR low/high pairs, byte-swap settings, burst/arbitration controls, coherency enables, page-fault gates, memcheck safe address/clamping, interrupt enables, IH metadata, clock-gating modes, memory power modes, performance-counter event selections, and PGFSM power configuration. These values must be restored after hardware reset, power loss, DPG transitions, suspend/resume, or GPU reset.

Transient or latched state includes ring pointers, clean/idle status, JPEG decode/job status, JRBC errors, interrupt status/ack bits, memcheck fault bits, RAS error counters/status, preemption commands/fences, reset-status bits, active-clock status, latency/perf counters, and PGFSM status. Driver code must respect hardware-defined clear and ack semantics; this header only supplies bit positions.

## Dependencies And Integration Points

The immediate dependencies are the other generated VCN 4.0.3 register headers, especially the offset header that provides register addresses and any default-value header that provides reset values. AMDGPU SOC15 access macros and field helpers consume this header to construct register writes and decode reads.

Major integration points are:

- VCN firmware bring-up and teardown: LMI control/status, VMIDs, BARs, interrupts, clean polling, and RAS.
- JPEG decode submission: JPEG core controls, output layout, ring state, interrupts, and decode status.
- JPEG memory isolation: JMI VMID assignment, page-fault gates, memcheck clamping, safe-address registers, and fault status/acknowledge registers.
- Power management: JPEG CGC gate/control/status fields, CGC memory controls, and PGFSM config/status fields.
- Diagnostics and observability: LMI/JMI latency counters, perfmon counters, JPEG performance banks, EDCC/RAS status, and memcheck status.

## Risks And Edge Cases

The central risk is bit-layout drift. These constants encode a hardware ABI, so a wrong shift or mask can enable the wrong interrupt, acknowledge the wrong fault, program the wrong VMID, leave memory traffic unstalled during reset, or gate a block that should remain active.

This chunk contains many repeated per-core and per-source blocks. Copy/paste errors are hard to spot by inspection, especially in `JPEG_MEMCHECK_*`, `VCN_UE_ERR_STATUS_*`, and per-core CGC memory-control fields. Changes should be checked against the authoritative generated register database, not inferred from nearby blocks alone.

Cross-generation reuse is another risk. Names such as `UVD_LMI_CTRL2`, `UVD_LMI_STATUS`, `JPEG_CGC_CTRL`, and `UVD_PGFSM_CONFIG` appear in VCN 4.0.5 and VCN 5.x code, but masks and available fields can differ. Code must include the header matching the active ASIC/IP version.

For status and ack registers, read/modify/write can be unsafe if the hardware uses write-one-to-clear or write-one-to-acknowledge semantics. Callers should write exactly the intended ack masks and avoid carrying stale status bits into unrelated writes.

The final `UVD_PGFSM_STATUS` definition is incomplete in this chunk. Any research or validation of PGFSM behavior must include the following chunk before drawing conclusions about all power-status masks.

## Test Signals

There are no direct unit tests for generated mask headers. Useful validation signals are integration and hardware-facing:

- A kernel build for VCN 4.0.3-capable configurations catches missing or renamed macros in AMDGPU VCN/JPEG code.
- VCN firmware boot, encode/decode smoke tests, and JPEG decode workloads should complete without stuck rings, unexpected interrupts, or VM faults.
- Suspend/resume, runtime power management, DPG, and GPU reset tests should verify that LMI/JMI clean polling, CGC programming, and PGFSM transitions do not time out.
- RAS or memcheck fault-injection diagnostics should report expected `VCN_*_ERR_STATUS_*` and `JPEG_MEMCHECK_*_STAT*` bits and clear them through the matching `ACK*` bits.
- Clock-gating tests should show expected `JPEG_CGC_STATUS` activity and no decode regressions when `JPEG_CGC_GATE`/`JPEG_CGC_CTRL` fields are toggled.
- Review validation should diff this generated chunk against AMD's register source for VCN 4.0.3, with special attention to repeated per-core JPEG fields and the mid-register boundary at `UVD_PGFSM_STATUS`.

### subset-b-003464: lines 7120-9714

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_sh_mask.h lines 7120-9714

## Scope And Purpose

This chunk is a generated AMDGPU VCN 4.0.3 register shift/mask header segment. It has no executable C logic; it exports preprocessor constants that describe bit positions and 32-bit masks for VCN/UVD, JPEG, MMSCH, JRBC, and JMI hardware registers. Driver code combines these macros with the companion `vcn_4_0_3_offset.h` register offsets and SOC15 register access helpers to program video decode/encode, JPEG decode, power management, virtualization, RAS, ring buffer, and memory-interface state.

The range starts in the middle of the `UVD_PGFSM_STATUS` definition, then covers the full `UVD_POWER_STATUS` through `UVD_JMI4_UVD_JMI_ATOMIC_CNTL2` register mask blocks and ends at the first `UVD_JMI5_UVD_JPEG_DEC_PF_CTRL` line. In this line range there are 456 register-name groups and 2,595 source lines, most following the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit shift for a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted field mask.

Because this is generated register ABI surface, the value of the file is correctness and stability rather than local algorithmic behavior.

## Register Groups

The initial UVD power and dynamic power-gating group defines status and control surfaces for VCN block power. `UVD_POWER_STATUS` exposes `UVD_POWER_STATUS`, `UVD_PG_MODE`, `UVD_CG_MODE`, `UVD_PG_EN`, RBC/software ring-buffer snoop disable bits, and `STALL_DPG_POWER_UP`. `UVD_JPEG_POWER_STATUS` mirrors the JPEG side with JPEG power status, JPEG power-gating mode, decode/encode JRBC snoop disable bits, and JPEG DPG stall. These masks are used by VCN and JPEG start/stop paths to toggle static or dynamic power gating and to poll the hardware power state.

The DPG local-memory-access and pause registers describe firmware/SRAM programming windows. `UVD_DPG_LMA_CTL`, `UVD_DPG_LMA_DATA`, `UVD_DPG_LMA_MASK`, and `UVD_DPG_LMA_CTL2` provide read/write selection, masking, auto-increment, SRAM selection, address fields, indirect access data, and 64-bit BAR write controls. `UVD_DPG_PAUSE` has JPEG and non-JPEG request/ack bits. The VCPU cache BAR/offset/VMID registers (`UVD_DPG_LMI_VCPU_CACHE_64BIT_BAR_*`, `UVD_DPG_VCPU_CACHE_OFFSET0`, `UVD_DPG_LMI_VCPU_CACHE_VMID`) describe DPG-visible firmware/cache memory placement.

The general UVD diagnostic and security group includes scratch registers `UVD_SCRATCH1` through `UVD_SCRATCH15` plus `UVD_SCRATCH32`, `UVD_FREE_COUNTER_REG`, `UVD_FW_VERSION`, `UVD_VERSION`, `UVD_REG_FILTER_EN`, and `UVD_SECURITY_REG_VIO_REPORT`. The register-filter bits gate privileged MMSCH, video, and JPEG register access. The violation report bits distinguish host, VCPU, video, DPG, JPEG, and JDPG register violations.

Fault and error handling is represented by `UVD_PF_STATUS`, VCPU error-detection registers, and RAS registers. `UVD_PF_STATUS` has page-fault occurred and clear bits for JPEG, NJ, encoders 0-5, EJPEG, JPEG2, and atomic paths. `CC_UVD_VCPU_ERR*` captures VCPU fault-detection bounds, status, clear, detect enable, TMZ debug disable, reset-on-fault, and faulting instruction address. RAS status registers record poisoned VF/PF state for VCPU/VCODEC, MMSCH, JPEG0, and JPEG1, while `UVD_RAS_CNTL_PMI_ARB` and `VCN_RAS_CNTL_MMSCH` provide status, ack, fatal-error, PMI, rearm, and ready control bits.

Addressing, counters, clocks, and feature-discovery masks include `UVD_GFX8_ADDR_CONFIG`, `UVD_GFX10_ADDR_CONFIG`, `UVD_GPCNT2_*`, `UVD_GPCNT3_*`, `UVD_VCLK_DS_CNTL`, `UVD_DCLK_DS_CNTL`, `UVD_TSC_LOWER`, `UVD_TSC_UPPER`, and `VCN_FEATURES`. `VCN_FEATURES` advertises capabilities such as video decode/encode, MJPEG decode/encode, virtualization, H.264 legacy decode, UDEC, MJPEG2 IDCT, SCLR, VP9, AV1 decode, EFC, EFC HDR-to-SDR, dual MJPEG decode, AV1 encode, and instance ID.

The VCN/JPEG doorbell and ring-buffer group defines JPEG doorbell controls `VCN_JPEG_DB_CTRL1` through `VCN_JPEG_DB_CTRL7`, `VCN_JPEG_DB_CTRL`, `VCN_RB_DB_CTRL`, `VCN_RB1_DB_CTRL` through `VCN_RB4_DB_CTRL`, `VCN_RB_ENABLE`, `VCN_RB_WPTR_CTRL`, UVD ring read/write pointer registers, output/audio/RBC ring pointers, and ring buffer enable fields. These masks encode doorbell offsets, enable bits, read-pointer select fields, doorbell enable state, and active RB lanes.

The MMSCH block starts at address block `aid_uvd0_mmsch_dec`. It defines microcode and SRAM access registers (`MMSCH_UCODE_ADDR/DATA`, `MMSCH_SRAM_ADDR/DATA`, lock bits), VF SRAM/doorbell/context layout registers, MMSCH run/reset/interrupt/control registers, VF context and GPCOM address/size registers, host and per-mailbox request/response registers, non-cache windows, last memory access diagnostics, scratch registers, and GPU IOV scheduling registers for slots 0, 1, and 2. The field names include the generated spelling `FUNCTINO_ID` and `NEXT_FUNCTINO_ID`; consumers must use the generated names exactly.

The `aid_uvd0_slmi_adpdec` block maps MMSCH non-cache local-memory-interface windows. It supplies low/high 64-bit BAR halves for NC0 through NC7, packed 4-bit VMIDs for NC0 through NC7, MMSCH LMI control bits for coherency, VM, privilege, byte swapping, read/write mode, and read/write drop, plus LMI error/status fields for unsupported length, address alignment, write clean, error length/address bits, and read/write clean.

The JRBC address blocks `aid_uvd0_uvd_jrbc1_uvd_jrbc_dec` through `aid_uvd0_uvd_jrbc7_uvd_jrbc_dec` repeat the same command-ring surface for seven JPEG ring-buffer controllers. Each JRBC instance defines RB write/read pointers, RB control (`RB_NO_FETCH`, read-pointer write enable, pre-write timer), IB size, urgent priority, reference data, conditional-read timers, soft reset/status, status interrupt enable/ack and error bits, RB/IB buffer status, IB size update, preemption command/fence data, RB size, and a scratch register.

The JMI address blocks `aid_uvd0_uvd_jmi1_uvd_jmi_dec` through `aid_uvd0_uvd_jmi4_uvd_jmi_dec` repeat the JPEG memory-interface layout for four channels, and the chunk ends at the start of JMI5. Each JMI instance provides JPEG decode page-fault control, LMI controls for JRBC and JPEG paths, drop controls, VMID assignment for IB/RB/JPEG/atomic writes, 64-bit BAR halves for JPEG read/write, JRBC RB/IB, JRBC memory-write, and JPEG preempt fence memory, preempt VMID, byte-swap controls, atomic write controls, and atomic swap controls.

## Important APIs, Types, And Functions

This chunk exports only C macros; it does not define functions, structs, enums, typedefs, variables, or inline helpers. Its effective API is the generated macro namespace consumed by AMDGPU driver code.

The companion offset header provides `reg*` names and base indices. Runtime driver code then uses helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `SOC15_WAIT_ON_RREG`, `SOC15_REG_OFFSET`, `WREG32_SOC15_DPG_MODE`, and `WREG32_SOC15_JPEG_DPG_MODE` to read, write, poll, or DPG-stage the registers. Representative consumers in the tree include `amdgpu/vcn_v4_0_5.c` for VCN power and ring setup, `amdgpu/jpeg_v4_0_5.c` for JPEG power and JRBC setup, later VCN/JPEG generation files that share compatible field names, and MMSCH headers/code that define mailbox response semantics.

## Control Flow

There is no direct control flow in the header. The control flow is implicit in hardware bring-up and teardown paths:

1. VCN or JPEG startup clears or sets anti-hang/power-status fields, enables power-gating mode, configures DPG SRAM or firmware cache windows, and waits for `UVD_POWER_STATUS` or `UVD_JPEG_POWER_STATUS` to reach the expected state.
2. Driver initialization programs address-configuration, doorbell, ring-buffer, BAR, VMID, and byte-swap fields before enabling fetch from VCN or JRBC rings.
3. MMSCH initialization or virtualization paths configure microcode/SRAM access, VF context memory, GPCOM memory, mailboxes, non-cache windows, and GPU IOV command blocks.
4. Runtime command submission advances ring write pointers; hardware updates read pointers, status, job-done bits, buffer state, and preemption/fence state.
5. Error paths inspect page-fault, RAS, VCPU error, security-violation, MMSCH LMI, JRBC status, or JMI drop/status bits and then write corresponding clear/ack bits where the hardware defines write-to-clear behavior.

The repeated JRBC and JMI blocks are intentionally instance-specific. Code must use the register offset for the active instance together with the matching mask names, not derive one channel by applying masks from an unrelated generation.

## State And Persistence Behavior

The macros themselves hold no state. They describe persistent hardware register state in the VCN/JPEG register file. Values survive until overwritten, reset, power-gated away, or reinitialized by firmware/driver resume logic. Power-gating and DPG fields are especially stateful because the driver polls them and uses them to decide when clocks, SRAM access, firmware cache, and rings can be touched safely.

Ring pointer, doorbell, BAR, VMID, and buffer-status fields represent live command processor state. Driver-side mirrors such as ring write pointers must remain coherent with hardware read/write pointer fields. After GPU reset, suspend/resume, or VCN/JPEG power loss, these fields need normal IP block reprogramming.

Fault, RAS, security, and JRBC status bits are latched diagnostic state. Many have paired clear or ack bits, but this header only names the bits; it does not encode side-effect semantics. Callers must preserve hardware-defined write-one-to-clear or write-one-to-ack behavior and avoid read/modify/write patterns that accidentally clear unrelated latched faults.

MMSCH and GPU IOV fields carry virtualization state: active VF/PF identifiers, mailbox contents, command-control words, VM busy status, context location/size, and active-function state. In SR-IOV or multi-instance configurations, stale values can affect scheduling ownership and isolation until the MMSCH path resets or explicitly reprograms them.

## Dependencies And Integration Points

The immediate dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_offset.h`, which supplies the register offsets and base indices for this generation. The masks are only meaningful when paired with the VCN 4.0.3 offsets and the correct IP instance.

AMDGPU integration points include:

- VCN power management and DPG mode in `drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.c`, which uses `UVD_POWER_STATUS` masks to enable/disable power gating and poll readiness.
- JPEG power and ring setup in `drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.c`, which uses `UVD_JPEG_POWER_STATUS` masks and JRBC register programming.
- Register dumps and diagnostics through `SOC15_REG_ENTRY_STR` tables, where stable register names make MMIO state observable.
- SR-IOV/MMSCH control code and headers, where mailbox response values, VF context memory, and GPU IOV scheduling registers bridge host driver state to the multimedia scheduler.
- RAS, page-fault, and reset paths, where poisoning, fault, status, clear, and ack bits provide hardware evidence for recovery decisions.

The file is also cross-generation aligned with VCN 4.x and 5.x headers. Similar register names appear in sibling headers, but offsets, available instances, and some bit layouts can differ. This chunk should therefore be treated as VCN 4.0.3-specific hardware description, not as a generic VCN contract.

## Risks And Edge Cases

The main risk is bit-layout drift. A wrong shift or mask can set the wrong hardware field, leave a block powered off, enable the wrong ring, corrupt VMID/BAR programming, mis-handle a page fault, or acknowledge the wrong error. This is particularly risky in dense packed fields such as `UVD_PGFSM_STATUS`, `VCN_RB_ENABLE`, `VCN_RB_WPTR_CTRL`, MMSCH GPU IOV command-control words, `UVD_LMI_MMSCH_NC_VMID`, and JMI swap/VMID registers.

Generated repetition is another risk. JRBC1-7 and JMI1-4 are structurally identical but must stay instance-specific. Copying masks across instances or normalizing the generated `FUNCTINO_ID` spelling would break builds or silently target the wrong register symbols.

Power-management ordering is fragile. Code using `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, DPG LMA, clock deep-sleep, and pause request/ack fields must respect hardware sequencing; touching SRAM, BARs, or rings while the block is stalled, gated, or not yet acknowledged can produce hangs.

Fault and RAS clear bits need side-effect awareness. The header exposes `*_CLEAR`, `*_ACK`, and status masks but cannot tell whether a write clears, arms, re-arms, or merely reports state. Driver changes should be checked against hardware documentation or existing generation code before changing read/modify/write behavior.

Virtualization and security fields affect isolation. Misprogrammed MMSCH VMIDs, VF context addresses, non-cache BARs, register filters, or GPU IOV active-function fields can route memory transactions to the wrong VMID or expose privileged multimedia registers to the wrong client.

## Test Signals

Build coverage should catch missing macro names in VCN/JPEG/MMSCH users, especially when the generated names are referenced by `vcn_v4_0_5.c`, `jpeg_v4_0_5.c`, debug register tables, or generation-specific headers.

Runtime validation should focus on hardware-facing behaviors:

- VCN and JPEG start/stop in static and dynamic power-gating modes complete without `SOC15_WAIT_ON_RREG` timeouts on `UVD_POWER_STATUS` or `UVD_JPEG_POWER_STATUS`.
- Suspend/resume and GPU reset restore DPG SRAM, firmware cache, BAR, VMID, doorbell, and ring pointer state.
- Video decode/encode and JPEG decode command rings advance write/read pointers and report job completion without JRBC illegal-command, memory-timeout, or preemption-status faults.
- SR-IOV or GPU IOV workloads show expected MMSCH mailbox responses, active VF IDs, VM busy state, and context sizes without cross-VF leakage.
- Fault-injection or error-reporting tests surface expected `UVD_PF_STATUS`, VCPU error, RAS poisoned VF/PF, security-violation, and MMSCH LMI status bits and clear only the intended latched conditions.
- Register-dump comparisons against AMD-generated headers or hardware specs confirm that VCN 4.0.3 offsets are paired with VCN 4.0.3 shift/mask values rather than sibling generation values.

### subset-b-003465: lines 9715-10919

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_sh_mask.h lines 9715-10919

## Scope And Purpose

This chunk is the tail of the generated VCN 4.0.3 shift/mask header for AMDGPU's VCN/UVD hardware block. It provides C preprocessor constants for register fields rather than executable code. The constants describe how to pack and decode 32-bit register values for three repeated JPEG/JMI decode address blocks, context-indirect VCN clock-gating and scratch registers, LMI adapter indirect CRC and byte-swap controls, and memory-check interrupt status/acknowledge registers.

The chunk begins at the end of the `aid_uvd0_uvd_jmi5_uvd_jmi_dec` block, then contains complete `aid_uvd0_uvd_jmi6_uvd_jmi_dec` and `aid_uvd0_uvd_jmi7_uvd_jmi_dec` blocks. It then switches to `uvdctxind` and `lmi_adp_indirect` address blocks before closing the header guard. The companion offset header `vcn_4_0_3_offset.h` supplies the register offsets, while this file supplies the field positions and masks used by driver register helpers.

There are no functions, structs, enums, or local variables here. The practical API is a hardware description contract: driver code can include this generation-specific header and use symbolic field names such as `UVD_JMI7_UVD_JMI_ATOMIC_CNTL__ATOMIC_SW_GATE_MASK` or `UVD_MEMCHECK2_SYS_INT_STAT__PREF_HI_ERR_MASK` instead of open-coded shifts.

## Register Field Groups

The `UVD_JMI5`, `UVD_JMI6`, and `UVD_JMI7` groups describe per-JPEG/JMI decoder memory-interface controls. Each block has the same shape: JPEG decoder prefetch control, JRBC and JPEG LMI arbitration controls, drop controls, VMID assignment registers, 64-bit BAR low/high halves for ring buffers, indirect buffers, JPEG read/write, preempt fences, and atomic write targets, plus JMI decode swap and atomic control registers. Common fields include `ARB_RD_WAIT_EN`, `ARB_WR_WAIT_EN`, read/write max burst fields, `RD_SWAP`/`WR_SWAP`, JPEG/JRBC read and write drop bits, VMID nibbles for command and memory traffic, and 32-bit halves of 64-bit addresses.

The JMI decode swap fields are two-bit memory-controller swap controls for ring-buffer, indirect-buffer, memory-read, memory-write, preempt, and JPEG traffic. The atomic control fields cover arbitration wait, maximum burst, write drop, write clamping, urgency, software gating, UVD-side swap, and memory-controller swap. Because these three blocks are parallel instances, consumers should treat the numeric instance prefix as part of the register identity and not collapse them into one shared macro set.

The `uvdctxind` group defines context-indirect control registers. `UVD_CGC_MEM_CTRL`, `UVD_CGC_MEM_DS_CTRL`, and `UVD_CGC_MEM_SD_CTRL` expose light-sleep, deep-sleep, and shutdown enables for VCN subblocks such as LMI_MC, MPC, MPRD, WCB, UDEC_RE/CM/IT/DB/MP, SYS, VCPU, MIF, LCM, MMSCH, and MPC1. `UVD_CGC_MEM_CTRL` also includes `LS_SET_DELAY` and `LS_CLEAR_DELAY` timing fields. `UVD_CGC_CTRL2` controls dynamic OCLK/RCLK ramp behavior and the gater divider. `UVD_SW_SCRATCH_00` through `UVD_SW_SCRATCH_15` are full-width scratch registers with a single `DATA` field. `UVD_IH_SEM_CTRL` defines interrupt-handler and semaphore stall/clean bits plus `IH_VMID`, `IH_USER_DATA`, and `IH_RINGID` metadata fields.

The `lmi_adp_indirect` group starts with `UVD_LMI_CRC0` through `UVD_LMI_CRC15` register definitions. Each CRC register exposes one full-width `CRC32` field and is intended for LMI data-path validation or diagnostics. `UVD_LMI_SWAP_CNTL2` then defines two-bit swap controls for SCPU read/write, CENC, and FBC key traffic, plus a wider `ATOMIC_MC_SWAP` field.

The memory-check groups describe error enable, status, and acknowledge bit layouts for system-visible and VCPU-visible VCN memory-check paths. `UVD_MEMCHECK_SYS_INT_EN` and `UVD_MEMCHECK_VCPU_INT_EN` use one enable bit per source, spanning base decoder clients (`RE`, `IT`, `MP`, `DB`, `DBW`, `CM`, `MIF_REF`, `VCPU`, `MIF_DBW`, `MIF_CM_COLOC`, `MIF_BSP0`, `MIF_BSP1`, `SRE`, `IT_RD`) and extended read/client sources (`CM_RD`, `DB_RD`, `MIF_RD`, `IDCT_RD`, `MPC_RD`, `LBSI_RD`, `RBC_RD`, `MIF_BSP2`, `MIF_BSP3`, `MIF_SCLR`, `MIF_SCLR2`, `PREF`). The first-generation status and ack registers expose low/high pairs for the base sources. The `UVD_MEMCHECK2_*` registers expose low/high pairs for the extended read/client sources.

An important layout detail is that `UVD_MEMCHECK2_SYS_INT_STAT` and `UVD_MEMCHECK2_SYS_INT_ACK` place `MIF_BSP2` and later fields at bits 22 through 31, while `UVD_MEMCHECK2_VCPU_INT_STAT` and `UVD_MEMCHECK2_VCPU_INT_ACK` place those same named sources at bits 18 through 27. This generation-specific asymmetry is part of the hardware ABI and should not be normalized by shared helper code.

## Important APIs, Types, And Functions

This chunk exports only macros of the generated AMD register form:

- `<REGISTER>__<FIELD>__SHIFT` is the shift count for the field.
- `<REGISTER>__<FIELD>_MASK` is the already-shifted 32-bit mask for the field.

The macros are normally paired with offsets from `vcn_4_0_3_offset.h`, including `regUVD_JMI5_*`, `regUVD_JMI6_*`, and `regUVD_JMI7_*` entries for the JMI decode blocks and `ixUVD_CGC_MEM_CTRL`, `ixUVD_SW_SCRATCH_00` through `ixUVD_SW_SCRATCH_15`, `ixUVD_IH_SEM_CTRL`, `ixUVD_LMI_CRC*`, `ixUVD_MEMCHECK_SYS_INT_EN`, `ixUVD_MEMCHECK_SYS_INT_STAT`, `ixUVD_MEMCHECK_SYS_INT_ACK`, `ixUVD_MEMCHECK_VCPU_INT_EN`, `ixUVD_MEMCHECK_VCPU_INT_STAT`, `ixUVD_MEMCHECK_VCPU_INT_ACK`, `ixUVD_MEMCHECK2_SYS_INT_STAT`, `ixUVD_MEMCHECK2_SYS_INT_ACK`, `ixUVD_MEMCHECK2_VCPU_INT_STAT`, and `ixUVD_MEMCHECK2_VCPU_INT_ACK`.

No type checking is provided by the header. Callers must use the masks with the correct offset, instance, and register-access path. Full-width `0xFFFFFFFFL` fields identify registers where the entire 32-bit value is payload, such as scratch data, CRC32 values, and low/high halves of 64-bit BAR addresses.

## Control Flow

There is no runtime control flow in this file. Runtime flow exists in the driver and firmware-facing paths that consume these masks:

1. VCN initialization or resume code programs clock-gating, memory light-sleep/deep-sleep/shutdown, swap, VMID, BAR, and atomic behavior by composing register values from these masks.
2. Command submission and JPEG/JRBC paths use the JMI instance registers to point hardware at ring buffers, indirect buffers, JPEG read/write buffers, preempt fences, and atomic write memory.
3. Hardware sets memory-check status bits when protected memory clients report low/high or source-specific faults.
4. Interrupt, diagnostic, or recovery code reads the matching status register, decodes the active bits with this header's masks, and writes the corresponding ack register bits to clear or acknowledge latched state.
5. Scratch and CRC registers provide side channels for firmware/driver handoff or data-path checking, depending on the active VCN firmware and test mode.

The status and ack registers are intentionally paired within each bank, but fields should not be copied between `SYS`, `VCPU`, `MEMCHECK`, and `MEMCHECK2` banks without checking the exact mask definitions.

## State And Persistence Behavior

The macros themselves persist no state. They describe hardware state in VCN memory-mapped or indirect registers. BAR low/high registers persist programmed addresses until rewritten or until the VCN block is reset or power-gated. VMID, swap, arbitration, burst, drop, prefetch, atomic, and clock-gating fields similarly represent live hardware configuration and must be restored during block bring-up, suspend/resume, GPU reset, or power-management transitions that lose register state.

Memory-check status bits are latched hardware error state. They remain visible until the appropriate acknowledge path is used, subject to the hardware's write-acknowledge semantics. Interrupt enable bits determine which sources can signal the system or VCPU paths and are distinct from the status bits. Scratch registers are mutable firmware/driver state and should be treated as volatile across reset or firmware reinitialization unless a higher-level protocol explicitly preserves them.

## Dependencies And Integration Points

The direct dependency is the companion VCN 4.0.3 offset header in the same directory. It maps the symbolic register names to offsets and base-index metadata; this shift/mask header completes the register description. Both headers are generated hardware description inputs used by AMDGPU IP-version code through SOC15/AMDGPU register access helpers.

Integration points include VCN 4.x block initialization, JPEG ring setup, command processor/JRBC setup, preemption fence programming, VMID/address programming, power and clock-gating code, memory-check interrupt handling, GPU reset, suspend/resume, and diagnostic register dumping. Similar field names appear in VCN 4.0.0, VCN 3.x, and older UVD headers, but those sibling headers are generation-specific and can differ in instance count, bit positions, or subblock names.

The `uvdctxind` and `lmi_adp_indirect` address blocks imply indirect access paths rather than ordinary direct MMIO in all contexts. Driver code must use the register helper appropriate for the offset namespace; using a direct helper with an indirect offset, or mixing a JMI direct register offset with an indirect `ixUVD_*` offset, would program the wrong hardware location.

## Risks And Edge Cases

The main risk is hardware ABI drift. A single wrong shift or mask can route a JPEG/JRBC memory transaction through the wrong VMID, program a bad BAR half, swap data incorrectly, drop reads or writes unexpectedly, or acknowledge the wrong memory-check source. The repeated JMI5/JMI6/JMI7 blocks are visually similar, which makes copy/paste or generated-source errors hard to spot by inspection.

The memory-check layouts have sparse fields and bank-specific differences. In particular, extended `MEMCHECK2` system and VCPU status/ack registers do not use identical high-bit layouts for all sources. Generic helper code should use bank-specific masks rather than deriving one bank from another.

Clock-gating and memory sleep/shutdown masks are power-management sensitive. Enabling the wrong subblock sleep field or using the wrong delay field can cause hangs, lost firmware communication, or wakeup timing problems that may only reproduce under runtime power management, suspend/resume, or reset stress.

Ack register writes may have side effects such as write-one-to-clear or write-one-to-acknowledge behavior; this header names the bits but does not document the write semantics. Read/modify/write patterns should be checked against the hardware programming guide or existing AMDGPU usage.

## Test Signals

There are no direct unit tests for this generated header. Useful validation signals are hardware and integration oriented:

- A kernel build for AMDGPU VCN 4.0.3 users catches missing or renamed macros and include mismatches.
- VCN/JPEG firmware bring-up, ring tests, decode tests, and preemption tests should pass without ring buffer address, VMID, or swap-related failures.
- Runtime power management, suspend/resume, and GPU reset tests should verify that clock-gating and memory sleep/shutdown state is restored and does not cause VCN hangs.
- Memory-check fault injection or diagnostic tests should show expected bits in `UVD_MEMCHECK*_INT_STAT` and clear them through the matching `UVD_MEMCHECK*_INT_ACK` masks.
- Register dumps compared against AMD's generated register specification should preserve the JMI5/JMI6/JMI7 instance separation and the `MEMCHECK2` system-versus-VCPU bit-position differences.
