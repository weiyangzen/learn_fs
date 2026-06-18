# subset-b-003543 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc_v12_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc_v12_0.h

Purpose: defines AMD UMC v12.0 RAS address/register constants and conversion macros used to decode machine-check memory-error records into SOC physical-address fields, UMC channel/socket identifiers, and bad-page retirement candidates.

Important APIs/types/functions: exports `ras_umc_func_v12_0`, `ras_umc_get_badpage_count()`, and `ras_umc_get_badpage_record()`. The main API surface is macro based: MCA/MCMP field masks, UMC instance/channel counts, normalized-address mapping counts, SOC PA field extractors/builders, bank/channel hash macros, ACA IPID decoders, bad-column masking, and retirement-loop sizing.

Control flow: no runtime code is implemented here. Consumers include this header to transform `MCA_UMC_UMC0_MCUMC_ADDRT0.ErrorAddr` and ACA IPID fields. A likely flow is: extract MCA error address, derive die/socket/UMC/channel from IPID, generate candidate PAs through bank/channel hashing and normalized-address expansion, mask bad column bits, then hand results to RAS bad-page reporting.

State and persistence: header constants encode hardware topology assumptions: 4 UMC instances, 8 channel instances, 4 AID nodes, 8 sockets, 192 GiB socket local-fabric size, and 16 retirement-loop variants. Persistent effect is indirect through page-retirement records produced by callers.

Dependencies/integration: depends on `ras.h`, `REG_GET_FIELD`, AMD RAS core context types, and UMC v12.0 hardware register layout. It integrates with AMDGPU RAS bad-page query paths.

Risks: macro arithmetic has side effects if arguments are expressions with mutations. Incorrect bit positions or hash enable constants can retire the wrong physical pages. Topology constants are brittle across ASIC variants. `0x...L` masks rely on width assumptions. Test signals: decode known MCA/IPID samples, validate candidate PA count and socket/channel mapping, exercise bad-column masking, and compare bad-page records with firmware/hardware error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc_v12_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/Kconfig

Purpose: defines the DRM "ARM devices" menu and build-time configuration for ARM HDLCD, legacy Mali Display Processor, and sourced Komeda display support.

Important APIs/types/functions: Kconfig symbols are `DRM_HDLCD`, `DRM_HDLCD_SHOW_UNDERRUN`, `DRM_MALI_DISPLAY`, and sourced `drivers/gpu/drm/arm/display/Kconfig` for `DRM_KOMEDA`. Symbols select DRM client setup, KMS helpers, GEM DMA helpers, bridge support for HDLCD, and videomode helpers for Mali display drivers.

Control flow: Kconfig dependency resolution determines which modules/objects the Makefiles build. `DRM_HDLCD` and `DRM_MALI_DISPLAY` require `DRM`, `OF`, ARM/ARM64/COMPILE_TEST, and `COMMON_CLK`; Komeda is sourced separately but remains under the DRM-dependent ARM menu.

State and persistence: no runtime state. Its persistent effect is the generated kernel `.config`, module availability, and compile coverage for the driver family.

Dependencies/integration: integrates ARM DRM drivers into the global DRM build. It feeds `drivers/gpu/drm/arm/Makefile` and `display/Kbuild`.

Risks: missing selects can produce link failures or partial feature exposure. Broad `COMPILE_TEST` support can expose architecture assumptions. Incorrect dependency tightening can silently drop display drivers from builds. Test signals: Kconfig `olddefconfig`, ARM/ARM64 and COMPILE_TEST builds, module-name checks for `hdlcd`, `mali-dp`, and `komeda`, and verifying selected helper libraries appear in `.config`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/Makefile

Purpose: maps ARM DRM Kconfig symbols to built objects and subdirectories.

Important APIs/types/functions: object variables are `hdlcd-y`, `mali-dp-y`, `obj-$(CONFIG_DRM_HDLCD)`, `obj-$(CONFIG_DRM_MALI_DISPLAY)`, and `obj-$(CONFIG_DRM_KOMEDA)`. HDLCD links `hdlcd_drv.o` and `hdlcd_crtc.o`; Mali DP links driver, hardware, plane, CRTC, and memory-writeback objects; Komeda descends into `display/`.

Control flow: kbuild evaluates enabled symbols and either links composite objects or enters the Komeda display subdirectory. The file is declarative and has no runtime execution.

State and persistence: persistent output is kernel object/module composition. The `mali-dp` module name follows the composite object name; Komeda is built through `display/komeda/Makefile`.

Dependencies/integration: consumes symbols from `drivers/gpu/drm/arm/Kconfig` and `drivers/gpu/drm/arm/display/Kconfig`. It participates in the parent DRM build tree.

Risks: object-list drift causes missing functions at link time or dead code. Adding Komeda objects here instead of under `display/` would break the current source-tree separation. Test signals: `make M=drivers/gpu/drm/arm`, allmodconfig link checks, and verifying module object names match Kconfig help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/Kbuild

Purpose: kbuild bridge for ARM display subdrivers, currently routing `CONFIG_DRM_KOMEDA` into the `komeda/` subdirectory.

Important APIs/types/functions: single kbuild rule `obj-$(CONFIG_DRM_KOMEDA) += komeda/`.

Control flow: when `DRM_KOMEDA` is enabled, kbuild recurses into `drivers/gpu/drm/arm/display/komeda/`; otherwise nothing under this subdirectory is built.

State and persistence: no runtime state. Persistent effect is source-tree-aligned build inclusion for Komeda.

Dependencies/integration: depends on `display/Kconfig` declaring `DRM_KOMEDA` and on the parent ARM DRM Makefile adding `display/` for the same symbol.

