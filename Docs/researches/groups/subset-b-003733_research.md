# subset-b-003733 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ring.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ring.c

## Purpose
`radeon_ring.c` implements the generic Radeon command ring bookkeeping used by graphics, DMA, UVD, VCE, and secondary CP rings. It manages CPU-side write pointers, GPU read-pointer observation, ring allocation, commit/rollback, lockup accounting, ring backup/restore for reset handling, BO-backed ring memory allocation, teardown, and debugfs inspection.

## Important APIs, types, and functions
Core entry points are `radeon_ring_alloc`, `radeon_ring_lock`, `radeon_ring_commit`, `radeon_ring_unlock_commit`, `radeon_ring_undo`, `radeon_ring_unlock_undo`, `radeon_ring_init`, and `radeon_ring_fini`. Lockup support is handled by `radeon_ring_lockup_update` and `radeon_ring_test_lockup`. Reset recovery uses `radeon_ring_backup` and `radeon_ring_restore`. `radeon_ring_supports_scratch_reg` identifies rings that can write scratch registers. Debugfs support exposes `radeon_debugfs_ring_info_show` and ring-name mapping for GFX, CP1/CP2, DMA, UVD, and VCE rings.

## Control flow
Allocation refreshes free dwords from the hardware read pointer, aligns the request to the ring fetch alignment, then waits on the next fence if there is not enough free space. Locking wraps allocation with `rdev->ring_lock`. Commit optionally emits an HDP flush through the ring, pads with NOPs to alignment, uses a memory barrier, optionally performs MMIO HDP flush, then writes the hardware write pointer. Undo restores `wptr_old` when command emission fails. Init creates a GTT BO, pins and maps it, sets pointer masks and writeback read-pointer addresses, then seeds lockup state. Fini detaches the ring under the lock and unmaps/unpins/unrefs the BO.

## State, dependencies, and integration points
Persistent state lives in `struct radeon_ring`: `ring_obj`, mapped `ring`, `gpu_addr`, `wptr`, `wptr_old`, `ptr_mask`, `ring_free_dw`, NOP opcode, writeback pointer addresses, and last semaphore addresses. It depends on Radeon BO, fence, writeback, ASIC ring callbacks, MMIO helpers, debugfs, and global `rdev->ring_lock`. Ring backup reads pending dwords from either a saved rptr register or WB memory, so reset recovery depends on valid read-pointer save support.

## Risks and test signals
Risks include off-by-one free-space accounting, missing barriers before wptr updates, padding/alignment mismatches, stale read-pointer writeback, and restoring commands that have already executed. Failures show up as ring stalls, fence timeouts, lockup reports, corrupted reset recovery, or debugfs ring dumps with unexpected rptr/wptr state. Useful signals are ring tests, IB tests, fence completion, suspend/resume, GPU reset recovery, and debugfs ring inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_sa.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_sa.c

## Purpose
`radeon_sa.c` wraps the DRM suballocator for Radeon small, temporary GPU-visible allocations. These allocations back transient structures such as semaphores and other ring scratch buffers without creating a full BO for every small object.

## Important APIs, types, and functions
The file operates on `struct radeon_sa_manager` and `struct drm_suballoc`. Manager lifecycle is split into `radeon_sa_bo_manager_init`, `radeon_sa_bo_manager_start`, `radeon_sa_bo_manager_suspend`, and `radeon_sa_bo_manager_fini`. Individual allocations use `radeon_sa_bo_new` and `radeon_sa_bo_free`. Debug builds expose `radeon_sa_bo_dump_debug_info`.

## Control flow
Initialization creates one Radeon BO of the requested size and initializes `drm_suballoc_manager` with the requested alignment. Start reserves, pins, and maps the manager BO in the requested domain, publishing GPU and CPU addresses. Suspend reverses the map/pin while keeping the BO allocated for resume. New allocations call `drm_suballoc_new` with nonblocking behavior disabled; frees optionally attach a DMA fence so the suballocation can be reused only after GPU use completes.

## State, dependencies, and integration points
State is held by the manager BO, `domain`, `gpu_addr`, `cpu_ptr`, and the embedded DRM suballocator. The file depends on Radeon BO reservation/pin/kmap helpers and DRM suballocation. `radeon_semaphore.c` uses the device `ring_tmp_bo` manager to allocate 8-byte semaphore slots that are visible to GPU engines.

## Risks and test signals
The main risks are freeing a suballocation before its fence completes, failing to pin/map the manager BO during resume, and exhausting the fixed pool under heavy synchronization pressure. Test signals include semaphore creation/free stress, ring synchronization tests, suspend/resume of the temporary pool, and debugfs suballocator dumps showing sane live/free ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_sa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_semaphore.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_semaphore.c

