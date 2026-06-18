# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003477`: lines 1-2377, `Docs/researches/chunks/subset-b-003477_research.md`
- `subset-b-003478`: lines 2378-4708, `Docs/researches/chunks/subset-b-003478_research.md`
- `subset-b-003479`: lines 4709-7202, `Docs/researches/chunks/subset-b-003479_research.md`
- `subset-b-003480`: lines 7203-8262, `Docs/researches/chunks/subset-b-003480_research.md`

## Chunk Research

### subset-b-003477: lines 1-2377

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_sh_mask.h lines 1-2377

## Scope

This chunk is the first 2,377 lines of the generated AMD VCN 5.3.0 shift/mask header. It contains preprocessor constants for register bit fields, not executable C. The companion register-offset header supplies MMIO register addresses; this file supplies `__SHIFT` and `_MASK` constants that AMDGPU VCN code uses with SOC15 register helpers to compose, update, poll, and acknowledge hardware register fields.

The covered address blocks are:

- `uvdctxind`: memory clock/power gating, software scratch registers, and interrupt-handler/semaphore metadata.
- `lmi_adp_indirect`: LMI CRC, byte-swap controls, and memcheck interrupt enable/status/ack registers for system and VCPU interrupt domains.
- `uvd_uvd_pg_dec`: VCN/UVD dynamic power-gating controls, scratch/state registers, firmware version, page-fault status, feature/version discovery, doorbell controls, ring enable/write-pointer controls, and ring pointer registers.
- `uvd_uvddec`: top-level decode standard selection, broad UVD clock-gating controls, and the beginning of the SUVD clock-gating matrix through the first part of `SMP_SUVD_CGC_GATE`.

Line 2377 ends inside `SMP_SUVD_CGC_GATE`; the following chunk is needed for the remaining masks and later register families.

## Purpose

`vcn_5_3_0_sh_mask.h` centralizes the bit layout for VCN 5.3.0 registers. The naming convention is consistent:

- `<REGISTER>__<FIELD>__SHIFT` gives the least significant bit for a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit masked field range.

Consumers should use these symbols instead of literal bit positions when programming the VCN hardware. The field definitions in this chunk cover power and clock control, DPG handshakes, firmware-visible scratch state, ring-buffer enablement, doorbell routing, feature discovery, page-fault/error reporting, and memcheck interrupt handling.

## Important Macro Families

### Context-indirect clock and scratch registers

The `uvdctxind` block starts with low-power memory controls:

- `UVD_CGC_MEM_CTRL` has light-sleep enable bits for LMI MC, MPC, MPRD, WCB, UDEC subblocks, SYS, VCPU, MIF, LCM, MMSCH, and MPC1, plus `LS_SET_DELAY` and `LS_CLEAR_DELAY` timing fields.
- `UVD_CGC_CTRL2` controls dynamic OCLK/RCLK ramp enable and a gater divider field.
- `UVD_CGC_MEM_DS_CTRL` and `UVD_CGC_MEM_SD_CTRL` mirror the same subblock map for deep-sleep and shutdown-style memory controls.
- `UVD_SW_SCRATCH_00` through `UVD_SW_SCRATCH_15` are full-width software scratch registers.
- `UVD_IH_SEM_CTRL` provides interrupt-handler and semaphore stall/status-clean controls plus IH VMID, user-data, and ring-id fields.

These fields are integration points for power-management, clock-gating, firmware handshakes, and interrupt routing. They do not store kernel state themselves; they describe persistent hardware registers that host driver and firmware can both observe or modify according to the ASIC contract.

### LMI CRC and memcheck interrupt registers

The `lmi_adp_indirect` block begins with full-width `UVD_LMI_CRC0` through `UVD_LMI_CRC3` and `UVD_LMI_CRC10` through `UVD_LMI_CRC15` CRC32 fields, followed by `UVD_LMI_SWAP_CNTL2` byte-swap selectors for SCPU read/write, atomic, CENC, and FBC key traffic.

The dominant portion of this block is the memcheck interrupt matrix:

- `UVD_MEMCHECK_SYS_INT_EN` and `UVD_MEMCHECK_VCPU_INT_EN` enable error reporting for RE, IT, MP, DB, DBW, CM, MIF reference/DBW/colocated/BSP/SCLR/SCLR2 paths, VCPU, SRE, read-side paths, RBC, and PREF.
- `UVD_MEMCHECK_SYS_INT_STAT` and `UVD_MEMCHECK_VCPU_INT_STAT` expose low/high error status bits for the first set of blocks.
- `UVD_MEMCHECK_SYS_INT_ACK` and `UVD_MEMCHECK_VCPU_INT_ACK` provide matching low/high acknowledge bits.
- `UVD_MEMCHECK2_SYS_INT_STAT`, `UVD_MEMCHECK2_SYS_INT_ACK`, `UVD_MEMCHECK2_VCPU_INT_STAT`, and `UVD_MEMCHECK2_VCPU_INT_ACK` carry the second status/ack bank for read-side CM/DB/MIF/IDCT/MPC/LBSI/RBC plus BSP2/BSP3, SCLR/SCLR2, and PREF low/high errors.

The enable/status/ack triplets are highly symmetrical but not interchangeable. System and VCPU domains have separate bit layouts for some later fields, so interrupt handling code must use the matching domain-specific constants.

### Dynamic power-gating and firmware-visible state

The `uvd_uvd_pg_dec` block maps the VCN dynamic power-gating control surface:

- `UVD_IPX_DLDO_CONFIG`, `UVD_IPX_DLDO_CONFIG_ONO0`, and `UVD_IPX_DLDO_CONFIG_ONO1` define ONO power-configuration fields; `UVD_IPX_DLDO_STATUS` reports ONO0 through ONO5 power status.
- `UVD_POWER_STATUS` reports VCN power status, PG mode, CG mode, PG enable, RBC/SW ring snoop-disable bits, and `STALL_DPG_POWER_UP`.
- `UVD_JPEG_POWER_STATUS` does the same for JPEG/JDPG and DCT decoder snoop-disable state.
- `UVD_DPG_LMA_CTL`, `UVD_DPG_LMA_DATA`, `UVD_DPG_LMA_MASK`, and `UVD_DPG_LMA_CTL2` define local-memory access controls, data/mask registers, direct SRAM access selection, FIFO-direct access, and video/JPEG write pointers.
- `UVD_DPG_PAUSE` provides request/ack pairs for JPEG and non-JPEG DPG pause.
- `UVD_MC_DJPEG_RD_SPACE` and `UVD_MC_DJPEG_WR_SPACE` expose DJPEG read/write space fields.
- `UVD_PG_IND_INDEX` and `UVD_PG_IND_DATA` provide a small indirect-index/data register pair.

These fields imply order-sensitive control flow in consumers: request DPG pause, poll the corresponding ack/status bit, update local-memory or power state, then release or resume. Misordered DPG access can touch a gated block or race firmware-owned state.

### Scratch, firmware, security, page fault, and feature registers

The same `uvd_uvd_pg_dec` block also includes firmware and diagnostic state:

- `UVD_SCRATCH1` through `UVD_SCRATCH15` and `UVD_FREE_COUNTER_REG` are full-width scratch/counter registers.
- `UVD_DPG_LMI_VCPU_CACHE_64BIT_BAR_LOW/HIGH`, `UVD_DPG_VCPU_CACHE_OFFSET0`, and `UVD_DPG_LMI_VCPU_CACHE_VMID` define DPG-mode VCPU cache address and VMID plumbing.
- `UVD_REG_FILTER_EN` enables register filtering and privilege controls for MMSCH, video, and JPEG access.
- `UVD_SECURITY_REG_VIO_REPORT` reports host, VCPU, video, DPG, JPEG, and JDPG register-violation sources.
- `UVD_FW_VERSION`, `UVD_VERSION`, and `VCN_FEATURES` expose firmware version, hardware version, instance ID, and feature availability such as video decode/encode, MJPEG decode/encode, virtualization, legacy H.264 decode, UDEC, MJPEG2 IDCT, SCLR, VP9, AV1, EFC, HDR2SDR, dual MJPEG, and AV1 encode.
- `UVD_PF_STATUS` reports and clears page faults for JPEG, non-JPEG, encoder0 through encoder4, EJPEG, and ATOMIC paths.
- `UVD_PF_STATUS` and `UVD_SECURITY_REG_VIO_REPORT` are important error-path observability points during VM faults, virtualization isolation faults, and firmware-access-policy failures.

