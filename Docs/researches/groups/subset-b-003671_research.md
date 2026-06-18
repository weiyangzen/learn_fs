# subset-b-003671 Nouveau DRM Research

Grouped research for Nouveau BIOS, buffer object, channel, connector, display, DMA, and debugfs files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bios.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bios.c

Purpose: Implements Nouveau's legacy VBIOS interpretation layer used by pre-GSP PCI devices, especially pre-Tesla display initialization. It translates BIT and BMP ROM structures into `drm->vbios`, builds DCB encoder/connector information, runs LVDS/TMDS init scripts, locates embedded EDID, and decides whether VBIOS init scripts must execute when the adapter is not POSTed.

Important APIs/functions: `nouveau_bios_init()`, `nouveau_run_vbios_init()`, `nouveau_bios_fp_mode()`, `nouveau_bios_parse_lvds_table()`, `run_tmds_table()`, `call_lvds_script()`, `bit_table()`, `olddcb_table()`, `olddcb_outp_foreach()`, `olddcb_conn()`, and `nouveau_bios_embedded_edid()`. Internal parsing is split across `parse_bit_*_tbl_entry()`, `parse_bmp_structure()`, `parse_dcb20_entry()`, `parse_dcb15_entry()`, `merge_like_dcb_entries()`, and board-specific `apply_dcb_encoder_quirks()`.

Control flow: `nouveau_bios_init()` skips non-PCI and GSP-RM devices, initializes the legacy `struct nvbios` from the nvkm BIOS object, parses BIT or BMP, parses/fabricates DCB outputs for pre-Tesla, decides whether the hardware is POSTed, loads NV17 panel sequencer microcode when needed, parses flat-panel tables, then enables later script execution. LVDS and TMDS entry points select clock comparison tables, protect RAMDAC clock-head binding, run init tables through `nouveau_bios_run_init_table()`, and repair side effects such as `NV_PBUS_POWERCTRL_2`.

State/persistence: The file persists parsed VBIOS data in `drm->vbios`, including ROM pointer/length, feature bits, DCB entries, flat-panel mode pointers, LVDS flags, script invocation cache, EDID pointer, and init execution flag. It writes hardware registers while running scripts, loading HWSQ microcode, and checking POST state.

Dependencies/integration: Depends on nvkm BIOS, nvif MMIO access, VGA/RAMDAC helpers, DCB definitions, DRM display modes, PowerPC Open Firmware quirks, and Nouveau encoder/display code. Downstream users include connector creation, encoder setup, mode validation, LVDS panel power sequencing, debugfs VBIOS export, and pre-NV50 modeset.

Risks: ROM parsing is version-sensitive and includes many heuristics and board-specific overrides. Bad offsets can lead to disabled outputs, wrong connector mappings, incorrect panel bpc/dual-link decisions, or unsafe script execution. DCB fabrication and fake connector indices are fallback heuristics. Test signals include boot logs for BIT/BMP/DCB versions, connector enumeration, LVDS/eDP panel bring-up, TMDS clock behavior, suspend/resume panel scripts, embedded EDID detection, and known quirk boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bios.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bios.h

Purpose: Declares the legacy VBIOS data model and public parser/script APIs consumed by Nouveau display, connector, and encoder code. It defines DCB capacity constants, ROM endian access helpers, BIT entry representation, the parsed `struct nvbios`, and old DCB table accessors.

Important APIs/types: `struct bit_entry`, `struct dcb_table`, `enum nouveau_or`, `enum LVDS_script`, and `struct nvbios`. Public functions include `bit_table()`, `olddcb_table()`, `olddcb_outp()`, `olddcb_outp_foreach()`, `olddcb_conntab()`, `olddcb_conn()`, `nouveau_bios_init()`, `nouveau_bios_takedown()`, `nouveau_run_vbios_init()`, `nouveau_bios_fp_mode()`, `nouveau_bios_embedded_edid()`, `nouveau_bios_parse_lvds_table()`, `run_tmds_table()`, and `call_lvds_script()`.

Control flow/state contract: The header makes `drm->vbios` the persistent carrier for parsed ROM state: ROM bytes, BIOS type/version, mobile flags, PLL defaults, init script pointers, RAM restrict tables, DCB outputs, LVDS/TMDS tables, panel mode pointers, cached EDID, and resume-sensitive LVDS script state. Callers initialize it through `nouveau_bios_init()` before using connector and encoder helpers.

Dependencies/integration: Includes nvkm BIOS and DCB/connector definitions plus DRM display mode declarations via users. `ROM16`, `ROM32`, and `ROMPTR` are central to all legacy ROM parsing. Connector code uses flat-panel/EDID helpers; encoder code uses script runners; debugfs exposes `data` and `length`; display code indirectly depends on DCB entries produced here.

