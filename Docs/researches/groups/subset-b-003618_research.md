# subset-b-003618 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_fw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_fw.c

Purpose: implements i915 microcontroller firmware selection, fetch, validation, memory staging, GGTT binding, DMA upload, RSA staging, cleanup, and diagnostics for GuC, HuC, and GSC firmware.

Important APIs/types/functions: platform firmware tables are built by `INTEL_GUC_FIRMWARE_DEFS`, `INTEL_HUC_FIRMWARE_DEFS`, and `INTEL_GSC_FIRMWARE_DEFS`, then represented as `struct uc_fw_blob` and `struct uc_fw_platform_requirement`. Public entry points are `intel_uc_fw_init_early()`, `intel_uc_fw_fetch()`, `intel_uc_check_file_version()`, `intel_uc_fw_init()`, `intel_uc_fw_upload()`, `intel_uc_fw_mark_load_failed()`, `intel_uc_fw_fini()`, `intel_uc_fw_resume_mapping()`, `intel_uc_fw_cleanup_fetch()`, `intel_uc_fw_copy_rsa()`, and `intel_uc_fw_dump()`. Header parsing flows through `__check_ccs_header()`, `check_gsc_manifest()`, and `guc_read_css_info()`.

Control flow: early init validates firmware table ordering, auto-selects the newest matching platform/revision blob, applies module-parameter overrides, and sets the status to selected, disabled, or unsupported. Fetch requests the selected file, falls back through older table entries on `-ENOENT` unless overridden, validates CSS or GSC manifest metadata, checks GuC version width and wanted/selected compatibility, then copies firmware bytes into LMEM or shmem GEM storage. Init pins pages, optionally creates an accessible RSA VMA, and binds the object into a reserved GGTT slot. Upload programs DMA source, WOPCM destination, copy size, and control bits, then marks transfer or load failure.

State and persistence: persistent driver state lives in `struct intel_uc_fw`: selected and wanted paths/versions, status, GEM object, size, GGTT VMA resource, optional RSA VMA, component sizes, DMA start offset, and GSC-header flag. The firmware blob itself is not retained after fetch; contents persist in the GEM object until cleanup.

Dependencies and integration points: depends on Linux firmware loading, i915 GEM memory creation, LMEM/shmem placement, GGTT reserved `uc_fw` node, WOPCM sizing, uncore DMA registers, GSC/HuC binary helpers, GuC submission versioning, and i915 module parameters.

Risks and test signals: risks include wrong table ordering, fallback to incompatible older firmware, user override bypassing strict expected versions, size arithmetic from untrusted firmware headers, GGTT reserved-offset conflicts on multi-GT systems, RSA copy from LMEM mappings during reset, and status transitions masking failed load state. Good signals are firmware table validation logs, missing-file fallback, CSS/GSC manifest rejection tests, MTL GuC/HuC compatibility checks, LMEM and shmem fetch paths, suspend/resume rebind, DMA timeout handling, RSA copy length checks, and debug dumps showing wanted versus selected versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_fw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_fw.h

Purpose: declares the shared firmware state machine and API used by GuC, HuC, and GSC code to reason about firmware availability, loading, and runtime status.

Important APIs/types/functions: defines `enum intel_uc_fw_status`, `enum intel_uc_fw_type`, `struct intel_uc_fw_ver`, `struct intel_uc_fw_file`, and `struct intel_uc_fw`. Inline helpers include status/type stringification, status-to-errno mapping, `intel_uc_fw_is_supported()`, `intel_uc_fw_is_enabled()`, `intel_uc_fw_is_available()`, `intel_uc_fw_is_loadable()`, `intel_uc_fw_is_loaded()`, `intel_uc_fw_is_running()`, `intel_uc_fw_is_in_error()`, `intel_uc_fw_is_overridden()`, `intel_uc_fw_sanitize()`, and upload-size helpers. It exports the implementation functions from `intel_uc_fw.c`.