Risks: duplicate gating in parent and child build files means a symbol-name mismatch would silently omit the Komeda driver. Test signals: build with `CONFIG_DRM_KOMEDA=y/m`, inspect built-in or module object inclusion, and run `make M=drivers/gpu/drm/arm/display`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/Kconfig

Purpose: declares the ARM Komeda display driver configuration symbol.

Important APIs/types/functions: `config DRM_KOMEDA` is a tristate symbol for the ARM Komeda display processor. It depends on `DRM`, `OF`, and `COMMON_CLK`, and selects DRM client setup, KMS helpers, GEM DMA helpers, and videomode helpers.

Control flow: Kconfig uses this symbol to include the Komeda build and expose module selection. The help text documents D71 support and module name `komeda`.

State and persistence: no runtime state. It persists as `.config` and determines whether the platform driver and KMS module are compiled.

Dependencies/integration: sourced from `drivers/gpu/drm/arm/Kconfig`; consumed by ARM/display kbuild files.

Risks: dependencies are minimal; missing architecture or IOMMU constraints can leave runtime probe failures to the driver. Over-selecting helpers can increase build footprint but keeps link dependencies available. Test signals: Kconfig dependency traversal, module build with `m`, built-in with `y`, and COMPILE_TEST builds if the parent menu allows them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/include/malidp_io.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/include/malidp_io.h

Purpose: provides small MMIO helpers for Mali/Komeda display register access using byte offsets over a `u32 __iomem *` base.

Important APIs/types/functions: `malidp_read32()`, `malidp_write32()`, `malidp_write64()`, `malidp_write32_mask()`, and `malidp_write_group()`. The helpers shift register byte offsets by two to address 32-bit words and wrap Linux `readl()`/`writel()`.

Control flow: register users compute byte offsets from hardware headers, then call these helpers for scalar, masked, 64-bit split, or contiguous table writes. `malidp_write32_mask()` reads the current register, clears mask bits, and ORs the supplied value.

State and persistence: all state is hardware MMIO state. There is no software cache, locking, or barrier beyond the semantics of `readl()`/`writel()`.

Dependencies/integration: depends on `<linux/io.h>`. Used broadly by D71 component/device code for GCU, LPU, CU, DOU, layer, scaler, and timing registers.

Risks: callers must pass byte offsets and already-mask `v` for masked writes; `v | tmp` can set bits outside `m` if not pre-masked. `malidp_write64()` assumes low then high register order. No endianness or posted-write verification is provided. Test signals: register trace/dump comparisons, sparse `__iomem` checks, hardware readback after masked writes, and table-programming tests for gamma/scaler coefficients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/include/malidp_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/include/malidp_product.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/include/malidp_product.h

Purpose: defines product/core identification helpers and a compact Komeda configuration ID representation.

Important APIs/types/functions: `MALIDP_CORE_ID()` packs product, major, minor, and status fields. Extractors return product, major, minor, and status from a core ID. Product IDs identify D71, D32, and Linlon D6. `union komeda_config_id` exposes max line size, number of pipelines, scalers, layers, and rich layers as bitfields over a `u32`.

Control flow: chip identification reads `GLB_CORE_ID`, uses the product extractor, and chooses D71-family chip functions. Sysfs `config_id` fills the union from enumerated pipeline resources and emits a hex value.

State and persistence: no dynamic state. The bitfield layout is a stable ABI-like representation exposed through sysfs.

Dependencies/integration: included by `komeda_dev.h` and D71 code. It couples register IDs to Linux-visible product naming and sysfs.

Risks: C bitfield layout depends on compiler/endianness expectations, though use is local to generated value. Product ID expansion requires updating D71 identification. Test signals: probe logs show expected product/revision, sysfs `core_id`/`config_id` match hardware documentation, and unsupported product IDs fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/include/malidp_product.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/include/malidp_utils.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/include/malidp_utils.h

Purpose: supplies common bit/range/polling helpers for Mali display drivers.

Important APIs/types/functions: `has_bit()`, `has_bits()`, `dp_wait_cond()`, `struct malidp_range`, `set_range()`, and `malidp_in_range()`.

Control flow: `dp_wait_cond()` repeatedly sleeps with `usleep_range()` until a condition becomes true or the retry count reaches zero, returning `0` or `-ETIMEDOUT`. Range helpers are used during resource enumeration and atomic validation to check layer/scaler/compositor dimensions.

State and persistence: no persistent state. `dp_wait_cond()` evaluates its condition more than once, so callers must pass expressions safe for repeated evaluation.

Dependencies/integration: includes Linux delay and errno headers. Used by D71 reset/opmode/TBU connect waits and Komeda validation paths.

Risks: macro condition evaluation can hide side effects. `has_bits(bits, mask)` assumes `bits` is the required set and `mask` is the available set; reversed arguments would invert semantics. Poll timing is fixed by callers and may be fragile on slow hardware. Test signals: timeout-path tests for reset/opmode/IOMMU, boundary-value tests for `malidp_range`, and review of all `has_bits()` call sites for argument order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/include/malidp_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/Makefile

Purpose: builds the Komeda DRM driver composite object and sets include paths for shared Mali display headers.

Important APIs/types/functions: `ccflags-y` includes `../include` and the Komeda source directory. `komeda-y` aggregates core driver, device, format, color, pipeline, framebuffer, KMS, CRTC, plane, writeback connector, private object, event, and D71 backend objects. `obj-$(CONFIG_DRM_KOMEDA) += komeda.o` exposes the module/built-in object.