The feature and version fields are read-only discovery inputs from the driver perspective. Scratch and page-fault clear fields are mutable hardware state, often shared between host, firmware, and interrupt/error paths.

### Counters, clocks, virtualization, and doorbells

The chunk defines several runtime plumbing registers:

- `CC_UVD_HARVESTING` reports whether MMSCH or UVD is disabled by harvesting.
- `CC_UVD_VCPU_ERR_DETECT_*`, `CC_UVD_VCPU_ERR`, and `CC_UVD_VCPU_ERR_INST_ADDR_*` describe VCPU error-detection ranges, VCPU error status, and faulting instruction address halves.
- `UVD_GFX8_ADDR_CONFIG` and `UVD_GFX10_ADDR_CONFIG` expose address/tiling configuration fields, including pipe/interleave/bank/SE/RA and RB mapping fields for the GFX10 form.
- `UVD_GPCNT2_*` and `UVD_GPCNT3_*` provide clear/start/count direction, frequency/divider, target, and status fields for general counters.
- `UVD_VCLK_DS_CNTL` and `UVD_DCLK_DS_CNTL` control and report video/decode clock deep-sleep state, including hysteresis counters.
- `UVD_TSC_LOWER` and `UVD_TSC_UPPER` expose a timestamp-style counter split across 32-bit and 24-bit fields.
- `UVD_GPUIOV_STATUS` reports VF enable state for GPU IOV.
- `VCN_UMSCH_CNTL` enables UMSCH firmware.
- `VCN_JPEG_DB_CTRL`, `VCN_RB1_DB_CTRL` through `VCN_RB4_DB_CTRL`, `VCN_UMSCH_RB_DB_CTRL`, `VCN_RB_DB_CTRL`, and `VCN_AGDB_CTRL0` through `VCN_AGDB_CTRL5` define doorbell offset, enable, and hit fields; `VCN_AGDB_MASK0` through `VCN_AGDB_MASK5` provide offset masks.

Doorbell offset masks use bits 2 through 27 with enable and hit bits at the top of the register. Callers must preserve alignment and avoid treating the offset as an arbitrary byte value.

### Ring enable and pointer registers

The ring-control portion of `uvd_uvd_pg_dec` includes:

- `VCN_RB_ENABLE` enable bits for the main RB, JPEG RB, RB1 through RB4, UMSCH RB, EJPEG RB, audio RB, and three DCT decoder RBs.
- `VCN_RB_WPTR_CTRL` write-pointer control/status-enable bits for main RB, JPEG, RB1 through RB4, UMSCH, EJPEG, and audio.
- `UVD_RB_RPTR`/`UVD_RB_WPTR`, `UVD_RB_RPTR2`/`UVD_RB_WPTR2`, `UVD_RB_RPTR3`/`UVD_RB_WPTR3`, `UVD_RB_RPTR4`/`UVD_RB_WPTR4`, `UVD_OUT_RB_RPTR`/`UVD_OUT_RB_WPTR`, `UVD_AUDIO_RB_RPTR`/`UVD_AUDIO_RB_WPTR`, and `UVD_RBC_RB_RPTR`/`UVD_RBC_RB_WPTR` define pointer fields in bits 4 through 22.

These fields sit on the boundary between host command submission, firmware scheduling, and hardware consumption. Pointer fields are shifted/aligned; writing raw unshifted or unmasked values can truncate low bits or desynchronize ring state.

### Decode and SUVD clock-gating controls

The `uvd_uvddec` block begins with:

- `UVD_TOP_CTRL`, which selects codec standard and standard version.
- `UVD_CGC_GATE`, a broad per-subblock clock-gating bitmap for SYS, UDEC, MPEG2, REGS, RBC, LMI MC/UMC, IDCT, MPRD, MPC, LBSI, LRBBM, UDEC subblocks, WCB, VCPU, MMSCH, LCM0/1, MIF, VREG, PE, PPU, SMPATN, DRM, and VIDEO_ATOMIC.
- `UVD_CGC_CTRL`, which controls dynamic clock mode, delay timers, and per-subblock clock-gating mode fields for many of the same domains.
- `AVM_SUVD_CGC_GATE`, `EFC_SUVD_CGC_GATE`, `ENT_SUVD_CGC_GATE`, `IME_SUVD_CGC_GATE`, `PPU_SUVD_CGC_GATE`, `SAOE_SUVD_CGC_GATE`, `SCM_SUVD_CGC_GATE`, `SDB_SUVD_CGC_GATE`, `SIT0_NXT_SUVD_CGC_GATE`, `SIT1_NXT_SUVD_CGC_GATE`, `SIT2_NXT_SUVD_CGC_GATE`, `SIT_SUVD_CGC_GATE`, `SMPA_SUVD_CGC_GATE`, and the start of `SMP_SUVD_CGC_GATE`.

The SUVD gate registers repeat a 32-bit matrix of subblocks: SRE, SIT, SMP, SCM, SDB, H.264/HEVC variants, SCLR, UVD_SC, ENT, IME, HEVC decode/encode SIT paths, SITE, VP9 paths, EFC, SAOE, AV1 paths, FBC PCLK/CCLK, SCM_AV1, and SMPA. Most of these registers have both 32 shifts and 32 masks in the covered chunk, which makes them sensitive to copy/paste or generation errors.

## Control Flow and State Behavior

This header has no functions, branches, locks, or local persistence. Runtime control flow is supplied by AMDGPU VCN code that includes the header and performs MMIO operations. The typical implied sequences are:

1. Discover instance/version/features using `UVD_VERSION`, `VCN_FEATURES`, harvesting, and IOV status fields.
2. Program power/clock policy through CGC memory controls, DLDO/PG status fields, DPG LMA controls, VCLK/DCLK deep-sleep controls, and UVD/SUVD clock-gate registers.
3. Configure firmware-visible memory and state through DPG VCPU cache BAR/offset/VMID, scratch registers, UMSCH enable, and address-config fields.
4. Enable rings and doorbells through `VCN_RB_ENABLE`, `VCN_RB_WPTR_CTRL`, doorbell control registers, and ring read/write pointer fields.
5. Enable and handle error paths through memcheck interrupt enable/status/ack registers, page-fault status/clear bits, security violation reports, and VCPU error registers.
6. During shutdown, suspend, reset, or DPG transitions, poll status/ack fields and gate clocks only after the relevant blocks have paused or drained.

Hardware register state persists until reset, power loss, firmware reinitialization, or explicit reprogramming. Scratch registers, ring pointers, doorbell hit bits, page-fault bits, memcheck status bits, and clock/power status bits can change asynchronously from host software because firmware and hardware engines also update them.

## Dependencies and Integration Points

- Depends on the matching VCN 5.3.0 register offset/header files for the `mm*` register addresses and address block selection.
- Consumed by AMDGPU VCN generation code through the ASIC register include set, alongside SOC15 register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, masked write helpers, polling helpers, and DPG-mode write paths.
- Integrates with AMDGPU power-management and runtime PM code through power status, DPG pause/LMA, VCLK/DCLK deep-sleep, and CGC gate/control masks.
- Integrates with VCN ring scheduling and firmware queues through `VCN_RB_ENABLE`, `VCN_RB_WPTR_CTRL`, doorbell controls, and the ring pointer registers.
- Integrates with interrupt and fault handling through memcheck SYS/VCPU enable/status/ack triplets, `UVD_PF_STATUS`, `UVD_SECURITY_REG_VIO_REPORT`, `UVD_IH_SEM_CTRL`, and VCPU error registers.
- Integrates with virtualization paths through `UVD_GPUIOV_STATUS`, VMID fields, privileged register filter bits, poisoned/error status interpretation, and per-instance feature/version fields.
- The generated names match adjacent VCN generations conceptually, but bit positions differ by ASIC. Consumers must include the 5.3.0 header for 5.3.0 hardware rather than reusing older VCN masks.

