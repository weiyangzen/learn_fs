# subset-b-001365 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v4_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v4_0.c

## Purpose

`vce_v4_0.c` implements the AMDGPU VCE 4.0 video encode IP block. It wires the VCE block into the AMDGPU IP lifecycle, programs firmware and VCPU memory windows, initializes up to three encode rings, supports the SR-IOV MMSCH initialization path, emits VCE ring packets for IBs, VM flushes, fences, register waits/writes, and services VCE fence interrupts.

## Important APIs, Types, And Functions

The exported integration object is `vce_v4_0_ip_block`, backed by `vce_v4_0_ip_funcs`. Lifecycle entry points are `vce_v4_0_early_init()`, `sw_init()`, `sw_fini()`, `hw_init()`, `hw_fini()`, `suspend()`, and `resume()`. `vce_v4_0_start()` is the normal hardware boot path: it writes ring bases/sizes for rings 0, 1, and 2, calls `vce_v4_0_mc_resume()`, releases the ECPU reset, waits in `vce_v4_0_firmware_loaded()`, and clears the busy flag. `vce_v4_0_sriov_start()` builds an MMSCH v1.0 command table and `vce_v4_0_mmsch_start()` submits it through the VF mailbox.

Ring operations are collected in `vce_v4_0_ring_vm_funcs`. Pointer accessors select register sets by `ring->me` and use doorbells when configured. Packet emitters include `vce_v4_0_ring_emit_ib()`, `vce_v4_0_ring_emit_fence()`, `vce_v4_0_emit_vm_flush()`, `vce_v4_0_emit_reg_wait()`, `vce_v4_0_emit_wreg()`, and `vce_v4_0_ring_insert_end()`.

## Control Flow

Early init delegates common VCE setup to `amdgpu_vce_early_init()`, chooses one ring for SR-IOV or three rings for bare metal, and installs ring/IRQ functions. Software init registers the VCE interrupt, allocates the VCE firmware BO through common VCE code, handles PSP firmware metadata and saved BO allocation when applicable, initializes all rings, and allocates the virtualization MM table. Hardware init chooses the direct or SR-IOV start path, then runs `amdgpu_ring_test_helper()` on each active ring.

Suspend saves the VCPU BO for PSP-loaded firmware, cancels idle work, gates clocks/power or disables DPM, stops the block, and calls common VCE suspend. Resume restores the saved BO or reloads firmware, then reruns hardware init. Powergating state changes simply stop or start the block; clockgating is a no-op stub kept for unload compatibility.

## State And Persistence

State is held under `adev->vce`: firmware, `vcpu_bo`, `saved_bo`, `gpu_addr`, mapped CPU address, ring array, idle work, IRQ source, and the SR-IOV MM table in `adev->virt.mm_table`. PSP firmware mode persists a saved VCPU BO image across suspend/resume. Doorbell write pointers persist in ring writeback memory and are reset before MMSCH initialization.

## Dependencies And Integration Points

The file depends on AMDGPU VCE common helpers, SOC15 register accessors, VCE 4.0 register offsets/masks, MMHUB register metadata, MMSCH v1.0 table formats, PSP firmware loading, DPM/powergating hooks, doorbell writes, ring scheduling, VM hub TLB flush helpers, and IRQ/fence processing. It integrates with the AMD IP block table as `AMD_IP_BLOCK_TYPE_VCE` major 4.0 and with common VCE CS parsing/tests via the ring function table.

## Risks And Test Signals

Risks include firmware-load timeouts, incorrect cache-window offsets between PSP and non-PSP firmware loading, SR-IOV MMSCH table size or offset corruption, doorbell/write-pointer desynchronization, powergating races with delayed idle work, and interrupt source data outside the three-ring range. Good test signals are successful firmware boot, ring tests for all active rings, suspend/resume with PSP and non-PSP firmware, SR-IOV VF MMSCH startup, VM flush/fence completion, interrupt fence processing for rings 0 to 2, and timeout handling when the VCE status bit never reports firmware loaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v4_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v4_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v4_0.h

## Purpose

`vce_v4_0.h` is the public declaration header for the VCE 4.0 AMDGPU IP block implementation. It lets ASIC discovery or IP block assembly code reference the VCE 4.0 block descriptor without exposing the private register programming and ring helper functions from `vce_v4_0.c`.

