# Research: subset-b-003751

Grouped research for Tegra DRM files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/`. Each section is delimited for deterministic split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/falcon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/falcon.c

Purpose: implements the generic NVIDIA Falcon microcontroller helper used by Tegra media engines. It reads firmware, normalizes little-endian firmware words into a DMA-visible buffer, parses the Falcon firmware v1 headers, DMA-copies code/data into Falcon IMEM/DMEM, starts the CPU, waits for idle, and exposes a simple method write path.

Important APIs/functions: `falcon_read_firmware()` requests the named firmware and records its size. `falcon_load_firmware()` copies and parses the image, then releases the `struct firmware`. `falcon_boot()` waits for memory scrubbing to finish, sets the firmware DMA base, submits 256-byte DMA transfers for data and code sections, enables Falcon interrupts and method/context interfaces, starts CPU execution, and waits for idle. `falcon_execute_method()` writes class method offset/data registers. Internal helpers poll DMA full/idle and parse `falcon_fw_bin_header_v1` plus OS header offsets.

Control flow and state: clients initialize `falcon->dev`, `falcon->regs`, and allocate/populate `falcon->firmware.virt/iova` before boot. Firmware ownership transitions from kernel firmware blob to copied DMA memory; `falcon_exit()` releases only a still-held firmware blob, while engine drivers free the DMA memory.

Dependencies/integration: depends on Linux firmware loading, MMIO, `readl_poll_timeout()`, PCI NVIDIA vendor IDs, and the register layout from `falcon.h`. Used by `nvdec.c` and `nvjpg.c`.

Risks: header parsing trusts offsets after basic magic/version/size checks and does not validate every section boundary against image size. `falcon_boot()` ignores individual `falcon_copy_chunk()` return values inside copy loops, so a DMA FIFO wait failure during a chunk can be lost until final idle wait. Address arguments are 32-bit register writes derived from DMA addresses/offsets, so callers must provide suitable memory.

Test signals: boot logs should show no firmware parse errors or Falcon boot timeouts; runtime resume of NVDEC/NVJPG exercises this path. Fault injection around missing firmware, bad magic/version, DMA poll timeout, and malformed section offsets is high-value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/falcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/falcon.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/falcon.h

Purpose: declares Falcon register offsets/bitfields, firmware image metadata structures, runtime firmware storage, and the public helper API consumed by Tegra engines with Falcon microcontrollers.

Important APIs/types: register macros cover method submission, interrupt masks/destinations, interface enable, CPU boot vector/control, DMA control/base/offset/command, and DMA transfer flags. `struct falcon_fw_bin_header_v1`, `struct falcon_fw_os_header_v1`, and section descriptors model the firmware container parsed by `falcon.c`. `struct falcon_firmware` stores the requested firmware pointer, DMA-visible virtual/physical/IOVA addresses, image size, and parsed code/data/bin sections. `struct falcon` binds device, MMIO base, and firmware state. Public functions are `falcon_init()`, `falcon_exit()`, `falcon_read_firmware()`, `falcon_load_firmware()`, `falcon_boot()`, `falcon_execute_method()`, and `falcon_wait_idle()`.

Control flow and state: the header makes allocation ownership explicit by keeping raw firmware and DMA buffer fields separate. Clients are expected to fill `dev`, `regs`, and DMA memory fields around the helper calls.

Dependencies/integration: only includes Linux integer types directly, but exposed structs use firmware, device, DMA, and `__iomem` types available through including C files. It is included by Falcon-based engine drivers and the helper implementation.

Risks: this header exposes hardware constants without type safety, so incorrect offsets or DMA context choices are compile-clean but hardware-visible. Firmware section fields are `unsigned long`/`size_t` after parsing, while hardware commands use narrower registers.

Test signals: compile coverage from NVDEC/NVJPG drivers, firmware load/boot smoke tests, and register trace validation are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/falcon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/fb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/fb.c

Purpose: provides Tegra DRM framebuffer allocation and validation helpers around GEM-backed planes.

Important APIs/functions: `tegra_fb_get_plane()` converts a DRM framebuffer plane object to `struct tegra_bo`. `tegra_fb_is_bottom_up()` checks the BO bottom-up flag. `tegra_fb_get_tiling()` maps DRM modifiers, including NVIDIA tiled/block-linear and sector-layout modifiers, into `struct tegra_bo_tiling`. `tegra_fb_alloc()` allocates a DRM framebuffer, fills mode metadata, attaches GEM objects, and calls `drm_framebuffer_init()`. `tegra_fb_create()` is the userspace-facing constructor that looks up GEM handles, validates each plane size against pitch/offset/dimensions, and delegates allocation.

Control flow and state: framebuffer state is held by DRM core; this file only binds existing GEM objects to framebuffer planes. On failure during handle lookup or size validation, already referenced plane GEM objects are dropped.

Dependencies/integration: integrates DRM GEM framebuffer helpers, FourCC modifiers, Tegra GEM BO types, and downstream plane code that consumes `tegra_fb_get_tiling()` and `tegra_fb_get_plane()`.

Risks: plane size math uses `unsigned int`, so very large mode/pitch inputs depend on DRM core constraints to avoid overflow. NVIDIA modifier decoding changes `sector_layout` only inside the vendor branch; callers should not assume it is initialized if an invalid non-NVIDIA modifier path is taken.

Test signals: framebuffer creation IOCTL tests for multi-plane formats, invalid handles, undersized GEM buffers, unsupported modifiers, and block-linear/sector-layout planes should exercise the critical paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/fbdev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/fbdev.c

Purpose: implements fbdev emulation probing and mmap support for Tegra DRM.

Important APIs/functions: `tegra_fb_mmap()` maps the first framebuffer plane through DRM GEM mmap and Tegra GEM mmap handling. `tegra_fbdev_fb_destroy()` tears down the helper, undoes the fbdev-specific `vmap()` for page-backed BOs, removes the framebuffer, and releases the DRM client. `tegra_fbdev_driver_fbdev_probe()` creates a dumb GEM BO sized from requested fbdev surface dimensions, allocates a Tegra framebuffer, fills fbdev info, maps backing pages if needed, and sets screen buffer/size/fixed memory information.

Control flow and state: the helper creates a single-plane framebuffer. For IOMMU/page-backed BOs it installs a kernel virtual mapping into `bo->vaddr` only for fbdev and later clears it during destroy. DMA-API BOs already have a persistent CPU mapping.

Dependencies/integration: relies on DRM fb helper infrastructure, Tegra `tegra_bo_create()`, `tegra_fb_alloc()`, and `__tegra_gem_mmap()`.

Risks: the special `bo->vaddr` assignment for page-backed fbdev objects must stay paired with destroy-time `vunmap()` or BO mapping semantics can be confused. Error handling after a failed `vmap()` removes the framebuffer but relies on DRM/GEM references to unwind the BO.

Test signals: boot console/fbdev handoff, fbdev mmap read/write, forced IOMMU and non-IOMMU configurations, and unload/reload leak checks are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/fbdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/firewall.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/firewall.c

Purpose: validates host1x command streams before submission so jobs cannot program engine address registers with IOVAs outside the mappings supplied for that submit.

Important APIs/functions: `tegra_drm_fw_validate()` walks command words from a gather, tracks current class and extended payload length, decodes host1x opcodes, and dispatches register validation. `fw_check_reg()` asks the client whether a register offset is address-bearing and validates the following data word. `fw_check_regs_seq()`, `fw_check_regs_mask()`, and `fw_check_regs_imm()` handle sequential, mask, and immediate write forms. `fw_check_class()` constrains class switches via client callbacks or the client base class.

Control flow and state: the validator keeps a cursor over command data (`pos/end`), current host1x class, submit mapping table, and payload state for wide opcodes. Valid SETCLASS updates `*job_class`, preserving class across gathers/jobs as expected by callers.

Dependencies/integration: depends on `tegra_drm_client_ops.is_addr_reg`, optional `is_valid_class`, submit mapping records, and host1x opcode encoding.

Risks: only recognized write opcodes are allowed; gather/restart/stream/appid opcodes are rejected here. Address validation accepts offsets inclusively between `m->iova` and `m->iova_end`, so mapping end semantics must match the submit mapping code. `SETPYLD` payload state is sticky until overwritten.

Test signals: submit tests should cover legal address writes, out-of-range IOVAs, IMM writes to address registers, invalid classes, SETCLASS masks, INCR_W/NONINCR_W without payload, and unsupported opcodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/firewall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gem.c

Purpose: implements Tegra GEM buffer objects, host1x BO operations, mmap, IOMMU mapping, dumb buffer allocation, and PRIME dma-buf import/export.

Important APIs/functions: `tegra_bo_create()` and `tegra_bo_create_with_handle()` allocate GEM objects and backing memory. `tegra_bo_pin()/unpin()` bridge GEM BOs to host1x mappings for submit/display users, handling imported dma-bufs, page-backed IOMMU BOs, and DMA-API BOs. `tegra_bo_iommu_map()/unmap()` allocate DRM MM IOVA space and map sg tables into the Tegra domain. `tegra_bo_free_object()` removes cached host1x mappings, unmaps imports, releases backing memory, and drops dma-bufs. `tegra_drm_mmap()` and `__tegra_gem_mmap()` implement userspace mapping for page-backed and DMA coherent/write-combined objects. PRIME functions expose and import dma-bufs with CPU sync and vmap/mmap support.

Control flow and state: BO state distinguishes allocated-via-DMA (`vaddr/iova`), allocated-via-IOMMU (`pages/sgt/mm/iova/size`), imported-via-DMA (`dma_buf`), and imported-via-IOMMU (`gem.import_attach/sgt/mm`). Host1x mapping state is transient and reference-counted by host1x core.

Dependencies/integration: integrates DRM GEM, DMA API, dma-buf, IOMMU, DRM MM allocator, host1x BO APIs, and Tegra DRM global `tegra->domain/mm/mm_lock`.

Risks: cleanup paths are complex and must match allocation mode exactly. Imported IOMMU buffers are attached/mapped early, and errors must detach/unmap in the right order. Display users require contiguous mappings when no shared IOMMU group is present. CPU cache sync only runs for page-backed BOs.

Test signals: dumb buffer creation/mmap, PRIME self-import and foreign import/export, host1x pin/unpin with scatter-gather fragmentation, IOMMU exhaustion, module unload with stale mappings, and DMA-buf CPU access tests are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gem.h

Purpose: declares Tegra GEM buffer object types, tiling metadata, conversion helpers, and public GEM/PRIME/mmap APIs.

Important APIs/types: `struct tegra_bo` embeds `drm_gem_object` and `host1x_bo` and stores flags, sg table, IOVA, CPU mapping, imported dma-buf, DRM MM node, pages, mapped size, and tiling. `enum tegra_bo_tiling_mode` and `enum tegra_bo_sector_layout` describe pitch/tiled/block layouts and Tegra-vs-GPU sector layout. Inline `to_tegra_bo()` and `host1x_to_tegra_bo()` are used throughout display and submit code.

Control flow and state: the header documents four memory-source/mapping combinations and the fields valid for each. That table is the practical contract for `gem.c`, display plane pinning, and host1x submission.

Dependencies/integration: includes host1x and DRM GEM headers and exports functions used by framebuffer, fbdev, plane, and driver IOCTL paths.

Risks: consumers must not assume every BO has both `pages` and `vaddr`; the allocation mode controls valid fields. `TEGRA_BO_BOTTOM_UP` is a Tegra-local flag interpreted by framebuffer/display code.

Test signals: build coverage plus tests crossing all four allocation/import modes are the meaningful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr2d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr2d.c

Purpose: platform and host1x client driver for Tegra 2D graphics engines.

Important APIs/functions: `gr2d_probe()` allocates the client, gets clock/reset resources, initializes OPP data, registers the host1x client, and builds the address-register bitmap. `gr2d_init()` requests a host1x channel and syncpoint, attaches IOMMU, and registers with Tegra DRM. `gr2d_exit()` unregisters, suspends, detaches, and releases channel/syncpoint. `gr2d_open_channel()`/`close_channel()` expose the channel to DRM contexts. `gr2d_is_addr_reg()` and `gr2d_is_valid_class()` feed the firewall. Runtime PM acquires/deasserts resets and enables the clock on resume, and stops the channel/asserts memory-client reset/turns off the clock on suspend.

Control flow and state: `struct gr2d` stores one shared channel, one syncpoint, reset bulk array, SoC version, and an address-register bitmap. Userspace jobs flow through `tegra_drm_submit`.

Dependencies/integration: integrates host1x, reset controller, runtime PM/autosuspend, OPP common setup, IOMMU attach, and firewall register classification.

Risks: suspend intentionally avoids full GR2D reset in some cases to prevent host1x cmdproc stalls; reset sequencing is hardware-sensitive. The firewall map must include every address-bearing register or userspace could submit unchecked addresses.

Test signals: host1x client registration, runtime PM suspend/resume, simple 2D job submission, invalid address-register submit rejection, and reset/clock error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr2d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr2d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr2d.h

Purpose: defines GR2D register offsets that contain memory base addresses and the register count used for firewall bitmap sizing.

Important APIs/types: macros cover regular and SB variants of source, destination, pattern, and U/V base address registers. `GR2D_NUM_REGS` defines the upper bound for `DECLARE_BITMAP(addr_regs, GR2D_NUM_REGS)`.

Control flow and state: no runtime logic; the constants seed `gr2d_addr_regs[]` in `gr2d.c`.

Dependencies/integration: consumed by `gr2d.c` and indirectly by command-stream firewall validation.

Risks: missing a new address register would weaken submit validation; an incorrect `GR2D_NUM_REGS` could cause valid offsets to be ignored.

Test signals: firewall tests for each defined address register and compile-time coverage through `gr2d.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr2d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr3d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr3d.c