## Risks

- Generated-layout drift is high impact. A wrong mask or shift can compile cleanly while programming the wrong hardware bit, causing hangs, missed interrupts, lost faults, or invalid power transitions.
- Read-modify-write code must clear masks before inserting shifted field values. This is especially important for multi-bit fields such as delay timers, power config/status, doorbell offsets, address-config fields, counter frequency/divider fields, and ring pointers.
- Interrupt-domain confusion is easy: SYS, VCPU, MEMCHECK2 SYS, and MEMCHECK2 VCPU status/ack fields look similar but have different register names and some different bit placement.
- DPG and power-gating fields are handshake-sensitive. Updating DPG local-memory access or clock-gating state without waiting on request/ack/status can race gated hardware.
- Doorbell and ring pointer fields are aligned fields. Unshifted byte offsets or pointers can be truncated by masks, causing queues to stop or consume the wrong commands.
- Security and page-fault clear bits can hide evidence if cleared too early. Error handlers should capture status before acknowledging or clearing.
- Chunk-boundary risk: this work item ends in the middle of `SMP_SUVD_CGC_GATE`. Any final per-file reconciliation must combine the next chunk before treating that register as complete.
- Manual edits to this generated-style header should be avoided unless backed by the ASIC register database or a hardware-spec correction.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Build coverage for VCN 5.3.0 paths, catching missing or misspelled generated symbols.
- VCN firmware bring-up logs showing expected `UVD_VERSION`, `VCN_FEATURES`, firmware version, harvesting, and IOV status values.
- Ring submission tests confirming doorbell hits, write-pointer controls, and read/write pointers advance under `VCN_RB_ENABLE`, `VCN_RB_WPTR_CTRL`, and `UVD_RB_*` masks.
- Suspend/resume, runtime-PM, and DPG-mode tests that exercise `UVD_DPG_PAUSE`, `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, DLDO status, VCLK/DCLK deep-sleep controls, and CGC gate/control masks without timeout.
- Fault-injection or error-path tests that observe and acknowledge memcheck SYS/VCPU interrupts, page-fault status, security violation reports, and VCPU error address/status fields.
- Virtualization tests that verify VF enable state, VMID fields, register filter privilege bits, and per-instance feature/version fields.
- Clock-gating diagnostics that compare `UVD_CGC_GATE`, `UVD_CGC_CTRL`, and SUVD gate masks against expected subblock idle/gated state during decode, encode, JPEG, and AV1/VP9 workloads.

### subset-b-003478: lines 2378-4708

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_sh_mask.h lines 2378-4708

## Scope And Purpose

This chunk is a generated AMDGPU VCN 5.3.0 shift/mask header segment for the UVD/VCN register block. It provides C preprocessor constants that describe bit positions and masks for clock-gating, interrupt, firmware mailbox, ring-buffer, context, decode-control, scratch, audio ring-buffer, status, and busy-state registers. The companion `vcn_5_3_0_offset.h` file supplies the register offsets, while this file supplies the field layout needed to compose and decode 32-bit register values.

The range starts in the middle of the `SMP_SUVD_CGC_GATE` mask list and ends in the middle of `UVD_ENC_PIPE_BUSY`. Those partial blocks must be reconciled with adjacent chunks when the final per-file document is assembled. Within this chunk, however, the complete register-comment blocks show the local hardware contract for VCN 5.3.0 sub-block gating and interrupt/status management.

There is no executable code here. The API surface is ABI-like hardware description: downstream AMDGPU code includes this header and uses stable symbolic macro names instead of open-coded shifts and bit masks while programming VCN/JPEG firmware bring-up, ring buffers, power management, interrupt handling, virtualization mailboxes, and diagnostics.

## Register Field Groups

The first large group covers SUVD clock-gating gate masks. `SRE_SUVD_CGC_GATE` and `UVD_SUVD_CGC_GATE` repeat the 32-bit layout used by the preceding `SMP_SUVD_CGC_GATE`: core sub-block enables for `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, codec-specific H.264/HEVC/VP9/AV1 paths, `SCLR`, `UVD_SC`, `ENT`, `IME`, `EFC`, `SAOE`, `FBC_PCLK`, `FBC_CCLK`, and `SMPA`. These are one-bit fields spanning bits 0 through 31.

The `*_SUVD_CGC_GATE2` blocks add a second-generation gate layout for `AVM`, `DBR`, `ENT`, `IME`, `SAOE`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, `SMPA`, `SMP`, `SRE`, and `UVD`. Each block exposes the same fifteen one-bit fields: `MPBE0`, `MPBE1`, `SIT_AV1`, `SDB_AV1`, `MPC1`, `SRE_AV1_ENC`, `CDEFE`, `AVM_0`, `AVM_1`, `SIT_NXT_CMN`, `SIT_NXT_DEC`, `SIT_NXT_ENC`, `SMPN_ENC`, `SMPN_DEC`, and `MPCMIF`. These fields describe newer AV1 and next-pipeline clock domains shared across many VCN sub-units.

The `*_SUVD_CGC_CTRL` blocks provide mode/control masks for individual sub-block clock-gating behavior. Blocks for `AVM`, `DBR`, `EFC`, `ENT`, `IME`, `PPU`, `SAOE`, `SCM`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, `SMPA`, `SMP`, `SRE`, and `UVD` share a layout with codec and pipeline mode bits such as `SRE_MODE`, `SIT_MODE`, `SMP_MODE`, `SCM_MODE`, `SDB_MODE`, H.264/HEVC/VP9/AV1 mode bits, `SCLR_MODE`, `UVD_SC_MODE`, `ENT_MODE`, `IME_MODE`, `SITE_MODE`, `EFC_MODE`, `SAOE_MODE`, `FBC_PCLK`, `FBC_CCLK`, and `CDEFE_MODE`. This mirrors the gate blocks but controls clock-gating policy rather than only gate selection/status.

`UVD_CGC_CTRL3` extends clock-gating control with a packed `CGC_CLK_OFF_DELAY` field at bits 0-7 and single-bit mode fields for `LCM0`, `LCM1`, `MIF`, `VREG`, `PE`, `PPU`, `SMPATN`, `DRM`, and `VIDEO_ATOMIC`. These fields are likely programmed during block initialization and power-management transitions.

The GPCOM registers are firmware/system command mailbox fields. `UVD_GPCOM_VCPU_DATA0` and `UVD_GPCOM_VCPU_DATA1` expose full 32-bit VCPU data payloads. `UVD_GPCOM_SYS_CMD` contains `CMD_SEND` at bit 0, a 30-bit `CMD` payload at bits 1-30, and `CMD_SOURCE` at bit 31. `UVD_GPCOM_SYS_DATA0` and `UVD_GPCOM_SYS_DATA1` mirror the full-width system data payload registers.

The VCPU interrupt group includes `UVD_VCPU_INT_EN`, `UVD_VCPU_INT_STATUS`, `UVD_VCPU_INT_ACK`, and `UVD_VCPU_INT_ROUTE`. The enable/status/ack registers cover address faults, semaphore timeouts, software ring interrupts `SW_RB1` through `SW_RB5`, ring-buffer/controller faults, `LBSI`, `UDEC`, LMI AXI errors, `SUVD`, read-pointer writes, job starts, page faults, `IDCT`, `MPRD`, `AVM`, clock-switch, MIF hardware interrupt, firmware driver request, and firmware driver ack events. `UVD_VCPU_INT_STATUS` additionally has `GPCOM_INT` at bit 20. `UVD_VCPU_INT_ROUTE` routes MIF hardware interrupt, driver-to-firmware request, and driver-to-firmware ack events.

