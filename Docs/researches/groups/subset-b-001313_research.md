# subset-b-001313 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_connectors.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_connectors.c

Purpose: this file implements the legacy non-DC amdgpu DRM connector layer. It creates VGA, DVI, HDMI, LVDS, eDP, DisplayPort, and DP-bridge connectors, wires their `drm_connector_funcs` and helper funcs, detects sinks, obtains EDID/DPCD data, validates modes, manages connector properties, and updates ATOM BIOS scratch registers for firmware/BIOS display state.

Important APIs and functions: exported entry points are `amdgpu_connector_hotplug()`, `amdgpu_connector_get_monitor_bpc()`, `amdgpu_connector_encoder_get_dp_bridge_encoder_id()`, `amdgpu_connector_is_dp12_capable()`, and `amdgpu_connector_add()`. Core helpers include EDID acquisition via `amdgpu_connector_get_edid()`, mode population through `amdgpu_connector_ddc_get_modes()`, native-panel fallback through `amdgpu_connector_lcd_native_mode()`, connector-specific detect functions for LVDS/VGA/DVI/DP, and mode validators for LVDS/VGA/DVI/DP. The connector registration path selects the appropriate funcs table, attaches properties such as underscan/audio/dither/load-detect/scaling, initializes AUX for DP, and marks polling mode based on HPD/DDC availability.

Control flow: detection paths acquire runtime PM when not running from the poll worker, probe DDC/HPD or load-detect encoders, refresh cached EDID, infer digital versus analog routing, update scratch registers, and then release runtime PM. DP detection additionally reads sink type and DPCD, powers eDP panels on around DPCD/EDID reads, handles DP bridges, and updates the DP subconnector property. Hotplug handling only retrains real external DP links when HPD is present, the connector is on, the previous sink was DP, the current sink still reports DP, and link training is needed.

State and persistence: state is in-memory on `struct amdgpu_connector`, `struct amdgpu_connector_atom_dig`, connector properties, cached `drm_edid`, HPD/router/DDC fields, `use_digital`, `detected_by_load`, and `detected_hpd_without_ddc`. Native panel mode is stored in the paired `amdgpu_encoder`. BIOS scratch registers are externally visible firmware state but are updated as connector status changes; no filesystem persistence is performed.

Dependencies and integration: the file depends on DRM connector/probe helpers, DRM EDID and DP helpers, runtime PM, amdgpu I2C/router helpers, ATOMBIOS encoder/DP helpers, amdgpu display HPD/DDC helpers, and module parameters such as `amdgpu_audio` and `amdgpu_deep_color`. It is used by the display discovery path to materialize DRM connectors that later participate in KMS probing and modesets.

Risks: DVI/shared-DDC handling is subtle because EDID may be missing or ambiguous, analog load detection can be destructive and is avoided unless forced, and delayed retry is needed for HPD-without-DDC. DP and eDP paths depend on correct panel power sequencing and DPCD availability. Deep-color bpc selection must obey max TMDS clock and module policy. The `failed:` path calls `drm_connector_cleanup()` even after partial initialization; callers rely on the connector's object layout and allocation discipline being correct.

Test signals: useful validation includes hotplug connect/disconnect for DVI/HDMI/DP/eDP/LVDS, shared-DDC systems, broken or hardcoded EDID laptops, DP bridge adapters, passive DP-to-HDMI/DVI adapters, deep-color HDMI modes near TMDS limits, forced DVI analog/digital modes, runtime PM suspend/resume probing, and KMS mode validation for panel scaling and pixel-clock rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_connectors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_connectors.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_connectors.h

Purpose: this header is the public contract for the legacy amdgpu connector implementation. It exposes connector hotplug handling, monitor bpc selection, DP bridge/capability helpers, and connector creation to the rest of the amdgpu display stack.

Important APIs/types: it declares `amdgpu_connector_hotplug()`, `amdgpu_connector_get_monitor_bpc()`, `amdgpu_connector_encoder_get_dp_bridge_encoder_id()`, `amdgpu_connector_is_dp12_capable()`, and `amdgpu_connector_add()`. The declarations depend on externally defined DRM and amdgpu types such as `struct drm_connector`, `struct amdgpu_device`, `struct amdgpu_i2c_bus_rec`, `struct amdgpu_hpd`, and `struct amdgpu_router`.