Purpose: platform and host1x client driver for Tegra 3D graphics engines across Tegra20/30/114.

Important APIs/functions: `gr3d_probe()` obtains clocks/resets, initializes power domains, builds the host1x DRM client, registers it, and populates address-register bitmap. `gr3d_init()` obtains a host1x channel and syncpoint, attaches IOMMU, and registers with Tegra DRM. `gr3d_exit()` unregisters and tears resources down. `gr3d_is_addr_reg()` classifies address-bearing 3D registers for firewall use. Power helpers handle legacy powergate sequencing when DT lacks generic power domains and support one or two 3D domains/clocks.

Control flow and state: `struct gr3d` stores a shared channel, SoC-specific clock/reset counts, optional PM domain list, and address-register bitmap. Runtime resume acquires resets, enables clocks, deasserts resets, and enables autosuspend; suspend stops the channel, asserts resets, disables clocks, and releases resets.

Dependencies/integration: uses host1x, Tegra PMC legacy powergate API, PM domains/OPP, reset bulk APIs, runtime PM, IOMMU, and Tegra DRM submit.

Risks: legacy power handling has SoC/DT-dependent branches and needs clock/reset balancing. Address-register coverage is large; omissions affect firewall security. Tegra20 single-clock handling intentionally treats 3D1 specially.