Control flow: kbuild links all listed objects into `komeda.o` when enabled. D71 files are always part of the Komeda object because current compatible strings all use `d71_identify()`.

State and persistence: no runtime state. Build output determines which symbols are available to the module.

Dependencies/integration: depends on `display/Kbuild` and shared include headers. It includes `komeda_wb_connector.o`, which is not in this subset but is part of the writeback integration referenced by KMS and pipeline state.

Risks: omitting a source file creates unresolved symbols or feature loss. Include-path order could mask header-name collisions. Test signals: module link, `modinfo komeda`, and compile coverage after adding new chip backends or KMS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_component.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_component.c

Purpose: implements D71-family hardware component discovery, validation, register programming, disable paths, and debug dumps for Komeda pipeline components.

Important APIs/types/functions: externally visible `d71_probe_block()`, `d71_dump()`, and `d71_pipeline_funcs`. Internal component handlers include layer, writeback layer, compositor, scaler, splitter, merger, image processor, and timing controller init/update/disable/dump functions. `get_resources_id()` maps D71 block IDs to Komeda component IDs; `d71_downscaling_clk_check()` enforces D71 scaler timing constraints.

Control flow: resource enumeration reads each block header and calls `d71_probe_block()`. For recognized block types it stores LPU/CU/DOU base addresses or creates Komeda components with chip-specific function tables. During atomic commit, generic pipeline update calls each active component `update()` to write framebuffer addresses, AFBC controls, input IDs, scaler phases, composition inputs, color/gamma/CTM coefficients, timing registers, and enable bits. Disable clears enable bits and input IDs.

State and persistence: persistent state is hardware register programming and component capability fields such as line sizes, ranges, supported rotations, supported color formats/depths, and split/merge limits. No software cache is maintained beyond DRM private states passed into update functions.

Dependencies/integration: depends on D71 register macros, Komeda pipeline/KMS/framebuffer/color types, `malidp_io`, DRM format/rotation/blending/color APIs, and seq_file debugfs dumps.

Risks: register offset arithmetic is dense and hardware-specific. Split/scaler phase math and AFBC payload/end-address selection are high-risk. Some init failures return `-1` instead of errno. Masked writes rely on callers passing values already limited to masks. Test signals: atomic modeset and plane-update tests, AFBC/non-AFBC framebuffer scanout, YUV color conversion, writeback jobs, split scaling, dual-link timing, downscaling clock rejection, IRQ error injection, and debugfs register dump review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_component.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_dev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_dev.c

Purpose: supplies the D71/D32/Linlon D6 chip backend for Komeda: identification, IRQ decoding, resource enumeration, format table initialization, opmode changes, flushes, reset, and optional TBU/IOMMU connection.

Important APIs/types/functions: `d71_identify()` returns `d71_chip_funcs`; `d71_read_block_header()` and `d71_enum_resources()` enumerate hardware; `d71_irq_handler()` maps GCU/LPU/CU/DOU status to `komeda_events`; `d71_enable_irq()`, `d71_disable_irq()`, `d71_change_opmode()`, `d71_flush()`, `d71_connect_iommu()`, and `d71_disconnect_iommu()` implement chip hooks.

Control flow: probe reads core ID, validates product, resets GCU, discovers pipeline count and configuration either from legacy PERIPH or GCU config registers, creates generic Komeda pipelines, then scans fixed-size blocks and delegates to `d71_probe_block()`. Runtime PM resume enables IRQs and connects TBU; suspend disconnects TBU, disables IRQs, and clocks are handled by core device code. IRQ handling reads `GLB_IRQ_STATUS`, clears raw IRQ registers, translates block status bits, and resets sticky error bits.

State and persistence: `struct d71_dev` is stored in `mdev->chip_data` and holds MMIO sub-block addresses, capability bits, global scaler coefficient addresses, and D71 pipeline wrappers. Hardware state includes GCU opmode, config-valid flush bits, IRQ masks, and TBU control.

Dependencies/integration: integrates with `komeda_dev_funcs`, `komeda_pipeline_add()`, D71 component probing, DRM format capabilities, `malidp_io`, and runtime PM.

Risks: block scan assumes fixed 0x200 spacing and valid `num_blocks`. IRQ masks omit some events unless vblank is toggled separately. TBU wait timeouts are hardware-sensitive. Product IDs all share D71 funcs, so subtle D32/D6 differences depend on config probing. Test signals: probe on each compatible, suspend/resume, IRQ/vblank/flip/error events, IOMMU on/off paths, reset timeout behavior, and format-modifier validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_dev.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_dev.h

Purpose: declares D71-private device and pipeline structures plus D71 backend entry points.

Important APIs/types/functions: `struct d71_pipeline` embeds `struct komeda_pipeline` and stores LPU/CU/DOU MMIO bases plus DOU forward-transform coefficient base. `struct d71_dev` stores parent `komeda_dev`, block/pipeline/rich-layer counts, max dimensions, dual-link/TBU capability bits, GCU/global coefficient/PERIPH MMIO bases, and D71 pipeline pointers. Public declarations include `d71_pipeline_funcs`, `d71_probe_block()`, `d71_read_block_header()`, and `d71_dump()`. `to_d71_pipeline()` converts generic to chip-specific pipeline.

Control flow: created by `d71_enum_resources()`, filled during block probing, and consumed by D71 component update/IRQ/flush/debug paths.

State and persistence: all fields are runtime hardware-discovery state. The structures persist for the lifetime of `komeda_dev` and are freed by D71 cleanup.

Dependencies/integration: includes `komeda_dev.h`, `komeda_pipeline.h`, and `d71_regs.h`. It is the bridge between generic Komeda core and D71-specific registers.

