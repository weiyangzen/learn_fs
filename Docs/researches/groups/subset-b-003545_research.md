# Research Report: subset-b-003545

Grouped research for Armada, Aspeed GFX, and AST DRM driver files. Each source file has a source-path-preserving section wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_hw.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_hw.h

Purpose: central register map and bit-field contract for the Armada LCD/SPU display engine used by the Armada DRM CRTC, primary plane, overlay plane, interrupt, cursor, clock, SRAM, color-key, and output-pad code.

Important APIs/types are the anonymous enums defining MMIO offsets such as `LCD_SPU_DMA_CTRL0`, `LCD_CFG_GRA_START_ADDR0`, `LCD_SPU_IRQ_ISR`, and bit macros including `CFG_DMA_FMT`, `CFG_GRA_FMT`, `CFG_CKMODE`, `CFG_ALPHA`, `CFG_PDWN*`, and `SCLK_*`. There are no functions; the integration surface is compile-time symbolic access to memory-mapped hardware registers.

Control flow is indirect: update paths queue writes to these offsets, often from IRQ-driven register flush paths as noted by the header comment. State is persistent in display controller registers: frame addresses, pitches, FIFO power, format selection, color conversion, gamma/palette SRAM, interrupt enable/status, and dumb-panel polarity. Dependencies are Linux `BIT()` and the surrounding Armada DRM helpers that interpret these masks.

Risks include incorrect preserve masks corrupting unrelated register bits, Armada 510 versus Armada 16x clock/register differences, and register writes from IRQ context requiring queued/atomic-safe sequencing. Test signals are mode-set success, no FIFO underflow IRQs, correct pixel format/color-key behavior, vblank/frame interrupts, and stable output after suspend/resume or plane flips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_ioctlP.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_ioctlP.h

Purpose: private ioctl prototype header for Armada GEM userspace entry points. It keeps the driver ioctl table and GEM implementation files sharing one declaration style.

Important API is `ARMADA_IOCTL_PROTO(name)`, which declares `armada_gem_create_ioctl`, `armada_gem_mmap_ioctl`, and `armada_gem_pwrite_ioctl` with the DRM ioctl signature `(struct drm_device *, void *, struct drm_file *)`. The file has no state or control flow.

Dependencies are DRM core types and the implementations in the GEM code plus registration in the Armada DRM driver. Integration risk is mostly ABI wiring: mismatched prototypes or removed declarations break ioctl table compilation, while semantic bugs live in the implementation files. Test signals are successful module build, ioctl registration, GEM buffer creation/mmap/pwrite behavior, and userspace exercising the Armada DRM UAPI without `-ENOTTY` or argument decoding failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_ioctlP.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_overlay.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_overlay.c

Purpose: implements the Armada overlay/video plane, including YUV/RGB format support, color conversion, color-key properties, brightness/contrast/saturation properties, legacy `update_plane` tracing, and atomic hardware programming.

Important types/functions are `struct armada_overlay_state`, `armada_drm_overlay_plane_atomic_update`, `armada_drm_overlay_plane_atomic_disable`, `armada_overlay_plane_update`, state reset/duplicate handlers, property get/set handlers, `armada_overlay_create_properties`, and `armada_overlay_plane_create`. The plane reuses `armada_drm_plane_atomic_check` from `armada_plane.c` for geometry, pitches, addresses, and interlace decisions.

Control flow: an atomic check precomputes plane state, then update queues register writes for DMA start addresses, Y/U/V pitches, source/destination rectangles, format/modifier bits, interlace frame toggling, horizontal smoothing, CBSH, CSC, and color-key registers. Visibility transitions power YUV FIFOs up or down through `LCD_SPU_SRAM_PARA1`. Legacy update allocates an atomic state, sets plane fields, traces `armada_ovl_plane_update`, and commits nonblocking.

State persists in custom atomic plane state and in hardware registers. Dependencies include DRM atomic helpers, fourcc format metadata, Armada GEM framebuffer `dev_addr`, CRTC register queues, and tracepoints. Risks are packed-YUV odd-x UV swap compensation, unsupported interlaced overlay behavior marked FIXME, property creation only checking one allocation, and ADV color-key writes gated by variant support. Test signals are property round trips, color-key edge cases, YUV/RGB overlay scanout, scaling/smoothing, interlace rejection/behavior, underflow-free flips, and tracepoint coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_overlay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_plane.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_plane.c

Purpose: shared Armada plane helper plus primary plane implementation. It translates DRM atomic plane state into Armada source/destination register fields, DMA addresses, pitches, interlace bookkeeping, and primary graphics-layer register updates.

Important functions are `armada_drm_plane_calc`, `armada_drm_plane_atomic_check`, `armada_drm_primary_plane_atomic_update`, `armada_drm_primary_plane_atomic_disable`, `armada_plane_reset`, `armada_plane_duplicate_state`, and `armada_drm_primary_plane_init`. Supported primary formats include packed YUV and common RGB formats.

Control flow: atomic check validates scaling/clipping, enforces even destination y coordinates for interlaced modes, computes packed height/width fields, and calculates two field addresses for interlace. Primary update then queues changed geometry, start-address, pitch, format, modifier, palette, frame-toggle, enable, and smoothing writes. Disable clears `CFG_GRA_ENA` and powers down cursor/palette/slave/graphics FIFO SRAM blocks.