## Important APIs, Types, And Functions

The single API is `extern const struct amdgpu_ip_block_version vce_v4_0_ip_block;`. The type is provided by AMDGPU core headers included by users of this header, not by this file.

## Control Flow

There is no executable control flow. Inclusion makes the VCE 4.0 IP block descriptor visible to compilation units that select hardware IP versions.

## State And Persistence

The header declares no state and owns no persistence. Runtime state is allocated and managed by the implementation through `adev->vce`.

## Dependencies And Integration Points

The header relies on a prior or transitive declaration of `struct amdgpu_ip_block_version`. Its integration point is the AMDGPU device/IP initialization layer, which can include this header to add VCE 4.0 to an ASIC's IP block list.

## Risks And Test Signals

Risk is limited to declaration drift: if the implementation changes the symbol name or removes the block, users of this header fail to link. Test signals are compile/link coverage for ASIC files that reference `vce_v4_0_ip_block`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v4_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_sw_ring.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_sw_ring.c

## Purpose

`vcn_sw_ring.c` implements a compact software-ring packet emitter set for VCN decode. Instead of programming generation-specific packet0 register sequences, it emits `VCN_DEC_SW_CMD_*` opcodes into an AMDGPU ring for firmware or a software command processor to interpret.

## Important APIs, Types, And Functions

The file exports six helpers declared in `vcn_sw_ring.h`: `vcn_dec_sw_ring_emit_fence()`, `vcn_dec_sw_ring_insert_end()`, `vcn_dec_sw_ring_emit_ib()`, `vcn_dec_sw_ring_emit_reg_wait()`, `vcn_dec_sw_ring_emit_vm_flush()`, and `vcn_dec_sw_ring_emit_wreg()`. They operate on `struct amdgpu_ring`, `struct amdgpu_job`, and `struct amdgpu_ib`. `vcn_dec_sw_ring_emit_vm_flush()` also uses `struct amdgpu_vmhub` and `amdgpu_gmc_emit_flush_gpu_tlb()`.

## Control Flow

Each helper appends a fixed packet sequence with `amdgpu_ring_write()`. Fence emission rejects 64-bit fence flags via `WARN_ON`, writes the fence address low/high dwords and sequence, then emits a trap. IB emission writes the job VMID and IB GPU address/length. VM flush asks GMC code to emit the TLB flush, then emits a register wait on the VM hub page-table base register to ensure the flush write is visible.

## State And Persistence

The file owns no durable state. It mutates only the ring write stream and indirectly depends on ring fields such as `adev`, `vm_hub`, and the caller-maintained write pointer.

## Dependencies And Integration Points

It depends on AMDGPU ring write helpers, job VMID extraction, IB metadata, VCN software command opcode definitions, and VM hub/GMC TLB flushing. It is intended to be plugged into an `amdgpu_ring_funcs` table by a VCN generation that uses the software-ring protocol.

## Risks And Test Signals

Risks include packet-size mismatches with `VCN_SW_RING_EMIT_FRAME_SIZE`, unsupported 64-bit fence flags, wrong register byte-address shifting, and VM flush waits aimed at the wrong hub register if `ring->vm_hub` is misconfigured. Test signals include ring parser acceptance of every opcode, fence interrupt completion, IB execution under nonzero VMIDs, VM flush correctness under address-space switches, and static checks that frame-size constants match emitted dwords.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_sw_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_sw_ring.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_sw_ring.h

## Purpose

`vcn_sw_ring.h` declares the VCN decode software-ring emitter interface and its expected frame size. It provides a small shared contract for generation-specific VCN code that wants to use the `VCN_DEC_SW_CMD_*` packet protocol.

## Important APIs, Types, And Functions

`VCN_SW_RING_EMIT_FRAME_SIZE` describes the frame overhead as VM flush, two VM fences, and an end packet. The header declares emitters for fences, IBs, register waits, VM flushes, register writes, and end packets. The function signatures expose AMDGPU ring, job, and IB types but leave their definitions to included AMDGPU headers.

## Control Flow

The header has no runtime control flow. It establishes the compile-time contract used by ring function tables and the implementation in `vcn_sw_ring.c`.

