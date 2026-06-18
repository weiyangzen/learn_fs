# subset-b-001368 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_sdma_pkt_open.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_sdma_pkt_open.h

## Purpose

`vega10_sdma_pkt_open.h` is a generated-style packet layout header for Vega10-family SDMA command streams. It contains no executable code, storage, or exported C objects. Its job is to give packet emitters symbolic opcodes, sub-opcodes, dword offsets, masks, shifts, and packing macros for constructing binary SDMA packets written into GPU command buffers.

The file covers ordinary SDMA packets and AQL SDMA packets. The ordinary packet families include linear, tiled, broadcast, sub-window, structure, PTE/PDE, write, fill, poll, atomic, semaphore, fence, indirect, timestamp, trap, dummy trap, pre-execute, conditional execute, SRBM write, and NOP packets. The AQL packet families cover a generic AQL header, AQL linear copy, and AQL barrier-or packet.

## Important APIs, Types, And Macros

The public surface is entirely macro-based:

- Top-level opcode macros define packet classes: `SDMA_OP_NOP`, `SDMA_OP_COPY`, `SDMA_OP_WRITE`, `SDMA_OP_INDIRECT`, `SDMA_OP_FENCE`, `SDMA_OP_TRAP`, `SDMA_OP_SEM`, `SDMA_OP_POLL_REGMEM`, `SDMA_OP_COND_EXE`, `SDMA_OP_ATOMIC`, `SDMA_OP_CONST_FILL`, `SDMA_OP_PTEPDE`, `SDMA_OP_TIMESTAMP`, `SDMA_OP_SRBM_WRITE`, `SDMA_OP_PRE_EXE`, and `SDMA_OP_DUMMY_TRAP`.
- Sub-opcode macros specialize shared packet classes, for example `SDMA_SUBOP_COPY_LINEAR`, `SDMA_SUBOP_COPY_TILED`, `SDMA_SUBOP_COPY_T2T_SUB_WIND`, `SDMA_SUBOP_PTEPDE_COPY`, `SDMA_SUBOP_PTEPDE_RMW`, and timestamp/poll/fill sub-ops.
- `SDMA_PKT_HEADER_OP(x)` and `SDMA_PKT_HEADER_SUB_OP(x)` provide generic header field packing for the common op/sub-op fields.
- Every packet field has a regular macro quartet: `<packet>_<word>_<field>_offset`, `_mask`, `_shift`, and a packing helper such as `SDMA_PKT_COPY_LINEAR_COUNT_COUNT(x)`.
- The AQL portion uses the same field pattern with names such as `SDMA_AQL_PKT_HEADER_HEADER_FORMAT(x)`, `SDMA_AQL_PKT_COPY_LINEAR_COMPLETION_SIGNAL_LO_COMPLETION_SIGNAL_31_0(x)`, and `SDMA_AQL_PKT_BARRIER_OR_DEPENDENT_ADDR_0_LO_DEPENDENT_ADDR_0_31_0(x)`.

Important packet groups and their roles:

- Copy packets: `SDMA_PKT_COPY_LINEAR`, `SDMA_PKT_COPY_DIRTY_PAGE`, `SDMA_PKT_COPY_PHYSICAL_LINEAR`, `SDMA_PKT_COPY_BROADCAST_LINEAR`, `SDMA_PKT_COPY_LINEAR_SUBWIN`, `SDMA_PKT_COPY_TILED`, `SDMA_PKT_COPY_L2T_BROADCAST`, `SDMA_PKT_COPY_T2T`, `SDMA_PKT_COPY_TILED_SUBWIN`, and `SDMA_PKT_COPY_STRUCT`.
- Write/fill packets: `SDMA_PKT_WRITE_UNTILED`, `SDMA_PKT_WRITE_TILED`, `SDMA_PKT_WRITE_INCR`, `SDMA_PKT_CONSTANT_FILL`, and `SDMA_PKT_DATA_FILL_MULTI`.
- Page-table packets: `SDMA_PKT_PTEPDE_COPY`, `SDMA_PKT_PTEPDE_COPY_BACKWARDS`, and `SDMA_PKT_PTEPDE_RMW`.
- Synchronization/control packets: `SDMA_PKT_INDIRECT`, `SDMA_PKT_SEMAPHORE`, `SDMA_PKT_FENCE`, `SDMA_PKT_TRAP`, `SDMA_PKT_DUMMY_TRAP`, `SDMA_PKT_NOP`, `SDMA_PKT_PRE_EXE`, and `SDMA_PKT_COND_EXE`.
- Poll/verify packets: `SDMA_PKT_POLL_REGMEM`, `SDMA_PKT_POLL_REG_WRITE_MEM`, `SDMA_PKT_POLL_DBIT_WRITE_MEM`, and `SDMA_PKT_POLL_MEM_VERIFY`.
- Timestamp and atomic packets: `SDMA_PKT_ATOMIC`, `SDMA_PKT_TIMESTAMP_SET`, `SDMA_PKT_TIMESTAMP_GET`, and `SDMA_PKT_TIMESTAMP_GET_GLOBAL`.