Control flow and state: the comment block documents the intended state progression from uninitialized through selected, available, loadable, transferred, and running, with terminal disabled, unsupported, missing, error, init fail, and load fail states. The `status` field is exposed read-only through a union to discourage accidental writes outside `intel_uc_fw_change_status()`. `INTEL_UC_RSVD_GGTT_PER_FW` defines static 2 MiB reserved GGTT slices per firmware.

Dependencies and integration points: includes firmware ABI definitions plus i915 device, GEM, and VMA types. Consumers in GuC/HuC/GSC loaders, reset paths, debugfs, and error handling use these helpers to gate upload, authentication, and cleanup.

Risks and test signals: status comparisons rely on enum ordering, so additions must preserve semantic thresholds. `__intel_uc_fw_status()` asserts that callers do not query an uninitialized object. Tests should cover disabled/unsupported gating, status-to-errno mapping, sanitize after reset, upload-size zero before fetch, and compile coverage with and without `CONFIG_DRM_I915_DEBUG_GUC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_fw_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_fw_abi.h

Purpose: defines the CSS firmware header ABI consumed by the i915 uC firmware loader for GuC and HuC DMA-loaded images.

Important APIs/types/functions: `struct uc_css_header` describes module metadata, header and component sizes in dwords, date/time fields, software version fields, `vf_version`, optional GuC private data size, and header info. Macros define bit fields for CSS date, time, and `sw_version`, including `CSS_SW_VERSION_UC_MAJOR`, `CSS_SW_VERSION_UC_MINOR`, and `CSS_SW_VERSION_UC_PATCH`. A `static_assert` fixes the ABI structure size at 128 bytes.

Control flow and state: this file has no runtime control flow. Loader code reads this packed structure directly from firmware bytes, validates that header, uCode, and RSA data are present, calculates upload and RSA sizes, and extracts firmware and GuC submission versions.

Dependencies and integration points: depends only on Linux integer types and build assertions. It is included by `intel_uc_fw.h` and `intel_uc_fw.c`; GSC-managed HuC/GSC blobs use separate manifest parsing but may still contain CSS data at a DMA start offset.

Risks and test signals: every field is part of a binary contract with firmware files, so packing, size, and dword-based arithmetic are critical. Test signals include rejecting too-small blobs, mismatched header size calculations, truncated uCode/RSA payloads, version extraction correctness, and build failures if the struct layout changes unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_fw_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/selftest_guc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/selftest_guc.c

Purpose: provides live GuC submission selftests for CTB recovery, GuC ID exhaustion and stealing, and fast error response handling.

Important APIs/types/functions: helpers are `request_add_spin()` and `nop_user_request()`. Subtests are `intel_guc_scrub_ctbs()`, `intel_guc_steal_guc_ids()`, and `intel_guc_fast_request()`, registered through `intel_guc_live_selftests()`. The code uses `igt_spinner`, request fences, runtime PM wakerefs, context creation, `intel_gt_wait_for_idle()`, `intel_gt_handle_error()`, and `intel_guc_send_nb()`.

Control flow: CTB scrub creates contexts with injected dropped schedule-enable, schedule-disable, and deregister G2H messages, waits for completion, forces GT error handling, then verifies idle. GuC ID stealing temporarily reduces available GuC IDs, blocks submissions behind a spinner until creation returns `-EAGAIN`, releases the spinner, submits again, and verifies `number_guc_id_stolen` increments. Fast request sends an invalid asynchronous H2G while a spinner proves the GPU remains alive, then waits for `fast_response_selftest` to record the expected error response.

State and persistence: tests temporarily mutate context drop flags, `guc->submission_state.num_guc_ids`, `guc->fast_response_selftest`, and request/context references. Cleanup restores the GuC ID count, releases requests and contexts, ends spinners, idles the GT where needed, and drops runtime PM refs.

Risks and test signals: risks include leaked request references on error paths, timeout sensitivity, leaving a spinner active, and failing to restore reduced GuC ID limits. Expected signals are skipped tests on wedged GTs or non-GuC submission, successful idle after reset scrub, observed GuC ID steal count change, and invalid H2G producing a fast response without killing the spinner.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/selftest_guc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/selftest_guc_hangcheck.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/selftest_guc_hangcheck.c

Purpose: live selftest that verifies a hung or reset GuC is detected by engine heartbeat and causes a recorded GPU reset, after which simple work still completes.

Important APIs/types/functions: `nop_request()` creates a kernel no-op request. `intel_hang_guc()` is the subtest and `intel_guc_hang_check()` registers it. It uses `kernel_context()`, `intel_engine_set_heartbeat()`, `igt_spinner`, `intel_reset_guc()`, `GUC_STATUS`, `GS_MIA_IN_RESET`, `i915_reset_count()`, and `intel_selftest_wait_for_rq()`.

Control flow: the test creates a kernel context and an engine context, saves the current reset count and heartbeat interval, sets a short heartbeat, starts a spinner request, explicitly resets the GuC, checks the GuC reset status bit, waits for heartbeat-driven recovery, and verifies the global reset count changed. It then submits a no-op request to prove the engine can still execute.

State and persistence: transient state includes the heartbeat interval, spinner request, context references, runtime PM wakeref, and reset count snapshot. Cleanup ends the spinner, restores heartbeat, releases requests/context, closes the kernel context, and drops the wakeref.

Dependencies and risks: depends on GuC submission, engine heartbeat, reset machinery, GT uncore reads, and selftest scheduler helpers. Risks include heartbeat timing sensitivity, false negatives when no engine is present, and cleanup ordering after reset failures. Test signals are skipped execution on wedged or non-GuC systems, reset-count increment, and successful post-reset no-op completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/selftest_guc_hangcheck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/selftest_guc_multi_lrc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/selftest_guc_multi_lrc.c

Purpose: live GuC selftest for multi-LRC parallel context submission on engine classes with multiple sibling engines.

Important APIs/types/functions: `logical_sort()` orders sibling engines by logical mask. `multi_lrc_create_parent()` creates a parallel parent context with siblings of a class. `multi_lrc_context_unpin()` and `multi_lrc_context_put()` clean parent/child contexts. `multi_lrc_nop_request()` submits a parent request and child requests, marking the last child with `I915_FENCE_FLAG_SUBMIT_PARALLEL`. `intel_guc_multi_lrc_basic()` registers the class loop.

Control flow: the test iterates engine classes, skipping compute and render because breadcrumb handshake is unsupported there. For each class with at least two engines, it creates a parallel context, submits parent and child no-op requests, waits for the parent request, then waits for GT idle before releasing the context tree.

State and persistence: all state is transient: sibling arrays, parent/child context references, request references, and GT idle state. Cleanup explicitly unpins all children and the parent, then drops the parent creation reference.

Dependencies and risks: depends on GuC submission, parallel engine context creation, logical engine masks, request submission ordering, and selftest wait helpers. Risks include sibling ordering mistakes, leaked child context pins on request creation failures, class skip assumptions, and timeout sensitivity. Test signals are skipped operation on wedged/non-GuC systems, clean no-op completion on supported classes, and GT idle within five seconds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/selftest_guc_multi_lrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/Makefile

Purpose: declares the object list that composes the `kvmgt` build when `CONFIG_DRM_I915_GVT` is enabled.

Important entries: includes the researched objects `gvt/aperture_gm.o`, `gvt/cfg_space.o`, `gvt/cmd_parser.o`, `gvt/debugfs.o`, `gvt/display.o`, and `gvt/dmabuf.o`, plus EDID, execlist, framebuffer decoder, firmware, GTT, handlers, interrupt, KVMGT, MMIO, opregion, page tracking, scheduler, trace points, and vGPU core objects.

Control flow and state: no runtime control flow. The build system appends these objects to `kvmgt-$(CONFIG_DRM_I915_GVT)`, determining which translation units participate in the GVT device implementation.

Dependencies and integration points: integrates with the kernel Kbuild infrastructure and the surrounding i915 driver build. Object ordering matters mainly for link inclusion, not initialization order, which is controlled by C code.

Risks and test signals: missing objects produce unresolved symbols for GVT entry points; extra objects can pull unsupported code into configurations. Test signals are successful `CONFIG_DRM_I915_GVT=y/m` builds and absence of unresolved references for vGPU resource, config, command parser, debugfs, display, and DMA-BUF APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/aperture_gm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/aperture_gm.c

Purpose: allocates and frees per-vGPU graphics memory aperture/hidden GM ranges and hardware fence registers from host GGTT resources.

Important APIs/types/functions: public APIs are `intel_vgpu_alloc_resource()`, `intel_vgpu_free_resource()`, `intel_vgpu_reset_resource()`, and `intel_vgpu_write_fence()`. Internal helpers include `alloc_resource()`, `free_resource()`, `alloc_gm()`, `alloc_vgpu_gm()`, `free_vgpu_gm()`, `alloc_vgpu_fence()`, `free_vgpu_fence()`, and `_clear_vgpu_fence()`.

Control flow: allocation first checks requested low GM, high GM, and fence counts against host-reserved limits and accumulated allocations, records aligned sizes, then inserts low and high GM nodes into the GGTT address manager. Fence allocation reserves host fence registers, stores pointers in the vGPU, and clears hardware fence state. Failure unwinds in reverse order. Freeing removes GGTT nodes, clears/unreserves fences under runtime PM, and decrements allocation counters.

State and persistence: modifies `vgpu->gm.low_gm_node`, `vgpu->gm.high_gm_node`, `vgpu->fence.regs`, per-vGPU size fields, and aggregate `gvt->gm`/`gvt->fence` allocation counters. Hardware fence registers are programmed through uncore writes and cleared on reset/free.

Dependencies and risks: depends on GGTT `drm_mm`, i915 fence reservation APIs, runtime PM, MMIO wakerefs, and vGPU config sizing. Risks include counter mismatches if partial allocation unwind is wrong, resource leaks when fence allocation partially fails, races around GGTT mutex ownership, and invalid fence indices. Test signals include overcommit rejection, partial allocation failure cleanup, reset clearing all owned fences, and repeated create/destroy cycles leaving host counters unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/aperture_gm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/cfg_space.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/cfg_space.c

Purpose: emulates a vGPU PCI configuration space, including writable-bit behavior, BAR sizing/programming, PCI command memory enable transitions, power state tracking, opregion hooks, and reset to defaults.

Important APIs/types/functions: public entry points are `intel_vgpu_emulate_cfg_read()`, `intel_vgpu_emulate_cfg_write()`, `intel_vgpu_init_cfg_space()`, and `intel_vgpu_reset_cfg_space()`. Internal helpers include `vgpu_pci_cfg_mem_write()`, `emulate_pci_command_write()`, `emulate_pci_rom_bar_write()`, `emulate_pci_bar_write()`, `map_aperture()`, and `trap_gttmmio()`.

Control flow: reads validate size/range and copy from virtual config memory. Writes validate size/range, then special-case PCI command, ROM BAR, regular BARs, SWSCI, and opregion base writes. Standard config writes apply byte-level RW masks and emulate RW1C status behavior. BAR writes implement all-ones sizing and normal GPA programming, toggling MMIO trapping and aperture mapping according to memory enable state.

State and persistence: stores emulated config bytes in `vgpu_cfg_space(vgpu)`, tracks BAR size and mapped/trapped state in `vgpu->cfg_space.bar[]`, records PMCSR offset, and sets `vgpu->d3_entered` on D3hot writes. Init copies firmware-provided config defaults, hides stolen memory, clears command bits and BAR high halves, sizes BAR metadata from the host PCI device, and locates PM capability.

Dependencies and risks: depends on PCI config constants, GVT firmware config snapshots, opregion emulation, and vGPU BAR helper APIs. Risks include unaligned partial BAR writes, masking mistakes in RW/RW1C bytes, stale aperture trap state across reset, and unsafe casting for small writes. Test signals include BAR all-ones sizing, memory enable/disable transitions, PM D3hot detection, opregion/SWSCI write paths, out-of-range rejection, and reset restoring default config while preserving primary/non-primary class selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/cfg_space.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/cmd_parser.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/cmd_parser.c

Purpose: implements the GVT command parser that scans guest ring buffers, batch buffers, workaround contexts, and engine contexts before host submission. It validates opcodes, command lengths, register access, graphics-memory addresses, display flips, and interrupt-generating commands, while shadowing guest command buffers into host-owned memory.

Important APIs/types/functions: core types are `struct cmd_info`, `struct cmd_entry`, and `struct parser_exec_state`. Public APIs are `intel_gvt_init_cmd_parser()`, `intel_gvt_clean_cmd_parser()`, `intel_gvt_scan_and_shadow_ringbuffer()`, `intel_gvt_scan_and_shadow_wa_ctx()`, `intel_gvt_scan_engine_context()`, and `intel_gvt_update_reg_whitelist()`. Major helpers are `get_opcode()`, `get_cmd_info()`, `cmd_parser_exec()`, `command_scan()`, `cmd_reg_handler()`, `cmd_address_audit()`, `cmd_handler_lri()`, `cmd_handler_lrm()`, `cmd_handler_srm()`, `cmd_handler_pipe_control()`, `cmd_handler_mi_display_flip()`, `cmd_handler_mi_batch_buffer_start()`, `find_bb_size()`, and `perform_bb_shadow()`.

Control flow: initialization builds a hash table from the static opcode table for the current device generation. Ring scanning copies the guest ring into a per-engine scan buffer, seeds parser state at head/tail, and repeatedly decodes and executes command handlers until tail. Batch-buffer-start commands may switch parser state from ring to first- or second-level batch buffers, copy guest batch contents into shmem shadow objects, verify a terminating batch end or chained start, and continue scanning the shadow copy. Command handlers either validate, patch, collect pending events, or reject unsafe commands. The default path advances IP by decoded command length unless a handler owns custom advancement.

State and persistence: modifies `workload->shadow_ring_buffer_va`, `workload->shadow_bb`, `workload->pending_events`, `workload->lri_shadow_mm`, `vgpu->scan_nonprivbb`, vGPU virtual MMIO registers for allowed LRI/display-flip paths, and GVT command accessibility/write-patch whitelists when scanning init contexts. Shadow objects and copied buffers persist as workload-owned artifacts until scheduler cleanup.

Dependencies and integration points: integrates with i915 engine IDs and command encodings, GVT MM/GTT translation, guest GPA reads, vGPU MMIO tracking, display register emulation, tracepoints, scheduler workload submission, default LRC state, and debugfs `scan_nonprivbb`.

Risks and test signals: this is security-sensitive because guest commands can target registers and memory. Risks include incomplete opcode coverage, incorrect length validation, address validation gaps for GGTT/PPGTT/index mode, batch scanning loops without bounds, unsafe register whitelisting, display flip plane mapping mistakes, shadow object lifetime errors, and bypassing nonprivileged batch scanning. Test signals include malicious address rejection, unknown opcode `-EBADRQC`, forbidden register access rejection, PDP LRI remapping, MI interrupt event delivery, display flip MMIO updates and no-op patching, ring wraparound scanning, nested batch buffer restrictions, WA context scanning, init-context whitelist population, and clean parser table init/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/cmd_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/cmd_parser.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/cmd_parser.h

Purpose: exposes the GVT command parser lifecycle and scan entry points to the rest of the GVT scheduler/submission code.

Important APIs/types/functions: declares `GVT_CMD_HASH_BITS`, forward declarations for `struct intel_gvt`, `struct intel_shadow_wa_ctx`, `struct intel_vgpu`, and `struct intel_vgpu_workload`, and prototypes for `intel_gvt_init_cmd_parser()`, `intel_gvt_clean_cmd_parser()`, `intel_gvt_scan_and_shadow_ringbuffer()`, `intel_gvt_scan_and_shadow_wa_ctx()`, `intel_gvt_update_reg_whitelist()`, and `intel_gvt_scan_engine_context()`.

Control flow and state: no executable logic. The prototypes define the parser phases used by GVT: initialize opcode tables, scan/shadow ring buffers, scan/shadow workaround contexts, update the register whitelist from default contexts, scan engine contexts, and clean parser state.

Dependencies and integration points: included by GVT core/scheduler code that owns `intel_gvt`, `intel_vgpu_workload`, and workaround-context objects. The hash-bit constant must match the command table declaration in the owning `intel_gvt` structure.

Risks and test signals: API misuse can skip command validation before workload submission. Test signals are successful GVT builds, parser init before workload execution, cleanup on GVT teardown, and scheduler paths invoking ring, WA context, and engine context scans at the expected points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/cmd_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/debug.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/debug.h

Purpose: centralizes GVT logging macros with consistent prefixes and subsystem tags.

Important APIs/types/functions: defines `gvt_err()`, `gvt_vgpu_err()`, and subsystem debug macros `gvt_dbg_core()`, `gvt_dbg_irq()`, `gvt_dbg_mm()`, `gvt_dbg_mmio()`, `gvt_dbg_dpy()`, `gvt_dbg_el()`, `gvt_dbg_sched()`, `gvt_dbg_render()`, and `gvt_dbg_cmd()`. `gvt_vgpu_err()` prints a vGPU id when a valid `vgpu` variable is in scope, otherwise falls back to a generic GVT prefix.

Control flow and state: no persistent state. The only branching is in `gvt_vgpu_err()`, which checks `IS_ERR_OR_NULL(vgpu)`.

Dependencies and integration points: depends on kernel `pr_err()` and `pr_debug()` plus call-site availability of a `vgpu` symbol for `gvt_vgpu_err()`. It is included broadly by GVT source files to make debug output grepable by subsystem.

Risks and test signals: macro use depends on local variable naming, so using `gvt_vgpu_err()` outside a scope with `vgpu` will fail to compile. Format-string correctness is checked by compiler diagnostics. Runtime signals are correctly prefixed errors and dynamic-debug controllable subsystem messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/debugfs.c

Purpose: creates debugfs controls and diagnostics for GVT and individual vGPUs.

Important APIs/types/functions: public functions are `intel_gvt_debugfs_init()`, `intel_gvt_debugfs_clean()`, `intel_gvt_debugfs_add_vgpu()`, and `intel_gvt_debugfs_remove_vgpu()`. File operations include `vgpu_mmio_diff_show()`, `vgpu_scan_nonprivbb_get()`, `vgpu_scan_nonprivbb_set()`, and `vgpu_status_get()`. Internal diff tracking uses `struct mmio_diff_param` and `struct diff_mmio`.

Control flow: global init creates a `gvt` debugfs root and a `num_tracked_mmio` file. Per-vGPU init creates `vgpuN` directories with `mmio_diff`, `scan_nonprivbb`, and `status` files. `mmio_diff` locks GVT and MMIO context state, reads hardware tracked MMIO under wakeref, compares against vGPU virtual registers, sorts differences by offset, prints them, and frees temporary nodes. The `scan_nonprivbb` attribute controls the command parser mask for nonprivileged batch scanning.

State and persistence: persistent debugfs dentries are stored in `gvt->debugfs_root` and `vgpu->debugfs`. `scan_nonprivbb` directly mutates `vgpu->scan_nonprivbb`; `status` reflects attached/active bits. `mmio_diff` allocates only transient list entries.

Dependencies and risks: depends on debugfs, seq_file helpers, list sorting, GVT MMIO iteration, uncore reads, and scheduler locks. Risks include debugfs unsafe file lifetime, atomic allocation failure during diff collection, lock ordering around GVT and MMIO context locks, and exposing mutable parser behavior through debugfs. Test signals include create/remove under debugfs, accurate MMIO diff counts, scan mask round trips, status bit reporting, and clean recursive removal on vGPU/GVT teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/display.c

Purpose: emulates virtual display presence, DP EDID/DPCD data, hotplug state, vblank interrupts, display register state, and reset/cleanup for GVT vGPUs.

Important APIs/types/functions: public entry points are `intel_vgpu_init_display()`, `intel_vgpu_reset_display()`, `intel_vgpu_clean_display()`, `intel_vgpu_emulate_vblank()`, `vgpu_update_vblank_emulation()`, `intel_vgpu_emulate_hotplug()`, and `pipe_is_enabled()`. Internal helpers include `get_edp_pipe()`, `edp_pipe_is_enabled()`, `setup_virtual_dp_monitor()`, `clean_virtual_dp_monitor()`, `emulate_monitor_status_change()`, `vblank_timer_fn()`, and `emulate_vblank_on_pipe()`.

Control flow: init initializes I2C EDID support, selects a virtual DP port by platform, allocates EDID/DPCD state, seeds fixed EDID and DP 1.2 DPCD data, configures a vblank hrtimer period from refresh rate, and programs virtual display registers to signal a monitor. Vblank timer callbacks request GVT service, which later increments frame counters and triggers vblank/flip-done virtual events under `vgpu_lock`. Hotplug emulation toggles platform-specific virtual ISR/IIR/fuse/hotplug registers and triggers the matching virtual event.

State and persistence: per-port `edid`, `dpcd`, type, resolution id, refresh rate, `vgpu->display.port_num`, and `vgpu->vblank_timer` persist for the vGPU lifetime. Virtual MMIO state is stored in vGPU register arrays and reset by `emulate_monitor_status_change()`.

Dependencies and risks: depends on i915 display register definitions, platform predicates, hrtimers, GVT event service, EDID helpers, and vGPU virtual register accessors. Risks include platform-specific register drift, fixed M/N timing values, unhandled ports/pipes, hrtimer cancellation races, allocation unwind leaks, and mismatched hotplug status bits. Test signals include guest detecting the expected virtual monitor, vblank and flip events firing only for enabled pipes, hotplug connect/disconnect interrupts, cleanup cancelling timers and freeing EDID/DPCD, and reset restoring display presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/display.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/display.h

Purpose: declares GVT virtual display data structures, constants, helper macros, and display emulation entry points.

Important APIs/types/functions: defines `SBI_REG_MAX`, `DPCD_SIZE`, `INTEL_GVT_MAX_UEVENT_VARS`, AUX constants, plane and port enums, `enum intel_vgpu_edid`, `struct intel_vgpu_sbi`, `struct intel_vgpu_dpcd_data`, `struct intel_vgpu_port`, and `struct intel_vgpu_vblank_timer`. Inline helpers provide EDID labels and x/y resolution. Macros include `intel_vgpu_port()`, `intel_vgpu_has_monitor_on_port()`, and `intel_vgpu_port_is_dp()`.

Control flow and state: no complex runtime flow in the header. It defines the persistent per-vGPU display state consumed by `display.c`: EDID and DPCD validity, port type/id, refresh rate in millihertz, and hrtimer period.

Dependencies and integration points: depends on Linux hrtimer/types and GVT structs. Included by display, EDID, framebuffer decoder, and other GVT paths that need to query ports or trigger display events.

Risks and test signals: enum values must stay consistent with array sizes such as `GVT_EDID_NUM` and `GVT_PORT_MAX`. The EDID helper defaults return zero or empty string for invalid IDs, so callers must validate resolution before use. Test signals are compile coverage across GVT display users, correct resolution helper values, monitor detection macros, and hrtimer state carried in `struct intel_vgpu_vblank_timer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/display_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/display_helpers.h