Test signals: probe on each compatible, runtime PM cycles, simple 3D submit, invalid address writes, and DT variants with/without generic power domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr3d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr3d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr3d.h

Purpose: defines GR3D address-register offsets and register-count bound used by firewall validation.

Important APIs/types: macros generate indexed attribute, texture, global surface, overflow surface, and sampler surface address registers, plus fixed Z/tag/output address registers. `GR3D_NUM_REGS` sizes the address bitmap.

Control flow and state: no executable logic; constants are consumed by `gr3d_addr_regs[]`.

Dependencies/integration: integrated with `gr3d.c` firewall callbacks and host1x submit validation.

Risks: register macro arithmetic must match hardware class layout. Missing address-register definitions allow unchecked command-stream pointers.

Test signals: firewall tests for representative indexed ranges and static review against hardware class docs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr3d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hda.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hda.c

Purpose: parses Intel HDA format words from HDMI codec scratch registers into Tegra HDMI audio format state.

Important APIs/functions: `tegra_hda_parse_format()` decodes PCM/non-PCM, base sample rate, multiplier/divider, bit depth, and channel count into `struct tegra_hda_format`.

Control flow and state: the function is stateless except for filling the caller-provided format struct. HDMI IRQ handling calls it when HDA scratch0 reports a valid format, then reconfigures HDMI audio.