## Control Flow

There is no runtime control flow in this header. Runtime behavior emerges when SDMA ring emitters combine the macros into ordered 32-bit dwords. A typical flow is:

1. Emit a packet header dword with `*_HEADER_OP(SDMA_OP_*)` and, when applicable, `*_HEADER_SUB_OP(SDMA_SUBOP_*)`.
2. Emit payload dwords in the numeric order defined by each field's `_offset`.
3. Split 64-bit GPU or system addresses into low and high dwords with the corresponding `*_ADDR_LO_*` and `*_ADDR_HI_*` field helpers.
4. Set mode bits such as `tmz`, `encrypt`, `broadcast`, `detile`, `mip_max`, `vmid`, cache/snoop flags, or AQL fence scopes as required by the packet type.

The command processor firmware and SDMA hardware interpret the resulting dword stream; this file does not validate packet sequencing or constraints.

## State And Persistence Behavior

The header is stateless. It neither reads nor writes kernel memory, hardware registers, GPU memory, files, nor persistent configuration. The state it influences is external: SDMA command buffers, GPU-visible memory, interrupt side effects, fences, and page table updates produced by callers that use these macros.

Because the helpers do not cast or size-check inputs, state correctness depends on callers passing already-normalized field values. Values outside a field width are silently masked.

## Dependencies

The file only depends on the C preprocessor and its include guard. It does not include other headers. Semantic dependencies are external and hardware-specific:

- SDMA firmware/hardware packet ABI for Vega10-compatible engines.
- AMDGPU packet emitter code that writes ring dwords.
- Address and tiling metadata from memory-management and graphics code.
- AQL consumers that need SDMA AQL packet layout compatibility.

## Integration Points

This header integrates with AMDGPU code that builds SDMA command streams. A repository search shows the broader tree has multiple ASIC-specific `*_sdma_pkt_open.h` headers with similar macro naming. Packet emitters include the appropriate ASIC header through their SDMA implementation or shared packet-building code.

Important integration expectations:

- Offsets are dword indexes, not byte offsets.
- Address fields often carry alignment-implied bit ranges, for example timestamp write address macros use `write_addr_31_3` shifted by 3.
- Count masks differ by packet type, such as 22-bit linear copy counts, 20-bit tiled counts, 19-bit PTE/PDE counts, and full 32-bit structure fields.
- The `tmz` and `encrypt` bits are security-sensitive because they influence trusted-memory/encrypted copy behavior.
- Broadcast and tiled packet layouts have additional destination, swizzle, pitch, slice-pitch, dimension, and mip fields that must match surface metadata.

## Risks

- Silent truncation is the main risk. Every packing macro masks `x` and shifts it; an invalid large value may produce a syntactically valid but semantically wrong packet.
- Packet definitions are hardware ABI. A wrong offset, mask, or shift can corrupt GPU memory, page tables, fences, or synchronization state.
- Header op/sub-op combinations are not type-safe. Callers can combine macros from one packet family with opcodes from another.
- 64-bit address splitting must be correct and alignment rules must be satisfied by callers.
- Page table packets and atomics can mutate memory-management state. Incorrect masks or counts can be high impact.
- AQL packet fields include completion signals and dependency addresses; bad values can break queue synchronization.

## Test Signals

Useful validation signals are mostly integration-level:

- Build coverage for all SDMA emitters that include this header.
- GPU ring tests that emit linear copy, tiled copy, fill, fence, semaphore, timestamp, poll, and indirect packets.
- IGT or AMDGPU selftests that verify SDMA copy correctness across VRAM, GTT, TMZ/encrypted memory, and tiled surfaces.
- VM/page-table stress tests that exercise PTE/PDE copy/RMW/backwards packets.
- Fault injection or debug logs around SDMA timeouts, bad fences, page faults, or ring hangs after packet changes.
- Static checks comparing these generated masks/offsets against the authoritative hardware register packet XML or generated source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_sdma_pkt_open.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega20_ih.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega20_ih.c