Risks: array limits (`D71_MAX_PIPELINE`, `D71_MAX_GLB_SCL_COEFF`) must match hardware probing. Null sub-block pointers cause crashes in IRQ/update paths if block enumeration is incomplete. Test signals: probe logs, debugfs register dump, block-header fuzz/error handling, and multi-pipeline/dual-link hardware validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_regs.h

Purpose: central D71 register map and hardware bit definitions for GCU, LPU, CU, DOU, layers, writeback, scaler, merger, splitter, backend timing, image processing, and coefficient blocks.

Important APIs/types/functions: macro groups define common block offsets, field extractors, IRQ/status bits, control bits, size/offset/crop packers, opmodes, AFBC controls, scaler coefficient addressing, block types, D71 limits/defaults, and `struct block_header`. `get_block_type()` extracts the D71 block type.

Control flow: no executable control flow. D71 code reads headers with these offsets, maps block types during probing, programs registers during component updates, and decodes events during IRQ handling.

State and persistence: describes hardware state layout. Persistent effects occur through callers writing register values generated with these macros.

Dependencies/integration: consumed by `d71_dev.c`, `d71_component.c`, and `d71_dev.h`. It must match hardware documentation for D71/D32/D6-family register compatibility.

Risks: any wrong offset, bit mask, or packing width directly corrupts hardware programming. Some defaults encode policy (`D71_DEFAULT_PREPRETCH_LINE`, cache bits, bus width). `HV_SIZE`/`HV_OFFSET` silently truncate to 12/13-bit fields. Test signals: register dump comparison with vendor docs, mode timing readback, scaler/layer programming traces, IRQ status injection, and static compile checks for macro users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_color_mgmt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_color_mgmt.c

Purpose: converts DRM color-management properties into Komeda/D71 hardware coefficient tables.

Important APIs/types/functions: `komeda_select_yuv2rgb_coeffs()` selects fixed 10-bit YUV-to-RGB matrices for BT.601, BT.709, and BT.2020. `drm_lut_to_fgamma_coeffs()` samples a DRM gamma LUT into 65 foreground gamma coefficients. `drm_ctm_to_coeffs()` converts a 3x3 DRM CTM into Q3.12 coefficients.

Control flow: plane layer updates use selected YUV coefficients for YUV framebuffer input. CRTC/improc validation converts gamma/CTM blobs when color management changes; D71 improc update writes the resulting tables to DOU coefficient or IPS registers.

State and persistence: static coefficient tables are immutable. Generated coefficient arrays live in `komeda_improc_state` and persist only as DRM private atomic state until committed to registers.

Dependencies/integration: depends on DRM color-management helpers and `komeda_color_mgmt.h`. Integrated through `komeda_pipeline_state.c` and `d71_component.c`.

Risks: `komeda_select_yuv2rgb_coeffs()` can return NULL for unexpected encoding; callers write the returned pointer without explicit fallback. Gamma sampling assumes LUT size covers sector indexes up to 4095. Test signals: color-management atomic commits, null/invalid encoding handling, CTM conversion accuracy, gamma ramp conformance, and YUV limited/full range visual tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_color_mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_color_mgmt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_color_mgmt.h

Purpose: declares Komeda color-management dimensions and conversion helpers.

Important APIs/types/functions: constants define coefficient counts and precision: 12 YUV2RGB/RGB2YUV coefficients, 12-bit precision, 65 gamma coefficients, 4096 LUT size, and 9 CTM coefficients. Function declarations are `drm_lut_to_fgamma_coeffs()`, `drm_ctm_to_coeffs()`, and `komeda_select_yuv2rgb_coeffs()`.

Control flow: header-only declarations used by pipeline-state validation and D71 hardware update code.

State and persistence: no state. Constants determine DRM color-management property sizes and hardware table write counts.

Dependencies/integration: includes `<drm/drm_color_mgmt.h>` and is included by `komeda_pipeline.h`, `d71_component.c`, and color conversion implementation.

Risks: changing coefficient counts without matching D71 register writes corrupts table programming. `KOMEDA_COLOR_LUT_SIZE` must match DRM CRTC color-management setup. Test signals: compile-time users of constants, CRTC gamma property size, and D71 register dump after gamma/CTM commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_color_mgmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_crtc.c

Purpose: implements DRM CRTC setup, atomic CRTC validation/enable/disable/flush, vblank control, event handling, mode validation/fixup, clock management, and bridge attachment for Komeda pipelines.

Important APIs/types/functions: exported `komeda_crtc_get_color_config()`, `komeda_crtc_get_aclk()`, `komeda_kms_setup_crtcs()`, `komeda_kms_add_crtcs()`, `komeda_crtc_handle_event()`, and `komeda_crtc_flush_and_wait_for_flip_done()`. Helper funcs implement DRM CRTC atomic hooks and CRTC funcs.

Control flow: atomic check updates clock ratio on modesets, builds display data flow for active CRTCs, then releases unclaimed resources. Enable resumes runtime PM, changes D71 opmode, sets clocks, enables vblank, and flushes. Flush updates affected pipelines and queues writeback jobs before chip flush. Disable performs one- or two-phase component disable, waits for flip completion, disables vblank/clocks, and drops runtime PM. IRQ events deliver vblank, writeback completion, and pending flip events.

State and persistence: `komeda_crtc_state` stores affected/active pipes, clock ratio, and slave z-order. `komeda_dev->dpmode` is protected by mutex. `disable_done` temporarily tracks disable completion.

Dependencies/integration: depends on DRM atomic helpers, vblank, bridge, runtime PM, clocks, Komeda pipeline state, and chip funcs.

