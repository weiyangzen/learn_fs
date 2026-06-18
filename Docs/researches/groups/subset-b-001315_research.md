# subset-b-001315 research

Work item: `subset-b-001315`

Scope: AMDGPU discovery, display, DMA-BUF, and doorbell support files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c

## Purpose

`amdgpu_discovery.c` is the AMDGPU hardware discovery and IP-block selection implementation. It loads the IP discovery binary from firmware, VRAM TMR, or system memory, validates binary and table signatures/checksums, extracts register base addresses and IP versions, applies harvest information, exposes discovery topology through sysfs and devcoredump, and finally registers the correct AMDGPU IP block implementations for the detected ASIC.

This file is a boot-time bridge between hardware/firmware discovery data and the rest of the driver. Most later AMDGPU subsystems depend on `adev->reg_offset`, `adev->ip_versions`, masks such as `adev->gfx.xcc_mask` and `adev->sdma.sdma_mask`, family/APU flags, and function tables selected here.

## Important APIs, types, and functions

- `amdgpu_discovery_set_ip_blocks(struct amdgpu_device *adev)` is the public entry point. It handles legacy fixed tables for older ASICs, dynamic discovery for newer/default ASICs, sysfs setup, family flag selection, NBIO/HDP/DF/SMUIO/LSDMA function table selection, and ordered IP block registration.
- `amdgpu_discovery_fini(struct amdgpu_device *adev)` tears down discovery sysfs and frees `adev->discovery.bin`.
- `amdgpu_discovery_dump(struct amdgpu_device *adev, struct drm_printer *p)` serializes the sysfs discovery object tree into a DRM printer for devcoredump/debugging.
- `amdgpu_discovery_get_nps_info(...)` returns NPS memory partition type and ranges, optionally refreshing from VRAM instead of using the cached discovery binary.
- `amdgpu_discovery_init()` allocates and loads `adev->discovery.bin`, checks the binary signature, validates binary checksum, and validates key tables including IP discovery, GC, harvest, VCN, and MALL.
- `amdgpu_discovery_reg_base_init()` parses the IP discovery table, converts base-address endianness in place, fills `adev->reg_offset[hw_ip][instance]`, records IP versions, and counts/masks VCN, JPEG, SDMA, VPE, UMC, and GC/XCC instances.
- `amdgpu_discovery_harvest_ip()`, `amdgpu_discovery_read_harvest_bit_per_ip()`, and `amdgpu_discovery_read_from_harvest_table()` apply disabled-IP information to VCN/JPEG instance masks, UMC active mask, GC XCC mask, SDMA mask, DMU harvest mask, and optional ISP state.
- `amdgpu_discovery_get_gfx_info()`, `amdgpu_discovery_get_mall_info()`, and `amdgpu_discovery_get_vcn_info()` parse auxiliary tables into `adev->gfx.config`, `adev->gfx.cu_info`, `adev->gmc.mall_size`, and VCN codec disable masks.
- Sysfs helper structures `ip_discovery_top`, `ip_die_entry`, `ip_hw_id`, and `ip_hw_instance` model `/sys/.../ip_discovery/die/<die>/<hw_id>/<instance>/` with read-only attributes such as `hw_id`, `major`, `minor`, `revision`, `harvest`, `num_base_addresses`, and `base_addr`.
- `amdgpu_discovery_set_*_ip_blocks()` functions map discovered IP versions to concrete implementation descriptors such as `gmc_v11_0_ip_block`, `gfx_v12_0_ip_block`, `sdma_v7_0_ip_block`, `dm_ip_block`, `mes_v12_1_ip_block`, and media/ISP/VPE blocks.

## Control flow

The dynamic path starts in `amdgpu_discovery_set_ip_blocks()`. For modern/default ASICs it calls `amdgpu_discovery_reg_base_init()`, which calls `amdgpu_discovery_init()` before parsing. `amdgpu_discovery_init()` obtains TMR location and size from registers, SR-IOV critical region data, PSP scratch registers, or ACPI fallback, allocates the discovery buffer, chooses a firmware filename when required, otherwise reads from VRAM or system memory, verifies signature and checksums, and validates supported tables.

After binary load, `amdgpu_discovery_reg_base_init()` walks dies and IP entries. For every valid IP instance it records instance masks, normalizes 32-bit and 64-bit base addresses, updates the register-base array, and records full IP versions including variant/subrevision when the table version supports them. Harvest handling then removes disabled instances from the masks. Auxiliary info tables enrich GFX, MALL, VCN, and NPS state.

`amdgpu_discovery_set_ip_blocks()` then initializes SOC-specific config for special families, creates the sysfs discovery tree, classifies the ASIC family and APU flags from GC version, selects function tables for NBIO/HDP/DF/SMUIO/LSDMA, and adds IP blocks in dependency order: common, GMC, PSP/IH ordering adjusted for SR-IOV, SMU depending on firmware load path, display, GC, SDMA, RAS, optional late SMU, media, MES, VPE, UMSCH-MM, and ISP.

