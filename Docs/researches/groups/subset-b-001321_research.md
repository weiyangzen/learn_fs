# subset-b-001321 Research

Grouped research report for AMDGPU register access, rings, reset, SDMA, synchronization, tracing, and related support files. Each section preserves the source path and is bounded by reconciliation markers for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reg_access.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reg_access.c

Purpose: implements AMDGPU register access helpers for direct MMIO, indirect PCIe/NBIO windows, block-specific register spaces, SMN base lookup, XCC-aware GFX register access, and wait-on-register polling. It centralizes the low-level hardware access policy used by the rest of the driver, including SR-IOV KIQ/RLCG routing, reset-domain interaction, and tracepoint emission.

Important APIs and functions: `amdgpu_reg_access_init()` initializes spinlocks and clears function pointers in `adev->reg`; `amdgpu_reg_*_rd32/wr32()` wrappers dispatch SMC, UVD context, DIDT, GC/SE CAC, audio endpoint, PCIe, extended PCIe, 64-bit PCIe, and PCIe-port accesses through registered callbacks and log `dev_err_once()` when unsupported. `amdgpu_reg_get_smn_base64()` chooses a device-specific SMN base provider or falls back to `amdgpu_reg_smn_v1_0_get_base()` for selected PCI IDs and XGMI/NBIO/MP0/UMC/DF blocks. `amdgpu_device_rreg/wreg()` are the core 32-bit MMIO helpers; XCC variants add per-XCC KIQ/RLCG dispatch. `amdgpu_mm_rreg8/wreg8()` provide byte MMIO. Indirect helpers read/write 32-bit and 64-bit registers through NBIO PCIe index/data registers, including extended high-address variants with high-index clearing. `amdgpu_device_wait_on_rreg()` polls until a masked register value reaches an expected value or `adev->usec_timeout` expires.

Control flow: normal register reads first honor `amdgpu_device_skip_hw_access()`. If the dword register offset fits in `adev->rmmio_size`, helpers either use KIQ under SR-IOV runtime while they can take `reset_domain->sem` for read, use RLCG access for SR-IOV VF non-runtime GFX accesses when flags allow it, or perform direct `readl/writel`. Out-of-MMIO offsets are converted to byte offsets and delegated to PCIe indirect callbacks. Indirect PCIe helpers serialize index/data programming under `adev->reg.pcie.lock`, write the index, read back for posting, then access data and clear high-index state when needed. The wait helper resets its timeout whenever the observed value changes, otherwise delays one microsecond per loop.

State and persistence: this file mutates only in-memory driver state and hardware registers. Persistent driver state consists of callback pointers and spinlocks in `adev->reg`, plus hardware-visible register writes. It also relies on `adev->no_hw_access`, SR-IOV runtime state, `adev->reset_domain`, NBIO offset callbacks, and `adev->gfx.rlc.rlcg_reg_access_supported`. No on-disk state is produced.

Dependencies and integration points: includes `amdgpu.h`, `amdgpu_reset.h`, `amdgpu_trace.h`, `amdgpu_virt.h`, and its header. It integrates with KIQ register helpers, SR-IOV RLCG virtualization, NBIO offset providers, reset-domain locking, tracepoints `trace_amdgpu_device_rreg/wreg`, and PCI device IDs. Higher-level IP blocks use these helpers via the public prototypes and common `RREG32/WREG32` macros.

Risks: missed locking around indirect index/data windows can corrupt concurrent access; incorrect SR-IOV KIQ/RLCG flag selection can bypass virtualization policy or access unavailable hardware; fallback PCIe offsets are used when NBIO funcs are absent and must match legacy hardware; `BUG()` in 8-bit helpers makes out-of-range offsets fatal; the wait helper warning string contains `0x%08xn`, likely intended to include a newline. Returning zero for unsupported reads can mask hardware capability errors if callers do not validate support.

Test signals: hardware bring-up should exercise direct MMIO and indirect PCIe reads/writes, SR-IOV VF runtime/non-runtime access, reset contention paths, XCC-specific GFX registers, and unsupported callback paths. Tracepoint visibility for `amdgpu_device_rreg/wreg`, timeout warnings from `amdgpu_device_wait_on_rreg()`, and lack of lockdep complaints around `reset_domain->sem` and PCIe spinlocks are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reg_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reg_access.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reg_access.h

Purpose: declares the register-access abstraction used by AMDGPU IP blocks. It defines callback types, per-register-space state containers, the aggregate `struct amdgpu_reg_access`, and public helper prototypes for direct, block, PCIe, extended, SMN, indirect, XCC, and wait-on-register access.

Important APIs and types: callback typedefs cover 32-bit register operations, extended 64-bit-address register operations, 64-bit data operations, block-qualified register operations, and SMN base resolution. `struct amdgpu_reg_ind`, `amdgpu_reg_ind_blk`, and `amdgpu_reg_pcie_ind` pair spinlocks with dispatch functions for each register namespace. `struct amdgpu_reg_smn_ext` stores an optional SMN base callback. `struct amdgpu_reg_access` groups SMC, UVD context, DIDT, GC/SE CAC, audio endpoint, PCIe, and SMN helpers under `adev->reg`.

Control flow: the header does not implement logic, but it defines the contracts used by `amdgpu_reg_access.c`: initialization must set locks and callback pointers, IP-specific setup code installs callbacks, and callers access hardware through wrapper functions rather than calling function pointers directly.

State and persistence: all structures are runtime-only members of `struct amdgpu_device`; spinlocks protect shared indirect windows and function-pointer-backed register spaces. No persistent storage is represented.

Dependencies and integration points: depends on Linux types/spinlocks and AMD HW IP block enums from `amdgpu_ip.h`. It is included by low-level register access code and transitively by common AMDGPU headers/macros. The prototypes integrate with NBIO, SMU/SMC, audio endpoint, SR-IOV, RLCG, and XCC code paths.

Risks: callback signatures must match the hardware block semantics exactly; register offsets are a mix of dword and byte units depending on helper family, so callers can easily pass the wrong unit. Missing callback initialization results in zero-returning read wrappers or ignored writes.

Test signals: compile coverage catches signature drift. Runtime validation should include unsupported callback cases, all registered callback families on supported ASICs, and lockdep around indirect register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reg_access.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_res_cursor.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_res_cursor.h

Purpose: provides an inline cursor for walking the physical backing ranges of TTM resources used by AMDGPU memory management. It abstracts VRAM buddy blocks and range-manager nodes behind a common `start`, `size`, and `remaining` iteration API.

Important APIs and types: `struct amdgpu_res_cursor` stores current physical start, current segment size, remaining requested bytes, current backend node pointer, and memory type. `amdgpu_res_first()` initializes a cursor for a resource subrange. `amdgpu_res_next()` advances by bytes, crossing nodes as needed. `amdgpu_res_cleared()` reports whether the current VRAM buddy block is marked cleared.

