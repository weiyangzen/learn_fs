# Research: subset-b-001323

This grouped report covers the AMDGPU user queue, video engine, SR-IOV virtualization, and VF error files listed for `subset-b-001323`. Each source file section is bounded by the required reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq.h

## Purpose

`amdgpu_userq.h` defines the public in-driver contract for AMDGPU user-mode queues. User queues let a DRM file/process own queue state directly while the kernel still manages object allocation, doorbells, VM validation, reset/suspend/resume hooks, eviction fences, hang detection, and synchronization integration. The header is a coordination point between user queue IOCTL handling, hardware-specific MQD programming, eviction fencing, and the `amdgpu_userq_fence` bridge.

## Important APIs, Types, And Data

The main state machine is `enum amdgpu_userq_state`: unmapped, mapped, preempted, hung, and invalid-VA. `struct amdgpu_userq_obj` wraps CPU pointer, GPU address, and backing BO for objects such as MQD, doorbell, firmware, and wptr storage. `struct amdgpu_userq_va_cursor` records GPU VAs that are relevant to validation and unmap detection.

`struct amdgpu_usermode_queue` is the per-queue object. It stores queue type, state, doorbell handle/index, queue flags, MQD properties, VM pointer, four queue-owned objects, `fence_drv` state, the last user queue fence, XCP id, priority, debugfs node, hang-detection delayed work, refcount, and a list of tracked VAs. It also owns `fence_drv_lock` and `fence_drv_xa`, which protect references to external fence drivers discovered by wait IOCTLs until the next signaled fence or queue destruction.

`struct amdgpu_userq_funcs` is the hardware abstraction for creating/updating/destroying MQDs, map/unmap, preempt/restore, and detect/reset. `struct amdgpu_userq_mgr` is a per-DRM-file manager with an xarray of queue ids, a mutex, the device, resume work, file pointer, and per-ring-type queue counts. `struct amdgpu_db_info` carries doorbell resolution inputs.

Exports include queue lookup/refcounting (`amdgpu_userq_get/put`), the userq IOCTL, manager init/fini/cancel, BO object create/destroy, eviction fence maintenance, doorbell lookup, supported IP mask checks, suspend/resume, reset pre/post hooks, scheduler isolation hooks, hang detection work, fence IRQ processing, and VA validation helpers.

## Control Flow And Integration

The header shows the lifecycle shape: a file initializes `amdgpu_userq_mgr`, user IOCTLs create/map queues through hardware-specific `amdgpu_userq_funcs`, GPU work is tracked through `amdgpu_userq_fence_driver`, and teardown cancels resume/hang work, releases queue BOs, and drains fence references. Reset paths call `amdgpu_userq_pre_reset`, `amdgpu_userq_post_reset`, and `amdgpu_userq_reset_work`; isolation paths stop/start schedulers by index. VM integration is explicit through `amdgpu_userq_input_va_validate` and `amdgpu_userq_gem_va_unmap_validate`, which prevent stale queue pointers after GEM VA changes.

Dependencies include `amdgpu_eviction_fence.h`, DRM file/device types, AMDGPU VM and BO types, xarray, workqueues, debugfs, and dma-fence. The queue manager is embedded in `amdgpu_fpriv`, and the helper macros expose that relationship.

## State, Persistence, Risks, And Tests

State is in-memory and per-process: xarray queue maps, queue refcounts, delayed work, object GPU mappings, and fence-driver references. GPU-visible persistence is through BOs and doorbells; reset/suspend code must restore or invalidate it. Important risks are lifetime races between queue destruction, hang/reset work, fence IRQ completion, and wait IOCTL external fence references; stale VM addresses after unmap; queue count leaks; and inconsistent queue state transitions during reset or isolation.