Purpose: provides small compatibility wrappers between GVT code and i915 display-device MMIO offset helpers.

Important APIs/types/functions: macros wrap `intel_display_device_mmio_base()`, `intel_display_device_pipe_offset()`, `intel_display_device_trans_offset()`, and `intel_display_device_cursor_offset()`. `gvt_for_each_pipe(display, __p)` iterates only valid pipes according to `intel_display_device_pipe_valid()`.

Control flow and state: no persistent state. The pipe iteration macro expands to a nested `for` plus `for_each_if` filter. A documented FIXME notes that some GVT callers pass transcoders to pipe-based addressing, currently cast to `enum pipe` because `TRANSCODER_A..D` map one-to-one with `PIPE_A..D`; `TRANSCODER_EDP` remains a caveat.

Dependencies and integration points: depends on `display/intel_gvt_api.h` and is used by GVT display and command parser code that needs platform-correct display offsets.

Risks and test signals: the transcoder-to-pipe cast is a known correctness risk for eDP or future display topologies. Test signals include display emulation on platforms with varying valid pipe masks, no out-of-range virtual register accesses, and review of any new TRANSCODER_EDP usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/display_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/dmabuf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/dmabuf.c

Purpose: exposes vGPU primary or cursor planes as DMA-BUF file descriptors by wrapping guest framebuffer memory in proxy i915 GEM objects.