Control flow and integration: callers use `amdgpu_connector_add()` during display object discovery to register DRM connectors for supported device bits and then use the smaller helpers in hotplug, encoder, and modeset code. The header intentionally does not expose connector internals such as detection helpers or funcs tables; those remain private to `amdgpu_connectors.c`.

State and persistence: the header itself has no state. It defines interfaces that mutate DRM connector state, amdgpu connector private state, and BIOS scratch state in the implementation.

Dependencies: it must be included after the core amdgpu and DRM type definitions or in translation units where those forward declarations are already available. It is tied to the legacy ATOMBIOS connector stack rather than the DC display manager path.

Risks: the function set is small but carries wide side effects. Any signature change affects display initialization and hotplug users. Because the header does not declare the involved structs itself, include-order mistakes can surface as build failures in new users.

Test signals: build coverage from display discovery and hotplug files is the primary signal. Runtime coverage comes from exercising connector creation and DP helper calls through KMS connector enumeration and HPD events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_connectors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cper.c

Purpose: this file builds and buffers CPER records for amdgpu RAS/ACA error reporting. It encodes fatal uncorrectable errors, corrected/deferred runtime errors, and bad-page-threshold events into AMD/nonstandard CPER layouts and writes them into an in-memory amdgpu ring buffer.

Important APIs and functions: exported functions are `amdgpu_cper_entry_fill_hdr()`, section fillers for fatal/runtime/bad-page-threshold sections, `amdgpu_cper_alloc_entry()`, record generators `amdgpu_cper_generate_ue_record()`, `amdgpu_cper_generate_ce_records()`, `amdgpu_cper_generate_bp_threshold_record()`, ring writer `amdgpu_cper_ring_write()`, and lifecycle functions `amdgpu_cper_init()`/`amdgpu_cper_fini()`. Internal helpers build timestamps, section descriptors, severity mappings, detect CPER headers across ring wrap, compute entry sizes, and expose rptr/wptr to `amdgpu_ring`.

Control flow: record generation allocates a correctly sized CPER buffer, fills the header with signature, revision, timestamp, platform/creator IDs, notify type, and section count, fills one or more sections from ACA bank registers or fixed bad-page-threshold fields, writes the completed record to `adev->cper.ring_buf`, and frees the temporary buffer. The ring writer copies byte chunks into the dword ring, handles wrap, updates `wptr`, and advances `rptr` on overflow until it lands on the next CPER header.

State and persistence: CPER state lives under `adev->cper`: enable flag, unique atomic record ID, counters, locks, an array-sized maximum, and an `amdgpu_ring` used as transient storage. Records are not persisted by this file; they remain in the ring until overwritten or consumed by other RAS/debug paths. The record ID includes socket ID when SMUIO supports it.

Dependencies and integration: the implementation depends on `amd_cper.h` structures, ACA bank data from `amdgpu_aca`, RAS enablement checks, SR-IOV CPER policy, `amdgpu_ring_init()`/`amdgpu_ring_fini()`, kernel time conversion, GUID constants, and device identity fields. Call sites include ACA error handling and RAS EEPROM threshold flows.

Risks: ring wrap logic is sensitive to byte-versus-dword arithmetic and CPER record alignment. Allocation failures in record generation can leak a temporary record on later section-fill errors because some error paths return before freeing. `amdgpu_cper_fini()` checks ACA/SR-IOV enablement differently from `amdgpu_cper_init()` and may skip cleanup if enablement conditions drift. Hardcoded bad-page register fields must match consumers' interpretation.

Test signals: inject ACA UE/CE/deferred banks, generate bad-page-threshold records, validate CPER signatures/lengths/section offsets across ring wrap, test maximum section counts and records near `CPER_MAX_RING_SIZE`, exercise SR-IOV and non-SR-IOV enablement gates, and run memory-failure paths for allocation and ring initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cper.h

Purpose: this header defines the amdgpu CPER subsystem's constants, state container, CPER record types, and external API used by ACA/RAS code to generate and buffer CPER entries.

Important APIs/types: constants describe maximum record count and ring size plus header/section sizes and section-offset macros. `enum amdgpu_cper_type` distinguishes runtime, fatal, boot, and bad-page-threshold records. `struct amdgpu_cper` stores enablement, a unique ID counter, locks, lifetime counters, write pointer, an entry pointer array, and an `amdgpu_ring` ring buffer. Public functions cover header/section filling, CPER allocation, UE/CE/bad-page record generation, ring writing, and init/fini.