Legacy ASIC cases such as VEGA10, VEGA12, RAVEN, VEGA20, ARCTURUS, ALDEBARAN, and some CYAN_SKILLFISH paths bypass full dynamic parsing for functional setup, use hard-coded register base and IP version assignments, and treat discovery binary initialization as non-fatal sysfs/debug support.

## State and persistence behavior

Persistent driver state is stored in `adev->discovery`, `adev->ip_versions`, `adev->reg_offset`, `adev->gfx`, `adev->gmc`, `adev->umc`, `adev->vcn`, `adev->jpeg`, `adev->sdma`, `adev->vpe`, `adev->harvest_ip_mask`, `adev->family`, `adev->flags`, and per-subsystem function-table pointers. The discovery binary remains cached in `adev->discovery.bin` until `amdgpu_discovery_fini()`.

The sysfs state is dynamically allocated and rooted at `adev->discovery.ip_top`; it is reference-counted through kobjects/ksets and explicitly traversed/free-walked by `amdgpu_discovery_sysfs_fini()`. Debugfs blob state references the same discovery binary buffer through `adev->discovery.debugfs_blob`.

The file mutates discovery table base-address fields in place after endian conversion. That makes later sysfs base-address exposure and `adev->reg_offset` use host-order lower 32-bit base values rather than raw firmware encoding.

## Dependencies and integration points

This file depends on AMD discovery table layouts from `discovery.h`, AMDGPU core device state from `amdgpu.h`, IP version constants, register helpers such as `RREG32`, VRAM access via `amdgpu_device_vram_access()`, firmware loading via `firmware_request_nowarn()`, ACPI TMR fallback, SR-IOV helpers, RAS boot status query, and a large set of IP block descriptor headers.

It integrates with sysfs/kobject infrastructure, DRM logging and devcoredump printers, debugfs blob wrappers, GMC/UMC/GFX/VCN/JPEG/SDMA/MES/VPE/ISP state, display manager selection, firmware loading policy, and the AMDGPU IP block initialization sequence. Failures here often prevent the driver from selecting later hardware implementations.

## Risks and edge cases

- Discovery binary validation is critical. Bad offsets, checksums, unsupported binary header versions, or malformed table sizes can stop initialization or hide optional tables.
- Some legacy paths ignore discovery initialization failures because they are only needed for sysfs; modern/default paths return errors and can block device bring-up.
- SR-IOV changes TMR source, display path, and PSP/IH ordering. Regressions can affect VF boot even if bare metal still works.
- The parser relies on table-provided counts and flexible-size IP entries. Validation catches out-of-range `instance_number` and `hw_id`, but corruption around offsets/counts remains a high-risk area.
- Harvest data controls instance masks and can disable complete media/IP blocks. Board-specific quirks such as Navy Flounder VCN harvesting are easy to break when adding new ASIC IDs.
- IP version switch tables are large and must be kept synchronized with new block implementations. Missing one case usually returns `-EINVAL` with "Failed to add ..." logs.
- Sysfs object lifetime uses embedded kobjects and manual list traversal under kset list locks. Leaks or double puts would show up during device removal or failed sysfs initialization.

## Test signals

Useful validation signals include boot logs containing discovery source and checksum errors, successful AMDGPU probe on each covered ASIC family, `/sys/.../ip_discovery` hierarchy correctness, devcoredump `HW IP Discovery` output, `dmesg` errors from each `Failed to add ... ip block` branch, SR-IOV VF initialization, RAS boot status fallback on discovery v4 failures, and graphics/media/SDMA/MES smoke tests that indirectly prove IP versions, register bases, and masks were populated correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.h

## Purpose

`amdgpu_discovery.h` is the public header for the discovery subsystem. It defines the cached discovery state carried by `struct amdgpu_device`, constants for default TMR placement, and the small API used by AMDGPU core, memory code, and diagnostics to initialize, query, dump, and tear down hardware discovery data.

## Important APIs, types, and functions

- `DISCOVERY_TMR_SIZE` and `DISCOVERY_TMR_OFFSET` define the default 10 KiB table size and 64 KiB-from-end offset used when firmware/registers do not supply a more specific discovery TMR location.
- `struct amdgpu_discovery_info` stores the `debugfs_blob_wrapper`, sysfs topology root `ip_top`, binary offset, size, loaded binary pointer, and `reserve_tmr` flag.
- `amdgpu_discovery_set_ip_blocks()` is the main setup API.
- `amdgpu_discovery_fini()` releases sysfs and binary resources.
- `amdgpu_discovery_get_nps_info()` returns NPS partitioning and memory ranges.
- `amdgpu_discovery_dump()` emits discovery topology to a `drm_printer`.

