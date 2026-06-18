# subset-b-003619 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/edid.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/edid.c

## Purpose
`edid.c` emulates the I2C paths a guest display driver uses to read monitor EDID data from an Intel GVT vGPU. It handles two transport styles: legacy GMBUS MMIO registers for non-DP ports and I2C-over-AUX transactions for DP ports. The file translates guest register writes into updates of `vgpu->display.i2c_edid`, returns bytes from the configured virtual port EDID block, and mirrors enough GMBUS/AUX status bits in vGPU virtual MMIO to make the guest driver believe hardware completed the transaction.

## Important APIs, Functions, And Types
The exported entry points are `intel_gvt_i2c_handle_gmbus_read()`, `intel_gvt_i2c_handle_gmbus_write()`, `intel_gvt_i2c_handle_aux_ch_write()`, and `intel_vgpu_init_i2c_edid()`. Internal helpers include `edid_get_byte()` for bounds-checked EDID byte consumption, platform pin decoders for BXT/CNP/default GMBUS0 layouts, `reset_gmbus_controller()`, and per-register emulators for GMBUS0 through GMBUS3. The implementation depends on the EDID state structs declared in `edid.h`, display port helpers such as `intel_vgpu_has_monitor_on_port()`, `intel_vgpu_port_is_dp()`, and virtual register access through `vgpu_vreg()`/`vgpu_vreg_t()`.

## Control Flow
For GMBUS, a guest first writes GMBUS0. `gmbus0_mmio_write()` stores the value, resets EDID state, decodes the selected pin to a GVT port, marks the state as `I2C_GMBUS`, and sets `edid_available` only if a monitor exists on a non-DP port. A later GMBUS1 write parses target address, byte count, index, and cycle type. EDID address `0x50` selects the target, index cycles set `current_edid_read`, stop cycles reset state, and data cycles move the GMBUS emulation to active/data phase. GMBUS3 reads then pack up to four EDID bytes into the data register and advance the current read cursor; the final read moves the emulation to wait or idle and reinitializes the high-level EDID state.

For AUX, `intel_gvt_i2c_handle_aux_ch_write()` only interprets writes to AUX control. It reads the AUX message from the following DATA register, decodes the target address and operation, synthesizes DONE plus reply size in AUX control, and places an ACK or one EDID byte in AUX data. Message length 3 is treated as start/restart/stop selection, while length 4 plus read opcode returns a byte. Non-control AUX data writes are simply mirrored into virtual MMIO.

## State And Persistence
State is entirely per-vGPU and transient: `state`, `port`, `target_selected`, `edid_available`, `current_edid_read`, GMBUS phase/cycle metadata, and AUX MOT flags live in `vgpu->display.i2c_edid`. EDID contents are stored on the selected virtual display port, not in this file. The emulation also persists protocol-visible status in virtual GMBUS/AUX MMIO registers. There is no on-disk persistence.

## Dependencies And Integration Points
This file integrates with the GVT MMIO dispatcher for GMBUS register reads/writes and with display register emulation for AUX writes. It depends on i915 display register definitions, DP AUX constants, platform checks (`IS_BROXTON`, `IS_COFFEELAKE`, `IS_COMETLAKE`), and GVT display configuration that supplies monitor presence and EDID blocks.

## Risks And Edge Cases
The logic intentionally supports only EDID reads. Unsupported target addresses are logged and ignored, GMBUS3 writes warn, and AUX write operations are mostly ignored. Protocol ordering matters: `edid_get_byte()` returns zero and logs if the guest reads before target selection, after the 128-byte block, or without available EDID. Port-pin mappings are platform-specific and stale mappings can break hotplug/EDID discovery. Partial or unusual guest I2C sequences may observe simplified status behavior because the implementation collapses hidden hardware phases.

## Test Signals
Useful validation includes guest boot/display probing on HDMI and DP virtual ports, EDID block reads of exactly 128 bytes, index-mode reads, stop/restart behavior, no-monitor reads producing error status, and DP AUX I2C-over-AUX reads returning ACK plus byte data. Kernel logs should be checked for `gvt_vgpu_err()` warnings about improper sequences, unsupported target addresses, or missing EDID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/edid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/edid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/edid.h