State lives in `struct armada_plane_state` and hardware registers queued through `armada_reg_queue_*`. Dependencies are DRM atomic helpers, Armada framebuffer/GEM helpers, CRTC register queue state, and `armada_hw.h` bit definitions. Risks include address truncation into 32-bit registers, interlace field-address assumptions, pitch width limits, and stale register state if mode-change checks miss a needed write. Test signals are primary scanout in every listed format, page flips with unchanged pitch, interlaced mode validation, scaled versus unscaled smoothing bit transitions, and no graphics FIFO underflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_plane.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_plane.h

Purpose: declares Armada plane-private atomic state and the helper functions shared by primary and overlay plane code.

Important type is `struct armada_plane_state`, which embeds `drm_plane_state` and caches `src_hw`, `dst_yx`, `dst_hw`, `addrs[2][3]`, `pitches[3]`, and `interlace`. Accessor macros expose those cached values to register-programming code. Declared functions include plane calculation/check/reset/duplicate helpers and primary plane initialization.

Control flow is structural: atomic check fills this state once, then primary and overlay update paths consume it without recalculating addresses. State is transient atomic commit state, not persistent storage, but it represents values later persisted into display registers. Dependencies are DRM plane state types and Armada source files that provide implementations.

Risks include declarations for cleanup/destroy helpers that are not implemented in this file set, tight coupling between cache layout and update macros, and invalid cached values if callers bypass the shared atomic check. Test signals are build/link coverage, successful state duplication/reset, and correct primary/overlay updates after atomic commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_trace.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_trace.c

Purpose: tracepoint definition translation unit for Armada DRM. It enables exactly one `CREATE_TRACE_POINTS` include of `armada_trace.h` when not being parsed by sparse/checker.

Important API is not a function but the tracepoint instantiation pattern required by Linux tracing. Control flow is compile-time: including this file creates the trace event descriptors for events declared in the header.

State is kernel tracing metadata and runtime trace buffers managed by ftrace/perf, not driver-owned persistent state. Dependencies are `armada_trace.h` and Linux trace infrastructure. Risks are duplicate tracepoint definition if `CREATE_TRACE_POINTS` is defined elsewhere, or missing tracepoints if this object is not linked. Test signals are successful build, tracefs events under the `armada` system, and visible records when IRQ or overlay update paths fire.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_trace.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_trace.h

Purpose: declares Armada DRM trace events for interrupt handling and overlay plane activity.

Important tracepoints are `armada_drm_irq`, recording a CRTC pointer and IRQ status word; `armada_ovl_plane_update`, recording plane/CRTC/framebuffer pointers and destination/source rectangles; and `armada_ovl_plane_work`, recording plane and CRTC pointers. `TRACE_SYSTEM` is `armada`, and `TRACE_INCLUDE_PATH` is set relative to the driver tree for generated trace code.

Control flow is tracing-only: event call sites populate entries with `TP_fast_assign`, and `TP_printk` formats pointer/status/geometry details. State persists only in enabled trace buffers. Dependencies are Linux tracepoint macros and forward-declared DRM objects.

Risks include pointer-only trace data limiting postmortem interpretation, path fragility if the file moves, and source coordinates printed after 16.16 fixed-point shifts. Test signals are tracepoint compilation, `trace_armada_*` symbols resolving, and useful trace output during overlay commits and IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/Kconfig

Purpose: Kconfig entry for the ASPEED BMC Graphics CRT DRM/KMS driver.

Important symbol is `DRM_ASPEED_GFX`, a tristate depending on DRM, OF, ASPEED architecture or compile testing, and MMU. It selects DRM client setup, KMS helpers, DMA GEM helpers, CMA/DMA_CMA when contiguous memory is available, and `MFD_SYSCON`.

Control flow is build-time only: enabling the symbol causes the Makefile to build `aspeed_gfx`. State/persistence is kernel configuration state and module selection. Dependencies mirror runtime needs: device tree matching, syscon regmap access, DMA-capable framebuffer memory, and simple KMS helpers.

Risks include missing reserved memory/CMA support on platforms that need contiguous scanout buffers, architecture coverage limited by DT/OF, and help text mentioning AST2500 even though the driver table also supports AST2400 and AST2600 compatibles. Test signals are `olddefconfig` selection, compile-test builds, module load on ASPEED DT systems, and successful dependency resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/Makefile

Purpose: build composition for the ASPEED GFX DRM driver.

Important entries are `aspeed_gfx-y := aspeed_gfx_drv.o aspeed_gfx_crtc.o aspeed_gfx_out.o` and `obj-$(CONFIG_DRM_ASPEED_GFX) += aspeed_gfx.o`. There is no runtime control flow or state.

Dependencies are the Kconfig symbol and the three object files that provide platform probe/sysfs/IRQ, simple display pipe/CRTC programming, and connector output. Integration risk is low but direct: adding a new source file or splitting functionality requires updating this list, and missing objects cause unresolved symbols such as `aspeed_gfx_create_pipe` or `aspeed_gfx_create_output`. Test signals are module build/link success and the resulting `aspeed_gfx` module containing all three implementation units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx.h