Risks: The structure contains raw ROM offsets and cached pointers, so it assumes the underlying nvkm BIOS data remains stable for the DRM device lifetime. Capacity constants cap parsed DCB arrays at 16 outputs/connectors; unexpected ROMs beyond those limits require careful bounds handling in implementations. Test signals are build coverage, boot-time parser logs, connector enumeration, and suspend/resume script state reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo.c

Purpose: Implements Nouveau's TTM-backed buffer object manager. It covers BO allocation, placement, pinning, CPU mapping, cache synchronization, legacy tile-region programming, GPU/CPU migration, BAR/iomem reservation, fault-time relocation, DMA-reservation fence integration, and the `ttm_device_funcs` callback table.

Important APIs/functions: `nouveau_bo_alloc()`, `nouveau_bo_init()`, `nouveau_bo_new()`, `nouveau_bo_new_pin()`, `nouveau_bo_new_map()`, `nouveau_bo_new_map_gpu()`, `nouveau_bo_pin_locked()`, `nouveau_bo_unpin_locked()`, `nouveau_bo_validate()`, `nouveau_bo_map()/unmap()`, `nouveau_bo_sync_for_device()/cpu()`, `nouveau_ttm_fault_reserve_notify()`, `nouveau_bo_fence()`, and `nouveau_bo_move_init()`. Internal movers include `nouveau_bo_move()`, `nouveau_bo_move_m2mf()`, `nouveau_bo_move_ntfy()`, `nouveau_bo_move_prep()`, and TTM TT/bus helpers.

Control flow: Allocation chooses kind/compression/page size from MMU/VMM capabilities, fixes alignment/size, initializes placement, and creates a TTM BO. Validation calls TTM placement and syncs non-coherent DMA pages for the device. Pinning reserves the BO, validates into the requested domain, updates available VRAM/GART counters, and handles contiguous VRAM forcing on Tesla+. Moves bind TT resources, notify GPUVA/VMA mappings, wait for outstanding work, optionally install legacy tile regions, perform null moves for system/TT transitions, use a selected hardware copy engine when possible, fall back to memcpy, then cleans up tile and mapping state.

State/persistence: State lives in `struct nouveau_bo`: TTM BO, placement array, mapping object, VMA list, GPU offset, kind/comp/page/tile fields, pin count via TTM, IO-reserve LRU node, and legacy tile pointer. Driver-wide state includes `drm->ttm.move`, `drm->ttm.chan`, copy object, IO reserve LRU, and availability counters.

Dependencies/integration: Integrates DRM GEM, TTM, dma-resv, AGP, PRIME import, Nouveau GEM/VMM/UVMM/memory/fence/channel subsystems, nvif memory mapping, and generation-specific move files. Display framebuffers, channels, command buffers, GEM ioctls, and fault handlers all rely on this layer.

Risks: Migration is concurrency-heavy and must preserve reservation locking, GPUVA mappings, tile region lifetime, DMA cache coherency, and fence ordering. Hardware copy fallback can be slow; BAR aperture exhaustion triggers LRU unmapping. Test signals include TTM/GEM tests, PRIME import/export, mmap faults for tiled and high VRAM BOs, suspend/resume, GPUVA map/unmap tracing, pin accounting, and copy-engine selection logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo.h

Purpose: Declares Nouveau's BO wrapper around `struct ttm_buffer_object` and the BO management/migration API used by GEM, display, channels, VMM, and TTM callbacks.

Important APIs/types: `struct nouveau_bo` stores placement, valid domains, kernel map, reserve metadata, root GEM sharing state, GPU offset, VMA list, contiguity/page/kind/compression/tile metadata, and legacy tile region. Public APIs cover allocation/init/new helpers, pin/unpin, map/unmap, placement changes, register-style read/write helpers, TTM fault notification, fence attachment, validation, CPU/device DMA sync, IO-reserve LRU management, and convenience create-pin-map helpers. It also declares generation-specific move init/copy entry points: `nv04`, `nv50`, `nv84`, `nva3`, `nvc0`, and `nve0`.

Control flow/state contract: Callers allocate and initialize BOs through `nouveau_bo_new()` or convenience helpers, reserve before locked pin/unpin paths, use `nouveau_bo_validate()` after changing placement, and finish through `nouveau_bo_fini()` or `nouveau_bo_unpin_del()`. `nvbo_kmap_obj_iovirtual()` asserts that a mapped BO is iomem when raw MMIO-style access is needed.

Dependencies/integration: Includes DRM GEM and TTM placement/BO headers and forward-declares Nouveau channel, client, DRM, fence, and VMA types. The DRF macros at the end adapt Nouveau register field helpers to BO-backed memory accesses.