## Purpose
`edid.h` defines the public data model and entry points for GVT EDID/I2C emulation. It describes the emulated EDID block, the GMBUS transaction state machine visible to GVT, the AUX channel state needed for I2C-over-AUX, and the functions called by MMIO/display emulation code.

## Important APIs, Types, And Constants
`EDID_SIZE` is fixed at 128 bytes and `EDID_ADDR` is the standard 7-bit EDID I2C address `0x50`. `struct intel_vgpu_edid_data` stores a validity flag and one EDID block. `enum gmbus_cycle_type` mirrors the GMBUS cycle encodings used by GMBUS1. `enum gvt_gmbus_phase` keeps only phases visible through GMBUS MMIO: idle, data, and wait. `struct intel_vgpu_i2c_gmbus` stores total byte count, cycle type, and phase. `struct intel_vgpu_i2c_aux_ch` tracks I2C-over-AUX MOT state. `enum i2c_state` distinguishes unspecified, GMBUS, and AUX flows. `struct intel_vgpu_i2c_edid` combines all per-vGPU EDID read state.

The exported functions are `intel_vgpu_init_i2c_edid()`, `intel_gvt_i2c_handle_gmbus_read()`, `intel_gvt_i2c_handle_gmbus_write()`, and `intel_gvt_i2c_handle_aux_ch_write()`.

## Control Flow And State
This header encodes the invariant that GMBUS and AUX EDID sequences cannot interleave. Callers are expected to initialize or reset `intel_vgpu_i2c_edid` when a new transaction starts, when a stop is observed, or when the emulated display path changes. The active state records selected port, whether the guest has addressed EDID, whether EDID is available on that port, and how many bytes have been consumed.

## Dependencies And Integration Points
The header is included by `gvt.h`, which embeds `struct intel_vgpu_i2c_edid` in `struct intel_vgpu_display`. It is also consumed by `edid.c` and any MMIO dispatcher that forwards GMBUS/AUX accesses. It only includes Linux basic types and forward-declares `struct intel_vgpu`, keeping the interface light.

## Risks And Test Signals
The state machine is intentionally minimal and exposes only the hardware phases the emulation uses. Any future extension for multi-block EDID, DDC segment addressing, or richer AUX behavior would need new fields and stricter sequencing rules. Tests should confirm state reset clears port, target, availability, byte cursor, GMBUS metadata, and AUX MOT flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/edid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/execlist.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/execlist.c

## Purpose
`execlist.c` emulates Intel execlist submission state for a vGPU. It converts guest ELSP descriptor writes into GVT workload objects, updates virtual execlist status and context status buffers, and synthesizes context-switch interrupts so the guest driver sees the expected scheduling lifecycle.

## Important APIs And Functions
The central exported API is `intel_vgpu_submit_execlist(vgpu, engine)`. The file also exports `intel_vgpu_execlist_submission_ops`, whose `init`, `reset`, and `clean` callbacks wire this implementation into `struct intel_vgpu_submission_ops`. Internal control is split between `emulate_execlist_schedule_in()`, `emulate_execlist_ctx_schedule_out()`, `emulate_execlist_status()`, `emulate_csb_update()`, `submit_context()`, `prepare_execlist_workload()`, and `complete_execlist_workload()`.

## Control Flow
`intel_vgpu_submit_execlist()` reads two context descriptors from `execlist->elsp_dwords`, rejects invalid descriptor zero or non-privileged GGTT submissions, and creates one workload for each valid descriptor. The first descriptor in a bundle carries `emulate_schedule_in=true`, causing `prepare_execlist_workload()` to update virtual execlist state before workload execution.

Schedule-in picks the next virtual slot from the current status register. If no slot is running, the new slot becomes running and an idle-to-active CSB event is emitted. If an existing context can be lite-restored/preempted by the new descriptor, the pending slot becomes running and a lite-restore/preempted CSB event is emitted. Otherwise the new slot is stored as pending and the status queue-full bit is updated.

On workload completion, `complete_execlist_workload()` skips schedule-out if the workload failed, its engine is resetting, or the next queued workload has the same context. Otherwise `emulate_execlist_ctx_schedule_out()` emits element-switch or active-to-idle/context-complete events and promotes pending work when needed.

