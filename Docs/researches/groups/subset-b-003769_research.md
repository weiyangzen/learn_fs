# Research: subset-b-003769

Grouped research for vmwgfx KMS, guest messaging, memory objects, resource lifetime, and DX helper resources under `sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_kms.h

Purpose: This header is the shared KMS/display contract for vmwgfx. It declares framebuffer wrappers, display-unit state, plane/crtc/connector state wrappers, dirty-update helper closures, and the public entry points used by legacy display units, screen objects, screen targets, and shared KMS helpers.

Important APIs/types/functions: `struct vmw_du_update_plane` is a callback-driven command construction closure for plane updates, with size calculation and post-prepare/pre-clip/clip/post-clip phases. `struct vmw_kms_dirty` is the older dirty-rect FIFO helper closure. `struct vmw_framebuffer`, `vmw_framebuffer_surface`, and `vmw_framebuffer_bo` distinguish surface-backed and BO-backed framebuffers. `struct vmw_display_unit` embeds DRM `crtc`, `encoder`, `connector`, primary plane, cursor plane, unit numbering, preferred mode/topology state, GUI placement, and VKMS CRC/vblank state. Exported functions include common connector/crtc/plane atomic helpers, dirty/readback helpers, framebuffer creation, implicit placement property setup, and display backend init/dirty/readback entry points for LDU, SOU, and STDU.

Control flow: Backend files populate callback closures and call `vmw_du_helper_plane_update()` or `vmw_kms_helper_dirty()`. Atomic helpers operate through the wrapper conversion macros (`vmw_crtc_state_to_vcs`, `vmw_plane_state_to_vps`, `vmw_connector_state_to_vcs`) and backend display units convert from DRM objects with container macros. `vmw_du_translate_to_crtc()` translates framebuffer-space rectangles into CRTC coordinates using fixed-point plane source offsets.

State and persistence: The header defines persistent per-display-unit topology state (`pref_*`, `gui_*`, `is_implicit`, set GUI coordinates) and plane state fields such as user object, BO size, pin count, CPU blit bytes-per-pixel, and cursor state. KMS object lifetime is owned by DRM core plus backend cleanup routines.

Dependencies and integration points: It depends on `vmwgfx_cursor_plane.h`, `vmwgfx_drv.h`, DRM encoder/framebuffer/probe-helper APIs, and backend implementations in `vmwgfx_kms.c`, `vmwgfx_ldu.c`, `vmwgfx_scrn.c`, and STDU code. Risks cluster around callback size accounting, coordinate translation, pin/unpin balancing, and assumptions that SVGA display units can act as CRTC/encoder/connector simultaneously. Test signals include atomic modeset, damage clipping, cursor updates, framebuffer create/dirty/readback ioctls, topology properties, and VKMS CRC/vblank behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_ldu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_ldu.c

Purpose: Implements the legacy display unit backend using SVGA registers and update FIFO commands. It supports legacy multimon display topology, CRTC/encoder/connector/primary-plane setup, scanout BO pinning at the start of VRAM, and damage updates through `SVGA_CMD_UPDATE`.

Important APIs/types/functions: `struct vmw_legacy_display` tracks active units, count transitions, and the single active framebuffer. `struct vmw_legacy_display_unit` derives from `vmw_display_unit` and links into the active list. `vmw_kms_ldu_init_display()` allocates backend state and initializes one or `VMWGFX_NUM_DISPLAY_UNITS` display units. `vmw_ldu_commit_list()` writes SVGA registers for global dimensions or per-display topology. `vmw_ldu_fb_pin()` and `vmw_ldu_fb_unpin()` pin the scanout BO, pausing overlays around VRAM movement. `vmw_ldu_primary_plane_atomic_update()` updates active state, commits registers, emits damage updates, and flushes commands.

Control flow: Atomic primary plane updates derive the LDU from the active CRTC, add or remove it from `ldu_priv->active`, then call `vmw_ldu_commit_list()`. If a framebuffer is active and FIFO commands are supported, the plane damage clips are emitted through `vmw_kms_ldu_do_bo_dirty()`, falling back to full-frame damage. Init builds DRM planes, optional cursor plane, connector, encoder, and CRTC; failure paths clean up partially initialized DRM objects.

State and persistence: The active display list remains sorted by unit number. The backend pins a single framebuffer while any display is active and unpins when the active count drops to zero. `last_num_active` records previous topology count. Display topology is persisted in SVGA registers until overwritten or display close.

Dependencies and integration points: Uses common KMS helpers, DRM atomic helper callbacks, cursor plane helpers, `vmw_bo_pin_in_start_of_vram()`, overlay pause/resume, and SVGA register/FIFO access. Risks include BUG_ON-heavy invariants, shared framebuffer assumptions across active LDUs, failure to emit display topology when FIFO/register capabilities differ, and error paths that log but cannot roll back atomic state. Test signals: legacy display enable/disable, multimon topology writes, damage-only plane updates, overlay pause/resume during mode changes, and cleanup with no active displays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_ldu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_mksstat.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_mksstat.h

Purpose: Defines optional kernel-side mksGuestStat counter support. When `CONFIG_DRM_VMWGFX_MKSSTATS` is enabled, it exposes counter IDs, page-layout helpers, and timing macros used to record nested self/total cycle counts into shared mksGuestStat pages.

Important APIs/types/functions: `mksstat_kern_stats_t` currently enumerates `MKSSTAT_KERN_EXECBUF` and `MKSSTAT_KERN_COTABLE_RESIZE`, with `MKSSTAT_KERN_COUNT` as the sentinel. `vmw_mksstat_get_kern_pstat()`, `_pinfo()`, and `_pstrs()` compute offsets from the descriptor base page to stat, info, and string pages. `struct mksstat_timer_t` stores the previous top timer, TSC start, and per-pid slot. `MKS_STAT_TIME_DECL`, `MKS_STAT_TIME_PUSH`, and `MKS_STAT_TIME_POP` wrap measured regions.

Control flow: The declaration macro samples `rdtsc()` and obtains a slot from `vmw_mksstat_get_kern_slot(current->pid, dev_priv)`. Push records the current top timer and installs the new counter. Pop reserves the slot by atomically replacing the pid with `MKSSTAT_PID_RESERVED`, restores the top timer, updates count/self/total cycles, subtracts nested elapsed time from the parent self counter, and releases the slot back to the pid.

State and persistence: Per-process stat state lives in arrays on `dev_priv` (`mksstat_kern_pids`, `mksstat_kern_top_timer`, `mksstat_kern_pages`). The backing pages are registered with the hypervisor by code in `vmwgfx_msg.c`. With the config disabled, all macros compile to no-ops.

Dependencies and integration points: Requires page-size layout constants, `rdtsc`, current task pid, atomic64 counters, and MKSGuestStat structures from device headers. Risks include TSC availability/ordering assumptions, strict enum ordering matching page initialization, slot contention returning a negative slot and silently disabling timing, and macro dependence on a visible `dev_priv` variable. Test signals include config-enabled builds, nested timer accounting, concurrent process slots, cleanup/reset paths, and disabled-config compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_mksstat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_mob.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_mob.c

Purpose: Manages guest-backed Memory OBjects (MOBs) and object-table bases. It builds 32-bit or 64-bit page tables for buffer pages, binds/unbinds MOBs to device IDs, and initializes the SVGA object tables needed for guest-backed surfaces, contexts, shaders, screen targets, and DX contexts.

Important APIs/types/functions: `struct vmw_mob` stores the page-table BO, page count, page-table depth, root DMA page, and device ID. Static `pre_dx_tables` and `dx_tables` describe enabled object tables based on SM4/DX support. `vmw_otables_setup()` selects and allocates table metadata, `vmw_otable_batch_setup()` creates one backing BO and calls `vmw_setup_otable_base()` for each enabled table, and `vmw_otables_takedown()` destroys them. `vmw_mob_create()`, `vmw_mob_bind()`, `vmw_mob_unbind()`, and `vmw_mob_destroy()` are the external MOB lifecycle functions.

Control flow: Object-table setup page-aligns table sizes, allocates one waitable system BO, then installs each table base with `SVGA_3D_CMD_SET_OTABLE_BASE64`. Larger tables get a MOB page table built by `vmw_mob_pt_populate()` and `vmw_mob_pt_setup()`. MOB binding uses direct depth-0 mapping for one data page; otherwise it allocates and fills multilevel page tables with `vmw_mob_build_pt()`, increments FIFO resource accounting, and emits `SVGA_3D_CMD_DEFINE_GB_MOB64`. Unbind emits `SVGA_3D_CMD_DESTROY_GB_MOB`, fences the page-table BO, and decrements FIFO accounting.

State and persistence: Page-table BOs are pinned/populated through TTM and released on MOB destroy. Object-table `page_table` pointers indicate active table bases. MOB IDs persist on the device until destroyed. Page-table depth constants differ for 32-bit vs 64-bit kernels.

Dependencies and integration points: Depends on TTM reservation/pinning, vmwgfx BO scatter-gather iteration, SVGA3D commands, FIFO resource accounting, and capability-driven object table sizing. Risks include BUG_ONs for page-table depth, reservation failures treated as impossible in helpers, command-reserve failure during takedown leaving device state active, and correctness of DMA address iteration. Test signals: 32/64-bit builds, DX and pre-DX initialization, multi-page MOBs, OTable teardown under command pressure, and BO move/unbind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_mob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_msg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_msg.c

Purpose: Provides VMware backdoor/RPCI messaging, user message ioctl handling, host guest-info/log helpers, optional high-bandwidth message transfer, and mksGuestStat descriptor registration/removal with the hypervisor.

Important APIs/types/functions: `struct rpc_channel` stores channel id and cookies. `vmw_open_channel()`, `vmw_close_channel()`, `vmw_send_msg()`, and `vmw_recv_msg()` implement the RPCI channel protocol. `vmw_host_get_guestinfo()` and `vmw_host_printf()` are kernel helpers. `vmw_msg_ioctl()` sends userspace messages and optionally copies replies back. mksGuestStat code includes `vmw_mksstat_get_kern_slot()`, `vmw_mksstat_add_ioctl()`, `vmw_mksstat_remove_ioctl()`, `vmw_mksstat_reset_ioctl()`, and `vmw_mksstat_remove_all()`. `vmw_disable_backdoor()` globally disables messaging.

Control flow: Channel open retrieves cookies from a hypercall. Send announces payload size, then uses high-bandwidth transfer unless encrypted memory prevents it, falling back to 4-byte payload hypercalls; checkpoint status retries up to `RETRIES`. Receive queries reply size, allocates a NUL-terminated buffer, receives payload, then sends receive status. mksGuestStat add validates userspace pointers/lengths, reserves a slot with atomics, allocates an instance descriptor page, copies a description, pins stat/info/string pages long-term, stores PFNs, and registers the descriptor PFN with the hypervisor. Removal uses process-group ownership and atomic reservation before unregistering and unpinning pages.

State and persistence: `vmw_msg_enabled` gates all backdoor messages. Registered mksGuestStat descriptors persist in `dev_priv->mksstat_user_pages`/pids or optional kernel arrays until removed/reset/cleanup. Pinned user pages remain pinned while descriptors are active.

Dependencies and integration points: Includes x86 and arm64 hypercall wrappers, confidential-computing memory encryption checks, DRM ioctl structures, pin_user_pages APIs, MKSGuestStat device structures, and timing macros from `vmwgfx_mksstat.h`. Risks include user-buffer length truncation, reply-size trust, long-term pin cleanup on partial failures, concurrency around pid slot reservation, and HB-port incompatibility with encrypted memory. Test signals: guestinfo/log success/failure, ioctl send-only and receive paths, checkpoint retry, encrypted-memory fallback, mksstat add/remove/reset with partial pin failures, and disabled backdoor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_msg_arm64.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_msg_arm64.h

Purpose: Supplies arm64 implementations of the VMware hypercall/backdoor helpers used by `vmwgfx_msg.c`. It emulates VMware x86 I/O-port semantics through register conventions and a trap instruction sequence.

Important APIs/types/functions: Defines VMware port constants, hypervisor magic, high-bandwidth direction flags, and x86 I/O encoding constants for register `x7`. Inline helpers include `vmware_hypercall1()`, `vmware_hypercall5()`, `vmware_hypercall6()`, `vmware_hypercall7()`, shared `vmware_hypercall_hb()`, and direction-specific `vmware_hypercall_hb_out()`/`_in()`.

Control flow: Each helper loads arm64 registers `x0` through the needed argument count with magic, command, payload arguments, port number, cookies, and encoded I/O metadata. The inline assembly executes `mrs xzr, mdccsr_el0`, which the VMware hypervisor intercepts. Output registers are copied into caller-provided `u32 *` slots, matching the x86 helper API expected by common message code.

State and persistence: The header has no persistent state. It is active only when `__aarch64__` is defined and otherwise compiles to an empty include guard. All state is transient register input/output.

Dependencies and integration points: Used by `vmwgfx_msg.c` for RPCI and mksGuestStat hypercalls on arm64. It must remain API-compatible with `<asm/vmware.h>` on x86. Risks include register constraint mistakes, truncating 64-bit return registers into `u32` outputs, incorrect direction/port flag encoding, and sensitivity to compiler inline-asm behavior. Test signals: arm64 builds, RPCI open/send/receive/close, high-bandwidth in/out payloads, mksstat one-argument calls, and comparison with x86 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_msg_arm64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_msg_x86.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_msg_x86.h

Purpose: Provides the x86 architecture include bridge for VMware hypercall helpers used by the common vmwgfx message layer.

Important APIs/types/functions: The header conditionally includes `<asm/vmware.h>` when building for `__i386__` or `__x86_64__`. The actual helper APIs (`vmware_hypercall1`, `vmware_hypercall5`, `vmware_hypercall6`, `vmware_hypercall7`, high-bandwidth helpers) are supplied by the architecture header.

Control flow: There is no runtime control flow here. The common message code includes this header and the arm64 header; preprocessor architecture guards ensure only the matching helper definitions are present.

State and persistence: No persistent state. This is a compile-time integration shim.

Dependencies and integration points: Depends on the kernel x86 VMware helper header and must stay API-compatible with `vmwgfx_msg_arm64.h`. Risks are mostly build-configuration risks: unsupported architectures get no helper definitions, x86 helper API changes would break `vmwgfx_msg.c`, and license/include guard mismatches can affect module builds. Test signals include x86_64 and i386 build coverage and exercising all message/mksstat hypercall paths through `vmwgfx_msg.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_msg_x86.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_overlay.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_overlay.c