The SUVD interrupt group exposes `UVD_SUVD_INT_EN`, `UVD_SUVD_INT_STATUS`, and `UVD_SUVD_INT_ACK` with packed function-interrupt ranges and error bits for `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, and `SMPA`. The later `UVD_SUVD_INT_STATUS2`, `UVD_SUVD_INT_EN2`, and `UVD_SUVD_INT_ACK2` provide a smaller second bank for `SMPA` and `SDB_AV1` function/error interrupts.

The encoder VCPU interrupt group defines `UVD_ENC_VCPU_INT_EN`, `UVD_ENC_VCPU_INT_STATUS`, and `UVD_ENC_VCPU_INT_ACK` for encoder `VR` and `LP` interrupts. `UVD_MASTINT_EN` gates top-level VCPU, system, encoder, and decoder interrupt paths. `UVD_SYS_INT_EN`, `UVD_SYS_INT_STATUS`, and `UVD_SYS_INT_ACK` provide system-visible interrupt masks/status/acknowledge bits for software rings, trap/status routing, semaphore faults, context writes, and writeback paths.

The control and identity registers include `UVD_DRV_FW_MSG`, `UVD_FW_DRV_MSG_ACK`, `UVD_JOB_DONE`, `UVD_CBUF_ID`, `UVD_CONTEXT_ID`, `UVD_CONTEXT_ID2`, `UVD_NO_OP`, `UVD_IOV_ACTIVE_FCN_ID`, `UVD_IOV_MAILBOX`, `UVD_IOV_MAILBOX_RESP`, `UVD_RB_ARB_CTRL`, `UVD_CTX_INDEX`, `UVD_CTX_DATA`, `UVD_CXW_WR`, `UVD_CXW_WR_INT_ID`, `UVD_CXW_WR_INT_CTX_ID`, and `UVD_CXW_INT_ID`. These fields support firmware-driver messages, job completion tracking, SR-IOV active function/mailbox communication, ring-buffer arbitration, indirect context register access, and context writeback interrupt metadata.

The ring-buffer fields define four input ring buffers and one output ring buffer. `UVD_RB_BASE_LO`, `UVD_RB_BASE_LO2`, `UVD_RB_BASE_LO3`, `UVD_RB_BASE_LO4`, and `UVD_OUT_RB_BASE_LO` use base-low fields starting at bit 6, enforcing 64-byte alignment. The corresponding high-address registers expose full 32-bit high halves, and the `UVD_RB_SIZE*` and `UVD_OUT_RB_SIZE` fields start at bit 4, indicating size granularity aligned to 16 bytes. `UVD_AUDIO_RB_BASE_LO`, `UVD_AUDIO_RB_BASE_HI`, and `UVD_AUDIO_RB_SIZE` apply the same alignment model for the audio ring buffer.

The decode-control group includes MPEG2 error/control fields, frame address and geometry registers, and picture/buffer controls: `UVD_MPEG2_ERROR`, `UVD_YBASE`, `UVD_UVBASE`, `UVD_PITCH`, `UVD_WIDTH`, `UVD_HEIGHT`, `UVD_PICCOUNT`, `UVD_MPRD_INITIAL_XY`, `UVD_MPEG2_CTRL`, `UVD_MB_CTL_BUF_BASE`, `UVD_PIC_CTL_BUF_BASE`, `UVD_DXVA_BUF_SIZE`, `UVD_SCRATCH_NP`, and `UVD_CLK_SWT_HANDSHAKE`. Most are full-width data fields; notable packed fields include `UVD_MPRD_INITIAL_XY` with 16-bit initial X/Y coordinates, MPEG2 control sub-fields for the picture structure and decode mode, DXVA row/number size fields, and clock-switch handshake bits for send/receive.

`UVD_GP_SCRATCH0` through `UVD_GP_SCRATCH23` are full-width scratch registers. They provide 24 generic 32-bit data fields for firmware-driver communication, temporary state, or diagnostics, depending on the firmware protocol active for this IP generation.

The final status group in this chunk includes `UVD_VCPU_INT_STATUS2`, `UVD_VCPU_INT_ACK2`, and `UVD_VCPU_INT_EN2` for `SW_RB6`, `UVD_SUVD_CGC_STATUS2` for second-bank clock-gating status on `SMPA`, `MPBE1`, AV1/next-pipeline, `CDEFE`, `SIT0/1/2`, and FBC clocks, `UVD_STATUS` for RBC/VCPU/GPCOM/DRM busy and request state, and the beginning of `UVD_ENC_PIPE_BUSY`, which marks encoder pipe busy bits for IME, SMP, SIT, SDB, ENT, LCM, MDM, MIF, CDEFE, BSP/BSD, and SAOE paths.

## Important APIs, Types, And Functions

This chunk exports only preprocessor macros. There are no functions, structs, enums, typedefs, global variables, or inline helpers. The generated naming convention is:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's right-shift amount.
- `<REGISTER>__<FIELD>_MASK` gives the field's already-shifted 32-bit mask.

Driver code combines these macros with register-offset symbols such as `regSRE_SUVD_CGC_GATE`, `regUVD_CGC_CTRL3`, `regUVD_GPCOM_SYS_CMD`, `regUVD_RB_BASE_LO`, `regUVD_SUVD_INT_EN2`, and `regUVD_ENC_PIPE_BUSY` from `vcn_5_3_0_offset.h`. Consumers typically use AMDGPU register helpers to read a register, mask/shift a field, then write the updated value back, or to test status/ack bits after interrupt handling.

## Control Flow

The header itself has no runtime control flow. The implied control flow appears in consumers:

1. VCN/JPEG initialization programs clock-gating gate and control registers using the `*_SUVD_CGC_GATE*`, `*_SUVD_CGC_CTRL`, and `UVD_CGC_CTRL3` fields.
2. Ring-buffer setup writes aligned base-low, base-high, and size fields for input, output, and audio ring buffers.
3. Firmware mailbox paths write `UVD_GPCOM_SYS_DATA*`, set `UVD_GPCOM_SYS_CMD__CMD` and `CMD_SEND`, then poll or handle status/ack interrupts.
4. Interrupt setup enables selected bits in `UVD_VCPU_INT_EN`, `UVD_SYS_INT_EN`, `UVD_SUVD_INT_EN`, `UVD_ENC_VCPU_INT_EN`, and the second-bank enable registers.
5. Interrupt handlers read the corresponding status registers, branch based on set masks, write matching ack bits, and may inspect `UVD_STATUS`, `UVD_SUVD_CGC_STATUS2`, or `UVD_ENC_PIPE_BUSY` to determine whether hardware is idle or stuck.
6. Context and virtualization paths use `UVD_CTX_INDEX`/`UVD_CTX_DATA`, CXW fields, and IOV mailbox fields to exchange state with firmware or virtual functions.

Because enable, status, and ack registers often have similar but not identical layouts, handlers should use the macros for the specific register being accessed rather than reusing fields from a neighboring register by name.

## State And Persistence Behavior

The macros are compile-time constants and hold no state. They describe persistent hardware register state inside the VCN block. Clock-gating modes, interrupt enables, ring-buffer base/size programming, mailbox data, scratch contents, and arbitration settings persist until the block is reset, power-gated, firmware-reinitialized, or explicitly rewritten by the driver.

Interrupt status bits represent latched hardware events until acknowledged through the corresponding `*_ACK` register. Busy/status registers such as `UVD_STATUS`, `UVD_SUVD_CGC_STATUS2`, and `UVD_ENC_PIPE_BUSY` reflect live hardware state and can change asynchronously with firmware execution, DMA/ring activity, and clock/power transitions. Scratch and mailbox registers are shared firmware-driver state, so their contents are protocol-dependent and may be meaningful across short command sequences but not across reset or firmware reload.

Ring-buffer base and size fields are especially stateful: an incorrect write can redirect firmware DMA to the wrong memory or make the firmware consume a malformed queue until the ring is reprogrammed. The low-base fields' bit-6 alignment and size fields' bit-4 alignment are part of that persistence contract.

## Dependencies And Integration Points

The immediate dependency is `drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_offset.h`, which defines the register addresses and base indices for the names whose field layouts appear here. This shift/mask header must be used with the matching VCN 5.3.0 offset header; mixing it with another VCN generation would silently produce wrong register programming.

AMDGPU integration points include `drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.c`, which includes both `vcn_5_3_0_offset.h` and `vcn_5_3_0_sh_mask.h`, and broader VCN firmware support such as `amdgpu_vcn.c`, which names the `amdgpu/vcn_5_3_0.bin` firmware. SOC integration in `soc21.c` advertises the VCN 5.3.0 encode/decode codec capabilities. These files rely on the generated register layer for hardware bring-up, firmware command exchange, interrupt routing, and power-management behavior.

The field names also align with common AMDGPU helper idioms: register offsets identify what to access, masks select fields, and shifts pack or unpack values. Hardware specifications and generated register databases are the authority for these constants; the header is not self-validating.

## Risks And Edge Cases

The highest risk is a wrong bit position or mask in a generated definition. A single-bit error in clock-gating fields can leave a VCN sub-block ungated, gated while in use, or falsely reported as idle. A wrong interrupt enable/status/ack mask can cause missed events, interrupt storms, or acknowledgements of the wrong source.

The repeated `*_SUVD_CGC_GATE2` and `*_SUVD_CGC_CTRL` blocks are intentionally similar, which makes copy/paste or generation drift hard to spot in review. They should be compared against the authoritative VCN 5.3.0 register source rather than inferred from neighboring blocks.

Partial chunk boundaries are important. This range omits the beginning of `SMP_SUVD_CGC_GATE` and the tail of `UVD_ENC_PIPE_BUSY`; final research must merge this with adjacent chunks before treating either register as fully documented.

Ring-buffer address fields are alignment-sensitive. Low base fields mask off the low six bits, and size fields mask off the low four bits; callers must not pass arbitrary byte addresses or sizes without applying the hardware-required alignment. Similar full-width data fields are easy to misuse because the mask does not encode semantic constraints such as address space, firmware ownership, or write ordering.

Firmware mailbox and scratch registers are protocol-sensitive. The macros identify fields but do not specify when firmware owns a register, which writes are doorbells, or what ordering/barrier rules are required around `CMD_SEND`, interrupt ack, and scratch updates.

Ack registers may have write-one-to-clear or write-one-to-ack semantics. The header does not encode those side effects, so read/modify/write patterns must follow the hardware programming guide and existing driver conventions.

## Test Signals

There are no direct unit tests for this generated header. Useful validation signals are build and hardware integration tests:

- A kernel build covering `jpeg_v5_3_0.c` and any VCN 5.3.0 consumers catches missing or renamed macros.
- VCN/JPEG firmware load, ring initialization, encode/decode submission, and teardown should complete without firmware mailbox timeouts or invalid ring-buffer behavior.
- Interrupt tests should verify that VCPU, system, SUVD, encoder, and second-bank interrupt status bits are enabled and acknowledged through the matching register masks.
- Suspend/resume, runtime power management, and GPU reset tests should confirm clock-gating control/status fields are restored and do not leave VCN busy or inaccessible.
- Virtualization/SR-IOV tests should exercise `UVD_IOV_ACTIVE_FCN_ID`, `UVD_IOV_MAILBOX`, and `UVD_IOV_MAILBOX_RESP` paths without cross-function mailbox confusion.
- Diagnostic polling of `UVD_STATUS`, `UVD_SUVD_CGC_STATUS2`, and `UVD_ENC_PIPE_BUSY` should match expected idle/busy transitions during decode, encode, and clock-switch activity.

### subset-b-003479: lines 4709-7202

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_sh_mask.h lines 4709-7202

## Scope And Purpose

This chunk is a 2,494-line segment of AMD's generated VCN 5.3.0 register shift/mask header. It defines C preprocessor constants only: hardware register fields are exported as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. There are no functions, structs, enums, variables, branches, allocations, locks, or direct MMIO operations in this chunk.

The path sits under a `ceph-client` source mirror, but the content is AMDGPU media-engine register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU VCN/UVD/JPEG code that combines these field masks and shifts with address macros from the companion VCN 5.3.0 register address header and then reads or writes hardware through the SOC15/MMIO register helpers.

The chunk starts inside `UVD_ENC_PIPE_BUSY`: earlier shift definitions and some masks for that busy bitmap are in the previous chunk, while this range begins at `UVD_ENC_PIPE_BUSY__MIF_RD_GEN1_BUSY_MASK`. It continues through VCN/UVD power, reset, clock-gating, VCPU, LMI memory-interface, JRBC ring, JPEG/JMI, interrupt, and memcheck registers. It ends inside `JPEG_MEMCHECK_SYS_INT_ACK2`; the remaining `JPEG_MEMCHECK_SYS_INT_ACK2` masks and following file content are outside this chunk.

## Important APIs, Types, And Macros

The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position used to pack or unpack a field.
- `<REGISTER>__<FIELD>_MASK`: raw 32-bit field mask used for masked reads and writes.

Major register families in this chunk:

- VCN/UVD high-level power, reset, and clock state: `UVD_FW_POWER_STATUS`, `UVD_CNTL`, `UVD_SOFT_RESET`, `UVD_SOFT_RESET2`, `UVD_MMSCH_SOFT_RESET`, `UVD_WIG_CTRL`, `UVD_CGC_STATUS`, `UVD_CGC_UDEC_STATUS`, `UVD_SUVD_CGC_STATUS`, `CDEFE_SUVD_CGC_GATE`, `CDEFE_SUVD_CGC_GATE2`, and `CDEFE_SUVD_CGC_CTRL`. These fields describe per-subblock power-off status, software resets and reset-status readbacks, MMSCH lock/reset, WIG/AVM reset and forced clocks, clock-gating status, and clock-gating enable/mode bits for decode, encode, codec, AV1, FBC, CDEFE, MPBE, MPC, AVM, and next-generation SIT/SMP/MPCMIF blocks.
- VCPU command, cache, and debug controls: `UVD_GPCOM_VCPU_CMD`, `UVD_VCPU_CACHE_OFFSET0` through `UVD_VCPU_CACHE_OFFSET8`, `UVD_VCPU_CACHE_SIZE0` through `UVD_VCPU_CACHE_SIZE8`, `UVD_VCPU_NONCACHE_OFFSET0/1`, `UVD_VCPU_NONCACHE_SIZE0/1`, `UVD_VCPU_CNTL`, `UVD_VCPU_PRID`, `UVD_VCPU_TRCE`, `UVD_VCPU_TRCE_RD`, `UVD_VCPU_IND_INDEX`, and `UVD_VCPU_IND_DATA`. These cover host-to-VCPU command submission, cached/noncached firmware memory windows, VCPU clock enable, resets, abort/runstall, trace/debug selectors, JTAG enable, probe timeout, and indirect VCPU data access.
- LMI/ADP decode memory apertures and control: many `UVD_LMI_*_64BIT_BAR_LOW/HIGH` registers for RE, IT, MP, CM, DB, DBW, IDCT, MPRD, RBC ring/IB, LBSI, VCPU cache/noncache, CENC, SRE, MIF luma/chroma/DBW/coloc/BSP/BSD/scaler/imagepaste/privacy, plus `UVD_ADP_ATOMIC_CONFIG`, `UVD_LMI_ARB_CTRL2`, `UVD_LMI_VCPU_CACHE_VMIDS_MULTI`, `UVD_LMI_VCPU_NC_VMIDS_MULTI`, `UVD_LMI_LAT_CTRL`, `UVD_LMI_LAT_CNTR`, `UVD_LMI_AVG_LAT_CNTR`, `UVD_LMI_SPH`, `UVD_LMI_VCPU_CACHE_VMID`, `UVD_LMI_CTRL2`, `UVD_LMI_URGENT_CTRL`, `UVD_LMI_CTRL`, `UVD_LMI_STATUS`, `UVD_LMI_PERFMON_*`, `UVD_LMI_ADP_SWAP_CNTL`, `UVD_LMI_RBC_RB_VMID`, `UVD_LMI_RBC_IB_VMID`, `UVD_LMI_MC_CREDITS`, `UVD_LMI_ADP_IND_INDEX/DATA`, `UVD_LMI_ADP_PF_EN`, and `UVD_LMI_PREF_CTRL`. These fields describe 64-bit GPU addresses, VMIDs, byte-swap policy, data coherency, CRC controls, clean/idle status, urgent/QoS/stall thresholds, arbitration and credits, latency/perf counters, atomics, page-fault enablement, and prefetch programming.
- JPEG ring-buffer command processors: repeated `UVD_JRBC0_*`, `UVD_JRBC1_*`, `UVD_JRBC2_*`, and `UVD_JRBC3_*` register sets. Each JRBC instance has ring write/read pointers, ring control, IB size/update, urgent control, reference data, conditional-read timers, soft reset/status, buffer status, JPEG preempt command and fence data, ring size, and scratch. These macros are the field contract for programming and diagnosing four JPEG ring/IB engines.
- JPEG decode datapath registers: `UVD_JPEG_CNTL`, `UVD_JPEG_RB_BASE`, `UVD_JPEG_RB_WPTR`, `UVD_JPEG_RB_RPTR`, `UVD_JPEG_RB_SIZE`, `UVD_JPEG_DEC_CNT`, `UVD_JPEG_SPS_INFO`, `UVD_JPEG_SPS1_INFO`, `UVD_JPEG_RE_TIMER`, `UVD_JPEG_DEC_SCRATCH0`, `UVD_JPEG_INT_EN`, `UVD_JPEG_INT_STAT`, `UVD_JPEG_TIER_CNTL0/1/2`, `UVD_JPEG_TIER_STATUS`, `UVD_JPEG_OUTBUF_CNTL`, `UVD_JPEG_OUTBUF_WPTR/RPTR`, `UVD_JPEG_PITCH`, `UVD_JPEG_UV_PITCH`, `JPEG_DEC_Y_GFX8_TILING_SURFACE`, `JPEG_DEC_UV_GFX8_TILING_SURFACE`, `JPEG_DEC_GFX8_ADDR_CONFIG`, `JPEG_DEC_Y_GFX10_TILING_SURFACE`, `JPEG_DEC_UV_GFX10_TILING_SURFACE`, `JPEG_DEC_GFX10_ADDR_CONFIG`, `JPEG_DEC_ADDR_MODE`, `UVD_JPEG_OUTPUT_XY`, `UVD_JPEG_GPCOM_CMD/DATA0/DATA1`, `UVD_JPEG_SCRATCH1`, and `UVD_JPEG_DEC_SOFT_RST`. These cover JPEG decode mode, ring base/pointers/size, stream parameters, output buffers, tiling/address configuration, command mailbox, interrupts, tier controls, and soft reset.
- JPEG memory interface and JMI controls: `UVD_JPEG_DEC_PF_CTRL`, `UVD_LMI_JRBC_CTRL`, `UVD_LMI_JPEG_CTRL`, `JPEG_LMI_DROP`, `UVD_LMI_JRBC_IB_VMID`, `UVD_LMI_JRBC_RB_VMID`, `UVD_LMI_JPEG_VMID`, JPEG/JRBC/preempt/atomic 64-bit BARs, `UVD_JMI_DEC_SWAP_CNTL`, `UVD_JMI_ATOMIC_CNTL`, `UVD_JMI_ATOMIC_CNTL2`, `UVD_JADP_MCIF_URGENT_CTRL`, `UVD_JMI_URGENT_CTRL`, `UVD_JMI_CTRL`, `UVD_JMI_LAT_CTRL`, `UVD_JMI_LAT_CNTR`, `UVD_JMI_AVG_LAT_CNTR`, `UVD_JMI_PERFMON_*`, `UVD_JMI_CLEAN_STATUS`, and `UVD_JMI_CNTL`. These fields define page-fault handling, LMI/JRBC/JPEG arbitration, burst lengths, swaps, drop controls, VMIDs, preempt fences, atomic writes, urgent/QoS policy, latency counters, clean status, and JMI command control.
- JPEG system interrupts and memory-checking: `JPEG_SOFT_RESET_STATUS`, `JPEG_SYS_INT_EN`, `JPEG_SYS_INT_EN1`, `JPEG_SYS_INT_STATUS`, `JPEG_SYS_INT_STATUS1`, `JPEG_SYS_INT_ACK`, `JPEG_SYS_INT_ACK1`, `JPEG_MEMCHECK_CLAMPING_CNTL`, `JPEG_MEMCHECK_SAFE_ADDR`, `JPEG_MEMCHECK_SAFE_ADDR_64BIT`, `JPEG_MEMCHECK_SYS_INT_EN`, `JPEG_MEMCHECK_SYS_INT_EN1`, `JPEG_MEMCHECK_SYS_INT_STAT`, `JPEG_MEMCHECK_SYS_INT_STAT1`, `JPEG_MEMCHECK_SYS_INT_STAT2`, `JPEG_MEMCHECK_SYS_INT_ACK`, `JPEG_MEMCHECK_SYS_INT_ACK1`, and the start of `JPEG_MEMCHECK_SYS_INT_ACK2`. These fields enable, report, and acknowledge JPEG/JRBC/EJRBC/scalar/bitstream/output-buffer read/write errors, plus memcheck high/low address errors and safe-address clamping.

## Control Flow And Runtime Behavior

There is no executable control flow in this header. Runtime use is indirect:

1. ASIC-specific AMDGPU VCN/JPEG implementation files include a generated address header for VCN 5.3.0 offsets and this shift/mask header for field layout.
2. Driver startup, firmware boot, power management, reset, ring setup, command submission, interrupt handling, JPEG decode, and diagnostics build register values with these constants.
3. Register helpers such as SOC15 `RREG32`/`WREG32` variants, `REG_SET_FIELD`, and masked write helpers preserve unrelated fields while changing one hardware field.
4. Hardware then owns the actual state transitions: reset-status bits, busy/clean bits, command/ring pointers, interrupt status/acknowledge bits, latency/perf counters, and memcheck status are updated by VCN/JPEG blocks.

Concrete integration expected in this tree is under `drivers/gpu/drm/amd/amdgpu/` VCN generation code, especially VCN 5.x files. Those drivers typically use the companion `vcn_5_3_0_d.h` register addresses together with these macros to enable VCPU clocks, assert/deassert `UVD_SOFT_RESET` subblocks, program VCPU cache windows and LMI BARs, configure LMI/JMI VMIDs and swaps, initialize JRBC/JPEG rings, enable JPEG interrupts, acknowledge completed/error statuses, and set clock-gating or power-gating policy.

## State And Persistence Behavior

The macros themselves hold no software state and persist nothing. They describe stateful VCN/UVD/JPEG hardware registers whose values persist in the media engine until reprogrammed, reset, power-gated, or restored by driver resume/reinitialization.

State represented by this chunk includes firmware power-off status, reset request/status bits, clock-gating gates and status, VCPU command and debug state, VCPU cache/noncache aperture layout, LMI/JMI 64-bit BARs, VMIDs, coherency and swap policy, MC/UMC credits, urgent/QoS and latency/perf counter state, clean/idle status, four JRBC ring/IB pointer and buffer states, JPEG decode output and tiling state, JPEG preemption fences, atomic write targets, interrupt enable/status/acknowledge state, and memcheck safe-address/error state.

Access type is not encoded by the macro names. Some fields are writable configuration bits, some are read-only status, some are hardware-updated counters, some are write-one-to-clear or acknowledge bits, and some are self-clearing command bits. Consumers must preserve reserved bits and follow the ASIC programming sequence for clocks, resets, ring pointer updates, BAR/VMID setup, interrupt acknowledgement, preemption fences, and memcheck clamping.

## Dependencies And Integration Points

This chunk must stay synchronized with the companion VCN 5.3.0 address header, normally `vcn_5_3_0_d.h`, which supplies the actual register offsets such as `regUVD_*`, `mmUVD_*`, or generation-specific equivalents. The mask header is also tied to AMDGPU's SOC15 register-access layer and field-helper macros.

Primary functional integration points are AMDGPU media code paths that manage VCN firmware boot, clock/power gating, VCPU setup, memory-interface aperture programming, JPEG ring setup, JPEG command submission, interrupt routing, error handling, and reset/recovery. The generated names are a compile-time contract: missing or renamed macros usually fail the build, while wrong numeric masks or shifts can compile cleanly and misprogram hardware at runtime.

The repeated JRBC instance layout is also an integration contract. `UVD_JRBC0_*` through `UVD_JRBC3_*` expose parallel ring engines with nearly identical field layouts, so driver loops or instance-specific setup code must match the correct address block to the matching macro namespace.

## Risks And Edge Cases

- The chunk starts mid-register at `UVD_ENC_PIPE_BUSY` and ends mid-register at `JPEG_MEMCHECK_SYS_INT_ACK2`. Final per-file reconciliation must merge adjacent chunks before making complete claims about either register.
- Generated-header drift is high risk. Incorrect reset or clock-gating masks in `UVD_SOFT_RESET`, `UVD_SOFT_RESET2`, `UVD_MMSCH_SOFT_RESET`, `UVD_CGC_STATUS`, `UVD_SUVD_CGC_STATUS`, or `CDEFE_SUVD_CGC_*` can leave VCN subblocks held in reset, falsely report reset completion, or gate clocks while decode/encode/JPEG work is active.
- `UVD_VCPU_CNTL` combines error status, clock enable, PMB/RBBM reset, abort, trace/debug, JTAG, timeout, block reset, runstall, and SRE command-interface reset fields. Full-register writes or bad masks can break firmware boot or recovery.
- LMI and JMI BAR fields are full-width halves of 64-bit GPU addresses. Low/high half mismatches, wrong VMIDs, or stale BARs can route media reads/writes to the wrong memory and produce IOMMU faults or silent corruption.
- Cache/noncache offset and size fields use narrow masks while many BAR fields are full 32-bit payloads. Consumers must not assume every address-like register uses the same alignment, width, or unit.
- LMI/JMI swap, coherency, drop, urgent, credits, and arbitration controls affect memory ordering and traffic priority. Wrong settings may only show up under high decode/JPEG bandwidth, preemption, or VM fault pressure.
- JRBC ring and IB fields are sequencing-sensitive. `RB_NO_FETCH`, read/write pointer fields, ring/IB sizes, conditional-read timers, buffer-valid status, and preempt fence data must be programmed in the right order or the command processor can fetch stale commands, hang, or report misleading timeout/error status.
- JPEG interrupt and memcheck registers have separate enable, status, and acknowledge namespaces, with similar names for ordinary system errors and memcheck errors. Confusing `*_STATUS` with `*_ACK`, or system interrupt bits with memcheck bits, can lose error diagnostics or leave interrupts latched.
- Repeated status bitmaps for `JPEG_SYS_INT_*`, `JPEG_MEMCHECK_SYS_INT_*`, and `UVD_JRBC*_UVD_JRBC_STATUS` are easy to copy incorrectly. A one-bit drift can affect only one DJRBC/JRBC lane, output buffer, scalar, bitstream fetch, or high/low address error path.
- Memcheck safe-address and clamping controls are protection-oriented. Incorrectly disabling clamping or programming an unsafe fallback address can turn a detected bad access into memory corruption.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with VCN 5.3 support so include users and `REG_SET_FIELD` expansions catch missing or renamed macros.
- Mechanically compare `vcn_5_3_0_sh_mask.h` against the authoritative generated register database and the companion `vcn_5_3_0_d.h` address header.
- Verify every field in lines 4709-7202 has the expected mask/shift pairing, while accounting for the chunk-boundary continuation at `UVD_ENC_PIPE_BUSY` and `JPEG_MEMCHECK_SYS_INT_ACK2`.
- Diff against adjacent VCN 5.x shift/mask headers where ASIC layout parity is expected, especially for `UVD_SOFT_RESET`, `UVD_VCPU_CNTL`, `UVD_LMI_*`, `UVD_JRBC*`, `UVD_JPEG_*`, `UVD_JMI_*`, and `JPEG_MEMCHECK_*`.
- Exercise VCN firmware boot, reset, suspend/resume, clock-gating and power-gating transitions, and watch for VCPU boot failures, stuck reset-status bits, lost clean/idle status, and recovery timeouts.
- Exercise JPEG decode across all exposed JRBC lanes where hardware supports them, including ring setup, IB submission, preemption fence writes, interrupt enable/status/ack handling, and error injection if available.
- Validate LMI/JMI BAR, VMID, coherency, swap, urgent/QoS, and credit programming with VM fault monitoring, ring pointer traces, high-bandwidth media workloads, and GPU reset recovery.
- Exercise JPEG memcheck paths by validating safe-address clamping, high/low read/write error reporting, status latching, and acknowledge behavior for DJRBC, EJRBC, bitstream fetch, output buffer, scalar, and BS write paths.

## Cross-Chunk Notes

The previous chunk is needed for the start of `UVD_ENC_PIPE_BUSY` and earlier VCN 5.3.0 register families. The following chunk is needed for the rest of `JPEG_MEMCHECK_SYS_INT_ACK2` and any later file content. The merge/reconciliation lane should combine all chunks before producing the final source-tree-aligned per-file report for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_sh_mask.h`.