## State And Persistence

No state is stored here. The macro is a derived constant that must stay synchronized with the implementation's emitted dword counts.

## Dependencies And Integration Points

It integrates with AMDGPU VCN ring setup and depends on existing definitions of `struct amdgpu_ring`, `struct amdgpu_job`, `struct amdgpu_ib`, `u64`, and `uint32_t`. It is included by `vcn_sw_ring.c` and any generation file that installs these emitters into a ring function table.

## Risks And Test Signals

Risk is mainly contract drift: if `VCN_SW_RING_EMIT_FRAME_SIZE` no longer matches the actual emitter dword count, callers may under-allocate ring space. Test signals are compile coverage and runtime ring tests that exercise VM flush plus fences without ring overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_sw_ring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v1_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v1_0.c

## Purpose

`vcn_v1_0.c` implements the first AMD VCN IP generation. It manages one VCN instance with one decode ring, two encode rings, JPEG v1.0 integration, firmware/MC programming, static and dynamic power-gating modes, ring packet emission, secure-submission BO validation for Raven encrypted buffers, IRQ handling, and IP state dumping.

## Important APIs, Types, And Functions

The exported block is `vcn_v1_0_ip_block`, backed by `vcn_v1_0_ip_funcs`. Lifecycle functions initialize ring/IRQ tables, call common VCN firmware helpers, create decode/encode rings, integrate JPEG, allocate an IP dump buffer, test rings, and suspend/resume common VCN firmware state. `vcn_v1_0_start_spg_mode()` and `vcn_v1_0_start_dpg_mode()` are the central boot paths; `vcn_v1_0_stop_spg_mode()` and `vcn_v1_0_stop_dpg_mode()` are the stop paths. `vcn_v1_0_pause_dpg_mode()` pauses or unpauses non-JPEG and JPEG DPG domains and restores ring registers.

Decode ring helpers emit packet0 sequences to VCN internal registers: start/end, fences/traps, IB setup, register waits, VM flushes, register writes, and NOP padding. Encode helpers emit `VCN_ENC_CMD_*` packets. `vcn_v1_0_validate_bo()` and `vcn_v1_0_ring_patch_cs_in_place()` move encrypted VCN message BOs to VRAM on Raven secure submissions.

## Control Flow

Early init sets two encoder rings, installs the per-instance powergate callback, hooks ring/IRQ functions, calls JPEG early init, then common VCN early init. Software init registers decode and encode IRQs, resumes firmware, initializes rings and register offsets, hooks the DPG pause callback, optionally initializes firmware logging, initializes JPEG software, and allocates register dump storage. Hardware init runs tests for decode, both encoders, and JPEG.

The start path selects DPG when `AMD_PG_SUPPORT_VCN_DPG` is set. SPG disables static powergating, marks VCN busy, disables clock gating, programs cache windows and tiling registers, boots VCPU, waits for idle, enables interrupts, initializes RBC decode and encoder ring registers, and starts JPEG. DPG writes an SRAM-backed programming sequence, enables dynamic PG, programs cache/ring state, and starts JPEG in DPG mode. Idle work counts outstanding fences, updates DPG pause state, and gates VCN/JPEG when no work remains.

## State And Persistence

State is in `adev->vcn.inst[0]`: firmware BOs, `fw_shared`, decode and encode rings, register offset aliases, pause state, idle work, current PG state, IRQ source, and the JPEG coordination mutex. `adev->vcn.ip_dump` stores sampled registers for diagnostics. Ring write pointers are mirrored in hardware registers and scratch state for DPG restore.

## Dependencies And Integration Points

The file depends on common VCN firmware/session helpers, SOC15 register accessors, VCN 1.0 and MMHUB 9.1 registers, JPEG v1.0, AMDGPU PM/DPM, VM/GMC flush helpers, ring scheduler/fence helpers, DRM IRQ registration, and TTM BO validation. It integrates with the generic `vcn_set_powergating_state()` wrapper and common VCN/JPEG ring tests.

## Risks And Test Signals