Risks: API misuse can break TTM reservation rules, leak pins, or access unmapped `kmap` memory. The compact bitfields for page/kind/comp/zeta must stay aligned with hardware/MMU limits. Test signals include compile coverage from all users, BO lifetime under error injection, mmap/page-fault tests, migration tests across all declared copy engines, and lockdep for reserve-held operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo0039.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo0039.c

Purpose: Provides NV04-era M2MF buffer copy support for Nouveau BO migration through the `NV039` class.

Important APIs/functions: `nv04_bo_move_m2mf()` emits pushbuf methods for page-sized copies between old and new TTM resources. `nv04_bo_move_init()` binds the M2MF object and notification context. The helper `nouveau_bo_mem_ctxdma()` selects `NvDmaTT` for TT memory or the channel VRAM context handle otherwise.

Control flow: The move function programs source/destination context DMA, then loops over the resource size in batches of at most 2047 pages. For each batch it writes offsets, pitches, line length/count, format, buffer notify, and a no-op launch. Offsets advance by copied page count.

State/persistence: No persistent file-local state. It consumes channel push state, context DMA handles, and TTM resource start/size.

Dependencies/integration: Called from `nouveau_bo_move_init()`'s method table when class `0x0039` is available. Depends on `nouveau_dma.h`, `nvif/push006c.h`, and class register definitions from `cl0039.h`.

Risks/test signals: Risks are incorrect context DMA selection, page count batching, or offset truncation on old hardware. Tests are BO migration between VRAM/GART/system on NV04-NV4x hardware, pushbuf wait failure injection, and checking `MM: using M2MF for buffer copies` logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo0039.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo5039.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo5039.c

Purpose: Implements NV50 `NV5039` M2MF copy support for TTM BO migration, including pitch and blocklinear memory layout handling.

Important APIs/functions: `nv50_bo_move_m2mf()` performs the copy; `nv50_bo_move_init()` binds the copy object and notification/VRAM context DMA handles.

Control flow: The move path obtains temporary source and destination VMAs from `nouveau_mem(old_reg)->vma[0/1]`, copies up to 4 MiB per push sequence, derives a 64-byte stride and height, configures source and destination layouts based on each resource's `kind`, programs upper/lower offsets, pitches, line length/count, format, and buffer notify, then advances offsets and remaining length.

State/persistence: No local persistent state. It relies on `nouveau_bo_move_prep()` having mapped old/new memory into the temporary VMA slots before execution.

Dependencies/integration: Selected by the BO core for class `0x5039` on suitable channels. Depends on `nouveau_mem`, `nvif/push206e.h`, and `cl5039.h`. It bridges TTM resources to hardware copy engine push methods.

Risks/test signals: Tiled layout programming is sensitive to `kind`, block-size fields, and VMA preparation. Incorrect height/stride math could under-copy tail bytes if resource sizes are not aligned by TTM. Test with tiled and linear BO migration, large BOs over 4 MiB, TT/VRAM transitions, and fallback behavior if push waits fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo5039.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo74c1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo74c1.c

Purpose: Provides an NV84-era copy path using the `NV74C1` engine, labelled CRYPT in the BO move method table.

Important APIs/functions: `nv84_bo_move_exec()` emits a compact sequence of `PUSH_NVSQ()` writes containing size, source VMA address, destination VMA address, and copy mode/query settings.

Control flow: The function waits for seven push entries, writes source/destination upper/lower addresses from `nouveau_mem(old_reg)->vma[0/1]`, writes `new_reg->size`, and launches a mode-copy operation without query reporting.

State/persistence: Stateless beyond channel push state and prepared memory VMAs.

Dependencies/integration: Used by `nouveau_bo_move_init()` for class `0x74c1` when available. Depends on `nouveau_dma.h`, `nouveau_mem.h`, and `nvif/push206e.h`.

Risks/test signals: Because register offsets are raw literals, class compatibility is fragile. It assumes the BO core prepared temporary VMAs and that one launch can cover `new_reg->size`. Test with NV84/NV9x BO moves, error handling when `PUSH_WAIT()` fails, and verification that copy fences complete before TTM cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo74c1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo85b5.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo85b5.c

Purpose: Implements NVA3-class DMA copy engine support for BO migration.

Important APIs/functions: `nva3_bo_move_copy()` copies page-sized lines from source to destination VMA addresses using the `NV85B5` push interface. A comment notes class compatibility with NVIDIA/Kepler DMA copy is not fully normalized.

