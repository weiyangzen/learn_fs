# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003456`: lines 1-2275, `Docs/researches/chunks/subset-b-003456_research.md`
- `subset-b-003457`: lines 2276-4740, `Docs/researches/chunks/subset-b-003457_research.md`
- `subset-b-003458`: lines 4741-7291, `Docs/researches/chunks/subset-b-003458_research.md`
- `subset-b-003459`: lines 7292-8937, `Docs/researches/chunks/subset-b-003459_research.md`

## Chunk Research

### subset-b-003456: lines 1-2275

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

### subset-b-003457: lines 2276-4740

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_0_sh_mask.h lines 2276-4740

## Scope

This chunk covers a large middle section of AMD's generated VCN 4.0.0 shift/mask header. It starts at the first field macro inside the `SCM_SUVD_CGC_CTRL` register layout and continues through the first `UVD_LMI_SPH__ADDR__SHIFT` definition. The range is declarative register ABI data only: every meaningful item is a preprocessor constant naming a hardware register field shift or mask. There are no C functions, structs, variables, branches, allocations, locks, or direct MMIO operations in this chunk.

The covered register families span several VCN/UVD sub-blocks:

- SUVD clock-gating control fields for `SCM`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, `SMPA`, `SMP`, `SRE`, `UVD_MPBE0`, `UVD_MPBE1`, and `UVD_SUVD`.
- Top-level VCN/UVD command, interrupt, firmware-message, job, context, ring-buffer, scratch, reset, clock-status, and power/status field layouts.
- `uvd0_ecpudec` VCPU cache, non-cache, control, trace, and indirect-access fields.
- `uvd0_uvd_mpcdec` motion/picture-cache control, byte-swap, mux/ALU, performance, and indirect-access fields.
- `uvd0_uvd_rbcdec` ring-buffer controller, write-pointer polling, semaphore, engine-start, timeout, and buffer-status fields.
- The opening of `uvd0_lmi_adpdec`, including many low/high 64-bit base-address register fields for VCN decoder clients, atomic/cache policy controls, arbitration controls, VMID packing, latency counters, and the first field of `UVD_LMI_SPH`.

The range has partial boundaries. The `SCM_SUVD_CGC_CTRL` comment is immediately before the mapped first line, and the `UVD_LMI_SPH` register is only partially included: this chunk contains the register comment and `ADDR__SHIFT`, while the status shifts and masks are in the following lines outside the requested range. The later merge/reconciliation lane should combine adjacent chunk reports before treating either boundary register as fully documented.

## Purpose

The purpose of this header section is to give the VCN 4.0.0 driver exact bit positions for programming and decoding hardware registers. Each complete field normally appears as:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit for the field.
- `<REGISTER>__<FIELD>_MASK`, the raw 32-bit mask for isolating or composing the field.