## Purpose
`radeon_semaphore.c` implements GPU semaphore objects used to synchronize command rings without always falling back to CPU fence waits. A semaphore is an 8-byte GPU-visible slot allocated from the ring temporary suballocator and emitted as signal/wait packets by ASIC-specific ring callbacks.

## Important APIs, types, and functions
The public functions are `radeon_semaphore_create`, `radeon_semaphore_emit_signal`, `radeon_semaphore_emit_wait`, and `radeon_semaphore_free`. The key type is `struct radeon_semaphore`, which stores the suballocation, GPU address, and a waiter count. Emission delegates to `radeon_semaphore_ring_emit` and emits tracepoints `radeon_semaphore_signale` and `radeon_semaphore_wait`.

## Control flow
Creation allocates the semaphore object, obtains an aligned 8-byte suballocation from `rdev->ring_tmp_bo`, records its GPU address, clears the backing 64-bit memory, and initializes waiter count. Signal and wait functions choose the target `struct radeon_ring`, call the ASIC emit hook, update `waiters`, and record the last wait/signal GPU address in the ring for lockup debugging. Free warns if waiters remain positive, frees the suballocation with an optional fence, releases memory, and nulls the caller pointer.

## State, dependencies, and integration points
The semaphore itself persists until explicitly freed. Its suballocation lifetime may extend until the supplied fence signals. Integration points are `radeon_sync.c`, media/test code, ring debugfs, tracepoints, ASIC ring packet emitters, and the DRM suballocator. Correctness depends on balanced signal and wait emission across rings and on consumers passing a fence when GPU work may still reference the semaphore slot.

## Risks and test signals
Unbalanced wait/signal counts can deadlock hardware; the file logs that condition as "hardware lockup imminent". Other risks are failed suballocation under pressure, stale semaphore memory reuse, and ASIC emit hooks returning false. Signals include ring sync tests, semaphore trace events, fence wait behavior, ring debugfs last semaphore addresses, and absence of GPU lockups during multi-ring submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_semaphore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_sync.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_sync.c

## Purpose
`radeon_sync.c` builds per-submission synchronization state from Radeon fences and reservation objects. It decides when to use GPU semaphores for cross-ring ordering and when to fall back to CPU waits.

## Important APIs, types, and functions
The file operates on `struct radeon_sync`, with arrays of target fences per ring and temporary semaphores. Public functions are `radeon_sync_create`, `radeon_sync_fence`, `radeon_sync_resv`, `radeon_sync_rings`, and `radeon_sync_free`. It relies on `radeon_fence_later`, `radeon_fence_need_sync`, `radeon_fence_note_sync`, `radeon_fence_wait`, DMA reservation iteration, and semaphore creation/emission.

## Control flow
Creation clears all semaphore and fence slots. `radeon_sync_fence` keeps only the later fence per ring and separately tracks the latest VM update fence. `radeon_sync_resv` iterates a DMA reservation object: Radeon fences from the same device are recorded, while foreign fences are waited on by CPU. `radeon_sync_rings` walks all ring fences, skips ones that do not require sync to the target ring, rejects disabled source rings, creates semaphores while capacity remains, emits a signal on the source ring and a wait on the target ring, then commits the source ring and records that the fence is synced to the target ring. If semaphore capacity or emission fails, it waits manually. `radeon_sync_free` releases semaphores using the final submission fence.

## State, dependencies, and integration points
The sync object is transient per IB/submission and does not persist beyond cleanup. It integrates with command submission, VM updates, BO reservation validation, and multi-ring scheduling. It assumes the caller already holds the target ring lock and has allocated enough wait-ring space before `radeon_sync_rings`.

## Risks and test signals
Risks include disabled rings causing invalid dependencies, too few semaphore slots, missed foreign-fence waits, uncommitted source-ring signal packets, and deadlock if ring locks are held incorrectly. Test signals include multi-ring sync tests, BO reservation sharing tests, VM update ordering, semaphore/fence tracepoints, and stress submissions across GFX, DMA, UVD, and VCE rings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_test.c

## Purpose
`radeon_test.c` provides built-in driver self-tests for GPU memory copies and ring synchronization. These are runtime diagnostics rather than unit tests: they allocate BOs, submit real GPU work, wait on fences, and validate copied data or semaphore ordering.

## Important APIs, types, and functions
`radeon_test_moves` invokes `radeon_do_test_moves` for DMA and/or blit copy engines. `radeon_test_create_and_emit_fence` emits a fence on ordinary rings or uses dummy UVD/VCE create/destroy messages for media rings. `radeon_test_ring_sync`, `radeon_test_ring_sync2`, `radeon_test_sync_possible`, and `radeon_test_syncing` exercise pairwise and three-way semaphore synchronization across ready rings.