## State And Persistence
State is per vGPU and per engine in `vgpu->submission.execlist[]`: two virtual slots, running slot, pending slot, running context pointer, and cached ELSP dwords. The code updates virtual MMIO status registers and, when the guest HW status page can be translated through GGTT, mirrors CSB data and write pointer into guest memory with `intel_gvt_write_gpa()`. No state survives vGPU destruction except normal guest-visible memory effects.

## Dependencies And Integration Points
The file depends on GVT workload creation/queueing, engine iteration and IDs from i915, GTT translation for HWSP writes, virtual event injection for context-switch interrupts, and descriptor/status layouts from `execlist.h`. It integrates with scheduler code through workload `prepare` and `complete` callbacks.

## Risks And Edge Cases
The slot model is a simplified hardware emulation and is sensitive to descriptor equality (`context_id` and `lrca`) and running-context pointer validity. Bad ELSP descriptors return `-EINVAL`, queue-full state rejects new slots, and missing HWSP translation silently limits updates to MMIO CSB state. Incorrect pending/running transitions can deadlock guest scheduling or generate wrong interrupt ordering.

## Test Signals
Signals include guest GPU workloads completing without hangs, context-switch interrupts arriving, CSB write pointer advancing modulo the emulated buffer, lite-restore paths when identical contexts are submitted, pending slot behavior under two-descriptor submissions, and clean reset of execlist state on engine reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/execlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/execlist.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/execlist.h

## Purpose
`execlist.h` declares the packed register/descriptor views and per-engine state structures used by GVT execlist emulation. It provides bitfield mappings for context descriptors, execlist status registers, context status pointers, and CSB entries.

## Important Types
`struct execlist_ctx_descriptor_format` overlays the low descriptor dword with valid, restore, addressing, coherency, fault, privilege, and LRCA fields, and treats the upper dword as `context_id`. `struct execlist_status_format` maps active/valid bits, queue-full state, write/current pointers, and current context id. `struct execlist_context_status_pointer_format` maps CSB read/write pointers and mask bits. `struct execlist_context_status_format` maps idle-to-active, preempted, element-switch, active-to-idle, context-complete, wait reasons, and lite-restore status. `struct execlist_ring_context` models the first 52 dwords of logical ring context image with MMIO address/value pairs. `struct intel_vgpu_execlist` stores two slots plus running/pending pointers and cached ELSP dwords.

## Control Flow And State
The header has no executable control flow beyond declarations, but it defines the state that `execlist.c` mutates during submit, schedule-in, schedule-out, reset, and cleanup. Two descriptors form one ELSP submission bundle; two virtual slots represent running and pending hardware execlists.

## Dependencies And Integration Points
It includes Linux types and forward references `struct intel_vgpu`/`struct intel_engine_cs` indirectly through users. The public API `intel_vgpu_submit_execlist()` is called by submission/MMIO code after ELSP writes are collected.

## Risks And Test Signals
Bitfield layout must match the guest-visible hardware ABI. Any compiler/layout or hardware-generation mismatch would corrupt descriptor interpretation and status reporting. Tests should cover descriptor decoding, CSB bit layout, and ABI compatibility with the i915 guest driver used by the supported platform generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/execlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/fb_decoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/fb_decoder.c

## Purpose
`fb_decoder.c` decodes guest-programmed display plane registers into host-readable framebuffer metadata for GVT. It extracts primary plane and cursor plane format, dimensions, tiling, stride, base graphics address, translated guest physical address, and cursor position/hotspot.

## Important APIs And Functions
The exported APIs are `intel_vgpu_decode_primary_plane()` and `intel_vgpu_decode_cursor_plane()`. Internal helpers include `bdw_format_to_drm()`, `skl_format_to_drm()`, `intel_vgpu_get_stride()`, `get_active_pipe()`, and `cursor_mode_to_drm()`. Static format tables map hardware encodings to DRM fourcc formats and bits-per-pixel.