Risks: flip timeout path can leave user-visible stalls. Dual-link mode halves horizontal timings and pixel clock, so bridge/mode tests matter. Opmode/clock transitions are serialized but error handling continues after some clock failures. Test signals: atomic modeset/page-flip tests, dual display and dual-link modes, suspend/resume, vblank enable/disable, writeback completion, hotplug/bridge attach, and two-phase disable regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_dev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_dev.c

Purpose: creates, initializes, exposes, resumes/suspends, and destroys the core `komeda_dev` hardware object.

Important APIs/types/functions: exported `komeda_dev_create()`, `komeda_dev_destroy()`, `komeda_dev_resume()`, and `komeda_dev_suspend()`. Internal helpers provide debugfs register dump, sysfs `core_id`, `config_id`, `aclk_hz`, and device-tree parsing for IRQ, reserved memory, pipeline nodes, pixel clocks, output ports, and output links.

Control flow: create allocates `komeda_dev`, maps registers, enables `aclk`, identifies chip, initializes format table, enumerates resources, parses DT, assembles pipelines, configures DMA segment size, detects IOMMU, disables clock, creates sysfs/debugfs, and returns the device. Destroy removes sysfs/debugfs, re-enables clock for teardown, destroys pipelines, releases reserved memory and chip data, unmaps registers, releases clock, and frees memory. Resume enables clock/IRQs and optionally connects IOMMU/TBU; suspend disconnects, disables IRQs, and disables clock.

State and persistence: holds MMIO base, clocks, IRQ, chip info, format table, pipelines, IOMMU domain, debugfs root, display mode, and error verbosity. Sysfs/debugfs expose runtime hardware state.

Dependencies/integration: platform resources, OF graph, reserved memory, DMA/IOMMU, debugfs/sysfs, D71 identify funcs, and Komeda pipeline assembly.

Risks: error paths call destroy on partially initialized objects. Manual devm cleanup plus devm ownership needs care. DT pipeline nodes and pxclk names are mandatory. Test signals: probe failure injection, DT variants, sysfs/debugfs reads under runtime PM, IOMMU and no-IOMMU devices, and repeated bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_dev.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_dev.h

Purpose: defines the generic Komeda hardware-device contract, event model, chip callbacks, display modes, and `struct komeda_dev`.

Important APIs/types/functions: event and error bit definitions classify VSYNC/FLIP/URUN/IBSY/OVR/EOW and hardware errors. `struct komeda_dev_funcs` is the chip backend vtable for format init, resource enumeration, cleanup, IOMMU, IRQ, vblank, register dump, opmode, and flush. `struct komeda_dev` stores device resources, chip info, format table, clocks, pipelines, IOMMU, debugfs, and error verbosity. Display modes describe inactive, display0, display1, and dual display.

Control flow: core code calls chip funcs during probe, PM, IRQ, vblank, atomic flush, and opmode transitions. Events flow from chip IRQ handler into KMS CRTC handling and event printing.

State and persistence: `komeda_dev` persists for platform-device lifetime. `dpmode` is mutable runtime state protected by `lock`. `err_verbosity` persists via debugfs until driver removal.

Dependencies/integration: includes Linux device/clock, `komeda_pipeline.h`, product IDs, and format caps. Used by nearly every Komeda source file.

Risks: callback contract is broad; missing chip funcs cause null dereferences if core assumes presence. Event bit allocation must match printer and CRTC handling. Test signals: callback coverage in chip backends, IRQ event classification, debugfs `err_verbosity`, dual-display opmode transitions, and static analysis for NULL func usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_drv.c

Purpose: platform-driver entry point for Komeda, tying hardware device creation to DRM/KMS registration and power management.

Important APIs/types/functions: `struct komeda_drv` stores `mdev` and `kms`. `dev_to_mdev()` exposes driver data to sysfs helpers. Probe/remove/shutdown manage lifecycle. Runtime and system PM hooks call Komeda suspend/resume and DRM mode-config suspend/resume. OF match table maps `arm,mali-d71`, `arm,mali-d32`, and `armchina,linlon-d6` to `d71_identify`.

Control flow: probe sets a 40-bit coherent DMA mask, allocates driver state, creates `komeda_dev`, enables runtime PM or resumes directly, attaches KMS, stores drvdata, and starts DRM clients. Remove detaches KMS, disables/suspends PM, destroys device, and clears drvdata. Shutdown performs atomic KMS shutdown.

State and persistence: per-platform `komeda_drv` persists in `dev_get_drvdata()`. Runtime PM state controls whether hardware is clocked/IRQ-enabled. DRM registration exposes device nodes and clients.

Dependencies/integration: Linux platform/OF/PM, DRM module platform driver macro, DRM client setup, `komeda_dev`, and `komeda_kms`.

Risks: drvdata is set after KMS attach, so sysfs/debugfs paths must not assume it during earlier create steps except where safe. Runtime PM disabled path manually resumes/suspends. Test signals: bind/unbind, module load/unload, system suspend/resume, runtime PM autosuspend behavior, DRM client/fbdev creation, and DMA mask failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_event.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_event.c

Purpose: formats and rate-limits Komeda hardware events and optional DRM state dumps.

Important APIs/types/functions: exported `komeda_print_events()`. Internal `komeda_sprintf()` appends bounded text, `evt_str()` maps event bits to strings, and `is_new_frame()` detects FLIP/EOW frame boundaries.

Control flow: KMS IRQ handler receives decoded chip events and calls `komeda_print_events()`. The function computes an event mask based on `mdev->err_verbosity`, rate-limits to the first relevant event per frame unless disabled, prints combined global/pipe event strings, and optionally dumps DRM atomic state on error/warning events.