The companion `vcn_4_0_0_offset.h` file supplies register addresses such as `regUVD_VCPU_CNTL`, while this file supplies the field layout. Runtime VCN code includes both headers and uses AMDGPU/SOC15 helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_WAIT_ON_RREG`. For example, `vcn_v4_0.c` uses masks from this chunk to unblock or block VCPU register access through `UVD_RB_ARB_CTRL__VCPU_DIS_MASK`, reset and clock the firmware CPU through `UVD_VCPU_CNTL__BLK_RST_MASK` and `UVD_VCPU_CNTL__CLK_EN_MASK`, program MPC mux fields through `UVD_MPC_SET_MUX*` shifts, and stall LMI UMC arbitration through `UVD_LMI_CTRL2__STALL_ARB_UMC_MASK`.

Because this is a generated hardware contract, the most important behavior is not local code execution but bit-accurate agreement between software and silicon. A wrong shift or mask can make otherwise correct driver code touch the wrong reset bit, clear the wrong interrupt source, expose an incorrect ring buffer base, or program an invalid VMID/cache policy.

## Important Macro Families

### SUVD Clock-Gating Control

The range begins with repeated `*_SUVD_CGC_CTRL` layouts for VCN decode and encode submodules:

- `SCM_SUVD_CGC_CTRL`
- `SDB_SUVD_CGC_CTRL`
- `SIT0_NXT_SUVD_CGC_CTRL`, `SIT1_NXT_SUVD_CGC_CTRL`, and `SIT2_NXT_SUVD_CGC_CTRL`
- `SIT_SUVD_CGC_CTRL`
- `SMPA_SUVD_CGC_CTRL` and `SMP_SUVD_CGC_CTRL`
- `SRE_SUVD_CGC_CTRL`
- `UVD_MPBE0_SUVD_CGC_CTRL` and `UVD_MPBE1_SUVD_CGC_CTRL`
- `UVD_SUVD_CGC_CTRL`

Most of these registers expose the same mode bits for sub-block clock gating: `SRE_MODE`, `SIT_MODE`, `SMP_MODE`, `SCM_MODE`, `SDB_MODE`, `SCLR_MODE`, `UVD_SC_MODE`, `ENT_MODE`, `IME_MODE`, `SITE_MODE`, `EFC_MODE`, `SAOE_MODE`, `SMPA_MODE`, `MPBE0_MODE`, `MPBE1_MODE`, AV1-specific `SIT_AV1_MODE` and `SDB_AV1_MODE`, `MPC1_MODE`, `AVM_0_MODE`, `AVM_1_MODE`, next-generation SIT common/decode/encode modes, and high bits for `FBC_PCLK`, `FBC_CCLK`, and `CDEFE_MODE`. These masks are used when power-management code enables or disables fine-grained clock gating for codec sub-blocks.

`UVD_CGC_CTRL3` extends clock-control coverage with `CGC_CLK_OFF_DELAY` plus LCM, MIF, VREG, PE, and PPU mode bits. The paired status registers later in the chunk expose whether the relevant clock domains are active or gated.

### Command and Firmware Messaging

`UVD_GPCOM_VCPU_DATA0`, `UVD_GPCOM_VCPU_DATA1`, `UVD_GPCOM_SYS_DATA0`, and `UVD_GPCOM_SYS_DATA1` are full-width data payload registers. `UVD_GPCOM_SYS_CMD` and `UVD_GPCOM_VCPU_CMD` define a common command layout: `CMD_SEND` at bit 0, `CMD` across bits 30:1, and `CMD_SOURCE` at bit 31. These fields underpin host-to-firmware and firmware-to-host command exchange, but this header does not define command opcodes or handshake ordering.

`UVD_DRV_FW_MSG` and `UVD_FW_DRV_MSG_ACK` are full-width message/acknowledgement registers. They are integration points between the kernel driver and VCN firmware; correctness depends on the caller following firmware ABI sequencing and timeout rules outside this header.

### Interrupt Enable, Status, Acknowledge, and Routing

The chunk defines several mirrored interrupt families:

- `UVD_VCPU_INT_EN`, `UVD_VCPU_INT_STATUS`, and `UVD_VCPU_INT_ACK`.
- `UVD_SUVD_INT_EN`, `UVD_SUVD_INT_STATUS`, and `UVD_SUVD_INT_ACK`.
- `UVD_ENC_VCPU_INT_EN`, `UVD_ENC_VCPU_INT_STATUS`, and `UVD_ENC_VCPU_INT_ACK`.
- `UVD_SYS_INT_EN`, `UVD_SYS_INT_STATUS`, and `UVD_SYS_INT_ACK`.
- Secondary `UVD_VCPU_INT_*2` and `UVD_SUVD_INT_*2` layouts.
- `UVD_MASTINT_EN` for master interrupt gating and overrun state.
- `UVD_VCPU_INT_ROUTE` for routing selected VCPU interrupt sources.

The VCPU/SYS interrupt fields include error and synchronization sources such as `PIF_ADDR_ERR`, semaphore wait/signal timeout, `RBC_REG_PRIV_FAULT`, software ring interrupts, `LBSI`, `UDEC`, `SUVD`, `RPTR_WR`, `JOB_START`/`JOB_DONE`, `GPCOM`, clock-switch events, MIF hardware interrupts, MPRD errors, RAS-control VCPU video-codec events, AVM events, and driver/firmware request/acknowledge events. The enable/status/ack naming pattern is important: callers usually enable a source, read status in an IRQ handler, and write the matching ack field to clear or retire the interrupt. The header only names bits; it does not mark whether a status field is sticky, write-one-to-clear, level-triggered, or edge-triggered.

### Job, Context, Ring, and Scratch Registers

The register block contains simple full-width or narrow fields for job and context tracking:

- `UVD_JOB_DONE` exposes a two-bit job completion value.
- `UVD_CBUF_ID`, `UVD_CONTEXT_ID`, and `UVD_CONTEXT_ID2` are full-width identifiers.
- `UVD_NO_OP` is a full-width no-op payload field.
- `UVD_CTX_INDEX` and `UVD_CTX_DATA` provide indexed context access.
- `UVD_CXW_WR`, `UVD_CXW_WR_INT_ID`, `UVD_CXW_WR_INT_CTX_ID`, and `UVD_CXW_INT_ID` expose context-write data/status and interrupt identity fields.

The ring register families describe firmware command rings:

- `UVD_RB_BASE_LO`/`HI` and `UVD_RB_SIZE` for the main ring.
- `UVD_RB_BASE_LO2`/`HI2`/`SIZE2`, `...3`, and `...4` for additional rings.
- `UVD_OUT_RB_BASE_LO`/`HI`/`SIZE` for an output ring.
- `UVD_AUDIO_RB_BASE_LO`/`HI`/`SIZE` for audio-related ring storage.
- `UVD_IOV_MAILBOX` and `UVD_IOV_MAILBOX_RESP` for virtualization mailbox exchange.

Low ring base fields start at bit 6, which implies 64-byte alignment in the low-address register. Ring size fields start at bit 4 and are masked by `0x007FFFF0`, so callers must pre-shift or use field helpers consistently rather than storing raw byte counts blindly.

The `UVD_RB_ARB_CTRL` fields control or drop access from SRBM, VCPU, RBC, and firmware-offload paths, plus `FAST_PATH_EN`. VCN start/stop code uses `VCPU_DIS` to block or unblock VCPU register access around reset and shutdown. Incorrect handling of this register can leave firmware unable to fetch commands or can expose register windows while the VCPU is being reset.

`UVD_GP_SCRATCH0` through `UVD_GP_SCRATCH23` are full-width scratch registers. They are hardware-visible state shared across host and firmware conventions, not normal kernel memory.

### Decode Setup and MPEG/MPC Fields

The chunk includes older UVD decode setup register layouts such as `UVD_MPEG2_ERROR`, `UVD_YBASE`, `UVD_UVBASE`, `UVD_PITCH`, `UVD_WIDTH`, `UVD_HEIGHT`, `UVD_PICCOUNT`, `UVD_MPRD_INITIAL_XY`, `UVD_MPEG2_CTRL`, `UVD_MB_CTL_BUF_BASE`, `UVD_PIC_CTL_BUF_BASE`, and `UVD_DXVA_BUF_SIZE`. Several are full-width `DUM` or `BASE` fields, while `UVD_MPRD_INITIAL_XY`, `UVD_MPEG2_CTRL`, and `UVD_DXVA_BUF_SIZE` split values into coordinate, enable/mode, and picture/macroblock-size fields.

The `uvd0_uvd_mpcdec` block provides motion/picture-cache and memory-swap layout:

- `UVD_MP_SWAP_CNTL` contains two-bit swap controls for reference slots 0 through 15; `UVD_MP_SWAP_CNTL2` covers reference slot 16.
- Luma/chroma search, hit, and hit-pending counters are full-width.
- `UVD_MPC_CNTL` includes block reset, replacement mode, performance reset, average weighting, urgent enable, request speed-up, and test-mode fields.
- `UVD_MPC_PITCH` exposes luma pitch.
- `UVD_MPC_SET_MUXA0/A1`, `UVD_MPC_SET_MUXB0/B1`, `UVD_MPC_SET_MUX`, and `UVD_MPC_SET_ALU` define mux/ALU programming fields used by VCN setup code.
- `UVD_MPC_PERF0` and `UVD_MPC_PERF1` expose max and average latency counters.
- `UVD_MPC_IND_INDEX` and `UVD_MPC_IND_DATA` provide indexed access.

`vcn_v4_0.c` programs `UVD_MPC_SET_MUXA0`, `UVD_MPC_SET_MUXB0`, and `UVD_MPC_SET_MUX` directly with the shift constants from this header during VCN initialization.

### Reset, Clock, Status, and Power-Related Fields

`UVD_STATUS` exposes VCN busy/idle information, including `UVD_BUSY`, `VCPU_REPORT`, `UVD_LOCKUP`, `UVD_STATUS`, `IDLE`, and `NOC_BUSY`. VCN stop paths wait for idle status before stalling memory interfaces and resetting blocks.

`UVD_ENC_PIPE_BUSY` is a dense status register for encode-pipe activity. It contains status bits for clock gating, writeback, readback, multiple control and pixel engines, cache components, DCT/IT/IME/IMC/FME/DB/DBW/CME/MIF activity, and all-pipe busy aggregation.

`UVD_FW_POWER_STATUS` contains firmware power-management handshake/status bits such as shared-memory valid, command/response flags, power-on request, P2V/V2P interrupt flags, MPC-on state, and interrupt status fields. The header describes the bits but not the firmware protocol for transitioning power states.

`UVD_CNTL`, `UVD_SOFT_RESET`, `UVD_SOFT_RESET2`, `UVD_MMSCH_SOFT_RESET`, and `UVD_WIG_CTRL` define reset and control bits for the VCN block, including UDEC, VCPU, LBSI, RBC, LMI, MPRD, IDCT, MIF, LCM, SUVD, atomic, PPU, MMSCH, AVM, ACAP, and WIG reset/status fields. These are high-risk write targets because reset fields are often adjacent to reset-status bits in the same register.

`UVD_CGC_STATUS`, `UVD_CGC_UDEC_STATUS`, `UVD_SUVD_CGC_STATUS`, and `UVD_SUVD_CGC_STATUS2` expose clock-gating state across SCLK, DCLK, and VCLK domains. They include top-level decoder/encoder active bits plus detailed status for UDEC, MP, RE, CM, IT, DB, SRE, SIT, SMP, SCM, SDB, SCLR, ENT, IME, SITE, EFC, SAOE, AV1, and next-generation SIT sub-blocks. These fields are diagnostic and validation signals for power-management transitions.

### VCPU Cache, Non-Cache, Control, and Trace

The `uvd0_ecpudec` block defines `UVD_VCPU_CACHE_OFFSET0..8` and `UVD_VCPU_CACHE_SIZE0..8`, each using a 21-bit field, plus `UVD_VCPU_NONCACHE_OFFSET0..1` and `UVD_VCPU_NONCACHE_SIZE0..1`. These registers partition firmware-visible cached and uncached memory windows.

`UVD_VCPU_CNTL` is a central firmware CPU control register. Its fields include `IRQ_ERR`, PMB enable/reset, RBBM reset, abort request, `CLK_EN`, trace enable/mux, JTAG enable, timeout disable, probe timeout value, block reset, runstall, and SRE command-interface resets. VCN boot code sets a probe timeout, enables the VCPU clock, releases `BLK_RST`, and then polls `UVD_STATUS` for responsiveness. Shutdown code blocks VCPU access, asserts `BLK_RST`, and clears `CLK_EN`.

`UVD_VCPU_PRID`, `UVD_VCPU_TRCE`, `UVD_VCPU_TRCE_RD`, `UVD_VCPU_IND_INDEX`, and `UVD_VCPU_IND_DATA` expose product ID, trace PC/data, and indirect-index/data access. These are debug and firmware-service surfaces rather than normal data structures.

### RBC, Semaphores, and Engine Start

The `uvd0_uvd_rbcdec` block describes the ring-buffer controller:

- `UVD_RBC_IB_SIZE` and `UVD_RBC_IB_SIZE_UPDATE` hold indirect-buffer size/remain fields.
- `UVD_RBC_RB_CNTL` controls ring buffer size, block size, no-fetch, write-pointer polling, no-update, read-pointer writeback, and block reset.
- `UVD_RBC_RB_RPTR_ADDR` gives the read-pointer writeback address.
- `UVD_RBC_VCPU_ACCESS` enables RBC access.
- `UVD_RBC_READ_REQ_URGENT_CNTL`, `UVD_RBC_RB_WPTR_CNTL`, `UVD_RBC_WPTR_STATUS`, `UVD_RBC_WPTR_POLL_CNTL`, and `UVD_RBC_WPTR_POLL_ADDR` configure and report write-pointer polling and read-request priority.

The semaphore fields are split across command, address, status, control, and timeout-count registers:

- `UVD_SEMA_CMD` defines request command, write phase, mode, VMID enable, and VMID.
- `UVD_SEMA_ADDR_LOW` and `UVD_SEMA_ADDR_HIGH` encode a 48-bit-ish target address in aligned low/high fields.
- `UVD_SEMA_TIMEOUT_STATUS` reports wait-incomplete, wait-fault, signal-incomplete, and timeout-clear bits.
- `UVD_SEMA_CNTL` enables semaphores and disables advanced mode.
- `UVD_SEMA_SIGNAL_INCOMPLETE_TIMEOUT_CNTL`, `UVD_SEMA_WAIT_FAULT_TIMEOUT_CNTL`, and `UVD_SEMA_WAIT_INCOMPLETE_TIMEOUT_CNTL` expose enable, mode, and counter fields for timeout detection.
- `UVD_SEMA_CMD` and `UVD_SEMA_ADDR_*` are VMID-sensitive, so wrong fields can point semaphore operations at the wrong virtual address context.

`UVD_ENGINE_CNTL` exposes engine start, start mode, and non-journal page-fault handling disable. `UVD_JOB_START` and `UVD_RBC_BUF_STATUS` provide job launch and buffer-status fields. `UVD_RBC_SWAP_CNTL` provides endian/swap controls for RBC ring, IB, and read-pointer writeback paths.

### LMI/ADP Address, VMID, Atomic, Arbitration, and Latency

The `uvd0_lmi_adpdec` portion is dominated by low/high 64-bit base-address fields. Each low register exposes `BITS_31_0`; each high register exposes `BITS_63_32`. Covered clients include RE, IT, MP, CM, DB, DBW, IDCT, MPRD streams, MPC, RBC ring/IB, LBSI, VCPU non-cache windows, VCPU cache windows, CENC, SRE, GPGPU, current/reference luma/chroma, DBW, CM colocated data, BSP0..3, BSD0..4, SCLR, image-paste luma/chroma, privacy luma/chroma, and `UVD_LMI_SPH_64BIT_BAR_HIGH`.

These fields are hardware address windows for VCN internal clients. They integrate with firmware setup, GPU memory management, VMID assignment, and LMI arbitration. The field layout itself is simple full-width low/high composition, but the operational risk is high because an incorrect base address can send decoder reads/writes to the wrong VRAM/GTT address.

`UVD_ADP_ATOMIC_CONFIG` defines four atomic-user write-cache nibbles plus an atomic read-urgent field. `UVD_LMI_ARB_CTRL2` defines CENC read wait, atomic write wait, CENC/atomic burst sizing, and MIF read/write request-return maxima. These are throughput and fairness controls for memory traffic.

`UVD_LMI_VCPU_CACHE_VMIDS_MULTI` packs VMIDs for VCPU cache windows 1 through 8 into eight four-bit fields across the register. `UVD_LMI_VCPU_NC_VMIDS_MULTI` similarly packs non-cache VMIDs for NC2 through NC7. These packed VMID fields are security-sensitive: an off-by-four shift or stale mask can assign a firmware memory window to the wrong virtual memory context.

`UVD_LMI_LAT_CTRL`, `UVD_LMI_LAT_CNTR`, and `UVD_LMI_AVG_LAT_CNTR` define latency measurement controls and counters, including scaling, max/min/average start bits, perfmon sync, skip, max/min latency, and average latency envelope/hit fields. The range ends just after the `UVD_LMI_SPH` register starts with `ADDR__SHIFT`; its remaining status fields are outside the mapped chunk.

## Control Flow

This header chunk has no executable control flow. The implied runtime pattern in consumers is:

1. Resolve a register address using the matching offset header and SOC15 instance helpers, for example `SOC15_REG_OFFSET(VCN, i, regUVD_VCPU_CNTL)`.
2. Read a raw register value with an AMDGPU MMIO helper when preserving unrelated bits is necessary.
3. Use the generated shift/mask pair directly or through `REG_SET_FIELD`/`REG_GET_FIELD` to compose or extract field values.
4. Write the raw value back with `WREG32_SOC15`, `WREG32_P`, or related helpers, respecting hardware ordering and side-effect requirements.
5. Poll status registers such as `UVD_STATUS`, `UVD_LMI_STATUS`, or clock-gating status registers when hardware requires reset/idle/clean handshakes.

Ordering is intentionally absent from the header. Start, stop, reset, power-gating, IRQ, and firmware-message sequencing live in VCN/JPEG/MMSCH driver code and firmware ABI definitions.

## State and Persistence Behavior

The macros describe hardware state, not kernel-owned storage:

- Clock-gating and reset control bits persist in VCN registers until changed or reset by hardware.
- Interrupt enable/status/ack fields reflect hardware event state and may have side effects on write depending on the register.
- Ring base/size, output-ring, audio-ring, mailbox, scratch, context, and job registers persist as firmware/driver communication state.
- VCPU cache and non-cache offset/size fields define firmware memory windows.
- MPC, RBC, semaphore, and engine-control fields configure active decode-command execution paths.
- LMI/ADP base-address, VMID, atomic, arbitration, and latency fields configure memory access and collect hardware counters.

The header contributes no lifetime management, synchronization, or persistence policy. Any persistence risk comes from callers composing raw register values incorrectly or using a mask generated for the wrong hardware revision.

## Dependencies and Integration Points

Direct dependencies are limited to preprocessing and include order. Consumers need this header together with `vcn_4_0_0_offset.h` and the common AMDGPU register helper macros.

Important integration points in this source tree include:

- `drivers/gpu/drm/amd/amdgpu/vcn_v4_0.c`, which includes the VCN 4.0.0 offset and shift/mask headers and uses many fields in this chunk for VCN boot, stop, reset, clock, ring, and MPC setup.
- `drivers/gpu/drm/amd/amdgpu/jpeg_v4_0.c`, which includes the same VCN 4.0.0 generated headers because the JPEG block shares VCN/UVD register definitions and interrupt-source conventions.
- `drivers/gpu/drm/amd/amdgpu/umsch_mm_v4_0.c`, which also includes the VCN 4.0.0 headers for multimedia scheduler integration.
- Common SOC15/AMDGPU MMIO helpers (`SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `SOC15_WAIT_ON_RREG`) and bitfield helpers (`REG_SET_FIELD`, `REG_GET_FIELD`).
- Firmware ABI structures and command paths under the VCN driver, especially where scratch registers, command registers, firmware messages, ring buffers, and power-status bits are used for host/firmware synchronization.