## Control Flow
Both decoders first locate the active pipe by scanning `pipe_is_enabled()`. Primary decode reads `DSPCNTR`, determines whether the plane is enabled, decodes format differently for Gen9+ universal plane encodings versus Broadwell-era display encodings, validates nonzero bpp, reads `DSPSURF`, validates the GMA range, translates the base through `intel_vgpu_gma_to_gpa()`, computes stride from `DSPSTRIDE` and tiling mode, reads width/height from `PIPESRC`, and reads X/Y offsets from `DSPTILEOFF`.

Cursor decode reads `CURCNTR`, rejects disabled or unsupported modes, fills ARGB cursor format metadata, validates and translates `CURBASE`, decodes signed X/Y position from `CURPOS`, and reads paravirtual cursor hotspot registers from the vGT interface.

## State And Persistence
The file does not own persistent state. It samples virtual display registers from `vgpu->mmio.vreg`, performs GGTT translation through `vgpu->gtt.ggtt_mm`, and writes a caller-provided plane descriptor. The descriptor is a snapshot and can become stale after a guest modeset or flip.

## Dependencies And Integration Points
Dependencies include i915 display register definitions, DRM fourcc constants, GVT display helpers, GTT address validation/translation, and vGT paravirtual info registers for cursor hotspots. Consumers are typically display, dmabuf, or mediated-device paths that need to expose guest framebuffer content to host userspace.

## Risks And Edge Cases
Only primary and cursor planes are exported despite sprite-related structures in the header. Unsupported pixel formats, invalid GM addresses, missing active pipes, and failed GMA-to-GPA translation return errors. Stride calculation is generation- and tiling-dependent; Y/Yf tiled and unusual bpp combinations are easy regression points. The active-pipe scan returns the first enabled pipe only, so multi-pipe scenarios may need higher-level coordination.

## Test Signals
Validation should exercise BDW and SKL+ format encodings, linear/X/Y/Yf tiling, cursor modes 64/128/256 ARGB, disabled plane paths returning `-ENODEV`, invalid GGTT mappings returning `-EINVAL`, and successful decoded GPA matching the guest GGTT entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/fb_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/fb_decoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/fb_decoder.h

## Purpose
`fb_decoder.h` defines register bit masks, event enums, display port enums, and decoded plane metadata structures for GVT framebuffer extraction. It is the public interface for code that wants to decode a vGPU's guest display state.

## Important Types And APIs
The header declares `enum GVT_FB_EVENT` for modeset and flip notifications, `enum DDI_PORT` for DDI port identity, `struct intel_vgpu_primary_plane_format`, `struct intel_vgpu_sprite_plane_format`, and `struct intel_vgpu_cursor_plane_format`. The primary and cursor structs include enabled state, bpp, DRM format, guest graphics base, translated GPA, dimensions, stride/offsets, and cursor position/hotspot fields. Public APIs are `intel_vgpu_decode_primary_plane()` and `intel_vgpu_decode_cursor_plane()`.

## Control Flow And State
The header itself is declarative. Its masks are consumed by `fb_decoder.c` to isolate fields from display registers such as plane control, source size, stride, sprite/cursor position, and cursor alpha/mode bits. The decoded structs are snapshots populated by callers and are not retained by the decoder.

## Dependencies And Integration Points
It forward-declares `struct intel_vgpu` and includes Linux types. The structures integrate with dmabuf/display export code and with the GTT layer through `base_gpa` fields filled by the decoder implementation.

## Risks And Test Signals
Register masks are generation-specific and must stay aligned with i915 display register definitions. The sprite struct is declared but no sprite decoder is exported in this file set, so users should not assume sprite decode coverage. Tests should verify mask extraction boundaries for maximum width/height/position fields and ABI stability of the decoded structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/fb_decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/firmware.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/firmware.c

## Purpose
`firmware.c` loads or exposes the GVT "golden hardware state" firmware used to seed vGPU PCI config space and MMIO state. If a matching firmware blob exists under `i915/gvt`, it verifies and copies the blob into `gvt->firmware`; if not, it creates a sysfs binary attribute so administrators can read out the current hardware state and install it as firmware.

## Important APIs And Functions
The exported lifecycle functions are `intel_gvt_load_firmware()` and `intel_gvt_free_firmware()`. Internal helpers include `expose_firmware_sysfs()`, `clean_firmware_sysfs()`, and `verify_firmware()`. `struct gvt_firmware_header` defines blob metadata: magic, CRC32, version, config/MMIO sizes, offsets, and payload.