Control flow and integration: RAS/ACA callers include this header to create records after hardware error collection. The implementation computes layout from the macros here, so the offset macros are part of the ABI between record allocation, section filling, and ring readers.

State and persistence: all declared state is per-device and in memory. `unique_id` is atomic to tolerate multiple producers, while `cper_lock` and `ring_lock` separate high-level CPER state from ring-buffer mutation. No on-disk persistence is specified.

Dependencies: the header includes `amd_cper.h` for CPER structures and `amdgpu_aca.h` for ACA bank types. It also relies on core amdgpu declarations for `struct amdgpu_device` and ring support.

Risks: layout macros assume CPER sections are packed in header, descriptor array, then homogeneous section arrays; mixed section types would require new layout rules. The `ring` pointer array and `count` fields are declared but the current implementation primarily uses `ring_buf`, so unused state can confuse future changes. `CPER_MAX_RING_SIZE` and `CPER_MAX_ALLOWED_COUNT` are fixed compile-time limits.

Test signals: compile-time structure size/offset checks, CPER parser compatibility tests, and RAS injection paths should verify that each exported generator creates records matching the layout described by this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cs.c

Purpose: this file implements the amdgpu command-submission ioctl path and related fence waiting/export helpers. It parses userspace CS chunks, creates one or more scheduler jobs, validates and reserves buffer objects, patches IBs, updates VM mappings, resolves synchronization dependencies, submits jobs to DRM scheduler entities, and records fences back into the amdgpu context.

Important APIs and functions: exported entry points are `amdgpu_cs_ioctl()`, `amdgpu_cs_wait_ioctl()`, `amdgpu_cs_fence_to_handle_ioctl()`, `amdgpu_cs_wait_fences_ioctl()`, `amdgpu_cs_find_mapping()`, and `amdgpu_cs_report_moved_bytes()`. The parser is built in passes: `amdgpu_cs_parser_init()`, `amdgpu_cs_pass1()` for copying and basic chunk validation, `amdgpu_cs_pass2()` for IB/dependency/syncobj/shadow parsing, `amdgpu_cs_parser_bos()` for BO/userptr reservation and validation, `amdgpu_cs_patch_jobs()`, `amdgpu_cs_vm_handling()`, `amdgpu_cs_sync_rings()`, and `amdgpu_cs_submit()`.

Control flow: `amdgpu_cs_ioctl()` rejects RAS poison and non-working acceleration, initializes the parser and context, validates user chunks, allocates jobs per scheduler entity up to gang size 4, handles user fences and BO lists, locks VM page tables and BOs through `drm_exec`, validates memory placement with throttled migration accounting, patches parseable IBs, updates VM PTE/PDE state, pushes explicit and implicit sync fences to jobs, arms jobs, wires gang dependencies, adds dma-resv fences to BOs, stores the fence in the context ring, signals post dependencies, and pushes jobs to scheduler queues. Failure paths unlock the BO-list mutex when needed and funnel through `amdgpu_cs_parser_fini()`.

State and persistence: per-submission state lives in `struct amdgpu_cs_parser`, including chunks, jobs, entities, `drm_exec`, BO list, user fence BO, sync object post-dependencies, movement thresholds, and `amdgpu_sync`. Persistent per-file-descriptor state is updated through the context fence ring, VM mappings, BO reservation/fence state, VM task info, preamble-presented flag, and syncobj handles. There is no disk persistence.

Dependencies and integration: this path integrates DRM ioctls, DRM scheduler, dma-fence, syncobj/sync_file, TTM, amdgpu BO lists, VM/HMM/userptr handling, RAS, ring parse/patch hooks, tracepoints, XCP/isolation state, and libdrm retry behavior on `-EAGAIN`.

Risks: user chunk parsing and length math are security-sensitive. Gang submission is limited and disallowed for SR-IOV VF multi-engine cases. Userptr invalidation races require notifier-lock validation and retry. VM update order and BO reservation ownership must be exact. `amdgpu_cs_find_mapping()` mutates BO flags to force contiguous VRAM when patching IBs. Movement throttling can change placement behavior and performance. Post-dependency allocation paths must correctly drop syncobjs and chains on failure.