Purpose: Implements the legacy VMware video overlay/Xv stream interface. It claims streams, pins stream buffers in VRAM or GMR, sends SVGA escape commands to set/flush video registers, pauses/resumes overlays during scanout buffer moves, and exposes stream control ioctls.

Important APIs/types/functions: `struct vmw_stream` stores the active BO, claimed flag, paused flag, and saved stream arguments. `struct vmw_overlay` owns a mutex and a fixed stream array (`VMW_MAX_NUM_STREAMS` is 1). `vmw_overlay_send_put()` emits `SVGA_ESCAPE_VMWARE_VIDEO_SET_REGS` plus flush. `vmw_overlay_send_stop()` disables a stream. `vmw_overlay_update_stream()`, `vmw_overlay_stop()`, `vmw_overlay_pause_all()`, `vmw_overlay_resume_all()`, `vmw_overlay_ioctl()`, `vmw_overlay_claim()`, `vmw_overlay_unref()`, `vmw_overlay_init()`, and `vmw_overlay_close()` implement public behavior.

Control flow: The ioctl validates overlay FIFO capabilities, resolves a user stream resource, locks the overlay mutex, then either stops the stream or looks up the BO and calls `vmw_overlay_update_stream()`. Updating stops old buffers if needed, pins the new buffer according to active display backend, emits the put command, references the BO, saves arguments, and clears paused state. Pause stops hardware and removes no-evict/pin pressure but retains the BO reference; resume replays saved arguments.