Risks include DPG pause races with JPEG, incorrect ring restore after DPG pause, firmware boot timeout/reset loops, encrypted BO migration failures, IP dump reads while powered off, and mismatched packet dword counts in ring frame sizes. Test signals include decode/encode/JPEG ring tests, secure Raven submissions using encrypted GTT BOs, SPG and DPG suspend/resume, idle work gating under mixed JPEG/VCN workloads, interrupt routing for source IDs 124/119/120, and debug dump output for active and inactive instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v1_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v1_0.h

## Purpose

`vcn_v1_0.h` exposes the small part of the VCN 1.0 implementation needed by adjacent code: the IP block descriptor and two power-management helpers used around ring submissions.

## Important APIs, Types, And Functions

It declares `vcn_v1_0_ring_end_use()`, `vcn_v1_0_set_pg_for_begin_use()`, and `vcn_v1_0_ip_block`. The helper prototypes operate on `struct amdgpu_ring` and allow related code, especially JPEG v1.0 coordination, to share the VCN 1.0 begin/end-use powergating behavior.

## Control Flow

The header has no executable flow. It enables callers to invoke implementation functions that cancel/reschedule idle work, ungate/gate VCN, and update DPG pause state around submissions.

## State And Persistence

No state is declared here. The implementation manipulates `adev->vcn.inst[0]`, DPG pause state, delayed idle work, and the VCN/JPEG workaround mutex.

## Dependencies And Integration Points

Consumers need AMDGPU ring and IP block type declarations. The header integrates VCN 1.0 with the broader IP block registration path and with any companion block that needs VCN-aware power management.

## Risks And Test Signals

Risks are API drift and incorrect external use of begin/end-use helpers without matching locking expectations. Test signals are compile coverage for VCN/JPEG v1.0 builds and runtime checks that JPEG and VCN submissions do not leave the shared block permanently ungated or gated while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_0.c

## Purpose

`vcn_v2_0.c` implements VCN 2.0 for AMDGPU. It carries forward the decode/encode ring model while adding doorbell-based write pointers, internal register-offset aliases for KMD commands, firmware shared multi-queue state, SR-IOV MMSCH v2.0 startup, reset support, register dump/sysfs reset-mask integration, and DPG/indirect-SRAM boot support.

## Important APIs, Types, And Functions

The main export is `vcn_v2_0_ip_block`. Lifecycle hooks in `vcn_v2_0_ip_funcs` call `vcn_v2_0_early_init()`, `sw_init()`, `hw_init()`, suspend/resume, idle checks, and clock/power state handlers. `vcn_v2_0_start()` handles the normal direct boot path, while `vcn_v2_0_start_dpg_mode()` handles DPG and optional PSP SRAM update. `vcn_v2_0_start_sriov()` builds an MMSCH v2.0 table for VF operation and `vcn_v2_0_start_mmsch()` submits it.

Several ring helpers are exported through `vcn_v2_0.h` for reuse by later generations: decode start/end/NOP, decode fence/IB/reg-wait/VM-flush/wreg, encode fence/IB/reg-wait/VM-flush/wreg/end, and `vcn_v2_0_dec_ring_test_ring()`. Ring function tables install these helpers plus `amdgpu_vcn_ring_begin_use()`, `amdgpu_vcn_ring_end_use()`, and `amdgpu_vcn_ring_reset()`.

## Control Flow

Early init chooses one encoder ring for SR-IOV VFs and two otherwise. Software init registers decode and encode interrupts, initializes common VCN firmware, enables doorbells, sets per-ring VM hubs, fills internal/external register offsets, assigns reset callbacks, allocates the virtualization MM table, sets `AMDGPU_VCN_MULTI_QUEUE_FLAG` in firmware shared memory, initializes fwlog/register dump/reset-mask sysfs, and marks supported reset types.

Hardware init enables the VCN doorbell range, starts the SR-IOV MMSCH path for VFs, tests decode, disables VF decode scheduling, and tests encoder rings. Normal start powers up VCN through DPM, configures clock/power gating, programs firmware/stack/context/non-cache windows, boots VCPU, resets decode and encode queue state through `fw_shared->multi_queue`, and initializes ring registers. DPG start writes similar state through DPG-mode accessors and can push an indirect SRAM image through PSP.

## State And Persistence