Purpose: shared private header for the ASPEED GFX simple DRM driver, defining device state, register offsets, and control bit macros used by probe, CRTC, and connector code.

Important type is `struct aspeed_gfx`, embedding `drm_device`, MMIO base, clock/reset handles, SCU regmap, per-SoC register offsets/defaults, a `drm_simple_display_pipe`, and one connector. Important macros define CRT register offsets (`CRT_CTRL1`, `CRT_HORIZ0`, `CRT_ADDR`, `CRT_THROD`, etc.) and fields for enable, DAC, color format, sync polarity, vblank interrupt, timings, offset, terminal count, and thresholds.

Control flow is indirect: CRTC code writes these fields during pipe enable/update/vblank setup, while driver code stores SoC-specific offsets and thresholds. State persists in hardware registers and the `aspeed_gfx` device struct. Dependencies include DRM device and simple KMS headers, clock/reset/regmap users, and SoC manuals.

Risks include register-field names with minor spelling issues, hardcoded 40 MHz/simple-mode assumptions in consumers, and fragile bitfield macros without range checking. Test signals are correct MMIO writes for RGB565/XRGB8888, vblank interrupt status handling, DAC mux behavior, and mode timing register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx_crtc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx_crtc.c

Purpose: implements the ASPEED GFX simple display pipe: mode timing programming, framebuffer base updates, controller enable/disable, and vblank interrupt control.

Important functions are `aspeed_gfx_set_pixel_fmt`, `aspeed_gfx_crtc_mode_set_nofb`, `aspeed_gfx_pipe_enable`, `aspeed_gfx_pipe_disable`, `aspeed_gfx_pipe_update`, `aspeed_gfx_enable_vblank`, `aspeed_gfx_disable_vblank`, and `aspeed_gfx_create_pipe`. Supported formats are `DRM_FORMAT_XRGB8888` and `DRM_FORMAT_RGB565`.

Control flow: pipe enable programs pixel format, sync polarities, interlace bit, horizontal/vertical totals/display/sync ranges, line offset/terminal count, FIFO thresholds, then switches the SCU DAC source and CRT/DAC enable bits. Pipe update handles pending vblank events under `event_lock`, obtains the DMA GEM address, and writes `CRT_ADDR`. Vblank callbacks set/clear interrupt enable/status bits in `CRT_CTRL1`.

State persists in CRT MMIO registers, SCU DAC mux bits, vblank event state, and the active framebuffer DMA address. Dependencies are DRM simple KMS, GEM DMA helpers, regmap, clock/reset initialized by probe, and display modes constrained elsewhere. Risks include returning early from `mode_set_nofb` on unsupported format without failing the atomic commit, fixed pixel clock limitations, terminal-count math tied to `scan_line_max`, and missing GEM object handling. Test signals are visible scanout after enable, page flips updating `CRT_ADDR`, vblank event delivery, format switching, and clean disable of CRT/DAC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx_drv.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx_drv.c

Purpose: platform driver for the ASPEED BMC GFX display controller. It owns compatible matching, MMIO/resource setup, reserved memory and DMA setup, reset/clock enable, IRQ registration, DRM device registration, sysfs controls, and shutdown/remove.

Important pieces are `struct aspeed_gfx_config`, AST2400/2500/2600 config tables, `aspeed_gfx_match`, `aspeed_gfx_setup_mode_config`, `aspeed_gfx_irq_handler`, `aspeed_gfx_load`, `aspeed_gfx_unload`, sysfs attributes `dac_mux` and `vga_pw`, `aspeed_gfx_probe`, `aspeed_gfx_remove`, and `aspeed_gfx_shutdown`. The DRM driver uses DMA GEM/fbdev helper ops.

Control flow: probe allocates a managed DRM device, maps MMIO, selects SoC config, finds SCU regmap by phandle or fallback compatible, initializes reserved memory and 32-bit DMA mask, deasserts reset, enables clock, clears control registers, initializes mode config/vblank/output/pipe/IRQ, creates sysfs, registers DRM, and starts generic clients. IRQ handler checks vertical interrupt status, calls `drm_crtc_handle_vblank`, and writes the configured clear register.

State persists in hardware registers, sysfs-visible SCU fields, clocks/resets, reserved memory assignment, DRM mode config, and platform drvdata. Dependencies are OF, syscon/regmap, reset/clk, reserved-memory, DRM DMA helpers, and the pipe/output files. Risks include no error unwinding for enabled clock/reset on mid-load failures, `dac_mux_store` returning `0` on regmap update failure, fallback SCU compatible being AST2500-specific, and a hard max mode of 800x600. Test signals are probe/remove cycles, sysfs read/write behavior, vblank IRQs, reserved memory/DMA mask success, and shutdown disabling scanout via atomic helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx_out.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx_out.c

Purpose: creates the single ASPEED GFX connector and supplies fallback modes without EDID.

Important functions are `aspeed_gfx_get_modes` and `aspeed_gfx_create_output`, plus connector helper/func tables. The connector type is `DRM_MODE_CONNECTOR_Unknown`; it uses atomic connector state helpers and `drm_helper_probe_single_connector_modes`.