Dependencies/integration: depends on ALSA HDA verb bit definitions and is included by `hdmi.c`.

Risks: sample-rate calculation uses integer arithmetic in `fmt->sample_rate *= (mul + 1) / (div + 1)`, so divider values greater than multiplier can collapse to zero before multiplication. Invalid bit-depth fields trigger `WARN(1)` and fall back to 8 bits.

Test signals: unit-style tests for known HDA format words, especially 44.1/48 kHz families, non-PCM, multichannel, and invalid bit-depth encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hda.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hda.h

Purpose: declares HDMI/HDA audio format data used by Tegra HDMI and the HDA parser.

Important APIs/types: `struct tegra_hda_format` contains sample rate, channel count, bit depth, and PCM flag. `tegra_hda_parse_format()` is exported to HDMI code.

Control flow and state: the structure is embedded in `struct tegra_hdmi` and is updated by codec callbacks or HDA scratch IRQs.

Dependencies/integration: includes Linux types and is consumed by `hda.c` and `hdmi.c`.

Risks: no validity flags are included, so users infer validity from fields such as nonzero sample rate.

Test signals: compile coverage and HDMI audio configuration tests that verify struct contents after format parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hdmi.c

Purpose: full Tegra HDMI output driver: platform probe, host1x client lifecycle, DRM connector/encoder integration, mode programming, TMDS electrical setup, audio/ELD/infoframe handling, debugfs register dump, and HDA/SPDIF codec interoperability.

Important APIs/functions: `tegra_hdmi_probe()` gets clocks, reset, regulators, DDC/HPD output resources, MMIO, IRQ, OPP data, and registers the host1x client. `tegra_hdmi_init()/exit()` create encoder/connector or bridge connector, initialize common output state, enable regulators, and register the HDMI codec for non-HDA SoCs. Encoder helpers validate clocking, enable/disable SOR/TMDS/video/audio, and program display-controller HDMI output bits. Audio helpers compute N/CTS/AVAL, program audio FS tables, ELD, AVI/audio/vendor infoframes, and reconfigure live audio. `tegra_hdmi_irq()` handles HDA codec scratch0 format changes.