Persistent runtime state includes `adev->vcn.inst[0]` firmware, `fw_shared`, rings, internal/external register aliases, reset callbacks, DPG SRAM pointer, pause state, supported reset mask, virtualization MM table, and sysfs reset-mask state. Doorbell writeback memory persists ring write pointers. `fw_shared->multi_queue.*_queue_mode` is used to coordinate queue resets with firmware.

## Dependencies And Integration Points

Dependencies include common VCN helpers, PSP SRAM update, MMSCH v2.0 definitions, SOC15/VCN 2.0 registers, IRQ source IDs, DPM, NBIO doorbell ranges, VM/GMC TLB flushing, ring scheduling, register dump helpers, and sysfs reset-mask support. It integrates with later VCN generations by exporting reusable ring emitters.

## Risks And Test Signals

Risks include doorbell index mistakes, SR-IOV decode scheduling assumptions, stale multi-queue reset flags, indirect SRAM load failures, DPG pause restoring rings with wrong write pointers, MMSCH table corruption, and generation-specific internal register offsets diverging from firmware expectations. Test signals are decode/encode ring tests, doorbell writeback checks, SR-IOV VF startup with encode-only scheduling, DPG direct and indirect modes, reset-mask sysfs behavior, per-queue reset, interrupt routing for decode/general/low-latency encode, and firmware shared queue-state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_0.h

## Purpose

`vcn_v2_0.h` exports VCN 2.0 ring packet helpers and the VCN 2.0 IP block descriptor. Later generation files reuse these helpers when their ring command protocol is compatible but their lifecycle, multi-instance, or RAS handling differs.

## Important APIs, Types, And Functions

The header declares decode helpers for start, end, NOP, fence, IB, register wait, VM flush, register write, and ring test. It also declares encode helpers for end, fence, IB, register wait, VM flush, and register write. The descriptor `vcn_v2_0_ip_block` exposes the complete VCN 2.0 IP implementation.

## Control Flow

There is no executable flow in the header. It defines the callable surface used by `vcn_v2_0.c` ring tables and by generation variants such as VCN 2.5 that reuse VCN 2.0 packet emitters.

## State And Persistence

No state is owned here. The declared functions operate on `struct amdgpu_ring`, `struct amdgpu_job`, and `struct amdgpu_ib`, updating ring command streams and hardware-visible write pointers in their implementation.

## Dependencies And Integration Points

Consumers need AMDGPU ring/job/IB type definitions and integer types. The header is an integration point between VCN generation implementations, common AMDGPU ring scheduling, and the ASIC IP block registry.

## Risks And Test Signals

Risk centers on ABI-like drift between the declarations and the implementation or unsafe reuse by a generation whose internal register offsets do not match the v2.0 helper assumptions. Test signals are compile/link coverage for v2.0 and v2.5 users plus runtime ring tests for every helper reused through a ring function table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_5.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_5.c

## Purpose

`vcn_v2_5.c` implements VCN 2.5 and VCN 2.6. It adapts the VCN 2.x design for up to two hardware instances, harvested-instance detection, per-instance doorbells and VM hubs, SR-IOV two-instance MMSCH setup, shared idle/power accounting, reuse of VCN 2.0 ring packet helpers, and VCN 2.6 RAS poison interrupt/status handling.

## Important APIs, Types, And Functions

The file exports `vcn_v2_5_ip_block`, `vcn_v2_6_ip_block`, and `vcn_v2_6_ras_hw_ops`. Lifecycle hooks are shared between 2.5 and 2.6 through `vcn_v2_5_ip_funcs` and `vcn_v2_6_ip_funcs`. `vcn_v2_5_early_init()` detects harvested instances or configures SR-IOV instances, sets ring/IRQ/RAS functions, and runs common VCN early init per instance. `vcn_v2_5_sw_init()` initializes each non-harvested instance, registers decode/encode/RAS IRQs, sets internal register aliases, configures doorbells and VM hubs, initializes rings, firmware shared flags, reset callbacks, RAS, register dump, and reset-mask sysfs.

Start/stop logic is in `vcn_v2_5_start()`, `vcn_v2_5_start_dpg_mode()`, `vcn_v2_5_stop()`, and `vcn_v2_5_stop_dpg_mode()`. `vcn_v2_5_sriov_start()` builds per-engine MMSCH v1.1 tables and `vcn_v2_5_mmsch_start()` submits them. Ring functions use VCN 2.5 pointer accessors but reuse VCN 2.0 emitters for packet content.