Control flow: output creation initializes connector fields, attaches helpers, and calls `drm_connector_init`. Mode probing always adds no-EDID modes up to 800x600. State is the embedded connector in `struct aspeed_gfx`; there is no hotplug or EDID persistence. Dependencies are DRM connector, EDID/no-EDID helpers, and the simple display pipe that attaches to this connector.

Risks include no physical detect, no EDID, no preferred mode assignment, and a connector initialized with `dpms = OFF` but no explicit detect path. Test signals are connector creation during probe, userspace seeing 800x600 modes, successful atomic state reset/duplicate/destroy, and pipe initialization attaching this connector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx_out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/Kconfig

Purpose: Kconfig entry for the ASPEED AST PCI server graphics DRM/KMS driver.

Important symbol is `DRM_AST`, a tristate depending on DRM and PCI. It selects DRM client setup, shmem GEM helpers, KMS helpers, I2C, and I2C bit-banging support. Help text warns that the driver is experimental and intended for server chipsets with modesetting support.

Control flow is build-time only. State is kernel configuration and module enablement. Runtime dependencies implied by the selection include PCI BAR access, DRM shmem framebuffer allocation, I2C/DDC for VGA EDID, and KMS helper infrastructure.

Risks are stale help wording relative to the modern atomic driver and broad PCI matching that depends on runtime chip detection. Test signals are config dependency resolution, compile-test coverage where possible, `ast` module build, and successful loading on supported ASPEED PCI display devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/Makefile

Purpose: object list for the AST DRM driver.

Important build composition includes generation-specific files `ast_2000.o` through `ast_2600.o`, cursor, DDC, DP501, ASTDP, core driver, memory manager, mode setting, POST helpers, SIL164, VBIOS, and VGA output. `obj-$(CONFIG_DRM_AST) := ast.o` links these into one module/built-in object.

Control flow and state are build-time. Dependencies are all listed source files and the Kconfig symbol. Integration risks include unresolved symbols if an output path or generation constructor is omitted and overlinking generation code that must remain guarded by runtime chip detection. Test signals are full module link, `modpost` success, and probe paths resolving all selected transmitter/mode helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2000.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2000.c

Purpose: first-generation AST device support: default extended VGA register setup, AST2000 POST/DRAM initialization, DCLK table, transmitter detection, generation quirks, and DRM device construction.

Important functions are `ast_2000_set_def_ext_reg`, `ast_2000_post`, `ast_2000_detect_tx_chip`, and `ast_2000_device_create`. Data includes `ast2000_dram_table_data`, `ast_2000_dclk_table`, and low/high CRTC memory request thresholds.

Control flow: POST resets scratch registers, applies default extended registers, initializes DRAM through the P2A bridge if available and VGA-only mode needs it, waits for ready bit `VGACRD0[6]`, or enables SIL164 DVO for non-P2A configurations. Device creation allocates `ast_device`, initializes core fields, assigns the DCLK table, detects SIL164 only when existing DVO state is meaningful, optionally posts, initializes VRAM mapping, then mode config.

State persists in indexed VGA registers, SCU/MMC registers, `ast->tx_chip`, DCLK table pointer, VRAM metadata, and mode config. Dependencies are `ast_post.h`, `ast_drv.h`, PCI, delays, and mode/mm helpers. Risks include busy-wait loops without timeout, hardcoded DRAM magic tables, false transmitter detection if power-on state is misread, and POST paths dependent on P2A availability. Test signals are AST2000 probe, successful VRAM size/mapping, analog/SIL164 output selection, mode setting at DCLK table rates, and resume repost.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2100.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2100.c

Purpose: second-generation AST1100/2100/2150/2200 POST and device support, adding DRAM layout detection and calibration plus widescreen capability detection shared by later generations.

Important functions include `ast_2100_get_dram_layout_p2a`, `ast_2100_post`, `__ast_2100_detect_wsxga_p`, `__ast_2100_detect_wuxga`, and `ast_2100_device_create`. Internal calibration helpers include `mmctestburst2_ast2150`, `cbrtest_ast2150`, `cbrscan_ast2150`, and `cbrdlli_ast2150`. Data includes AST1100/2100 DRAM register tables and uses `ast_2000_dclk_table`.

Control flow: P2A POST selects a DRAM table based on chip, patches DRAM type entries according to detected layout, writes MMC registers with required delays, calibrates DLL CBR for 266 MHz parts, clears reset/control bits, then waits for VRAM ready. Widescreen detection reads BMC/IKVM scratch bits and WUXGA support bits.

State persists in MMC/SCU registers, VGA indexed scratch/status registers, display capability booleans, `tx_chip`, and mode config. Dependencies are first-generation defaults/TX detection, POST helpers, P2A access, and later VBIOS mode filtering. Risks include unbounded ready waits, calibration restart loops, scratch-bit interpretation differences across BMC firmware, and display capability under/over-reporting. Test signals are AST1100/2100/2150 probe, DRAM calibration stability, widescreen/full-HD mode availability, and correct fallback when P2A is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2200.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2200.c

