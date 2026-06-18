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