## Purpose

`vega20_ih.c` implements the AMDGPU interrupt handler (IH) IP block for Vega20-generation OSSSYS IH hardware. It initializes interrupt ring buffers, programs their register offsets and doorbells, enables and disables interrupt delivery, reads and advances write/read pointers, handles overflow recovery, dispatches secondary IH ring work, and exposes the block through `amd_ip_funcs` and `amdgpu_ih_funcs`.

The implementation supports primary ring `adev->irq.ih`, secondary rings `ih1` and `ih2`, and software ring `ih_soft`. It also has SR-IOV paths where IH control register programming may be delegated to PSP firmware instead of direct MMIO writes.

## Important APIs, Types, And Functions

Exported objects:

- `const struct amd_ip_funcs vega20_ih_ip_funcs`: AMDGPU IP lifecycle entry points for early init, software init/fini, hardware init/fini, suspend/resume, reset, idle, clock gating, and power gating.
- `const struct amdgpu_ip_block_version vega20_ih_ip_block`: IP block descriptor with type `AMD_IP_BLOCK_TYPE_IH`, version 4.2.0, and `vega20_ih_ip_funcs`.

Internal function groups:

- Register layout: `vega20_ih_init_register_offset()` fills `struct amdgpu_ih_regs` for ring0, ring1, and ring2 based on `OSSSYS` SOC15 register offsets and PSP register IDs.
- Ring enable/disable: `vega20_ih_toggle_ring_interrupts()` toggles `IH_RB_CNTL.RB_ENABLE`, GPU timestamp enable, overflow clear, and ring0 `ENABLE_INTR`; `vega20_ih_toggle_interrupts()` applies that to every allocated hardware ring.
- Ring programming: `vega20_ih_rb_cntl()` constructs core `IH_RB_CNTL` fields; `vega20_ih_doorbell_rptr()` and `vega20_setup_retry_doorbell()` construct doorbell control values; `vega20_ih_enable_ring()` writes base address, control, writeback address, pointers, and doorbell rptr.
- Hardware lifecycle: `vega20_ih_irq_init()` disables interrupts, configures NBIO IH control, programs ASIC-specific `IH_CHICKEN` behavior, enables rings, configures doorbell range and retry CAM, and re-enables interrupts. `vega20_ih_irq_disable()` disables all rings and waits briefly.
- Pointer operations: `vega20_ih_get_wptr()` reads write pointers from writeback memory or registers, detects and clears overflow, and adjusts the read pointer after overflow. `vega20_ih_set_rptr()` writes the read pointer through doorbells or MMIO. `vega20_ih_irq_rearm()` retries lost SR-IOV doorbell writes.
- Self interrupt dispatch: `vega20_ih_self_irq()` schedules `ih1_work` or `ih2_work` based on `entry->ring_id`; `vega20_ih_set_self_irq_funcs()` wires the IRQ source.
- IP lifecycle: `vega20_ih_early_init()`, `vega20_ih_sw_init()`, `vega20_ih_sw_fini()`, `vega20_ih_hw_init()`, `vega20_ih_hw_fini()`, `vega20_ih_suspend()`, and `vega20_ih_resume()`.
- Power management: `vega20_ih_update_clockgating_state()`, `vega20_ih_set_clockgating_state()`, and no-op `vega20_ih_set_powergating_state()`.