Purpose: third-generation AST2200/2150 device constructor and widescreen capability policy.

Important functions are `ast_2200_detect_widescreen` and `ast_2200_device_create`. It reuses `ast_2000_dclk_table`, `ast_2000_detect_tx_chip`, optional `ast_post_gpu`, `ast_mm_init`, and `ast_mode_config_init`. Quirks set CRTC memory request thresholds to 47/63.

Control flow is a thin generation wrapper: allocate managed `ast_device`, initialize common fields/quirks, detect transmitter, optionally POST, map VRAM, set widescreen/full-HD/WUXGA booleans using shared Gen2 helpers, and initialize mode config.

State persists in the common `ast_device`, mode capability flags, TX chip, VRAM mapping, and mode config. Dependencies are Gen2 widescreen helpers and common AST core. Risks are inherited from shared POST/TX paths; this file’s unique risk is mode capability policy for AST2200 specifically setting full-HD only on that chip. Test signals are AST2200 probe, availability of WSXGA+/FullHD/WUXGA modes as expected, and successful analog/SIL164 output initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2300.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2300.c

Purpose: fourth-generation AST2300/1300 support, including extended register defaults, DDR2/DDR3 trap decoding, memory-controller training, third-party transmitter detection/backup, widescreen policy, and device construction.

Important functions are `ast_2300_set_def_ext_reg`, `ast_2300_post`, `ast_2300_detect_tx_chip`, and `ast_2300_device_create`. The long internal POST path includes `struct ast2300_dram_param`, CBR/DLL tests (`mmc_test2`, `cbr_scan*`, `finetuneDQSI`, `finetuneDQI_L`, `cbr_dll2`), DDR info builders, and `ddr2_init`/`ddr3_init`.

Control flow: P2A POST unlocks SCU/MMC, slows CPU/AHB in VGA-only mode, derives DRAM type/chip/VRAM size from trap bits, selects timing parameters, initializes DDR2 or DDR3, performs calibration/retry loops, marks memory ready, and initializes third-party TX. TX detection reads scratch TX type bits, backs up DP501 firmware when possible, maps unsupported TX values to warnings, and records `AST_TX_*`.

State persists in SCU/MMC registers, calibration results, VGA indexed registers, DP501 firmware backup buffer/address, TX chip, VRAM mapping, and display capability flags. Dependencies are POST memory tests, PCI BAR reserved buffer mapping, `drmm_kzalloc`, DP501 helpers, VBIOS mode tables, and common mode config. Risks are numerous hardcoded register sequences, several busy-wait loops, retry loops that can be long on bad DRAM, unsupported TX chips treated as warnings rather than probe failures, and reserved-buffer mapping when VRAM is smaller than BAR0. Test signals are Gen4 probe/POST, DDR2 and DDR3 boards, DP501 firmware backup, analog/SIL164/DP501 output selection, widescreen mode exposure, and resume repost stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2400.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2400.c

Purpose: fifth-generation AST2400/1400 device constructor and widescreen policy.

Important functions are `ast_2400_detect_widescreen` and `ast_2400_device_create`. It uses Gen4 TX detection, `ast_2000_dclk_table`, optional `ast_post_gpu`, VRAM init, reserved DP501 buffer mapping, and mode config. Quirks set higher CRTC memory thresholds of 96/120.

Control flow: allocate/init `ast_device`, detect TX chip from Gen4+ scratch fields, optionally POST, initialize VRAM, map reserved BAR0 space for DP501 firmware/status if VRAM consumes less than BAR0, set WSXGA+/FullHD/WUXGA support, then initialize mode config.

State includes TX chip, DP501 reserved buffer pointer, VRAM metadata, display capability flags, and mode config. Dependencies are PCI BAR sizing, Gen4 TX detection, DP501 output path, and VBIOS mode filtering. Risks include non-fatal reserved buffer mapping failure reducing DP501 functionality, AST1400 special-cased full-HD support, and inherited TX detection ambiguity. Test signals are AST2400/1400 probe, DP501 status reads through reserved buffer, 1920x1080 mode availability where expected, and stable scanout at 96/120 thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2400.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2500.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2500.c

Purpose: sixth-generation AST2500/2510 support, including AHB bus-lock reset workaround, DDR3/DDR4 initialization and training, AST2500 DCLK table, widescreen policy, and device construction.

Important functions are `ast_2500_patch_ahb`, `ast_2500_post`, `ast_2500_device_create`, and the internal DRAM sequence: `set_mpll_2500`, `reset_mmc_2500`, `ddr_init_common_2500`, `ddr_phy_init_2500`, `ddr3_init_2500`, `ddr4_init_2500`, `check_dram_size_2500`, `enable_cache_2500`, `ddr_test_2500`, and `ast_dram_init_2500`. Data includes DDR3/DDR4 1600 timing tables and `ast_2500_dclk_table`.

Control flow: POST clears fast-reset/bus-lock conditions, disables watchdogs, applies USB/eSPI strap workarounds, slows CPU/AHB in VGA-only mode, retries DRAM initialization up to five times, marks VRAM ready, and waits for ready status. DDR4 path trains PHY and DDR Vref windows; DDR3 path programs fixed PHY/controller values. Device creation then maps VRAM/reserved DP501 buffer, sets display capabilities, and initializes mode config.

