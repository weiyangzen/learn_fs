# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 15094-17728

## Purpose

This chunk is a generated AMD DCN 4.2.0 display register shift/mask header slice. It contains no executable C logic; its public surface is 2,101 `#define` constants that name bit positions (`__SHIFT`) and bit masks (`_MASK`) for DCN 4.2 hardware register fields.

The range starts in the tail of `DIG_INTERRUPT_DEST`, covers several display interrupt-routing destination registers, then moves through the DMU/DMCUB firmware interface, DMCUB memory regions/mailboxes/interrupts, MCIF writeback and MMHUBBUB registers, DC perfmon blocks, Azalia/HDA audio registers, and ends in the beginning of DCHUBBUB SDPIF/VM security and address fields. Although this file is stored under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO accesses in this range. The API contract is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field inside the same register.

The important register-field families in this chunk are:

- Interrupt destination groups: `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, `DSC_INTERRUPT_DEST`, `HPO_INTERRUPT_DEST`, and `DPP_INTERRUPT_DEST`. These route display, I2C/DDC, HPD, audio, AUX, DSC, HPO, and DPP events to interrupt handling paths.
- `DMCUB_RBBMIF_SEC_CNTL` plus `RBBMIF_*`: security control, timeout status, timeout-disable masks, interrupt status, and sticky status flags for the DMCUB RBBM interface.
- `DMCUB_REGION*` and `DMCUB_REGION3_CW*`: DMCUB firmware memory windows, base/top addresses, offsets, high-address halves, per-window enables, and TMR AXI-space selection.
- `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, `DMCUB_INTERRUPT_STATUS`, `DMCUB_INTERRUPT_TYPE`, and external interrupt registers: timer, inbox, outbox, GPINT, IH, fault, and register-mailbox interrupt bits.
- DMCUB control and mailbox registers: `DMCUB_SEC_CNTL`, `DMCUB_MEM_CNTL`, inbox/outbox base/size/read/write pointers, timer registers, scratch registers 0 through 23, `DMCUB_CNTL`, `DMCUB_CNTL2`, GPINT data registers, fault-address registers, low-speed wake interrupt enable, memory power control, `HOST_INTERRUPT_CSR`, and register inbox/outbox message/status registers.
- MCIF writeback: `MCIF_WB_BUFMGR_*`, buffer pitch/status/address/size/resolution fields for four buffers, arbitration and SCLK/P-state/self-refresh controls, clock gating, security level, VMID/TMZ, QoS, VCE control, luma/chroma sizes, and high address halves.
- MMHUBBUB: writeback latency watermark, general watermark, warmup config/control/base/region/security/VMID fields, min TTO, SMU watermark control, WBIF misc/outstanding counters, memory power status/control, clock control, soft reset, DMU interface error status, and client unit ID.
- DC perfmon instances 3 and 4: counter select, clear, enable, state, window, interrupt control, compare values, and high/low counter readback fields.
- Azalia/HDA audio: stream index/data windows for streams 0 through 15, clock and global memory-power controls, straps, endpoint/input-endpoint indirect index/data windows, controller clock gating, DTO and SOCCLK controls, DMA controls, RIRB/CORB controls, payload capabilities, CRC controls/results, codec root parameters, function power/reset controls, converter synchronization, and audio port connectivity.
- DCHUBBUB SDPIF and VM fields at the end: `DCHUBBUB_SDPIF_CFG0/1/2`, `VM_REQUEST_PHYSICAL`, force-IO status, framebuffer and AGP base/top/offset fields, local HBM address start/end/lock, and pipe security/noalloc levels for surface, DMDATA, DCC metadata, cursor, 3DLUT, and GPUVM requests.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to register-table construction:

1. DCN 4.2 display code includes the matching generated offset header and this shift/mask header.
2. Block-specific headers use macro families such as `SR`, `SRI`, `SF`, `DMUB_SR`, `DMUB_SF`, `HUBBUB_SF`, and `HWS_SF` to bind generic register-field tables to these generated `dcn_4_2_0_sh_mask.h` names.
3. Runtime objects for DMUB, IRQ service, hubbub, MMHUBBUB/writeback, audio, and hardware sequencing receive register offsets plus these shift/mask tables.
4. Driver helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use the tables to access MMIO bitfields.

The macros in this chunk do not define programming order. DMCUB boot/setup, mailbox messaging, interrupt enable/acknowledge, writeback buffer management, audio initialization, perfmon programming, and DCHUBBUB VM/SDPIF setup are controlled by consumer code and hardware specifications outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing by itself. It names hardware-visible state fields whose lifetime is controlled by DCN hardware, firmware, display driver sequencing, power gating, suspend/resume, and reset paths.

