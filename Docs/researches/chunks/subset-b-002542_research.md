# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 39974-42401

## Scope

This chunk is a generated AMD GC 11.0.3 shift/mask register-header segment. It contains preprocessor constants only: each hardware register field is represented by a `__SHIFT` macro and a matching `__MASK` macro used by AMDGPU register helpers to pack and unpack 32-bit register values. There are no functions, structs, enums, variables, includes, memory allocations, locks, callbacks, branches, or direct MMIO operations in this range.

The selected lines start in the middle of `RLC_RLCS_GPM_LEGACY_INT_DISABLE`, immediately after the first field shift from the preceding chunk. They then finish the tail of the `gc_rlc_rlcsdec` register-field map, cover the full visible `gc_pfvfdec_rlc`, `gc_pwrdec`, and `gc_pspdec` address-block sections, and enter the `gc_gfx_imu_gfx_imudec` block. The chunk ends after the first two `GFX_IMU_DPM_CONTROL` shifts; the remaining `GFX_IMU_DPM_CONTROL` masks and later GFX IMU RAM fields continue in the next adjacent chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM register metadata for the GC 11.0.3 graphics IP. It is not Ceph filesystem logic.

## Purpose

`gc_11_0_3_sh_mask.h` supplies bit layouts for GC 11.0.3 registers. Driver code pairs these macros with register addresses from the matching `gc_11_0_3_offset.h` header and uses helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to set or decode a named field without embedding raw bit positions and masks.

This chunk concentrates on RLC/RLCS control and telemetry, power-clock gating controls, PSP-visible graphics debug/security windows, and graphics IMU mailboxes and interrupt plumbing:

- RLC/RLCS global power-management interrupt, graphics-command-response, UTCL2 override, IMU/RLC message, telemetry, RAM-access, doorbell-fence, SDMA interrupt, clock-gating, memory-power, IH, and decode-end fields.
- RLC PF/VF decode fields for safe mode, streaming performance monitor sampling and interrupt reporting, command-submission instruction-buffer address/length, CP scheduler masks, EOF/spare interrupt counters, and PACE/RLCV spare interrupt state.
- Graphics power decode fields for CGTT/CGCG/ICG/MGCG controls across TCC, SPI, VGT, IA, WD, GS/NGG, PA, SC, SQ, TA, DB, CB, CP, CPF, CPC, RLC, GCEA, GL1/GL2, CHI/CHR, GUS, PH, UTCL1, and LDS/CHC/CHCG blocks.
- PSP decode fields for CP MES/MEC/GFX RS64 debug-memory indexed access, CPG/CPC PSP debug control, GRBM IOV error FIFO, GRBM security and CAM/HYP_CAM indexed data, and first RLC firmware-log violation address capture.
- Graphics IMU decode fields for 48 C2P mailbox messages, mailbox access controls, power-management IRQ control, MP1/RLC mutex and command/data/status exchange, SOC request path, VF control, telemetry, scratch registers, timestamp offset registers, core/PIC interrupt masks/levels/edges/priorities/status, interrupt-handler metadata, VID change, clock bypass, clock control, doorbell control, RLC clock-gating/throttle/reset-vector/override, and the beginning of DPM accumulator control.

## Important APIs, Types, And Macros

There are no callable APIs or C data types. The public surface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field low-bit position.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for the field.
- Register address symbols live in companion generated headers, usually as `mm...` constants in `gc_11_0_3_offset.h`.
- Consumers normally combine address macros and shift/mask macros through AMDGPU register helpers, MMIO read/modify/write paths, firmware message code, reset flows, virtualization handling, perf monitoring, and debug dumps.

The main macro families in this slice are:

- `RLC_RLCS_*`: RLCS-side controls for source IDs, `GCR_DATA_0..3` phase payloads, `GCR_STATUS` busy/out-count/response tag, perfmon clock state, UTCL2 GPA/VF and permission overrides, IMU-to-RLC and RLC-to-IMU mailbox data/control/toggle bits, telemetry current/voltage/temperature, mutex acquire state, gfxoff/deep-sleep status, IMU RAM address/data request toggles, GFX doorbell fence acknowledgement, SDMA interrupt auto-ack/status/info, PMM CGCG control, graphics memory power control and RM control, interrupt-handler context/ring/VM/source/VF metadata, and `RLC_RLCS_DEC_END`.
- `RLC_*` in `gc_pfvfdec_rlc`: `RLC_SAFE_MODE`, SPM sample and memory-controller controls, SPM interrupt control/status/info, CSIB address and length, CP scheduler bitmap, EOF interrupt status/count, spare interrupt counters, and PACE/RLCV spare interrupt state.
- `CGTT_*`, `CGTX_*`, `CGTS_*`, `ICG_*`, `GFX_ICG_*`, `*_CGTT_*`, `*_CLK_CTRL`, and `*_MGCG_OVERRIDE`: power and clock gating fields. These typically expose override, disable, delay, threshold, hysteresis, force-on, and per-subblock gating controls for graphics front-end, shader, texture, LDS, cache, primitive, color/depth, command-processor, RLC, GL1/GL2, and UTCL1 blocks.
- `CP_*_DM_INDEX_*`, `CPG_PSP_DEBUG`, `CPC_PSP_DEBUG`, `GRBM_*`, and `RLC_FWL_FIRST_VIOL_ADDR`: PSP-facing indexed debug-memory controls, PSP debug enable/index fields, GRBM IOV/security/CAM data windows, hypervisor CAM data windows, and first firmware-log violation address capture.
- `GFX_IMU_C2PMSG_*`: 48 full-width command-to-power mailbox registers, plus access-control bitmaps that gate who may read or write groups of C2P messages.
- `GFX_IMU_*` mailbox, status, telemetry, scratch, timestamp, interrupt, IH, power, and RLC-interaction registers: full-width data/status fields, request/ack/change/done toggles, mutex request/acquire bits, VF enable/ID state, telemetry current/voltage/temperature, scratch data, GTS timestamp offset low/high words, PIC interrupt mask/level/edge/priority/status, IH context/ring/VM/source/VF metadata, VID-change request/ack/data/source fields, clock-bypass/divider/cooldown fields, doorbell fence override/status, RLC reset-vector exit source, and DPM accumulator start/reset fields.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 11.0.3 register address and shift/mask headers for the active ASIC generation.
2. Read a hardware register, prepare a register write value, or assemble an indexed/debug access payload.
3. Use the generated `__SHIFT` and `__MASK` pairs, often through field helpers, to pack one field into a register value or extract one field from a status value.
4. Write the value through AMDGPU MMIO/indexed-register paths, mailbox paths, reset/power-management routines, PSP/RLC/IMU message code, or debug/perf reporting code.
5. For status paths, decode returned bits into idle-wait decisions, interrupt handling, telemetry, virtualization attribution, power-state decisions, or diagnostic output.

For the RLC/RLCS and GFX IMU message registers, higher-level control flow is handshake-oriented: one side writes data/control registers, toggles a change/request bit, and polls or receives an indication through done/ack/status bits. For SPM and DPM counters, software configures sampling or accumulation, starts or resets counting, then reads status/result fields. For clock/power gates, code applies masks as part of ASIC bring-up, power-management transitions, firmware sequencing, or debug overrides. This header does not define required ordering, polling intervals, reset defaults, clear-on-read behavior, or firmware ownership rules.

## State And Persistence Behavior

The macros are stateless and persist nothing. They describe stateful hardware registers owned by the GPU, firmware, PSP, RLC, IMU, power-management logic, virtualization fabric, and AMDGPU runtime.

RLC/RLCS message, mutex, RAM-access, doorbell-fence, and status fields represent live firmware and hardware coordination state. Toggle fields such as `CHGTOG`, `DONETOG`, `REQTOG`, and `ACKTOG` are especially order-sensitive: missing an edge or writing a stale toggle value can make a mailbox or RAM transaction appear stuck. Status bits such as `ALLOW_GFXOFF`, `ALLOW_FA_DCS`, `DISABLE_GFXCLK_DS`, `PWR_DOWN_ACTIVE`, and `RLC_ALIVE` are volatile and should be decoded as snapshots rather than persistent software state.

The PF/VF RLC decode registers include virtualization- and interrupt-facing state. Safe-mode, scheduler, EOF, spare interrupt, and SPM fields may influence or report behavior across physical and virtual functions. Fields that count or latch interrupt events can require explicit clear sequences not expressible in a shift/mask header.

Clock-gating and memory-power registers persist programmed power policy until firmware or driver code changes them, or until reset/power gating restores defaults. Many fields are overrides or disables rather than passive status. Incorrect full-register writes can force clocks on, disable low-power states, or gate clocks while a block is active.

PSP debug, GRBM security, CAM, HYP_CAM, and firmware-log violation registers are sensitive diagnostic and isolation state. Indexed access windows depend on a correct index/data sequence. IOV, security, and violation fields may be sticky or privilege-controlled, and stale values can misattribute a security or virtualization fault.

GFX IMU C2P mailbox, RLC command, SOC request, VF control, telemetry, scratch, GTS offset, interrupt-controller, IH, VID-change, clock, doorbell, and reset-vector fields describe live communication and power-management state. Scratch and timestamp offset registers can act as persistent firmware/driver rendezvous storage while the IMU is running. Interrupt mask/level/edge/priority state persists configured routing until changed, and `GFX_IMU_PIC_INT_STATUS` exposes volatile pending status bits. The chunk-ending `GFX_IMU_DPM_CONTROL` fields are incomplete here; the masks and result counters are in the next chunk.