## Control Flow
Load allocates buffers for config space and MMIO, builds a firmware path from PCI vendor/device/revision, and calls `request_firmware()`. Missing firmware is not fatal: execution falls through to `expose_firmware_sysfs()` and returns success after exposing a generated blob. If firmware is found, `verify_firmware()` checks magic, version, CRC32 over the payload metadata/data region, expected config/MMIO sizes, and PCI vendor/device/revision fields in the embedded config space. Verified blobs are copied into `firmware->cfg_space` and `firmware->mmio`, released, and marked `firmware_loaded=true`.

## State And Persistence
Runtime state lives in `gvt->firmware.cfg_space`, `gvt->firmware.mmio`, and `firmware_loaded`. The generated sysfs binary attribute stores a vmalloc buffer in `bin_attr_gvt_firmware.private` until cleanup. On-disk persistence is delegated to the Linux firmware loader path; this code never writes the firmware file itself.

## Dependencies And Integration Points
The file uses Linux firmware loading, CRC32, sysfs binary attributes, PCI IDs, and initial i915 vGPU state arrays (`i915->vgpu.initial_cfg_space`, `initial_mmio`). Other GVT initialization code consumes `gvt->firmware` after load. Device cleanup must call `intel_gvt_free_firmware()` to release buffers or remove the sysfs attribute.

## Risks And Edge Cases
If firmware is absent, GVT still returns success but depends on sysfs extraction and later firmware installation for stable future loads. Verification assumes the blob is large enough for the header and offsets; malformed firmware with inconsistent offsets is only partially guarded by size/value checks. The cleanup path removes the sysfs file only when firmware was not loaded, so `firmware_loaded` must be accurate.

## Test Signals
Tests should cover successful firmware load, missing firmware sysfs exposure, invalid CRC/version/device rejection with fallback exposure, correct sysfs blob size and CRC, and cleanup without leaks across both loaded and exposed modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/gtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/gtt.c

## Purpose
`gtt.c` implements GVT graphics translation table virtualization. It emulates guest GGTT MMIO reads/writes, shadows guest per-process GTT page tables into host-addressable shadow page tables, translates guest graphics memory addresses to guest physical addresses, manages scratch pages, tracks guest page-table writes, and restores host GGTT state after power management.

## Important APIs And Functions
Device-level APIs are `intel_gvt_init_gtt()`, `intel_gvt_clean_gtt()`, and `intel_gvt_restore_ggtt()`. Per-vGPU APIs include `intel_vgpu_init_gtt()`, `intel_vgpu_clean_gtt()`, `intel_vgpu_reset_ggtt()`, `intel_vgpu_invalidate_ppgtt()`, `intel_vgpu_destroy_all_ppgtt_mm()`, `intel_vgpu_emulate_ggtt_mmio_read()`, `intel_vgpu_emulate_ggtt_mmio_write()`, `intel_vgpu_gma_to_gpa()`, `intel_vgpu_get_ppgtt_mm()`, `intel_vgpu_put_ppgtt_mm()`, `intel_vgpu_pin_mm()`, `intel_vgpu_unpin_mm()`, `intel_vgpu_flush_post_shadow()`, and `intel_vgpu_sync_oos_pages()`.

The main internal subsystems are Gen8 PTE operations, GMA index operations, shadow page-table allocation/population/invalidation, GGTT virtual/host entry management, partial GGTT PTE write handling, out-of-sync page-table optimization, and scratch page tree setup.

## Control Flow
Initialization sets Gen8 operation tables, allocates a device scratch page, optionally preallocates out-of-sync pages, and initializes LRU locking. A vGPU then creates a GGTT `intel_vgpu_mm`, allocates virtual GGTT plus saved host aperture/hidden arrays, resets host GGTT entries to the scratch page, initializes page-table tracking lists, and builds per-type scratch page tables.

For GGTT MMIO writes, the code normalizes the offset, rejects invalid access sizes, ignores ballooned-out GM ranges, handles split 4-byte updates by queuing partial PTE state, maps present guest GFNs to DMA addresses, falls back to scratch on mapping failure, updates the virtual guest GGTT copy, unmaps the previous host mapping, writes the host GGTT PTE, and invalidates GGTT. It also invalidates cached last context descriptors if their LRCA entry was overwritten.