State and persistence: uses static `en_print` as global rate-limit state across devices. `err_verbosity` is mutable through debugfs.

Dependencies/integration: depends on DRM printing/state dump and event definitions in `komeda_dev.h`.

Risks: static rate-limit state is not per-device. Event string buffer truncation is silent except bounded. Duplicate/incorrect event labels would mislead debugging. Test signals: IRQ event injection, toggling `err_verbosity`, multiple-device behavior, state-dump-on-event, and ensuring repeated errors are suppressed or printed according to settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_format_caps.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_format_caps.c

Purpose: implements format/modifier capability lookup and plane format-list generation for Komeda layers.

Important APIs/types/functions: `komeda_get_format_caps()`, `komeda_get_afbc_format_bpp()`, `komeda_supported_modifiers[]`, `komeda_format_mod_supported()`, `komeda_get_layer_fourcc_list()`, and `komeda_put_fourcc_list()`.

Control flow: framebuffer creation and plane validation ask the format table for a fourcc/modifier match. For linear formats it selects caps with no AFBC layouts; for AFBC it verifies requested feature bits and layout against caps. Plane creation builds a de-duplicated fourcc list for a layer type. Format/mod support also calls optional chip-specific validation.

State and persistence: `komeda_supported_modifiers` is a global immutable list exposed to DRM plane initialization. Allocated fourcc lists are temporary and freed after plane init.

Dependencies/integration: depends on DRM fourcc/AFBC definitions, `malidp_utils`, D71 format table initialization, framebuffer creation, and plane funcs.

Risks: `has_bits(afbc_features, caps->supported_afbc_features)` allows subsets but rejects feature bits not advertised; correctness depends on caller expectations. Fourcc de-duplication uses a reverse loop with signed index. Modifier list is broad and filtered later by per-layer checks. Test signals: format/modifier enumeration with IGT, AFBC layout/feature combinations, per-layer supported formats, and framebuffer creation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_format_caps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_format_caps.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_format_caps.h

Purpose: declares Komeda format capability data structures, AFBC helper macros, and format capability APIs.

Important APIs/types/functions: AFBC macros wrap DRM AFBC modifier bits. Layer-type flags distinguish rich, simple, and writeback layers. Alignment constants define AFBC header/body/superblock requirements. `struct komeda_format_caps` records hardware format ID, fourcc, supported layer types, rotations, AFBC layouts, and AFBC features. `struct komeda_format_caps_table` stores the table and optional chip-specific predicate.

Control flow: D71 initializes a table; framebuffer and plane paths query it for caps and modifier support.

State and persistence: format tables are immutable chip data referenced by `komeda_dev->fmt_tbl`; `komeda_fb` stores a pointer to the selected caps.

Dependencies/integration: Linux types, DRM fourcc UAPI, D71 format table, framebuffer size/address handling, and plane format setup.

Risks: AFBC alignment constants feed memory-size validation; incorrect values can under-check buffers. Hardware IDs are consumed directly by D71 layer register programming. Test signals: framebuffer size validation, AFBC scanout, writeback format checks, and cross-checking hardware IDs against D71 docs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_format_caps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_framebuffer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_framebuffer.c

Purpose: creates Komeda framebuffers, validates memory layout/alignment, computes pixel DMA addresses, and checks layer compatibility.

Important APIs/types/functions: `komeda_fb_create()`, `komeda_fb_check_src_coords()`, `komeda_fb_get_pixel_addr()`, `komeda_fb_is_layer_supported()`, plus framebuffer funcs destroy/create_handle. AFBC and non-AFBC size checks validate GEM objects, pitch alignment, payload offset, and plane sizes.

Control flow: DRM mode config calls `komeda_fb_create()`, which allocates `komeda_fb`, finds format caps, fills DRM framebuffer fields, runs AFBC or linear size checks, initializes DRM framebuffer, and records whether IOMMU virtual addresses are used. Later atomic validation uses source-coordinate and layer-support helpers; D71 update uses computed DMA addresses.

State and persistence: `komeda_fb` extends `drm_framebuffer` with selected format caps, `is_va`, aligned AFBC dimensions, AFBC minimum size, and AFBC payload offset. GEM object refs persist until framebuffer destroy.

Dependencies/integration: DRM GEM DMA/framebuffer helpers, overflow checking, Komeda format caps, device bus width, and D71 layer programming.

Risks: non-AFBC error paths can leak looked-up GEM refs if later plane validation fails before cleanup. `komeda_fb_get_pixel_addr()` returns a `dma_addr_t` but uses `-EINVAL` for invalid plane. AFBC size math is security-sensitive. Test signals: IGT framebuffer tests, malformed pitch/offset/size handles, AFBC tiled and non-tiled buffers, multi-plane YUV, IOMMU/no-IOMMU addressing, and kmemleak/refcount checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_framebuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_framebuffer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_framebuffer.h

Purpose: declares the Komeda framebuffer extension and framebuffer helper APIs.

Important APIs/types/functions: `struct komeda_fb` embeds `drm_framebuffer` and stores `format_caps`, `is_va`, AFBC aligned width/height, `afbc_size`, and `offset_payload`. `to_kfb()` converts from DRM framebuffer. Functions cover creation, source-coordinate checking, pixel-address lookup, and layer support.

Control flow: header connects DRM mode-config `fb_create`, atomic validation, and D71 hardware update paths.

State and persistence: `komeda_fb` persists as long as the DRM framebuffer object exists. Its AFBC metadata is computed once at creation and reused by atomic state and register programming.

