# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_0_0_sh_mask.h lines 2537-3815

## Scope And Purpose

This chunk is the final 1,279-line segment of AMD's generated VCN 2.0.0 register shift/mask header. It defines C preprocessor constants only: hardware register fields are exported as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. There are no functions, structs, enums, variables, allocations, branches, or direct MMIO operations in this chunk.

The path sits under a `ceph-client` source mirror, but the content is AMDGPU media-engine register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU VCN/UVD code that combines these masks with register address macros from the companion VCN address header and accesses hardware through `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `SOC15_REG_OFFSET`, `SOC15_DPG_MODE_OFFSET`, and `REG_SET_FIELD`.

This chunk starts in the tail of `UVD_LMI_SWAP_CNTL`; earlier fields of that register are in the previous chunk. It continues through VCN memory-interface, VCPU, ring-buffer, semaphore, context-switch, clock-gating, DMA/busy-status, encode-ring, and MMSCH non-cache aperture fields, then closes the file guard with `#endif`.

## Important APIs, Types, And Macros

The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position used to pack or unpack a field.
- `<REGISTER>__<FIELD>_MASK`: raw 32-bit field mask used for masked reads/writes.

Major register families in this chunk:

- Memory swap, cache, and aperture programming: `UVD_LMI_SWAP_CNTL`, `UVD_MP_SWAP_CNTL`, `UVD_VCPU_CACHE_OFFSET0` through `UVD_VCPU_CACHE_OFFSET8`, `UVD_VCPU_CACHE_SIZE0` through `UVD_VCPU_CACHE_SIZE8`, `UVD_VCPU_NONCACHE_OFFSET0/1`, `UVD_VCPU_NONCACHE_SIZE0/1`, `UVD_LMI_VCPU_CACHE*_64BIT_BAR_LOW/HIGH`, `UVD_LMI_VCPU_NC*_64BIT_BAR_LOW/HIGH`, `UVD_LMI_RBC_IB_64BIT_BAR_*`, `UVD_LMI_RBC_RB_64BIT_BAR_*`, and `UVD_LMI_MC_CREDITS`. These fields describe byte-lane swap modes, VCPU cached/noncached memory windows, 64-bit ring/IB BARs, and memory-controller credit throttles.
- MPC, UDEC, and general processor communication: `UVD_UDEC_ADR`, `UVD_MPC_LUMA_*`, `UVD_MPC_CHROMA_*`, `UVD_MPC_CNTL`, `UVD_MPC_PITCH`, `UVD_MPC_SET_MUXA*`, `UVD_MPC_SET_MUXB*`, `UVD_MPC_SET_MUX`, `UVD_MPC_SET_ALU`, `UVD_GPCOM_SYS_CMD`, `UVD_GPCOM_SYS_DATA0/1`, `UVD_GPCOM_VCPU_CMD`, and `UVD_GPCOM_VCPU_DATA0/1`. These cover decode/MPC counters, replacement/performance controls, mux/ALU programming, and host/VCPU command mailboxes.
- VCPU control and debug: `UVD_VCPU_CNTL`, `UVD_VCPU_PRID`, `UVD_VCPU_TRCE`, `UVD_VCPU_TRCE_RD`, and `UVD_CXW_WR`. Fields include VCPU clock enable, soft resets, abort request, trace muxing, timeout controls, JTAG enable, codec/offload bits, probe timeout, and trace/readback data.
- Reset and high-level status: `UVD_SOFT_RESET`, `UVD_STATUS`, `UVD_JOB_START`, `UVD_JOB_DONE`, `CG_TIMESTAMP_LOW/HIGH`, `UVD_VERSION`, `UVD_NO_OP`, and `UVD_SCRATCH_NP`. These describe block-level soft reset bits, reset-status readbacks, UVD busy/ack/GP-com flags, job start/done handshakes, timestamp/version/scratch/no-op values.
- Ring-buffer and command fetch control: `UVD_LMI_RBC_IB_VMID`, `UVD_RBC_IB_SIZE`, `UVD_LMI_RBC_RB_VMID`, `UVD_RBC_RB_RPTR`, `UVD_RBC_RB_WPTR`, `UVD_RBC_RB_WPTR_CNTL`, `UVD_RBC_READ_REQ_URGENT_CNTL`, `UVD_RBC_WPTR_STATUS`, `UVD_RBC_RB_CNTL`, `UVD_RBC_RB_RPTR_ADDR`, `UVD_RBC_WPTR_POLL_CNTL`, `UVD_RBC_WPTR_POLL_ADDR`, `UVD_RBC_BUF_STATUS`, `UVD_RBC_IB_SIZE_UPDATE`, `UVD_RBC_BDM_PRE`, `UVD_RBC_CAM_*`, `UVD_RBC_VCPU_ACCESS`, and `UVD_RBC_CXW_RELEASE`. These fields control ring buffer size/block size, no-fetch/no-update modes, read/write pointers, VMIDs, polling, CAM remap entries, buffer validity, and context-switch release.
- Semaphore and timeout controls: `UVD_SEMA_ADDR_LOW/HIGH`, `UVD_SEMA_CMD`, `UVD_SEMA_TIMEOUT_STATUS`, `UVD_SEMA_WAIT_INCOMPLETE_TIMEOUT_CNTL`, `UVD_SEMA_WAIT_FAULT_TIMEOUT_CNTL`, and `UVD_SEMA_SIGNAL_INCOMPLETE_TIMEOUT_CNTL`. They expose semaphore address packing, request mode/phase/VMID fields, timeout status, clear bit, enable bits, timeout counts, and resend timers.
- Context switch/save-restore controls: `UVD_CXW_EN`, `UVD_CXW_SE`, `UVD_CXW_FINISHED`, `UVD_CXW_SHIFT_FINISHED`, `UVD_CXW_START`, `UVD_CXW_BLOCK_STATUS`, `UVD_STOP_CONTEXT`, `UVD_CXW_SAVE_AREA_ADDR`, `UVD_CBUF_ID`, `UVD_CONTEXT_ID`, `UVD_CXW_SAVE_AREA_SIZE`, `UVD_CONTEXT_ID2`, `UVD_CXW_CNTL`, `UVD_CXW_EVENT`, `UVD_CXW_SCAN_AREA_OFFSET`, `UVD_CXW_SHIFT_CNTL`, and `UVD_CXW_INT_ID`. These fields describe context stop mode, save-area address/size, context IDs, scan/shift operation state, interrupt enables, event flags, and idle status for VCPU/LBSI/LMI.
- SUVD and media-clock gating: `UVD_ENGINE_CNTL`, `UVD_SUVD_CGC_GATE`, `UVD_SUVD_CGC_STATUS`, and `UVD_SUVD_CGC_CTRL`. These cover engine start, start mode, page-fault handling disable, software clock-gating enables, clock-gating status, and mode bits for decode/encode subblocks such as SRE, SIT, SMP, SCM, SDB, SCLR, UVD_SC, ENT, IME, SITE, EFC, and codec-specific H.264/HEVC/VP9 paths.
- DMA, encode, and busy-status windows: `MDM_DMA_CMD`, `MDM_DMA_STATUS`, `MDM_DMA_CTL`, `MDM_ENC_PIPE_BUSY`, `MDM_WIG_PIPE_BUSY`, `UVD_ENC_PIPE_BUSY`, `UVD_ENC_REG_INDEX`, `UVD_ENC_REG_DATA`, `UVD_OUT_RB_*`, `UVD_RB_*`, `UVD_RB_*2`, and `UVD_RB_*4`. These describe MDM DMA command/control/status, encode and WIG pipeline busy flags, indexed encode register access, output rings, primary encode rings, and fourth ring entries.
- MMSCH non-cache address block: `UVD_LMI_MMSCH_NC0_64BIT_BAR_LOW/HIGH` through `UVD_LMI_MMSCH_NC7_64BIT_BAR_LOW/HIGH`, `UVD_LMI_MMSCH_NC_VMID`, `UVD_LMI_MMSCH_CTRL`, `UVD_MMSCH_SOFT_RESET`, and `UVD_LMI_ARB_CTRL2`. These fields describe MMSCH-visible non-cache BARs, per-aperture VMIDs, coherency/VM/swap/read/write/drop controls, MMSCH reset/lock bits, and LMI arbitration burst/return limits.