The generated register names must remain synchronized with the matching offset file. A valid mask paired with the wrong `reg*` address is as dangerous as an invalid mask.

## Risks and Edge Cases

- Generated-header drift: VCN start/stop code relies on exact `UVD_VCPU_CNTL`, `UVD_RB_ARB_CTRL`, `UVD_MPC_SET_MUX*`, `UVD_SOFT_RESET`, and LMI field positions. Drift can produce silent hardware misprogramming rather than a compile error.
- Partial boundary risk: this chunk begins inside `SCM_SUVD_CGC_CTRL` and ends inside `UVD_LMI_SPH`; adjacent chunks are required for complete register documentation at both edges.
- Read-modify-write side effects: reset, interrupt ack, timeout clear, and clock-control registers may include side-effect bits. Blind writes using full masks can clear status, assert reset, or acknowledge interrupts unexpectedly.
- Repeated layout copy errors: the many `*_SUVD_CGC_CTRL`, interrupt enable/status/ack, ring, scratch, and LMI BAR families are mechanically similar. Prefix or instance mistakes are easy to miss in review.
- Packed VMID fields: `UVD_LMI_VCPU_CACHE_VMIDS_MULTI` and `UVD_LMI_VCPU_NC_VMIDS_MULTI` pack several four-bit VMIDs into one register. A wrong shift can cross security/isolation boundaries between VCN firmware memory windows.
- Address alignment assumptions: ring bases, semaphore addresses, and several base/size registers expose shifted or masked address fields. Callers must provide aligned values and understand whether helpers expect raw or unshifted field values.
- Reset/status adjacency: `UVD_SOFT_RESET` mixes reset controls and reset status bits. Preserving reserved/status bits incorrectly can leave hardware stuck in reset or make shutdown fail.
- Firmware protocol dependency: GPCOM, driver/firmware messages, scratch registers, and firmware power status require external ABI sequencing; this header cannot validate stale firmware, command-source races, or timeout selection.
- Interrupt source symmetry: enable/status/ack registers mostly mirror names but not perfectly. Handlers should not assume a field exists in all three variants without checking the generated definition.
- Hardware-generation specificity: these masks are for VCN 4.0.0. Reusing them against VCN 4.0.3, 4.0.5, or 5.x registers must be justified by the matching generated headers, not by similar names.

## Test Signals

Useful validation signals for this chunk are primarily build-time, static, and hardware-integration oriented:

- Build AMDGPU with VCN 4.0.0 support and ensure all `vcn_v4_0.c`, `jpeg_v4_0.c`, and `umsch_mm_v4_0.c` references to `UVD_*` field macros resolve without local compatibility shims.
- Compare the generated `vcn_4_0_0_sh_mask.h` and `vcn_4_0_0_offset.h` against AMD's source register database when generated-header churn appears; treat field-position changes as hardware ABI changes.
- Boot VCN 4.0.0 hardware and verify the firmware start sequence: program MPC muxes, resume memory controller windows, unblock VCPU access, release `UVD_VCPU_CNTL__BLK_RST`, and observe `UVD_STATUS` responsiveness.
- Exercise VCN shutdown and reset paths, checking idle polling, LMI clean polling, `UVD_LMI_CTRL2__STALL_ARB_UMC_MASK`, VCPU access blocking, VCPU clock disable, and `UVD_SOFT_RESET` behavior.
- Validate decode workloads through the VCN ring so ring base/size, RBC control, write-pointer polling, semaphore, and job-done/interrupt fields are exercised under normal command submission.
- Inspect interrupt handling under error and completion conditions: VCPU/SYS/SUVD enable bits should correspond to observed status bits, and ack writes should clear only intended sources.
- Use power-management or debugfs/reg-dump flows to confirm CGC control/status transitions across idle, active decode, and power-gated states.
- On virtualized or VMID-heavy configurations, verify VCPU cache/non-cache VMID and LMI base-address programming with memory isolation tests, because the packed VMID and BAR fields directly affect firmware memory access.