Test signals: ioctl fuzzing for chunk IDs/lengths/addresses, IB parse tests per ring type, gang submission and SR-IOV rejection tests, userptr invalidation with retry, BO-list duplicate/reservation contention, syncobj timeline wait/signal, fence wait all/any behavior including already-signaled fences and fence errors, VRAM migration throttling, VM lost/generation cancellation, RAS poison rejection, and lockdep coverage around `drm_exec`, BO-list mutex, and notifier lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cs.h

Purpose: this header defines the command-submission parser data structures shared by `amdgpu_cs.c` and helpers that need to inspect CS mappings.

Important APIs/types: `AMDGPU_CS_GANG_SIZE` fixes the maximum submission gang to four scheduler entities/jobs. `struct amdgpu_cs_chunk` stores a copied userspace chunk ID, dword length, and kernel data pointer. `struct amdgpu_cs_post_dep` tracks syncobj output state, optional timeline chain, and point. `struct amdgpu_cs_parser` is the central per-ioctl state object: device/file/context, chunks, gang entities/jobs/leader, `drm_exec`, BO list, memory migration counters, user fence BO, post dependencies, and `amdgpu_sync`. The only declared function is `amdgpu_cs_find_mapping()`.

Control flow and integration: `amdgpu_cs.c` fills this structure progressively through parser passes. Ring parsers and patch hooks can use `amdgpu_cs_find_mapping()` to resolve IB virtual addresses back to BO mappings owned by the current CS reservation ticket.

State and persistence: the parser is transient and freed at ioctl completion. It references persistent objects such as contexts, BO lists, BOs, syncobjs, and VM mappings but does not own their lifetime beyond references acquired by the parser.

Dependencies: the header includes `drm_exec`, `ww_mutex`, amdgpu job, BO-list, and ring declarations. It forward-declares `struct amdgpu_bo_va_mapping` to avoid exposing VM internals.

Risks: changing field ownership or cleanup expectations risks leaks, double puts, or lock-order bugs in the ioctl path. Increasing `AMDGPU_CS_GANG_SIZE` would require revisiting userspace ABI expectations, scheduler dependency wiring, and VM invalidation constraints.

Test signals: build and runtime coverage should include ring parse callbacks that include this header, gang-size boundary tests, and failure-path cleanup tests that ensure each parser-owned reference is dropped exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_csa.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_csa.c

Purpose: this file manages the static CSA, a reserved GPU virtual address mapping used for command-stream context save/restore and SR-IOV graphics preemption support. It allocates a kernel BO, zeroes it, maps it into per-process VMs at a reserved address, and unmaps it during teardown.

Important APIs and functions: `amdgpu_csa_vaddr()` returns the sign-extended reserved CSA virtual address. `amdgpu_allocate_static_csa()` creates a kernel BO in the requested domain, maps CPU memory, zero-fills it, and stores `adev->virt.csa_cpu_addr`. `amdgpu_free_static_csa()` releases the BO. `amdgpu_map_static_csa()` locks the VM page directory and CSA BO with `drm_exec`, creates a `bo_va`, and maps it readable/writable/executable at the supplied CSA address. `amdgpu_unmap_static_csa()` locks the same objects, unmaps the virtual address, and deletes the VM BO mapping.

Control flow: device initialization allocates the static CSA BO; file/VM initialization maps it for clients that need SR-IOV preemption metadata; file teardown unmaps it. Both map and unmap use `drm_exec_until_all_locked()` with contention retry before touching VM mapping state.

State and persistence: persistent state is in-memory only: the BO pointer, CPU address in `adev->virt.csa_cpu_addr`, and per-VM `amdgpu_bo_va` mapping. There is no on-disk persistence. The mapping is deterministic because it uses the reserved `AMDGPU_VA_RESERVED_CSA_START()` address.

Dependencies and integration: this code depends on amdgpu BO kernel allocation/free helpers, VM BO add/map/unmap/delete helpers, `drm_exec`, GMC sign extension, and SR-IOV/GFX/MES users that consume `amdgpu_csa_vaddr()` for preemption payloads. Call sites include device init, KMS open/close VM setup, MES context mapping, and GFX/SDMA/VPE command paths.