## Control Flow And Runtime Behavior

There is no executable control flow in this header. Runtime use is indirect:

1. ASIC-specific AMDGPU VCN files include generated address headers for `mmUVD_*` or `regUVD_*` offsets and this shift/mask header for the field layout.
2. Driver startup, suspend/resume, power-gating, ring initialization, and debug paths build register values with constants from this header.
3. The driver writes or reads hardware through MMIO helpers such as `WREG32_SOC15`, `RREG32_SOC15`, `WREG32_P`, and DPG/indirect variants.
4. Field-helper macros such as `REG_SET_FIELD` depend on these names to preserve unrelated bits while changing fields like `UVD_RBC_RB_CNTL.RB_BUFSZ` or `UVD_MPC_CNTL.REPLACEMENT_MODE`.

Concrete integration visible in this tree includes `drivers/gpu/drm/amd/amdgpu/vcn_v2_0.c`, where the driver:

- Enables VCPU clocking through `UVD_VCPU_CNTL__CLK_EN_MASK`.
- Clears and asserts reset fields in `UVD_SOFT_RESET`.
- Programs `UVD_MPC_CNTL__REPLACEMENT_MODE`.
- Initializes decode ring control through `UVD_RBC_RB_CNTL__RB_BUFSZ`, `RB_BLKSZ`, `RB_NO_FETCH`, `RB_NO_UPDATE`, and `RB_RPTR_WR_EN`.
- Writes ring-buffer BARs using `UVD_LMI_RBC_RB_64BIT_BAR_LOW/HIGH`.
- Reads `UVD_STATUS` after setup to flush posted writes and avoid race conditions.
- Enables software clock gating with the `UVD_SUVD_CGC_GATE__*` masks.