Test signals include user queue create/map/unmap/preempt/restore IOCTL coverage, VM unmap invalidation, reset with active queues, suspend/resume with active and idle queues, hang detection, eviction fence behavior, doorbell allocation, supported IP mask gating, and stress tests for many queues up to `AMDGPU_MAX_USERQ_COUNT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq_fence.c

## Purpose

`amdgpu_userq_fence.c` bridges user-mode queue progress into the Linux `dma_fence`, DRM syncobj, and BO reservation model. User queues expose progress through GPU-written seq64 memory. This file allocates that seq64 memory, creates dma-fences whose sequence numbers are queue write pointers, publishes those fences to BO reservations and syncobjs, and returns wait metadata so another user queue can wait on AMDGPU user queue fences by polling GPU VAs.

## Important APIs And Functions

`amdgpu_userq_fence_driver_alloc()` allocates `struct amdgpu_userq_fence_driver`, seq64 memory via `amdgpu_seq64_alloc`, a dma-fence context, timeline name, refcount, and the fence list lock. `amdgpu_userq_fence_driver_destroy()` cancels and signals remaining fences with `-ECANCELED`, frees seq64 memory, and releases the driver. `amdgpu_userq_fence_driver_get/put()` wrap kref lifetime.

`amdgpu_userq_fence_driver_process()` reads the seq64 value, cuts all pending fences whose `seqno <= rptr` into a temporary list, signals them, drops their retained external fence driver arrays, and releases the fence references. `amdgpu_userq_fence_driver_force_completion()` marks the latest queue fence canceled, writes its seqno into seq64 memory, and processes the list.

`amdgpu_userq_fence_alloc()` allocates a fence and drains `userq->fence_drv_xa` into `fence_drv_array`, taking references to external fence drivers. This prevents wait-created dependencies from accumulating indefinitely in the queue and makes the new fence responsible for releasing them when it signals. `amdgpu_userq_fence_init()` initializes `dma_fence`, updates `last_fence`, puts it on the driver's pending list if not already signaled, and starts hang detection.

`amdgpu_userq_signal_ioctl()` looks up syncobjs, BO read/write handles, and the target queue; reads the queue wptr from the queue's VM mapping; creates a userq dma-fence; locks BO reservations with `drm_exec`; adds read/write fences to BO reservation objects; and replaces the requested syncobjs. `amdgpu_userq_wait_ioctl()` either counts relevant fences or returns an array of GPU VA/value pairs for AMDGPU userq fences, falling back to blocking waits on non-userq fences.

## Control Flow And State

Signal flow is: validate feature and handle counts, duplicate user arrays, look up objects, get queue, read wptr, create fence, release queue-manager mutex, lock BO reservations, publish fence, and unwind references. Wait flow is two-phase: with `num_fences == 0`, it counts syncobj and BO reservation fences so userspace can size a buffer; with a nonzero count, it gathers fences, deduplicates them, finds userq fences, stores their fence-driver references in the wait queue xarray, and copies `va/value` pairs to userspace.

Persistent state is in-memory plus GPU-visible seq64 memory. Each fence driver owns seq64 CPU/GPU/VA addresses and a pending fence list. Each queue owns a primary fence driver, a temporary xarray of external fence drivers, and `last_fence`. BO reservations and syncobjs receive fence references that outlive the IOCTL.

## Dependencies And Integration

The file integrates with `amdgpu_userq.h`, `amdgpu_seq64`, AMDGPU VM/BO lookup, `drm_exec`, GEM object lookup, DRM syncobj APIs, dma-resv, dma-fence unwrap/dedup helpers, xarray, RCU fence release, and user-copy helpers. It relies on the queue manager's `userq_mutex` being held by `amdgpu_userq_get()` paths and explicitly unlocks it after fence initialization.

## Risks And Test Signals

Important risks include fence-driver lifetime bugs, xarray draining errors, incorrect use of `xas_find_marked` when no free mark is available, lock ordering between queue mutexes, BO reservations, and fence list locks, user pointer/count overflow, blocking waits on non-AMDGPU fences, stale wptr mappings, and lost completion if seq64 memory is freed too early. The code also caps handle arrays at `1 << 16` but needs tests for zero, max, and malicious counts.

Test signals should cover signal IOCTL with read/write BOs and syncobjs, wait IOCTL count and return modes, timeline syncobj unwrapping, non-userq fence fallback waits, queue destruction with pending waits, forced completion on reset, concurrent signal/wait/destruction, invalid user pointers, missing queue ids, wptr BO mapping failures, fence IRQ processing, and stress with many external fence drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq_fence.h

## Purpose

`amdgpu_userq_fence.h` declares the data structures and entry points for the user queue fence subsystem. It is the header consumed by queue lifecycle code, IOCTL dispatch, reset paths, and fence IRQ handling to allocate, process, force-complete, and publish user queue synchronization.

## Important Types And APIs

`struct amdgpu_userq_fence` embeds `struct dma_fence` as `base`, a spinlock required by dma-fence operations, a list link for the driver's pending-fence list, and an array of retained `amdgpu_userq_fence_driver` pointers. That array carries external userq fence-driver dependencies returned by wait IOCTLs so they can be released when the next queue fence is signaled.

`struct amdgpu_userq_fence_driver` owns the seq64 progress memory (`va`, `gpu_addr`, `cpu_addr`), a dma-fence context, `fence_list_lock`, the list of pending fences, the AMDGPU device pointer, a kref, and a task-derived timeline name. It is the per-queue object that turns a GPU-written sequence value into dma-fence completion.

The exported functions are lifetime helpers (`amdgpu_userq_fence_driver_alloc/free/get/put/destroy`), progress helpers (`amdgpu_userq_fence_driver_process`, `amdgpu_userq_fence_driver_force_completion`), and IOCTL entry points (`amdgpu_userq_signal_ioctl`, `amdgpu_userq_wait_ioctl`).

## Control Flow And Integration

The header reflects a split between per-queue fence-driver state and per-fence objects. Queue creation allocates a fence driver. User signal creates fences and publishes them to reservations/syncobjs. Fence IRQ or forced reset paths process or complete the driver. Queue teardown frees the driver and drops any wait-derived driver references.

Dependencies include Linux `types.h`, dma-fence structures through included AMDGPU headers, `amdgpu_userq.h`, xarray ownership from `struct amdgpu_usermode_queue`, and DRM IOCTL dispatch types. The header is intentionally small but sits on a high-risk boundary between userspace synchronization ABI and kernel fence lifetime rules.

## State, Risks, And Tests

State is not persistent across driver lifetime; it is GPU-visible through seq64 memory and kernel-visible through lists/refcounts. Risks are mostly lifetime and lock-rule related: dangling fence-driver pointers, missed kref drops, fence list corruption, and forced completion racing normal signaling. Test signals should include allocation/free failure paths, queue destruction with pending fences, repeated wait/signal cycles that create external driver arrays, reset cancellation, and dma-fence callback/wait correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq_fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_utils.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_utils.h

## Purpose

`amdgpu_utils.h` provides a generic macro framework for declaring small capability classes whose capabilities have two-bit access attributes: invalid, read-only, write-only, or read-write. In this subset it is used by virtualization capability declarations in `amdgpu_virt.h`, but the macros are generic for any AMDGPU subsystem that wants compact capability metadata.

## Important APIs And Types

`enum amdgpu_cap_attr` defines the encoded values: `AMDGPU_CAP_ATTR_INVALID`, `AMDGPU_CAP_ATTR_RO`, `AMDGPU_CAP_ATTR_WO`, and `AMDGPU_CAP_ATTR_RW`. `AMDGPU_CAP_ATTR_BITS` fixes the storage width at two bits and `AMDGPU_CAP_ATTR_MAX` bounds validation.

`DECLARE_ATTR_CAP_CLASS(NAME, LIST_MACRO)` is the public macro. It expands an X-macro list into `enum NAME_cap_id { ... NAME_COUNT }` and then emits helpers via `DECLARE_ATTR_CAP_CLASS_HELPERS(NAME)`. The helpers define `struct NAME_caps` with a bitmap sized to `NAME_COUNT * 2`, `NAME_attr_init()`, `NAME_attr_set()`, `NAME_attr_get()`, and convenience predicates `NAME_cap_is_ro/wo/rw()`.

The implementation uses kernel bitmap helpers `bitmap_zero`, `bitmap_write`, and `bitmap_read`. It validates null pointers, out-of-range capability ids, and attributes wider than the two-bit field, returning `-EINVAL` on invalid inputs.

## Control Flow, State, And Integration

Callers define a list macro such as `AMDGPU_VIRT_CAPS_LIST(X)`, invoke `DECLARE_ATTR_CAP_CLASS(amdgpu_virt, AMDGPU_VIRT_CAPS_LIST)`, initialize a caps object, then set or query per-capability access attributes. The state is a compact bitmap embedded in the caller's object; there is no allocation, locking, persistence, or IO.

This header depends on bitmap APIs and error constants being available through includers. It integrates with any subsystem that needs generated capability enums plus consistent accessors without duplicating boilerplate.

## Risks And Test Signals

Risks are macro-related: namespace collisions, passing a non-enum value, forgetting to initialize the bitmap, using capability lists with too many entries for expected storage, or assuming these helpers are atomic. The code does not lock, so concurrent set/get requires caller-side synchronization if the capability object is mutable.

Test signals can be simple compile-time users plus unit-style checks: generated enum count, init zeroes all attributes, set/get each legal attribute, invalid cap id returns `-EINVAL`, invalid attribute value returns `-EINVAL`, null input handling, and predicate correctness for RO/WO/RW/invalid values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_uvd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_uvd.c

## Purpose

`amdgpu_uvd.c` implements legacy UVD video decode support: firmware selection/loading, firmware BO allocation, suspend/resume save and restore, per-file decode handle tracking, command submission validation/patching, kernel-generated create/destroy messages, power management, and IB self-tests. It covers pre-VCN decode hardware and compatibility quirks such as 256 MB address segment restrictions on older chips.

## Important APIs And Functions

`amdgpu_uvd_sw_init()` selects firmware by ASIC, requests and validates it, derives firmware version and maximum session handles, allocates per-instance VCPU BOs, initializes handle slots, determines 64-bit address support and context-buffer support, and allocates a shared message IB BO. `amdgpu_uvd_sw_fini()` destroys the scheduler entity, frees saved VCPU snapshots, VCPU BOs, rings, message BO, and firmware.

`amdgpu_uvd_prepare_suspend()`, `amdgpu_uvd_suspend()`, and `amdgpu_uvd_resume()` handle VCPU BO preservation. Resume either restores saved BO contents or reloads firmware/zeros the rest and forces ring fence completion. RAS ATHUB events and DPC recovery are treated specially because they can corrupt VCPU memory.

The CS parser is built around `struct amdgpu_uvd_cs_ctx`. `amdgpu_uvd_cs_packets()` walks packet0/type2 command streams. `amdgpu_uvd_cs_pass1()` validates/forces buffer placement for older non-64-bit UVD. `amdgpu_uvd_cs_pass2()` patches virtual addresses to real GPU offsets, enforces buffer sizes, 256 MB segment limits, valid command ids, and message-before-other-command ordering. `amdgpu_uvd_cs_msg()` validates create/decode/destroy messages and per-file handles. `amdgpu_uvd_cs_msg_decode()` computes minimum DPB/image/context sizes for H264, VC1, MPEG2, MPEG4, MJPEG, and H265.

`amdgpu_uvd_get_create_msg()` and `amdgpu_uvd_get_destroy_msg()` synthesize firmware messages for ring tests and cleanup, then submit through `amdgpu_uvd_send_msg()`. `amdgpu_uvd_ring_begin_use/end_use()` ungate/gate clocks and power with delayed idle work. `amdgpu_uvd_ring_test_ib()` validates IB execution. `amdgpu_uvd_used_handles()` counts active sessions.

## Dependencies And Integration

The file depends on firmware loading, AMDGPU BO/TTM placement, VM mapping lookup, CS parsing, ring/job submission, scheduler entities, dma-fence, RAS state, DPM/powergating, and hardware register packet definitions from `cikd.h` and `uvd_4_2_d.h`. It integrates with file close through `amdgpu_uvd_free_handles()` and with ring setup through `amdgpu_uvd_entity_init()`.

## State, Risks, And Tests

Persistent runtime state lives in `adev->uvd`: firmware pointer/version, max handles, per-instance VCPU BOs, message BO, atomic handle array plus owning `drm_file`, idle work, context-buffer mode, and decode image width. Risks include malformed command streams causing out-of-bounds reads if length checks miss a case, integer overflow or divide-by-zero in decode-size math for invalid dimensions, handle leaks/collisions across files, BO placement failures, stale saved BOs after reset, and powergating races around active fences.

Test signals include firmware selection for each supported ASIC, old/new firmware version handling, CS parser rejection of invalid packet types/registers/commands/alignment, decode message buffer-size validation, create/decode/destroy handle transitions, file-close cleanup, suspend/resume with active and inactive sessions, RAS-triggered resume behavior, 256 MB segment crossing tests, idle clock gating, and ring/IB self-tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_uvd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_uvd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_uvd.h

## Purpose

`amdgpu_uvd.h` declares the shared data model and entry points for legacy UVD decode support. It defines firmware memory sizing, instance limits, harvest flags, per-instance resources, global UVD state, and the lifecycle/parser/test APIs consumed by UVD IP block implementations and common AMDGPU paths.

## Important Types And APIs

The header sets default and maximum decode handles (`10` and `40`), stack/heap/session sizes, firmware offset, and maximum UVD instances. `AMDGPU_UVD_FIRMWARE_SIZE(adev)` computes aligned firmware payload size from the common firmware header.

`struct amdgpu_uvd_inst` contains the VCPU BO, CPU/GPU addresses, saved BO copy, decode ring, encode rings associated with UVD-era blocks, IRQ source, and soft reset register state. `struct amdgpu_uvd` stores firmware pointer/version, max handles, number of encode rings and UVD instances, address-mode/context-buffer flags, per-instance array, per-handle owning DRM file and atomic handle value, scheduler entity, idle work, harvest config, decode image width, keyselect, and shared message IB BO.

Exported functions cover software init/fini, scheduler entity init, suspend/resume, kernel create/destroy messages, handle cleanup on file close, CS parsing, ring power begin/end hooks, IB testing, and active handle counting.

## Control Flow And Integration

The header supports the common lifecycle: firmware and BO allocation during software init, ring/entity setup by hardware IP code, CS parser use during job submission, per-file handle cleanup on close, suspend/resume preservation, and delayed idle power management. It integrates with `amdgpu_cs_parser`, `amdgpu_job`, `amdgpu_ring`, dma-fence, DRM file ownership, and AMDGPU firmware headers.

## State, Risks, And Tests

State is concentrated in `adev->uvd` and is reset/suspend sensitive. The handle arrays are per-device but owner-tagged by `drm_file`; tests must verify ownership isolation and cleanup. Risks are stale firmware pointers, wrong BO sizing after firmware format changes, harvested instance handling, mismatched max handle assumptions between firmware and driver, and parser/test callers using uninitialized rings.

Test signals include structure initialization defaults, harvested instance skip logic, handle count boundaries, firmware BO sizing, ring entity init only on the primary decode ring, and API behavior when firmware or VCPU BO is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_uvd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vce.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vce.c

## Purpose

`amdgpu_vce.c` implements legacy VCE video encode support. It loads chip-specific firmware, allocates the firmware/VCPU BO, tracks encode sessions per DRM file, validates and patches VCE command streams, submits kernel-generated create/destroy messages, emits VCE ring commands, handles idle power gating, and runs ring/IB tests.

## Important APIs And Functions

`amdgpu_vce_firmware_name()` maps ASICs to firmware filenames. `amdgpu_vce_early_init()` requests firmware and decodes version fields. `amdgpu_vce_sw_init()` allocates the VCPU BO, initializes handle ownership arrays, delayed idle work, and idle mutex. `amdgpu_vce_sw_fini()` tears down scheduler entity, rings, firmware, mutex, and BO. `amdgpu_vce_suspend()` refuses suspend when active handles exist because running encode sessions cannot be preserved; `amdgpu_vce_resume()` zeros and reloads firmware into the BO.

Handle and cleanup helpers include `amdgpu_vce_validate_handle()` and `amdgpu_vce_free_handles()`. The kernel message helpers `amdgpu_vce_get_create_msg()` and `amdgpu_vce_get_destroy_msg()` build direct or delayed IBs with session, task, feedback, initialize, or destroy commands.

The parser has two modes. `amdgpu_vce_ring_parse_cs()` validates command lengths, checks and constrains referenced BO placement with `amdgpu_vce_validate_bo()`, then relocates addresses with `amdgpu_vce_cs_reloc()`, enforces session-first ordering, create-before-use for new handles, destroy semantics, and ASIC-specific command acceptance. `amdgpu_vce_ring_parse_cs_vm()` performs the lighter VM-mode handle/session validation without reloc patching.

Ring helpers emit IB and fence packets (`amdgpu_vce_ring_emit_ib`, `amdgpu_vce_ring_emit_fence`), test ring pointer movement, test IB execution through create/destroy messages, and map encode rings to scheduler priorities.

## Dependencies And Integration

The file integrates with firmware loading, AMDGPU BO/TTM placement, CS parser and IB helpers, DRM scheduler entity, dma-fence, ring submission, DPM/powergating, SR-IOV skip behavior, and common command definitions from `amdgpu_vce.h`/`cikd.h`. File-close cleanup is necessary because hardware sessions outlive individual submissions unless explicitly destroyed.

## State, Risks, And Tests

Device state lives in `adev->vce`: firmware, VCPU BO, atomic handle array, owner file array, image size per session, delayed idle work, ring array, scheduler entity, harvest config, and keyselect. Risks include command length under-validation before reading `idx + n`, handle leaks or collisions across files, freeing allocated handles on parser error but not clearing owner/image metadata, BO relocation crossing 4 GB boundaries, suspend failure with active sessions, and idle power gating while fences are still pending.

Test signals include firmware lookup and missing-firmware fallback, parser rejection of bad command lengths/order/opcodes, create/destroy state transitions, VM parser behavior, cross-file handle collision, BO too-small and boundary cases, cleanup on file close, ring emit packet shape, SR-IOV ring-test skip, idle begin/end behavior, and active-session suspend rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vce.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vce.h

## Purpose

`amdgpu_vce.h` declares the shared VCE encoder state and public helper APIs for legacy AMD video encode blocks. It is consumed by VCE hardware IP implementations, command submission, file cleanup, power management, and ring setup code.

## Important Types And APIs

The header defines `AMDGPU_MAX_VCE_HANDLES` as 16, the firmware offset, harvest flags for two VCE blocks, and a firmware version helper constant. `struct amdgpu_vce` holds the VCPU BO and addresses, optional saved BO pointer, firmware and feedback versions, per-session atomic handles, per-session owning `drm_file`, per-session image size, delayed idle work, idle mutex, firmware pointer, VCE rings, IRQ source, harvest config, scheduler entity, soft reset state, ring count, keyselect, and a GART node.

Exports cover early firmware init, software init/fini, scheduler entity init, suspend/resume, file-close handle cleanup, non-VM and VM command stream parsing, IB/fence ring emission, ring/IB tests, begin/end power-use hooks, ring sizing helpers, and priority mapping.

## Control Flow And Integration

The common flow is firmware load in early init, VCPU BO allocation in software init, ring/entity setup, CS parser enforcement during submissions, idle power management around ring use, and teardown on software fini. Handle ownership spans submissions, so close cleanup and parser rollback are key integration points.

Dependencies include `amdgpu_device`, `amdgpu_ring`, `amdgpu_job`, `amdgpu_cs_parser`, dma-fence, firmware, DRM file ownership, and power management. Several functions are implemented in `amdgpu_vce.c`; sizing helpers may be provided by IP-version-specific code.

## State, Risks, And Tests

State is per-device and mostly in-memory/GPU-BO backed. Risks include stale handles, mismatched ring counts, use of VCE APIs when firmware is absent, suspend attempts with live sessions, and incorrect image size state driving reloc validation. Test signals should cover init/fini idempotence, ring count boundaries, handle ownership isolation, parser entry points, and firmware/BO absent cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vcn.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vcn.c

## Purpose

`amdgpu_vcn.c` implements common support for modern VCN video decode/encode blocks: firmware lookup, BO/shared-memory setup, suspend/resume preservation, power profile and power gating coordination, decode/encode/unified ring tests, firmware log debugfs, scheduler-mask debugfs, RAS poison dispatch, SR-IOV-aware RAS handling, sysfs reset mask, per-instance engine reset, and IP state dumps.

## Important APIs And Functions

`amdgpu_vcn_early_init()` binds each VCN instance to firmware, supporting shared or per-instance firmware. `amdgpu_vcn_sw_init()` initializes per-instance mutexes, counters, idle work, DPG indirect SRAM mode, a Steam Deck BIOS quirk, unified queue selection for VCN4+, firmware version logging, VCPU BO sizing, firmware shared memory layout selection for VCN3/4/5, optional firmware log space, and optional DPG SRAM BO. `amdgpu_vcn_sw_fini()` releases DPG SRAM, saved BOs, VCPU BO, rings, firmware, register dump buffers, and mutexes.

Suspend/resume helpers save VCPU BOs unless RAS/DPC recovery requires a clean reload. `amdgpu_vcn_get_profile/put_profile()` toggle the video DPM power profile while any VCN instance is ungated. `amdgpu_vcn_ring_begin_use/end_use()` maintain submission counters, cancel/schedule idle work, transition power state, and pause/unpause DPG for pre-unified queue engines.

Ring tests include direct decode register writes, software decode ring END packets, decode message IBs, software decode buffer IBs, encode initialize/close-session messages, and unified queue tests that combine encode/decode paths depending on IP version. `amdgpu_vcn_unified_ring_ib_header()` and checksum helpers build the single-queue packet wrapper.

RAS/debug interfaces include `amdgpu_vcn_process_poison_irq()`, `amdgpu_vcn_ras_sw_init()`, `amdgpu_vcn_ras_late_init()`, `amdgpu_vcn_psp_update_sram()`, firmware log init/read debugfs, VCN scheduler mask debugfs, reset mask sysfs, and register dump init/dump/print. `amdgpu_vcn_ring_reset()` resets whole VCN instances for non-unified queues by stopping schedulers, invoking the IP reset callback, retesting rings, forcing fence completion, and restarting schedulers.

## Dependencies And Integration

The file depends on firmware loading, AMDGPU BO/IB/job/ring APIs, DRM scheduler, DPM power profiles, IP version helpers, PSP firmware loading, debugfs, sysfs, RAS core, reset domains, and SR-IOV virtualization callbacks. It is designed to be called by IP-version-specific VCN block code that fills register addresses, ring callbacks, reset callbacks, DPG callbacks, and RAS IRQ sources.

## State, Risks, And Tests

State is per VCN instance in `adev->vcn.inst[]`: firmware, VCPU BO, shared memory offsets, rings, IRQs, DPG SRAM, pause state, counters, mutexes, current power state, delayed idle work, firmware version, queue mode, and reset callback. Device-level state tracks instance masks, RAS, register dump buffers, supported reset mask, caps, and workload profile active state.

Risks include firmware shared layout mismatches across VCN generations, incorrect per-instance firmware release when firmware is shared, DPG pause races with encode submissions, idle power gating while counters or fences are active, debugfs log pointer validation errors, sysfs/debugfs updates racing ring scheduling, reset not restarting schedulers on failure paths, and SR-IOV poison handling when virtualization ops are absent.

Test signals include per-IP firmware naming, per-instance firmware mode, BO/shared memory sizing for VCN3/4/5, firmware log enable/read wraparound, begin/end power profile nesting, DPG pause behavior, encode/decode/unified ring tests, SR-IOV ring-test skips, RAS poison dispatch in PF and VF modes, sysfs reset mask creation/removal, scheduler mask debugfs set/get, per-instance reset failure paths, and register dump output for powered/unpowered instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vcn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vcn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vcn.h

## Purpose

`amdgpu_vcn.h` is the central VCN contract for modern AMD video decode/encode blocks. It defines command opcodes, DPG register access macros, firmware shared-memory layouts, per-instance and device-level state, RAS/debug structures, codec disable flags, ring types, and common lifecycle/test/RAS/reset APIs.

## Important Types And Data

The header defines VCN stack/context sizes, firmware offset, maximum encode rings and instances, harvest flags, decode/encode command ids, DPG LMA read/write macros for SOC15/SOC24, firmware shared capability flags, codec disable masks, SMU DPM interface ids, and DRM-key workaround constants.

`struct amdgpu_vcn_inst` is the main per-instance state: device/instance ids, VCPU BO, saved BO, decode and encode rings, scheduler score, IRQ and RAS poison IRQ sources, register mappings, DPG SRAM BO and cursor, pause state, firmware shared memory metadata, codec config, submission counters, power-gating locks/state, delayed idle work, firmware version, encode ring count, indirect SRAM flag, internal registers, workaround locks, callbacks for DPG pause/power/reset, unified-queue flag, and reset mutex.

`struct amdgpu_vcn` stores device-level instance count, instance array, harvest mask, RAS block pointers, instance masks, register dump buffer/list, supported reset mask, caps, firmware sharing mode, workload profile state, and register counts. Firmware shared structs describe VCN3, VCN4, and VCN5 memory contracts for queue modes, firmware logging, ring buffer setup, DRM key workaround, queue decoupling, RB metadata, decode buffers, and SMU interface data.

Exports include early/software init/fini, suspend/resume, ring begin/end, disabled-queue tests, decode/encode/unified ring tests, priority mapping, PSP SRAM update, firmware log/debugfs setup, RAS init/poison handling, sysfs/debugfs controls, powergating, ring reset, register dumps, and workload profile management.

## Control Flow And Integration

IP-version-specific code fills the register and callback fields, then common VCN code handles firmware memory, power transitions, tests, debugfs/sysfs, and RAS. The DPG macros are used by hardware blocks to access internal VCN registers while power-gated. Firmware shared-memory structs are written into the VCPU BO region and consumed by firmware, so layout compatibility is critical.

Dependencies include `amdgpu_ras.h`, AMDGPU register macros, BO/ring/job types, debugfs/sysfs, PSP firmware loading, reset logic, and DRM printer/debug infrastructure.

## State, Risks, And Tests

State is GPU-BO backed, firmware-shared, and per-instance. Risks include ABI drift in firmware shared structs, unbounded assumptions about instance/ring counts, incorrect harvest masking, callback null dereferences, DPG macro misuse, and debugfs/sysfs access after teardown. Test signals include build coverage for all macro users, struct layout validation against firmware expectations, init/fini across harvested instances, unified versus split queue behavior, codec disable masks, reset mask reporting, and RAS/debug paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vcn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vf_error.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vf_error.c

## Purpose

`amdgpu_vf_error.c` implements a small SR-IOV VF-side error log buffer and transmission path. It records VF error codes locally, then sends pending entries to the PF/GIM host through the virtualization mailbox operation `trans_msg` using `IDH_LOG_VF_ERROR`.

## Important APIs And Functions

`amdgpu_vf_error_put()` is the producer. It returns immediately outside SR-IOV VF mode, encodes the VF category plus sub-error through `AMDGIM_ERROR_CODE()`, locks `adev->virt.vf_errors.lock`, writes code/flags/data into a fixed-size ring slot selected by `write_count % AMDGPU_VF_ERROR_ENTRY_SIZE`, increments `write_count`, and unlocks.

`amdgpu_vf_error_trans_all()` is the consumer/transmitter. It validates the device, VF mode, virt ops, and `trans_msg` callback. It locks the buffer, clamps `read_count` forward if writes have overrun the fixed ring, then sends each pending entry as three mailbox data words: combined code/flags, low 32 bits of data, and high 32 bits of data. Each successful iteration increments `read_count`.

## Control Flow, State, And Integration

The buffer is embedded in `adev->virt.vf_errors` and protected by its mutex. The code intentionally keeps only the newest 16 entries if producers overrun consumers. Transmission is synchronous under the same lock and depends on the platform-specific virtualization ops installed by `amdgpu_virt_init()`.

Dependencies include `amdgpu.h`, `amdgpu_vf_error.h`, `mxgpu_ai.h` for mailbox request ids, and SR-IOV mode macros from virtualization headers.

## Risks And Test Signals

Risks include dropping old errors without per-entry accounting, holding the mutex while calling `trans_msg`, no retry/error return from transmission, integer growth of read/write counters over very long uptimes, and tight coupling to GIM enum values. Test signals should cover non-VF no-op behavior, ring overwrite clamping, mailbox data packing, concurrent producers, missing `virt.ops`, and transmission ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vf_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vf_error.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vf_error.h

## Purpose

`amdgpu_vf_error.h` declares the VF error ABI constants and functions used by SR-IOV virtual functions to report driver/GPU initialization and reset errors back to the host-side GIM/PF component.

## Important APIs And Types

`AMDGIM_ERROR_CODE_FLAGS_TO_MAILBOX(c, f)` packs a 16-bit error code and 16-bit flags into one mailbox dword. `AMDGIM_ERROR_CODE(t, c)` packs a 4-bit category and 12-bit sub-error into a 16-bit code.

`enum AMDGIM_ERROR_VF` lists VF sub-errors such as ATOMBIOS init failure, missing VBIOS, GPU post error, clock query failure, fence init failure, driver init/IB/late-init failure, ASIC resume failure, GPU reset failure, and test. The comment requires the enum to stay in sync with the AMD GIM driver. `enum AMDGIM_ERROR_CATEGORY` defines GIM/PF/VF/VBIOS/monitor categories.

The exported functions are `amdgpu_vf_error_put()` and `amdgpu_vf_error_trans_all()`.

## Control Flow And Integration

Callers record VF errors with a category-specific sub-error, flags, and 64-bit data. Later, the transmit function drains pending records through the virtualization mailbox. The data buffer and lock are declared in `amdgpu_virt.h` as part of `struct amdgpu_vf_error_buffer`.

## State, Risks, And Tests

The header itself stores no state but defines an inter-component ABI. Risks include enum drift from GIM, incompatible packing assumptions, and insufficient category/code width for new errors. Test signals include compile-time checks for expected enum values where possible, mailbox packing tests, and integration tests that verify host-side decode of VF error reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vf_error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_virt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_virt.c

## Purpose

`amdgpu_virt.c` implements common AMDGPU virtualization support for passthrough and SR-IOV VF operation. It detects virtualization mode, installs ASIC-specific virt ops, negotiates full GPU access and reset handshakes, manages PF2VF/VF2PF shared-memory data exchange, handles dynamic critical regions, reserves RAS bad pages, provides indirect register access through RLCG/VFI, exposes SR-IOV video codec limits, and proxies RAS telemetry/CPER/remote commands to the host.

## Important APIs And Functions

Basic operation wrappers include `amdgpu_virt_request_full_gpu()`, `amdgpu_virt_release_full_gpu()`, `amdgpu_virt_reset_gpu()`, `amdgpu_virt_request_init_data()`, `amdgpu_virt_ready_to_reset()`, and `amdgpu_virt_wait_reset()`. These call installed `virt->ops` callbacks and update runtime/no-hw-access caps. `amdgpu_virt_init_setting()` applies VF display/power defaults, while `amdgpu_virt_init()` detects VF/passthrough state and selects VI/SOC15/NV virt ops.

Data exchange is handled by `amdgpu_virt_init_data_exchange()`, `amdgpu_virt_exchange_data()`, `amdgpu_virt_read_pf2vf_data()`, `amdgpu_virt_write_vf2pf_data()`, and delayed work `amdgpu_virt_update_vf2pf_work_item()`. PF2VF checks version and checksum, imports feature flags, register access flags, multimedia bandwidth limits, UUID, and RAS caps. VF2PF writes driver version, memory usage, firmware versions, dummy page, optional MES info, and checksum. Retry failures can schedule reset when RAS interrupts or retry limits indicate stale data.

Dynamic critical region support is in `amdgpu_virt_init_critical_region()` and `amdgpu_virt_get_dynamic_data_info()`. It reads a host-provided init-data header from VRAM, validates VRAM bounds, signature, checksum, and per-table sizes, records table offsets/sizes, reserves the critical VRAM region, and lets callers copy dynamic table contents.

RAS support includes bad-page data setup/reservation, `amdgpu_virt_get_ras_capability()`, telemetry count requests, CPER dump requests, post-reset telemetry refresh, critical-region hit checks, bad-page requests, and remote RAS command forwarding. It ratelimits host messages and caches telemetry so reads can continue during reset.

Register access support includes `amdgpu_virt_get_rlcg_reg_access_flag()`, `amdgpu_virt_rlcg_reg_rw()`, `amdgpu_virt_rlcg_vfi_reg_rw()`, `amdgpu_sriov_wreg()`, and `amdgpu_sriov_rreg()`. These route protected GC/MMHUB register reads/writes through legacy scratch registers or newer VFI registers when SR-IOV access restrictions require it, protected by `rlcg_reg_lock`.

## Control Flow, State, And Integration

Initialization detects VF state from ASIC-specific IOV function registers. If SR-IOV is present, ASIC-specific ops are installed and optional GPU init data is requested. Early data exchange may read PF2VF data from BIOS or dynamic critical region; later, reserved VRAM mappings are used for ongoing PF2VF/VF2PF updates. Reset paths stop data exchange and set MP1 FLR state before reset, then adjust GC/MES readiness afterward.

Persistent runtime state lives in `adev->virt`: caps, ops, mm table, error buffer, shared reserve pointers, feature/reg-access flags, dynamic critical region metadata, delayed VF2PF work, multimedia limits, RLCG lock, RAS caps/cache/rate limits, bad page handler data, and migration flags. GPU-visible state includes reserved VRAM PF2VF/VF2PF/telemetry areas and optional MM table BO.

Dependencies include `amdgpu_ras`, reset domains, DPM, VI/SOC15/NV virt ops, firmware info from many IP blocks, TTM VRAM manager, PSP/RLCG register control, Xen/hypervisor detection, CPER ring helpers, and SR-IOV message definitions.

## Risks And Test Signals

Risks are high because this file gates hardware access in virtualized environments. Key risks include checksum or size validation mistakes for host-provided shared memory, delayed work running across teardown/reset, missed cancellation of data exchange, incorrect cap transitions between full-access/runtime modes, RLCG timeouts or stale GRBM shadow registers, bad-page reservation leaks, trusting telemetry sizes/checksums, null virt ops, firmware skip list drift, and ABI drift with `amd_sriovmsg.h`.

Test signals include SR-IOV detection across supported ASICs, passthrough detection, full GPU request/release/reset callback failures, PF2VF v1/v2 checksum and size validation, VF2PF field/checksum generation, delayed update retry/reset behavior, dynamic critical region signature/checksum/bounds failures, bad page import/reservation, RLCG/VFI read/write paths and timeout errors, firmware skip decisions per MP0 version, video codec limit updates, RAS caps and telemetry block mapping, CPER dump ring writes, critical-region hit queries, and reset pre/post behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_virt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_virt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_virt.h

## Purpose

`amdgpu_virt.h` defines the AMDGPU virtualization data model, feature flags, host/guest shared-memory structures, operation callbacks, SR-IOV helper macros, RLCG register access constants, RAS telemetry state, dynamic critical region metadata, and public virtualization APIs. It is the common header used by bare-metal, passthrough, and SR-IOV VF-aware AMDGPU code.

## Important Types, Macros, And APIs

Capability flags identify SR-IOV-ready VBIOS, IOV enabled, VF mode, passthrough, runtime mode, and VF MMIO protection. RLCG constants define indirect GC/MMHUB read/write operations, scratch-register error bits, VFI commands/status, and function identifier register offsets. `enum amdgpu_sriov_vf_mode` distinguishes bare metal, one-VF, and multi-VF modes.

`struct amdgpu_virt_ops` is the host-interface callback table for full GPU access, init data, reset, mailbox transmission, RAS poison handling, RAS telemetry/CPER/bad-page/critical-region requests, and remote RAS commands. `struct amdgpu_virt_fw_reserve` stores PF2VF, VF2PF, telemetry, and checksum-key pointers. Legacy and current PF2VF/VF2PF message structs describe shared data exchanged with GIM/PF.

`struct amdgpu_virt` is the main device virtualization state: caps, CSA object, interrupt sources, FLR/bad-page work, MM table, ops, VF error ring, shared reserve pointers, generated capability attributes, feature/reg-access flags, dynamic critical region table, delayed VF2PF work and retry interval, multimedia bandwidth limits, autoload ucode id, RLCG lock, debug access mutex, RAS caps/telemetry/cache, bad-page handler data, and XGMI migration flag.

Macros such as `amdgpu_sriov_vf`, `amdgpu_sriov_runtime`, `amdgpu_sriov_fullaccess`, `amdgpu_sriov_reg_indirect_*`, `amdgpu_sriov_ras_*`, and `amdgpu_virt_xgmi_migrate_enabled` centralize mode/feature checks. `DECLARE_ATTR_CAP_CLASS(amdgpu_virt, AMDGPU_VIRT_CAPS_LIST)` uses `amdgpu_utils.h` to declare virtualization capability attributes.

The public APIs cover mode setup, full GPU access, reset handshake, MM table allocation, RAS interrupt/error data, data exchange, dynamic critical region access, debugfs access gating, VF mode query, codec updates, SR-IOV register read/write, firmware skip decisions, pre/post reset, XNACK support, RLCG access, RAS telemetry/CPER/bad-page/critical checks, and remote RAS commands.

## Control Flow And Integration

Most AMDGPU subsystems call the small mode macros to branch around VF restrictions. IP block code uses `amdgpu_sriov_wreg/rreg` when register access may need RLCG. Reset code calls pre/post hooks. Firmware loading asks `amdgpu_virt_fw_load_skip_check()`. Video code imports codec bandwidth limits. RAS code delegates host telemetry through virtualization APIs. VF error reporting uses `vf_errors`.

Dependencies include `amdgv_sriovmsg.h`, `amdgpu_utils.h` through included AMDGPU headers, RAS block enums, video codec types, DRM/BO/ring structures, workqueues, mutexes, and SR-IOV mailbox request enums.

## State, Risks, And Tests

State is broad and cross-subsystem. Risks include ABI drift in PF2VF/VF2PF and RAS telemetry structs, macro checks that miss runtime/full-access distinctions, stale shared-memory pointers after reset, delayed work races, feature flag misinterpretation, non-atomic cap updates, and incorrect RLCG selection causing blocked MMIO or host errors.

Test signals include compile coverage for all helper macros, mode detection results, virt ops null handling, PF2VF/VF2PF struct size/alignment compatibility, data exchange pointer setup for legacy and dynamic regions, debugfs access gating, SR-IOV register access flag selection, RAS capability bit mapping, codec limit propagation, and reset/data-exchange lifecycle ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_virt.h -->