Control flow: initialization validates `start + size <= res->size`, selects behavior by `res->mem_type`, walks VRAM buddy block lists or TTM range-manager `drm_mm_node` arrays until the requested start offset is located, and sets the first segment to the minimum of node remainder and requested size. Advancing decrements remaining, adjusts within-segment offsets when possible, or moves to the next VRAM block/range node when the current segment is exhausted. Unsupported or null resources fall back to a linear cursor with no backend node.

State and persistence: the cursor is stack/local iteration state; it does not mutate TTM resources. It reads VRAM manager block metadata, range-manager nodes, and cleared flags.

Dependencies and integration points: depends on DRM MM, TTM resource/range manager, and `amdgpu_vram_mgr.h`. It is used by VM updates, TTM moves, display pinning, VRAM SG-table creation, and coredump code to translate logical BO offsets into physical GPU-addressable chunks.

Risks: off-by-one or unit errors between bytes, pages, and dwords can corrupt DMA/VM operations. `BUG_ON(size > cur->remaining)` and `BUG_ON(start + size > res->size)` make invalid callers fatal. The fallback path can hide unsupported memory types by returning linear offsets, which is useful for special paths but risky if callers assume physical placement. `amdgpu_res_cleared()` only supports VRAM.

Test signals: migration and VM-update tests should cover VRAM multi-block resources, GTT/range-manager resources, doorbell/MMIO remap placements, zero-size ranges, and cleared VRAM skip behavior in TTM clearing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_res_cursor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reset.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reset.c

Purpose: implements common reset orchestration for AMDGPU devices, including ASIC-specific reset-control initialization, reset handler dispatch, reset-domain lifetime/locking, reset descriptions, and a special XGMI hive reset-on-init flow.

Important APIs and functions: `amdgpu_reset_init/fini()` dispatch to Aldebaran, Sienna Cichlid, or SMU 13.0.10 reset setup based on MP1 IP version. `amdgpu_reset_prepare_hwcontext()` and `amdgpu_reset_perform_reset()` select a reset handler from `adev->reset_cntl` and invoke its prepare/perform/restore hooks. `amdgpu_reset_do_xgmi_reset_on_init()` drives an init-time reset for a multi-device XGMI list using `xgmi_reset_on_init_handler`. `amdgpu_reset_create_reset_domain()` allocates a domain, initializes a single-threaded workqueue, refcount, reset atomics, and rwsem. `amdgpu_device_lock_reset_domain()` and unlock set `in_gpu_reset` and hold the rwsem write side. `amdgpu_reset_get_desc()` formats reset source descriptions; `amdgpu_reset_in_recovery()` checks init-level state.

Control flow: XGMI reset-on-init preparation unregisters each GPU instance, suspends valid/hardware IP blocks in reverse order except display, marks hardware off, and backs up VCN firmware BO state. Reset execution locks each device reset control, records the active ASIC reset method, queues `xgmi_reset_work` on the default workqueue for all devices, flushes all work, collects `asic_reset_res`, then clears active reset and unlocks. Restore calls `amdgpu_device_reinit_after_reset()` and initializes KFD paths if needed. Generic reset dispatch requires a handler; missing handlers return `-EOPNOTSUPP`.

State and persistence: reset state is in memory: `active_reset`, `reset_lock`, `in_gpu_reset`, `reset_res`, reset-domain refcount, reset workqueue, and each IP block's `status.hw`. Hardware state changes through suspend/reset/reinit hooks. No disk persistence.

Dependencies and integration points: integrates with ASIC-specific reset modules (`aldebaran`, `sienna_cichlid`, `smu_v13_0_10`), IP block suspend/reinit, XGMI reset work, KFD initialization, VCN BO backup, reset-domain synchronization used by register access, and reset source reporting used by recovery/coredump paths.

Risks: the XGMI path must coordinate multiple devices; partial queueing failures or one device returning reset error can leave some devices already reset. `amdgpu_reset_xgmi_reset_on_init_prep_hwctxt()` returns `r` after the loop even if no iteration initializes it on unusual input, although normal non-empty lists cover it. Handler hooks are assumed present once a handler is returned. Reset-domain lock ordering is critical because register access may take read locks and reset takes write locks.

Test signals: multi-GPU XGMI reset-on-init, single-device rejection, unsupported ASIC fallback, reset-domain lockdep, GPU recovery logs, KFD reinit after reset, and `amdgpu_reset_get_desc()` strings for job/RAS/MES/HWS/user/userq sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reset.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reset.h

Purpose: declares AMDGPU reset contexts, handler/control objects, reset domains, reset source/flag enums, and helper APIs for reset orchestration and reset-domain synchronization.

Important APIs and types: `enum AMDGPU_RESET_FLAGS` records full reset, skip hardware reset, skip coredump, and host FLR bits. `enum AMDGPU_RESET_SRCS` identifies reset trigger sources. `struct amdgpu_reset_context` carries method, requesting device, job, hive, device list, flags, and source. `struct amdgpu_reset_handler` defines prepare/perform/restore hooks plus optional `do_reset`. `struct amdgpu_reset_control` owns reset work, lock, handlers array, active reset method, and handler lookup/async callbacks. `struct amdgpu_reset_domain` owns a refcounted workqueue, type, rwsem, and reset status atomics.

Control flow: callers create domains, get/put references with kref helpers, schedule work on domain workqueues, lock/unlock domain reset windows, and dispatch through reset handlers. The `for_each_handler` macro iterates registered handler slots until NULL. DPC helpers synchronize PCIe DPC state with `adev->no_hw_access`.

State and persistence: all state is runtime-only and held under `amdgpu_device` or reset-domain objects. The rwsem is the central synchronization primitive between reset and hardware access.

Dependencies and integration points: includes `amdgpu.h` for core device types. It is consumed by reset implementation, register access, GPU recovery, ASIC reset modules, and PCIe DPC handling.

Risks: handler arrays are bounded by `AMDGPU_RESET_MAX_HANDLERS`; missing terminators or wrong hook setup can produce unsupported reset or NULL dereferences in implementation code. `amdgpu_reset_pending()` requires the domain sem to be held and asserts that via lockdep.

Test signals: compile coverage for handler signatures, lockdep for reset-domain helpers, reset work scheduling on both single-device and XGMI domains, and DPC paths toggling no-hardware-access state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c

Purpose: implements common ring-buffer management for AMDGPU command engines. Rings are GPU-visible command buffers with host-maintained write pointers, GPU read pointers, fence writeback, scheduler integration, debugfs introspection, MQD initialization, software-ring delegation hooks, and reset helper glue.

Important APIs and functions: `amdgpu_ring_max_ibs()` returns per-ring-type IB count limits. `amdgpu_ring_alloc()`, `amdgpu_ring_insert_nop()`, `amdgpu_ring_generic_pad_ib()`, `amdgpu_ring_commit()`, and `amdgpu_ring_undo()` manage command emission reservations and pointer updates. `amdgpu_ring_init()` allocates writeback slots, fence state, ring backup, GTT ring BO, and scheduler registration. `amdgpu_ring_fini()` frees writeback slots, ring BO, backup, and VMID wait fence. `amdgpu_ring_soft_recovery()` tries engine-provided soft recovery for a timed-out fence. Debugfs helpers expose ring contents, virtual ring RAS CPER dumps, MQD memory, and forced fence errors. `amdgpu_ring_test_helper()` tests a ring and updates scheduler readiness. `amdgpu_ring_init_mqd()` builds MQD properties and calls the per-HW-IP MQD manager. IB begin/end/offset helpers forward to software-ring muxing when `ring->is_sw_ring`.