## Control flow

Callers treat this header as the lifecycle contract: set IP blocks during device initialization, optionally query NPS information after discovery has populated the cached binary, dump topology during diagnostics, and call fini during device teardown.

## State and persistence behavior

`struct amdgpu_discovery_info` persists the loaded discovery binary and sysfs/debugfs representation across the device lifetime. `reserve_tmr` records whether the table memory reservation is required, which matters when the discovery table was sourced from VRAM/TMR rather than a standalone firmware file.

## Dependencies and integration points

The header includes `<linux/debugfs.h>` for `debugfs_blob_wrapper` and forward-declares `ip_discovery_top` and `drm_printer` to avoid broad include dependencies. It is consumed by `amdgpu_discovery.c` and any AMDGPU component that needs discovery lifecycle or NPS queries.

## Risks and edge cases

The header exposes only opaque discovery topology state, so ABI risk is internal to the driver. The main risk is that fields in `amdgpu_discovery_info` must stay consistent with teardown logic in `amdgpu_discovery.c`; stale `bin` or `ip_top` pointers would cause removal/debug paths to fail.

## Test signals

Compile coverage is the primary header-level test. Runtime signals come from successful discovery initialization and teardown, a valid debugfs blob size/data pair, valid NPS query behavior, and absence of sysfs lifetime errors during module unload or GPU hot-unplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_display.c

## Purpose

`amdgpu_display.c` implements shared AMDGPU display helpers used by legacy and DC display paths. It handles hotplug work, page flip scheduling, framebuffer creation and validation, format modifier conversion, display properties, scanout position queries, suspend/resume display buffer pinning, and DRM panic scanout-buffer access.

The file sits between DRM/KMS core interfaces and AMDGPU buffer/display internals. Its most sensitive responsibilities are fencing and pinning BOs during page flips, translating AMD tiling metadata into DRM format modifiers, proving framebuffer plane sizes fit in the backing BO, and making scanout state safe across runtime PM and panic paths.

## Important APIs, types, and functions

- `amdgpu_display_hotplug_work_func()` runs outside IRQ context, locks mode config, calls each connector hotplug handler, and emits a DRM HPD event.
- `amdgpu_display_crtc_page_flip_target()` implements the CRTC page-flip path: allocate flip work, pin the new BO, collect write fences, update CRTC state under `event_lock`, and schedule MMIO flip work.
- `amdgpu_display_flip_work_func()` waits on shared fences and avoids issuing a flip too early in vblank before calling the ASIC `page_flip` hook and marking `AMDGPU_FLIP_SUBMITTED`.
- `amdgpu_display_unpin_work_func()` asynchronously unpins and unreferences the old framebuffer BO after the flip lifecycle completes.
- `amdgpu_display_crtc_set_config()` wraps legacy mode setting with runtime PM reference handling and tracks `adev->have_disp_power_ref`.
- `amdgpu_display_user_framebuffer_create()` is `mode_config.fb_create`; it looks up the GEM handle, rejects imported DMA-BUF scanout when the buffer cannot live in a supported domain, allocates `struct amdgpu_framebuffer`, verifies, initializes, and publishes a DRM framebuffer.
- `amdgpu_display_framebuffer_init()` reads BO tiling/TMZ/GFX12-DCC state, verifies legacy tiling or converts tiling flags to modifiers, validates sizes, and aliases all planes to the same BO with proper object references.
- `convert_tiling_flags_to_modifier()` and `convert_tiling_flags_to_modifier_gfx12()` translate AMDGPU tiling flags into DRM AMD modifiers, including DCC and DCC-retile metadata.
- `amdgpu_lookup_format_info()` selects synthetic DRM format descriptions for DCC and DCC-retile buffers.
- `amdgpu_display_verify_sizes()` and `amdgpu_display_verify_plane()` check pitch, offset alignment, and minimum backing BO size for all image, DCC, and retile planes.
- `amdgpu_display_modeset_create_props()` creates common display connector properties, including coherent mode, load detection, scaling mode, underscan, audio, dither, and adaptive backlight modulation.
- `amdgpu_display_get_crtc_scanoutpos()` decodes vblank and current scanout position using display function hooks and applies vblank lead-line correction.
- `amdgpu_display_suspend_helper()` and `amdgpu_display_resume_helper()` disable polling/DPMS, unpin or repin cursor and scanout BOs, and restore modes.
- `amdgpu_display_get_scanout_buffer()` exposes a framebuffer to DRM panic handling, either by mapping the BO or by using indirect MMIO writes for no-CPU-access VRAM BOs.

## Control flow

Hotplug starts from an IRQ-scheduled work item. The worker serializes connector scanning with `mode_config->mutex`, invokes connector-specific handling, then notifies userspace with `drm_helper_hpd_irq_event()`.