Control flow: The function computes source/destination offsets from prepared memory VMAs, converts the destination size to page count, then loops in batches of at most 8191 pages. Each batch emits source/destination upper/lower addresses, input/output pitches, line length, line count, and a launch/control word.

State/persistence: Stateless besides channel push cursor and memory VMA addresses.

Dependencies/integration: Selected by BO core for class `0x85b5`. Depends on `nouveau_bo.h`, `nouveau_dma.h`, `nouveau_mem.h`, and `nvif/push206e.h`.

Risks/test signals: Batch limits and raw method offsets must match the class. The function assumes page-granular copy and does not explicitly handle sub-page tails, relying on TTM resource sizing. Test on NVA3/NVAF hardware with large migrations, VRAM-to-VRAM and TT/VRAM paths, and fence completion under GPU reset or channel kill.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo85b5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo9039.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo9039.c

Purpose: Provides Fermi `NV9039` M2MF buffer copy support and object initialization for BO migration.

Important APIs/functions: `nvc0_bo_move_m2mf()` emits copy method sequences; `nvc0_bo_move_init()` binds the object handle.

Control flow: The copy path reads prepared source/destination VMAs from `nouveau_mem(old_reg)`, loops over page batches up to 2047 pages, programs destination and source offsets, page pitches, line length/count, and issues `LAUNCH_DMA` with pitch-to-pitch layout, no interrupt, no completion flush, and one-word semaphore struct size.

State/persistence: Stateless except channel push state. It relies on the BO core's temporary VMA preparation and fence cleanup.

Dependencies/integration: Chosen from `nouveau_bo_move_init()` for class `0x9039`. Depends on `nvif/push906f.h` and `cl9039.h`.

Risks/test signals: LAUNCH flags control synchronization behavior and must pair correctly with the BO core's explicit fence wait. Test with Fermi M2MF migration, multi-batch large BOs, GPU fault/reset injection, and software-copy fallback when method submission fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo9039.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo90b5.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo90b5.c

Purpose: Implements Fermi `NV90B5` DMA copy support for BO migration.

Important APIs/functions: `nvc0_bo_move_copy()` loops over page batches and emits raw `NV90B5` copy method offsets plus an immediate launch command.

Control flow: Source and destination offsets come from prepared memory VMAs. The function loops over up to 8191 pages at a time, writes address and pitch/line registers, emits line count, then launches the copy with `PUSH_NVIM()`. Offsets advance by pages copied.

State/persistence: No persistent local state. It consumes channel push state and relies on caller-provided TTM old/new resources.

Dependencies/integration: Used by `nouveau_bo_move_init()` for `COPY0`/`COPY1` class entries and also by some later GRCE/COPY combinations through shared init. Depends on `nouveau_mem` and `nvif/push906f.h`.

Risks/test signals: Raw register offsets and launch value are hardware-specific. Migration correctness depends on VMA preparation and page-aligned TTM sizing. Test with Fermi copy-engine migration, dual copy engine selection, large page-batched BOs, and forced fallback after push wait failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo90b5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_boa0b5.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_boa0b5.c

Purpose: Implements Kepler+ `NVA0B5` DMA copy support used by the BO migration method table.

Important APIs/functions: `nve0_bo_move_copy()` programs virtual source/destination offsets, pitches, line length/count, and `LAUNCH_DMA`; `nve0_bo_move_init()` binds the object handle through a push sequence.

Control flow: The move path waits for push space, writes upper/lower source and destination VMA addresses from `nouveau_mem(old_reg)->vma[0/1]`, uses page-sized pitch and line length, sets line count from `PFN_UP(new_reg->size)`, and launches a non-pipelined, flush-enabled, pitch-to-pitch virtual copy with no semaphore or interrupt.

State/persistence: Stateless except channel push state and the BO core's copy object lifetime.

Dependencies/integration: Preferred for many COPY/GRCE classes in `nouveau_bo_move_init()` from `0xa0b5` through newer class IDs. Depends on `nvif/push906f.h` and `cla0b5.h`.

Risks/test signals: The launch flags choose virtual addressing and no semaphore, so synchronization must come from the fence created by the BO core. Test on Kepler and newer GPUs, including copy-engine class fallback order, large migrations, compressed/kind memory, and GPU reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_boa0b5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_chan.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_chan.c

Purpose: Creates, initializes, idles, kills, and destroys Nouveau command channels. It allocates push buffers, context DMA objects, USERD memory, semaphore BOs, kill events, legacy SW fence objects, and runlist/channel accounting used by fences, GEM command submission, and BO migration.

Important APIs/functions: `nouveau_channel_new()`, `nouveau_channel_del()`, `nouveau_channel_idle()`, `nouveau_channel_kill()`, `nouveau_channels_init()`, and `nouveau_channels_fini()`. Internal construction is split into `nouveau_channel_prep()`, `nouveau_channel_ctor()`, `nouveau_channel_init()`, plus push callbacks `nouveau_channel_wait()` and `nouveau_channel_kick()`.