### subset-b-003458: lines 4741-7291

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_0_sh_mask.h lines 4741-7291

## Scope

This chunk covers 2,551 lines of the generated AMD VCN 4.0.0 shift/mask header. It begins inside the `uvd0_uvddec` local-memory-interface area at the tail of `UVD_LMI_SPH`, then defines the VCN/JPEG register field layouts through the start of `uvd0_slmi_adpdec`. The chunk contains 2,138 `#define` entries and is declarative hardware ABI data only: it has no C functions, structs, variables, branches, loops, allocations, locking, or direct MMIO reads/writes.

The covered register groups are:

- LMI and VCN RAS tail registers: `UVD_LMI_VCPU_CACHE_VMID`, `UVD_LMI_CTRL2`, `UVD_LMI_URGENT_CTRL`, `UVD_LMI_CTRL`, `UVD_LMI_STATUS`, LMI perf counters, ADP swap/indirect/prefetch controls, MIF reference BARs, and `VCN_RAS_CNTL`.
- `uvd0_jpegnpdec`: JPEG decode control, ring base/read/write/size registers, decode counters, SPS/output/tier configuration, JPEG interrupt enable/status bits, tiling/address-mode fields, command/data indirect registers, scratch, and decoder soft reset.
- `uvd0_uvd_jrbc_dec`: JPEG ring-buffer controller write/read pointers, ring/IB control and sizes, urgent control, conditional-read timers, status/error/trap/preempt bits, preempt fence data, and scratch.
- `uvd0_uvd_jmi_dec`: JPEG memory-interface urgent/QoS controls, page-fault handling, LMI/JMI control, decode/encode drop and clamping registers, VMID fields, many 64-bit BAR low/high pairs for JPEG/JRBC/EJRBC/encoder paths, latency/perf counters, clean status, swap controls, atomic controls, RAS controls, and JPEG2 page-fault control.
- `uvd0_uvd_jpeg_common_dec`: JPEG common reset, system interrupt enable/status/ack, memcheck interrupt enable/status/ack, master interrupt, interrupt-handler metadata, and JRBBM arbitration.
- `uvd0_uvd_jpeg_common_sclk_dec`: JPEG clock gating, dynamic clock control/status, memory low-power controls, soft reset, and four perf-bank counters.
- `uvd0_uvd_pg_dec`: VCN power-gating FSM configuration/status, power status, DPG local-memory access registers, scratch registers, firmware/version/feature/RAS status, doorbell controls, ring enable/write-pointer controls, ring pointer mirrors, and DPG LMA control.
- `uvd0_mmsch_dec`: multimedia scheduler ucode/SRAM access, VF context/GPCOM/mailbox registers, scheduler control/status, non-cache windows, last memory-access debug registers, scratch registers, GPU IOV scheduling blocks 0-2, VFID FIFOs, NACK status, and busy status.
- The first few `uvd0_slmi_adpdec` MMSCH non-cache BAR definitions for `NC0` and `NC1`.

