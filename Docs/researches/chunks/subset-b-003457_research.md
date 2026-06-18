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