## Control flow
The move test allocates a pinned VRAM BO, then iterates 1 MiB GTT BOs across the available GTT aperture. For each GTT BO it writes pointer-pattern data, copies GTT to VRAM through DMA or blit, waits on the fence, verifies VRAM contents, rewrites VRAM with a second pattern, copies back to GTT, waits, and verifies again. Cleanup unwinds pin/reserve/ref state through labeled error paths. Sync tests create a semaphore, submit wait packets before fences, verify fences do not signal early, emit signal packets from another ring, then wait and repeat. The three-ring variant checks that one of two waiting fences signals after the first signal and both complete after the second.

## State, dependencies, and integration points
The file depends on Radeon BO allocation/pin/map, copy callbacks, fences, rings, UVD/VCE dummy messages, semaphores, and DRM logging. It mutates hardware rings and temporary BOs but persists no state after cleanup. Media rings are handled specially because simple fence packets can be unsafe for their VCPU command streams.

## Risks and test signals
These tests can consume substantial VRAM/GTT and take time proportional to aperture size. Bugs in cleanup could leak pinned BOs or fences; bugs in expected patterns can produce false copy failures. Success is reported through `DRM_INFO`; failures use `DRM_ERROR` and `pr_warn`. Valuable signals are copy correctness in both directions, fence timeout behavior, semaphore ordering, and readiness of every configured ring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_trace.h

## Purpose
`radeon_trace.h` defines Linux tracepoints for key Radeon driver events: BO creation, command submission, VMID allocation, VM page-table updates, VM flushes, fence lifecycle, and semaphore wait/signal activity.

## Important APIs, types, and definitions
It declares `TRACE_SYSTEM radeon` and trace events `radeon_bo_create`, `radeon_cs`, `radeon_vm_grab_id`, `radeon_vm_bo_update`, `radeon_vm_set_page`, and `radeon_vm_flush`. It defines event classes for `radeon_fence_request` and `radeon_semaphore_request`, then derives `radeon_fence_emit`, `radeon_fence_wait_begin`, `radeon_fence_wait_end`, `radeon_semaphore_signale`, and `radeon_semaphore_wait`.

## Control flow
The header is included normally by users of trace macros and included once with `CREATE_TRACE_POINTS` by `radeon_trace_points.c`. Each event collects stable fields from Radeon objects into the trace entry during `TP_fast_assign`, then formats concise output with `TP_printk`. The final section deliberately sits outside the include guard to invoke `<trace/define_trace.h>`.

## State, dependencies, and integration points
The file depends on Linux tracepoint infrastructure, DRM file/device structures, Radeon BO/CS/VM/fence/semaphore structures, and helper functions such as `radeon_fence_count_emitted`. It does not own runtime state, but it becomes part of the kernel tracing ABI for this driver. VM code, fence code, semaphore code, and command submission call these tracepoints to expose ordering and memory-management behavior.

## Risks and test signals
Risks are tracepoint field drift, dereferencing invalid objects during tracing, and ABI/format changes affecting diagnostics. The misspelled event name `radeon_semaphore_signale` is part of the local trace API and must match call sites. Test signals include successful kernel tracepoint compilation, trace event availability under ftrace/perf, and sensible event streams during BO creation, command submission, VM updates, fence waits, and semaphore sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_trace_points.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_trace_points.c

## Purpose
`radeon_trace_points.c` is the single compilation unit that instantiates the Radeon tracepoints declared in `radeon_trace.h`.

## Important APIs, types, and functions
The file includes DRM Radeon UAPI and `radeon.h`, defines `CREATE_TRACE_POINTS`, and includes `radeon_trace.h`. It contains no functions of its own; the generated tracepoint definitions are produced by the Linux trace infrastructure.

## Control flow
Build-time control flow is the important behavior: ordinary source files include `radeon_trace.h` for declarations, while this file includes it with `CREATE_TRACE_POINTS` so storage and registration code are emitted exactly once. This avoids multiple-definition errors while still allowing every driver file to use `trace_radeon_*` calls.

## State, dependencies, and integration points
The generated tracepoint state is registered with the kernel tracing subsystem. This translation unit depends on all types referenced by tracepoint prototypes being visible through `radeon.h` and included DRM headers. It integrates with every file that calls Radeon tracepoints, especially VM, command submission, fences, semaphores, and BO allocation paths.

## Risks and test signals
The main risk is omitting this file from the build or defining `CREATE_TRACE_POINTS` elsewhere, causing missing trace symbols or duplicate definitions. Test signals are successful module/kernel link, visible Radeon trace events in tracing interfaces, and no unresolved `trace_radeon_*` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_trace_points.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ttm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ttm.c