Risks: `amdgpu_allocate_static_csa()` ignores the return value of `amdgpu_bo_create_kernel()` and only checks `*bo`, so unexpected helper behavior could hide errors. Map/unmap must keep VM PD and BO locking order consistent with broader VM code. Executable PTE permissions are intentionally broad and should remain limited to the reserved CSA object. The reserved VA must not collide with user mappings.

Test signals: SR-IOV preemption tests, KMS open/close with CSA map/unmap, VM teardown leak checks, lockdep for VM/BO reservation, allocation failure injection, and GPU preemption tests that verify firmware can read the CSA payload at the expected address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_csa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_csa.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_csa.h

Purpose: this header exposes the static CSA manager contract for device, VM, and firmware command paths that need the reserved context-save area.

Important APIs/types: `AMDGPU_CSA_SIZE` defines the default static CSA size as 128 KiB. Public declarations include `amdgpu_get_total_csa_size()`, `amdgpu_csa_vaddr()`, allocation/free helpers, and VM map/unmap helpers.

Control flow and integration: device init code allocates the static CSA object, per-file VM setup maps it through `amdgpu_map_static_csa()`, command-generation code computes offsets from `amdgpu_csa_vaddr()`, and teardown unmaps/frees it. The header is included by paths that do not need implementation details of `amdgpu_csa.c`.

State and persistence: no state is stored in the header. The APIs manipulate per-device BO state and per-VM VA mappings in memory.

Dependencies: declarations require amdgpu core types such as `struct amdgpu_device`, `struct amdgpu_bo`, `struct amdgpu_vm`, and `struct amdgpu_bo_va`.

Risks: the searched amdgpu tree shows `amdgpu_get_total_csa_size()` declared here but no definition or call in this subset, which may be a stale declaration or defined outside the visible tree in other configurations. Consumers must keep size and address assumptions synchronized with firmware expectations. Any change to `AMDGPU_CSA_SIZE` can affect reserved VA layout and preemption packet construction.

Test signals: compile/link coverage for all declared APIs, SR-IOV preemption coverage, and static analysis for unused or undefined declarations are the key signals for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_csa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ctx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ctx.c

Purpose: this file implements amdgpu GPU context management. It backs the `AMDGPU_CTX` ioctl, manages per-file context IDs, lazily creates DRM scheduler entities per hardware IP/ring, tracks recent fences and reset/RAS state, handles priority and stable-pstate policy, and reports per-context GPU time usage.

Important APIs and functions: exported APIs include `amdgpu_ctx_priority_is_valid()`, `amdgpu_ctx_ioctl()`, `amdgpu_ctx_get()`/`amdgpu_ctx_put()`, `amdgpu_ctx_get_entity()`, `amdgpu_ctx_add_fence()`, `amdgpu_ctx_get_fence()`, `amdgpu_ctx_priority_override()`, `amdgpu_ctx_wait_prev_fence()`, manager init/flush/fini, and usage accounting. Internal helpers translate amdgpu priority to DRM scheduler and hardware priority, check privilege for high priority, initialize/finalize entities, allocate/free contexts in an IDR, query reset/RAS state, and set/get stable pstate.

Control flow: context allocation validates priority, checks permissions, allocates an IDR slot, initializes reset counters, VM generation, priority, and stable pstate. Entity creation happens lazily when CS or wait paths request a hardware IP/ring; it selects schedulers, handles XCP scheduler selection, disables load balancing for video engines that retain context, and initializes a `drm_sched_entity`. CS submission stores fences in a circular array via `amdgpu_ctx_add_fence()`, while wait/query ioctls retrieve fences or reset/RAS flags. Context free removes the IDR entry, destroys scheduler entities, accounts fence time, restores stable pstate if needed, and frees memory.

State and persistence: state is per-file and in-memory: `amdgpu_ctx_mgr` owns an IDR and accumulated time counters; each `amdgpu_ctx` stores reset counters, priority, stable pstate, guilty flag, preamble status, VM generation, RAS counters, entities, and recent fences. Stable pstate affects device power-management state while a context owns it, but there is no persistent storage.

Dependencies and integration: the implementation integrates DRM auth/master checks, Linux capabilities, DRM scheduler entities, dma-fence timestamps, amdgpu scheduler arrays, XCP partitioning, VM generation, RAS counters, DPM performance levels, GPU reset state, and CS ioctl handling.