Dependencies/integration: includes DRM framebuffer and Komeda format caps headers. Used by KMS, plane, pipeline-state, and D71 component code.

Risks: callers assume every framebuffer passed to Komeda is a `komeda_fb`; mixing generic DRM framebuffers would break `to_kfb()`. Test signals: framebuffer lifecycle, writeback framebuffer handling, source crop validation, and AFBC metadata consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_framebuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_kms.c

Purpose: initializes the DRM device, GEM/fbdev helpers, mode configuration, IRQ handler, atomic check/commit tail, and KMS attach/detach/shutdown lifecycle.

Important APIs/types/functions: `komeda_kms_attach()`, `komeda_kms_detach()`, `komeda_kms_shutdown()`, `komeda_gem_dma_dumb_create()`, KMS IRQ handler, `komeda_kms_check()`, and commit-tail helpers. Defines `komeda_kms_driver` with GEM DMA ops and atomic modesetting.

Control flow: attach allocates managed DRM device, stores `mdev`, initializes mode config, adds private objects, planes, vblank, CRTCs, writeback connectors, requests IRQ, initializes polling, and registers DRM. Atomic check performs modeset checks, adds affected planes, normalizes zpos, then helper plane checks. Commit tail disables modesets, commits active planes, enables modesets, waits for Komeda flip-done flushes, waits DRM flip completion, and cleans planes.

State and persistence: `komeda_kms_dev` embeds `drm_device` and stores CRTCs. Normalized z-order is written into plane states per commit. IRQ registration and DRM device registration persist until detach.

Dependencies/integration: DRM atomic/GEM DMA/fbdev/vblank/probe helpers, Komeda framebuffer, CRTC/plane/private/writeback setup, and chip IRQ event decoding.

Risks: custom `komeda_kms_atomic_commit_hw_done()` waits every active CRTC, so one stuck pipe can delay all commits. Zpos uniqueness is stricter than generic DRM. Cleanup must handle partial attach failures. Test signals: IGT atomic, zpos conflict tests, dumb buffer pitch alignment, IRQ handling, vblank init, attach failure injection, and hot-unplug/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_kms.h

Purpose: defines Komeda DRM/KMS wrapper objects and declares KMS-facing helper APIs.

Important APIs/types/functions: structs `komeda_plane`, `komeda_plane_state`, `komeda_wb_connector`, `komeda_crtc`, `komeda_crtc_state`, and `komeda_kms_dev`; conversion macros; inline helpers `is_writeback_only()`, `is_only_changed_connector()`, and `has_flip_h()`. Declares CRTC/plane/private/writeback/KMS lifecycle and event functions.

Control flow: object wrappers are used by DRM init and atomic state hooks. Inline helpers support writeback-only commits, connector-change detection, and split-flow orientation under rotation/reflection.

State and persistence: KMS objects persist for DRM device lifetime; plane/CRTC private states persist per atomic state. `komeda_crtc` records master/slave pipelines, slave plane mask, writeback connector, pending disable completion, and encoder.

Dependencies/integration: DRM atomic, blend, device, writeback, print APIs and Komeda pipeline types.

Risks: wrappers assume specific embedding layout for `container_of`. `has_flip_h()` depends on DRM rotation simplification and affects split crop direction. Test signals: CRTC/plane state duplication/destruction, writeback connector paths, split with rotations/reflections, and multi-pipeline CRTC masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_pipeline.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_pipeline.c

Purpose: manages generic Komeda pipeline/component allocation, lookup, assembly, input/output capability verification, slave-pipeline discovery, and register/debug dumps.

Important APIs/types/functions: `komeda_pipeline_add()`, `komeda_pipeline_destroy()`, `komeda_pipeline_get_component()`, `komeda_pipeline_get_first_component()`, `komeda_component_add()`, `komeda_component_destroy()`, `komeda_pipeline_get_slave()`, `komeda_assemble_pipelines()`, `komeda_pipeline_dump()`, and `komeda_pipeline_dump_register()`.

Control flow: chip enumeration adds pipelines and components. Assembly verifies that advertised inputs resolve to existing components, fills reverse supported-output masks, finds right-side layers for layer split, and disables dual-link if hardware timing controller does not support it. KMS setup uses slave discovery to map CRTCs. Debug paths dump component capabilities and registers.

State and persistence: `komeda_pipeline` stores component pointers, availability masks, layer/scaler counts, DT graph nodes, dual-link flag, and chip funcs. Component structures store capabilities, IDs, MMIO bases, and function tables.

Dependencies/integration: OF node lifecycle, Linux clocks, seq_file, DRM logging, Komeda device/KMS/pipeline headers, and chip-specific component creation.

Risks: component IDs encode array positions and cross-pipeline resources, so wrong IDs miswire pipelines. `komeda_component_add()` requires layers/scalers in sequence. Destroy assumes component masks are valid and clocks/nodes were acquired. Test signals: resource enumeration logs, DT dual-link fallback, layer split right-layer selection, debugfs register dumps, and component graph consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_pipeline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_pipeline.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_pipeline.h

Purpose: defines the generic Komeda pipeline/component model, per-component atomic state structures, data-flow configuration, chip pipeline callbacks, and pipeline/component APIs.

Important APIs/types/functions: component IDs/masks; `struct komeda_component_funcs`; base `komeda_component` and derived layer/scaler/compiz/merger/splitter/improc/timing structs and states; `struct komeda_data_flow_cfg`; `struct komeda_pipeline_funcs`; `struct komeda_pipeline` and `struct komeda_pipeline_state`; conversion macros and public builder/update/disable APIs.