State and persistence: Stream state persists in `dev_priv->overlay_priv`. Claimed streams are reserved until `vmw_overlay_unref()`. Active stream BO references persist until stop/unref/close. Saved arguments persist across pause/resume.

Dependencies and integration points: Uses SVGA escape/video headers, vmwgfx BO pin helpers, FIFO command reservation, user BO/resource lookup, and KMS scanout paths that pause overlays around VRAM pressure. Risks include one-stream assumptions, command-reserve failure handling, BUG_ON on unexpected unpin failures, saved argument validity across mode changes, and capability mismatches. Test signals: claim/free ioctls, enable/disable stream, pause/resume during LDU/SOU mode changes, legacy vs screen-object buffer pin domains, and close with leaked active stream warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_overlay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_page_dirty.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_page_dirty.c

Purpose: Tracks CPU dirtied pages in vmwgfx BOs so coherent guest-backed resources can synchronize changed backing ranges to hardware resources. It dynamically switches between page-table dirty-bit scanning and write-protect/mkwrite tracking.

Important APIs/types/functions: `enum vmw_bo_dirty_method` selects `VMW_BO_DIRTY_PAGETABLE` or `VMW_BO_DIRTY_MKWRITE`. `struct vmw_bo_dirty` stores a kref, first/last dirty bounds, method, transition counter, bitmap size, and page bitmap. Public functions include `vmw_bo_is_dirty()`, `vmw_bo_dirty_scan()`, `vmw_bo_dirty_add()`, `vmw_bo_dirty_release()`, `vmw_bo_dirty_transfer_to_res()`, `vmw_bo_dirty_clear()`, `vmw_bo_dirty_clear_res()`, `vmw_bo_dirty_unmap()`, `vmw_bo_vm_mkwrite()`, and `vmw_bo_vm_fault()`.