### subset-b-003480: lines 7203-8262

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_sh_mask.h lines 7203-8262

## Scope And Purpose

This chunk is the final 1,060-line segment of AMD's generated VCN 5.3.0 shift/mask header. It contains C preprocessor constants only: hardware register fields are exposed as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. It defines no functions, structs, variables, allocations, locking, or executable control flow.

The file sits under a `ceph-client` source mirror, but this content is AMDGPU media-engine register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU VCN/JPEG/UMSCH code that combines these masks with addresses from `vcn_5_3_0_offset.h` and uses SOC15/SOC24 register helpers to read, write, or compose MMIO values.

The chunk starts in the middle of `JPEG_MEMCHECK_SYS_INT_ACK2`, after its first few field definitions in the previous chunk. It ends at the `#endif` closing the header guard, so there is no following VCN 5.3.0 shift/mask content in this file.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset used to pack or unpack a field.
- `<REGISTER>__<FIELD>_MASK`: raw bit mask for a field in a 32-bit hardware register.

Major register groups in this chunk:

- JPEG interrupt and arbitration tail: the remainder of `JPEG_MEMCHECK_SYS_INT_ACK2`, `JPEG_MASTINT_EN`, `JPEG_IH_CTRL`, and `JRBBM_ARB_CTRL`. These cover memory-check error acknowledgements for JPEG read/write clients, master interrupt overrun reset and interrupt-overrun mask fields, interrupt-handler routing fields such as VMID/user-data/ring-id, and JRBBM drop controls for SRBM, EJRBC, and DJRBC0 paths.
- `uvd_uvd_jpeg_common_sclk_dec`: `JPEG_CGC_GATE`, `JPEG_CGC_CTRL`, `JPEG_CGC_STATUS`, common/decoder/encoder CGC memory controls, and `JPEG_PERF_BANK_*` registers. These describe JPEG decoder/encoder/JMCIF/JRBBM clock gates, dynamic clock-gating mode, gate/off delays, active-clock status, memory light-sleep/deep-sleep/shutdown enables, and four performance-counter event/count banks.
- `uvd_vcn_umsch_dec`: UMSCH scheduler and MES front-end registers including `VCN_UMSCH_MES_CNTL`, `UMSCH_CTL`, AGDB write pointers, four mailbox/response pairs, UTCL1 control, busy flags, ring-buffer base/size/read/write pointers, master interrupt control, IH control, system interrupt enable/status/ack/source, IH context ID, force/drop/UTCL2 response controls, and `UMSCH_MES_RESET_CTRL`.
- `uvd_vcn_cprs64dec`: a large MES core/control/debug register block. It covers program counter and interrupt routine start addresses, trap vector halves, `VCN_MES_CNTL` core control bits, pipe priorities, interrupt masks and pending status, scratch index/data, instruction pointer, RISC-V-like machine CSRs (`MSTATUS`, `MEPC`, `MCAUSE`, `MBADADDR`, `MIP`, cycle/time/instret, ISA/vendor/arch/imp/hart IDs), icache/dcache operations, general-purpose registers, indexed data memory access, local instruction/data/scratch apertures, perf-count selection, interrupt data words 16 through 31, and 16 data-cache aperture base/mask/control triplets.
- `uvd_vcn_hypdec`: hypervisor-visible MES instruction/data base and bounds registers. These define low/high halves, VMID, execute-disable, cache-policy, and bound fields for instruction and data memory mappings, with both `IC/DC` and `MI/MD` naming aliases.
- `uvd_slmi_adpdec`: S/LMI adapter registers for MMSCH non-cacheable windows. These include eight 64-bit BAR low/high pairs, packed VMID fields for NC0 through NC7, MMSCH coherency/VM/privilege/swap/read/write/drop controls, MMSCH LMI status/error fields, active PF/VF identity, and UMSCH LMI clean-status bits.