## Purpose
`radeon_ttm.c` connects the Radeon BO layer to the DRM TTM memory manager. It initializes VRAM/GTT managers, chooses eviction placements, moves BOs by GPU blit or CPU memcpy, maps BO resources to bus addresses, manages GTT backing pages including userptr pages, and exposes memory debugfs views.

## Important APIs, types, and functions
The TTM driver callbacks are collected in `radeon_bo_driver`: `radeon_ttm_tt_create`, populate/unpopulate, destroy, eviction policy, move, and IO memory reservation. Public APIs include `radeon_ttm_init`, `radeon_ttm_fini`, `radeon_ttm_set_active_vram_size`, `radeon_ttm_tt_set_userptr`, `radeon_ttm_tt_is_bound`, `radeon_ttm_tt_has_userptr`, and `radeon_ttm_tt_is_readonly`. Internal helpers cover `radeon_evict_flags`, `radeon_move_blit`, `radeon_bo_move`, GART bind/unbind, userptr pin/unpin, and debugfs file operations.

## Control flow
Initialization creates the TTM device with the Radeon callback table, initializes VRAM and GTT range managers, constrains active VRAM to visible VRAM, reserves/pins a stolen VGA memory BO, and registers debugfs files. Moves bind TT memory when entering GTT, wait on the BO, handle null/system transitions cheaply, request multihop moves through TT for system-to-VRAM cases, try accelerated copy when the copy ring is ready, and fall back to memcpy. GTT backend bind pins userptr pages when present, builds DMA addresses, sets GART flags, and calls `radeon_gart_bind`; unbind reverses userptr pinning and GART mappings.

## State, dependencies, and integration points
Persistent state includes `rdev->mman.bdev`, TTM resource managers, the TTM page pool, stolen VGA memory BO, GART mappings, userptr metadata in `struct radeon_ttm_tt`, and movement statistics. It depends on Linux DMA, get_user_pages, sg tables, TTM, DRM PRIME, AGP helpers, Radeon BO/GART/copy/fence code, and debugfs. It is central to GEM, command validation, VM mappings, copy acceleration, and suspend/fini ordering.

## Risks and test signals
High-risk areas are userptr lifetime/security, dirtying writable user pages, DMA mapping direction, AGP vs PCIe backend divergence, visible-VRAM bus mapping, multihop move correctness, and fallback after accelerated copy failures. Test signals include BO allocation/move stress, userptr tests, PRIME/import paths, GART bind/unbind validation, debugfs VRAM/GTT reads, suspend/resume, and fence-protected eviction behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ttm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ttm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ttm.h

## Purpose
`radeon_ttm.h` is the private header for Radeon TTM initialization and teardown. It keeps the public surface of `radeon_ttm.c` small for other driver components.

## Important APIs, types, and functions
The header forward-declares `struct radeon_device` and declares `radeon_ttm_init(struct radeon_device *rdev)` and `radeon_ttm_fini(struct radeon_device *rdev)`.

## Control flow
There is no runtime control flow. The declarations are consumed by device initialization and teardown paths so ASIC bring-up code can initialize BO/TTM memory management and later finalize it in reverse order.

## State, dependencies, and integration points
The header owns no state. The declared functions manage `rdev->mman`, TTM resource managers, stolen VGA memory, debugfs files, and GART cleanup from the implementation file. It is integrated with Radeon ASIC init/fini paths such as RS400/RS600 and later chips through the broader BO initialization layer.

## Risks and test signals
Risks are minimal but include prototype drift or missing includes causing build failures. Runtime signals come indirectly from successful Radeon memory-manager initialization, BO creation, GART operation, and clean teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ttm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ucode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ucode.c

## Purpose
`radeon_ucode.c` provides firmware-header diagnostics and validation for Radeon microcode blobs. It understands the common header and IP-specific v1.0 header extensions for MC, SMC, GFX, RLC, and SDMA firmware.

## Important APIs, types, and functions
The shared helper `radeon_ucode_print_common_hdr` prints common header fields. Public printers are `radeon_ucode_print_mc_hdr`, `radeon_ucode_print_smc_hdr`, `radeon_ucode_print_gfx_hdr`, `radeon_ucode_print_rlc_hdr`, and `radeon_ucode_print_sdma_hdr`. `radeon_ucode_validate` checks that the firmware file size matches the little-endian `size_bytes` value in the common header.

## Control flow
Each print function reads header major/minor version, logs common fields, then uses `container_of` to access the corresponding extended header when `version_major == 1`. Unknown versions are logged as errors. Validation performs a simple total-size check and returns `0` or `-EINVAL`.