Control flow: Small BOs start with page-table scanning; larger BOs start by write-protecting mappings and recording writes in `mkwrite`. Pagetable scanning calls `clean_record_shared_mapping_range()` and switches to mkwrite after repeated empty scans. Mkwrite scanning re-write-protects dirty ranges and switches to pagetable scanning after repeated high dirty percentages. VM fault handling reserves the BO, cleans intersecting resources before prefaulting dirty-tracked pages, chooses write-protected protections for mkwrite mode, then delegates to TTM fault helpers.

State and persistence: Dirty state is attached to `vbo->dirty` and reference-counted across users. Dirty bounds and bitmap persist until transferred or cleared. Resource transfer clears bitmap ranges and calls `vmw_resource_dirty_update()`.

Dependencies and integration points: Integrates TTM VM fault/reservation helpers, DRM VMA node offsets, shared mapping dirty/write-protect helpers, vmwgfx resource clean/dirty functions, and BO reservation locks. Risks include bounds update mistakes after partial clears, division by zero if malformed BO sizes ever occur, subtle page offset units, interaction with unmap losing dirty bits, and fault retry semantics. Test signals: mmap write faults, dirty transfers to coherent resources, method switching thresholds, unmap before eviction, resource clean failures causing SIGBUS, and refcounted add/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_page_dirty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_prime.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_prime.c