Control flow: Constructor selects the highest supported channel class, allocates a push BO in coherent GART or optional VRAM, maps it and possibly a GPU VMA, builds ctxdma for legacy classes, allocates USERD for Volta+, creates the nvif channel object, maps USERD, registers kill notification for Fermi+, creates VRAM/GART context DMA for pre-Fermi, initializes the nvif channel push backend for NV50/Fermi/Volta variants, reserves skip NOP space, creates legacy software fence object on old chips, creates a fence context, and joins SVM. Destruction reverses these resources and parts SVM if needed.

State/persistence: `struct nouveau_channel` keeps nvif channel/object handles, runlist/chid/inst/token, push BO/VMA/ctxdma/address, dma ring cursors, USERD offsets, semaphore BO/VMA, fence context pointer, kill event, and killed atomic flag. Driver-wide runlist metadata is allocated from nvif device info.

Dependencies/integration: Depends on nvif channel/object/event/mem APIs, BO/VMM/SVM/fence subsystems, DMA ring helpers, and module parameter `vram_pushbuf`. Used by GEM command submission, TTM copy engine setup, fences, and GPU reset/killed-channel handling.

Risks/test signals: Resource teardown must tolerate partially constructed channels. Push buffer address mode differs sharply by generation and memory domain. Kill events must poison fences to avoid hangs. Test channel create/destroy under failures, SVM join/part, fence idle behavior, vram_pushbuf mode, runlist accounting, and GPU reset/channel kill notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_chan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_chan.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_chan.h

Purpose: Declares the Nouveau channel object and lifecycle API used by command submission, fences, DMA push helpers, copy engines, and SVM.

Important APIs/types: `struct nouveau_channel` embeds `struct nvif_chan` and stores client/VMM references, USERD memory/object, runlist/channel identifiers, VRAM/GART/NVSW objects, push buffer BO/VMA/ctxdma/address, fence pointer, DMA ring cursor fields, USER GET/PUT offsets, semaphore BO/VMA, user/blit objects, kill event, and killed flag. Public functions are `nouveau_channels_init/fini()`, `nouveau_channel_new()`, `nouveau_channel_del()`, `nouveau_channel_idle()`, and `nouveau_channel_kill()`. The module parameter `nouveau_vram_pushbuf` is exported.

Control flow/state contract: Callers create a channel with runmask and context handles, submit through `chan.push` and DMA helpers, idle through a fence, and delete with a pointer-to-pointer API that nulls the caller's reference. Kill state is atomic and propagates to the fence context.

Dependencies/integration: Includes nvif object/event/channel headers and forward-declared device data. It is tightly coupled to `nouveau_dma.h` macros, `nouveau_fence`, BO/VMA allocation, and nvif channel constructors.

Risks/test signals: Consumers must not touch a channel after kill/delete, and ring cursor fields must remain consistent with push callback updates. Test signals include lockdep around channel mutex users, fence context teardown, channel kill events, runlist-aware channel counts, and compile coverage across legacy and GPFIFO channel paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_chan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_connector.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_connector.c

Purpose: Implements DRM connector objects for Nouveau, including detection, EDID acquisition, LVDS/eDP fallbacks, connector properties, mode enumeration/validation, hotplug handling, DP AUX transfer, and connector creation from nvif or legacy DCB data.

Important APIs/functions: `nouveau_connector_create()`, `nouveau_connector_hpd()`, `nouveau_conn_native_mode()`, `nouveau_conn_attach_properties()`, connector atomic property get/set/duplicate/destroy/reset functions, `find_encoder()`, and `nouveau_conn_mode_clock_valid()` via the header. Internal logic includes DDC/OF/LVDS detection, EDID ownership, forced encoder selection, scaler mode injection, depth detection, late/early register, hotplug/IRQ event callbacks, AUX transfer, and DCB-to-DRM connector type mapping.

Control flow: Detection resumes or keeps runtime PM active, probes DP/nvif output status or I2C DDC, fetches EDID through I2C or nvif, corrects DVI-I encoder type from EDID digital bit, falls back to Open Firmware EDID, then analog/TV load detection when forced. LVDS detection tries DDC, ACPI EDID, VBIOS hardcoded panel mode, and embedded EDID, then applies lid status. Mode enumeration adds EDID modes or VBIOS native mode, computes native mode/depth, asks TV encoders for modes, and adds scaler modes for fixed panels.