## Control Flow And Runtime Behavior

There is no control flow in this header. Runtime use is indirect:

1. ASIC-specific AMDGPU code includes `vcn_5_3_0_offset.h` for register addresses and this header for field masks/shifts.
2. Helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_UMSCH`, `SOC15_WAIT_ON_RREG`, and SOC24 JPEG DPG helpers compose, preserve, poll, or update the actual register values.
3. JPEG initialization and power-management paths use the JPEG CGC masks to enable/disable media clock gating and DPG SRAM programming.
4. UMSCH setup programs MES reset, cache invalidation, pipe reset/active/halt state, instruction/data bases, local masks, interrupt routine addresses, and force/GPUVM policy before starting the media scheduler firmware.

Concrete consumers in this tree include `amdgpu/jpeg_v5_3_0.c`, where `JPEG_CGC_CTRL__*` and `JPEG_CGC_GATE__*` fields drive JPEG clock gating and DPG mode, and `amdgpu/umsch_mm_v4_0.c`, where `UMSCH_MES_RESET_CTRL`, `VCN_MES_CNTL`, `VCN_MES_IC_BASE_CNTL`, `VCN_MES_PRGRM_CNTR_START*`, local aperture, instruction/data base, bound, and `UVD_UMSCH_FORCE` fields are programmed for the UMSCH micro-engine.

## State And Persistence Behavior

The macros hold no software state and persist nothing by themselves. They describe stateful hardware registers whose values persist in JPEG, UMSCH, MES, hypervisor, and LMI blocks until reset, power-gating, firmware reinitialization, suspend/resume restore, or another register write changes them.

State represented by this chunk includes JPEG memory-check acknowledgement bits, interrupt routing metadata, clock-gating enable/mode/status, memory low-power controls, JPEG performance counter configuration and counts, UMSCH ring-buffer pointers and mailboxes, system interrupt latch/ack/source fields, scheduler busy state, MES firmware entry points, cache invalidation/prime/bypass state, pipe reset/active/halt/step controls, debug and machine CSR snapshots, local and data-cache aperture mappings, hypervisor instruction/data bounds, MMSCH non-cacheable BARs and VMIDs, read/write drop controls, and LMI clean/error status.

Access semantics are not encoded in macro names. Some fields are persistent configuration, some are hardware-updated status, some are interrupt acknowledgements, some are command/self-clearing operations, and some are firmware/debug scratch state. Consumers must preserve reserved bits and follow the owning block's sequencing rules, especially around cache invalidation, interrupt acknowledgement, firmware address programming, VMID/aperture setup, and LMI drop/error status.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_offset.h`, which supplies matching addresses such as `regJPEG_CGC_GATE`, `regVCN_UMSCH_MES_CNTL`, `regVCN_MES_PRGRM_CNTR_START`, `regVCN_MES_PRGRM_CNTR_START_HI`, `regVCN_MES_IC_BASE_LO`, and `regUVD_LMI_MMSCH_CTRL`.