State persists in SCU/WDT/MMC/DDR PHY registers, DCLK table pointer, TX chip, VRAM/reserved-buffer mappings, and mode flags. Dependencies are P2A access, POST helpers, Gen4 TX detection, delays, PCI BAR information, and common mode code. Risks include long busy waits, fragile magic register sequences, DRAM init failure only logged before ready wait continues, watchdog/USB/eSPI side effects, and mode quirks for hsync precatch. Test signals are AST2500/2510 cold POST, DDR3 and DDR4 boards, fast-reset recovery, DP501/SIL164/analog output, FullHD modes, and suspend/resume repost.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2600.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2600.c

Purpose: seventh-generation AST2600 device support, mainly selecting ASTDP launch behavior, AST2500 DCLK table, stronger CRTC quirks, widescreen policy, and common initialization.

Important functions are `ast_2600_post` and `ast_2600_device_create`. Quirks set memory thresholds 160/224 and enable both hsync precatch and hsync add4 workarounds.

Control flow: POST applies Gen4+ extended defaults and launches the ASPEED DP MCU when `tx_chip == AST_TX_ASTDP`. Device creation allocates/init common state, assigns `ast_2500_dclk_table`, detects TX, forces `ast_post_gpu` for ASTDP even if VGA did not require POST, initializes VRAM, sets WSXGA+/FullHD and WUXGA support, then creates mode config.

State persists in indexed VGA registers, ASTDP firmware/MCU state, TX chip, VRAM mapping, display support flags, and mode config. Dependencies are Gen4 TX detection, `ast_dp_launch`, common POST dispatch, and ASTDP output code. Risks include ASTDP devices being unusable if MCU launch times out, inherited P2A/default config limitations, and hsync workaround specificity for 1080-line modes. Test signals are AST2600 probe, ASTDP link/EDID behavior, FullHD/WUXGA mode exposure, and resume repost with DP reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_2600.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_cursor.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_cursor.c

Purpose: hardware cursor plane for AST devices, using a reserved VRAM block with ARGB4444 cursor pixels plus a signature/checksum area consumed by hardware.

Important functions are `ast_cursor_vram_offset`, `ast_cursor_calculate_checksum`, `ast_set_cursor_image`, `ast_set_cursor_base`, `ast_set_cursor_location`, `ast_set_cursor_enabled`, `ast_cursor_plane_get_argb4444`, `ast_cursor_plane_helper_atomic_check/update/disable`, and `ast_cursor_plane_init`. Supported cursor formats are `ARGB4444` and `ARGB8888` converted to ARGB4444.

Control flow: init reserves the last aligned cursor-sized block in VRAM. Atomic check rejects scaled or oversized cursors. Update merges damage, converts/copies the framebuffer into ARGB4444 memory, writes cursor pixels and signature, programs base address, writes signed/negative-position offsets, and toggles the hardware enable bit to make changes visible. Disable clears the enable bit.

State persists in cursor VRAM, signature fields, indexed cursor registers, and the software conversion buffer. Dependencies are shadow-plane helpers, GEM CPU access, DRM format conversion, `ast_plane_vaddr`, and CRTC mode validity. Risks include fallback white square on CPU-access failure, endian-specific copy handling, checksum/signature correctness, cursor memory reducing primary framebuffer space, and hardware requiring a valid active primary/CRTC. Test signals are cursor size rejection, ARGB8888 conversion correctness, negative-position clipping, disable during full modesets, and no corruption of primary framebuffer VRAM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_cursor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_ddc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_ddc.c

Purpose: bit-banged I2C/DDC adapter for AST analog output EDID reads.

Important type is `struct ast_ddc`, containing the `ast_device`, `i2c_algo_bit_data`, and `i2c_adapter`. Important functions are SDA/SCL setters/getters, pre/post transfer lock hooks, `ast_ddc_release`, and `ast_ddc_create`.

Control flow: adapter creation allocates DRM-managed state, fills bit-banging callbacks, registers an I2C adapter, and attaches a managed cleanup action. Transfers lock `ast->modeset_lock` so DDC indexed-register access cannot race modeset register programming. SDA/SCL setters write inverted bits into VGACR B7 and poll until latched; getters sample repeatedly until five stable reads or a large retry limit.

State persists in the I2C adapter registration and transiently in VGACR B7 pin-control bits. Dependencies are `i2c-algo-bit`, DRM managed allocation/actions, AST indexed register helpers, and the mode lock. Risks include long polling loops on stuck pins, inverted signal semantics, possible EDID read latency due to 20 us bit delay and 2200 us timeout, and shared register contention if callers bypass the lock. Test signals are adapter registration, EDID read success on VGA, correct cleanup on device removal, and no modeset/DDC races under hotplug polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_ddc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_ddc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_ddc.h

Purpose: small public-private header declaring AST DDC adapter creation.

Important API is `struct i2c_adapter *ast_ddc_create(struct ast_device *ast)`, with forward declarations for `ast_device` and `i2c_adapter`. There is no runtime control flow or state in the header.