Page flip flow starts with `amdgpu_display_crtc_page_flip_target()`. It references the old BO, reserves and pins the new BO in display-supported domains, ensures GART allocation, collects write fences from the new BO reservation object, computes the target vblank, and installs `work` in the CRTC under `event_lock` only if no flip is already pending. `amdgpu_display_flip_work_func()` then waits for each shared fence by registering callbacks; once fences are done and scanout is outside the unsafe pre-target vblank window, it calls the ASIC-specific `page_flip()` hook. Cleanup of the old BO happens in separate unpin work.

Framebuffer creation starts with a GEM handle lookup. Imported DMA-BUFs are rejected when they cannot be scanned out from GTT and cannot be migrated to VRAM. The helper fills DRM framebuffer fields, checks format/modifier support against planes, reads BO metadata, converts missing modifiers from tiling flags, validates image and metadata planes, initializes DRM framebuffer functions, and finally drops the lookup reference while the framebuffer owns its plane references.

Modifier conversion is split by generation. GFX12 uses `GFX12_SWIZZLE_MODE` and GFX12 DCC fields. GFX9-GFX11 derive tile version, block size, XOR bits, packers/RB/pipe metadata, DCC mode, DCC plane offsets, DCC pitch, and optional render DCC retile plane from BO metadata. Size verification recomputes natural block dimensions and ensures every plane offset and pitch satisfies hardware block alignment and does not exceed BO size.

Suspend flow disables KMS polling, DPMSes connectors off under modeset locks, and unpins cursor/front buffers not owned by fbdev helper. Resume repins cursors, restores mode, DPMSes connectors on, and reenables polling.

## State and persistence behavior

The file mutates CRTC page flip state (`pflip_status`, `pflip_works`, `primary->fb`), BO pin counts, BO flags such as `AMDGPU_GEM_CREATE_VRAM_CONTIGUOUS`, framebuffer modifier/format/plane arrays, `adev->have_disp_power_ref`, `adev->mode_info` property pointers, display priority, CRTC scaling state, cursor GPU addresses, and the static `panic_abo` pointer used only under DRM panic locking.

Asynchronous flip state persists between the initial ioctl/helper call, fence callback scheduling, delayed work retries around vblank, flip interrupt completion elsewhere in the driver, and unpin cleanup work. Framebuffer state persists in DRM objects until destroyed by `drm_gem_fb_destroy()`.

## Dependencies and integration points

This file depends on DRM KMS, GEM framebuffer helpers, damage helpers, vblank helpers, EDID/DDC helpers, runtime PM, AMDGPU BO/GEM/TTM helpers, connector/encoder structures, ASIC display function hooks in `adev->mode_info.funcs`, and AMD format modifier macros. It integrates with PRIME/DMA-BUF policy by rejecting imported buffers that cannot be displayed safely, and with `drm_panic` through `get_scanout_buffer`.

## Risks and edge cases

- Page-flip error paths must drop BO references, fences, pins, reservations, and allocated work exactly once. Mistakes produce leaks, stuck pinned BOs, or use-after-free in fence callbacks.
- Flip scheduling intentionally delays around vblank to avoid submitting too early. Incorrect scanout position or target vblank math can cause missed flips, tearing, or long delays.
- Framebuffer modifier conversion is generation-sensitive. New tiling modes, DCC variants, or incorrect `gb_addr_config_fields` can yield invalid modifiers or reject valid scanout buffers.
- The code requires all planes of multi-plane framebuffers to use the same BO before modifier conversion. This is an AMD-specific assumption that can reject otherwise legal DRM layouts.
- DCC retile offset extraction depends on opaque BO metadata layout and ASIC family. Bad metadata returns `-EINVAL` or omits the retile plane.
- Imported DMA-BUF scanout depends on `amdgpu_display_supported_domains()` and can be rejected on systems without GTT display support.
- Panic rendering supports no-CPU-access BOs only when they are VRAM-backed and 32 bpp; other cases fail to display panic output.
- Runtime PM reference tracking in legacy set_config relies on active CRTC enumeration after helper set_config; mismatches can affect power management.

## Test signals

Useful signals include KMS page-flip/vblank tests, IGT framebuffer modifier and size validation tests, hotplug and EDID/DDC tests, suspend/resume display tests, imported DMA-BUF scanout tests, debug logs for unsupported pixel format/modifier and pitch/offset failures, panic screen smoke tests on CPU-accessible and no-CPU-access BOs, and absence of pinned-BO leaks after repeated page flips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_display.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_display.h

## Purpose

`amdgpu_display.h` declares the shared AMDGPU display helper API and defines convenience wrappers around `adev->mode_info.funcs`. It is the contract between display IP implementations, AMDGPU core display setup, and common KMS helper code in `amdgpu_display.c`.

## Important APIs, types, and functions