Important external types and helpers include `struct amdgpu_device`, `struct amdgpu_ih_ring`, `struct amdgpu_ih_regs`, `struct amdgpu_irq_src`, `struct amdgpu_iv_entry`, `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, `WREG32_NO_KIQ`, `WDOORBELL32`, `SOC15_REG_OFFSET`, `WREG32_SOC15`, `WREG32_FIELD15`, `amdgpu_ih_ring_init()`, `amdgpu_irq_init()`, and `psp_reg_program()`.

## Control Flow

Driver bring-up starts with `vega20_ih_early_init()`, which installs IH function tables. `vega20_ih_sw_init()` registers the self-IRQ source, decides whether rings use bus addresses, allocates ring0, ring1, conditionally ring2, and the software ring, assigns doorbell indices, initializes per-ring register offsets, and calls generic IRQ software initialization.

Hardware initialization flows through `vega20_ih_hw_init()` to `vega20_ih_irq_init()`:

1. Disable all allocated rings via `vega20_ih_toggle_interrupts(false)`.
2. Let NBIO perform IH control setup through `adev->nbio.funcs->ih_control(adev)`.
3. On bare metal, program `IH_CHICKEN` or Aldebaran-specific `mmIH_CHICKEN_ALDEBARAN` when the ASIC/version and address-space mode require `MC_SPACE_GPA_ENABLE`.
4. For each allocated hardware ring, call `vega20_ih_enable_ring()` and clear the software overflow flag.
5. Program the IH doorbell range on non-SR-IOV configurations.
6. Enable PCI bus mastering.
7. Allocate and program the retry CAM doorbell, then enable retry CAM using normal or Aldebaran-specific registers.
8. Re-enable all hardware rings via `vega20_ih_toggle_interrupts(true)`.
9. Mark `ih_soft` enabled when its ring exists.

Interrupt processing uses the generic AMDGPU IRQ flow through `adev->irq.ih_funcs`. `get_wptr` obtains the producer pointer. Ring0 normally uses memory writeback; secondary rings fall back to register reads. If overflow is detected, the handler warns, advances `ih->rptr` to `(wptr + 32) & ptr_mask`, clears hardware overflow, and returns the masked pointer. After consumers parse IV entries, `set_rptr` publishes the consumer pointer through a doorbell or MMIO register.

Self-IRQ entries from the IH client schedule asynchronous work for ring1 or ring2. Suspend and resume map directly to hardware fini/init.

## State And Persistence Behavior

Persistent state is in `adev->irq` and hardware registers, not on disk. The file mutates:

- Ring allocation fields, `ring_size`, `enabled`, `rptr`, `overflow`, `gpu_addr`, `wptr_addr`, `wptr_cpu`, `rptr_cpu`, `use_bus_addr`, `use_doorbell`, and `doorbell_index`.
- Register offset descriptors under `ih->ih_regs`.
- Device doorbell state including `adev->irq.retry_cam_doorbell_index` and `adev->irq.retry_cam_enabled`.
- Hardware IH registers for ring base, control, read/write pointers, doorbell read pointers, writeback address, retry CAM, `IH_CHICKEN`, and clock-control overrides.

State is re-created during driver load or resume. Ring hardware pointers are reset to zero when rings are disabled or enabled. Overflow handling updates the software read pointer to reduce the chance of parsing overwritten vectors.

## Dependencies

The file includes Linux PCI support and AMDGPU internal headers: `amdgpu.h`, `amdgpu_ih.h`, `soc15.h`, OSSSYS register offset/mask headers, `soc15_common.h`, and `vega20_ih.h`.

Runtime dependencies include:

- SOC15 register offset macros and OSSSYS register field definitions.
- NBIO callbacks for IH control and doorbell range programming.
- PSP register programming for SR-IOV virtual functions.
- AMDGPU interrupt core registration and ring allocation helpers.
- Doorbell index setup from Vega20 register initialization.
- PCI bus mastering.
- ASIC version checks for OSSSYS 4.2.1 and 4.4.x behavior.

## Integration Points

`vega20_ih_ip_block` is added by device discovery for supported ASICs. Generic AMDGPU IRQ code calls `adev->irq.ih_funcs->get_wptr`, `decode_iv`, `decode_iv_ts`, and `set_rptr`. The file relies on `vega20_doorbell_index_init()` from `vega20_reg_init.c` having established `adev->doorbell_index.ih` before `sw_init` assigns IH doorbells.

The IP block also integrates with:

- `amdgpu_irq_add_id()` for the self interrupt source.
- Workqueues `adev->irq.ih1_work` and `adev->irq.ih2_work` for secondary ring draining.
- SR-IOV paths that require PSP-mediated register writes and retry rearming.
- Clock gating control through `AMD_CG_SUPPORT_IH_CG`.

## Risks

- PSP programming failures return `-ETIMEDOUT`; incomplete error recovery can leave interrupts disabled during bring-up or resume.
- Overflow recovery intentionally skips to a guessed readable position. This can drop interrupt vectors, so downstream users must tolerate missed or delayed events after overflow.
- Ring0 has writeback and `ENABLE_INTR` behavior that secondary rings do not. Applying ring0 assumptions to ring1/ring2 would be incorrect.
- SR-IOV doorbell rearm loops are bounded by `MAX_REARM_RETRY`; persistent lost doorbell writes may still leave interrupts unacknowledged.
- ASIC-specific register selection for Aldebaran/OSSSYS 4.4.x is version-sensitive. Missing a new version can program the wrong retry CAM or chicken register.
- `vega20_ih_wait_for_idle()` deliberately returns `-ETIMEDOUT`, which means generic callers should not expect a useful idle wait implementation.
- The APU special case for OSSSYS 4.4.2 disables bus addresses. Regressions in address-space selection can break IH ring memory access.

## Test Signals

Useful test and debug signals:

- Driver load/resume on Vega20 and related OSSSYS 4.4.x ASICs should complete with `vega20_ih_irq_init()` returning zero.
- Interrupt-driven workloads should show advancing IH write/read pointers and no persistent `ring buffer overflow` warnings.
- Suspend/resume tests should confirm interrupts resume and rings are reinitialized.
- SR-IOV VF testing should cover PSP register programming paths and doorbell rearm behavior.
- MSI and non-MSI configurations should verify `RPTR_REARM` behavior on ring0.
- Secondary ring tests should confirm self IRQs schedule `ih1_work` and `ih2_work`.
- Clock gating tests should verify `IH_CLK_CTRL` soft override fields change only when `AMD_CG_SUPPORT_IH_CG` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega20_ih.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega20_ih.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega20_ih.h

## Purpose

`vega20_ih.h` is the public declaration header for the Vega20 IH IP block implementation. It exposes the function-table object and IP-block descriptor defined by `vega20_ih.c` so other AMDGPU initialization code can reference and register the IH block.

## Important APIs, Types, And Functions

The header declares two external constants:

- `extern const struct amd_ip_funcs vega20_ih_ip_funcs;`
- `extern const struct amdgpu_ip_block_version vega20_ih_ip_block;`

It does not define local types, inline functions, register macros, or data structures. The referenced types are declared by AMDGPU core headers included by C files that include this header.

## Control Flow

There is no runtime control flow in the header. It participates in compile-time linkage:

1. A C file includes `vega20_ih.h`.
2. The compiler sees the external declarations.
3. Linkage resolves the objects to their definitions in `vega20_ih.c`.
4. Device discovery or ASIC setup code can pass `&vega20_ih_ip_block` into AMDGPU IP block registration.

## State And Persistence Behavior

The header has no mutable state and no persistence behavior. It only makes externally defined constant objects visible across translation units.

## Dependencies

The file depends on the definitions of `struct amd_ip_funcs` and `struct amdgpu_ip_block_version` being visible to consumers. It protects itself with `__VEGA20_IH_H__` include guards and carries AMD's MIT-style license text.

## Integration Points

Primary integration is with AMDGPU discovery and SOC setup code. Repository search shows `vega20_ih_ip_block` is used by discovery code to add the Vega20 IH block, while `vega20_ih.c` includes this header to keep declarations consistent with definitions.

## Risks

- If the declarations diverge from the definitions in `vega20_ih.c`, build or link failures will occur.
- Because the header does not include the core type declarations itself, include ordering must provide `struct amd_ip_funcs` and `struct amdgpu_ip_block_version`. This is normal for internal AMDGPU headers but can surprise isolated include tests.
- The include guard name must remain unique to avoid accidental exclusion with another header.

## Test Signals

Useful signals are build-oriented:

- Compile units that include `vega20_ih.h` without duplicate symbol or incomplete type errors.
- Link succeeds with `vega20_ih.c` included in the AMDGPU build.
- Device discovery can reference `vega20_ih_ip_block` and register the block for supported ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega20_ih.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega20_reg_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega20_reg_init.c

## Purpose

`vega20_reg_init.c` initializes Vega20-specific register base tables and doorbell index assignments inside `struct amdgpu_device`. These values are foundational configuration used by SOC15 register access macros and by IP blocks that need doorbell slots, including graphics, SDMA, IH, UVD/VCE, VCN, and non-CP clients.

## Important APIs, Types, And Functions

The file defines two functions:

- `int vega20_reg_base_init(struct amdgpu_device *adev)`: fills `adev->reg_offset[HWIP][instance]` for every `i < MAX_INSTANCE` using base arrays from `vega20_ip_offset.h`.
- `void vega20_doorbell_index_init(struct amdgpu_device *adev)`: fills `adev->doorbell_index` with Vega20 doorbell constants such as KIQ, MEC rings, user queue range, graphics ring, SDMA engine slots, IH, UVD/VCE, VCN, first/last non-CP, maximum assignment, and SDMA doorbell range.

Important data touched:

- `adev->reg_offset` indexed by hardware IP IDs: `GC_HWIP`, `HDP_HWIP`, `MMHUB_HWIP`, `ATHUB_HWIP`, `NBIO_HWIP`, `MP0_HWIP`, `MP1_HWIP`, `UVD_HWIP`, `VCE_HWIP`, `DF_HWIP`, `DCE_HWIP`, `OSSSYS_HWIP`, `SDMA0_HWIP`, `SDMA1_HWIP`, `SMUIO_HWIP`, `NBIF_HWIP`, `THM_HWIP`, `CLK_HWIP`, `UMC_HWIP`, and `RSMU_HWIP`.
- `adev->doorbell_index` fields including `kiq`, `mec_ring0..7`, `userqueue_start/end`, `gfx_ring0`, `sdma_engine[0..7]`, `ih`, `uvd_vce.*`, `vcn.*`, `first_non_cp`, `last_non_cp`, `max_assignment`, and `sdma_doorbell_range`.

## Control Flow

`vega20_reg_base_init()` performs a simple loop over hardware instances. For each instance, it assigns each supported hardware IP's register offset pointer to the corresponding `*_BASE.instance[i]` data from `vega20_ip_offset.h`. It returns zero unconditionally.

`vega20_doorbell_index_init()` is straight-line initialization. It copies predefined `AMDGPU_VEGA20_DOORBELL*` constants into the device doorbell-index structure. The function shifts `AMDGPU_VEGA20_DOORBELL_MAX_ASSIGNMENT` left by one for `max_assignment`, consistent with 32-bit doorbell indexing where some constants are 64-bit doorbell slots.

## State And Persistence Behavior

The file mutates runtime device initialization state only. It does not allocate memory, perform MMIO, access hardware directly, or persist anything to disk.

The assigned register-offset pointers persist for the lifetime of the `amdgpu_device` and are consumed by SOC15 access helpers. Doorbell indexes similarly persist as the canonical slot map used by later IP blocks. For example, `vega20_ih.c` derives IH doorbell indices from `adev->doorbell_index.ih`.

## Dependencies

The file includes `amdgpu.h`, `soc15.h`, `soc15_common.h`, and `vega20_ip_offset.h`. It depends on:

- `MAX_INSTANCE` and hardware IP enum indexes.
- Generated Vega20 base structures such as `GC_BASE`, `HDP_BASE`, `OSSSYS_BASE`, `SDMA0_BASE`, and `RSMU_BASE`.
- Vega20 doorbell constants such as `AMDGPU_VEGA20_DOORBELL_IH`, `AMDGPU_VEGA20_DOORBELL_sDMA_ENGINE0`, and `AMDGPU_VEGA20_DOORBELL64_VCN0_1`.
- `struct amdgpu_device` layout for `reg_offset` and `doorbell_index`.

## Integration Points

Repository references show `vega20_reg_base_init()` is called from SOC15/device discovery initialization paths before IP blocks rely on SOC15 register offsets. The IH implementation relies on the `ih` doorbell index assigned here. SDMA, graphics, compute, media, and user queue code rely on their assigned doorbell ranges to ring hardware queues without colliding.

The `NBIF_HWIP` register offset deliberately aliases `NBIO_BASE`, which reflects naming compatibility between NBIO/NBIF users in the driver. SDMA doorbell range is set to `20`, affecting how many doorbell slots are reserved for SDMA engines.

## Risks

- Incorrect register base pointers break all `SOC15_REG_OFFSET` users for the affected hardware IP and can lead to wrong MMIO addresses.
- Doorbell index collisions can cause one engine to ring another engine's queue or corrupt interrupt/read-pointer behavior.
- The comment contains typos, but the functional risk is in the hard-coded hardware map staying synchronized with generated Vega20 offset headers and ASIC variants.
- The function returns success unconditionally; there is no runtime validation that generated base tables are present or sized as expected.
- `max_assignment` uses a left shift. Changing doorbell units elsewhere without updating this function could cause off-by-one or unit mismatches.

## Test Signals

Useful validation signals:

- Early boot logs should show successful SOC15 register access after `vega20_reg_base_init()`.
- IP block initialization for GC, SDMA, IH, NBIO, OSSSYS, and media blocks should not fail due to invalid register offsets.
- Doorbell-based queue submission should work for KIQ, MEC rings, graphics, SDMA engines, IH read pointers, and media rings.
- Interrupt handling tests indirectly verify the IH doorbell assignment.
- Multi-engine SDMA workloads help verify `sdma_engine[0..7]` and `sdma_doorbell_range`.
- Static comparison against generated Vega20 offset and doorbell specification headers can catch drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega20_reg_init.c -->