State/persistence: `struct nouveau_connector` stores DCB connector type/index, nvif connector/event handles, hotplug pending bits, DP AUX, DP encoder, detected encoder, EDID, native mode, backlight, and connector property state. Module parameters control TV detection, lid handling, dual-link TMDS, and HDMI max clock.

Dependencies/integration: Uses DRM connector/helpers/atomic/EDID/DP AUX, runtime PM, ACPI lid/video, vga_switcheroo, Nouveau BIOS, display properties, encoder helpers, DP link functions, and nvif connector/output APIs.

Risks/test signals: Detection spans power management and hotplug work, so runtime PM imbalance or polling deadlocks are key risks. EDID ownership and native mode replacement must avoid leaks. Mode validation depends on hardware generation, HDMI caps, DCB max frequency, and DP link limits. Test with DVI-I analog/digital, DP MST/SST, eDP/LVDS panels without EDID, ACPI lid events, hotplug IRQs, property changes causing modesets, and HDMI clock overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_connector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_connector.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_connector.h

Purpose: Declares Nouveau connector state, connector atom properties, helper macros, backlight hooks, and connector public APIs.

Important APIs/types: `struct nouveau_conn_atom` extends `drm_connector_state` with dithering, scaler/underscan, procamp, and a bitmask of changed property groups. `struct nouveau_connector` wraps `drm_connector` and stores DCB type/index, nvif connector and hotplug/IRQ events, DP AUX, fixed DP encoder, detected encoder, EDID, native mode, optional backlight, and non-atomic property state. Helpers include `nouveau_connector()`, `nouveau_connector_is_mst()`, `nouveau_for_each_non_mst_connector_iter`, and `nouveau_crtc_connector_get()`.

Control flow/state contract: Atomic paths allocate and duplicate `nouveau_conn_atom`; legacy pre-NV50 paths use the embedded `properties_state`. Connector code uses MST filtering for iteration, and `nouveau_crtc_connector_get()` maps a CRTC to its active non-MST connector.

Dependencies/integration: Includes nvif conn/event, NV display class definitions for property enum values, DRM DP/CRTC/encoder utilities, and Nouveau CRTC/encoder declarations. Backlight APIs compile to no-ops when `CONFIG_DRM_NOUVEAU_BACKLIGHT` is disabled.

Risks/test signals: The dither enum values intentionally match hardware fields, so changing them can break nv50/gf119 programming. Connector iteration excludes MST connectors by design. Test build variants with and without backlight/debug configs, property propagation into atomic state, MST connector filtering, and CRTC-to-connector lookup under cloned or disconnected modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_connector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_crtc.h

Purpose: Defines Nouveau's CRTC wrapper and minimal helper API shared by display, connector, cursor, and legacy modeset code.

Important APIs/types: `struct nouveau_crtc` embeds `drm_crtc`, nvif head/event objects, CRTC index, saved flat-panel control and user state, procamp fields, last DPMS state, saved cursor position, current framebuffer metadata, cursor BO/VMA callbacks, LUT depth, and optional save/restore hooks. Inline helpers `nouveau_crtc()` and `to_drm_crtc()` convert between DRM and Nouveau types. `nv04_cursor_init()` is declared for legacy cursor setup.

Control flow/state contract: Display code uses `head` for scanout position and vblank control, connectors use CRTC linkage to find active connector, and cursor paths use the embedded callback table. The structure stores hardware restore state for legacy modesetting and suspend/resume.

Dependencies/integration: Includes DRM CRTC, nvif head, and nvif event headers. It is consumed by `nouveau_display.c`, `nouveau_connector.h`, and generation-specific display implementations.

Risks/test signals: Fields are shared across old and newer display paths, so changes can regress legacy NV04/NV50 behavior. Cursor callback pointers must be initialized before use. Test signals include vblank enable/disable, cursor movement/show/hide, suspend/resume restore, CRTC scanout position accuracy, and legacy DPMS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_debugfs.c

Purpose: Provides Nouveau debugfs files for VBIOS dump, strap register peek, performance state inspection/control, GPUVA reporting, and module-level debugfs root creation.

Important APIs/functions: `nouveau_drm_debugfs_init()`, `nouveau_debugfs_init()`, `nouveau_debugfs_fini()`, `nouveau_module_debugfs_init()`, and `nouveau_module_debugfs_fini()`. File callbacks include `nouveau_debugfs_vbios_image()`, `nouveau_debugfs_strap_peek()`, `nouveau_debugfs_pstate_get/set/open()`, `nouveau_debugfs_gpuva()`, and `nouveau_debugfs_gpuva_regions()`.