For PPGTT, `intel_vgpu_get_ppgtt_mm()` finds or creates an MM object keyed by guest PDP roots. Creation shadows roots immediately if the vGPU is attached. Shadowing walks guest page tables, allocates `intel_vgpu_ppgtt_spt` pages, registers write protection, recursively populates child tables, maps leaf guest pages, splits unsupported 64K entries into 4K PTEs, and splits 2M entries when host mapping cannot support them. Guest page-table writes enter `ppgtt_write_protection_handler()`, which updates or defers shadow entries depending on write size. Before workload submission, post-shadow and out-of-sync lists are flushed back into consistent shadow state.

`intel_vgpu_gma_to_gpa()` translates through GGTT by reading the virtual GGTT PTE. For PPGTT it walks shadow roots and child SPTs using GMA index helpers, reading the guest final entry at the last level so the returned address is a guest physical address.

## State And Persistence
Global state in `gvt->gtt` includes PTE/GMA ops, scratch page, optional out-of-sync free/use lists, and a PPGTT MM LRU list protected by `ppgtt_mm_lock`. Per-vGPU state includes `ggtt_mm`, PPGTT MM list, SPT radix tree keyed by shadow MFN, out-of-sync and post-shadow lists, and per-level scratch page tree. Host GGTT aperture/hidden PTE arrays are saved per vGPU for restore. No disk persistence exists; state is reconstructed during driver/vGPU init and restored to hardware on resume.

## Dependencies And Integration Points
The implementation depends on i915 GGTT structures, MMIO runtime power helpers, VFIO DMA read/write from `gvt.h`, GVT page tracking, DMA map/unmap cache helpers, tracepoints, execlist submission state, and guest workload submission ordering. It is on the hot path for framebuffer decoding, command parsing, context shadowing, and display base translation.

## Risks And Edge Cases
This is a high-risk memory translation layer. Incorrect refcounts or invalidation can leak DMA mappings or leave stale host PTEs. Partial PTE writes must not expose half-written shadow mappings. 64K and 2M splitting paths must clean up already-mapped pages on failure. Out-of-sync mode is disabled by default but, if enabled, weak synchronization before workload submission can produce stale shadows. LRU reclaim cannot invalidate pinned MMs. `intel_vgpu_gma_to_gpa()` reports a generic "invalid mm type" message even for translation failures, so diagnostics can be misleading.

## Test Signals
Important signals include GGTT read/write emulation for 4- and 8-byte accesses, split PTE updates, invalid GM range handling, DMA map failure fallback to scratch, PPGTT creation for 3-level and 4-level roots, guest page-table write protection updates, post-shadow flush before workload submission, 64K/2M split coverage, MM pin/LRU reclaim behavior, clean vGPU teardown with empty SPT tree, suspend/resume GGTT restore, and framebuffer GMA-to-GPA translation matching guest mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/gtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/gtt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/gtt.h

## Purpose
`gtt.h` declares the GVT GTT virtualization interface and the core data structures shared by GGTT/PPGTT emulation. It defines generic GTT entry operations, GMA index operations, MM objects, shadow page-table objects, scratch pages, out-of-sync pages, and exported functions used by submission, display, command parsing, and vGPU lifecycle code.

## Important Types
`struct intel_gvt_gtt_entry` wraps a 64-bit PTE value and GVT type. `struct intel_gvt_gtt_pte_ops` abstracts PTE read/write, present/PSE/IPS/64K-split bits, and PFN access. `struct intel_gvt_gtt_gma_ops` abstracts GGTT and PPGTT GMA index extraction. `struct intel_gvt_gtt` is device-global GTT state. `enum intel_gvt_gtt_type` enumerates GGTT PTEs, PPGTT leaf entries, root entries, and page-table levels. `struct intel_vgpu_mm` represents either a GGTT MM with virtual/host PTE arrays and partial write list or a PPGTT MM with guest/shadow PDPs, root type, shadowed flag, and list links. `struct intel_vgpu_ppgtt_spt` represents a shadow page table and its associated guest page tracking metadata.