Every field is represented by the generated pair `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. The matching `vcn_4_0_0_offset.h` file supplies the register addresses; this chunk supplies the bit layouts for composing and decoding register values.

## Purpose

The purpose of this header section is to give AMDGPU compile-time names for VCN 4.0.0 JPEG, memory-interface, power-management, interrupt, RAS, doorbell, and MMSCH register fields. Consumers use these constants through register helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `SOC15_WAIT_ON_RREG`, and DPG-mode helpers.

For example, VCN/JPEG driver code uses these definitions to:

- Stall or unstall LMI/UMC arbitration with `UVD_LMI_CTRL2__STALL_ARB_UMC_MASK`, then poll `UVD_LMI_STATUS` clean bits before reset or power transitions.
- Enable JPEG ring interrupts with `JPEG_SYS_INT_EN__DJRBC_MASK` or per-pipe variants in newer generations.
- Program JPEG clock gating with `JPEG_CGC_GATE__JPEG_DEC_MASK`, `JPEG_CGC_GATE__JPEG2_DEC_MASK`, `JPEG_CGC_GATE__JMCIF_MASK`, and `JPEG_CGC_GATE__JRBBM_MASK`.
- Poll and update VCN power state with `UVD_POWER_STATUS__UVD_POWER_STATUS_MASK`, `UVD_POWER_STATUS__UVD_PG_MODE_MASK`, and `UVD_POWER_STATUS__UVD_PG_EN_MASK`.
- Initialize or inspect MMSCH virtual-function context/GPCOM addresses, mailbox registers, GPU IOV command controls, VM busy status, and active function masks.

The header itself is not policy. It is the hardware ABI vocabulary that lets runtime code perform precise bitfield operations without open-coded constants.

## Important Macro Families

### LMI Control, Status, and Performance

`UVD_LMI_CTRL2` defines secondary LMI control bits for SPH disable, MC/UMC urgent handling, CRC reset/select, MC read/write ID selection, VCPU non-cache extension enables, SPU extra client ID, ring-engine offload, non-JPEG MIF gating, and the important `STALL_ARB_UMC` bit used by reset/power paths to stop UMC arbitration.

`UVD_LMI_CTRL` controls write-clean timer behavior, request mode, MC urgent masking/assertion, data-coherency enables for VCPU/CM/DB/IT/MIF paths, CRC controls, firmware-failure disable behavior, and MC/UMC block resets. `UVD_LMI_STATUS` exposes clean/idle/pending state, including read/write clean, raw clean, VCPU write clean, UMC read/write clean, pending MC writes, UMC UVD/AVP idle, ADP clean state, BSP write-clean bits, and CENC read clean. Runtime reset paths in VCN generations poll these clean bits before asserting resets or changing arbitration.

`UVD_LMI_URGENT_CTRL` is split into MC read, MC write, UMC read, and UMC write urgent-stall groups. Each group has enable/stall/assert fields. `UVD_LMI_PERFMON_CTRL`, `UVD_LMI_PERFMON_COUNT_LO`, and `UVD_LMI_PERFMON_COUNT_HI` provide a small LMI performance counter. `UVD_LMI_ADP_SWAP_CNTL`, `UVD_LMI_RBC_RB_VMID`, `UVD_LMI_RBC_IB_VMID`, `UVD_LMI_MC_CREDITS`, `UVD_LMI_ADP_IND_INDEX/DATA`, `UVD_LMI_PREF_CTRL`, and MIF reference BARs cover byte swapping, VMIDs, outstanding credits, indirect ADP register access, prefetch behavior, and 64-bit luma reference addressing.

### JPEG Decode and Ring Programming

The `uvd0_jpegnpdec` block starts with `UVD_JPEG_CNTL` request/error-reset bits and ring-buffer fields: `UVD_JPEG_RB_BASE`, `UVD_JPEG_RB_WPTR`, `UVD_JPEG_RB_RPTR`, and `UVD_JPEG_RB_SIZE`. The ring pointer and size fields are shifted by four bits and masked to aligned byte ranges.

Decode status/configuration includes `UVD_JPEG_DEC_CNT`, SPS width/height and chroma/subformat fields, `UVD_JPEG_RE_TIMER`, scratch, output-buffer control/read/write pointers, pitch/UV pitch, GFX8/GFX10 tiling surface fields, address-config and address-mode registers, output XY fields, GPCOM command/data registers, indirect index/data, and decoder soft reset/status.

`UVD_JPEG_INT_EN` and `UVD_JPEG_INT_STAT` have parallel layouts for normal and error events: output-buffer write-pointer increment, job available, fence value, FIFO overflow, block-count out-of-sync, EOI, HFM, reset, ECS marker, timeout, marker, format, and profile errors. These bits feed JPEG interrupt handling and are strong test signals for command submission, job completion, and malformed-stream handling.

Tier controls (`UVD_JPEG_TIER_CNTL0/1/2` and `UVD_JPEG_TIER_STATUS`) describe component IDs, sampling factors, quantization table IDs, coefficient counts, tier index/counter state, and block accounting. They are part of the JPEG parser/decoder hardware programming model rather than general driver-owned state.

### JRBC Command Processor and Preemption

`uvd0_uvd_jrbc_dec` describes the JPEG ring-buffer controller. `UVD_JRBC_RB_WPTR`, `UVD_JRBC_RB_RPTR`, and `UVD_JRBC_RB_SIZE` are the hardware-visible command ring pointers/size. `UVD_JRBC_RB_CNTL` controls fetch and read-pointer write enable. `UVD_JRBC_IB_SIZE` and `UVD_JRBC_IB_SIZE_UPDATE` describe indirect-buffer sizing, while `UVD_JRBC_RB_BUF_STATUS` and `UVD_JRBC_IB_BUF_STATUS` expose buffer valid/read/write positions.

`UVD_JRBC_RB_COND_RD_TIMER` and `UVD_JRBC_IB_COND_RD_TIMER` contain retry timer, retry interval, continuous polling, and memory-timeout enable fields. `UVD_JRBC_STATUS` is the main completion/error register with job done bits, illegal-command bits, conditional-register-read timeout, memory read/write timeout, trap status, preempt status, interrupt enable, and interrupt ack. `UVD_JPEG_PREEMPT_CMD` controls preemption enable, wait-for-job-done, and fence command behavior, with two 32-bit preempt fence data words.

These masks are used around ring startup, command submission, interrupt handling, and GPU reset diagnosis. A wrong pointer mask or status bit definition can turn a live ring into a stuck-ring or false-timeout condition.

### JMI, VMID, BAR, Swap, and Memcheck Controls

The `uvd0_uvd_jmi_dec` block covers the memory-facing path for JPEG decode/encode and JRBC/EJRBC. `UVD_JADP_MCIF_URGENT_CTRL` and `UVD_JMI_URGENT_CTRL` define watermarks, urgent timers, urgent step sizes, QoS enables, and MC read/write urgent assertion. `UVD_JMI_CTRL`, `UVD_LMI_JRBC_CTRL`, `UVD_LMI_JPEG_CTRL`, `UVD_JMI_EJRBC_CTRL`, `UVD_LMI_EJPEG_CTRL`, and `UVD_JMI_SCALER_CTRL` provide arbitration wait enables, max burst fields, read/write swap fields, MC urgent controls, CRC control, and scaler/JPEG memory behavior.

Drop and clamping registers (`JPEG_LMI_DROP`, `UVD_JMI_EJPEG_DROP`, `JPEG_MEMCHECK_CLAMPING`, `UVD_JMI_EJPEG_MEMCHECK_CLAMPING`) let hardware drop or clamp selected read/write paths to safe addresses. `JPEG_MEMCHECK_SAFE_ADDR` and `JPEG_MEMCHECK_SAFE_ADDR_64BIT` provide safe address fields. These are security and robustness sensitive because they affect behavior after memory-check or page-fault conditions.

VMID registers define which GPU VMIDs are used by JPEG/JRBC read/write/fence/atomic paths: `UVD_LMI_JRBC_IB_VMID`, `UVD_LMI_JRBC_RB_VMID`, `UVD_LMI_JPEG_VMID`, `UVD_JMI_ENC_JRBC_IB_VMID`, `UVD_JMI_ENC_JRBC_RB_VMID`, `UVD_JMI_ENC_JPEG_VMID`, `UVD_LMI_JPEG_PREEMPT_VMID`, `UVD_LMI_ENC_JPEG_PREEMPT_VMID`, and `UVD_LMI_JPEG2_VMID`. These fields are integration points with AMDGPU VM and SR-IOV isolation; an incorrect VMID mask can make hardware access the wrong address space.

The many `*_64BIT_BAR_LOW/HIGH` registers define low/high 32-bit halves for JPEG read/write, preempt fence, JRBC/EJRBC ring and IB, ring/IB memory read/write, encoder PEL read, bitstream write, scaler read/write, JPEG2 read/write, atomic user writes, and HUFF fence paths. Each low/high half exposes the full 32-bit field. Correct low-before-high or high-before-low ordering is a caller responsibility; the header only gives masks.

`UVD_JMI_DEC_SWAP_CNTL`, `UVD_JMI_ENC_SWAP_CNTL`, and `UVD_JMI_DEC_SWAP_CNTL2` define two-bit byte-swap fields per data path. `UVD_JMI_ATOMIC_CNTL` and `UVD_JMI_ATOMIC_CNTL2` control atomic arbitration, burst, drop/clamping, urgent, software gate, atomic mode, endianness, address alignment, and memory-address-type behavior.

`UVD_JMI_CLEAN_STATUS` is the JPEG memory-interface equivalent of LMI clean state. It exposes clean/raw/pending bits for LMI, DJRBC, EJRBC, JPEG, PEL, scaler, bitstream, JPEG2, and MC write pending paths. It is relevant to reset and power-down sequencing.

### JPEG Common Interrupt, Clock, and Perf Blocks

`JPEG_SOFT_RESET_STATUS`, `JPEG_SYS_INT_EN`, `JPEG_SYS_INT_STATUS`, and `JPEG_SYS_INT_ACK` define the common JPEG interrupt domain. System interrupt bits include DJRBC, EJRBC, decode/encode page-fault reports, JPEG core, JPEG2 core, and RAS control notifications. `JPEG_MEMCHECK_SYS_INT_EN/STAT/ACK` separately expose high/low read/write memory-check errors for DJRBC, EJRBC, BS fetch/write, PEL fetch, scalar read/write, output-buffer write, and JPEG2 read/write paths.

`JPEG_MASTINT_EN` controls interrupt overrun reset/status. `JPEG_IH_CTRL` describes the interrupt handler packet metadata: soft reset, stall, status clean, VMID, user data, and ring ID. `JRBBM_ARB_CTRL` provides DJRBC/EJRBC/SRBM drop controls.

The SCLK common block defines clock gating and memory low-power behavior. `JPEG_CGC_GATE` gates JPEG decode, JPEG2 decode, JPEG encode, JMCIF, and JRBBM. `JPEG_CGC_CTRL` configures dynamic clock mode, delay timers, and per-block mode bits. `JPEG_CGC_STATUS` reports VCLK/SCLK active state per block. `JPEG_COMN_CGC_MEM_CTRL`, `JPEG_DEC_CGC_MEM_CTRL`, `JPEG2_DEC_CGC_MEM_CTRL`, and `JPEG_ENC_CGC_MEM_CTRL` control light sleep, deep sleep, shutdown, and software light-sleep enables for memories. `JPEG_SOFT_RESET2` adds atomic soft reset. `JPEG_PERF_BANK_CONF`, `JPEG_PERF_BANK_EVENT_SEL`, and four count registers expose a compact perf-bank interface.

### VCN Power, Feature, RAS, Doorbell, and Ring State

The `uvd0_uvd_pg_dec` block describes power gating and DPG state. `UVD_PGFSM_CONFIG` and `UVD_PGFSM_STATUS` contain two-bit power config/status fields for many sub-blocks (`UVDM`, `UVDS`, `UVDF`, `UVDTC`, `UVDB`, `UVDTA`, `UVDLM`, `UVDTD`, `UVDTE`, `UVDE`, `UVDAB`, `UVDJ`, `UVDTB`, `UVDNA`, `UVDNB`). `UVD_POWER_STATUS` and `UVD_JPEG_POWER_STATUS` expose global and JPEG power status/mode, snoop disable bits, PG enable, clock-gating mode, and DPG power-up stall. VCN runtime power code polls and updates these fields around start/stop and dynamic power-gating paths.

`UVD_PG_IND_INDEX/DATA`, `UVD_DPG_LMA_CTL/DATA/MASK`, `UVD_DPG_PAUSE`, and `UVD_DPG_LMA_CTL2` define direct power-gating/local-memory access controls and SRAM write pointers. `UVD_DPG_LMI_VCPU_CACHE_64BIT_BAR_LOW/HIGH`, `UVD_DPG_VCPU_CACHE_OFFSET0`, and `UVD_DPG_LMI_VCPU_CACHE_VMID` define DPG VCPU cache addressing.

Scratch registers `UVD_SCRATCH1` through `UVD_SCRATCH32`, `UVD_FW_VERSION`, `UVD_VERSION`, timestamp counter low/high, and general-purpose counter registers provide firmware, diagnostic, and timing state. `UVD_PF_STATUS` exposes many page-fault status bits and fields. `UVD_RAS_VCPU_VCODEC_STATUS`, `UVD_RAS_MMSCH_FATAL_ERROR`, `UVD_RAS_JPEG0_STATUS`, `UVD_RAS_JPEG1_STATUS`, and `UVD_RAS_CNTL_PMI_ARB` describe poison/fatal/RAS control state.

`VCN_FEATURES` advertises hardware capabilities: video decode/encode, MJPEG decode/encode, virtualization, H.264 legacy decode, UDEC, MJPEG2 IDCT, scaler, VP9, AV1 decode, EFC encode, HDR2SDR, dual MJPEG decode, AV1 encode, and instance ID. Code that derives feature support from this register depends on exact masks.

Doorbell and ring controls include `VCN_RB_DB_CTRL`, `VCN_JPEG_DB_CTRL`, `VCN_RB1_DB_CTRL` through `VCN_RB4_DB_CTRL`, `VCN_UMSCH_RB_DB_CTRL`, `VCN_AGDB_CTRL0` through `VCN_AGDB_CTRL5`, and `VCN_AGDB_MASK0` through `VCN_AGDB_MASK5`. They share offset, enable, and hit fields for doorbell routing. `VCN_RB_ENABLE` enables multiple video/JPEG/UMSCH/EJPEG/audio rings, and `VCN_RB_WPTR_CTRL` enables write-pointer checksum/control-store behavior for the same ring families. Ring pointer mirror registers expose video, output, audio, RBC, and numbered RB read/write pointers.

### MMSCH and GPU IOV Scheduler

The `uvd0_mmsch_dec` block defines the multimedia scheduler register interface. `MMSCH_UCODE_ADDR/DATA` and `MMSCH_SRAM_ADDR/DATA` provide ucode and SRAM access with lock bits on address registers. `MMSCH_VF_SRAM_OFFSET`, `MMSCH_DB_SRAM_OFFSET`, and `MMSCH_CTX_SRAM_OFFSET` describe SRAM partitioning for virtual functions, doorbells, and context storage.

Interrupt and VF context/GPCOM registers include `MMSCH_INTR`, `MMSCH_INTR_ACK`, `MMSCH_INTR_STATUS`, `MMSCH_VF_VMID`, `MMSCH_VF_CTX_ADDR_LO/HI`, `MMSCH_VF_CTX_SIZE`, `MMSCH_VF_GPCOM_ADDR_LO/HI`, `MMSCH_VF_GPCOM_SIZE`, host/response mailboxes, and two per-VF mailbox pairs. `MMSCH_CNTL` exposes scheduler clock enable, error-detection enable, IRQ error field, NACK and doorbell-busy interrupt enables, probe timeout, timeout disable, and idle status.

`MMSCH_NONCACHE_OFFSET0/SIZE0` and `MMSCH_NONCACHE_OFFSET1/SIZE1` describe non-cache windows. `MMSCH_PROC_STATE1`, `MMSCH_LAST_MC_ADDR`, and `MMSCH_LAST_MEM_ACCESS_HI/LO` are debug/status registers for scheduler execution and memory access. Scratch registers provide firmware-visible storage.

GPU IOV command and status blocks repeat for scheduler blocks 0, 1, and 2: `MMSCH_GPUIOV_SCH_BLOCK_*` identify block ID/version/size; `MMSCH_GPUIOV_CMD_CONTROL_*` contains command type, execute, interrupt enables, VM-busy interrupt enable, function ID, and next function ID; `MMSCH_GPUIOV_CMD_STATUS_*`, `MMSCH_GPUIOV_VM_BUSY_STATUS_*`, `MMSCH_GPUIOV_ACTIVE_FCNS_*`, and `DW6/DW7/DW8` provide command state and data. There are parallel `*_IP_*` scheduler-block and command-status registers, context-size/location fields, VFID FIFO head/tail pairs, NACK status, mailbox data, and `MMSCH_VM_BUSY_STATUS_0/1/2`.

The chunk ends after the first `uvd0_slmi_adpdec` definitions for MMSCH non-cache BAR low/high registers. The continuation of `UVD_LMI_MMSCH_NC1_64BIT_BAR_HIGH` and later NC2-NC7/VMID fields belongs to the next chunk.

## Control Flow

There is no executable control flow in this header chunk. Runtime control flow is implied by how AMDGPU callers use the macros:

1. Resolve the register address with a companion `reg*`/`mm*` offset macro from `vcn_4_0_0_offset.h` or an ASIC-specific wrapper.
2. Read the raw 32-bit register value with `RREG32_SOC15`, `RREG32_SOC15_OFFSET`, or a DPG-mode read helper.
3. Extract fields with `REG_GET_FIELD` or manual mask/shift operations, or compose updates with `REG_SET_FIELD`, `WREG32_P`, or explicit read-modify-write.
4. For state transitions, poll status masks with helpers such as `SOC15_WAIT_ON_RREG`, then write control fields in the order required by the hardware block.

Typical flow examples from nearby VCN/JPEG generations are: program clock gates before ring setup; enable JPEG system interrupts; set ring write pointers; poll LMI/JMI clean bits before reset; update `UVD_POWER_STATUS` for DPG mode; and initialize MMSCH VF context/GPCOM pointers before GPU IOV command execution.

The header does not encode sequencing, delays, clear-on-read behavior, write-one-to-clear semantics, or serialization. Those rules live in the driver code and hardware programming guide.

## State and Persistence Behavior

The macros describe hardware register state, not storage allocated by the driver:

- Ring pointers, ring sizes, IB sizes, doorbell controls, and write-pointer controls persist in VCN/JPEG registers until reset or explicit reprogramming.
- Interrupt enable/status/ack and memcheck status/ack fields represent transient hardware event state; ack registers can have side effects depending on hardware semantics.
- Power-gating, clock-gating, and memory low-power fields persist across runtime power transitions and directly affect block availability.
- VMID and BAR fields persist as hardware address-space and buffer mappings for JPEG/JRBC/EJRBC/MMSCH paths.
- Perf counters and latency counters accumulate hardware events until reset, wrap, or reconfiguration.
- RAS and page-fault status fields capture error state that may need explicit rearm, clear, or poison handling.
- MMSCH mailbox, SRAM, GPU IOV command, busy, and active-function fields represent scheduler and virtualization state shared with firmware/hardware.

Because this file only names bitfields, the persistence risk is indirect but significant: a wrong mask can make software preserve, clear, set, or poll the wrong bits in persistent hardware state.

## Dependencies and Integration Points

Direct dependencies are the C preprocessor and the matching VCN 4.0.0 offset header. Practical integration points in this tree include:

- `drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.c`, which uses the same generated field families for JPEG clock gating, JPEG system interrupt enable, JPEG ring write-pointer reset/read/write, and DPG-mode JPEG register programming.
- `drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.c`, which uses `UVD_LMI_CTRL2`, `UVD_LMI_STATUS`, `UVD_POWER_STATUS`, `UVD_PGFSM_CONFIG`, and related masks for VCN power, reset, clock, and LMI clean sequencing.
- Newer VCN/JPEG implementations such as `vcn_v5_0_1.c`, `vcn_v5_0_2.c`, `jpeg_v5_0_2.c`, and `jpeg_v5_3_0.c`, which preserve the same programming pattern and show how these generated field names are consumed as the IP evolves.
- `drivers/gpu/drm/amd/amdgpu/mmsch_v2_0.h` and VCN virtualization paths, which define/use MMSCH register offsets corresponding to this scheduler and GPU IOV field layout.
- AMDGPU register helper infrastructure (`REG_GET_FIELD`, `REG_SET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `SOC15_WAIT_ON_RREG`, and DPG-mode helpers), which assumes every generated `_MASK` and `__SHIFT` pair matches the underlying register.
- Firmware and hardware interfaces for VCN, JPEG, MMSCH, RAS, page-fault reporting, and SR-IOV/GPU IOV scheduling.