- Function-hook macros dispatch to ASIC/display-manager-specific callbacks for vblank counters, backlight level, HPD sense/polarity/GPIO, bandwidth update, page flip, scanout position, encoder creation, and connector creation.
- `amdgpu_display_hotplug_work_func()` is the deferred HPD worker entry point.
- `amdgpu_display_update_priority()` applies the module display-priority setting into `adev->mode_info`.
- `amdgpu_display_supported_domains()` returns VRAM and optionally GTT scanout domains for a BO.
- `amdgpu_display_user_framebuffer_create()` and `amdgpu_lookup_format_info()` support DRM framebuffer creation and modifier-aware format lookup.
- `amdgpu_display_suspend_helper()` and `amdgpu_display_resume_helper()` provide shared suspend/resume display handling.
- `amdgpu_display_get_scanout_buffer()` supports DRM panic rendering.
- `ABM_*` constants define adaptive backlight modulation values including sysfs-controlled, off, min, bias, and max levels.

## Control flow

Display IP-specific code installs `adev->mode_info.funcs`; callers use the macros to invoke the active implementation without hard-coding DC or legacy display paths. The declared functions are called from DRM mode-config hooks, PM paths, HPD work scheduling, panic handling, and display initialization.

## State and persistence behavior

The header itself owns no storage beyond constants, but it exposes operations that mutate `adev->mode_info`, CRTC state, framebuffer state, connector properties, BO pinning, and panic scanout buffers. The macros assume `adev->mode_info.funcs` is valid before use.

## Dependencies and integration points

The header includes `<drm/drm_panic.h>` for `struct drm_scanout_buffer` and relies on forward-visible AMDGPU/DRM types supplied by including translation units. It integrates with the mode-info function table populated by ASIC display backends and with common DRM framebuffer and suspend/resume paths.

## Risks and edge cases

The macro wrappers perform no NULL checks. A missing or partially initialized `mode_info.funcs` table will fail at call sites. Because the macros evaluate arguments in function-call form, they should be used with side-effect-safe arguments. ABM constants must stay aligned with property creation and DC/sysfs expectations.

## Test signals

Compile coverage for all display backends is the key header-level signal. Runtime signals include successful page flips, HPD, backlight, scanout position queries, framebuffer creation, suspend/resume, and panic scanout on both DC and non-DC configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dma_buf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dma_buf.c

## Purpose

`amdgpu_dma_buf.c` implements AMDGPU PRIME/DMA-BUF export and import support. It lets AMDGPU GEM buffer objects be shared with other devices, controls placement and pinning for peer-to-peer and CPU access, maps backing memory into scatter/gather tables, handles dynamic attachment invalidation, and detects XGMI-accessible peer GPU memory.

The file is a bridge between DRM GEM/PRIME, Linux DMA-BUF, TTM memory placement, AMDGPU VM invalidation, PCI P2PDMA policy, and XGMI multi-GPU sharing.

## Important APIs, types, and functions

- `amdgpu_dmabuf_ops` is the exported `dma_buf_ops` table: attach, pin, unpin, map/unmap, release, begin CPU access, mmap, vmap, and vunmap.
- `amdgpu_gem_prime_export()` prepares a GEM BO for export with TTM, rejects userptr and always-valid VM BOs, delegates to `drm_gem_prime_export()`, and installs AMDGPU DMA-BUF ops.
- `amdgpu_gem_prime_import()` returns a same-device exported GEM object directly or creates an imported SG BO and dynamically attaches to the source DMA-BUF.
- `amdgpu_dma_buf_attach()` updates peer-to-peer eligibility, disables P2P for GFX12+ DCC VRAM surfaces and unreachable PCI P2P paths, then updates shared VM BO state under the BO reservation lock.
- `amdgpu_dma_buf_pin()` chooses a pin domain from allowed domains and attachment peer2peer capabilities, preferring VRAM only when all attachments support P2P and move notifiers are available.
- `amdgpu_dma_buf_map()` validates/moves unpinned BOs into GTT or VRAM as appropriate, then builds an `sg_table` for TT pages, VRAM resources, or MMIO-remap resources.
- `amdgpu_dma_buf_unmap()` frees the corresponding SG table through the TT, VRAM, or MMIO-remap path.
- `amdgpu_dma_buf_begin_cpu_access()` moves readable buffers to GTT when supported, improving CPU access performance and avoiding direct VRAM reads.
- `amdgpu_dma_buf_vmap()` and `amdgpu_dma_buf_vunmap()` pin around generic GEM DMA-BUF vmap/vunmap.
- `amdgpu_dma_buf_move_notify()` invalidates mappings for imported buffers and clears/updates VM page tables for VMs referencing the imported BO.
- `amdgpu_dmabuf_is_xgmi_accessible()` detects whether a BO can be accessed by the importing AMDGPU device over XGMI.

## Control flow