Important APIs/types/functions: public APIs are `intel_vgpu_query_plane()`, `intel_vgpu_get_dmabuf()`, and `intel_vgpu_dmabuf_cleanup()`. GEM object operations are `vgpu_gem_get_pages()`, `vgpu_gem_put_pages()`, and `vgpu_gem_release()` in `intel_vgpu_gem_ops`. Other helpers include `vgpu_create_gem()`, `vgpu_get_plane_info()`, `pick_dmabuf_by_info()`, `pick_dmabuf_by_num()`, `update_fb_info()`, `validate_hotspot()`, `dmabuf_obj_get()`, and `dmabuf_obj_put()`.

Control flow: query validates VFIO flags, decodes the requested primary/cursor plane, checks alignment and GGTT range, reuses an existing matching dmabuf object or allocates a new one with an IDR id, and returns plane metadata plus `dmabuf_id`. `get_dmabuf` looks up the id, creates a read-only proxy GEM object, exports it via i915 PRIME, converts it to an fd, adjusts the query-held init reference, and drops the local GEM reference. GEM page population reads host GGTT PTEs for the guest framebuffer, pins guest DMA pages, builds an sg table, and unmaps on put.

State and persistence: maintains `vgpu->dmabuf_obj_list_head`, `vgpu->object_idr`, per-object `kref`, `initref`, `dmabuf_id`, and copied framebuffer info. Cleanup detaches objects from the live vGPU, removes IDs, and drops any outstanding query refs while exported DMA-BUFs can release later as orphaned objects.