Reserved masks appear throughout the chunk. Callers should preserve reserved bits during read-modify-write unless the hardware programming sequence explicitly requires a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.3 register family remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` supplies matching register addresses.
- The matching generated default/reset-value header, where present, supplies expected defaults for many of these registers.
- AMDGPU common register helpers provide field packing/extraction and MMIO/indexed-register access.
- RLC, GFXOFF, clock/power management, PSP, SR-IOV, interrupt handling, perf/telemetry, debugfs, hang-dump, and reset code depend on the exact field positions.

Key integration points include RLC firmware mailbox handling, IMU/RLC command exchange, RLC RAM indexed access, SDMA-to-RLC interrupt acknowledgement, SPM sampling and interrupt reporting, command-submission instruction-buffer setup, CP scheduler and EOF signaling, graphics clock-gating programming, memory-power control, PSP debug-memory access, GRBM IOV/security fault reporting, GRBM CAM/HYP_CAM inspection, IMU C2P mailbox communication with power firmware, MP1/IMU mutex handling, SOC request forwarding, VF control in virtualized environments, telemetry collection, timestamp calibration, IMU interrupt routing, IMU-originated IH packets, VID-change requests, doorbell fence override/status, RLC reset-vector selection, and DPM accumulation.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask compiles cleanly but can write a different hardware field or decode misleading state.
- This chunk starts and ends mid-register family. `RLC_RLCS_GPM_LEGACY_INT_DISABLE__GC_CAC_EDC_EVENT_CHANGED__SHIFT` is in the previous chunk, and `GFX_IMU_DPM_CONTROL` masks are in the next chunk. File-level analysis must reconcile adjacent chunks.
- Toggle-based handshakes are easy to misuse. `CHGTOG`/`DONETOG`, `REQTOG`/`ACKTOG`, and request/ack fields need edge-aware consumers; simply writing a constant field value can deadlock communication.
- Clock-gating and memory-power fields are high-impact side-effect registers. Bad masks can cause hangs, excessive power draw, failed gfxoff entry, or blocks being gated while active.
- Virtualization and security registers need exact VF/VFID/source attribution. Misdecoded PF/VF, CAM, HYP_CAM, IOV, or violation-address fields can send reset or fault handling to the wrong function.
- Indexed debug windows require correct index/data sequencing. Mixing up CP MES, MEC, GFX RS64, GRBM CAM, and HYP_CAM indices can return plausible but unrelated data.
- Full-width mailbox, scratch, and data registers use `0xFFFFFFFFL`; partial writes through the wrong helper can lose firmware payload bits.
- Interrupt mask/level/edge/priority programming is persistent. Incorrect priority or polarity fields can hide IMU events, create repeated interrupts, or route IH packets with wrong source/context metadata.
- Address and timestamp high/low register pairs can be race-prone if read or written without documented latching or ordering. The shift/mask header cannot express atomicity requirements.
- Reserved fields are numerous. Writes that fail to preserve reserved bits may change undocumented firmware or ASIC behavior.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_11_0_3_sh_mask.h`, especially RLC, GFXOFF, power-management, PSP, virtualization, interrupt, and telemetry paths.
- Mechanical comparison against AMD's authoritative GC 11.0.3 register database for every `__SHIFT` and `__MASK` in lines 39974-42401.
- Cross-checks that each register comment in this chunk has a corresponding address macro in `gc_11_0_3_offset.h` and, where expected, a default/reset value in the generated default header.
- Static shift/mask sanity checks: masks align with shifts, fields in the same register do not overlap unless documented, full-width data fields use `0xFFFFFFFFL`, low/high address pairs have consistent widths, and reserved masks fill only unused bits.
- RLC/IMU mailbox tests that send messages both directions and verify change/done/request/ack toggles, mutex acquire behavior, status transitions, and timeout handling.
- RLC RAM-access and GCR tests that validate request/ack completion, phase data packing, busy/out-count status, and response tags.
- GFXOFF and power-management tests that exercise `ALLOW_GFXOFF`, deep-sleep disable, graphics memory power control, clock-gating overrides, VID change, DPM accumulator start/reset, and post-resume restore.
- SPM and telemetry tests that configure sampling/interrupts, collect current/voltage/temperature data, and verify interrupt status/info fields under controlled workloads.
- PSP/debug tests that use CP MES/MEC/GFX RS64 indexed access and GRBM CAM/HYP_CAM windows, validating index/data sequencing and privilege restrictions.
- SR-IOV tests that trigger VF reset, IOV/security errors, doorbell fence behavior, and violation logging, then confirm source/VF/VM attribution.
- Interrupt tests that vary IMU PIC mask, level, edge, priority, status, and IH metadata fields, then confirm expected interrupt routing and clearing.
- Runtime warning signals include stuck RLC/IMU mailbox toggles, failed gfxoff entry, unexpected power draw, SDMA/RLC interrupt timeouts, missing telemetry, wrong PSP debug data, repeated IMU interrupts, invalid VF attribution, GRBM security violations with impossible source IDs, or GPU reset loops after clock/power programming.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002542`. It covers lines 39974-42401 of `gc_11_0_3_sh_mask.h`. The final per-file research should merge it with adjacent chunks to complete the partial `RLC_RLCS_GPM_LEGACY_INT_DISABLE` and `GFX_IMU_DPM_CONTROL` families and to place the RLC/RLCS, PF/VF RLC, power decode, PSP decode, and GFX IMU definitions in the full GC 11.0.3 register map.