## State, dependencies, and integration points
The file owns no persistent state. It depends on Linux firmware objects, endian conversion helpers, DRM logging, and structures from `radeon_ucode.h`. UVD, SDMA, MC, GFX, RLC, and power-management firmware loading paths can call validation or header printers before copying microcode to hardware.

## Risks and test signals
Validation is intentionally shallow: it does not verify CRC, payload offsets, or minimum header size before dereferencing, so callers must only pass firmware buffers large enough for the common header. Risks include accepting corrupt blobs with matching size or rejecting valid future header formats in diagnostics. Test signals include firmware load success, expected debug logs for known blobs, and graceful `-EINVAL` on size mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ucode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ucode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ucode.h

## Purpose
`radeon_ucode.h` defines firmware size/address constants and packed header layouts shared by Radeon firmware loaders. It covers CP, MEC, RLC, MC, SDMA, and SMC microcode families across R600 through CIK-era chips.

## Important APIs, types, and definitions
The header contains many firmware size constants such as `R600_PFP_UCODE_SIZE`, `CIK_MEC_UCODE_SIZE`, `BONAIRE_MC2_UCODE_SIZE`, and `CIK_SDMA_UCODE_SIZE`, plus SMC start/size constants for RV7xx, Evergreen, Northern Islands, Southern Islands, Bonaire, and Hawaii variants. Header structures include `common_firmware_header`, `mc_firmware_header_v1_0`, `smc_firmware_header_v1_0`, `gfx_firmware_header_v1_0`, `rlc_firmware_header_v1_0`, `sdma_firmware_header_v1_0`, and `union radeon_firmware_header`. It declares the ucode print helpers and `radeon_ucode_validate`.

## Control flow
The file has no executable flow. Loader code uses constants to validate legacy firmware payload lengths and uses the header structures to parse newer binary firmware headers in a byte-order-aware way.

## State, dependencies, and integration points
The header owns no runtime state. It is consumed by `radeon_ucode.c`, UVD, SDMA, MC, CP, RLC, SMC, and ASIC-specific firmware loaders. It assumes Linux integer types and `struct firmware` are visible to consumers.

## Risks and test signals
Firmware constants must match the blobs shipped by linux-firmware; incorrect values cause firmware load failures or truncated uploads. Structure layout drift affects every parser of new-style firmware. Test signals are successful firmware request/validation across supported ASICs, correct printed versions/features, and absence of microcode load errors during device probe/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ucode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_uvd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_uvd.c

## Purpose
`radeon_uvd.c` manages the Unified Video Decoder block: firmware selection/loading, decoder BO allocation, session handle tracking, command-stream validation, dummy messages for tests, runtime clock/power usage, and UPLL divider calculation.

## Important APIs, types, and functions
Lifecycle APIs are `radeon_uvd_init`, `radeon_uvd_fini`, `radeon_uvd_suspend`, and `radeon_uvd_resume`. Session cleanup uses `radeon_uvd_free_handles`; placement constraints use `radeon_uvd_force_into_uvd_segment`. CS validation is centered on `radeon_uvd_cs_parse`, with helpers `radeon_uvd_cs_reg`, `radeon_uvd_cs_reloc`, `radeon_uvd_cs_msg`, `radeon_uvd_cs_msg_decode`, and `radeon_uvd_validate_codec`. Test/message helpers include `radeon_uvd_get_create_msg`, `radeon_uvd_get_destroy_msg`, and `radeon_uvd_send_msg`. Power helpers are `radeon_uvd_note_usage`, `radeon_uvd_idle_work_handler`, `radeon_uvd_calc_upll_dividers`, and `radeon_uvd_send_upll_ctlreq`.

## Control flow
Init chooses firmware by ASIC family, tries newer Bonaire firmware before legacy fallback, validates new-style headers, sets max handle count based on firmware version, allocates/pins/maps a VRAM VCPU BO sized for firmware, stack, heap, and sessions, and clears handle arrays. Resume copies firmware into the BO and zeroes the remaining working area. Suspend and file-close cleanup destroy active handles by sending destroy messages and waiting on fences. CS parsing requires 16-dword IB alignment and relocation chunks, accepts only selected packet/register writes, requires a message command before other commands, validates handle ownership, codec support, DPB/image sizes, buffer bounds, and 256MB segment restrictions.

## State, dependencies, and integration points
Persistent state is in `rdev->uvd`: firmware pointer, header flag, max handles, VCPU BO CPU/GPU addresses, atomic handles, owning DRM files, image sizes, and delayed idle work. It integrates with BO/GEM, command submission, relocation validation, UVD ring scheduling, fences, PM/DPM clocks, firmware loading, and test code.