Control flow and state: `struct tegra_hdmi` persists connector/output, MMIO, regulators, clocks/reset, SoC config, audio source/format, pixel clock, DVI/HDMI mode, stereo flag, audio device, and mutex. Runtime resume powers PM, clock, and reset; encoder enable resumes host1x client, configures hardware, then enables packets/audio. Disable reverses visible output and suspends.

Dependencies/integration: depends on DRM connector/encoder helpers, bridge connector, EDID/ELD/infoframe APIs, HDMI codec, runtime PM/OPP, regulators, reset/clock APIs, `tegra_output`, `tegra_dc`, and register definitions from `hdmi.h`.

Risks: mode enable sequence is hardware-sensitive and includes a `BUG_ON()` retry exhaustion while waiting for SOR power state. Audio lock disables the HDMI IRQ, so lock/IRQ ordering matters. `dvi` fallback is used when audio setup fails. TMDS tables are SoC-specific and pixel-clock-threshold based. Debugfs reads require active CRTC.

Test signals: HDMI hotplug/mode-set, DVI sink fallback, audio playback via SPDIF/HDA, ELD correctness, suspend/resume with active display, debugfs register reads, and invalid mode clock tests are central.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hdmi.h

Purpose: defines Tegra HDMI/SOR register offsets and bitfield macros used by `hdmi.c`.

Important APIs/types: macros cover SOR state/power/PLL/lane drive, HDMI generic/audio/AVI/vendor infoframes, ACR/N/CTS audio registers, input control, pin drive/pre-emphasis/peak-current tables, HDA scratch/ELD/presence registers, interrupts, and pad control.

Control flow and state: no executable logic; the file is the hardware ABI for HDMI register programming and debugfs register enumeration.

Dependencies/integration: consumed by `hdmi.c` TMDS tables, encoder enable/disable, IRQ handling, audio setup, and debugfs.

Risks: dense bitfield definitions are easy to misuse because many fields have SoC-specific encodings. HDCP registers are defined although the implementation notes HDCP is not implemented.

Test signals: register trace comparisons during mode-set/audio enable, build coverage, and hardware validation across Tegra20/30/114/124.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hub.c

Purpose: implements the Tegra186+ display hub, shared window-group planes, display-hub atomic private state, and runtime PM for hub clocks/resets.

Important APIs/functions: `tegra_shared_plane_create()` creates universal DRM planes with Tegra186+ formats/modifiers and zpos. Plane helpers check format/tiling, pin framebuffers, assign window ownership, program scaling/blending/YUV/address registers, and disable windows. `tegra_display_hub_atomic_check()` selects the active display clock with the highest pixel rate; `tegra_display_hub_atomic_commit()` sets hub clock parent/rate and updates fetch-meter/common state. `tegra_display_hub_prepare()/cleanup()` currently enable/disable all window groups with usecounts. Probe wires clocks, reset, window-group resets, child head clocks, runtime PM, host1x client registration, and child population.

Control flow and state: `struct tegra_display_hub` owns a DRM private object, host1x client, clocks, reset, head clocks, SoC info, and window groups. `struct tegra_shared_plane` extends `tegra_plane` with a window-group pointer. Runtime PM enables display/DSC/hub/head clocks and deasserts reset; suspend reverses it.

Dependencies/integration: integrates DRM atomic private objects, Tegra DC register access, common plane helpers, host1x client PM, OF child population, clocks/resets, and framebuffer tiling helpers.

Risks: window groups are globally enabled because finer enable points are missing. Shared-plane ownership can fail with `-EBUSY` if hardware owner differs. Scaling code contains TODO/XXX notes and currently forces 5-tap programming. 64-bit GPU sector-layout address flag is conditional on DMA address width.

Test signals: atomic multi-head commits, shared plane movement between CRTCs, block-linear and sector-layout modifiers, YUV multi-plane scanout, scaling, runtime suspend/resume, and hub clock parent selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hub.h

Purpose: declares display hub and shared-plane data structures plus public hub integration functions.

Important APIs/types: `struct tegra_windowgroup` tracks per-window-group reset, parent host1x client, usecount, and lock. `struct tegra_shared_plane` embeds `tegra_plane`. `struct tegra_display_hub` stores DRM private object, host1x client, clocks, resets, head clocks, SoC capabilities, and window groups. `struct tegra_display_hub_state` stores atomic-selected DC/clock/rate. Public functions cover prepare/cleanup, shared-plane creation, atomic check, and atomic commit.