Newer VCN generation files, such as `vcn_v4_0_5.c`, `vcn_v5_0_1.c`, and `vcn_v5_0_2.c`, show the same programming pattern with generation-specific address/mask headers, which is useful for validating intended semantics and evolution of field names.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe stateful hardware registers in the VCN/UVD block. Values written through these fields persist in hardware until changed by the driver, reset by a soft/hard reset, affected by power gating, or restored during resume/reinitialization.

State represented by this chunk includes byte-swap policy, VCPU memory apertures and BARs, ring and indirect-buffer pointers, ring sizes, VMIDs, semaphore addresses and timeout counters, VCPU clock/reset/debug control, block reset status, context save/restore state, clock-gating configuration and status, MDM DMA state, encode pipeline busy state, output/encode rings, scratch registers, and MMSCH non-cache BAR/VM/coherency settings.

Access type is not encoded by the macros. Some fields are configuration bits, some are hardware-updated status, some are counters, some are write-one or self-clearing handshakes, and some must be touched only in a defined sequence while clocks or resets are in a particular state. Consumers must preserve reserved bits and respect the programming model around ring pointer reset, DPG stall, semaphore timeout clear, context save/restore, and soft reset sequencing.

## Dependencies And Integration Points

This chunk must stay synchronized with the companion VCN 2.0.0 register address header, typically `vcn_2_0_0_d.h`, which supplies the actual `mmUVD_*` address values consumed alongside these masks. The mask header is also tied to AMDGPU's generic SOC15 register access layer and field helpers.

Primary in-tree integration points are AMDGPU VCN/UVD implementation files under `drivers/gpu/drm/amd/amdgpu/`, especially `vcn_v2_0.c` for the matching generation. The constants support media firmware boot, ring setup, command submission, interrupt/status handling, power management, dynamic power gating, clock gating, context switching, and diagnostics.

The generated names are the compile-time contract. A missing or renamed macro usually fails the build. An incorrect numeric mask or shift can compile cleanly but route driver writes to the wrong bit, corrupt neighboring fields, or cause hardware state machines to hang.

## Risks And Edge Cases