Important state named by this range includes:

- Interrupt routing and status state for display links, HPD, DDC/I2C, AUX, audio, DSC, HPO, DPP, DMCUB, and host register mailboxes.
- DMCUB boot/runtime state: secure reset/status, memory region mappings, code-window enables, inbox/outbox ring base/size/pointers, register-mailbox readiness/messages/responses, GPINT data, timers, scratch registers, firmware fault addresses, and memory power controls.
- MCIF writeback state: buffer ownership/status, pitch, luma/chroma addresses, high address bits, buffer dimensions, interrupt enables/acknowledges, lock state, VMID/security/TMZ, arbitration, self-refresh, P-state, and QoS controls.
- MMHUBBUB state: warmup address ranges, writeback and hubbub power status, clock-gating controls, soft reset, DF/DMU error status, and performance counters.
- Azalia audio state: stream and endpoint indirect register windows, DTO and SOCCLK controls, controller clock gating, codec capabilities, DMA state, CRC generation/result registers, power-state controls, endpoint synchronization, and audio connectivity reports.
- DCHUBBUB SDPIF/VM state: request-credit enable/status/errors, response status clear bits, host-VM security levels, force-IO address/status capture, framebuffer/AGP apertures, local HBM address lock, and per-pipe security/noalloc levels.

Access semantics are not encoded here. Many fields are configuration bits that persist until rewritten or reset, while status/interrupt fields may be latched, write-one-to-clear, self-clearing, read-only, or valid only when the relevant display block is powered and clocked.

## Dependencies And Integration Points

This generated file must remain synchronized with AMD's DCN 4.2 register database and the companion offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`.