Export starts when DRM PRIME calls `amdgpu_gem_prime_export()`. The function rejects BOs that should not be exported, asks TTM to set up export constraints without allowing resource eviction, then returns a DMA-BUF using AMDGPU-specific operations.

Attachment starts through `amdgpu_dma_buf_attach()`. The importer may be another AMDGPU attachment using `amdgpu_dma_buf_attach_ops`; if so, the helper recovers its `amdgpu_device`. The attach callback adjusts `attach->peer2peer` based on compression, XGMI accessibility, and PCI P2P distance, then updates shared VM state.

Map flow first moves an unpinned BO into a device-accessible placement: GTT by default, plus VRAM when the buffer prefers VRAM and the attachment supports P2P. It then returns DMA addresses. TT memory maps normal pages through DMA API, VRAM uses AMDGPU VRAM manager SG allocation, and MMIO-remap uses its dedicated allocator. Unmap chooses the matching free path by resource type and SG page presence.

Import flow returns the original GEM object for same-device AMDGPU DMA-BUFs. For other devices it creates a `ttm_bo_type_sg` BO backed by the DMA-BUF reservation object, restricts placement to GTT, dynamically attaches with AMDGPU attach ops, increments the DMA-BUF refcount, and stores the attachment in `obj->import_attach`.

Move notification invalidates the imported BO in AMDGPU VM lists, evicts it to a null/empty placement if it has a resource, and walks VM BO bases to clear freed mappings and handle moved mappings while carefully dealing with reservation locking conflicts.

## State and persistence behavior

The code mutates BO placement, pin count, flags such as `AMDGPU_GEM_CREATE_CPU_ACCESS_REQUIRED`, `allowed_domains`, `preferred_domains`, import attachments, DMA-BUF `peer2peer` flags, VM BO invalidation state, and page tables for VMs referencing imported BOs. Imported BOs share the exporter DMA-BUF reservation object, so synchronization state persists across drivers.

Mapped SG tables are transient per attachment mapping and must be released via `unmap_dma_buf`. VM invalidation state persists until the next VM update clears or rebuilds page tables. XGMI accessibility marks are consumed by VM mapping code outside this file.

## Dependencies and integration points

The file depends on Linux DMA-BUF, DRM PRIME/GEM helpers, DMA fence reservation objects, TTM, AMDGPU BO/GEM/TTM/VM/XGMI/display helpers, PCI P2PDMA, and DMA mapping APIs. It integrates with `amdgpu_ttm.c` imported SG handling, `amdgpu_vm.c` XGMI and moved-BO handling, display scanout domain policy, and external devices such as RDMA NICs or other GPUs.

## Risks and edge cases

- Peer-to-peer policy is hardware-sensitive. Allowing P2P for GFX12 DCC-compressed VRAM or unreachable PCI topology can corrupt data or fail DMA.
- Pinning chooses VRAM only if every attachment remains peer2peer-capable; a single incompatible attachment forces GTT and affects performance.
- Map/unmap must pair allocation paths exactly. Misidentifying TT vs VRAM vs MMIO-remap SG tables can leak or unmap through the wrong API.
- Move notification has complex locking around VM reservations. If locks cannot be taken it may skip a VM update, relying on later synchronization; errors other than `-EBUSY` are logged.
- Same-device import intentionally returns the existing GEM object rather than wrapping the DMA-BUF file, changing refcount behavior compared with cross-device import.
- Export rejects userptr and `VM_ALWAYS_VALID` BOs; callers must handle `-EPERM`.
- CPU read access migration to GTT is skipped for write-only access or when GTT scanout/access domains are unsupported.

## Test signals

Relevant validation includes DRM PRIME import/export tests, cross-GPU and same-GPU DMA-BUF sharing, RDMA P2P scenarios, GFX12 DCC sharing fallback, XGMI hive P2P mapping tests, repeated map/unmap leak checks, CPU-access readback tests, VM invalidation after exporter movement, and display tests using imported DMA-BUFs under both GTT-supported and VRAM-only scanout policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dma_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dma_buf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dma_buf.h

## Purpose

`amdgpu_dma_buf.h` declares AMDGPU's PRIME/DMA-BUF public interface. It exposes export/import hooks for the DRM driver, the XGMI accessibility helper used by VM and DMA-BUF paths, and the AMDGPU-specific `dma_buf_ops` table.

## Important APIs, types, and functions

- `amdgpu_gem_prime_export(struct drm_gem_object *gobj, int flags)` exports an AMDGPU GEM object as a DMA-BUF.
- `amdgpu_gem_prime_import(struct drm_device *dev, struct dma_buf *dma_buf)` imports a DMA-BUF as a GEM object on an AMDGPU device.
- `amdgpu_dmabuf_is_xgmi_accessible(struct amdgpu_device *adev, struct amdgpu_bo *bo)` returns whether the importer can access the BO over XGMI.
- `extern const struct dma_buf_ops amdgpu_dmabuf_ops` lets other code compare or install the AMDGPU DMA-BUF operation table.