Control flow: allocation aligns the requested dwords, checks `max_dw` except during reemit, stores old wptr, and calls `begin_use`. Command writers advance `ring->wptr` under `buf_mask/ptr_mask`; commit pads to alignment, issues a memory barrier, calls hardware `set_wptr`, then `end_use`. Initialization chooses scheduler depth based on ring type, assigns a global ring index once, allocates writeback offsets for rptr/wptr/fence/trailing fence/conditional execution, starts fences for non-CPER rings, sizes the ring by max submission depth, allocates backup memory and the GPU ring BO, clears the ring with NOPs, and registers the scheduler for the ring's HW IP/priority unless disabled. Debugfs read returns a 12-byte pointer header followed by ring data, with special CPER handling.

State and persistence: ring state includes GPU BOs, CPU mappings, writeback offsets/addresses, local wptr/rptr cache, fence driver state, scheduler readiness, MQD pointers, doorbell data, VM hub/invalidation engine, and reset backup buffers. Persistent storage is not used; hardware-visible ring BO and writeback memory are re-created at driver init/resume.

Dependencies and integration points: depends on DRM scheduler, writeback allocator, AMDGPU BO management, fence driver, RAS manager, MQD managers, debugfs, CPER/RAS virtualization, GFX priority helpers, and ring function tables supplied by each IP block. It is a central integration point for IB scheduling, VM flush emission, reset recovery, and user/kernel submissions.

Risks: mismatched `count_dw` reservations and writes can overrun ring space; pointer masking must match 32-bit versus 64-bit ring support; cleanup does not remove the ring from `adev->rings` but marks resources unavailable; debugfs reads expose hardware state and must maintain alignment/user-copy correctness; scheduler readiness must be consistent with ring tests and reset recovery. Soft recovery intentionally sets fence error `-ENODATA` before trying to make progress, so callers must tolerate failed fences.

Test signals: ring tests at IP init, IB ring tests, debugfs `amdgpu_ring_*` and `amdgpu_mqd_*` reads, fence completion under normal and reset paths, scheduler ready state, CPER ring dumps, and soft recovery behavior during induced hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ring.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ring.h

Purpose: defines AMDGPU ring, indirect buffer, scheduler, fence, ring function-table, and public ring/fence/IB interfaces. It is the core contract between generic AMDGPU scheduling code and ASIC/IP-specific command engines.

Important APIs and types: constants define ring limits, fence owner sentinels, fence flags, and IB pool types. `enum amdgpu_ring_type` maps ring classes to HW IPs and internal types such as KIQ, MES, UMSCH, and CPER. `struct amdgpu_ib` represents a scheduled indirect buffer. `struct amdgpu_fence_driver` and `struct amdgpu_fence` hold fence writeback and reset metadata. `struct amdgpu_ring_funcs` is the key polymorphic interface: pointer get/set, CS parse/patch, IB/fence/VM/cache emitters, test hooks, NOP/padding, power-use hooks, register waits, preemption, reset, and cleaner shader emission. `struct amdgpu_ring` stores device pointer, function table, scheduler, ring BO, writeback slots, fences, MQD, doorbell, VM hub, scheduler policy, software-ring state, and reset cache.

Control flow: callers generally use macros such as `amdgpu_ring_emit_ib`, `amdgpu_ring_emit_fence`, `amdgpu_ring_get_rptr`, and `amdgpu_ring_set_wptr` to dispatch through the function table. Inline writers update the in-memory ring buffer and wptr. `amdgpu_ring_patch_cond_exec()` computes emitted dword distance and patches a conditional-execute placeholder. Public prototypes connect to ring init/fini, debugfs, MQD init, IB allocation/scheduling, fence driver operations, scheduler readiness, and reset helpers.

State and persistence: the header models runtime ring state only. GPU-visible persistence is in ring BOs, writeback memory, MQD BOs, and fence slots. Fence owners encode synchronization policy across VM, KFD, and general submissions.

Dependencies and integration points: depends on DRM scheduler, DRM suballocator, DRM print, and AMDGPU UAPI. It is included throughout the driver by gfx, compute, SDMA, VCN, VM, IB, fence, scheduler, reset, and debugfs code.

Risks: the `amdgpu_ring_funcs` table has many optional and mandatory callbacks; missing callbacks can fail at runtime. The inline write helpers do not validate capacity beyond `count_dw` accounting, so callers must reserve correctly. Pointer/unit fields combine bytes, dwords, GPU addresses, CPU pointers, and masks; wrong units cause hard-to-debug command corruption. Software ring fields add coupling to `amdgpu_ring_mux`.

Test signals: build coverage for all IP function tables, ring init/test/IB tests, fence wait and forced-completion tests, reset reemit paths, and scheduler behavior across priorities and ring types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ring_mux.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ring_mux.c

Purpose: implements a multiplexer that lets multiple software GFX rings feed one real hardware ring, including low/high priority software rings, approximate software read pointers, IB chunk tracking, and mid-command-buffer preemption resubmission.

Important APIs and functions: `amdgpu_ring_mux_init/fini()` allocate entries, initialize the chunk slab, lock, and resubmit timer. `amdgpu_ring_mux_add_sw_ring()` registers a software ring entry. `amdgpu_ring_mux_set_wptr()` copies new software-ring commands into the real ring and commits them. `amdgpu_ring_mux_get_wptr/rptr()` expose software pointers, with rptr estimated from real-ring rptr and last copied range. `amdgpu_sw_ring_*_gfx()` are GFX wrappers for ring callbacks. `amdgpu_sw_ring_ib_begin/end/mark_offset()` manage per-IB chunk metadata. `amdgpu_mcbp_handle_trailing_fence_irq()` handles trailing fence IRQs after preemption, processes low-priority fences, and schedules resubmission if work remains.

Control flow: setting a software ring wptr takes the mux spinlock, optionally drains pending low-priority resubmissions, records copy pointers and corresponding real-ring positions, copies wrapped or linear command ranges to the real ring with `amdgpu_ring_write_multiple()`, and commits the real ring. IB begin allocates a chunk with start pointer and sentinel patch offsets; mark calls store control/CE/DE offsets; IB end stores end pointer and fence sequence and removes already signaled chunks. If high-priority work arrives and MCBP detects old unsignaled low-priority fences while no high-priority fences are pending, it sets `pending_trailing_fence_signaled` and calls real-ring `preempt_ib`. When trailing fence IRQ confirms preemption, resubmission state is armed and a timer later copies low-priority chunks between last completed and target seqno, patching offsets when needed.