Risks: lazy entity initialization uses `cmpxchg`; concurrent requests can create and discard duplicate entities, so cleanup must remain correct. Stable pstate is single-owner and guarded by `stable_pstate_ctx_lock`; leaked contexts can leave PM policy pinned. Fence ring indexing depends on `amdgpu_sched_jobs` and returns `NULL` for too-old fences. Priority override mutates existing entities and scheduler sets. Manager fini logs contexts still alive rather than forcibly cleaning them.

Test signals: context alloc/free/query ioctl tests, priority permission tests for master/CAP_SYS_NICE/render clients, fence wait and old-fence behavior, reset and VRAM-lost query flags, RAS CE/UE flag updates, stable-pstate owner conflict tests, scheduler entity creation per HW IP/ring including invalid bounds, XCP partition coverage, and teardown leak/lockdep checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ctx.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ctx.h

Purpose: this header defines amdgpu context and context-manager structures plus the APIs used by command submission, waits, scheduling, and file teardown.

Important APIs/types: `AMDGPU_MAX_ENTITY_NUM` caps per-HW-IP entity slots. `struct amdgpu_ctx_entity` stores the hardware IP, next sequence number, DRM scheduler entity, and flexible array of recent fences. `struct amdgpu_ctx` stores refcounting, ring lock, reset/query counters, priority, stable pstate, guilty flag, preamble state, VM generation, RAS counters, manager pointer, and entity table. `struct amdgpu_ctx_mgr` stores the device pointer, context IDR lock, IDR, and per-HW-IP time counters. The header declares context lookup/refcount, entity lookup, fence add/get, priority validation/override, ioctl, previous-fence wait, manager lifecycle, and usage APIs.

Control flow and integration: CS code obtains contexts and scheduler entities through this API, stores submission fences, and waits for previous fences. DRM ioctl dispatch calls `amdgpu_ctx_ioctl()`. File lifecycle code initializes, flushes, and finalizes the manager. Diagnostics can call usage accounting.

State and persistence: all structures are per-process/per-device in memory. Fence arrays retain only a bounded recent history sized by `amdgpu_sched_jobs`; old fences intentionally become unavailable.

Dependencies: the header depends on ktime/types, `amdgpu_ring.h`, DRM file/device forward declarations, dma-fence, kref, IDR, mutex, and scheduler entity definitions pulled through included amdgpu headers.

Risks: structure fields are tightly coupled to `amdgpu_ctx.c` cleanup and CS assumptions. The flexible fence array requires allocation with enough elements. Any change to entity counts affects userspace-visible ring validation and scheduler selection.

Test signals: compile coverage across CS, KMS file lifecycle, and scheduler code; runtime CS/wait ioctl tests; and memory-safety checks around context refcounting and manager finalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ctx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_debugfs.c

Purpose: this file registers and implements amdgpu debugfs interfaces for register access, wave/GPR inspection, sensors, GFXOFF controls, IB tests, memory eviction, benchmarking, VM/page-table visibility, ring preemption testing, firmware/security/RAS debug hooks, VBIOS/discovery blobs, and usermode queue diagnostics.

Important APIs and functions: exported functions are `amdgpu_debugfs_init()`, `amdgpu_debugfs_regs_init()`, `amdgpu_debugfs_vm_init()`, and `amdgpu_debugfs_userq_init()` with no-op stubs when `CONFIG_DEBUG_FS` is disabled. File operations cover `amdgpu_regs`, `amdgpu_regs2`, `amdgpu_gprwave`, DIDT/PCIE/PCIE64/SMC registers, `amdgpu_gca_config`, sensors, wave status, GPR reads, GFXOFF controls/status/count/residency, IB preemption, SCLK forcing, IB tests, VM info, evict VRAM/GTT, benchmark, per-client page-table info, and user queue MQD info.

Control flow: register/debug reads validate alignment and size, acquire runtime PM, enable virtualization debugfs access, select GRBM/SRBM banks when requested, optionally hold PM power-gating locks, perform register access or gfx function callbacks, restore bank selection, release PM, and disable virtual debug access. `amdgpu_debugfs_init()` creates top-level files, initializes other amdgpu debugfs modules, creates per-ring and VCN firmware logs, scheduler masks, RAS/security/PSP entries, and static blobs. IB preemption stops the scheduler, requests ring preemption, processes and swaps old fences, recovers unfinished jobs, waits for empty, signals old fences, and restarts scheduling under the reset-domain semaphore.