Control flow and state: hub state is part of DRM atomic private object machinery, allowing clock-parent/rate decisions to be staged before commit.

Dependencies/integration: depends on DRM plane/private state concepts, host1x client types, reset/clock types, and `plane.h`.

Risks: window-group usecount correctness depends on paired prepare/cleanup and mutex protection. `supports_dsc` controls optional clock acquisition.

Test signals: build coverage, atomic hub state duplication/destruction tests, and prepare/cleanup balance checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/mipi-phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/mipi-phy.c

Purpose: provides default MIPI D-PHY timing calculation and validation helpers.

Important APIs/functions: `mipi_dphy_timing_get_default()` fills a `struct mipi_dphy_timing` using D-PHY v1.2 timing formulas derived from bit period. `mipi_dphy_timing_validate()` checks each field against D-PHY v1.2 min/max/formula constraints.

Control flow and state: stateless helper functions operate on caller-owned timing structs. Defaults are in nanoseconds and intentionally assume reverse-direction HS mode for `hstrail` because only one field is available.

Dependencies/integration: used by Tegra display/DSI-style PHY code outside this subset and declared in `mipi-phy.h`.

Risks: formulas depend on caller-provided `period`; wrong units produce plausible but invalid timings. Validation checks exact relationships for TA values and can reject board-specific overrides.

Test signals: known-good DSI bit rates should validate defaults; boundary tests for each invalid range are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/mipi-phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/mipi-phy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/mipi-phy.h

Purpose: declares MIPI D-PHY timing structure and helper prototypes.

Important APIs/types: `struct mipi_dphy_timing` contains global operation timing parameters such as clock/data prepare, settle, trail, LPX, turnaround, init, and wakeup times in nanoseconds. Functions provide default fill and validation.

Control flow and state: no persistent state; consumers pass mutable timing structs.

Dependencies/integration: shared by Tegra MIPI/DSI PHY code.

Risks: the field `taget` appears to represent TA_GET and must be used consistently despite the spelling. All fields are unsigned ints, so unit conversion overflow is caller-sensitive.

Test signals: compile coverage and validation of defaults across supported bit periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/mipi-phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/nvdec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/nvdec.c

Purpose: host1x/DRM client driver for Tegra NVDEC video decoder engines, supporting Falcon firmware on Tegra210/186/194 and RISC-V bootrom firmware descriptors on Tegra234.

Important APIs/functions: `nvdec_probe()` inherits DMA mask, maps registers, gets clocks, sets max clock rate, reads optional host1x class, initializes Falcon or RISC-V boot descriptors/carveout/reset, and registers the host1x client. `nvdec_init()/exit()` attach IOMMU, request channel/syncpoint, register/unregister DRM client, manage dma parameters, and free firmware memory. Runtime resume enables clocks and boots either RISC-V or Falcon. `nvdec_load_falcon_firmware()` allocates firmware memory via DMA API or shared Tegra DRM allocator, loads/parses firmware, and maps shared-domain memory for cache maintenance. `nvdec_boot_riscv()` runs bootloader and OS descriptors through the bootrom and waits for debug info to clear.

Control flow and state: `struct nvdec` owns Falcon/RISC-V state, MMIO, DRM client, channel, clocks, reset, SoC config, and carveout base. Userspace contexts obtain the shared channel and submit through `tegra_drm_submit`.

Dependencies/integration: integrates host1x, Tegra DRM submit/memory context, Falcon/RISC-V helpers, memory controller carveout info, runtime PM, IOMMU, clocks, reset, and stream-ID programming.

Risks: firmware allocation/free paths depend on `client->group`. RISC-V boot requires DT descriptor offsets and memory-controller carveout index 1. SID programming is SoC-dependent. Exit assumes firmware memory exists after runtime paths; failed early initialization needs correct guard behavior.

Test signals: probe on all compatibles, runtime resume boot, decode job submit, memory-context negotiation, missing firmware, bad RISC-V descriptors, stream-ID/IOMMU configurations, suspend/resume under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/nvdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/nvjpg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/nvjpg.c

Purpose: host1x/DRM client driver for Tegra210 NVJPG JPEG engine using Falcon firmware.

Important APIs/functions: `nvjpg_probe()` inherits DMA mask, maps registers, gets and maxes the NVJPG clock, initializes Falcon, and registers the host1x client. `nvjpg_init()/exit()` attach/detach IOMMU, register/unregister the Tegra DRM client, manage inherited DMA parameters, force runtime suspend, and free firmware memory. `nvjpg_load_falcon_firmware()` mirrors NVDEC Falcon loading with DMA API or shared Tegra DRM allocation depending on host1x client group. Runtime resume enables the clock, loads firmware once, and boots Falcon; suspend disables the clock. `nvjpg_can_use_memory_ctx()` explicitly reports memory contexts unsupported.