State and persistence: mux state is runtime-only: real ring pointer, software entries, per-entry copy/read/write pointers, chunk lists with fence seqnos and patch offsets, spinlock, timer, resubmit seqno/wptr, and pending trailing fence flag. The real ring receives copied command packets and fence timestamps are updated for resubmitted chunks.

Dependencies and integration points: depends on `amdgpu_ring`, fence helpers, GFX MCBP flag, real-ring preemption, patch callbacks (`patch_cntl`, `patch_ce`, `patch_de`), timers, spinlocks, and slab allocation. It integrates with `amdgpu_ring.c` through `ring->is_sw_ring` IB hooks and with GFX ring function tables for software-ring pointer callbacks.

Risks: chunk list operations rely on begin/end ordering; `list_last_entry()` is used without an explicit empty check and can be unsafe if callers mark/end without a chunk. The global `amdgpu_mux_chunk_slab` is shared at file scope, so multiple mux instances could conflict during init/fini. Approximate rptr logic is intentionally imprecise for analysis tools. Preemption/resubmission races depend on timer/spinlock behavior and fence seqno correctness. Copying command packets from software rings must preserve wrap and alignment expectations of the real ring.

Test signals: high/low priority GFX submissions, MCBP-induced preemption, trailing fence IRQ handling, resubmission timer paths, ring debug dumps comparing software and real pointers, and stress with wrapped software ring buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ring_mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ring_mux.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ring_mux.h

Purpose: declares the software-ring multiplexer data structures and public helpers used by GFX rings to share a real hardware ring.

Important APIs and types: `struct amdgpu_mux_entry` tracks one software ring and the last copied range in both hardware and software pointer spaces. `enum amdgpu_ring_mux_offset_type` identifies control, DE, and CE patch offsets. `enum ib_complete_status` names default, preempted, and completed IB states, although this header's implementation does not use it directly. `struct amdgpu_ring_mux` stores the real ring, entry array, spinlock, resubmit state, timer, and trailing-fence flag. `struct amdgpu_mux_chunk` records one IB's software-ring start/end, fence seqno, and patch offsets.

Control flow: the declared functions initialize/finalize mux state, add software rings, route pointer operations, start/end IB chunk tracking, mark patch offsets, handle trailing fence IRQs, and provide GFX-specific software ring callbacks.

State and persistence: all state is volatile runtime scheduling/preemption metadata; no persistent storage. The structures point to `struct amdgpu_ring` objects owned elsewhere.

Dependencies and integration points: includes Linux timer/spinlock and `amdgpu_ring.h`. Used by GFX ring setup and generic ring IB hooks.

Risks: consumers must maintain `entry_index` consistency and call begin/end/mark in valid order. Chunk offsets use `buf_mask + 1` as a sentinel, which assumes valid ring offsets are always `<= buf_mask`. The header exposes enough mutable structure that misuse outside the mux implementation could break synchronization.

Test signals: compile coverage with GFX software rings enabled, pointer callback tests, and preemption/resubmission validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ring_mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rlc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rlc.c

Purpose: implements generic GFX RLC support: safe-mode transitions for clock/power gating updates, allocation/setup/free of RLC save-restore, clear-state, and CP jump-table buffers, and parsing/registering RLC firmware components from versioned firmware headers.

Important APIs and functions: `amdgpu_gfx_rlc_enter_safe_mode()` and exit call IP-specific RLC functions when clock-gating flags require safe updates. `amdgpu_gfx_rlc_init_sr()`, `init_csb()`, and `init_cpt()` allocate BOs and initialize save/restore, clear-state, and CP table buffers. `amdgpu_gfx_rlc_setup_cp_table()` copies jump-table data from CE/PFP/ME/MEC/MEC2 firmware headers into the CP table. `amdgpu_gfx_rlc_fini()` releases the allocated BOs. `amdgpu_gfx_rlc_init_microcode()` parses RLC firmware header v2.0 plus optional v2.1 through v2.5 sections and registers PSP-loadable firmware images in `adev->firmware.ucode` while increasing `fw_size`.

Control flow: safe mode exits early if already in desired state or RLC is disabled, then calls set/unset hooks only for relevant CG flags. Buffer initialization uses AMDGPU BO helpers; failure calls `amdgpu_gfx_rlc_fini()` to clean partial state. Firmware parsing always requires major version >= 2, runs v2.0 first to extract common version/register restore data and allocate combined register-list storage, then conditionally parses additional minor-version sections. PSP firmware registration is conditional on `adev->firmware.load_type == AMDGPU_FW_LOAD_PSP` and component sizes being non-zero.

State and persistence: RLC state is held in `adev->gfx.rlc`: BO pointers/GPU addresses/CPU mappings, safe-mode flags per RLC instance, firmware version/feature fields, byte sizes, and pointers into firmware blobs. Hardware-visible state includes VRAM/GTT BOs consumed by RLC/CP firmware. The code does not write disk state.

Dependencies and integration points: depends on Linux firmware support, `amdgpu_gfx.h`, firmware header layouts, AMDGPU BO helpers, PSP firmware loader bookkeeping, and per-ASIC `amdgpu_rlc_funcs`. It integrates with GFX power/clock gating, firmware loading, CP command processor setup, and SR-IOV RLCG register-access ranges.

Risks: firmware header offsets and sizes are trusted; malformed firmware could lead to invalid pointers without extensive local validation. `register_list_format` allocation is not freed in this file's `fini()` path, so ownership must be handled elsewhere or this is leak-prone. CP table setup assumes firmware pointers for each ME index are present and table sizes fit the allocated table. Minor-version parsing uses equality for 3/4/5, so a newer minor version would only get sections up to v2.2 unless updated.

Test signals: firmware load logs, PSP `fw_size` accounting, RLC safe-mode transitions during CG/PG changes, BO allocation failure handling, CP table validation, and ASIC bring-up across RLC firmware header versions 2.0 through 2.5.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rlc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rlc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rlc.h

Purpose: defines RLC firmware identifiers, table-of-content layouts, RLC function callbacks, RLCG register-access control registers, the `struct amdgpu_rlc` runtime state, and the public RLC helper prototypes.

Important APIs and types: `FIRMWARE_ID`, `SOC21_FIRMWARE_ID`, and `SOC24_FIRMWARE_ID` enumerate firmware table IDs for RLC, SDMA, CP, MES, RS64, debug, SR-IOV, and related images. `RLC_TABLE_OF_CONTENT` and V2 define bitfield layouts for RLC autoload/TOC entries. `struct amdgpu_rlc_funcs` supplies ASIC-specific safe-mode, init/resume/stop/reset/start, clear-state, CP table, SPM VMID update, and RLCG access-range hooks. `struct amdgpu_rlcg_reg_access_ctrl` stores scratch and VFI registers for indirect RLCG access. `struct amdgpu_rlc` stores BOs, firmware metadata, safe-mode flags, autoload/TOC buffers, and RLCG support data.