Control flow: plane/wb/CRTC atomic checks construct `komeda_data_flow_cfg`, acquire private states for components, and fill component-specific state. Commit code later calls `komeda_pipeline_update()` or `komeda_pipeline_disable()` to dispatch chip callbacks.

State and persistence: distinguishes static hardware capabilities in component structs from transient atomic private states. Pipeline state tracks CRTC ownership and active component mask; component states track binding user, active/changed/affected inputs, and component-specific register data.

Dependencies/integration: DRM atomic helpers, Mali range utilities, color management, framebuffer/KMS forward declarations, and chip backends.

Risks: active/changed/affected input masks are subtle and must stay consistent for incremental register updates. Maximum input/layer/scaler constants cap hardware support. Test signals: atomic private state duplicate/reset behavior, resource contention across CRTCs, component changed-input updates, split/merge flows, and compile checks for all conversion macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_pipeline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_pipeline_state.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_pipeline_state.c

Purpose: performs Komeda atomic resource allocation and data-flow validation for layers, scalers, splitters, mergers, compositors, image processors, timing controllers, writeback, and display output.

Important APIs/types/functions: exported `pipeline_composition_size()`, `komeda_complete_data_flow_cfg()`, layer/wb/display/split data-flow builders, `komeda_release_unclaimed_resources()`, `komeda_pipeline_disable()`, `komeda_pipeline_update()`, and `komeda_pipeline_get_old_state()`. Internal helpers allocate pipeline/component private states, bind users, validate dimensions/formats/scaling, split flows, and build component input chains.

Control flow: plane check initializes data flow, validates layer and optional scaler/split/merge, then feeds compiz. CRTC check validates slave/master compiz output, improc color/depth, and timing controller. Writeback builds `compiz -> scaler/splitter/merger -> wb_layer`. Release/unbound logic marks no-longer-used components for disable. Commit update iterates changed components and calls chip update/disable functions.

State and persistence: atomic private state records component users, inputs, per-component parameters, active component masks, and pipeline ownership. No persistent storage; committed state becomes current DRM private object state and hardware registers after flush.

Dependencies/integration: DRM atomic state locking, CRTC/plane/writeback state, Komeda framebuffer and format checks, scaler clock callback, color conversion, and chip component funcs.

Risks: resource allocation can return `-EBUSY` or `-EDEADLK` under contention. Split math handles rotation, reflection, YUV alignment, overlap, crops, and z-order and is high risk. `komeda_compiz_validate()` sets output before checking `dflow` non-NULL, though current callers pass non-NULL. Test signals: IGT atomic plane scaling/rotation/zpos, dual-pipeline composition, split-scaling edge cases, writeback scaling, resource release after plane disable, and modeset disable/enable cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_pipeline_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_plane.c

Purpose: creates DRM planes for Komeda layers and implements plane atomic validation/state lifecycle.

Important APIs/types/functions: `komeda_kms_add_planes()` is exported. Internal `komeda_plane_atomic_check()` builds layer data flow, `komeda_plane_init_data_flow()` maps DRM plane state to Komeda flow, and helpers create/destroy/reset/duplicate plane states. Plane funcs expose format-modifier checks and DRM atomic plane operations.

Control flow: KMS setup iterates each pipeline layer, creates a `komeda_plane`, builds a layer-specific format list, initializes a universal plane, attaches helper funcs, and creates rotation, alpha, blend, color, and zpos properties. Atomic check skips disabled/inactive cases, gets the target CRTC state, initializes data flow, and calls normal or split layer builder. Actual hardware updates are deferred to CRTC flush.

State and persistence: each `komeda_plane` points to a hardware layer. `komeda_plane_state` extends DRM plane state with z-order list linkage and `layer_split` flag. CRTC slave plane masks are updated at plane creation.

Dependencies/integration: DRM atomic/blend/color property APIs, Komeda framebuffer, format caps, KMS CRTC state, and pipeline-state builders.

Risks: zpos range is hard-coded 0..8 and duplicate zpos is rejected by KMS check. `layer_split` consumes two z-order slots. Format-modifier support checks rotation as 0 at plane level, with full rotation later in atomic check. Test signals: plane property enumeration, all layer formats/modifiers, rotation/reflection, alpha/blending, zpos conflicts, disabled CRTC updates, and split-layer cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_private_obj.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_private_obj.c

Purpose: registers DRM private objects for every Komeda pipeline component and implements create/duplicate/destroy functions for their atomic private states.

Important APIs/types/functions: exported `komeda_kms_add_private_objs()` and `komeda_kms_cleanup_private_objs()`. Private state funcs exist for layers, scalers, compiz, splitter, merger, improc, timing controller, and pipeline. `komeda_component_state_reset()` clears transient binding/input state during duplication.

Control flow: KMS attach adds a pipeline private object, then private objects for each component present in each pipeline. Atomic duplication copies old state but resets `binding_user`, active/changed inputs, and active component masks so each commit recomputes resource ownership. Cleanup walks DRM mode-config private object list and finalizes each object.

State and persistence: private object initial states persist in DRM mode config. Per-commit duplicates hold transient validation results that become current on atomic commit. Component state reset preserves affected inputs so disables/changed-input tracking can compare old and new state.

Dependencies/integration: DRM private object helpers, Komeda KMS/device/pipeline structures, and pipeline-state validation/update code.

Risks: repetitive state functions are easy to update inconsistently. Cleanup finalizes all private objects in mode config, so ordering with mode-config cleanup matters. Reset semantics are central to avoiding stale users and missed disables. Test signals: atomic state duplication/destruction under stress, commit rollback/failure paths, private object cleanup on attach failure, resource contention, and kmemleak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_private_obj.c -->