## Risks and test signals
Risks include firmware fallback mistakes, handle leaks/collisions, accepting malformed decode messages, relocation buffers crossing 256MB boundaries, insufficient DPB checks, and clock-off while work is pending. Signals include UVD firmware version logs, CS parser rejections, UVD IB/ring tests, decode workload success, handle cleanup on file close/suspend, fence completion, and idle clock-down behavior after one second of inactivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_uvd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_vce.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_vce.c

## Purpose
`radeon_vce.c` manages the Video Coding Engine encoder block. It loads and validates supported VCE firmware versions, allocates firmware/heap BOs, tracks encoding session handles, validates VCE command streams, emits VCE-specific ring packets, and provides ring/IB tests.

## Important APIs, types, and functions
Lifecycle functions are `radeon_vce_init`, `radeon_vce_fini`, `radeon_vce_suspend`, and `radeon_vce_resume`. Runtime power/session helpers are `radeon_vce_note_usage`, `radeon_vce_idle_work_handler`, and `radeon_vce_free_handles`. Test/session IB helpers are `radeon_vce_get_create_msg` and `radeon_vce_get_destroy_msg`. CS validation uses `radeon_vce_cs_parse`, `radeon_vce_validate_handle`, and `radeon_vce_cs_reloc`. Ring integration uses `radeon_vce_semaphore_emit`, `radeon_vce_ib_execute`, `radeon_vce_fence_emit`, `radeon_vce_ring_test`, and `radeon_vce_ib_test`.

## Control flow
Init selects Tahiti or Bonaire firmware by family, loads the blob, scans it for firmware and feedback version strings, rejects unsupported firmware versions, allocates/pins a VRAM VCPU BO sized by VCE generation, and clears handle slots. Resume maps the BO, zeroes it, and either calls the v1.0 firmware loader or copies the firmware directly. Suspend refuses to proceed if encoding sessions are active. Command parsing walks length-prefixed VCE commands, requires a session command before meaningful work, allocates or validates session handles, requires a create command for newly allocated handles, patches/validates relocations for encode/context/bitstream/feedback buffers, forbids commands after destroy, and frees handles on destroy or error after allocation.

## State, dependencies, and integration points
State resides in `rdev->vce`: firmware pointer/version, feedback version, VCPU BO/GPU address, atomic handles, owning DRM files, image sizes, and idle work. It depends on Radeon BO, IB, fence, ring, semaphore, PM/DPM, firmware, ASIC VCE helpers, and command-submission parser structures. It integrates with ring tests and `radeon_test.c` through dummy create/destroy messages.

## Risks and test signals
Risks include fragile firmware string scanning, unsupported active-session suspend, handle collisions, buffer-size under-validation, wrong endian packet emission, and clock gating while fences remain. Test signals include firmware version logs, parser rejection of malformed IBs, VCE ring pointer movement, create/destroy IB fence completion, encoder workload success, and handle cleanup on file close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_vce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_vm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_vm.c

## Purpose
`radeon_vm.c` implements Radeon GPU virtual memory for Cayman and newer hardware. It manages VM manager enablement, VMID allocation/reuse, page-directory and page-table BOs, BO virtual-address mappings, PTE/PDE updates through the DMA ring, invalidation/freed lists, and VM teardown.

## Important APIs, types, and functions
Manager functions are `radeon_vm_manager_init` and `radeon_vm_manager_fini`. Per-VM lifecycle uses `radeon_vm_init` and `radeon_vm_fini`. Submission integration uses `radeon_vm_get_bos`, `radeon_vm_grab_id`, `radeon_vm_flush`, and `radeon_vm_fence`. BO mapping uses `radeon_vm_bo_find`, `radeon_vm_bo_add`, `radeon_vm_bo_set_addr`, `radeon_vm_bo_update`, `radeon_vm_bo_rmv`, `radeon_vm_bo_invalidate`, `radeon_vm_clear_freed`, and `radeon_vm_clear_invalids`. Internal update helpers include `radeon_vm_set_pages`, `radeon_vm_clear_bo`, `radeon_vm_update_page_directory`, `radeon_vm_frag_ptes`, `radeon_vm_update_ptes`, and `radeon_vm_fence_pts`.

## Control flow
VM init allocates a page-table pointer array and a cleared VRAM page directory. Mapping a BO validates address bounds and interval-tree overlap, clones old mappings to the freed list when remapping, inserts new ranges into the VM interval tree, grows `max_pde_used`, and lazily allocates/clears required page-table BOs. Page-directory updates coalesce contiguous PDE writes into one DMA IB. BO updates choose valid/system/snooped/writeable flags from TTM placement and userptr read-only state, sync against page-table reservations, emit PTE writes/copies/sets, pad and schedule the DMA IB, mark the fence as a VM update, and fence touched page tables. VMID allocation skips VMID 0, prefers free IDs, otherwise chooses the earliest active fence with preference for the same ring.