Control flow: the header defines callback and state contracts consumed by GFX IP code and `amdgpu_rlc.c`. Generic helpers allocate and populate buffers using sizes and hooks stored here; ASIC-specific code fills `funcs`, register lists, CP table sizes, and register-access controls.

State and persistence: all fields are runtime driver state or pointers to firmware blobs/BO mappings. Hardware-visible persistence is via GPU BOs for save/restore, clear-state, CP table, autoload, and TOC content.

Dependencies and integration points: includes `clearstate_defs.h` and references `struct amdgpu_device` and `struct amdgpu_ring`. It integrates with GFX firmware loading, RLC autoload, SR-IOV RLCG register access, power gating, and CP setup.

Risks: bitfield TOC layouts are ABI-sensitive with firmware; changing packing or enum IDs can break firmware loading. `AMDGPU_MAX_RLC_INSTANCES` bounds per-XCC safe-mode and register-control arrays; callers must validate instance IDs. Firmware pointer fields reference loaded firmware memory and require lifetime coordination.

Test signals: firmware TOC parsing for SOC21/SOC24, safe-mode across multiple RLC instances, RLCG register access on SR-IOV devices, and GFX init/resume/reset flows using each `amdgpu_rlc_funcs` callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rlc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sa.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sa.c

Purpose: wraps DRM suballocation management around an AMDGPU kernel BO, providing a simple suballocated memory pool for small GPU-visible allocations such as indirect buffers.

Important APIs and functions: `amdgpu_sa_bo_manager_init()` creates a kernel BO, clears it, and initializes `drm_suballoc_manager`. `amdgpu_sa_bo_manager_fini()` tears down the manager and frees the BO. `amdgpu_sa_bo_new()` allocates a suballocation. `amdgpu_sa_bo_free()` frees a suballocation, optionally fence-delayed. Under debugfs, `amdgpu_sa_bo_dump_debug_info()` emits allocator state through a DRM printer.

Control flow: initialization allocates a BO with requested size, GPU page alignment, and domain, then initializes the suballocator with requested alignment. Allocation calls `drm_suballoc_new()` with non-blocking behavior (`false`, timeout 0) and maps errors to NULL plus negative return. Free checks for NULL pointer-to-pointer, passes the fence to the suballocator, then clears the caller's pointer.

State and persistence: runtime state lives in `struct amdgpu_sa_manager`: backing BO, GPU address, CPU pointer, and DRM suballoc manager. Fence-delayed frees persist only in allocator runtime state until fences signal.

Dependencies and integration points: depends on AMDGPU BO helpers and DRM suballoc. It is used by IB pools and other small GPU-visible allocation paths.

Risks: `amdgpu_sa_bo_manager_fini()` logs an error if called without a BO but otherwise cannot recover leaked suballoc users. Allocation is non-blocking, so callers must handle `-ENOSPC`/allocator errors. Fence lifetime correctness is critical because premature reuse can corrupt in-flight GPU commands.

Test signals: IB allocation/free stress, fence-delayed reuse, debugfs allocator dumps, and BO allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sched.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sched.c

Purpose: implements the AMDGPU scheduler ioctl that lets privileged/user API paths override process-wide or context-specific AMDGPU context priorities for another DRM file descriptor.

Important APIs and functions: `amdgpu_sched_ioctl()` validates the UAPI op and priority, then dispatches to `amdgpu_sched_process_priority_override()` or `amdgpu_sched_context_priority_override()`. The process helper resolves an FD to `amdgpu_fpriv`, locks its context manager, and applies `amdgpu_ctx_priority_override()` to each context in the IDR. The context helper resolves a single context by ID and overrides only that context.

Control flow: the ioctl first rejects unknown ops before validating arguments. FD acquisition uses `CLASS(fd, f)(fd)` cleanup style and returns `-EINVAL` for empty descriptors. Priority validity is checked via `amdgpu_ctx_priority_is_valid()`. Context-manager updates are serialized by `mgr->lock`; single-context lookup uses `amdgpu_ctx_get/put`.

State and persistence: mutates runtime context priority override fields in `struct amdgpu_ctx`; no persistent storage. Changes affect subsequent scheduler entity priority decisions until context reset/destruction or another override.

Dependencies and integration points: depends on DRM AMDGPU UAPI, Linux fd helpers, `amdgpu_ctx`, `amdgpu_vm`, and `amdgpu_file_to_fpriv`. It is part of the DRM ioctl surface and interacts with context priority conversion in `amdgpu_ctx.c`/scheduler code.

Risks: FD-based override can affect all contexts owned by a different DRM file, so access control must be enforced by surrounding ioctl policy. Races are managed for context manager enumeration, but priority changes can still interact with active scheduling. Invalid context IDs and non-AMDGPU fds must be handled cleanly.

Test signals: ioctl tests for both ops, invalid op/priority/fd/context ID, multiple contexts under one file, and observable scheduler priority changes in submitted jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sched.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sched.h

Purpose: declares scheduler priority conversion and the AMDGPU scheduler ioctl entry point.

Important APIs and types: forward-declares `enum drm_sched_priority`, `struct drm_device`, and `struct drm_file`; declares `amdgpu_to_sched_priority()` and `amdgpu_sched_ioctl()`.

Control flow: no implementation here; it establishes the interface between context priority code, DRM scheduler priority mapping, and the ioctl dispatcher.

State and persistence: none.

Dependencies and integration points: included by scheduler ioctl implementation and code needing AMDGPU-to-DRM scheduler priority conversion.

Risks: the header exposes `amdgpu_to_sched_priority()` although that function is implemented elsewhere, so signature drift would break compilation. The final `#endif` uses a C++-style comment but is harmless.

Test signals: compile coverage and ioctl/context priority tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c

Purpose: provides common SDMA helper logic for instance/ring lookup, context-save-area addressing, RAS registration/interrupt dispatch, SDMA firmware loading/parsing, scheduler-mask debugfs, reset-mask sysfs, shared page-queue helpers, and per-engine soft reset orchestration.

Important APIs and functions: `amdgpu_sdma_get_instance_from_ring()` and `amdgpu_sdma_get_index_from_ring()` map rings to SDMA instances. `amdgpu_sdma_get_csa_mc_addr()` returns per-instance CSA addresses for OS preemption when allowed. `amdgpu_sdma_ras_late_init()`, `amdgpu_sdma_process_ras_data_cb()`, `amdgpu_sdma_process_ecc_irq()`, and `amdgpu_sdma_ras_sw_init()` wire SDMA into the RAS framework. `amdgpu_sdma_init_microcode()` requests firmware, parses header versions 1/2/3, handles duplicate firmware across instances, and registers PSP ucode entries. Debugfs scheduler mask get/set toggles `ring->sched.ready` for SDMA and page queues. Sysfs reset mask exposes supported reset modes. `amdgpu_sdma_get_shared_ring()` and `amdgpu_sdma_is_shared_inv_eng()` handle page queues sharing invalidation engines. `amdgpu_sdma_reset_engine()` stops schedulers/queues, performs instance soft reset, restarts queues, force-completes fences, and restarts scheduler workqueues.