Dependencies are the implementation in `ast_ddc.c` and output code that needs an I2C bus for EDID. Integration risks are minimal: prototype drift would break builds, while actual DDC behavior depends on the implementation. Test signals are compile/link success and VGA output paths obtaining an adapter for connector EDID probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_ddc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_dp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_dp.c

Purpose: ASPEED DisplayPort output support for AST Gen7+ devices, covering DP MCU launch, EDID reads through indexed registers, link training, PHY sleep, mode-index programming, connector state, and encoder/connector initialization.

Important functions are `ast_dp_launch`, `ast_astdp_read_edid_block`, `ast_astdp_is_connected`, `ast_dp_set_phy_sleep`, `ast_dp_link_training`, `ast_dp_set_enable`, encoder helper callbacks, connector helper callbacks, custom connector state reset/duplicate/destroy, and `ast_astdp_output_init`. `struct ast_astdp_connector_state` stores the hardware mode index.

Control flow: launch waits for MCU firmware executing and marks EDID read done. Detection temporarily wakes PHY, checks HPD plus link-success bits, updates cached physical status/epoch, but returns logical connected for BMC compatibility. Mode check maps resolutions to ASTDP mode indexes. Mode set writes misc and video-format index registers. Enable wakes PHY, trains link, waits vrefresh, and enables DP video; disable turns video off and sleeps PHY. EDID reading serializes under `modeset_lock`, reads 4-byte chunks through mirrored registers, and suppresses extension blocks.

State persists in DP PHY/video indexed registers, cached physical connector status, connector atomic mode index, and EDID-derived connector properties. Dependencies are DRM atomic/EDID helpers, VBIOS mode refresh indexes, AST indexed register helpers, and the global modeset lock. Risks include no EDID extensions, long retry sleeps on EDID, mode-index table ignoring refresh/flags FIXME, always-connected logical status, and link training failure only logged. Test signals are AST2600 DP hotplug, EDID/no-EDID mode lists, 1024x768 fallback, supported mode validation, DP enable/disable, and suspend/resume relaunch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_dp501.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_dp501.c

Purpose: support for the DP501 DisplayPort transmitter used on some AST Gen4/Gen5 boards, including firmware loading/backup/launch, command handshaking, connection detection, EDID reads, DVO/analog setup, and DRM output creation.

Important functions are `ast_load_dp501_microcode`, `ast_backup_fw`, `ast_launch_m68k`, `ast_init_3rdtx`, `ast_dp501_is_connected`, `ast_dp512_read_edid_block`, `ast_init_dvo`, `ast_init_analog`, DP501 encoder enable/disable callbacks, connector detect/get_modes callbacks, and `ast_dp501_output_init`. The file declares firmware `ast_dp501_fw.bin`.

Control flow: Gen4/5 TX initialization either programs DVO/SIL164, launches M68K DP501 firmware from a backed-up or requested firmware image into reserved VRAM, or selects analog output. Command helpers exchange ACK/NACK bits through indexed registers to toggle DP501 video output. Detection validates firmware version and PnP monitor bits either through P2A boot memory or the reserved BAR0 buffer. EDID reads 4-byte chunks from DP501 memory. Connector detection caches physical status but returns logical connected for BMC fallback modes.

State persists in `ast->dp501_fw`, firmware backup buffer, reserved firmware status mapping, SCU DVO/DAC mux registers, command mailbox bits, and cached connector physical status. Dependencies are firmware loader, P2A bridge, PCI reserved buffer mapping from generation constructors, DRM EDID helpers, and output mode config. Risks include unaligned firmware word reads, external firmware availability, long ACK/NACK waits, fallback to analog on ambiguous TX scratch values, always-connected logical status, and no bounds validation beyond EDID block count. Test signals are DP501 firmware launch, EDID read from P2A and non-P2A paths, video output enable/disable, fallback no-EDID modes, and analog/DVO mux correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_dp501.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_drv.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_drv.c

Purpose: AST PCI DRM driver core. It defines module parameters, DRM driver ops, PCI matching/probe/remove/shutdown, chip/config detection, MMIO/VGA enablement, and power-management suspend/resume paths.

Important functions are `ast_device_init`, `__ast_device_set_tx_chip`, `ast_is_vga_enabled`, `ast_enable_vga`, `ast_enable_mmio`, `ast_open_key`, `ast_detect_chip`, `ast_pci_probe`, `ast_pci_remove`, `ast_pci_shutdown`, `ast_drm_freeze`, `ast_drm_thaw`, `ast_drm_resume`, and PM callbacks. The PCI table matches ASPEED display-class AST2000/AST2100 IDs, while revision/SCU bits identify actual generations.

Control flow: probe removes conflicting framebuffer apertures, enables PCI, maps BAR1 and I/O registers, enables VGA if needed, unlocks extended registers, enables MMIO, detects config mode from DT/P2A/defaults and chip generation from PCI revision/SCU revision, dispatches to the generation-specific constructor, registers DRM, and starts clients. Suspend freezes mode config and powers PCI down; thaw/resume re-enables VGA/MMIO, reposts GPU, and resumes modes.