Control flow and state: `struct nvjpg` stores Falcon state, MMIO, DRM client, device, clock, and static config. Unlike NVDEC, no channel/open/submit callbacks are provided in this file, so it primarily registers engine capabilities and firmware boot state.

Dependencies/integration: depends on host1x client registration, Tegra DRM client lifecycle, runtime PM, Falcon helpers, DMA API, IOMMU attach, and firmware `nvidia/tegra210/nvjpg.bin`.

Risks: the exit path frees firmware memory based on fields populated only after runtime resume. If the device is registered but never resumed, zero/null handling must remain safe. Memory contexts are disabled, so callers must not assume group address-space support.

Test signals: probe/runtime resume, firmware missing/corrupt, autosuspend, IOMMU attach failure, and unload without prior firmware boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/nvjpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/output.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/output.c

Purpose: common output/connector support for Tegra display outputs, including panel/bridge discovery, EDID/DDC, HPD, CEC notifier, connector mode acquisition, and output suspend/resume.

Important APIs/functions: `tegra_output_probe()` discovers panel/bridge through graph or legacy `nvidia,panel`, obtains DDC adapter, optional fixed EDID, HPD GPIO/IRQ, and initializes polling. `tegra_output_connector_get_modes()` prefers panel modes, otherwise reads fixed or DDC EDID, updates connector display info, updates CEC physical address, and adds modes. `tegra_output_connector_detect()` uses HPD GPIO or panel presence and invalidates CEC on disconnect. `tegra_output_init()/exit()` enable/disable HPD IRQ and create HDMI CEC notifier. `tegra_output_find_possible_crtcs()` computes encoder CRTC mask from DT output mapping with a fallback mask.

Control flow and state: `struct tegra_output` owns panel/bridge/DDC/EDID/HPD/CEC resources used by output-specific drivers such as HDMI and RGB. HPD IRQ is requested during probe but disabled until connector initialization.

Dependencies/integration: uses DRM OF, panel, bridge connector, EDID, HPD helper, I2C, GPIO descriptor, and CEC notifier APIs.

Risks: mixing graph and legacy panel bindings triggers a warning and legacy panel assignment. HPD IRQ ordering is important to avoid handler access before connector setup. `drm_edid_alloc()` result is stored without explicit null-error distinction.

Test signals: DT graph and legacy panel variants, DDC EDID and fixed EDID, HPD connect/disconnect, CEC physical address updates, suspend/resume IRQ balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/plane.c

Purpose: common Tegra DRM plane state, framebuffer pinning, format conversion, memory-bandwidth estimation, legacy blending/transparency state, and interconnect setup.

Important APIs/functions: `tegra_plane_funcs` provides atomic plane operation hooks. Reset/duplicate/destroy manage `struct tegra_plane_state`, including IOVA/map arrays and bandwidth fields. `tegra_plane_prepare_fb()` calls DRM GEM prepare then pins framebuffer BOs to DC-visible IOVAs; cleanup unpins. `tegra_plane_state_add()` performs DRM plane clipping/visibility checks, calculates bandwidth, and marks the DC state plane update bit. `tegra_plane_format()` maps DRM FourCC formats to Tegra window color-depth values and byte-swap modes. `tegra_plane_format_is_yuv()` and indexed helpers classify hardware formats. Legacy helpers emulate opaque formats and update sibling blending state. `tegra_plane_interconnect_init()` obtains memory ICC paths.

Control flow and state: plane atomic state stores mappings for up to three planes, tiling/format/swap, reflect flags, legacy blending, opacity, and bandwidth. Pinning selects `map->phys` for non-group display paths requiring contiguous memory or BO IOVA for grouped/shared-domain paths.

Dependencies/integration: integrates DRM atomic/GEM helpers, host1x BO pinning, Tegra framebuffer/BO helpers, DC state, interconnect framework, and hardware color-depth constants from DC headers.

Risks: framebuffer cleanup assumes `state->crtc` still identifies a DC. Bandwidth is an estimate and intentionally ignores some layout effects except tiled x2. Legacy transparency forces sibling planes into the atomic state when zpos/opacity changes. Multi-plane YUV pitch constraints are enforced by callers such as hub.

Test signals: atomic plane updates/disables, mmap/imported BO scanout, fragmented BO rejection without IOMMU group, all supported FourCC mappings, zpos/alpha changes, ICC path acquisition, and bandwidth votes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/plane.h

Purpose: declares Tegra plane and plane-state structures plus common plane helper APIs.