Control flow: firmware initialization decodes an IP-version-based filename, requests instance-specific firmware, rejects invalid duplicate/header combinations, populates version and `burst_nop`, optionally clones instance 0 into all instances, then registers PSP firmware entries depending on header major version and special multi-AID handling. RAS late init registers IRQs for each supported instance and rolls back on failure. Reset engine rejects SR-IOV VFs, serializes by per-instance mutex, optionally stops scheduler workqueues, calls IP callbacks to stop/start kernel queues around soft reset, and only restarts schedulers/force-completes fences on reset success.

State and persistence: SDMA runtime state includes per-instance firmware pointers/versions, rings, page queues, burst-NOP flag, aid/xcc IDs, firmware BO fields, engine reset mutex, guilty flags, RAS interface, supported reset mask, scheduler-ready flags, and reset callback list. Firmware blobs are kernel-managed loaded resources; no disk state is written.

Dependencies and integration points: depends on Linux firmware, AMDGPU RAS, reset helpers, GC register headers, KFD SRAM ECC signaling, PSP firmware loader bookkeeping, DRM scheduler, debugfs, sysfs device attributes, and SDMA IP-specific function callbacks.

Risks: duplicate firmware mode copies entire instance structs, so pointer ownership and later release must avoid double-free; `amdgpu_sdma_destroy_inst_ctx()` breaks after first release when duplicate is true. Debugfs scheduler-mask validation must reject a zero effective mask to avoid disabling all queues. Reset engine only restarts schedulers on success; failure leaves queues stopped by design or requires higher-level recovery. Instance IDs must be validated by callers before indexing. CSA addressing supports only index <= 31.

Test signals: firmware loading across header versions and duplicate/non-duplicate modes, PSP ucode size accounting, RAS ECC interrupt injection, debugfs `amdgpu_sdma_sched_mask`, sysfs `sdma_reset_mask`, page queue/shared invalidation behavior on GC 9.4.3/9.4.4/9.5.0, and per-engine reset success/failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.h

Purpose: defines common SDMA data structures, IRQ instance IDs, RAS memory IDs, SDMA function callbacks, buffer-copy/fill function table, and public SDMA helper prototypes.

Important APIs and types: `AMDGPU_MAX_SDMA_INSTANCES` caps instances at 16; `enum amdgpu_sdma_irq` enumerates per-instance ECC IRQ indices. `struct amdgpu_sdma_funcs` supplies stop/start/soft-reset kernel queue callbacks. `struct amdgpu_sdma_instance` stores firmware, two rings, burst-NOP, AID/XCC ID, firmware BO, reset mutex, guilty state, and callbacks. `enum amdgpu_sdma_ras_memory_id` names SDMA memory blocks for RAS. `struct amdgpu_sdma` aggregates instances, IRQ sources, masks, page-queue flags, RAS state, dumps, reset support, and CSA info callback. `struct amdgpu_buffer_funcs` exposes SDMA-backed copy/fill emitters used by memory management.

Control flow: the header defines the contracts implemented by `amdgpu_sdma.c` and IP-specific SDMA generations. Macros `amdgpu_emit_copy_buffer` and `amdgpu_emit_fill_buffer` dispatch through `adev->mman.buffer_funcs`.

State and persistence: structures are runtime driver state and hardware command-emission callbacks. Firmware pointers and BOs are kernel resources tied to device lifetime.

Dependencies and integration points: includes `amdgpu_ras.h` and references rings, devices, IRQs, firmware, and buffer manager code. Used by SDMA IP blocks, TTM migration/fill code, RAS, reset, and scheduler integration.

Risks: the `union` of `aid_id/xcc_id` assumes mutually exclusive interpretation by ASIC family. Function callbacks are optional in some paths but reset logic depends on them for per-engine reset. Shared ring/page queue fields must be initialized consistently with `has_page_queue`.

Test signals: compile coverage for IP callbacks, SDMA ring init/tests, buffer copy/fill migration tests, RAS block tests, and reset callback coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_securedisplay.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_securedisplay.c

Purpose: implements a debugfs validation interface for PSP secure display trusted application commands and shared helper functions for preparing and reporting secure display TA command buffers.

Important APIs and functions: `psp_securedisplay_parse_resp_status()` maps TA status codes to device error logs. `psp_prep_securedisplay_cmd_buf()` points into the PSP securedisplay shared buffer, zeros a command, sets default generic-failure status, and sets the command ID. Under debugfs, `amdgpu_securedisplay_debugfs_write()` parses opcode input, runtime-resumes the DRM device, serializes on the securedisplay mutex, invokes query-TA or send-ROI-CRC TA commands, logs results, and runtime-autosuspends. `amdgpu_securedisplay_debugfs_init()` creates `securedisplay_test` when the TA context is initialized.

Control flow: debugfs writes are single-shot (`*pos` must be zero) and limited to a 63-byte command string. Opcode 1 sends `TA_SECUREDISPLAY_COMMAND__QUERY_TA`; opcode 2 validates `phy_id < TA_SECUREDISPLAY_MAX_PHY`, writes it into the input union, and sends `SEND_ROI_CRC`. Both commands call `psp_securedisplay_invoke()` and inspect the returned command status. Runtime PM is acquired before TA interaction and released at the end.

State and persistence: mutable state is the PSP securedisplay shared command buffer, securedisplay mutex, and runtime PM usage count. No persistent data is stored; debugfs only logs responses.

Dependencies and integration points: depends on debugfs, runtime PM, PSP context, `ta_secureDisplay_if.h`, and `psp_securedisplay_invoke()` implemented in PSP code. The debugfs node is initialized from AMDGPU debugfs setup after PSP TA load.

Risks: opcode 2 returns early on invalid input without dropping the runtime PM reference acquired earlier, which can leak a PM usage count. Input parsing via `sscanf` does not validate conversion counts. The interface is write-only debugfs and intended for validation, but it drives secure TA and I2C-related operations, so it should remain restricted. Shared-buffer layout must match TA ABI.

Test signals: debugfs writes for opcode 1 and 2, invalid opcode/phy ID, runtime PM reference accounting, TA status error logs, and securedisplay TA initialization/termination in PSP flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_securedisplay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_securedisplay.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_securedisplay.h

Purpose: declares secure display debugfs initialization and PSP secure display command helper functions.

Important APIs and types: includes `amdgpu.h` and `ta_secureDisplay_if.h`; declares `amdgpu_securedisplay_debugfs_init()`, `psp_securedisplay_parse_resp_status()`, and `psp_prep_securedisplay_cmd_buf()`.

Control flow: no implementation; the header exposes helpers to PSP initialization code and debugfs setup.

State and persistence: none in the header; functions operate on PSP securedisplay context and shared TA command buffers.

Dependencies and integration points: integrates AMDGPU PSP code, TA ABI definitions, and debugfs validation code.