State persists in PCI drvdata, `ast_device` fields, VGA/MMIO decode bits, module `modeset` parameter, chip/config decisions, and PM-saved PCI state. Dependencies are PCI, aperture helpers, DRM shmem/fbdev helpers, generation constructors, DT SCU revision properties, and P2A bridge access. Risks include broad device matching relying on runtime detection, P2A availability assumptions, repeated `ast_enable_mmio` managed action registration during thaw, BAR length validation edge cases, and POST on resume failing display recovery. Test signals are probe on every generation, module parameter disabling via DRM helper macro, conflicting framebuffer removal, suspend/resume, shutdown, and correct generation constructor dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_drv.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_drv.h

Purpose: main private header for the AST DRM driver. It defines chip/config/TX enums, device state, plane/cursor/connector/CRTC private structs, register access helpers, display mode constants, DP501/ASTDP constants, and cross-file prototypes.

Important types are `enum ast_chip`, `enum ast_tx_chip`, `enum ast_config_mode`, `enum ast_dram_layout`, `struct ast_device_quirks`, `struct ast_device`, `struct ast_plane`, `struct ast_cursor_plane`, `struct ast_connector`, and `struct ast_crtc_state`. Important helpers include generation tests, raw/indexed MMIO accessors, and `ast_read32`/`ast_write32`.

Control flow is via inline accessors and declarations consumed by all AST files. State described here includes VRAM mappings, IO register mappings, mode lock, primary/cursor planes, CRTC, per-output encoder/connector union, widescreen capability flags, TX chip, DCLK table, and DP501 firmware buffers.

Dependencies are DRM core types, Linux I/O primitives, `ast_reg.h`, and all implementation files. Risks include many raw register helpers with no locking by default, union output storage assuming one active TX path, generation enum encoding coupled to `__AST_CHIP_GEN`, and broad shared state making ordering bugs possible during probe/PM. Test signals are compile coverage, lockdep around `modeset_lock`, correct chip generation classification, and all output paths resolving their prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_mm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_mm.c

Purpose: AST VRAM sizing and write-combined BAR0 mapping.

Important functions are `ast_get_vram_size` and `ast_mm_init`. VRAM size is decoded from indexed register `0xaa` and reduced by reserved-memory bits in register `0x99`.

Control flow: `ast_mm_init` gets BAR0 base/length, reserves/adds write-combining memtype best-effort, computes usable VRAM, maps that range with `devm_ioremap_wc`, and records `ast->vram`, `vram_base`, and `vram_size`. It does not create a full GEM memory manager; scanout uses shmem shadow copies into this mapped VRAM.

State persists in `ast_device` VRAM fields and architecture WC reservations. Dependencies are PCI BAR resources, DRM managed lifetime, AST indexed register access, and cursor/primary plane sizing. Risks include no explicit check that decoded VRAM size is <= BAR0 length, unknown default initialization if register values fall outside documented cases, reserved DP501 memory shrinking primary framebuffer space, and performance fallback if WC reservation fails. Test signals are successful probe mapping, correct framebuffer max mode validation, cursor offset calculation, and no BAR overrun on boards with reserved memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_mode.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_mode.c

Purpose: AST atomic KMS mode-setting core. It initializes primary/cursor planes, CRTC, mode config, gamma/palette handling, VBIOS mode table programming, shadow framebuffer damage upload, panic scanout buffer access, and output selection.

Important functions include `ast_mode_config_init`, `ast_primary_plane_init`, `ast_crtc_init`, `ast_plane_init`, `ast_plane_vaddr`, `ast_primary_plane_helper_atomic_check/update/enable/disable`, `ast_crtc_helper_atomic_check/mode_set_nofb/flush/enable/disable`, register setters for VBIOS color/mode/std/CRTC/DCLK/sync/offset/start address, and `ast_mode_config_mode_valid`.

Control flow: mode config sets max dimensions based on FullHD support, initializes planes, CRTC, and one output based on `ast->tx_chip`. Primary plane check records framebuffer format into custom CRTC state. CRTC atomic check validates gamma LUT size, selects standard/VBIOS tables, and rewrites adjusted timings from VBIOS mode entries. `mode_set_nofb` waits vrefresh, writes VGA/VBIOS timing registers, DCLK, thresholds, and sync polarity. Plane update copies shmem damage into write-combined VRAM and updates color/offset only when needed; enable sets scanout start address. Commit tail serializes register access with `modeset_lock`.

State persists in `ast_crtc_state` format/table pointers, VRAM shadow scanout, VGA indexed registers, gamma LUT/palette, and DRM mode config. Dependencies are DRM atomic/shadow-plane helpers, VBIOS/timing tables, generation quirks, cursor plane, output initializers, and memory manager. Risks include reliance on VBIOS tables for all valid modes, fixed 16-bit pitch limit, skipped offset/address writes to avoid BMC stalls, no vblank interrupt support, locking all commit tail against EDID/register readers, and mode availability tied to generation flags. Test signals are modeset/pageflip/damage tests, C8/RGB565/XRGB8888 gamma behavior, panic scanout buffer retrieval, FullHD max dimension policy, hsync workaround modes, and suspend/resume mode restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_mode.c -->
