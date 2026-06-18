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