## State, dependencies, and integration points
Persistent state is split among `rdev->vm_manager`, per-VM page directory/tables, per-ring VM IDs, interval trees, invalidated/freed/cleared status lists, fences, and BO `va` lists. Dependencies include Radeon BO/TTM, DMA reservations, fences, IB scheduling, GART, ASIC VM callbacks, interval trees, mutexes/spinlocks, and tracepoints. Command submission uses this file to validate VM BOs and flush page directories before executing IBs.

## Risks and test signals
Risks include address-overlap bugs, stale PTEs after unmap/invalidate, missing sync to VMID last use when clearing invalid mappings, page-table BO allocation races, DMA IB size underestimation, and fragment PTE flags on non-contiguous system pages. Signals include VM tracepoints, GPU page-fault absence, command submission under remap/unmap stress, userptr readonly mapping behavior, VMID reuse ordering, and clean VM teardown with no active BO warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs100d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs100d.h

## Purpose
`rs100d.h` is a small register-definition header for RS100 northbridge top-of-memory programming. It defines the `NB_TOM` register and bitfield helpers used to describe framebuffer start/top positions.

## Important APIs, types, and definitions
The file defines `R_00015C_NB_TOM` and field macros `S_00015C_MC_FB_START`, `G_00015C_MC_FB_START`, `C_00015C_MC_FB_START`, `S_00015C_MC_FB_TOP`, `G_00015C_MC_FB_TOP`, and `C_00015C_MC_FB_TOP`.

## Control flow
There is no executable logic. Consumers use the macros to pack or extract 16-bit framebuffer base/top fields from a 32-bit register value.

## State, dependencies, and integration points
The header owns no state; the hardware register stores memory-controller configuration. It is part of the same register macro style as RS400/RS600 definition headers and integrates with ASIC memory-controller initialization code that locates VRAM on integrated chipsets.

## Risks and test signals
Incorrect masks or shifts would misplace VRAM in the memory map, causing boot-time memory-controller failures or corrupted framebuffer access. Test signals are correct VRAM size/location detection and stable modeset/BO access on RS100-family hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs100d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs400.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs400.c

## Purpose
`rs400.c` contains RS400/RS480 and related integrated-GPU ASIC support. It programs the integrated PCIe GART, memory controller, GPU pipe setup, startup/resume/suspend/fini sequences, debugfs GART state, and indirect MC register access.

## Important APIs, types, and functions
GART functions include `rs400_gart_adjust_size`, `rs400_gart_init`, `rs400_gart_enable`, `rs400_gart_disable`, `rs400_gart_fini`, `rs400_gart_tlb_flush`, `rs400_gart_get_page_entry`, and `rs400_gart_set_page`. MC/GPU helpers are `rs400_mc_wait_for_idle`, `rs400_gpu_init`, `rs400_mc_init`, `rs400_mc_rreg`, `rs400_mc_wreg`, and `rs400_mc_program`. Device lifecycle uses `rs400_init`, `rs400_startup`, `rs400_resume`, `rs400_suspend`, and `rs400_fini`. Debugfs exposes `rs400_debugfs_gart_info_show`.

## Control flow
Init disables VGA rendering, initializes scratch/surface defaults, restores sanity registers, requires COMBIOS, resets/tests posting, initializes clocks and MC layout, starts fence/BO/GART systems, sets safe registers, initializes PM, then calls startup. Startup programs MC, starts clocks, initializes GPU pipes through `r300_gpu_init`, enables bus mastering and GART, initializes writeback, starts GFX fences, installs/enables IRQs, initializes CP and IB pool. Resume disables GART, restarts clocks, programs MC, resets/posts, reinitializes surfaces, and reruns startup. Suspend disables PM, CP, writeback, IRQ, and GART. Fini unwinds PM, CP, WB, IB, GEM, GART, IRQ, fences, BOs, BIOS, and allocated BIOS memory.

## State, dependencies, and integration points
Persistent state includes `rdev->mc`, `rdev->gart`, CP/ring/fence/writeback state, BIOS state, PM state, and debugfs files. It depends on `rs400d.h`, R100/R300/R420 helpers, COMBIOS, Radeon GART/BO/IRQ/fence/IB/PM infrastructure, and MC indirect access protected by `mc_idx_lock`.