## Control Flow

Hardware init either starts SR-IOV and marks VF schedulers or, for bare metal, enables each instance's doorbell range and tests decode plus encoder rings. Normal start skips harvested instances, enables DPM per instance, configures anti-hang/power/clock state, programs VCPU memory windows and tiling, boots VCPU with retry loops, initializes decode and two encode rings under firmware shared queue-reset flags, and reads back status. DPG start writes the same state through DPG-mode accessors, supports indirect SRAM, enables VCN 2.6 RAS registers when applicable, and resets decode queue state.

Idle work aggregates fences across all non-harvested instances and gates the whole VCN block only when all fences and total submissions are gone. Begin/end-use increments/decrements atomic submission counters, ungates the block, updates DPG pause for encoder submissions when firmware is not handling unified queues, and manages the VCN performance profile.

## State And Persistence

State is per `adev->vcn.inst[i]`: firmware, shared firmware page, decode and encode rings, register aliases, pause state, reset callback, RAS poison IRQ, DPG SRAM, atomic DPG encoder submission count, and ring `me` instance IDs. Shared state includes `adev->vcn.num_vcn_inst`, `harvest_config`, `supported_reset`, `ras`, and `inst[0].total_submission_cnt`. Firmware shared queue mode flags persist queue-reset coordination.

## Dependencies And Integration Points

Dependencies include common VCN firmware/ring/RAS helpers, VCN 2.0 ring emitters, SOC15 VCN 2.5 registers, MMSCH v1.0/v1.1 structures, IRQ client IDs for VCN0/VCN1, DPM, NBIO doorbell ranges, PSP SRAM update, register dump/sysfs reset mask helpers, and AMDGPU RAS late init. It integrates with the RAS framework by setting `adev->vcn.ras` for IP 2.6 and processing poison IRQs through `amdgpu_vcn_process_poison_irq`.

## Risks And Test Signals

Risks include harvested-instance masking errors, using `inst[i]` state after skip, doorbell index collisions across instances, VM hub mismatch on IP 2.5, SR-IOV table size/offset mistakes, shared idle gating while another instance still has submissions, DPG pause races with atomic counters, VCN 2.6 RAS enablement on non-2.6 parts, and a suspicious fwlog init reference to `inst[i]` after an inner loop where `i` may equal `num_enc_rings`. Test signals include one- and two-instance boot, harvested-instance disable path returning `-ENOENT` when both are disabled, per-instance ring tests, SR-IOV scheduler readiness, DPG direct/indirect paths, reset-mask sysfs, RAS poison IRQ/status tests on IP 2.6, suspend/resume across all instances, and idle gating under concurrent decode/encode load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_5.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_5.h

## Purpose

`vcn_v2_5.h` declares the VCN 2.5 and VCN 2.6 IP block descriptors and the VCN 2.6 RAS sub-block enumeration used by poison-status handling.

## Important APIs, Types, And Functions

`enum amdgpu_vcn_v2_6_sub_block` currently defines `AMDGPU_VCN_V2_6_VCPU_VCODEC` and `AMDGPU_VCN_V2_6_MAX_SUB_BLOCK`. The exported descriptors are `vcn_v2_5_ip_block` and `vcn_v2_6_ip_block`.

## Control Flow

The header has no executable flow. It makes the IP descriptors and RAS sub-block identifiers available to ASIC/IP selection and RAS code.

## State And Persistence

No state is stored here. Runtime VCN 2.5/2.6 state lives in `adev->vcn` and per-instance structures in the implementation.

## Dependencies And Integration Points

Consumers require `struct amdgpu_ip_block_version`. The enum is coupled to `vcn_v2_6_query_poison_by_instance()` in the implementation, which iterates from zero to `AMDGPU_VCN_V2_6_MAX_SUB_BLOCK`.

## Risks And Test Signals

Risk is mainly enum/implementation drift: adding sub-blocks requires updating poison status reads and tests. Test signals are compile/link coverage for ASIC files referencing the 2.5/2.6 block descriptors and RAS tests that iterate the enum range without missing supported poison sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_5.h -->