## Control Flow And State
The header encodes the reference model: MM objects are `kref` managed with a separate pin count; PPGTT shadow pages are tracked in a radix tree; guest page table writes may be post-shadowed or moved to out-of-sync pages; GGTT state is split into guest-visible virtual entries and host hardware entries. Inline helpers `intel_vgpu_mm_get()`, `intel_vgpu_mm_put()`, and `intel_vgpu_destroy_mm()` define lifetime transitions.

## Dependencies And Integration Points
It includes `gt/intel_gtt.h`, Linux kref/mutex/radix tree APIs, and forward-declares GVT objects. The exported APIs are consumed by `gtt.c`, execlist/context submission, command parser paths that need PPGTT roots, display decoders that translate framebuffer bases, and vGPU lifecycle cleanup/reset code.

## Risks And Test Signals
Type enum ordering is semantically significant because implementation helpers test ranges and derive child/scratch types by arithmetic. Any new type must preserve those assumptions or update `gtt.c`. Struct fields carry concurrency and lifetime invariants; tests should stress kref/pin interactions, radix-tree cleanup, partial PTE list cleanup, and all exported init/clean/reset APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/gtt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/gvt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/gvt.h

## Purpose
`gvt.h` is the central private header for Intel GVT-g vGPU support. It aggregates subsystem headers, defines core device and vGPU structures, global resource accounting, MMIO metadata, firmware state, submission state, display state, memory aperture helpers, lifecycle APIs, and utility helpers for GPA access and runtime MMIO access.

## Important Types And APIs
Key structs include `intel_gvt_device_info` for platform limits and MMIO/GTT geometry, `intel_vgpu` for each mediated vGPU, `intel_gvt` for device-global state, `intel_vgpu_submission` for per-engine workload/execlist state, `intel_vgpu_display` for EDID/port/SBI state, `intel_vgpu_cfg_space`, `intel_vgpu_irq`, `intel_vgpu_gm`, `intel_gvt_mmio`, and `intel_gvt_firmware`. It declares vGPU lifecycle APIs, resource allocation/reset/free APIs, firmware load/free, opregion/EDID setup, config-space emulation, hotplug, workload scanning, failsafe mode, debugfs hooks, page tracking, and DMA map/unmap helpers.

## Control Flow And State
This header establishes the object graph used by the implementation files in this subset. `intel_gvt` owns global locks, `intel_gt`, IDR of vGPUs, global MMIO/GTT/firmware/IRQ/scheduler state, service thread state, command table, mdev type metadata, and debugfs root. Each `intel_vgpu` owns its VFIO device, locks, status bits, resource slices, virtual config/MMIO, GTT state, display state, submission queues, page tracking, dmabuf state, MSI trigger, and DMA mapping caches. Inline helpers manipulate service requests, PCI BAR config fields, MMIO attribute flags, and guest physical memory reads/writes.

## Dependencies And Integration Points
`gvt.h` includes almost every GVT subsystem header and i915 GT/display/VFIO/KVM page-tracking interfaces. The files in this work item depend heavily on it: `edid.c` uses display and virtual register fields, `execlist.c` uses submission/workload/event state, `fb_decoder.c` uses display/GTT helpers, `firmware.c` uses device info and firmware buffers, and `gtt.c` uses aperture macros, GPA access, runtime PM wrappers, and DMA/page-track declarations.

## Risks And Edge Cases
Because it is a central header, changes have broad compile and ABI impact inside the driver. Several macros perform direct pointer arithmetic into virtual MMIO/config-space buffers and assume valid offsets/alignment. GM aperture/hidden range macros are used for security-sensitive address validation. `intel_gvt_read_gpa()` and `intel_gvt_write_gpa()` require the vGPU to be attached and pass through VFIO DMA operations; callers must handle `-ESRCH` and guest memory faults.

## Test Signals
Compile coverage across all GVT objects is essential after any header change. Runtime signals include correct vGPU creation/destruction, resource accounting, MMIO attribute behavior, guest config reads/writes, GM range validation, GPA read/write failure handling for detached vGPUs, service thread wakeups, and no regressions in EDID, execlist, framebuffer decode, firmware, and GTT paths that consume these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/gvt.h -->
