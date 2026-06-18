# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h lines 9940-12094

## Scope

This chunk is the final large slice of the generated AMD GC 11.0.3 register offset header. It contains only C preprocessor constants: 2,083 `#define` statements across 2,155 lines, including 1,728 `reg*` MMIO offset macros, 864 matching `_BASE_IDX` macros for `reg*` entries, and 355 `ix*` indirect-register index macros. There are no functions, structs, enums, globals, locks, allocations, I/O calls, or executable branches in this range.

The chunk starts inside the `gc_grtavfs_grtavfs_dec` address block after the block comment from the previous chunk, covers GRTAVFS, hypervisor, CP hypervisor, GRBM hypervisor, GCVM shared hypervisor, RLC, RLCS, PF/VF RLC, power/clock, PSP, GFX IMU, CAC indirect, RTAVFS indirect, and SQ wave-debug indirect offsets, then ends with the header guard `#endif`.

Although this file lives under `sources/distributed-fs/ceph-client`, it is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_11_0_3_offset.h` gives symbolic register addresses for AMD graphics core 11.0.3. Driver code combines these offsets with SOC15 MMIO helpers, indirect-register accessors, and companion shift/mask/default headers to program and inspect GPU hardware without hard-coding numeric addresses at call sites.

This chunk's purpose is to expose register locations for:

- RTAVFS/GRTAVFS clock-voltage and adaptive-voltage-frequency-scaling access windows.
- RLC and GPU IOV hypervisor state, including virtual-function enable/masks, scheduler state, doorbell status, VM busy state, SDMA status, firmware memory windows, scratch windows, and virtualization reset/response registers.
- Command processor hypervisor microcode and instruction/data memory windows for PFP, ME, MEC, MES, CPC, and GFX RS64 blocks.
- GRBM hypervisor selector/data windows and GCVM shared frame-buffer size/offset registers per VF.
- Core RLC, RLCS, and PF/VF RLC control/status, timers, interrupts, doorbells, safe mode, power-gating, clock counting, UTCL1 errors, profiling, residency counters, IMU/SMU mailboxes, and firmware bootload/reset vectors.
- GC power and clock-gating controls for graphics pipeline blocks.
- PSP-facing CP/GRBM/RLC debug, CAM, security, firewall, and data-memory index windows.
- GFX IMU mailbox, scratch, telemetry, interrupt, clock/reset, RAM, timer, fence, bootloader, and PSP-facing registers.
- CAC and RTAVFS indirect index spaces plus SQ wave-debug indirect registers.

## Important APIs, Types, And Macros

The only API surface is the macro namespace generated for the hardware register database:

- `reg<NAME>` macros give MMIO register offsets as word offsets, not byte offsets.
- `reg<NAME>_BASE_IDX` macros select the SOC15 register-base instance. Every visible `reg*` entry in this chunk uses base index `1`.
- `ix<NAME>` macros give indices for indirect register spaces such as `gccacind`, `secacind`, `grtavfsind`, and `sqind`.
- `// addressBlock:` and `// base address:` comments group register names by hardware decoder/address block.

There are no callable APIs or C types in this header. Runtime consumers generally use these constants through AMDGPU helpers such as `RREG32_SOC15`, `WREG32_SOC15`, indirect wave/CAC accessors, `SOC15_REG_OFFSET`, and field helpers from matching shift/mask headers.

Important macro families in this chunk include:

- GRTAVFS/RTAVFS registers: `regGRTAVFS_*`, `regGRTAVFS_SE_*`, `regRTAVFS_*`, and `ixRTAVFS_REG0..194` provide direct and indirect windows for AVFS register address/data/control/status, target frequency/voltage, soft reset, PSM, and clock controls.
- Hypervisor and IOV registers: `regRLC_GPU_IOV_*`, `regRLC_HYP_*`, `regRLC_GPU_IOV_SDMA0..7_STATUS`, `regRLC_GPU_IOV_SDMA0..7_BUSY_STATUS`, `regRLC_GPU_IOV_VF_*`, `regRLC_GPU_IOV_SCH_*`, and `regRLC_GPU_IOV_INT_*` describe virtual-function scheduling, doorbells, masks, interrupts, reset requests, scratch, and SDMA status.
- RLC firmware and memory windows: `regRLC_GPM_UCODE_*`, `regRLC_RLCP_IRAM_*`, `regRLC_RLCV_IRAM_*`, `regRLC_LX6_*`, `regRLC_PACE_*`, `regRLC_SRM_*`, and related scratch/data address pairs expose firmware upload/debug surfaces.
- CP hypervisor registers: `regCP_HYP_*`, aliases such as `regCP_PFP_UCODE_*`, `regCP_ME_RAM_*`, `regCP_MEC_ME*_UCODE_*`, instruction-cache and data-cache base/bound controls, MES/MEC memory base aliases, and GFX RS64 base/bound registers.
- GRBM/GCVM hypervisor registers: `regGRBM_GFX_INDEX_SR_*`, `regGRBM_GFX_CNTL_SR_*`, `regGC_IH_COOKIE_0_PTR`, `regGRBM_SE_REMAP_CNTL`, and `regGCMC_VM_FB_SIZE_OFFSET_VF0..15`.
- Core RLC registers: `regRLC_CNTL`, `regRLC_STAT`, timer and clock-count registers, `regRLC_RLCG_DOORBELL_*`, power-gating controls, SERDES access, GPM general registers, SRM indexed address/data registers, UTCL1 control/error/status registers, PACE/RLCV/RLCP/XT doorbells, firewall, profiling, residency counters, GFX IH client status, SPM delay accessors, LX6/XT core status, SMU command/message/argument registers, and IMU bootload/reset-vector registers.
- RLCS registers: `regRLC_RLCS_*` covers decoder start/end, exception registers, clock/deep-sleep controls, IOV state, soft reset, interrupt controls and info, bootload status, power brake, general/auxiliary registers, GCR data/status, IMU/RLC message and telemetry registers, RAM access, IH controls, and `regRLC_RLCS_DEC_END`.
- PF/VF RLC registers: `regRLC_SAFE_MODE`, SPM sample/MC/interrupt registers, CSIB address/length, CP scheduler/EOF interrupt registers, and spare interrupt registers.
- Power/clock registers: `regCGTS_*`, `regCGTT_*`, `regCGTX_*`, `regSQ_*_CLK_CTRL`, `regICG_*`, `regGFX_ICG_*`, `regTA_CGTT_CTRL`, `regDB_CGTT_*`, `regCB_CGTT_*`, `regGL1*`, `regCHI_*`, `regGUS_*`, and related block clock-gating controls.
- PSP/debug registers: `regCP_MES_DM_INDEX_*`, `regCP_MEC_DM_INDEX_*`, `regCP_GFX_RS64_DM_INDEX_*`, `regCPG_PSP_DEBUG`, `regCPC_PSP_DEBUG`, `regGRBM_IOV_ERROR_FIFO`, security/CAM registers, and `regRLC_FWL_FIRST_VIOL_ADDR`.
- GFX IMU registers: `regGFX_IMU_C2PMSG_0..47`, access-control registers, power-management IRQ, MP1/RLC mailboxes, status, SOC access, VF control, telemetry, scratch, GTS offsets, PIC/IH interrupt controls, fuse/clock/doorbell/DPM/reset/isolation controls, RAM access, fence logging, timers, core status, and PSP bootloader/I-RAM windows.
- Indirect CAC/SQ registers: `ixGC_CAC_*`, release/stall/power-brake LUTs, fixed-pattern performance counters, `ixSE_CAC_*`, and SQ wave debug indices such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO/HI`, `ixSQ_WAVE_TTMP0..15`, `ixSQ_WAVE_M0`, and `ixSQ_WAVE_EXEC_LO/HI`.

## Control Flow

This header has no runtime control flow. It affects behavior only when compiled C code expands these macros while calculating register addresses.

The implied runtime flow is:

1. GC 11.0.3-specific driver code includes this offset header, often with `gc_11_0_3_sh_mask.h` and default-value headers.
2. The driver selects a `reg*` macro and base index for SOC15 MMIO access, or an `ix*` macro for an indirect aperture.
3. AMDGPU helpers translate the symbolic offset into a device register address and perform read, write, poll, or read-modify-write operations.
4. Hardware/firmware state machines in RLC, CP, GRBM, PSP, IMU, SMU, CAC, RTAVFS, or SQ observe the register access and perform the actual operation.

Examples of consumer paths in this tree include `amdgpu/imu_v11_0_3.c`, `amdgpu/gfxhub_v3_0_3.c`, and `amdgpu/gfx_v11_0_3.c`, which include this GC 11.0.3 offset header. Related generation code such as `gfx_v11_0.c` uses the same register families for RLC safe-mode commands, IMU C2P mailbox access, and SQ wave debug reads.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent and volatile state exists in GPU registers, firmware RAMs, doorbell state, MMIO-visible status latches, indirect register spaces, and memory-backed firmware/queue structures.

State described by this chunk includes:

- Firmware code/data windows and checksums for RLC, CP, PFP, ME, MEC, MES, GPM, RLCP, RLCV, LX6, PACE, and GFX IMU blocks.
- Virtualization and IOV state such as VF enable bits, VF masks, active function ID, scheduler control, SDMA status, VM busy state, interrupt status/disable/force, scratch windows, and virtual reset requests/responses.
- Doorbell ranges, controls, statuses, and captured data for RLCG, RLCV, RLCP, XT, IMU, and CPAXI monitoring.
- Power-management and clock state such as RLC power gating, dynamic/static PG status, residency counters, CGTT/ICG controls, memory sleep, SMU clock requests, SMU commands, and AVFS target frequency/voltage registers.
- Error, security, and debug state such as UTCL1 error/status, firewall violations, GRBM IOV error FIFO, security/CAM data, GFX IH client statuses, CP/PSP debug windows, SPM/SPP profiling state, and SQ wave debug registers.
- IMU mailbox, scratch, telemetry, timer, reset, isolation, fence, RAM, bootloader, and RLC/MP1/SOC handshake state.

Many registers are live hardware status or command apertures rather than durable software state. Some values persist until GPU reset, power-gating loss, suspend/resume reinitialization, firmware reload, queue teardown, or driver reprogramming. Some status bits may be clear-on-read, write-one-to-clear, self-clearing, firmware-owned, or access-restricted, but this offset header does not encode those side-effect classes.

## Dependencies And Integration Points

This chunk depends on the GC 11.0.3 register description remaining internally consistent:

- The companion GC 11.0.3 shift/mask header supplies bitfield layouts for many registers named here.
- Default-value headers for nearby GC 11.x generations provide reset-value context where generated defaults exist.
- SOC15 register helper infrastructure interprets `reg*` offsets and `_BASE_IDX` values.
- Indirect access helpers interpret `ix*` indices for CAC, RTAVFS, and SQ debug apertures.
- Firmware loading and runtime management code must agree with the instruction/data memory windows exposed here.

Integration points include AMDGPU graphics initialization, RLC bring-up, CP/MES/MEC firmware upload, PSP coordination, GFXHUB/VM configuration, SR-IOV scheduling, VF reset handling, SDMA/queue status attribution, interrupt handling, safe-mode entry/exit, clock/power gating, SMU messaging, IMU boot and telemetry, shader profiling/thread tracing, CAC/power-brake tuning, and wavefront debug/register-dump tooling.

## Risks And Edge Cases

- Generated-header drift is the main risk. An incorrect numeric offset or base index can compile cleanly but direct reads/writes to the wrong hardware register.
- The line range starts after the `gc_grtavfs_grtavfs_dec` address-block comment, so the first visible GRTAVFS macros rely on previous-chunk context.
- Several names are aliases for the same offset, especially CP hypervisor and MES/MEC memory-base registers. Consumers must use aliases consistently with the intended firmware block and access mode.
- The large RLC/RLCS region mixes configuration, status, interrupt, firmware-memory, power, doorbell, error, and mailbox registers. Full-register writes or stale generation assumptions can break firmware sequencing, power gating, or queue progress.
- Doorbell and scheduler offsets are liveness-sensitive. Wrong RLCG/RLCV/RLCP/XT/IMU doorbell ranges or status offsets can cause lost notifications, stuck queues, or misleading diagnostics.
- IOV and VF registers are isolation-sensitive. Misprogramming VF masks, active function IDs, VM busy status, reset requests, scratch windows, or GCMC VF frame-buffer offsets can corrupt virtualization behavior or hide guest faults.
- Firmware upload windows require strict address/data ordering. Misusing `*_ADDR`, `*_DATA`, `*_BASE_LO/HI`, and `*_BOUND_LO/HI` aliases can load code or data into the wrong microcontroller aperture.
- PSP, GRBM security/CAM, and firewall registers are privilege-sensitive. Incorrect offsets can affect protected debug/security flows or obscure first-violation attribution.
- Clock, power, memory-sleep, AVFS, and IMU reset/isolation registers interact with active hardware state. Access must follow existing sequencing and polling rules rather than treating offsets as ordinary storage.
- Indirect `ix*` register spaces are not MMIO offsets. Accidentally passing `ixSQ_*`, `ixGC_CAC_*`, or `ixRTAVFS_*` constants through direct SOC15 MMIO helpers would address the wrong space.
- The RTAVFS indirect list skips `ixRTAVFS_REG188`; tools that assume a contiguous 0..194 range may mis-handle the gap.
- The chunk closes the header guard. Any generated merge conflict or missing `#endif` around this range would break all translation units including this header.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations that include GC 11.0.3 support. Missing or malformed macros should surface in `imu_v11_0_3.c`, `gfxhub_v3_0_3.c`, `gfx_v11_0_3.c`, shared GFX 11 code, and related firmware/power/debug paths.
- Mechanically compare every offset and `_BASE_IDX` in this chunk against AMD's authoritative GC 11.0.3 register database.
- Cross-check matching register names in `gc_11_0_3_sh_mask.h` and default headers where applicable; offsets, masks, and defaults must describe the same hardware generation.
- Run static checks that every `reg*` macro has a paired `_BASE_IDX` macro, every paired entry in this chunk uses the expected base index, and `ix*` macros are not paired with `_BASE_IDX`.
- Validate alias groups intentionally share offsets, especially CP/PFP/ME/MEC/MES memory windows and GRBM CAM/security aliases.
- Boot affected GC 11.0.3 hardware and exercise graphics/compute queue creation, firmware loading, ring submission, fence progress, VM fault handling, SDMA activity, and SR-IOV paths if available.
- Exercise RLC safe mode, GPU reset, suspend/resume, power-gating, clock-gating, memory-sleep, SMU messaging, and IMU boot/telemetry while checking for stuck polls or timeout regressions.
- Exercise interrupt/error paths and inspect CP/RLC/RLCS/GRBM/UTCL1/firewall/IOV diagnostic registers for sane attribution.
- Read SQ wave debug registers via the proper indirect path and compare wave status, PC, TTMP, M0, and EXEC values against known-good debug tooling.
- Use register-dump comparison against reference hardware or firmware logs for RLC doorbells, RLC/IMU mailboxes, GFX IMU C2P messages, CAC indirect registers, RTAVFS indirect registers, and PSP-facing debug/CAM windows.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002525`. The final per-file research should merge this with neighboring chunks for full `gc_11_0_3_offset.h` coverage. The previous chunk owns the address-block context immediately before line 9940, and this chunk owns the final header guard closure after the SQ indirect register definitions.