Observed DCN 4.2 consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c` includes this header and programs the DMCUB region windows, inbox/outbox pointers, register mailboxes, host interrupts, GPINT/IH interrupt enables, fault/debug readback, and system-memory DMUB setup described by this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.h` builds `dmub_srv_dcn42_reg_offset`, `dmub_srv_dcn42_reg_shift`, and `dmub_srv_dcn42_reg_mask` tables from `DMCUB_*`, `HOST_INTERRUPT_CSR`, `MMHUBBUB_SOFT_RESET`, and DCN VM fields covered here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c` includes this header for HPD and DMCUB outbox interrupt source setup, including `DMCUB_INTERRUPT_ENABLE` and `DMCUB_INTERRUPT_ACK` fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.h` consumes `DCN_VM_FB_LOCATION_*`, `DCN_VM_AGP_*`, `DCHUBBUB_SDPIF_CFG0/1`, and related DCHUBBUB masks in hubbub register/field tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.c` writes SDPIF request/port-control fields through those tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn42/dcn42_mmhubbub.c` updates `MMHUBBUB_CLOCK_CNTL` fine-grain clock-gating fields that are part of the MMHUBBUB family in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` initializes DCN 4.2 audio resources using `AZALIA_AUDIO_DTO`, `AZALIA_CONTROLLER_CLOCK_GATING`, and endpoint/root codec field masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h` defines audio field-list macros for endpoint index/data, supported rate/power-state fields, and related Azalia codec metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce/dce_hwseq.h` supplies shared hardware-sequencer audio register and field-list macros consumed by DCN 4.2 hardware sequencing.

Behaviorally, this range sits at several display integration boundaries: display firmware command transport, interrupt routing, captured-frame/writeback memory traffic, display audio, performance observation, and hubbub memory/VM request policy.

## Risks And Edge Cases

- These are untyped preprocessor constants. An incorrect shift or mask can compile cleanly and only surface as a runtime register-programming failure on specific hardware paths.
- The header is generated. Manual edits risk divergence from AMD's register source, the offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are artificial. The first lines are the tail of `DIG_INTERRUPT_DEST`, and the final lines stop inside the DCHUBBUB SDPIF pipe security/noalloc family. Adjacent chunk reports are needed before making whole-file claims.
- Interrupt destination, enable, acknowledge, and status fields are especially side-effect-sensitive. Wrong masks can route events incorrectly, leave interrupt status stuck, miss HPD/AUX/audio/DMUB events, or create interrupt storms.
- DMCUB region and mailbox fields are boot-critical. Bad base/top/offset/high-address masks can make firmware fetch the wrong memory, corrupt ring buffers, break command submission, or make debug/fault readback misleading.
- DMCUB register mailbox and `HOST_INTERRUPT_CSR` fields form a host/firmware synchronization path. Incorrect ready, response, status, enable, or acknowledge bits can deadlock command exchanges or lose outbox notifications.
- RBBMIF timeout-disable and status bits can hide or misreport DMCUB bus timeouts. Overly broad masks could disable detection for unrelated clients.
- MCIF writeback buffer address, high-address, VMID, security, TMZ, pitch, size, and resolution fields affect memory writes. Wrong masks risk corrupted captures, writes to wrong memory, VM/security violations, overrun/underrun reports, or failures only with high addresses or protected surfaces.
- MMHUBBUB memory-power, clock-gating, soft-reset, and warmup fields are sequencing-sensitive and can interact with suspend/resume, idle power states, display writeback, and firmware initialization.
- Azalia endpoint, stream, DMA, DTO, clock-gating, power-state, and CRC fields affect display audio. Incorrect masks can produce silent audio, format/rate capability mismatches, bad DMA behavior, clocking issues, or unreliable CRC diagnostics.
- DCHUBBUB framebuffer/AGP/local-HBM address fields and pipe security/noalloc levels affect display memory request policy. Incorrect masks can produce VM faults, security-level mismatches, incorrect physical request behavior, or failures under host-VM/RIOMMU paths.
- Perfmon fields are diagnostic but still sensitive: bad select, clear, enable, or compare masks can invalidate performance data or trigger misleading interrupts.

## Test Signals

Useful validation should combine generated-header consistency checks with runtime display and firmware behavior:

- Build DCN 4.2 AMDGPU display support. Missing or renamed macros should surface in `dmub_dcn42.c`, `dmub_dcn42.h`, `irq_service_dcn42.c`, `dcn42_hubbub.h`, `dcn42_hubbub.c`, `dcn42_mmhubbub.c`, `dcn42_resource.c`, `dcn42_resource.h`, and shared DCE audio/hardware-sequencer headers.
- Mechanically compare this range against the authoritative DCN 4.2 register-field database and verify every `_MASK` has the expected paired `__SHIFT`.
- Cross-check registers in this range against `dcn_4_2_0_offset.h` so every field-bearing register has a matching offset/base-index entry.
- Boot DCN 4.2 hardware with DMUB enabled and verify firmware load, region-window setup, inbox/outbox ring pointer movement, register mailbox responses, GPINT/IH behavior, and DMCUB debug/fault readbacks.
- Exercise DMUB outbox interrupts and host register mailbox interrupts. Expected signals are one interrupt per event, correct acknowledge behavior, no stuck status bits, and no missed ready/response notifications.
- Force or simulate DMCUB fault and timeout paths where possible, then check `DMCUB_INST_FETCH_FAULT_ADDR`, `DMCUB_DATA_WRITE_FAULT_ADDR`, `DMCUB_UNDEFINED_ADDRESS_FAULT_ADDR`, and RBBMIF status/flag registers.
- Exercise display writeback across buffer slots, high physical addresses, protected/TMZ paths, different pitches/resolutions, and rapid enable/disable transitions. Watch for MCIF writeback overrun, slice interrupt, buffer-status, VMID/security, and address-fence anomalies.
- Test suspend/resume, idle power transitions, and clock-gating toggles with DMUB, MMHUBBUB, audio, and writeback active; expected results are restored register state and no stuck memory-power status.
- Exercise display audio on all exposed DCN 4.2 audio instances: stream enable/disable, format/rate changes, endpoint capability reads, clock gating, DTO programming, and CRC diagnostics. Expected signals are stable audio, correct capabilities, and no DMA/RIRB/CORB errors.
- Validate interrupt routing for HPD, HPD RX, I2C/DDC, AUX, DSC, HPO, DPP, and audio event families on real connectors where available.
- Use perfmon instances 3 and 4 to select counters, clear counters, run a workload, and read high/low values; expected signals are monotonic or workload-correlated values and correct compare/interrupt behavior.
- Exercise host-VM, AGP/framebuffer aperture, local-HBM, SDPIF credit/error, and pipe security/noalloc paths under multi-plane display workloads. Expected signals are no unexpected VM faults, no SDPIF credit errors, and valid force-IO status only when intentionally triggered.

## Cross-Chunk Notes

This chunk begins after the semantic start of `DIG_INTERRUPT_DEST`, so earlier `DIG_INTERRUPT_DEST` fields are owned by the previous chunk. It ends inside the DCHUBBUB SDPIF pipe field family after `DCHUBBUB_SDPIF_PIPE_GPUVM_SEC_LVL`; adjacent later chunks should cover any remaining pipe-security/noalloc, DCHUBBUB, or VM fields. The merge lane should reconcile those boundaries before producing whole-file conclusions for `dcn_4_2_0_sh_mask.h`.