The generated header must stay synchronized with the offset header and with ASIC-specific source files. A field layout from VCN 4.0.0 used with a VCN 4.0.5 or VCN 5.x address is only safe when the hardware field layout is intentionally unchanged.

## Risks and Edge Cases

- Large generated ABI surface: this chunk has more than two thousand macros. Mechanical generation errors can compile cleanly while corrupting runtime bitfield access.
- Partial chunk boundaries: line 4741 starts after the `UVD_LMI_SPH` comment and shift definitions, so this chunk only contains the end of that register. The end also cuts into the `uvd0_slmi_adpdec` BAR sequence after `NC1`. Merge/reconciliation should combine adjacent chunks before treating those registers as fully researched.
- Read-modify-write hazards: control registers mix enable, reset, urgent, stall, CRC, drop, clamping, and ack-like fields. Broad writes can accidentally reset blocks, acknowledge interrupts, disable clocks, drop traffic, or change QoS.
- Pointer and alignment masks: JPEG/JRBC ring pointers, BAR low fields, and MMSCH context/GPCOM low-address fields encode alignment in low bits. Using raw byte addresses without respecting shifts/masks can misprogram hardware addresses.
- VMID isolation risk: JPEG/JRBC/EJRBC/MMSCH VMID fields are security-sensitive in virtualized or multi-process GPU contexts. Wrong masks can route hardware reads/writes through the wrong VMID.
- Interrupt status/ack confusion: `JPEG_SYS_INT_STATUS`, `JPEG_SYS_INT_ACK`, `JPEG_MEMCHECK_SYS_INT_STAT`, and `JPEG_MEMCHECK_SYS_INT_ACK` have similar layouts. Accidentally using status masks as write data for the wrong ack register can lose diagnostics or leave interrupts asserted.
- Clean-status polling risk: `UVD_LMI_STATUS` and `UVD_JMI_CLEAN_STATUS` expose many similar clean/raw/pending bits. Waiting on the wrong bit can cause reset hangs or premature reset while memory traffic is still pending.
- Power and clock sequencing risk: `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `JPEG_CGC_GATE`, and memory low-power fields require hardware-specific ordering. This header cannot prevent writes while the block is gated or powered down.
- RAS and page-fault side effects: RAS, poison, page-fault, memcheck, and clamping fields may be sticky or require rearm/ack sequences. Incorrect masks can hide hardware faults or repeatedly retrigger interrupts.
- Naming typo preservation: GPU IOV command control fields use the generated spelling `FUNCTINO_ID` rather than `FUNCTION_ID`. Consumers must use the generated name exactly unless the register generator is corrected across all dependent files.

## Test Signals

Useful validation for this chunk is mostly compile-time, static, and hardware-integration oriented:

- Build AMDGPU with VCN 4.0 support so all `UVD_*`, `JPEG_*`, `VCN_*`, and `MMSCH_*` field macros referenced by VCN/JPEG/MMSCH code resolve with the matching offset headers.
- Compare generated `vcn_4_0_0_sh_mask.h` against AMD's register database or a known-good upstream header; focus on high-risk families: ring pointers, VMIDs, BAR halves, interrupt ack/status, power status, clean status, and MMSCH GPU IOV controls.
- Boot supported VCN 4.x hardware and verify VCN/JPEG initialization: clock-gating writes, DPG-mode programming, JPEG ring write-pointer reset/readback, and interrupt enable should complete without ring timeout.
- Exercise JPEG decode submissions and confirm `UVD_JRBC_RB_WPTR/RPTR`, `UVD_JRBC_STATUS` job-done/error bits, and `JPEG_SYS_INT_STATUS/ACK` behave as expected.
- Test malformed or fault-injected JPEG paths where available: memcheck status/ack bits, page-fault report bits, clamping/drop behavior, and RAS JPEG status should produce stable diagnostics without interrupt storms.
- Run suspend/resume, runtime DPG, and GPU reset paths while JPEG/VCN rings are idle and active; failures often show up as waits on `UVD_LMI_STATUS`, `UVD_JMI_CLEAN_STATUS`, `UVD_POWER_STATUS`, or `UVD_JPEG_POWER_STATUS`.
- On SR-IOV/GPU IOV configurations, validate MMSCH VF context/GPCOM address programming, mailbox exchange, GPU IOV command status, VM busy status, active function masks, and VFID FIFO state.
- Review any future generated-header churn together with `vcn_4_0_0_offset.h` and ASIC-specific C files. Field changes in this chunk should be treated as hardware ABI changes, not formatting-only edits.

### subset-b-003459: lines 7292-8937

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_0_sh_mask.h lines 7292-8937

## Scope And Purpose

This chunk is the final 1,646-line segment of AMD's generated VCN 4.0.0 shift/mask header. It contains C preprocessor constants only: each hardware register field is represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. It defines no functions, structs, enums, storage, locking, allocation, or direct MMIO operations.

The path is under a `ceph-client` source mirror, but this file is AMDGPU media-engine register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU VCN and UMSCH code that combines these masks with companion register address macros from `vcn_4_0_0_offset.h` and register helper macros such as `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_SOC15_UMSCH`.

This chunk starts mid-register with `UVD_LMI_MMSCH_NC1_64BIT_BAR_HIGH`, so the low half and NC0 definitions are in the previous chunk. It continues through UVD context/LMI/memcheck fields, UMSCH scheduler fields, MES microcontroller state and memory aperture registers, and closes the file guard with `#endif`.