Risks: header guard lacks trailing double underscore but is unique enough. The include of full `amdgpu.h` is broad but needed for PSP/device types.

Test signals: compile coverage in PSP and debugfs code, plus securedisplay TA debugfs runtime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_securedisplay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_seq64.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_seq64.c

Purpose: implements a global pool of 64-bit GPU/CPU-visible slots mapped into reserved VM address space. It is used for user queue fence memory, TLB counters, and VM updates.

Important APIs and functions: `amdgpu_seq64_init()` allocates a GTT BO of `AMDGPU_VA_RESERVED_SEQ64_SIZE`, zeros it, and initializes the bitmap. `amdgpu_seq64_fini()` frees it. `amdgpu_seq64_alloc()` finds a free slot, sets the bitmap, and returns VM VA, optional GPU address, and CPU pointer. `amdgpu_seq64_free()` clears a slot by VA. `amdgpu_seq64_map()` locks the VM page directory and BO using `drm_exec`, adds the BO to a VM, maps it at the reserved seq64 VA range as readable/uncached, and updates page tables. `amdgpu_seq64_unmap()` locks and removes a file-private mapping.

Control flow: VA base is computed with `AMDGPU_VA_RESERVED_SEQ64_START(adev)` and sign-extended. Mapping uses `drm_exec_until_all_locked()` with retry-on-contention around VM PD and BO locks, then `amdgpu_vm_bo_add`, `amdgpu_vm_bo_map`, and `amdgpu_vm_bo_update`; failures delete the BO VA before cleanup. Allocation is first-fit over `adev->seq64.used`, with no visible lock in this file, so callers must provide serialization or accept bitmap atomicity assumptions.

State and persistence: `adev->seq64` stores the backing BO, GPU address, CPU base pointer, slot count, and bitmap. Per-file mappings are stored in `fpriv->seq64_va`. State is runtime-only but GPU-visible while mapped.

Dependencies and integration points: depends on AMDGPU BO and VM APIs, reserved VA constants, GMC sign extension, and DRM exec locking. It is initialized/finalized from device lifecycle and used by user queue fence code.

Risks: allocation/free bitmap operations are not locked here, so concurrent callers could race unless higher-level code serializes. `amdgpu_seq64_free()` trusts VA arithmetic; invalid VA below base underflows before division. Mapping failure paths clean up BO VA but leave caller-owned `*bo_va` pointer stale unless caller discards it. The doc comment in the header says `free` takes GPU address, while implementation expects VA.

Test signals: device init/fini, concurrent user queue fence allocation/free, VM map/unmap per file, reserved VA correctness across GPU address modes, and ENOSPC behavior after exhausting slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_seq64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_seq64.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_seq64.h

Purpose: declares the seq64 slot-pool structure and public lifecycle, allocation, free, map, and unmap APIs.

Important APIs and types: `AMDGPU_MAX_SEQ64_SLOTS` derives the number of 64-bit slots from reserved VA size. `struct amdgpu_seq64` holds the backing BO, slot count, GPU address, CPU base pointer, and bitmap. Public functions cover init/fini, allocate/free, and VM map/unmap.

Control flow: no implementation, but callers are expected to initialize the pool once per device, map it into process VMs as needed, allocate 64-bit slots, and free by VA.

State and persistence: runtime state only; backing memory is a GTT BO visible to GPU and CPU.

Dependencies and integration points: includes `amdgpu_vm.h`; used by core device lifecycle and user queue fence/VM update code.

Risks: prototype `amdgpu_seq64_free(struct amdgpu_device *adev, u64 gpu_addr)` names the argument `gpu_addr`, while implementation interprets it as VA. That naming mismatch can mislead callers and reviewers.

Test signals: compile coverage, seq64 user queue fence tests, slot exhaustion/reuse, and VM mapping lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_seq64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_smuio.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_smuio.h

Purpose: defines the SMUIO abstraction for ROM register access, clock-gating state, package/topology identity, XGMI/ethernet-switch capabilities, custom HBM detection, and GPU clock counter retrieval.

Important APIs and types: `enum amdgpu_pkg_type` identifies APU, CEM, OAM, BB, and unknown packages. `struct amdgpu_smuio_mcm_config_info` stores socket and die IDs. `struct amdgpu_smuio_funcs` supplies callbacks for ROM index/data offsets, ROM clock gating, clock-gating flags, die/socket ID, package type, host GPU XGMI support, ethernet switch connectivity, custom HBM support, and GPU clock counter. `struct amdgpu_smuio` stores the callback table.

Control flow: no logic; ASIC-specific SMUIO modules populate `funcs`, and common code calls through it to query platform/topology and ROM clocking information.

State and persistence: runtime callback pointer only. Returned topology/package data reflects hardware registers.

Dependencies and integration points: references `struct amdgpu_device` and is embedded under AMDGPU device state. Integrates with SMU/SMUIO IP blocks, topology discovery, clock gating, ROM access, and clock counter users.

Risks: optional callbacks require NULL checks by callers. Package enum numeric values likely match firmware/register encodings and should not be changed casually.

Test signals: ASIC-specific SMUIO init, ROM access, clock-gating state reporting, topology ID queries, XGMI support detection, and clock counter reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_smuio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_socbb.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_socbb.h

Purpose: defines firmware/UAPI-style structures for SoC bounding-box data used by display and power calculations, including voltage-scaling states and memory/display latency/bandwidth parameters.

Important APIs and types: `struct gpu_info_voltage_scaling_v1_0` stores per-state clocks and DRAM speed. `struct gpu_info_soc_bounding_box_v1_0` stores self-refresh times, urgent latencies, writeback latency, ideal bandwidth percentages, request size, downspread, DRAM timing/channel parameters, fabric/DCN return widths, VCO data, urgent out-of-order return sizes, VM page size, clock-change latencies, XFC timing, urgent burst flag, number of states, and up to eight clock-limit entries.

Control flow: no functions. The structures are data contracts for code that parses or reports GPU info bounding-box data.

State and persistence: no runtime state here; instances are populated elsewhere from firmware/BIOS or query data.

Dependencies and integration points: uses fixed-width integer types and integrates with display mode validation, DCN bandwidth calculations, and KMS GPU-info query paths.

Risks: struct layout is ABI/data-format sensitive. One field uses a C++-style comment with a long descriptive name, harmless for C99 kernels but notable. Consumers must respect `num_states` and not overrun the fixed `clock_limits[8]` array.

Test signals: display bring-up with firmware-provided bounding boxes, KMS info queries, and bandwidth/latency validation across supported ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_socbb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sync.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sync.c

Purpose: implements AMDGPU synchronization objects that collect DMA fences needed before command submission, deduplicate fences by context, filter implicit fences by owner/mode, transfer fences to DRM scheduler jobs, wait for them, and manage a slab cache for sync entries.