State and persistence: debugfs state is ephemeral and mostly reflects live device state. Per-open `regs2` and `gprwave` files store selected bank/state in private data protected by a mutex. Writes can mutate hardware state, PM policy, GFXOFF state, SCLK soft range, ring scheduling/fences, and eviction state. Debugfs files disappear with the device/debugfs lifecycle; no disk persistence is done.

Dependencies and integration: this file depends on debugfs, runtime PM, uaccess, PCI/register macros, amdgpu PM/DPM, DC debugfs when enabled, RAS/RAP/secure display/firmware attestation/PSP/TA/MES/UMR/userq modules, TTM eviction, DRM scheduler, dma-fence, reset domains, VM/BO helpers, and gfx IP callbacks for wave/GPR reads.

Risks: many entries expose powerful hardware mutation to privileged debugfs users. Alignment, bank-selection bounds, runtime PM, and virtualization access must be correct to avoid invalid register access. Some error paths in wave/GPR helpers can call `pm_runtime_put_autosuspend()` even after failed `pm_runtime_get_sync()` paths, so changes need care. `amdgpu_debugfs_gfxoff_count_read()` writes a `u64` to userspace while advancing/resulting in 4-byte increments, a detail worth regression-testing. IB preemption manually manipulates scheduler/fence state and is high risk.

Test signals: debugfs smoke tests for every created file, 32-bit/64-bit alignment rejection, banked GRBM/SRBM register access with invalid selector bounds, runtime PM suspend/resume, SR-IOV virtual access denial/enablement, wave/GPR reads on supported and unsupported IPs, GFXOFF and sensor reads, SCLK range validation, IB test/preemption under reset-domain locking, per-client VM and user queue debugfs creation, and `CONFIG_DEBUG_FS=n` build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_debugfs.h

Purpose: this header declares the amdgpu debugfs initialization hooks used by device setup, subsystem-specific debug providers, fence/firmware/GEM helpers, VM/client setup, and usermode queue diagnostics.

Important APIs/types: it forward-declares `struct amdgpu_usermode_queue` and declares `amdgpu_debugfs_regs_init()`, `amdgpu_debugfs_init()`, `amdgpu_debugfs_fini()`, `amdgpu_debugfs_fence_init()`, `amdgpu_debugfs_firmware_init()`, `amdgpu_debugfs_gem_init()`, `amdgpu_debugfs_mes_event_log_init()`, `amdgpu_debugfs_vm_init()`, and `amdgpu_debugfs_userq_init()`.

Control flow and integration: device initialization calls `amdgpu_debugfs_init()` after DRM primary minor/debugfs root setup. That function calls the subsystem init declarations here and registers per-device files. Per-open VM and user queue setup use the client-level init functions to create entries under `file->debugfs_client`.

State and persistence: the header has no state. Declared functions create debugfs dentries or no-op depending on config/implementation. Debugfs state is kernel runtime state only.

Dependencies: users must include this with definitions for `struct amdgpu_device` and `struct drm_file` available. The concrete definitions are spread across `amdgpu_debugfs.c` and other amdgpu debugfs provider files.

Risks: declarations here cover functions not implemented in `amdgpu_debugfs.c` itself, so missing provider objects would become link failures. Publicly declaring `amdgpu_debugfs_fini()` requires matching lifecycle behavior elsewhere. Because debugfs is optional, callers must tolerate no-op implementations where provided.

Test signals: `CONFIG_DEBUG_FS=y/n` builds, link coverage for every declared provider, device probe/remove debugfs lifecycle tests, and per-client debugfs creation tests for VM/user queue entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dev_coredump.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dev_coredump.c

Purpose: this file implements amdgpu Linux devcoredump support. On GPU reset or job timeout it snapshots device, firmware, VM fault, IP, ring, and IB information, formats it into a readable text dump asynchronously, and publishes it through `/sys/class/drm/card*/device/devcoredump/data`. When `CONFIG_DEV_COREDUMP` is disabled, it provides no-op stubs.