Control flow: Per-device init allocates `drm->debugfs` and constructs an nvif control object. Minor init creates writable `pstate`, DRM info files `vbios.rom`, `strap_peek`, GPUVA info, and sets the VBIOS inode size. `pstate` read queries state count, attributes, current power source, user states, and current pstate. `pstate` write parses optional `dc:`/`ac:` prefix and `none`/`auto`/hex state, resumes the device, and sends `NVIF_CONTROL_PSTATE_USER`. GPUVA walks all clients, locks each UVMM, prints drm GPUVA info and region maple tree entries.

State/persistence: Persists only the nvif control object and debugfs root/dentries. It reads `drm->vbios`, clients list, UVMM region trees, and hardware strap register. Pstate writes affect GPU power-management policy via nvif control.

Dependencies/integration: Uses Linux debugfs/seq_file, DRM debugfs helpers, runtime PM, nvif control methods, Nouveau client/UVMM locking, and global `nouveau_debugfs_root`.

Risks/test signals: Debugfs reads can race with client teardown unless locks are correct. Pstate writes are privileged but still need careful input parsing and runtime PM balancing. Test with debugfs disabled build, reading VBIOS size/contents, pstate read/write under suspend, GPUVA output with multiple clients, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_debugfs.h

Purpose: Declares Nouveau debugfs state and init/fini entry points, with compile-time no-op fallbacks when debugfs is disabled.

Important APIs/types: `struct nouveau_debugfs` contains the nvif control object used by debugfs pstate operations. `nouveau_debugfs(dev)` returns `nouveau_drm(dev)->debugfs`. Public functions are `nouveau_drm_debugfs_init()`, `nouveau_debugfs_init()`, `nouveau_debugfs_fini()`, `nouveau_module_debugfs_init()`, and `nouveau_module_debugfs_fini()`. `nouveau_debugfs_root` is exported under `CONFIG_DEBUG_FS`.

Control flow/state contract: Device initialization should call `nouveau_debugfs_init()` before DRM minor debugfs file creation, and teardown should call `nouveau_debugfs_fini()`. Module init/fini controls the top-level debugfs directory. In non-debugfs builds these functions compile away and return success.

Dependencies/integration: Includes DRM debugfs and Nouveau driver headers only under `CONFIG_DEBUG_FS`. The implementation integrates with nvif control and DRM minor debugfs registration.

Risks/test signals: Callers must tolerate `nouveau_debugfs()` returning NULL if initialization failed or debugfs is disabled. Test signals include compile coverage for both config states, module unload, debugfs file creation, and pstate path behavior when the control object is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_display.c

Purpose: Implements Nouveau's DRM display core glue: mode_config setup, display engine construction/destruction, framebuffer validation/creation, hotplug work, vblank/scanning helpers, suspend/resume, property creation, and dumb-buffer allocation.

Important APIs/functions: `nouveau_display_create/destroy/init/fini/suspend/resume()`, `nouveau_display_hpd_resume()`, `nouveau_display_vblank_enable/disable()`, `nouveau_display_scanoutpos()`, `nouveau_framebuffer_new()`, `nouveau_user_framebuffer_create()`, `nouveau_framebuffer_get_layout()`, and `nouveau_display_dumb_create()`. Internal helpers decode and validate NVIDIA format modifiers, check blocklinear sizes, create DRM properties, and process HPD work.

Control flow: Display creation allocates `struct nouveau_display`, initializes DRM mode_config, sets max dimensions by GPU family, initializes polling, constructs nvif display unless modeset is disabled, delegates to nv04 or nv50 display creation, resets mode_config, initializes vblank/CRC, and registers ACPI notification. Init enables HPD/IRQ events before calling generation-specific init and enabling polling. Fini shuts down modesets if needed, blocks events, cancels HPD work for non-runtime teardown, disables polling, and delegates generation-specific fini. Suspend stores atomic state when applicable before fini; resume reinitializes and restores atomic state.

State/persistence: `drm->display` holds nvif display, property pointers, generation-private data, suspend atomic state, and supported format modifiers. HPD pending bits live in `drm` and connector state. Framebuffers retain GEM object references through DRM framebuffer lifecycle.

Dependencies/integration: Uses DRM atomic/helper/framebuffer/vblank/probe APIs, ACPI video notifier, nvif display/head methods, Nouveau GEM/BO, connector and CRTC wrappers, nv50 display/CRC/tile helpers, runtime PM in HPD work, and generation-specific display implementations.

Risks/test signals: Framebuffer modifier validation must match BO kind/tile layout and prevent out-of-bounds scanout. HPD work must balance runtime PM and mode_config locking. Suspend/resume must preserve atomic state and not leave events enabled. Test with linear and blocklinear framebuffers, YUV overlay restrictions pre-NV50, hotplug storms, ACPI reprobe, runtime suspend, vblank timing, dumb buffers, and headless devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_display.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_display.h