Dependencies and risks: depends on VFIO gfx plane ABI, i915 GEM PRIME export, guest page pin/unmap helpers, framebuffer decoders, GGTT validation, DRM format modifiers, and vGPU locks. Risks include sg-table count mistakes, `fb_info->size` used as sg iteration count in put path, refcount handoff between query/get/release, orphan object lifetime after vGPU removal, unsupported modifiers, and stale framebuffer reuse matching. Test signals include probe-only query, invalid flag rejection, primary/cursor metadata correctness, duplicate query reuse, fd export success, close-time unpin/unmap, vGPU cleanup with open fds, and malformed framebuffer range rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/dmabuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/dmabuf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/dmabuf.h

Purpose: declares the GVT DMA-BUF plane-export data structures and public query/get/cleanup APIs.

Important APIs/types/functions: `struct intel_vgpu_fb_info` records guest framebuffer start GMA/GPA, DRM format and modifier, width, height, stride, size, cursor position/hotspot, and owning DMA-BUF object. `struct intel_vgpu_dmabuf_obj` records the owning vGPU, framebuffer info, `dmabuf_id`, kref, initial-reference flag, and list node. Public functions are `intel_vgpu_query_plane()`, `intel_vgpu_get_dmabuf()`, and `intel_vgpu_dmabuf_cleanup()`.

Control flow and state: no executable logic. The structures define the persistent bridge between VFIO plane queries and later fd export. Query creates or reuses `intel_vgpu_dmabuf_obj`; get converts it to a GEM/PRIME DMA-BUF; cleanup detaches list/IDR state when the vGPU is destroyed.

Dependencies and integration points: depends on Linux kref/list types, VFIO-facing implementation in `dmabuf.c`, GVT framebuffer decoders, and i915 GEM PRIME. Consumers use `dmabuf_id` as the handoff token between query and get ioctls.

Risks and test signals: lifetime is subtle because exported DMA-BUFs can outlive the vGPU; `vgpu` may become NULL and cleanup must handle orphaned objects. Test signals include correct kref behavior across query/get/close, stable metadata copied in `intel_vgpu_fb_info`, cursor hotspot sentinel handling, and no IDR/list leaks after cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/dmabuf.h -->