- The chunk starts mid-register at `UVD_LMI_SWAP_CNTL`; final per-file reconciliation must merge the previous chunk before making complete claims about that register.
- Many ring, BAR, and pointer fields are alignment-shifted. Examples include base-address fields shifted by 6, pointer/size fields shifted by 4, poll address shifted by 2, and semaphore address pieces covering selected address bits. Incorrect shifts can produce valid-looking but wrong GPU addresses.
- `UVD_RBC_RB_CNTL`, `UVD_RBC_RB_WPTR`, `UVD_RBC_RB_RPTR`, and `UVD_RBC_RB_RPTR_ADDR` are sequencing-sensitive. Bad masks or full-register writes can cause command fetch to start from stale pointers, stop updating the read pointer, or fetch while the ring is being reset.
- `UVD_SOFT_RESET` spans many subblocks plus reset-status bits in the high half of the register. Mixing writable reset bits and status bits incorrectly can leave decode subblocks in reset or misread reset completion.
- `UVD_VCPU_CNTL` combines clock enable, resets, debug/trace, abort, timeout, and codec/offload controls. Accidentally altering unrelated bits while enabling the clock can affect firmware boot or error recovery.
- Semaphore timeout status and clear fields may be latched or write-sensitive. Treating timeout status as ordinary read/write state could lose diagnostics or fail to clear a timeout.
- Context-switch fields (`UVD_CXW_*`) encode save/restore, scan, shift, interrupt, event, and idle state. Wrong save-area alignment or event masks can corrupt context images or miss context-switch interrupts.
- `UVD_SUVD_CGC_GATE`, `UVD_SUVD_CGC_STATUS`, and `UVD_SUVD_CGC_CTRL` contain many one-bit fields for codec-specific subblocks. Omitting one mask may affect only a specific H.264, HEVC, VP9, decode, or encode path and may escape generic decode testing.
- `MDM_ENC_PIPE_BUSY`, `MDM_WIG_PIPE_BUSY`, and `UVD_ENC_PIPE_BUSY` are broad status bitmaps. Incorrect busy masks can make idle waits finish too early or never finish, especially under encode workloads.
- MMSCH non-cache BAR and VMID fields configure scheduler-visible apertures. Bad VMID/coherency/swap/drop settings can produce memory faults, stale data, or silent corruption in scheduler/firmware interactions.
- Several all-ones data fields (`*_DATA`, `*_CRC32`, scratch, dummy display fields) intentionally expose full 32-bit payloads. Consumers still need to know whether the underlying register is data, status, scratch, or reserved dummy state before writing it.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with VCN 2.0 support so include users and `REG_SET_FIELD` expansions catch missing or renamed macros.
- Mechanically compare `vcn_2_0_0_sh_mask.h` against the authoritative generated register database and the companion `vcn_2_0_0_d.h` address header.
- Verify every field in lines 2537-3815 has a consistent mask/shift pair, while accounting for chunk-boundary continuation at `UVD_LMI_SWAP_CNTL` and full-width fields whose mask is `0xFFFFFFFFL`.
- Run VCN 2.0 boot/start/stop, suspend/resume, reset, and DPG paths and watch for VCPU boot failures, posted-write races, firmware timeout logs, ring pointer mismatches, and stuck busy/status bits.
- Exercise decode ring submission, indirect-buffer submission, semaphore wait/signal paths, context save/restore, software clock-gating enable/disable, and clock-gating status reads.
- Exercise encode-specific paths that touch `UVD_ENC_REG_INDEX/DATA`, `UVD_OUT_RB_*`, `UVD_RB_*2`, `UVD_RB_*4`, `MDM_*`, and `UVD_ENC_PIPE_BUSY` fields, not only decode-only workloads.
- Validate memory BAR, VMID, swap, and coherency programming with IOMMU/VM fault monitoring, ring buffer read/write pointer tracing, and GPU reset recovery.
- Diff against adjacent VCN generation headers and implementation files for intentional layout changes, especially around `UVD_VCPU_CNTL`, `UVD_SOFT_RESET`, `UVD_SUVD_CGC_*`, `UVD_LMI_MMSCH_*`, and encode-ring fields.

## Cross-Chunk Notes

The previous chunk is needed for the start of `UVD_LMI_SWAP_CNTL` and earlier VCN/UVD register families. This chunk closes the file, so there is no following chunk content for `vcn_2_0_0_sh_mask.h`. The merge/reconciliation lane should combine all chunks before producing the final source-tree-aligned per-file report for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_0_0_sh_mask.h`.