## Control flow

DRM driver setup wires the export/import declarations into PRIME hooks. VM and DMA-BUF attachment code use the XGMI helper to decide whether shared VRAM can be accessed directly or must fall back to ordinary DMA mapping/system memory paths.

## State and persistence behavior

The header owns no state. The declared functions mutate GEM/BO references, DMA-BUF attachments, reservation objects, memory placement, and VM invalidation state in their implementation.

## Dependencies and integration points

The header includes `<drm/drm_gem.h>` and relies on AMDGPU device/BO type visibility from including files. It integrates with DRM PRIME, Linux DMA-BUF, AMDGPU VM, XGMI, and TTM memory management.

## Risks and edge cases

Callers comparing `dma_buf->ops` with `amdgpu_dmabuf_ops` depend on this symbol remaining the canonical AMDGPU DMA-BUF identity. The XGMI helper must be used before assuming peer GPU VRAM is safely accessible.

## Test signals

Compile coverage across DRM driver registration, VM, and DMA-BUF code is the header-level signal. Runtime signals include successful PRIME export/import, same-device import refcount behavior, and correct XGMI vs non-XGMI mapping decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dma_buf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_doorbell.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_doorbell.h

## Purpose

`amdgpu_doorbell.h` defines AMDGPU doorbell state, doorbell index assignments, and the public helpers for reading, writing, initializing, allocating, and translating doorbell offsets. Doorbells are CPU-visible MMIO or doorbell-domain BO locations used to notify GPU engines that queue write pointers or other ring state changed.

## Important APIs, types, and functions

- `struct amdgpu_doorbell` stores doorbell BAR base/size, the number of kernel-reserved doorbells, the kernel doorbell BO, and the CPU address used by the driver.
- `struct amdgpu_doorbell_index` is the normalized per-device assignment table used by graphics, compute, SDMA, MES, IH, VCN/UVD/VCE/JPEG, VPE, and user queue code.
- Assignment enums encode generation/layout-specific ranges:
  - `AMDGPU_DOORBELL_ASSIGNMENT` for older 32-bit doorbell layouts.
  - `AMDGPU_VEGA20_DOORBELL_ASSIGNMENT` for Vega20-like 64-bit layouts with SDMA/IH/media ranges and XCC/AID extensions.
  - `AMDGPU_NAVI10_DOORBELL_ASSIGNMENT` for Navi layouts including MES and graphics user queues.
  - `AMDGPU_DOORBELL64_ASSIGNMENT` for a compact 64-bit assignment map.
  - `AMDGPU_DOORBELL_ASSIGNMENT_LAYOUT1` and `AMDGPU_SOC_V1_0_DOORBELL_ASSIGNMENT` for newer multi-XCC/SOC layouts.
- `amdgpu_mm_rdoorbell()`, `amdgpu_mm_wdoorbell()`, `amdgpu_mm_rdoorbell64()`, and `amdgpu_mm_wdoorbell64()` perform 32-bit and 64-bit doorbell aperture access.
- `amdgpu_doorbell_init()`, `amdgpu_doorbell_fini()`, and `amdgpu_doorbell_create_kernel_doorbells()` manage driver doorbell resources.
- `amdgpu_doorbell_index_on_bar()` translates an index inside a doorbell BO into an absolute BAR dword index.
- `RDOORBELL32`, `WDOORBELL32`, `RDOORBELL64`, and `WDOORBELL64` are convenience macros used by ring/IP code with an in-scope `adev`.

## Control flow

ASIC setup calls an ASIC-specific doorbell index initializer that fills `adev->doorbell_index` using one of the assignment layouts. `amdgpu_doorbell_init()` establishes aperture bounds from PCI BAR2 and computes the maximum kernel doorbell range. Later `amdgpu_doorbell_create_kernel_doorbells()` allocates a doorbell-domain BO for kernel doorbells and maps it to `cpu_addr`. Ring and IP code then reads or writes doorbells through the access helpers/macros when updating queue pointers.

## State and persistence behavior

Doorbell layout state persists in `adev->doorbell_index`. Aperture and allocation state persists in `adev->doorbell`. The kernel doorbell BO pins/backs the CPU-visible doorbell area until `amdgpu_doorbell_fini()` frees it. Doorbell writes are hardware notifications rather than ordinary persisted memory semantics.

## Dependencies and integration points

The header is consumed by graphics, SDMA, MES, VCN/JPEG, IH, user queue, VPE, NBIO, and ring code. It relies on `struct amdgpu_device`, `struct amdgpu_bo`, and generation-specific initialization code elsewhere to populate assignments correctly.

## Risks and edge cases

