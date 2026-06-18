# subset-b-001311 research

Grouped research for AMDGPU/KFD bridge files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu`. Each section preserves the source path and is wrapped for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_aldebaran.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_aldebaran.c

Purpose: this file specializes the KFD-to-KGD callback table for Aldebaran, a GFX9.4.2 family device. It mostly reuses the generic GFX9 queue, VM, interrupt, CU occupancy, trap handler, and SDMA helpers, but overrides debug trap programming and address watchpoint setup where Aldebaran's `SPI_GDBG_PER_VMID_CNTL` and `TCP_WATCH` register semantics differ from earlier GFX9 code.

Important APIs and functions: `kgd_aldebaran_enable_debug_trap` returns a per-VMID debug-control value with `TRAP_EN=1`, `EXCP_EN=0`, and `EXCP_REPLACE=0`. The local disable callback returns the same control shape but lets `keep_trap_enabled` decide `TRAP_EN`. `kgd_aldebaran_validate_trap_override_request` filters the supported KFD trap mask down to FP exceptions, integer divide-by-zero, address watch, and memory violation, and accepts only OR or REPLACE override modes. `kgd_aldebaran_set_wave_launch_trap_override` merges requested mask bits with the previous mask and returns an updated `SPI_GDBG_PER_VMID_CNTL` value. `kgd_aldebaran_set_wave_launch_mode` returns a register value with `LAUNCH_MODE` set. `kgd_gfx_aldebaran_set_address_watch` writes high and low watch addresses through RLC-safe GC register writes and returns a valid `TCP_WATCH0_CNTL` value.

Control flow: the exported `aldebaran_kfd2kgd` table wires generic GFX9 callbacks for shared memory, PASID/VMID mapping, interrupt initialization, compute HQD load/dump/destroy, HIQ load, wave control, VM page table base, CU occupancy, trap handler settings, IQ wait programming, and HQD reset/PQ-address helpers. SDMA callbacks come from Arcturus, reflecting compatible multi-SDMA queue register handling. Debug setup is split: KFD receives register values from the Aldebaran callbacks and applies them through the higher-level debug path rather than this file directly programming every debug register.

State and persistence: the file does not own durable state. It changes hardware state through MMIO writes for TCP watch addresses, and its callbacks compute register values for KFD to persist into per-VMID debug control. Watchpoint state persists in GC registers until cleared by the GFX9 clear callback. Queue and VM state persistence is delegated to the generic GFX9 and Arcturus helpers.

Dependencies and integration: includes `amdgpu_amdkfd_arcturus.h`, `amdgpu_amdkfd_gfx_v9.h`, Aldebaran GC 9.4.2 register headers, and KFD UAPI trap mask definitions. The integration point is `const struct kfd2kgd_calls aldebaran_kfd2kgd`, selected by AMDGPU/KFD device setup code for this ASIC.

Risks: trap mask validation must match hardware bit layout; unsupported trap bits are silently removed from the supported mask and invalid override modes return `-EPERM`. Address watch uses `watch_address_mask >> 6`, unlike several later files that shift by 7, so cross-generation copy/paste is risky. Watch address writes use instance 0 and RLC writes, so multi-XCC assumptions should be reviewed when changing this code. Test signals include debugger trap enable/disable, OR/REPLACE trap override behavior, KFD address watch hits, and SDMA queue lifecycle tests through the Arcturus callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_aldebaran.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_aldebaran.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_aldebaran.h

Purpose: this header exposes the small subset of Aldebaran debug helpers that other KFD/KGD bridge files reuse. It intentionally declares only `kgd_aldebaran_enable_debug_trap` and `kgd_aldebaran_set_wave_launch_mode`, leaving Aldebaran-specific disable, trap-override, and address-watch helpers private to the implementation file.

Important APIs: `kgd_aldebaran_enable_debug_trap(struct amdgpu_device *adev, bool restore_dbg_registers, uint32_t vmid)` returns a `SPI_GDBG_PER_VMID_CNTL` bitfield for enabling trap handling. `kgd_aldebaran_set_wave_launch_mode(struct amdgpu_device *adev, uint8_t wave_launch_mode, uint32_t vmid)` returns a bitfield with Aldebaran's launch mode encoded. Both APIs match the `kfd2kgd_calls` debug callback signatures, which makes them reusable by other GFX9.4.x tables.

Control flow and integration: `amdgpu_amdkfd_gc_9_4_3.c` includes this header and uses these two helpers in its `gc_9_4_3_kfd2kgd` table. `amdgpu_amdkfd_aldebaran.c` provides the definitions and also uses them in `aldebaran_kfd2kgd`. The header relies on declarations for `struct amdgpu_device`, `bool`, and fixed-width integer types being available through including translation units; it does not include those dependencies itself.

State and persistence: the header declares pure register-value helper APIs and owns no state. Persistent behavior is in the callers that write returned values into debug registers or save them in KFD debug bookkeeping.

Dependencies: this header is part of the AMDGPU driver private interface, not UAPI. It depends on the implementation file and on the broader KFD/KGD callback contract defined around `struct kfd2kgd_calls`.

Risks and test signals: because there is no include guard in the excerpted file, repeated inclusion is benign only because it contains declarations, but adding definitions or data here would be risky. Signature drift would break both Aldebaran and GC 9.4.3 tables at compile time. Tests are compile/link coverage plus debugger bring-up paths that exercise the shared enable and launch-mode callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_aldebaran.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.c

Purpose: this file provides Arcturus-specific KFD/KGD support. It reuses GFX9 compute queue and VM helpers, implements Arcturus SDMA queue load/dump/occupancy/destroy across up to eight SDMA engines, and customizes debug trap enable/disable to adjust barrier wait-count behavior safely around compute scheduler suspension.

Important APIs and functions: `kgd_arcturus_hqd_sdma_load` programs an SDMA RLC queue from a `v9_sdma_mqd`, disables `RB_ENABLE`, waits up to two seconds for `CONTEXT_STATUS.IDLE`, sets doorbell, read/write pointers, ring base, RPTR writeback address, and re-enables the ring. `kgd_arcturus_hqd_sdma_dump` allocates a register dump covering RB, status, CSA, IB, pointer-update, and mid-command registers. `kgd_arcturus_hqd_sdma_is_occupied` checks `RB_ENABLE`. `kgd_arcturus_hqd_sdma_destroy` disables the ring, waits for idle using the caller's timeout, clears the doorbell, re-enables RB control, and saves RPTR back into the MQD. `set_barrier_auto_waitcnt` toggles `adev->barrier_has_auto_waitcnt` and `SQ_CONFIG.DISABLE_BARRIER_WAITCNT` while KFD and compute schedulers are suspended. The exported `arcturus_kfd2kgd` table binds these SDMA and debug functions to KFD.

Control flow: SDMA queue load and destroy are hardware-state machines driven by RB enable and idle bits. Debug enable locks `grbm_idx_mutex`, stalls wave launch through GFX9, enables automatic barrier waitcnt by suspending KFD and compute schedulers, clears `SPI_GDBG_TRAP_MASK`, then unstalls. Disable reverses the barrier setting and clears the mask. `suspend_resume_compute_scheduler` iterates ready compute rings, stops schedulers, waits for empty fences, and waits for GFX idle before register modification.

State and persistence: queue state persists in SDMA registers and is partially copied back into MQDs on destroy. Barrier behavior persists in `adev->barrier_has_auto_waitcnt` and `SQ_CONFIG`. Debug trap state persists in SPI trap registers. The function takes `reset_domain->sem` read lock opportunistically; if lock acquisition fails, software state may be updated while hardware programming is skipped.

Dependencies and integration: depends on SDMA 4.2.2 register headers for engines 0-7, GFX9 shared helpers, reset-domain locking, KFD suspend/resume, DRM scheduler control, and AMDGPU ring/fence primitives. The table is selected for Arcturus devices and also supplies SDMA callbacks reused by Aldebaran.

Risks: invalid SDMA engine ids fall back to engine 0 after warning, which prevents crashes but can hide caller bugs. Scheduler suspension around barrier programming is delicate; failures while draining rings skip hardware writes but still resume. SDMA idle waits can return `-ETIME`; callers must handle failed queue eviction or restore. Test signals include SDMA queue load/destroy with all engine ids, timeout injection around idle bits, debug trap enable/disable with active compute queues, and validation that scheduler stop/start is balanced on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.h

Purpose: this header declares the Arcturus SDMA HQD operations that are shared outside `amdgpu_amdkfd_arcturus.c`, most notably by the Aldebaran KFD/KGD callback table.

Important APIs: `kgd_arcturus_hqd_sdma_load` loads an SDMA MQD and optionally seeds the write pointer from userspace memory. `kgd_arcturus_hqd_sdma_dump` returns an allocated register/value array for one SDMA engine queue. `kgd_arcturus_hqd_sdma_is_occupied` reports whether the MQD's SDMA RLC queue is enabled in hardware. `kgd_arcturus_hqd_sdma_destroy` disables an SDMA queue, waits for idle, clears doorbell state, and saves the read pointer.

Control flow and integration: the declarations are consumed by `amdgpu_amdkfd_aldebaran.c` and by Arcturus's own callback table. They match the SDMA slots in `struct kfd2kgd_calls`, allowing KFD queue-management code to call through the table without knowing the ASIC-specific register layout.

State and persistence: no state is stored in the header. The declared functions mutate SDMA RLC registers and MQD read-pointer fields in their implementation.

Dependencies: the file assumes `struct amdgpu_device`, `struct mm_struct`, `bool`, `uint32_t`, and `__user` annotations are already visible through the including source. It is a private driver header, not a user ABI.

Risks and test signals: signature mismatches surface as compile failures in Aldebaran/Arcturus builds. Because no include guard is present in the shown file, keeping the header limited to declarations avoids duplicate-definition issues. Tests should cover both direct Arcturus callback-table use and Aldebaran reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_fence.c

Purpose: this file implements KFD eviction fences on top of Linux `dma_fence`. These fences prevent TTM from moving KFD-owned BOs until user-mode queues for the owning process, or an SVM BO range, are evicted/quiesced. It bridges memory pressure and GPU scheduler fence signaling to KFD process eviction/restore work.

Important APIs and functions: `amdgpu_amdkfd_fence_create` allocates `struct amdgpu_amdkfd_fence`, grabs an `mm_struct` reference with `mmgrab`, stores the optional `svm_range_bo`, context id, and task command as the timeline name, initializes a spinlock, and calls `dma_fence_init` with a monotonically increasing atomic sequence. `to_amdgpu_amdkfd_fence` validates that a generic fence uses `amdkfd_fence_ops`. `amdkfd_fence_enable_signaling` is the key scheduler callback: if the fence is unsignaled, it schedules either `kgd2kfd_schedule_evict_and_restore_process` for process eviction fences or `svm_range_schedule_evict_svm_bo` for SVM BO fences. `amdkfd_fence_release` drops the mm reference and frees through RCU. `amdkfd_fence_check_mm` prevents TTM from evicting BOs belonging to the same process, except SVM BO fences where overcommitment is allowed.

Control flow: TTM and the GPU scheduler encounter this fence while moving BOs. `enable_signaling` returns true when the fence is already signaled or scheduling indicates the eviction path is already complete; otherwise it returns false after queuing async eviction/restore work. Release occurs when the final fence reference is dropped.

State and persistence: fence state is held in `dma_fence` core fields, `fence_seq`, the referenced `mm`, optional `svm_bo`, and `context_id`. The mm reference persists until `release`. The fence name is copied from the current task at creation. There is no disk persistence.

Dependencies and integration: depends on Linux DMA fence, spinlock, RCU freeing, `mmgrab/mmdrop`, KFD process eviction, and SVM range eviction. It integrates with AMDGPU BO movement through the fence attached to KFD BO reservations and with TTM's eviction-value checks through `amdkfd_fence_check_mm`.

Risks: `enable_signaling` runs in scheduler/fence contexts, so it must not block on long GPU work itself; it only schedules work. Failure to signal after eviction would block BO moves. Incorrect `mm` matching could either deadlock self-eviction or allow moving BOs still referenced by active queues. Test signals include memory-pressure eviction of KFD BOs, process teardown with outstanding fences, SVM overcommit eviction, repeated fence release under RCU, and negative tests for non-AMDKFD fences passed to `to_amdgpu_amdkfd_fence`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c

Purpose: this file adapts the GFX9 KFD/KGD bridge to GC 9.4.3 multi-XCC hardware. It reuses many GFX9 and Aldebaran helpers but overrides SDMA register addressing, PASID/VMID mapping, compute HQD load, debug trap-mask mapping, address watch programming, and SDMA doorbell discovery for the 9.4.3 register model.

Important APIs and functions: `kgd_gfx_v9_4_3_hqd_sdma_load/dump/is_occupied/destroy` operate on `v9_sdma_mqd` and use `GET_INST(SDMA0, engine_id)` with the 4.4.2 SDMA register names. `kgd_gfx_v9_4_3_set_pasid_vmid_mapping` programs ATHUB mapping, waits up to 10 ms for update status, clears it, then programs IH LUT entries for both XCC and AID indices. `kgd_gfx_v9_4_3_hqd_load` writes MQD/HQD registers for a selected XCC and uses CP write-pointer polling rather than direct user pointer reads. Trap helpers map KFD software masks to `SPI_GDBG_PER_VMID_CNTL` fields, including wave-start and wave-end trap bits. Address watch writes TCP watch address registers per XCC and returns the control value. `kgd_gfx_v9_4_3_hqd_sdma_get_doorbell` reports the doorbell offset for active SDMA queues.

Control flow: queue load acquires the target pipe/queue through GFX9's SRBM helper, writes HQD registers from the MQD, enables doorbell logic, optionally seeds CP polling with a guessed 64-bit WPTR, initializes the EOP fetcher, and marks HQD active. SDMA load follows disable-wait-program-enable ordering. Destroy disables SDMA RB enable, waits for idle, clears doorbell, re-enables RB control, and saves RPTR. The callback table combines these local routines with generic GFX9 dump/destroy/CU/VM functions and Aldebaran debug enable/launch-mode helpers.

State and persistence: persistent state is hardware register state in GC, ATHUB, OSSSYS, and SDMA blocks plus saved MQD RPTR fields. PASID mappings persist until overwritten or cleared. Debug trap settings are encoded in per-VMID control values returned to the caller.

Dependencies and integration: includes GC 9.4.3, ATHUB 1.8.0, OSSSYS 4.4.2, SDMA 4.4.2, GFX9 shared headers, and Aldebaran debug declarations. The table `gc_9_4_3_kfd2kgd` is the main integration point.

Risks: multi-XCC/AID IH LUT indexing is subtle and easy to regress. Queue load assumes queue wrap did not invalidate the guessed WPTR. SDMA timeout failures return `-ETIME`. `clear_address_watch` is a no-op returning 0, so the broader debug path must clear via returned controls or future hardware support. Test signals include PASID mapping on both XCCs of an AID, SDMA queue lifecycle on each instance, debugger trap masks including wave-start/end, watchpoint hits, and doorbell reporting only when `CONTEXT_STATUS.SELECTED` is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c

Purpose: this is the base GFX10 KFD/KGD implementation. It provides callback-table support for shared memory setup, VMID/PASID mapping, interrupt setup, compute HQD load/dump/destroy, HIQ mapping through KIQ, SDMA queue load/dump/destroy, wave control, debug trap and wave-launch control, address watchpoints, IQ wait programming, and trap handler address programming.

Important APIs: private callbacks include `kgd_program_sh_mem_settings`, `kgd_set_pasid_vmid_mapping`, `kgd_init_interrupts`, `kgd_hqd_load`, `kgd_hiq_mqd_load`, `kgd_hqd_dump`, SDMA load/dump/occupancy/destroy helpers, `kgd_hqd_destroy`, `get_atc_vmid_pasid_mapping_info`, `kgd_wave_control_execute`, and `set_vm_context_page_table_base`. Public helpers declared in the header include `kgd_gfx_v10_enable_debug_trap`, `kgd_gfx_v10_disable_debug_trap`, trap override validation/programming, `kgd_gfx_v10_set_wave_launch_mode`, address-watch helpers, IQ wait helpers, and placeholder HQD reset/PQ/SDMA-doorbell helpers.

Control flow: compute queue load locks SRBM selection, writes HQD registers from `v10_compute_mqd`, enables doorbell logic, optionally configures CP one-shot WPTR polling with a guessed 64-bit write pointer, starts the EOP fetcher, and marks the HQD active. HIQ load emits a `PACKET3_MAP_QUEUES` packet on the KIQ ring under ring lock. HQD destroy maps KFD preempt types to CP dequeue requests, clears scheduler1 for HIQ VMID 0, and polls `CP_HQD_ACTIVE` until inactive or timeout. SDMA queue load/destroy follows the recurring disable-wait-program-enable pattern. Debug trap programming stalls wave launch, clears or updates global `SPI_GDBG_TRAP_MASK`, then restores launch state. Address watch writes both TCP and SQ watch registers, disables the slot before programming address registers, and re-enables it.

State and persistence: hardware state includes SRBM-selected HQD registers, SDMA queue registers, ATHUB/IH mappings, GFXHUB VM PT registers, SPI debug registers, TCP/SQ watch registers, and KIQ ring submissions. MQD RPTR state is updated on SDMA destroy. Placeholders return 0 for PQ address, HQD reset, and SDMA doorbell, signaling unsupported or unimplemented introspection for this generation.

Dependencies and integration: depends on GC 10.1.0, ATHUB 2.0.0, OSSSYS 5.0.0, `v10_structs`, `nv/nvd` GRBM selection, KFD UAPI trap masks, AMDGPU ring/KIQ, and GFXHUB functions. The exported `gfx_v10_kfd2kgd` table is consumed by KFD device setup.

Risks: GFX10 trap mask is global, so validation allows only OR-ing address-watch bits to avoid affecting other processes. WPTR guessing assumes no overflow beyond queue size. Direct register programming requires SRBM locks to be balanced. Test signals include compute and SDMA queue lifecycle, HIQ map-packet submission, PASID mapping visibility in IH/ATHUB, address-watch hit/clear behavior, and debugger paths with `restore_dbg_registers` true and false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.h

Purpose: this header exposes GFX10 debug, address-watch, IQ wait, and limited HQD introspection helpers for reuse by GFX10.3 and other closely related implementations.

Important APIs: declarations cover debug trap enable/disable, trap override validation and programming, wave launch mode, TCP/SQ address watch setup and clear, IQ wait-time read and dequeue wait-count packet construction, and placeholder-style `hqd_get_pq_addr`, `hqd_reset`, and `hqd_sdma_get_doorbell` helpers. The signatures mirror `struct kfd2kgd_calls` callback slots.

Control flow and integration: `amdgpu_amdkfd_gfx_v10_3.c` includes this header and reuses the debug/address/IQ/HQD helper functions in its `gfx_v10_3_kfd2kgd` table while overriding queue load, PASID mapping, and SDMA register offsets. The base GFX10 file provides the definitions.

State and persistence: the header stores no state. Its declared functions manipulate SPI debug state, watchpoint registers, IQ wait registers, or report unsupported HQD values in the implementation.

Dependencies: consumers need AMDGPU core types, KFD preemption/debug UAPI types, and fixed-width integer types available before inclusion. This is a private driver header rather than UAPI.

Risks and test signals: since the header is a sharing boundary between base GFX10 and GFX10.3, changes can silently affect both tables. Compile coverage catches signature drift; runtime tests should include GFX10.3 debug trap and watchpoint flows to ensure shared helpers still match that hardware's register behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c

Purpose: this file adapts the GFX10 KFD/KGD bridge for GFX10.3 ASICs. It reuses base GFX10 debug/watch/IQ helpers but supplies generation-specific queue programming, PASID-to-IH mapping for devices where ATC is defeatured, SDMA register offsets for up to four engines, and trap handler setup.

Important APIs and functions: `program_sh_mem_settings_v10_3`, `set_pasid_vmid_mapping_v10_3`, `init_interrupts_v10_3`, `hqd_load_v10_3`, `hiq_mqd_load_v10_3`, `hqd_dump_v10_3`, `hqd_sdma_load_v10_3`, `hqd_sdma_dump_v10_3`, `hqd_is_occupied_v10_3`, `hqd_sdma_is_occupied_v10_3`, `hqd_destroy_v10_3`, `hqd_sdma_destroy_v10_3`, `wave_control_execute_v10_3`, `get_atc_vmid_pasid_mapping_info_v10_3`, `set_vm_context_page_table_base_v10_3`, and `program_trap_handler_settings_v10_3` are bound into `gfx_v10_3_kfd2kgd`.

Control flow: compute load mirrors base GFX10 but also programs `RLC_CP_SCHEDULERS.scheduler1` for HIQ queues with VMID 0. HIQ load submits `PACKET3_MAP_QUEUES` through KIQ. PASID mapping writes only `IH_VMID_0_LUT` because the comment states ATC is defeatured on Sienna Cichlid. SDMA load/destroy use GFX10 register names with engine base selected by a switch over engines 0-3. Queue destroy maps KFD drain/reset/save requests to CP dequeue request values and polls `CP_HQD_ACTIVE`. Trap handler setup writes TBA/TMA registers with `TRAP_EN` set in `SQ_SHADER_TBA_HI`.

State and persistence: persistent state is in SRBM-selected HQD registers, SDMA queue registers, IH LUT, GFXHUB VM PT registers, shader trap handler registers, and KIQ ring packets. SDMA destroy copies RPTR back into the MQD. Debug and address-watch state is delegated to shared GFX10 helpers.

Dependencies and integration: includes GFX10.3 GC, OSSSYS 5.0.0, ATHUB 2.1.0, `v10_structs`, `nv/nvd`, and `amdgpu_amdkfd_gfx_v10.h`. The callback table is the integration boundary with KFD.

Risks: the ATC-defeatured mapping means code expecting `get_atc_vmid_pasid_mapping_info_v10_3` to observe mappings can see stale or absent ATHUB state. Invalid SDMA engine ids fall through to engine 0 after warning. Queue WPTR guessing has the same wrap assumption as GFX9/10. Test signals include IH-only PASID mapping, HIQ scheduler1 setup/clear, KIQ map queue packet emission, SDMA queue lifecycle on engines 0-3, and shared GFX10 debugger/watchpoint behavior on GFX10.3 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c

Purpose: this file implements the GFX11 KFD/KGD callback table. It updates the GFX10-style queue, SDMA, VM, wave-control, and debug routines for SOC21 register selection and GFX11 register names.

Important APIs and functions: callback implementations include `program_sh_mem_settings_v11`, `set_pasid_vmid_mapping_v11`, `init_interrupts_v11`, `hqd_load_v11`, `hiq_mqd_load_v11`, `hqd_dump_v11`, `hqd_sdma_load_v11`, `hqd_sdma_dump_v11`, occupancy checks, destroy paths, `wave_control_execute_v11`, `set_vm_context_page_table_base_v11`, GFX11 debug trap helpers, trap mask mapping, address-watch setup/clear, and placeholder HQD PQ/reset/doorbell helpers.

Control flow: SRBM selection uses `soc21_grbm_select`. Compute queue load writes `v11_compute_mqd` HQD fields, handles HIQ scheduler1 programming for VMID 0, enables doorbell logic, seeds CP WPTR polling when a user pointer is supplied, starts the EOP fetcher, and marks the queue active. HIQ mapping uses KIQ `PACKET3_MAP_QUEUES`. SDMA queue load/destroy use renamed `SDMA0_QUEUE0_*` registers and two-engine offset selection; invalid engine ids call `BUG()`. Debug trap callbacks return per-VMID control values instead of globally writing `SPI_GDBG_TRAP_MASK`. Trap validation supports FP, integer divide-by-zero, address watch, memory violation, and conditionally wave-start/end trap bits for GC IP >= 11.0.4. Address watch writes TCP watch address registers through RLC writes and returns a valid control value.

State and persistence: state persists in HQD/SDMA registers, IH LUT, GFXHUB page-table registers, SPI per-VMID debug controls, TCP watch registers, and MQD RPTR fields saved on SDMA destroy. The callback table sets `get_atc_vmid_pasid_mapping_info = NULL`, indicating no ATHUB query path here.

Dependencies and integration: depends on GC 11.0.0, OSSSYS 6.0.0, SOC21 GRBM selection, `v11_structs`, KFD UAPI debug masks, KIQ ring infrastructure, and GFXHUB VM functions. Integration is `const struct kfd2kgd_calls gfx_v11_kfd2kgd`.

Risks: `BUG()` on invalid SDMA engine ids is harsher than older warning/fallback behavior. `KFD_PREEMPT_TYPE_WAVEFRONT_SAVE` is not handled in destroy and falls back to drain through default behavior. Address-watch clear returns 0 without writing a clear register. Tests should cover SDMA engine validation, GC 11.0.4+ wave start/end trap support, KIQ HIQ load, compute queue preemption timeouts, and VMID rejection in page-table programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12.c

Purpose: this file provides a narrower GFX12 KFD/KGD callback table for SOC24-era devices. It implements interrupt setup, HQD and SDMA register dumps, wave-control execution, per-VMID debug control value generation, trap-mask conversion, address-watch programming, and an SDMA doorbell placeholder.

Important APIs and functions: `init_interrupts_v12` enables timestamp and opcode-error interrupts for a selected MEC pipe. `hqd_dump_v12` dumps 56 compute HQD registers after SRBM queue selection. `hqd_sdma_dump_v12` dumps a compact SDMA queue range from `RB_CNTL` through `CONTEXT_STATUS`. `wave_control_execute_v12` writes `GRBM_GFX_INDEX` and `SQ_CMD` and restores broadcast selection. Debug callbacks return `SPI_GDBG_PER_VMID_CNTL` values with trap enable, exception mask, replacement mode, optional trap-on-start/end bits, and either launch mode or stall mode. `kgd_gfx_v12_set_address_watch` writes TCP watch address high/low registers and returns a valid control value.

Control flow: queue-specific register access is protected by `srbm_mutex` and selected with `soc24_grbm_select`. Dump helpers allocate output arrays, select the queue, read sequential registers, and release the queue. Debug trap override first maps previous hardware control to KFD mask bits, merges requested bits, maps back to hardware fields, and returns the new control value. The callback table omits many older callbacks such as queue load/destroy and VM mapping, suggesting those are supplied elsewhere or unsupported in this table.

State and persistence: this file mostly observes or returns register state rather than owning queue lifecycle. It mutates interrupt registers, `GRBM_GFX_INDEX`, `SQ_CMD`, and TCP watch address registers. Debug state persists wherever the returned per-VMID control values are applied by KFD.

Dependencies and integration: includes GC 12.0.0 register headers, SOC24 GRBM selection, and KFD UAPI trap masks. `gfx_v12_kfd2kgd` is the integration point and sets `get_atc_vmid_pasid_mapping_info = NULL`.

Risks: the reduced callback set means callers must tolerate NULL function pointers for queue lifecycle and VM operations. `BUG()` is used for invalid SDMA engine ids. Address-watch clear and SDMA doorbell reporting are placeholders returning 0. Test signals include callback-table NULL handling, HQD/SDMA dump sizes, trap mask round-trips including wave-start/end, stall launch mode value 4, and TCP watchpoint hits on GFX12.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12_1.c

Purpose: this file adapts the narrow GFX12 KFD/KGD support to GC 12.1.0 multi-instance hardware. It uses `amdgpu_gfx_select_me_pipe_q`, `GET_INST`, and XCC-aware register writes for queue selection, interrupt setup, dumps, wave control, trap value generation, and address watchpoints.

Important APIs and functions: `init_interrupts_v12_1`, `hqd_dump_v12_1`, `hqd_sdma_dump_v12_1`, `wave_control_execute_v12_1`, debug trap enable/disable, trap override validation and conversion, wave-launch mode, address-watch setup/clear, and SDMA doorbell placeholder populate `gfx_v12_1_kfd2kgd`. `get_sdma_rlc_reg_offset` maps a logical SDMA engine through `GET_INST(SDMA0, engine_id)` and `adev->sdma.num_inst_per_xcc` to select SDMA0 or SDMA1 register bases per XCC.

Control flow: compute dump selects the requested queue for the requested instance, reads 56 HQD registers from `regCP_MQD_BASE_ADDR` through `regCP_HQD_PQ_WPTR_HI`, and releases selection. SDMA dump calculates a per-instance queue offset and reads the compact queue register range through context status. Wave control locks `grbm_idx_mutex`, writes per-instance `GRBM_GFX_INDEX` and `SQ_CMD`, and restores broadcast selection. Debug trap and trap-mask logic mirrors GFX12, including wave-start/end support and special launch-mode value 4 for stall. Address watch writes TCP watch address registers through `WREG32_XCC` and uses a 25-bit high address mask.

State and persistence: state persists in per-instance interrupt, GRBM/SQ, SDMA, TCP watch, and debug-control registers when callers apply returned values. This file allocates dump buffers with `kmalloc`, unlike some sibling files that use `kmalloc_objs`.

Dependencies and integration: depends on GC 12.1.0 register headers, `soc_v1_0.h`, XCC instance macros, KFD UAPI trap masks, and AMDGPU SDMA instance topology. Integration is `const struct kfd2kgd_calls gfx_v12_1_kfd2kgd`.

Risks: SDMA offset logic depends on correct `num_inst_per_xcc`; invalid modulo cases call `BUG()`. Address-watch high bits differ from GFX12 (`0x1ffffff` versus `0xffff`), so cross-generation reuse is unsafe. The callback table remains narrow and leaves queue lifecycle callbacks absent. Tests should cover multi-XCC dump instance selection, SDMA engine-to-XCC mapping, 49-bit watch addresses, trap mask round-trips, and NULL callback handling in KFD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v7.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v7.c

Purpose: this file is the CIK/GFX7 KFD/KGD bridge. It implements queue, SDMA, PASID/VMID, memory, wave-control, scratch backing, VM fault, and VM page-table callbacks for older GFX7 hardware using legacy register names and SRBM selection.

Important APIs and functions: `kgd_program_sh_mem_settings` writes SH memory config, APE1 base/limit, and bases for a VMID. `kgd_set_pasid_vmid_mapping` programs ATC mapping, waits indefinitely for update status, clears it, and mirrors mapping to IH. `kgd_hqd_load` writes CIK MQD registers, enables doorbell control, temporarily releases SRBM selection while reading user WPTR to avoid lock inversion, then marks HQD active. SDMA load/dump/occupancy/destroy operate on `cik_sdma_rlc_registers`. `kgd_hqd_destroy` issues CP dequeue requests with an IQ timer workaround and polls active state. `set_scratch_backing_va`, `set_vm_context_page_table_base`, and `read_vmid_from_vmfault_reg` support KFD memory and fault handling.

Control flow: SRBM selection writes `mmSRBM_GFX_CNTL` under `srbm_mutex`. HQD destroy disables doorbell control, maps KFD drain/reset requests, waits around IQ timer and pending dequeue conditions with IRQs disabled and preemption disabled, writes `CP_HQD_DEQUEUE_REQUEST`, and waits for inactive. SDMA queue load disables RB enable, waits up to two seconds for idle, programs doorbell, RPTR/WPTR, virtual address, ring base, RPTR writeback, and enables RB control.

State and persistence: state lives in legacy CP HQD, SDMA RLC, ATC/IH, SH, VM context, and fault-status registers. MQD SDMA RPTR is saved on destroy. The VM page-table base writes only the low 32 bits to `VM_CONTEXT8_PAGE_TABLE_BASE_ADDR + vmid - 8`.

Dependencies and integration: includes CIK/GFX7, SDMA, OSS, GMC, and CIK structure headers. Integration is `gfx_v7_kfd2kgd`, which lacks modern debug trap callbacks but includes legacy scratch and VM fault support.

Risks: PASID mapping waits without timeout, which can hang on hardware failure. Direct user WPTR read requires careful lock release/reacquire and could race queue state changes. The IQ timer workaround uses IRQ/preemption suppression and fixed retry loops. Test signals include CIK queue load/destroy under memory pressure, SDMA idle timeout, VM fault VMID reporting, scratch backing VA programming, and PASID mapping update-status behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v8.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v8.c

Purpose: this file implements the VI/GFX8 KFD/KGD bridge. It is structurally close to GFX7 but adds GFX8 MQD layout support, HIQ scheduler programming, Tonga-specific EOP handling, larger SDMA dump coverage, and VI-specific register constants.

Important APIs and functions: `kgd_program_sh_mem_settings`, `kgd_set_pasid_vmid_mapping`, `kgd_init_interrupts`, compute `kgd_hqd_load/dump/is_occupied/destroy`, SDMA `kgd_hqd_sdma_load/dump/is_occupied/destroy`, `get_atc_vmid_pasid_mapping_info`, `kgd_wave_control_execute`, `set_scratch_backing_va`, and `set_vm_context_page_table_base` populate `gfx_v8_kfd2kgd`. `get_sdma_rlc_reg_offset` uses `SDMA1_REGISTER_OFFSET` and `KFD_VI_SDMA_QUEUE_OFFSET`.

Control flow: compute HQD load selects the queue, programs scheduler1 for HIQ if VMID is 0, writes MQD/HQD fields, skips EOP RPTR/WPTR writes on Tonga as an erratum, enables doorbell, releases SRBM while reading user WPTR, reacquires and writes WPTR if valid, then activates the HQD. Destroy clears HIQ scheduler1 when applicable, runs the same IQ timer/dequeue-pending workaround as GFX7, sends a dequeue request, and waits for inactive. SDMA load/destroy follow disable-wait-program-enable and save RPTR.

State and persistence: persistent state includes SRBM-selected HQD registers, `RLC_CP_SCHEDULERS.scheduler1`, SDMA RLC registers, ATC/IH mappings, scratch backing VA, and VM context page-table base. SDMA RPTR is saved back into the MQD.

Dependencies and integration: depends on GFX8, OSS 3.0, GMC 8.1, VI structures, and ASIC id definitions. Integration is `const struct kfd2kgd_calls gfx_v8_kfd2kgd`.

Risks: PASID mapping has no timeout. Tonga EOP handling is special and must not be removed without context-save validation. Like GFX7, the HQD destroy workaround blocks IRQ/preemption briefly and relies on fixed retry limits. Test signals include Tonga and non-Tonga HQD load, HIQ scheduler1 setup/clear, SDMA queue lifecycle, PASID update-status completion, and scratch/VM page-table programming on KFD VMIDs only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v9.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v9.c

Purpose: this is the shared GFX9 KFD/KGD implementation and the main provider of helpers reused by Arcturus, Aldebaran, and GC 9.4.3. It supports XCC-aware SRBM selection, PASID/VMID mapping for GFX and MM hubs, compute and SDMA queue lifecycle, HIQ mapping, wave control, VM setup, debug trap control, address watchpoints, CU occupancy, trap handler setup, and HQD reset/PQ discovery.

Important APIs: exported helpers include `kgd_gfx_v9_program_sh_mem_settings`, `kgd_gfx_v9_set_pasid_vmid_mapping`, `kgd_gfx_v9_init_interrupts`, `kgd_gfx_v9_hqd_load`, `kgd_gfx_v9_hiq_mqd_load`, `kgd_gfx_v9_hqd_dump`, `kgd_gfx_v9_hqd_is_occupied`, `kgd_gfx_v9_hqd_destroy`, `kgd_gfx_v9_wave_control_execute`, `kgd_gfx_v9_get_atc_vmid_pasid_mapping_info`, VM PT setup, CU occupancy, debug trap helpers, address watch helpers, IQ wait helpers, trap handler setup, `kgd_gfx_v9_hqd_get_pq_addr`, and `kgd_gfx_v9_hqd_reset`. Static SDMA helpers populate the base GFX9 table.

Control flow: queue access uses `soc15_grbm_select` with `GET_INST(GC, inst)` under `srbm_mutex`. HQD load writes MQD registers, enables doorbells, uses CP one-shot WPTR polling instead of CPU user-memory reads, starts EOP fetch, and activates the queue. PASID mapping writes ATHUB VMID0 and VMID16 mappings, waits for update bits, clears status, and mirrors values into GFX and MM IH LUTs. HQD destroy sends CP dequeue requests and polls active with timeout. HQD reset enters RLC safe mode, records the queue base, tries `SPI_COMPUTE_QUEUE_RESET`, then optionally resets the MEC pipe via `CP_MEC_CNTL`. CU occupancy locks SRBM and GRBM index, scans shader engines and active queue maps, reads wave counts, and records doorbell offsets.

State and persistence: state lives in GC, ATHUB, OSSSYS, SDMA, GFXHUB, MMHUB, SPI debug, TCP watch, and MQD fields. Debug trap state is global for many GFX9 parts; wave launch stall and trap mask programming are protected by `grbm_idx_mutex`. SDMA destroy persists RPTR back into MQDs.

Dependencies and integration: depends on GC 9.0, SDMA 4.0, ATHUB 1.0, OSSSYS 4.0, SOC15/SOC15D helpers, `v9_structs`, KFD UAPI, and AMDGPU GFX/MM hub funcs. `gfx_v9_kfd2kgd` is the base table; the header exports helpers for sibling ASIC files.

Risks: several waits have no timeout for PASID mapping, while queue operations rely on timeout returns that callers must handle. Debug trap mask is global on some parts, so validation only permits OR address-watch requests to avoid cross-process impact. CU occupancy can be inaccurate if VMID-to-PASID remaps while registers are sampled. Test signals include queue load/destroy/reset on each XCC, dual hub PASID mapping, CU occupancy under oversubscription, debug trap/watchpoint flows, and SDMA lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v9.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v9.h

Purpose: this header exports the shared GFX9 helper surface used both by the base GFX9 callback table and by closely related ASIC-specific files such as Arcturus, Aldebaran, and GC 9.4.3.

Important APIs: declarations cover shared memory programming, PASID/VMID mapping, interrupt setup, compute HQD load/HIQ load/dump/occupancy/destroy, wave control, ATC mapping query, VM page-table base setup, CU occupancy, trap handler setup, queue acquire/release and queue-mask helpers, wave launch stall, debug trap enable/disable, trap override validation/programming, wave launch mode, address watch setup/clear, IQ wait retrieval and dequeue packet construction, HQD PQ address reporting, HQD reset, and SDMA doorbell reporting.

Control flow and integration: ASIC files include this header to compose their `kfd2kgd_calls` tables from generic GFX9 operations while overriding only the hardware-specific pieces. GC 9.4.3 uses queue acquire/release and base queue mask helpers, Arcturus and Aldebaran reuse most compute/VM functions, and Aldebaran/GC 9.4.3 share debug helpers through this surface where compatible.

State and persistence: the header itself is stateless. The declared functions mutate queue, VM, debug, watch, and hub registers and sometimes save queue pointers into MQDs.

Dependencies: consumers need `struct amdgpu_device`, `struct mm_struct`, `struct kfd_cu_occupancy`, KFD preemption/debug constants, user-pointer annotations, and fixed-width integer types. The header is a private driver contract.

Risks and test signals: this is a broad sharing boundary; signature or semantic changes can affect several ASIC generations. Some helpers are safe only for GFX9 register layouts, so new ASIC files should not reuse them without checking register offsets, hub topology, and debug-mask scope. Compile coverage catches API drift; runtime signals should include all callback-table consumers, multi-XCC queue selection, debug watchpoints, CU occupancy, and HQD reset/PQ introspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v9.h -->