Purpose: Provides vmwgfx PRIME/dma-buf handle conversion glue. Full dma-buf attach/map support is intentionally unimplemented for external virtual-device use, but fd-to-handle and handle-to-fd paths bridge TTM and GEM PRIME behavior.

Important APIs/types/functions: `vmw_prime_dmabuf_ops` supplies attach/detach/map/unmap/release ops; attach and map return `-ENOSYS`, detach/unmap are no-ops, and release is NULL. `vmw_prime_fd_to_handle()` first tries `ttm_prime_fd_to_handle()` and falls back to `drm_gem_prime_fd_to_handle()`. `vmw_prime_handle_to_fd()` decides whether to export via TTM or GEM based on handle range, dumb-BO state, and whether a surface handle aliases the BO.

Control flow: fd import is simple fallback. Export checks handles above `VMWGFX_NUM_MOB` as TTM object handles. For lower handles, it looks up the BO; dumb BOs export through GEM PRIME, non-dumb BOs try to locate a surface handle for the buffer and export that through TTM, otherwise fall back to GEM PRIME for the BO handle.

State and persistence: The file does not own long-lived state. It temporarily references BOs during lookup and releases them before returning. Exported dma-buf lifetime is owned by DRM/TTM/GEM infrastructure.

Dependencies and integration points: Depends on `ttm_object`, dma-buf ops, vmwgfx BO lookup, surface lookup by buffer, and DRM GEM PRIME fallback. Risks include limited dma-buf interoperability because attach/map are not implemented, handle namespace assumptions around `VMWGFX_NUM_MOB`, and correct BO unref on all paths. Test signals: PRIME import/export of dumb BOs, export of surface-backed buffers, invalid handle errors, fallback paths, and external device attach attempts returning `-ENOSYS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_prime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_reg.h

Purpose: Minimal kernel-space SVGA virtual hardware register include wrapper. It defines a few vmwgfx-side structures/constants and includes the main SVGA3D register definitions.

Important APIs/types/functions: `struct svga_guest_mem_descriptor` holds a physical page number and page count. `struct svga_fifo_cmd_fence` holds a FIFO fence value. `SVGA_SYNC_GENERIC` and `SVGA_SYNC_FIFOFULL` define sync reason constants. The header then includes `device_include/svga3d_reg.h`, which supplies the command/register structures used throughout vmwgfx.

Control flow: None at runtime; this file is compile-time type and constant plumbing.

State and persistence: None. Hardware state is managed by callers using the included register definitions.

Dependencies and integration points: Included by driver code needing SVGA3D command layouts and register constants. Risks are low but include ABI drift between local wrapper structs and device headers, and broad compile breakage if included headers change. Test signals: build coverage across files using SVGA commands, fence command encoding, and register write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_resource.c

Purpose: Central resource lifetime, validation, eviction, backup-MOB attachment, dirty synchronization, pinning, and user-handle lookup layer for vmwgfx hardware resources.

Important APIs/types/functions: `vmw_resource_init()`, `vmw_resource_alloc_id()`, `vmw_resource_release_id()`, `vmw_resource_reference()`, and `vmw_resource_unreference()` implement kref/IDR lifecycle. `vmw_resource_mob_attach()`/`_detach()` maintain a BO RB tree of attached resources and priority accounting. `vmw_resource_reserve()`, `vmw_resource_validate()`, `vmw_resource_unreserve()`, `vmw_resource_evict_all()`, `vmw_resource_pin()`, and `vmw_resource_unpin()` manage visibility and eviction. `vmw_resources_clean()` and `vmw_resource_dirty_update()` integrate dirty tracking. `vmw_query_move_notify()` handles DX query MOB readback before migration.

Control flow: Validation creates a hardware resource if needed, binds its backup BO if required, allocates/updates dirty trackers, transfers dirty BO ranges, and calls type-specific sync callbacks. If hardware returns `-EBUSY`, validation evicts resources from the same-type LRU until success or an error limit. Eviction ensures backup buffers exist, unbinds with optional readback, destroys hardware state, marks guest memory dirty, and backs off reservations. Release unbinds attached MOBs, frees dirty/coherent tracking, kills bindings, destroys hardware, frees resource memory, and removes IDs.

State and persistence: Resource state includes kref, ID, LRU membership, binding list, guest memory BO/offset/size, dirty flags, coherent flag, pin count, and type-specific callback table. Attached resources persist in each BO's `res_tree`; evictable resources persist in per-type LRU lists.

Dependencies and integration points: Depends on TTM reservation/validation, vmwgfx BO helpers, binding manager, resource-private callback tables, dirty tracking, FIFO command callbacks supplied by resource types, and device locks (`resource_lock`, `cmdbuf_mutex`, `binding_mutex`). Risks include lock ordering, BUG_ONs on reservation assumptions, stale RB-tree state, dirty flag consistency during BO switches, eviction starvation, and readback requirements before moves. Test signals: create/bind/unbind/destroy for each resource type, eviction under resource pressure, coherent BO mmap writes, pin/unpin nesting, DX query MOB migration, and user handle type checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_resource_priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_resource_priv.h

Purpose: Private resource manager interface shared by vmwgfx resource implementations. It defines the common virtual-function tables for resources and the simple-resource helper abstraction.

Important APIs/types/functions: `enum vmw_cmdbuf_res_state` describes committed/add/delete state notifications for command-buffer managed resources. `struct vmw_user_resource_conv` maps TTM base-object types to `struct vmw_resource`. `struct vmw_res_func` is the central resource vtable: type, memory requirements, domain/busy-domain, eviction support, priority, create/destroy/bind/unbind callbacks, command-buffer commit notifications, dirty callbacks, and clean callback. `struct vmw_simple_resource_func` extends this for fixed-shape ioctl-created resources. `struct vmw_simple_resource` embeds `vmw_resource` plus a function table pointer.

Control flow: Resource implementation files declare static `vmw_res_func` or `vmw_simple_resource_func` tables and hand them to `vmw_resource_init()` or `vmw_simple_resource_create_ioctl()`. The generic resource layer calls these callbacks during validation, eviction, cleanup, and dirty synchronization.

State and persistence: The header defines shape but no storage. Persistent state lives in each resource object and the callback tables, which are typically static const.

Dependencies and integration points: It depends on `vmwgfx_drv.h`, TTM object types, and all resource implementations (`shader`, `surface`, `context`, `views`, simple states). Risks are contract-level: callback NULLability must match generic resource behavior, `needs_guest_memory` must be accurate for MOB attachment, and dirty callbacks must be internally consistent. Test signals include compile coverage for all resource vtables, validation/eviction of every resource type, simple resource create/lookup/free, and command-buffer resource add/delete notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_resource_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_scrn.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_scrn.c

Purpose: Implements the Screen Object Unit (SOU) display backend. It creates/destroys SVGA screen objects, allocates VRAM backing buffers for primary planes, supports cursor planes and VKMS hooks, and performs dirty/readback blits for BO-backed and surface-backed framebuffers.

Important APIs/types/functions: `struct vmw_screen_object_unit` derives from `vmw_display_unit`, stores a backing BO, and tracks whether the screen is defined. `vmw_kms_sou_init_display()` initializes all display units when GMR and `SVGA_CAP_SCREEN_OBJECT_2` are available. `vmw_sou_fifo_create()`/`_destroy()` emit define/destroy screen FIFO commands. `vmw_sou_primary_plane_prepare_fb()` creates or reuses a pinned VRAM backing buffer. `vmw_sou_plane_update_bo()` and `_surface()` build callback closures for `vmw_du_helper_plane_update()`. Public dirty/readback functions include `vmw_kms_sou_do_surface_dirty()`, `vmw_kms_sou_do_bo_dirty()`, and `vmw_kms_sou_readback()`.

Control flow: Atomic modeset destroys an existing screen and recreates it with connector GUI coordinates and current CRTC mode if a framebuffer is present. Plane prepare allocates a CRCT-sized VRAM BO while pausing overlays. Plane update chooses BO or surface path: BO path defines a GMRFB and emits `BLIT_GMRFB_TO_SCREEN`; surface path validates the surface and emits `BLIT_SURFACE_TO_SCREEN` with a destination bounding box and relative clip rects. Readback defines a GMRFB then emits `BLIT_SCREEN_TO_GMRFB`.

State and persistence: Each SOU has a persistent screen definition on the device while active, a pinned backing buffer in plane state, and connector GUI placement state inherited from `vmw_display_unit`. Fence output may be returned for dirty/readback synchronization.

Dependencies and integration points: Uses DRM atomic/damage helpers, common KMS dirty/update helpers, vmwgfx validation, BO placement/pinning, overlay pause/resume, SVGA screen-object commands, and VKMS vblank/CRC callbacks. Risks include non-failable atomic mode-set error logging, BO size reuse across state transitions, overlay resume failures after allocation, clip bounding-box translation errors, and command size accounting. Test signals: SOU capability gating, multi-display modesets, damage clips, surface and BO framebuffers, readback fences, cursor operation, and disable/destroy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_scrn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_shader.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_shader.c

Purpose: Manages guest-backed legacy shaders, command-buffer managed compatibility shaders, and DX shaders. It handles user shader object creation/destruction, shader bytecode backing BOs, MOB binding/unbinding, DX cotable tracking, and shader resource staging.

Important APIs/types/functions: `struct vmw_shader` stores resource base, type, size, and signature counts. `struct vmw_user_shader` wraps a TTM base object for userspace handles. `struct vmw_dx_shader` tracks context, cotable, user ID, committed state, and cotable list membership. GB callbacks are `vmw_gb_shader_create()`, `_bind()`, `_unbind()`, and `_destroy()`. DX callbacks include `vmw_dx_shader_create()`, `_bind()`, `_unbind()`, `_commit_notify()`, scrub/unscrub helpers, `vmw_dx_shader_add()`, and cotable scrub. User APIs include `vmw_shader_define_ioctl()`, `vmw_shader_destroy_ioctl()`, `vmw_compat_shader_add()`, `vmw_shader_remove()`, and `vmw_shader_lookup()`.

Control flow: User shader definition validates the bytecode BO range and shader type, initializes a guest-backed resource with delayed ID allocation, then creates a TTM base object handle. GB validation allocates an ID, emits `DEFINE_GB_SHADER`, binds the MOB via `BIND_GB_SHADER`, and fences backup BOs on unbind. DX shaders are added to command-buffer managers; commit notification inserts/removes them from cotables and toggles committed state. Scrub unbinds a DX shader MOB without requiring later context access; unscrub rebinds using context-specific command reservation.

State and persistence: Shader resources persist as kref-managed `vmw_resource` objects. GB resources hold optional bytecode BO references and device IDs. DX resources keep cotable references and committed/list state under `binding_mutex`.

Dependencies and integration points: Depends on resource manager, BO creation/kmap/validation, binding manager, cotables, command-buffer resource manager, SVGA shader commands, and TTM user objects. Risks include user key packing limits, bytecode range validation overflow, DX committed/list consistency, command-reserve failure during destroy/scrub, and BO fence correctness on unbind. Test signals: shader create/destroy ioctls, invalid handles/types/ranges, compat shader bytecode copy, DX define/remove commit notification, context/cotable eviction scrub, and resource pressure eviction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_shader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_simple_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_simple_resource.c

Purpose: Generic helper for ioctl-created simple resources whose type-specific behavior can be described by `struct vmw_simple_resource_func`. It avoids duplicating TTM base-object setup, resource initialization, handle return, lookup, and teardown code.

Important APIs/types/functions: `struct vmw_user_simple_resource` embeds a TTM base object and a variable-sized `vmw_simple_resource`. `vmw_simple_resource_create_ioctl()` allocates enough memory for the requested simple resource, initializes the generic resource, registers a user handle, and writes the handle back through the type-specific callback. `vmw_simple_resource_lookup()` validates handle type and returns a referenced `vmw_resource`. Private helpers include `vmw_simple_resource_init()`, `vmw_simple_resource_free()`, and `vmw_simple_resource_base_release()`.

Control flow: Create allocates `offsetof(..., simple) + func->size`, stores the function table, initializes the resource with immediate ID allocation, invokes the type-specific `init`, creates the TTM base object, and drops the local reference. Base-object release unrefs the embedded resource; final resource free releases memory with `ttm_base_object_kfree()`.

State and persistence: Persistent state is the TTM base object plus embedded resource and type-specific tail. Object lifetime is jointly controlled by TTM handle references and resource krefs. No global state is owned here.

Dependencies and integration points: Depends on `vmwgfx_resource_priv.h`, TTM object files/base objects, DRM file-private `tfile`, and resource vtables supplied by simple resource implementations. Risks include allocation-size correctness for variable tail objects, type mismatch handling, double-unref mistakes during failed base-object init, and immediate ID allocation for resources that may not need hardware state yet. Test signals: simple resource create ioctls for every user, invalid handle/type lookup, init failure cleanup, handle release, and resource destructor invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_simple_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_so.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_so.c

Purpose: Manages DX views and related state-object cotable mappings. Views reference surfaces and contexts, are command-buffer managed, and must be destroyed/restored around surface or cotable eviction to keep device bindings coherent.

Important APIs/types/functions: `struct vmw_view` stores RCU head, resource base, immutable context/surface/cotable references, list nodes for surface and cotable membership, view type/id, saved define command size/data, and committed state. Core functions include `vmw_view_add()`, `vmw_view_remove()`, `vmw_view_create()`, `vmw_view_destroy()`, `vmw_view_commit_notify()`, `vmw_view_cotable_list_destroy()`, `vmw_view_surface_list_destroy()`, `vmw_view_srf()`, `vmw_view_lookup()`, and `vmw_view_dirtying()`. Constant tables map view types to destroy commands and cotables; state-object cotables are listed in `vmw_so_cotables`.

Control flow: Adding a view validates command size and ID/type ranges, copies the user define command, references the surface and cotable, initializes a delayed resource, and stages it in the command-buffer resource manager. Commit notification links or unlinks the view from the surface view list and cotable list and toggles committed/id state. Recreate replays the saved define command, patching `sid` because surface IDs may change after eviction. Destroy scrubs bindings, emits the type-specific destroy command in the owning context, and removes list membership.

State and persistence: View objects persist through resource krefs and are RCU-freed. Committed/list membership is protected by `binding_mutex`. Views hold references to surfaces and cotables so targets outlive the view.

Dependencies and integration points: Depends on resource manager, binding manager, context cotables, surface view lists, command-buffer resource manager, SVGA DX view command layouts, and build-time layout assertions. Risks include saved command ABI assumptions, view-key packing limits, list consistency under eviction/removal, command-reserve failure during destroy, and correct dirty classification for RTV/DSV/UAV. Test signals: create/remove for all four view types, surface eviction destroying dependent views, cotable eviction, context restore recreating views with new SIDs, invalid command sizes/types, and build asserts for SVGA layout drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_so.c -->