## Important APIs, Types, And Macros

The exported API is the generated register-field macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position used to pack or unpack a hardware field.
- `<REGISTER>__<FIELD>_MASK`: the raw register mask for that field.

Major register groups in this chunk:

- MMSCH LMI apertures and controls: `UVD_LMI_MMSCH_NC1_64BIT_BAR_HIGH` through `UVD_LMI_MMSCH_NC7_64BIT_BAR_HIGH`, `UVD_LMI_MMSCH_NC_VMID`, `UVD_LMI_MMSCH_CTRL`, `UVD_MMSCH_LMI_STATUS`, and `VCN_RAS_CNTL_MMSCH`. These describe non-cacheable 64-bit BAR windows, per-window VMIDs, MMSCH coherency/VM/privilege/swap/read/write/drop controls, clean-status bits, and MMSCH RAS fatal/PMI/rearm/ready fields.
- UVD context clock and scratch registers: `UVD_CGC_MEM_CTRL`, `UVD_CGC_CTRL2`, `UVD_CGC_MEM_DS_CTRL`, `UVD_CGC_MEM_SD_CTRL`, `UVD_SW_SCRATCH_00` through `_15`, and `UVD_IH_SEM_CTRL`. These cover light-sleep, deep-sleep, shutdown, dynamic clock ramp, software scratch storage, and interrupt/semaphore stall/status/VMID/user-data/ring fields.
- LMI adapter and memcheck fields: `UVD_LMI_CRC0` through `UVD_LMI_CRC15`, `UVD_LMI_SWAP_CNTL2`, `UVD_MEMCHECK_SYS_INT_EN`, `UVD_MEMCHECK_SYS_INT_STAT`, `UVD_MEMCHECK_SYS_INT_ACK`, `UVD_MEMCHECK_VCPU_INT_EN`, `UVD_MEMCHECK_VCPU_INT_STAT`, `UVD_MEMCHECK_VCPU_INT_ACK`, and the second-bank `UVD_MEMCHECK2_*` status/ack registers. These expose CRC readbacks, byte-swap policy, and interrupt enable/status/ack masks for UVD memory range checks across RE, IT, MP, DB/DBW, CM, MIF, VCPU, IDCT, MPC, LBSI, RBC, BSP, scaler, and prefetch clients.
- UMSCH front-end scheduler registers: `VCN_UMSCH_MES_UTCL1_CNTL`, `VCN_UMSCH_MES_BUSY`, `VCN_UMSCH_RB_BASE_LO/HI`, `VCN_UMSCH_RB_SIZE`, `VCN_UMSCH_RB_RPTR`, `VCN_UMSCH_RB_WPTR`, `VCN_UMSCH_MASTINT_EN`, `VCN_UMSCH_IH_CTRL`, `VCN_UMSCH_SYS_INT_EN/STATUS/ACK/SRC`, `VCN_UMSCH_IH_CTX_CTRL`, `VCN_UMSCH_CGC_CTRL`, `VCN_UMSCH_CGC_STATUS`, and `VCN_UMSCH_CGC_MEM_CTRL`. These define UTCL1 retry/snoop/drop/invalidate controls, MES busy sub-states, ring buffer base/size/read/write pointers, interrupt controller fields, context ID, and scheduler clock/memory-gating controls.
- UMSCH debug, violation, and force registers: `UVD_INTERNAL_REG_VIOLATION_8`, `UVD_UMSCH_FORCE`, `UVD_UMSCH_DEBUG_INDEX`, `UVD_UMSCH_DEBUG_DATA_LO/HI`, `UVD_UMSCH_DEBUG_UTCL2_TCIU_IF`, and `UMSCH_MES_RESET_CTRL`. These expose internal access-violation address/master/op fields, instruction/data-cache GPUVM force bits, drop-disable force, debug indexed reads, UTCL2/TCIU debug data, and MES core soft reset.
- MES microcontroller control and CSR-like state: `VCN_MES_PRGRM_CNTR_START`, `VCN_MES_INTR_ROUTINE_START`, `VCN_MES_MTVEC`, `VCN_MES_CNTL`, `VCN_MES_PIPE_PRIORITY_CNTS`, `VCN_MES_PIPE0_PRIORITY` through `_PIPE3_PRIORITY`, `VCN_MES_HEADER_DUMP`, `VCN_MES_MIE`, `VCN_MES_INTERRUPT`, `VCN_MES_SCRATCH_INDEX/DATA`, `VCN_MES_INSTR_PNTR`, `VCN_MES_MSCRATCH`, `VCN_MES_MSTATUS`, `VCN_MES_MEPC`, `VCN_MES_MCAUSE`, `VCN_MES_MBADADDR`, `VCN_MES_MIP`, `VCN_MES_MCYCLE`, `VCN_MES_MTIME`, `VCN_MES_MINSTRET`, `VCN_MES_MISA`, `VCN_MES_MVENDORID`, `VCN_MES_MARCHID`, `VCN_MES_MIMPID`, `VCN_MES_MHARTID`, and `VCN_MES_MTIMECMP`. These define boot vectors, pipe reset/active/halt/cache-invalidate bits, priority controls, interrupts, scratch access, program counter, exception/status/timer/counter state, and machine identity readbacks.
- MES memory/cache/aperture setup: `VCN_MES_IC_OP_CNTL`, `VCN_MES_DC_BASE_CNTL`, `VCN_MES_DC_OP_CNTL`, `VCN_MES_LOCAL_*`, `VCN_MES_IC_BASE_*`, `VCN_MES_DC_BASE_*`, `VCN_MES_MIBASE_*`, `VCN_MES_MDBASE_*`, `VCN_MES_MIBOUND_*`, `VCN_MES_MDBOUND_*`, `VCN_MES_DC_APERTURE0_*` through `_15_*`, and `VCN_HYP_ME1_PIPE0/1_VMID_CNTL`. These describe instruction/data cache operations, VMID/cache policy/execute-disable settings, local instruction/data/scratch apertures, base and bound registers, 16 data-cache apertures with VMID and bypass mode, and hypervisor VMID allow/default controls.
- MES debug and miscellaneous data registers: `VCN_MES_DEBUG_INTERRUPT_INSTR_PNTR`, `VCN_MES_GP0` through `GP9`, `VCN_MES_DM_INDEX_ADDR/DATA`, `VCN_MES_DBG_FROM_RST`, `VCN_MES_PERFCOUNT_CNTL`, `VCN_MES_PENDING_INTERRUPT`, `VCN_MES_PRIV_LEVEL`, `VCN_MES_PRIV_LEVEL_VIOLATION_STATUS`, high halves of program/debug pointers, and `VCN_MES_INTERRUPT_DATA_16` through `_31`.

## Control Flow And Runtime Behavior

There is no control flow inside this header. The runtime pattern is indirect:

1. ASIC-specific AMDGPU files include the VCN 4.0.0 offset and shift/mask headers.
2. Code reads a register, uses `REG_SET_FIELD` or equivalent bit manipulation with these masks/shifts, and writes the result back through SOC15/VCN register helpers.
3. Hardware implements the actual side effects: UVD memory-clock gating, memcheck interrupt status, UMSCH ring activity, MES firmware boot, cache invalidation/priming, VM aperture translation, and interrupt delivery.

The strongest concrete consumer in this source tree is `drivers/gpu/drm/amd/amdgpu/umsch_mm_v4_0.c`. Its UMSCH firmware load path clears `UMSCH_MES_RESET_CTRL.MES_CORE_SOFT_RESET`, programs `VCN_MES_CNTL` reset/halt/active/cache bits, sets `VCN_MES_IC_BASE_CNTL` VMID/execute/cache policy, writes instruction and interrupt start addresses, configures local instruction and data apertures, writes `VCN_MES_IC_BASE_*`, `VCN_MES_DC_BASE_*`, `VCN_MES_MIBOUND_LO`, and `VCN_MES_MDBOUND_LO`, forces IC/DC GPUVM through `UVD_UMSCH_FORCE`, invalidates/primes the instruction cache with `VCN_MES_IC_OP_CNTL`, releases the MES core, and then polls `VCN_MES_MSTATUS_LO` for the firmware-ready value.

The same file's ring setup programs `VCN_UMSCH_RB_BASE_LO/HI` and `VCN_UMSCH_RB_SIZE`, and stores `VCN_UMSCH_RB_WPTR`/`VCN_UMSCH_RB_RPTR` offsets for later ring operation. Older UVD generation files also use the shared `UVD_CGC_MEM_CTRL` field model to toggle memory low-power behavior, making this chunk part of the broader AMD media clock-gating contract.

## State And Persistence Behavior

The macros hold no software state and persist nothing by themselves. They describe stateful hardware registers whose values remain in the VCN, UVD, UMSCH, MES, LMI, and memcheck blocks until firmware, the driver, reset logic, power gating, or suspend/resume restore paths change them.

State represented by this chunk includes MMSCH non-cacheable BAR base/VMID mappings, MMSCH coherency/drop/swap controls, RAS enable/rearm/ready bits, UVD memory light/deep/shutdown sleep enables, dynamic clock ramp settings, scratch words, IH/semaphore state, LMI CRC readbacks, swap policy, memcheck interrupt enable/status/ack latches, UMSCH ring base/size/pointers, UMSCH busy and clock-gating status, MES boot vectors, control and machine-status registers, cache operation triggers, firmware-visible GP registers, timer/counter/identity state, local and translated memory aperture windows, DC aperture VMID/bypass controls, and hypervisor VMID permissions.

Access type is not encoded in the macro names. Some fields are persistent configuration, some are read-only status, some are write-one-to-ack interrupt bits, some are hardware-updated counters or pointers, and some are sequencing-sensitive commands such as cache invalidate/prime or reset/halt release. Consumers must preserve reserved bits and follow the hardware programming sequence for each register class.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_0_offset.h`, which supplies address macros such as `regUVD_LMI_MMSCH_NC*_64BIT_BAR_*`, `regVCN_UMSCH_RB_BASE_LO`, and `regVCN_MES_CNTL`. The shift/mask header alone cannot identify where a register lives; it only defines the bit layout once a consumer has the address.

Primary integration points are:

- AMDGPU UMSCH support in `amdgpu/umsch_mm_v4_0.c`, which relies on the `VCN_MES_*`, `UVD_UMSCH_FORCE`, `UMSCH_MES_RESET_CTRL`, and `VCN_UMSCH_RB_*` fields for firmware boot and ring setup.
- AMDGPU SOC15 register helpers and field helpers, especially `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_UMSCH`, `SOC15_WAIT_ON_RREG`, and `SOC15_REG_OFFSET`.
- AMD media clock-gating and power paths that use UVD/VCN CGC memory low-power controls and status bits.
- Interrupt handling and diagnostic paths that may enable, read, and acknowledge `UVD_MEMCHECK*`, `VCN_UMSCH_SYS_INT_*`, `VCN_UMSCH_IH_CTRL`, `UVD_IH_SEM_CTRL`, violation, debug, and pending-interrupt fields.
- Firmware and PSP load paths, because the values programmed into MES instruction/data base, bound, local aperture, GP, cache, and reset/control registers determine how the UMSCH microcontroller fetches and executes its firmware.

The generated macro names are a compile-time contract. Missing or renamed symbols usually fail to build, but wrong numeric masks or shifts can compile cleanly and produce hardware misconfiguration.

## Risks And Edge Cases

- The chunk starts in the middle of the MMSCH NC BAR sequence. `UVD_LMI_MMSCH_NC0_*` and `UVD_LMI_MMSCH_NC1_64BIT_BAR_LOW` are outside this chunk, so the final per-file report should merge neighboring chunks before describing the full NC aperture set.
- MES boot sequencing is sensitive. Incorrect `VCN_MES_CNTL`, `UMSCH_MES_RESET_CTRL`, `VCN_MES_IC_BASE_CNTL`, `VCN_MES_IC_OP_CNTL`, or start-address masks can leave firmware halted, executing from the wrong address, using a bad VMID, or failing the `VCN_MES_MSTATUS_LO` readiness poll.
- Base/mask/bound fields have alignment assumptions: instruction base low starts at bit 12, data base low starts at bit 16, UMSCH ring base low starts at bit 6, and several bound/aperture registers expose full 32-bit masks. Wrong shifts can silently truncate addresses or widen/narrow accessible firmware memory.
- UMSCH ring pointer and size fields use the same `WPTR`-named bit layout in size, read-pointer, and write-pointer registers. Consumers must not infer semantics from the field name alone without the register context.
- Interrupt and memcheck groups contain enable, status, and ack registers with similar field names. Mixing a status mask with an ack write, or acknowledging the wrong low/high error bit, can lose diagnostics or leave interrupt storms uncleared.
- Low-power fields in `UVD_CGC_MEM_CTRL`, `UVD_CGC_MEM_DS_CTRL`, and `UVD_CGC_MEM_SD_CTRL` target many subblocks. Wrong masks can block power savings or gate a memory domain while decode/scheduler firmware still needs it.
- RAS and violation/debug registers may expose latched fault data or rearm behavior. Treating those fields as ordinary writable control bits can hide faults or cause repeated fatal-error signaling.
- `UVD_LMI_MMSCH_CTRL` combines coherency, VM, privilege, swap, read/write, and drop policy. A field-width or polarity error can produce DMA coherency bugs, byte-order corruption, dropped transactions, or access with the wrong privilege/VM context.
- The repeated `VCN_MES_DC_APERTURE0` through `_15` triplets are easy to mis-index. An off-by-one register in generated data can affect only one aperture and appear only with specific firmware memory mappings.
- The file ends with `#endif`; this is the final chunk for the header. Any automated merge should account for the terminating guard but should not treat it as a runtime artifact.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with VCN 4.x and UMSCH support enabled so include dependencies, `REG_SET_FIELD` expansion, and direct users of `VCN_MES_*`, `UVD_UMSCH_FORCE`, `UMSCH_MES_RESET_CTRL`, and `VCN_UMSCH_RB_*` symbols are checked.
- Mechanically compare this line range against the authoritative VCN 4.0.0 register database and companion `vcn_4_0_0_offset.h`, verifying every field has the expected mask/shift pair and every register address has a matching bit-layout definition.
- Cross-check repeated families for consistency: MMSCH NC BAR low/high pairs, 16 scratch registers, memcheck enable/status/ack banks, 16 DC aperture base/mask/control triplets, interrupt data registers 16-31, and GP register low/high pairs.
- Runtime smoke should cover UMSCH firmware load, including MES reset/halt release, instruction cache invalidate/prime, instruction/data base programming, PSP and non-PSP firmware-load paths, and the `VCN_MES_MSTATUS_LO` ready poll.
- Ring tests should validate UMSCH ring base, size, read pointer, write pointer, doorbell, and interrupt delivery under command submission.
- Media stress should exercise VCN decode/encode workloads with memory low-power toggles, suspend/resume, power-gating transitions, and clock-gating entry/exit to catch bad CGC memory control masks.
- Fault-path tests should inject or observe memcheck/RAS/internal-violation conditions where possible, confirming enable/status/ack bits map to the intended low/high client errors and that diagnostics are not lost.
- Watch kernel logs for UMSCH firmware load failures, `regVCN_MES_MSTATUS_LO` timeout messages, ring stalls, interrupt storms, memory check errors, VM faults, bad firmware fetches, decode hangs, and regressions that appear only after suspend/resume or power-gating cycles.

## Cross-Chunk Notes

The previous chunk is needed for the beginning of the MMSCH non-cacheable BAR register set. This chunk closes the header and has no following `vcn_4_0_0_sh_mask.h` content, but final reconciliation should still merge all chunks for the source file before making complete claims about the generated VCN 4.0.0 register namespace.