Important APIs/types: `struct tegra_plane` embeds `drm_plane` and stores owning DC, register offset/index, and interconnect paths. `struct tegra_cursor` extends it with cursor BO/dimensions. `struct tegra_plane_state` extends DRM plane state with host1x mappings, per-plane IOVAs, tiling, hardware format/swap, reflection flags, legacy blending/opacity, and bandwidth fields. Public helpers cover prepare/cleanup, state add, format mapping/classification, legacy state setup, and interconnect init.

Control flow and state: these structures are allocated/duplicated by `plane.c` and consumed by DC/hub update paths.

Dependencies/integration: depends on DRM plane types, Tegra BO, host1x mapping, ICC, and DC-specific consumers.

Risks: arrays are fixed at three planes, matching supported framebuffer plane count assumptions. `to_tegra_plane_state(NULL)` returns NULL for convenience, but callers must still guard dereferences.

Test signals: compile coverage and atomic state duplication/destruction under plane updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/rgb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/rgb.c

Purpose: implements the display-controller local RGB/LVDS-style output path for Tegra DCs.

Important APIs/functions: `tegra_dc_rgb_probe()` finds the `rgb` child node, probes common output resources, gets display clocks and PLL parents, and stores the output on the DC. Encoder enable/disable programs pinmux/output tables, sync polarities, data-enable/interface format, and commits DC state. `tegra_rgb_encoder_atomic_check()` configures DC clock state, either by changing PLL-derived parent rate or by using the shift-clock divider when parent changes are unsafe. `tegra_dc_rgb_init()` creates the encoder, wraps direct panels into panel bridges, attaches bridges/connectors, initializes common output state, and limits possible CRTCs to the owning DC. Remove/exit release clocks and output resources.

Control flow and state: `struct tegra_rgb` stores common output, parent DC, PLL handles, parent clock, and DC clock. Probe-time resources persist until DC removal; encoder hooks program the DC during atomic modesets.

Dependencies/integration: uses common `tegra_output`, DRM bridge/panel connector helpers, Tegra DC register writes, clock APIs, and DT child node discovery.

Risks: older DT compatibility requires panel wrapping and optional bridge modeling. Clock parent policy differs by SoC and can produce approximate clocks via divider when PLL rate changes are not allowed. Static pin register tables are hardware-specific.

Test signals: panel and bridge DT variants, mode-set sync polarity, clock-rate validation on Tegra20 versus later SoCs, suspend/remove resource balance, and RGB-only possible CRTC mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/rgb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/riscv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/riscv.c

Purpose: provides shared helpers for Tegra DRM engines that boot firmware through a RISC-V bootrom, currently used by Tegra234 NVDEC.

Important APIs/functions: `tegra_drm_riscv_read_descriptors()` reads bootloader and OS manifest/code/data offsets from device-tree properties into `tegra_drm_riscv_descriptor` structs and rejects an all-zero descriptor set. `tegra_drm_riscv_boot_bootrom()` selects the RISC-V core, programs shifted physical addresses for manifest, code, and data, programs secure DMA config with GSC ID, locks DMA config, starts the CPU, and polls bootrom return code for PASS.

Control flow and state: callers initialize `dev` and `regs`; descriptors persist in `struct tegra_drm_riscv`. Boot is stateless per descriptor except for hardware registers. NVDEC sequences bootloader then resets and boots OS.

Dependencies/integration: depends on OF property reading, MMIO writes, `readl_poll_timeout()`, and consumers that provide carveout physical base addresses.

Risks: descriptor `code_size` and `data_size` fields exist but are not populated by the current reader. Address programming shifts physical addresses by 8, so alignment and carveout base correctness are critical. Poll timeout reports raw return code.

Test signals: DT property validation, bad/all-zero descriptor rejection, bootrom timeout/error paths, and Tegra234 NVDEC runtime resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/riscv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/riscv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/riscv.h

Purpose: declares RISC-V firmware descriptor and boot helper state for Tegra DRM engines.

Important APIs/types: `struct tegra_drm_riscv_descriptor` stores manifest, code, and data offsets plus size fields. `struct tegra_drm_riscv` stores caller-provided device/MMIO pointers and bootloader/OS descriptors. Public functions read descriptors from DT and execute a descriptor through the bootrom.

Control flow and state: descriptors are read during probe and reused during runtime resume boot sequences.

Dependencies/integration: consumed by `nvdec.c` for Tegra234. Requires device tree properties matching the reader in `riscv.c`.

Risks: size fields are part of the ABI but currently unused/unfilled by the helper implementation, which can mislead future callers.

Test signals: compile coverage, DT descriptor parsing tests, and RISC-V boot smoke tests through NVDEC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/riscv.h -->