Important APIs and functions: exported functions are `amdgpu_coredump()`, `amdgpu_coredump_init()`, and `amdgpu_coredump_fini()`. Internal helpers include `amdgpu_devcoredump_fw_info()` for firmware/VBIOS details, `amdgpu_devcoredump_format()` for the text report, `amdgpu_devcoredump_read()` for devcoredump reads, `amdgpu_devcoredump_free()` for cleanup, and `amdgpu_devcoredump_deferred_work()` for asynchronous one-time formatting and `dev_coredumpm()` registration.

Control flow: `amdgpu_coredump()` skips creation if formatting work is already busy, allocates a sized `amdgpu_coredump_info` including per-IB metadata when a PASID job is available, captures task info, ring pointer, ring buffers with unsignalled fences, reset time, skip/VRAM-lost flags, and job IB GPU addresses/sizes, stores it on `adev->coredump`, queues work, and logs the sysfs path. Deferred work computes formatted size with a sizing pass, allocates the buffer, formats again, then publishes the coredump. Reads copy from the cached formatted buffer by offset.

State and persistence: the snapshot lives in memory until the devcoredump core frees it. It includes formatted text, ring snapshots, ring metadata, reset task/time, PASID, and IB descriptors. It is exposed through sysfs devcoredump, not written directly to a repository or driver-owned file. `amdgpu_coredump_fini()` flushes work before hardware/IP teardown.

Dependencies and integration: the file depends on Linux `devcoredump`, generated kernel release strings, DRM printers, amdgpu discovery, IP block print hooks, firmware fields, VM fault and VM-by-PASID lookup, BO reservation/kmap/GART/MMIO access, ring/fence state, job metadata, and reset paths. Call sites include job timeout handling and GPU reset handling.

Risks: formatting can be large, capped at 256 MiB, and performs extensive device/VM/BO inspection after a fault. Ring snapshot allocation uses `total_ring_size` bytes for a `u32 *`, matching byte count but requiring careful offset math. IB dumping must avoid mapping lookups during sizing and must reserve/unreserve BOs correctly. If another coredump is already in progress, new faults are dropped. The comment assumes single-threaded callers for `adev->coredump` pointer updates.

Test signals: `CONFIG_DEV_COREDUMP=y/n` builds, forced GPU reset/job-timeout generation, concurrent reset while work is busy, sysfs read offsets and repeated reads, ring snapshot with signalled and unsignalled fences, IB dump for CPU-accessible and NO_CPU_ACCESS VRAM BOs, VM lookup failure paths, allocation failure injection, and device remove flushing while coredump work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dev_coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dev_coredump.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dev_coredump.h

Purpose: this header defines the amdgpu devcoredump data structures and public lifecycle/API for creating device coredumps after GPU faults.

Important APIs/types: when `CONFIG_DEV_COREDUMP` is enabled, `AMDGPU_COREDUMP_VERSION` identifies the text format. `struct amdgpu_coredump_ring` stores ring read/write pointers, ring index, and snapshot offset. `struct amdgpu_coredump_ib_info` stores an IB GPU address and dword size. `struct amdgpu_coredump_info` stores device pointer, reset task/time, VRAM flags, timed-out ring, ring snapshots, formatted output cache, PASID, IB count, and a counted flexible array of IB descriptors. The header always declares `amdgpu_coredump()`, `amdgpu_coredump_init()`, and `amdgpu_coredump_fini()`.

Control flow and integration: reset and timeout paths call `amdgpu_coredump()` with the affected job and VRAM-loss status. Device init/fini call the lifecycle functions to initialize and flush deferred work. Consumers do not need to know whether the config produces a real coredump or no-op stubs.

State and persistence: the structures describe an in-memory snapshot later exposed by the kernel devcoredump facility. The formatted output is cached to avoid expensive repeated printing during sysfs reads.

Dependencies: the header includes `amdgpu.h`, so it depends on broad driver type definitions. The counted flexible array uses kernel annotations and is only defined under `CONFIG_DEV_COREDUMP`.

Risks: struct layout is part of the private implementation contract between capture, formatting, read, and free functions. Adding fields can increase memory pressure during fault handling. Callers must not dereference config-guarded structs when devcoredump is disabled.

Test signals: config-on/config-off builds, reset path invocation, flexible-array sizing for jobs with multiple IBs, and teardown flushing are the main signals for this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dev_coredump.h -->