## Risks and test signals
Risks include unsupported GTT sizes, wrong GART table address packing, RS690/RS740 register-path divergence, MC programming while clients are active, and fragile reset/post ordering. Test signals include successful probe on RS400/RS480, GART debugfs register dumps, BO allocation through GTT, CP/ring/fence tests, suspend/resume, and absence of HyperZ/pipe glitches noted by the code comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs400.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs400d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs400d.h

## Purpose
`rs400d.h` defines RS400 register addresses and bitfield macros used by the RS400 ASIC implementation. It covers framebuffer location, northbridge top-of-memory, CP status, and RBBM status bits.

## Important APIs, types, and definitions
Key registers are `R_000148_MC_FB_LOCATION`, `R_00015C_NB_TOM`, `R_0007C0_CP_STAT`, and `R_000E40_RBBM_STATUS`. Field helpers encode/decode framebuffer start/top, CP sub-block busy state, command-stream busy state, GUI DMA/video DMA busy flags, command processor busy, command FIFO availability, and numerous 2D/3D/render/backend busy bits.

## Control flow
There is no executable flow. `rs400.c` and reset/debug paths use these macros to program memory-controller framebuffer ranges and to report/reset GPU/CP status.

## State, dependencies, and integration points
The header owns no state; it names hardware register state. It integrates with MMIO accessors such as `RREG32`/`WREG32`, MC programming, reset diagnostics, and post/reset failure logging. The macro style matches generated Radeon register headers, with `S_` setters, `G_` getters, and `C_` clear masks.

## Risks and test signals
Bad register definitions would break MC framebuffer mapping or misread GPU busy/idle conditions, which can lead to unsafe reset decisions or misleading diagnostics. Test signals are correct RS400 probe, sane reset logs, successful MC programming, and reliable CP/RBBM status interpretation during hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs400d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs600.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs600.c

## Purpose
`rs600.c` implements RS600/Radeon X1250/X1270 integrated-GPU support. It combines AVIVO display helpers, page flipping, display format programming, power-management register updates, HPD/IRQ handling, GPU reset, R600-like GART programming, memory-controller setup, bandwidth updates, and full ASIC lifecycle.

## Important APIs, types, and functions
Display functions include `avivo_wait_for_vblank`, `rs600_page_flip`, `rs600_page_flip_pending`, and `avivo_program_fmt`. PM hooks are `rs600_pm_misc`, `rs600_pm_prepare`, and `rs600_pm_finish`. HPD/IRQ functions include `rs600_hpd_sense`, `rs600_hpd_set_polarity`, `rs600_hpd_init`, `rs600_hpd_fini`, `rs600_irq_set`, `rs600_irq_disable`, `rs600_irq_process`, and `rs600_get_vblank_counter`. GART functions include `rs600_gart_tlb_flush`, `rs600_gart_get_page_entry`, and `rs600_gart_set_page`, with static init/enable/disable/fini helpers. Lifecycle functions are `rs600_init`, `rs600_startup`, `rs600_resume`, `rs600_suspend`, and `rs600_fini`.

## Control flow
Init disables VGA, initializes scratch/surface/default registers, requires ATOM BIOS, resets/tests posting, reads clocks and MC layout, initializes debugfs/fence/BO/GART/safe-register/PM state, then starts acceleration. Startup programs MC, starts clocks, initializes pipes, enables GART, writeback, GFX fences, IRQs, CP, IB pool, and audio. IRQ processing acknowledges display, HPD, HDMI, and software interrupts, processes fences/vblank/pageflips, queues hotplug/audio work, and rearms MSI. GART enable pins a VRAM table, programs PT0 client/context registers, sets flat base/start/end, maps the system aperture to VRAM, enables page tables, and flushes TLBs. Reset stops MC clients, halts CP, clears ring pointers, disables bus mastering, soft-resets VAP/GA, CP, and MC, restores PCI state, and checks busy bits.

## State, dependencies, and integration points
State spans `rdev->mc`, `rdev->gart`, display CRTCs/connectors, IRQ status registers, PM power states, audio work, CP/ring/fence/writeback/IB, ATOM BIOS, and debugfs. Dependencies include AVIVO/DCE register definitions, ATOM BIOS, R100/R420/RV515 helpers, RS600 safe-register tables, Radeon audio, DRM vblank, PCI state APIs, and MC indirect access under `mc_idx_lock`.

## Risks and test signals
Risks include page-table register misprogramming, IRQ ack races, MSI rearm quirks, unsafe reset delays, HPD polarity mistakes, display underruns during PM changes, and GART table unpinning while active. Test signals include modeset/pageflip/vblank tests, HPD and HDMI audio interrupts, GTT BO access, CP/ring/fence tests, audio init, suspend/resume, reset recovery, and bandwidth/display-priority behavior under dual CRTC load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs600.c -->