Important APIs and functions: `amdgpu_sync_create()` initializes the hash table. `amdgpu_sync_fence()` adds a fence, keeping only the later fence per context. `amdgpu_sync_resv()` extracts relevant fences from a DMA reservation object. `amdgpu_sync_kfd()` extracts KFD bookkeeping fences. `amdgpu_sync_peek_fence()` returns the next unsignaled dependency, using scheduled fences for same-ring scheduler fences. `amdgpu_sync_get_fence()` removes and returns an unsignaled fence. `amdgpu_sync_clone()`, `amdgpu_sync_move()`, `amdgpu_sync_push_to_job()`, `amdgpu_sync_wait()`, and `amdgpu_sync_free()` manage sync contents. `amdgpu_sync_init/fini()` create/destroy the slab cache.

Control flow: adding a fence first checks for null, then scans the bucket for signaled entries or matching contexts; signaled entries can be replaced, and matching contexts keep the later fence via `dma_fence_is_later()`. Reservation syncing iterates READ-usage fences, unwraps fence chains, filters by `amdgpu_sync_test_fence()`, adds one chain fence when any contained fence matters, and drops iterator references appropriately. Filtering always syncs undefined owners/moves, skips KFD eviction fences except for eviction/move owners, skips VM update fences for most non-VM/KFD owners, and applies ALWAYS/NE_OWNER/EQ_OWNER/EXPLICIT modes. Push-to-job adds unsignaled fences as DRM scheduler dependencies without removing them. Wait blocks on each fence and frees entries as they complete.

State and persistence: `struct amdgpu_sync` owns a small hash table of `amdgpu_sync_entry` objects, each holding a fence reference. Global state is the `amdgpu_sync_slab` cache. No persistent storage.

Dependencies and integration points: depends on DMA fences/chains/reservation objects, DRM scheduler fences/jobs, AMDGPU ring scheduler ownership, KFD fence type detection, trace header inclusion, and context owner sentinels from `amdgpu_ring.h`.

Risks: fence reference ownership is subtle, especially in reservation chain iteration where the stored fence may be the chain fence while filtering inspects contained fences. Same-ring optimization returns the scheduled fence rather than finished fence, which is correct for ordering but can surprise users expecting completion. No locking is internal to `amdgpu_sync`; callers must serialize access. Owner filtering must remain aligned with VM/KFD eviction semantics to avoid deadlocks or missing dependencies.

Test signals: implicit sync across reservation objects, explicit mode skipping, VM/KFD owner filtering, fence chain handling, same-ring scheduled-fence optimization, dependency push to scheduler jobs, interruptible/non-interruptible wait, and slab init/fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sync.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sync.h

Purpose: declares AMDGPU sync modes, the sync object container, and public fence collection/manipulation APIs.

Important APIs and types: `enum amdgpu_sync_mode` defines ALWAYS, not-equal-owner, equal-owner, and EXPLICIT filtering modes. `struct amdgpu_sync` is a 16-bucket hash table of fence entries. Function prototypes cover creation, direct fence add, reservation/KFD extraction, peek/get, clone/move, push-to-job, wait, free, and subsystem init/fini.

Control flow: the header defines the external lifecycle: initialize a sync object, collect fences, optionally inspect or move dependencies, push them to jobs or wait, and free resources.

State and persistence: sync state is in-memory fence references only; no persistent state.

Dependencies and integration points: depends on Linux hashtable and forward-declared DMA/AMDGPU types. It integrates with command submission, VM updates, BO reservation handling, scheduler jobs, and KFD.

Risks: callers must call `amdgpu_sync_create()` before use and `amdgpu_sync_free()` after use. The object is not self-locking. Small hash size is intentional but can be a performance concern with many fence contexts.

Test signals: command submission dependency tests, reservation sync tests, clone/move/free leak checks, and scheduler dependency integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_trace.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_trace.h

Purpose: defines Linux tracepoints for major AMDGPU events: register reads/writes, interrupt vectors, BO creation/move/list status, command submission and scheduling, VM mapping/update/flush operations, PASID allocation/free, isolation changes, cleaner shader fences, IB pipe sync, and reset register dumps.

Important APIs and events: `TRACE_EVENT(amdgpu_device_rreg/wreg)` records device ID, register, and value. `amdgpu_iv` records interrupt vector metadata. `amdgpu_bo_create`, `amdgpu_bo_list_set`, `amdgpu_cs_bo_status`, and `amdgpu_bo_move` cover memory objects. `amdgpu_cs`, `amdgpu_cs_ioctl`, and `amdgpu_sched_run_job` record submissions and scheduler jobs. VM events include BO map/unmap, mapping/update/CS derived events, PTE updates, set/copy PTEs, and VM flush. PASID events share an event class. Other tracepoints cover isolation pointer transitions, cleaner shader sequence, pipe sync fence dependencies, and reset register dumps.

Control flow: tracepoint macros define per-event prototypes, argument capture, fast assignment, and print formats. `AMDGPU_JOB_GET_TIMELINE_NAME` derives scheduler fence timeline names for job events. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` make the header consumable by `define_trace.h`.

State and persistence: tracepoints do not own state; they snapshot runtime objects into trace buffers when enabled. Dynamic arrays are used for PTE destination dumps.

Dependencies and integration points: depends on Linux tracepoint infrastructure, AMDGPU object/job/VM/ring definitions, DMA fences, and scheduler objects. Called from register access, interrupt handling, CS ioctl/scheduler paths, VM code, BO management, PASID allocator, reset dump code, and IB scheduling.

Risks: tracepoint field access assumes objects are alive for the call duration; enabling verbose events like PTE updates can produce large trace output. Format strings and field widths are ABI-ish for tracing tooling. `AMDGPU_JOB_GET_TIMELINE_NAME` dereferences nested scheduler fence ops and assumes a valid job fence.

Test signals: kernel tracepoint compilation, `trace-cmd`/ftrace enabling for each event, command submission traces, VM update traces with dynamic arrays, and register access traces from `amdgpu_reg_access.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_trace_points.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_trace_points.c

Purpose: instantiates the AMDGPU tracepoint definitions by defining `CREATE_TRACE_POINTS` and including `amdgpu_trace.h`.

Important APIs and functions: this file has no functions. It includes `drm/amdgpu_drm.h`, `amdgpu_cs.h`, and `amdgpu.h` so tracepoint definitions have the needed type context, then includes the trace header with `CREATE_TRACE_POINTS`.

Control flow: during compilation, Linux tracepoint macros emit the storage and registration objects for the trace events declared in `amdgpu_trace.h`. Other translation units include the header without `CREATE_TRACE_POINTS` to reference the trace calls.

State and persistence: tracepoint registration state is kernel runtime metadata; no driver-specific persistent state.

Dependencies and integration points: directly depends on tracepoint infrastructure through `amdgpu_trace.h` and is required exactly once in the driver build to avoid missing or duplicate tracepoint definitions.

Risks: removing or duplicating this translation unit would cause link errors or duplicate definitions. Include ordering matters because tracepoint prototypes reference AMDGPU CS/device types.

Test signals: successful module/kernel link, tracepoint availability under `/sys/kernel/tracing/events/amdgpu/`, and runtime trace emission from call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_trace_points.c -->