Purpose: Declares the Nouveau display core structure and public display/framebuffer APIs shared by DRM driver setup, connector code, CRTC code, and generation-specific display implementations.

Important APIs/types: `struct nouveau_display` stores private generation data, destructor/init/fini callbacks, nvif display object, DRM property pointers for dithering/underscan/procamp, saved atomic suspend state, and supported format modifiers. Public functions cover display lifecycle, HPD resume, vblank control, scanout position, dumb-buffer creation, HDMI mode setup, framebuffer layout decoding, framebuffer creation, and user framebuffer creation.

Control flow/state contract: `nouveau_display_create()` allocates and installs `drm->display`; generation-specific code fills callbacks and modifier lists; `nouveau_display_init/fini()` call the callbacks and manage common event/polling state; framebuffer helpers validate BO layout before DRM framebuffer registration.

Dependencies/integration: Includes Nouveau driver state, nvif display, and DRM framebuffer declarations. It is consumed by `nouveau_display.c`, connector property code, HDMI encoder setup, nv04/nv50 display paths, and GEM/dumb-buffer paths.

Risks/test signals: The callback table must be initialized consistently by generation-specific display creation before common lifecycle calls. Property pointers may be NULL depending on generation. Test signals include headless display creation, property availability by GPU generation, framebuffer modifier support, suspend/resume state restore, and vblank/scanout helper calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dma.c

Purpose: Implements legacy DMA push-ring space management for Nouveau channels. It waits for free push-buffer space, handles GET pointer validation, detects timeouts, and wraps the ring through the skip area.

Important APIs/functions: `nouveau_dma_wait()` is the exported wait/space function used by `RING_SPACE()` and channel push callbacks. Internal `READ_GET()` reads the GPU GET pointer from USERD/user object, resets timeout progress when GET advances, detects lockup after repeated stalled reads, validates that GET is inside the main push buffer, and returns an adjusted dword offset.

Control flow: `nouveau_dma_wait()` loops until `chan->dma.free >= size`. If GET is invalid or in the skip area, it keeps polling. When GET is behind or equal to the current PUT, it uses space to the ring end; if insufficient, it emits a jump back to the start, waits until GET leaves the skip region, writes PUT to `NOUVEAU_DMA_SKIPS`, and resets ring cursors. When GET is ahead, it computes free space as `get - cur - 1`.

State/persistence: Mutates `chan->dma.free`, `cur`, and `put`, writes jump commands into the push BO, and updates hardware PUT through macros in `nouveau_dma.h`.

Dependencies/integration: Depends on channel USERD offsets, push buffer address, BO read/write helpers, nvif user register access, and memory barriers from `WRITE_PUT()`. Used by all legacy push submission paths and class-specific BO move push emission.

Risks/test signals: GET pointer races can cause ring corruption or false GPU lockups. The skip-area race workaround is subtle and generation-sensitive. Test with small ring wrap cases, indirect push buffers that temporarily move GET outside the main ring, stalled GPU timeout behavior, and stress command submission under concurrent fences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dma.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dma.h

Purpose: Declares the DMA push-ring helper API, constants, object handles, and inline macros used by Nouveau channel submission and generation-specific push emitters.

Important APIs/macros: `nouveau_dma_wait()`, `NOUVEAU_DMA_SKIPS`, `NV50_DMA_PUSH_MAX_LENGTH`, `NV50_DMA_IB_MAX`, object handles such as `NvDmaFB`, `NvDmaTT`, `NvNotify0`, `NvSema`, `NvEvoSema0/1`, `RING_SPACE()`, `OUT_RING()`, `WRITE_PUT()`, `FIRE_RING()`, and `WIND_RING()`. It also defines NV_SW method offsets for vblank semaphore/page-flip operations.

Control flow/state contract: Push emitters call `RING_SPACE()` before writing commands with `OUT_RING()` or nvif push helpers. `FIRE_RING()` writes hardware PUT if new commands were emitted and advances the stored PUT cursor; `WIND_RING()` discards unsubmitted commands by resetting `cur` to `put`. `WRITE_PUT()` uses a memory barrier and a readback before the nvif PUT write.

Dependencies/integration: Includes `nouveau_bo.h` and `nouveau_chan.h`. Uses BO-backed push buffer access and nvif user register writes. Generation-specific BO copy files and old display/fence paths depend on these constants.

Risks/test signals: Incorrect space accounting or PUT writes can hang command submission. Consumers must reserve enough space before raw writes. Test through pushbuf wrap stress, fence/page-flip semaphore paths, copy engine push emission, and architectures requiring strict memory ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dma.h -->