The primary integration points are:

- JPEG 5.3.0 bring-up, suspend/resume, power-gating, dynamic-power-gating, and clock-gating code.
- UMSCH media scheduler firmware loading and start-up code, including UMSCH-specific write helpers and firmware GPU-address programming.
- VCN interrupt handling, where IH control, master interrupt enable, system interrupt status/source/ack, and interrupt-data registers route events into AMDGPU interrupt rings.
- Firmware and debug tooling that reads MES status, machine CSRs, busy flags, scratch registers, perf counters, and pending interrupts during bring-up or failure diagnosis.
- Virtualization and memory-management paths that depend on VMID, GPUVM force, hypervisor base/bounds, MMSCH NC BARs, PF/VF active ID, and LMI clean/drop/error fields.

The generated names are the compile-time contract. Missing or renamed symbols generally fail to build, but incorrect numeric masks or shifts can compile cleanly and cause incorrect MMIO programming at runtime.

## Risks And Edge Cases

- The chunk begins mid-register. The first field definitions for `JPEG_MEMCHECK_SYS_INT_ACK2` are in the previous chunk, so final per-file reconciliation must merge the boundary before making complete claims about that register.
- JPEG clock-gating masks are used directly in `jpeg_v5_3_0.c`. Bad `JPEG_CGC_GATE` or `JPEG_CGC_CTRL` masks can leave JPEG clocks enabled, gate clocks while active, break DPG-mode SRAM programming, or cause resume-only media failures.
- Interrupt fields are sequencing-sensitive. Incorrect master/IH/sys-int/ack/source masks can lose events, route them to the wrong VMID/ring/user-data, fail to clear latched interrupts, or hide memory-check failures.
- UMSCH ring-buffer pointer, mailbox, and AGDB write-pointer fields are full-width or alignment-sensitive. Wrong shifts or masks can desynchronize firmware/driver queues and produce scheduler hangs.
- MES firmware entry-point and aperture fields encode shifted or partial address values. Off-by-shift errors in `*_BASE_LO`, `*_PRGRM_CNTR_START*`, local masks, or hypervisor bounds can start firmware at the wrong address or map code/data incorrectly.
- Cache-control and reset fields such as `VCN_MES_CNTL`, `VCN_MES_IC_OP_CNTL`, `VCN_MES_DC_OP_CNTL`, and `UMSCH_MES_RESET_CTRL` may be self-clearing or require polling. Treating them as ordinary sticky bits risks stale cache contents or incomplete reset sequencing.
- Many debug/status registers are hardware-owned. Writing full register values to MES CSR/status/counter/pending-interrupt fields or LMI status fields could clear diagnostics or perturb firmware state.
- Repetitive aperture definitions (`VCN_MES_DC_APERTURE0` through `15`) and MMSCH NC BAR/VMID definitions are copy-error prone; a single incorrect index can affect only one VMID/window and appear only under specific virtualization or firmware workloads.
- The generated file includes both `DEPRECATED` and misspelled `DEPRACATED` field names in `VCN_MES_DC_OP_CNTL`; consumers must use the generated spelling that matches the header rather than normalizing names locally.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with VCN 5.3.0, JPEG 5.3.0, and UMSCH support enabled so include users and `REG_SET_FIELD`/`REG_GET_FIELD` expansions catch missing symbols.
- Mechanically compare this header with the authoritative VCN 5.3.0 register database and the companion `vcn_5_3_0_offset.h` address header.
- Diff against nearby VCN 5.x and 4.x generated headers where layout parity is expected, while accounting for VCN 5.3.0-specific address shifts and JPEG0-only decode fields.
- Exercise JPEG decode/encode paths across suspend/resume, DPG mode, clock-gating enable/disable, power-gating transitions, and interrupt delivery; watch for media timeouts, stuck busy bits, and unexpected memory-check acknowledgements.
- Exercise UMSCH firmware load/start, ring submission, mailbox responses, interrupt routing, reset/recovery, and GPUVM/VMID paths; watch for scheduler firmware hangs, invalid instruction/data fetches, stale cache behavior, and missed system interrupts.
- For virtualization-sensitive systems, validate PF/VF active function reporting, MMSCH NC window VMIDs, hypervisor instruction/data bounds, LMI clean bits, and MMSCH unsupported-length/address-alignment error reporting.
- Use hardware register dumps or tracepoints around firmware setup to confirm programmed base/bound/mask values match the expected shifted address encodings and that reserved bits remain preserved.

## Cross-Chunk Notes

The previous chunk is required for the beginning of `JPEG_MEMCHECK_SYS_INT_ACK2` and other JPEG common register definitions immediately before line 7203. This chunk closes `vcn_5_3_0_sh_mask.h`, so final reconciliation should combine all chunks for the source file before presenting a complete generated-header inventory.