- Assignment constants are hardware contracts. Off-by-one ranges or using a 32-bit index where a 64-bit/QWORD index is expected can notify the wrong engine.
- Several media assignments intentionally overlap because engines are mutually exclusive on a given ASIC; consumers must select the right semantic layout.
- New multi-XCC layouts require correct per-XCC ranges for KIQ/KCQ and user queues.
- The 64-bit access helpers operate on `cpu_addr + index` cast to `atomic64_t *`; callers must pass an index aligned to the layout's 64-bit convention.
- The convenience macros require a local variable named `adev`, so they are unsuitable for contexts without that convention.

## Test signals

Signals include successful ring tests for graphics/compute/SDMA/MES/media, no "beyond doorbell aperture" logs, correct queue write-pointer advancement, SR-IOV and multi-XCC queue bring-up, user queue doorbell allocation tests, and suspend/resume/reset tests that prove doorbell BOs are recreated and mapped correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_doorbell.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_doorbell_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_doorbell_mgr.c

## Purpose

`amdgpu_doorbell_mgr.c` implements the doorbell helper functions declared in `amdgpu_doorbell.h`. It bounds-checks 32-bit and 64-bit doorbell aperture accesses, translates doorbell BO-relative indices to BAR indices, initializes aperture metadata from PCI BAR2, allocates kernel doorbell storage, and frees it during teardown.

## Important APIs, types, and functions

- `amdgpu_mm_rdoorbell()` and `amdgpu_mm_wdoorbell()` read/write 32-bit doorbell dwords through `readl()` and `writel()`.
- `amdgpu_mm_rdoorbell64()` and `amdgpu_mm_wdoorbell64()` read/write 64-bit doorbells through `atomic64_read()` and `atomic64_set()`.
- `amdgpu_doorbell_index_on_bar()` computes `amdgpu_bo_gpu_offset(db_bo) / sizeof(u32) + doorbell_index * DIV_ROUND_UP(db_size, 4)`.
- `amdgpu_doorbell_create_kernel_doorbells()` allocates an `AMDGPU_GEM_DOMAIN_DOORBELL` kernel BO, maps CPU access into `adev->doorbell.cpu_addr`, reserves an extra page for MES ring-test use, and updates `num_kernel_doorbells` to the allocated dword count.
- `amdgpu_doorbell_init()` skips SI-era hardware, validates BAR2, calls `amdgpu_asic_init_doorbell_index()`, records BAR base/size, computes the kernel-reserved range from the maximum assignment, and adds a second page for Vega10+ paging queue assumptions.
- `amdgpu_doorbell_fini()` frees the kernel doorbell BO and CPU mapping.

## Control flow

Initialization first determines whether the ASIC supports doorbells. For supported ASICs it verifies PCI BAR2, initializes generation-specific assignments, records BAR base and length, and calculates how many dwords can be used by kernel assignments. If the range is nonzero, later kernel doorbell creation allocates a page-aligned doorbell-domain BO large enough for reserved assignments plus an extra MES page. Runtime ring code uses the read/write helpers to notify engines. Teardown frees the BO and CPU mapping.

## State and persistence behavior

The manager stores aperture state in `adev->doorbell.base`, `size`, `num_kernel_doorbells`, `kernel_doorbells`, and `cpu_addr`. `adev->mes.db_start_dw_offset` is set to the first dword of the extra MES page during kernel doorbell creation. Doorbell writes affect hardware engine notification state immediately and are not protected by software locks in this helper.

## Dependencies and integration points

This file depends on PCI resource BAR2, `amdgpu_asic_init_doorbell_index()`, AMDGPU BO kernel allocation/free helpers, `amdgpu_device_skip_hw_access()` for reset/suspend/no-HW-access paths, and consumers throughout ring/IP code that use doorbell writes for queue notification.

## Risks and edge cases

- Access helpers only check `index < num_kernel_doorbells`; wrong generation-specific index scaling can still target the wrong doorbell while staying in range.
- `amdgpu_device_skip_hw_access()` suppresses MMIO access during unsafe windows; callers must tolerate reads returning zero and writes being dropped.
- SI-era devices set all doorbell state to zero and return success, so consumers must not assume doorbells exist just because initialization succeeded.
- BAR2 unavailable or a zero computed assignment range returns `-EINVAL` and prevents doorbell use.
- The extra Vega10+ page changes `num_kernel_doorbells` after initial range computation, so bounds checks cover MES/paging queue use as well as static assignments.

## Test signals

Useful signals include successful `amdgpu_doorbell_init()` and kernel BO allocation, no "reading/writing beyond doorbell aperture" errors, passing ring tests that rely on WDOORBELL32/WDOORBELL64, MES ring test success using `db_start_dw_offset`, correct behavior when hardware access is skipped, and clean teardown without BO or mapping leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_doorbell_mgr.c -->
