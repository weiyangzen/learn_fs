# subset-b-003763 Research

Grouped research for VC4 shader/VEC display validation, VeriSilicon DC DRM, VGEM, and VirtIO GPU DRM files. Each source section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_validate_shaders.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_validate_shaders.c

## Purpose
`vc4_validate_shaders.c` validates VC4 QPU shader BO contents before they can execute on hardware without an IOMMU. It rejects unsafe register writes, invalid branches, unsupported signals, unbounded uniform reads, direct TMU reads without clamp proof, and threaded shaders that touch the upper register halves; it also records texture sample relocation metadata and uniform stream layout for command-list validation.

## Important APIs, Types, and Functions
The main exported API is `vc4_validate_shader(struct drm_gem_dma_object *shader_obj)`, returning `struct vc4_validated_shader_info` or `NULL`. `struct vc4_shader_validation_state` tracks instruction pointer, TMU setup slots, live clamp/immediate state, branch targets, uniform-address update requirements, loop reset needs, and threaded register usage. Important helpers include `waddr_to_live_reg_index()`, `raddr_add_a_to_live_reg_index()`, `check_tmu_write()`, `validate_uniform_address_write()`, `check_reg_write()`, `track_live_clamps()`, `check_instruction_reads()`, `vc4_validate_branches()`, and `vc4_handle_branch_target()`.

## Control Flow
Validation initializes live register state, allocates a branch-target bitmap, allocates the validated-info result, and first scans all instructions for legal branch form and in-range branch targets. It then walks instructions linearly until the program-end delay slots complete. Each instruction is classified by QPU signal: normal math-like signals validate writes and uniform reads, `LOAD_IMM` validates writes and immediate tracking, and `BRANCH` validates no side-effect writes and delay-slot placement. Branch target entries reset tracked live state and force a uniform address reset before later uniform reads. Texture setup counts TMU parameters and records a sample when `TMU*_S` submits the lookup.

## State and Persistence Behavior
All validation state is transient except the returned `vc4_validated_shader_info`, which persists with the immutable shader BO and records `uniforms_size`, `uniforms_src_size`, texture sample offsets, direct-sample markers, uniform-address reset offsets, and threaded status. The code assumes shader BOs are immutable after creation, so successful validation is a one-time capability check. Hardware state is not touched; only kernel memory is allocated and freed.

## Dependencies and Integration Points
The file depends on DRM logging/allocation helpers, VC4 driver types, `vc4_qpu_defines.h` bitfield macros, GEM DMA BO mapping, and later VC4 validation/relocation code that consumes texture sample and uniform offset metadata. It is an authorization boundary between userspace shader blobs and QPU execution.

## Risks
The validator is security-critical because missed unsafe QPU behavior can permit arbitrary memory access. Direct TMU read safety depends on recognizing a specific `MAX(x,0)` then `MIN(..., uniform)` clamp pattern and invalidating that proof at all control-flow joins. Uniform address reset validation is intentionally conservative and may reject shaders that are semantically safe but not in the supported form. Branch delay-slot, program-end, and thread-switch timing are subtle. Allocation failure paths must free partially allocated metadata.

## Test Signals
Useful tests include shader fuzzing, branch target and delay-slot edge cases, direct TMU access with and without clamp proof, uniform reads across branch targets and backward loops, threaded shaders using lower versus upper registers, unsupported write addresses such as VPM DMA trigger, texture setup overflow, program-end termination checks, and memory-leak checks on validation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_validate_shaders.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_vec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_vec.c

## Purpose
`vc4_vec.c` implements the VC4 VEC SDTV encoder component for composite PAL/NTSC/SECAM output. It exposes a DRM encoder and connector, creates TV mode properties, validates analog timing constraints, programs VEC/WSE/DAC registers during atomic enable, and integrates the platform device into the VC4 componentized DRM driver.

## Important APIs, Types, and Functions
Key types are `struct vc4_vec_variant`, `struct vc4_vec`, `enum vc4_vec_tv_mode_id`, and `struct vc4_vec_tv_mode`. Important functions include `vc4_vec_tv_mode_lookup()`, connector property handlers, `vc4_vec_connector_init()`, `vc4_vec_encoder_enable()`, `vc4_vec_encoder_disable()`, `vc4_vec_encoder_atomic_check()`, `vc4_vec_late_register()`, `vc4_vec_bind()`, and platform probe/remove. Register macros cover VEC config, color subcarrier frequency, DAC power, status, and debugfs register exposure.

## Control Flow
Platform probe registers a component. Bind creates DRM TV properties, allocates the VEC object, maps registers, resolves the SoC variant and clock, enables runtime PM, initializes the TVDAC encoder, then initializes the composite connector. Atomic check maps connector TV mode plus adjusted `htotal` to a VEC mode table entry and rejects unsupported horizontal/vertical timing shapes. Atomic enable enters the DRM device, resumes power, sets the VEC clock to 108 MHz, enables it, resets hardware blocks, writes mode-common and mode-specific registers, programs custom subcarrier frequency when needed, powers the DAC, and enables the VEC. Disable clears enable bits, powers down DAC/LDO/bias blocks, disables the clock, and releases runtime PM.

## State and Persistence Behavior
Persistent state is the `struct vc4_vec` instance, register mapping, clock pointer, TV mode property pointer, SoC variant DAC configuration, connector state, and debugfs regset. Hardware state persists in VEC registers while the encoder is active and is reset/reprogrammed on each enable. Runtime PM and clock state are tied to encoder active state.

## Dependencies and Integration Points
The file uses DRM atomic helpers, TV mode properties, connector helper TV mode generation, component framework, platform OF matching, VC4 register/debugfs helpers, clocks, runtime PM, and KUnit register-access guards. It integrates with VC4 encoder routing and with downstream userspace modesetting through standard DRM connector properties plus a legacy `mode` enum property.

## Risks
Mode selection depends on `htotal` to distinguish PAL-60/monochrome variants sharing DRM TV mode IDs. Register programming is hardware-specific and has few readback checks. `vc4_vec_connector_detect()` returns unknown, so userspace relies on virtual/probed modes. Clock rate sharing with HDMI requires enable-time rate setting. Timing validation is conservative and must track analog standard requirements. Error paths during enable must balance runtime PM and clock state.

## Test Signals
Tests should cover connector property set/get mapping, all supported TV modes, invalid timing rejection, enable/disable PM and clock balancing, debugfs register exposure, device-tree matches for BCM2835 and BCM2711 DAC settings, KUnit paths that must not touch registers, and atomic modesets switching between 50 Hz and 60 Hz standards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_vec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/Kconfig

## Purpose
`verisilicon/Kconfig` declares the `DRM_VERISILICON_DC` build option for VeriSilicon DC-series display controllers. It documents module naming and selects the DRM, bridge, helper, DMA GEM, regmap MMIO, and videomode infrastructure needed by the driver.

## Important APIs, Types, and Functions
The key symbol is `config DRM_VERISILICON_DC`, a tristate depending on `DRM`, `COMMON_CLK`, and either `RISCV` or `COMPILE_TEST`. It selects `DRM_BRIDGE_CONNECTOR`, `DRM_CLIENT_SELECTION`, `DRM_DISPLAY_HELPER`, `DRM_GEM_DMA_HELPER`, `DRM_KMS_HELPER`, `REGMAP_MMIO`, and `VIDEOMODE_HELPERS`.

## Control Flow
Kconfig evaluation exposes the driver only on supported architectures or compile-test builds. When enabled as built-in or module, the Makefile builds `verisilicon-dc.o`, allowing the platform driver to bind to `verisilicon,dc` nodes.

## State and Persistence Behavior
There is no runtime state in this file. Its persistent effect is build-time configuration, module availability, and selected helper subsystems.

## Dependencies and Integration Points
The symbol integrates with the DRM subsystem menu, common clock framework, RISC-V SoC builds, module autoloading, and the adjacent Makefile. Selected dependencies match the runtime code's use of atomic KMS, bridge connectors, DMA-backed GEM dumb buffers, and MMIO regmaps.

## Risks
Missing selects would create link or compile failures in minimal configs. The architecture dependency may hide the driver from non-RISC-V SoCs if VeriSilicon DC IP appears elsewhere. Over-selection increases kernel image size but keeps the small driver self-contained.

## Test Signals
Build coverage should include `m`, `y`, and `COMPILE_TEST` configurations, allmodconfig/allyesconfig, and minimal DRM+COMMON_CLK configs on RISC-V.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/Makefile

## Purpose
`verisilicon/Makefile` builds the VeriSilicon DC DRM module from bridge, CRTC, DC platform, DRM core, hardware database, common plane, and primary-plane sources.

## Important APIs, Types, and Functions
The important build variables are `verisilicon-dc-objs` and `obj-$(CONFIG_DRM_VERISILICON_DC)`. The object list is `vs_bridge.o`, `vs_crtc.o`, `vs_dc.o`, `vs_drm.o`, `vs_hwdb.o`, `vs_plane.o`, and `vs_primary_plane.o`.

## Control Flow
When `CONFIG_DRM_VERISILICON_DC` is enabled, Kbuild links the listed objects into `verisilicon-dc.o` and then into either the kernel image or a loadable module.

## State and Persistence Behavior
There is no runtime state. The Makefile fixes the compilation and link order contract for the driver module.

## Dependencies and Integration Points
It is driven by the Kconfig symbol and expects every listed source file to compile against the selected DRM/regmap/clock helper APIs. It intentionally excludes register-only headers because they are included by the C files.

## Risks
Adding a new source file without updating this list can produce missing-symbol link failures. Removing or renaming files without this update breaks the module build.

## Test Signals
Kbuild tests for built-in and module configurations, plus `modinfo verisilicon-dc` after a module build, validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge.c

## Purpose
`vs_bridge.c` implements the VeriSilicon output bridge layer between a DC CRTC and a downstream DRM bridge. It detects DPI versus DP graph endpoints, exposes bus-format negotiation, programs panel/DP/DPI output registers, creates an encoder and bridge connector, and wires the output into atomic KMS.

## Important APIs, Types, and Functions
Key entry point: `vs_bridge_init(struct drm_device *drm_dev, struct vs_crtc *crtc)`. Important helpers include `vs_bridge_attach()`, DPI/DP bus-format callbacks, `vs_bridge_atomic_check_dp()`, `vs_bridge_enable_common()`, `vs_bridge_atomic_enable_dpi()`, `vs_bridge_atomic_enable_dp()`, `vs_bridge_atomic_disable()`, and `vs_bridge_detect_output_interface()`. `struct vsdc_dp_format` maps Linux media-bus formats to VSDC DP register fields and YUV state.

## Control Flow
Initialization probes the device-tree graph for a remote endpoint on the CRTC output's DPI port and then DP port. It obtains the downstream bridge, allocates a `struct vs_bridge`, chooses DPI or DP bridge funcs, allocates a plain encoder, assigns the possible CRTC mask, registers and attaches the local bridge without creating a connector, then creates a bridge connector and attaches it to the encoder. Atomic enable programs either DPI RGB888 or DP format/YUV bits, applies bus polarity flags, enables DE/data/clock output, starts the panel, and commits panel config. Disable clears running bits and commits.

## State and Persistence Behavior
Persistent state is `struct vs_bridge`: the DRM bridge base, encoder, connector, CRTC pointer, downstream bridge pointer, and output interface type. Hardware state persists in display panel, DPI, and DP config registers until disabled or reprogrammed. There is no separate cache of bus format beyond DRM bridge state.

## Dependencies and Integration Points
The file depends on OF graph helpers, DRM bridge/encoder/connector helpers, `drm_bridge_connector`, media-bus format constants, regmap access to DC registers, `vs_crtc` output IDs, and register definitions in `vs_bridge_regs.h`. It is invoked by `vs_drm_initialize()` after each CRTC is created.

## Risks
Only DPI RGB888 is advertised for DPI. DP bus format support must remain synchronized between the format table, input/output callbacks, atomic check, and register programming. Device-tree port numbering is part of the ABI. `drm_bridge_attach()` and connector creation failures abort the whole DRM initialization. Common enable uses bus flag polarity interpretation that should be verified against downstream bridge expectations.

## Test Signals
Tests should cover DT graphs with DPI, DP, missing endpoints, and `-EPROBE_DEFER`; DP RGB/YUV media-bus format negotiation; atomic enable register programming; disable sequencing; connector creation; and modeset operation with bridge chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge.h

## Purpose
`vs_bridge.h` defines the VeriSilicon bridge object and public bridge initializer used by the DRM core path. It is the small cross-file contract between bridge setup and CRTC/DC state.

## Important APIs, Types, and Functions
It defines `enum vs_bridge_output_interface` with DPI and DP values, `struct vs_bridge` containing DRM bridge, encoder, connector, CRTC, downstream bridge, and interface type, `drm_bridge_to_vs_bridge()`, and `vs_bridge_init()`.

## Control Flow
Consumers pass a DRM device and `struct vs_crtc` to `vs_bridge_init()`, then the bridge implementation allocates and attaches the encoder/bridge/connector for that output. The inline container helper is used by bridge callbacks to recover driver state.

## State and Persistence Behavior
The header declares persistent per-output bridge state but owns no memory itself. Instances are devm/drmm-managed by the implementation.

## Dependencies and Integration Points
It depends on DRM bridge, connector, and encoder definitions and forward-declares `struct vs_crtc`. `vs_drm.c` includes it to initialize outputs; `vs_bridge.c` implements the callbacks.

## Risks
The enum values match DT endpoint port indices used by `of_graph_get_remote_node()` and must not be changed casually. The object stores raw pointers whose lifetime is managed externally by DRM/devm helpers.

## Test Signals
Compile tests and bridge initialization for both DPI and DP outputs validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge_regs.h

## Purpose
`vs_bridge_regs.h` maps VeriSilicon DC output-panel, DPI, DP, start, and commit registers used by `vs_bridge.c`.

## Important APIs, Types, and Functions
Important macros include `VSDC_DISP_PANEL_CONFIG(n)`, polarity and enable bits for DE/data/clock/running/YUV, `VSDC_DISP_DPI_CONFIG(n)` format fields, `VSDC_DISP_PANEL_START`, `VSDC_DISP_DP_CONFIG(n)` RGB/YUV format fields, and `VSDC_DISP_PANEL_CONFIG_EX(n)` commit bit.

## Control Flow
The bridge code writes these macros during atomic enable/disable. DPI mode clears DP enable and writes DPI format; DP mode writes DP format and YUV state; both paths start the panel and set commit.

## State and Persistence Behavior
These macros describe persistent MMIO state in the display controller. No software state lives here.

## Dependencies and Integration Points
The header depends on Linux bit macros and is included by the bridge implementation. It must match the DC register map and the regmap max range in `vs_dc.c`.

## Risks
Incorrect bit positions can invert polarity, disable outputs, or select a wrong bus format. Format constants are shared with the DP media-bus mapping and must stay synchronized.

## Test Signals
Register-write trace tests for DPI/DP enable and disable, plus hardware validation for RGB/YUV bus formats and polarity flags, validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc.c

## Purpose
`vs_crtc.c` implements VeriSilicon DC CRTC operations: pixel-clock enable/disable, display timing register programming, mode validation/fixup, vblank IRQ enable/disable, and CRTC allocation with a primary plane.

## Important APIs, Types, and Functions
The public entry is `vs_crtc_init()`. Important callbacks are `vs_crtc_atomic_enable()`, `vs_crtc_atomic_disable()`, `vs_crtc_mode_set_nofb()`, `vs_crtc_mode_valid()`, `vs_crtc_mode_fixup()`, `vs_crtc_enable_vblank()`, and `vs_crtc_disable_vblank()`. It uses `struct vs_crtc` and register macros from `vs_crtc_regs.h` and `vs_dc_top_regs.h`.

## Control Flow
Initialization allocates a managed CRTC object, stores DC pointer/output ID, creates a primary plane, initializes the DRM CRTC with that plane, and attaches helper funcs. Mode fixup normalizes CRTC timings and rounds the pixel clock through the output clock. Mode set writes horizontal/vertical display/total/sync registers and applies sync polarity bits, then sets the clock rate. Atomic enable prepares/enables the pixel clock and turns vblank on; disable turns vblank off and disables the pixel clock. Vblank callbacks toggle top-level VSYNC IRQ bits for the output.

## State and Persistence Behavior
Persistent state is the `struct vs_crtc` plus DRM CRTC state. Hardware timing registers and pixel-clock rate persist until the next modeset. Vblank state is maintained by DRM core and IRQ enable bits.

## Dependencies and Integration Points
The file depends on DRM atomic/vblank helpers, common clock APIs, regmap, `vs_primary_plane_init()`, DC top IRQ registers, and the DC identity output count. Bridge enable later starts the output panel that consumes these timings.

## Risks
Timing fields are 15-bit and validation only checks totals, not every start/end relationship. Clock errors are warned in mode set/enable but not always propagated. Vblank handling assumes DC top IRQ status bits line up with output IDs. Primary-plane creation failure aborts CRTC creation.

## Test Signals
Mode validation should cover too-large totals and unroundable clocks. Atomic modeset tests should verify register values, clock rate feedback, enable/disable ordering, vblank IRQ toggling, and multi-output CRTC IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc.h

## Purpose
`vs_crtc.h` defines the VeriSilicon CRTC object, timing limit, container helper, and public initializer.

## Important APIs, Types, and Functions
It defines `VSDC_DISP_TIMING_VALUE_MAX`, `struct vs_crtc` with DRM CRTC base, `struct vs_dc *dc`, and output ID, `drm_crtc_to_vs_crtc()`, and `vs_crtc_init()`.

## Control Flow
The DRM initialization path calls `vs_crtc_init()` for each hardware display output, then bridge and IRQ paths recover the driver object through `drm_crtc_to_vs_crtc()`.

## State and Persistence Behavior
The header declares per-CRTC state ownership. Runtime state is held in allocated `struct vs_crtc` instances and DRM atomic CRTC state.

## Dependencies and Integration Points
It depends on DRM CRTC and vblank headers and forward-declares `struct vs_dc`. It is shared by CRTC, bridge, DRM core, and plane paths.

## Risks
The timing max macro is used for validation and must match hardware bitfield width. The output ID is used as an array index into clocks, CRTCs, and registers.

## Test Signals
Compile coverage and multi-output modeset/vblank tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc_regs.h

## Purpose
`vs_crtc_regs.h` defines display timing, sync, gamma/dither, current-location, and display IRQ register offsets for VeriSilicon DC CRTCs.

## Important APIs, Types, and Functions
Key macros are `VSDC_DISP_HSIZE`, `VSDC_DISP_VSIZE`, `VSDC_DISP_HSYNC`, `VSDC_DISP_VSYNC`, field masks and builders for display/total/start/end values, sync enable/polarity bits, dither defaults, gamma registers, and display IRQ status/enable offsets.

## Control Flow
`vs_crtc_mode_set_nofb()` writes size and sync registers using these macros; future gamma/dither support would use the remaining definitions.

## State and Persistence Behavior
These macros describe persistent MMIO register state. The file itself has no runtime storage.

## Dependencies and Integration Points
It depends on Linux bit macros and is consumed by `vs_crtc.c`. Offsets must be within the regmap range configured by `vs_dc.c`.

## Risks
Incorrect shifts or masks corrupt display timings. Dither/gamma definitions are currently unused, so future users must verify default values and commit semantics.

## Test Signals
Mode-set register traces and hardware output timing measurements should verify encoded horizontal/vertical fields and sync polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc.c

## Purpose
`vs_dc.c` is the platform driver for VeriSilicon DC hardware. It probes resources, sets DMA mask, controls clocks/resets, maps MMIO through regmap, identifies the chip, requests IRQs, initializes DRM, and handles remove/shutdown.

## Important APIs, Types, and Functions
Important items include `vs_dc_regmap_cfg`, OF match table for `verisilicon,dc`, `vs_dc_irq_handler()`, `vs_dc_probe()`, `vs_dc_remove()`, `vs_dc_shutdown()`, and the `module_platform_driver()` registration.

## Control Flow
Probe validates an OF node and downstream port count, enforces `VSDC_MAX_OUTPUTS`, sets a 32-bit coherent DMA mask, allocates `struct vs_dc`, obtains optional shared resets, enables core/AXI/AHB clocks, gets IRQ, deasserts resets, maps MMIO, initializes regmap, reads chip identity, verifies DT port count against hardware display count, fetches per-output pixel clocks, requests IRQ, stores drvdata, and calls `vs_drm_initialize()`. Errors after reset deassert reassert resets. Remove finalizes DRM and asserts resets. Shutdown runs DRM atomic shutdown.

## State and Persistence Behavior
Persistent driver state is `struct vs_dc`: regmap, clocks, resets, DRM device pointer, and chip identity. Hardware reset and clocks persist while the platform device is bound. IRQ state routes through DRM vblank handling.

## Dependencies and Integration Points
The file integrates platform devices, OF graph, reset controller, common clock, DMA API, regmap MMIO, IRQs, chip identity from `vs_hwdb.c`, and DRM setup in `vs_drm.c`.

## Risks
The IRQ handler reads `VSDC_TOP_IRQ_ACK` as status and delegates clearing semantics to hardware/regmap assumptions; if the register is write-to-clear, behavior needs verification. Display-count mismatch between DT and hardware aborts probe. Reset assertion on all late failures is important because clocks are devm-managed. A 32-bit DMA mask constrains framebuffer placement.

## Test Signals
Probe tests should cover no OF node, no ports, too many ports, unsupported identity, missing pix clocks, IRQ failure, reset failure, and DRM init failure. Runtime tests should cover vblank IRQ delivery, shutdown path, and unbind/rebind reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc.h

## Purpose
`vs_dc.h` declares the central VeriSilicon display-controller state shared by platform, DRM, CRTC, bridge, and plane code.

## Important APIs, Types, and Functions
It defines `VSDC_MAX_OUTPUTS`, `VSDC_RESET_COUNT`, and `struct vs_dc` containing regmap, core/AXI/AHB clocks, per-output pixel clocks, reset bulk data, DRM device pointer, and chip identity.

## Control Flow
Probe fills `struct vs_dc`; DRM initialization and atomic callbacks then use it to access registers, clocks, output count, supported formats, and CRTC pointers.

## State and Persistence Behavior
`struct vs_dc` persists for the platform-device bind lifetime and owns no devm resource directly, but stores pointers to devm-managed resources. `drm_dev` is set during DRM initialization and cleared during finalize.

## Dependencies and Integration Points
The header depends on clock, regmap, reset, DRM device, and hardware database definitions. It is the shared state contract for all VeriSilicon DC files.

## Risks
Array fields are fixed at two outputs; future hardware with more outputs requires coordinated updates. `drm_dev` can be NULL during probe failure/finalize and must not be dereferenced outside initialized paths.

## Test Signals
Compile tests and dual-output modeset/IRQ coverage validate the shared state layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc_top_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc_top_regs.h

## Purpose
`vs_dc_top_regs.h` defines top-level VeriSilicon DC reset, IRQ, and chip-identity register offsets.

## Important APIs, Types, and Functions
Macros include `VSDC_TOP_RST`, `VSDC_TOP_IRQ_ACK`, `VSDC_TOP_IRQ_VSYNC(n)`, `VSDC_TOP_IRQ_EN`, `VSDC_TOP_CHIP_MODEL`, `VSDC_TOP_CHIP_REV`, and `VSDC_TOP_CHIP_CUSTOMER_ID`.

## Control Flow
`vs_hwdb.c` reads identity registers, `vs_dc.c` reads IRQ ACK/status, and `vs_crtc.c` toggles VSYNC IRQ enable bits using these definitions.

## State and Persistence Behavior
The file describes persistent MMIO register state and contains no software state.

## Dependencies and Integration Points
It depends on Linux bit macros and is included by DC, CRTC, DRM IRQ, and hardware database code.

## Risks
IRQ ACK/status semantics must match hardware. Identity offsets drive supported-format and display-count selection; wrong values reject or misconfigure hardware.

## Test Signals
Hardware probe logs, IRQ enable/readback checks, and identity table matching validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc_top_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_drm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_drm.c

## Purpose
`vs_drm.c` implements the DRM-device layer for VeriSilicon DC: GEM/dumb buffer policy, mode-config setup, CRTC/bridge creation, vblank init, device registration, fbdev/client setup, shutdown, and IRQ dispatch.

## Important APIs, Types, and Functions
Key APIs are `vs_drm_initialize()`, `vs_drm_finalize()`, `vs_drm_shutdown_handler()`, and `vs_drm_handle_irq()`. Important internal pieces include `vs_gem_dumb_create()`, `vs_drm_driver`, mode-config funcs, and `vs_mode_config_init()`.

## Control Flow
Initialization allocates a managed `struct vs_drm_dev`, links it to `vs_dc`, initializes mode config, removes conflicting firmware framebuffers, creates a CRTC and bridge for each hardware display, initializes vblank, sets mode bounds and atomic helpers, starts connector polling, resets mode config, registers the DRM device, and starts DRM clients. Finalize unregisters DRM, stops polling, performs atomic shutdown, and clears `dc->drm_dev`. IRQ handling walks display outputs, sends vblank events for known VSYNC bits, and warns once on unknown interrupts.

## State and Persistence Behavior
Persistent state is `struct vs_drm_dev`, its CRTC pointer array, and the linked `struct vs_dc`. Dumb buffers are DMA GEM objects with 128-byte aligned pitches. DRM registration exposes device nodes and fbdev/client state until finalize.

## Dependencies and Integration Points
The file depends on DRM driver, atomic helper, GEM DMA/fbdev DMA, aperture removal, bridge/CRTC init, vblank, connector polling, and top-level IRQ bit definitions. It is called exclusively by the platform DC driver.

## Risks
The CRTC array assignment happens even when `vs_bridge_init()` returns NULL for skipped outputs, so display count and bridge presence must be handled by userspace/DRM correctly. `vs_gem_dumb_create()` enforces pitch alignment but format support remains governed by planes. Unknown IRQ bits may indicate unhandled hardware events. Shutdown assumes `dc->drm_dev` is valid.

## Test Signals
Tests should cover conflicting simple-framebuffer removal, registration failure unwind, dumb buffer pitch alignment, dual-output vblank handling, skipped bridge outputs, DRM hotplug polling, remove, and system shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_drm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_drm.h

## Purpose
`vs_drm.h` declares the VeriSilicon DRM device wrapper and lifecycle/IRQ APIs used by the platform DC driver.

## Important APIs, Types, and Functions
It defines `struct vs_drm_dev` embedding `struct drm_device`, storing `struct vs_dc *dc`, and a CRTC pointer array sized by `VSDC_MAX_OUTPUTS`. It declares `vs_drm_initialize()`, `vs_drm_finalize()`, `vs_drm_shutdown_handler()`, and `vs_drm_handle_irq()`.

## Control Flow
The platform driver calls initialize after resources are ready, finalize during remove, shutdown handler during system shutdown, and IRQ handler from the top-level interrupt routine.

## State and Persistence Behavior
The DRM wrapper persists for the DRM device lifetime and points back to DC state. CRTC pointers are populated during initialization and consumed by IRQ dispatch.

## Dependencies and Integration Points
It depends on platform device and DRM device types and on `VSDC_MAX_OUTPUTS` from the included DC context. It is shared between DC, DRM, CRTC, and IRQ code.

## Risks
The header relies on `VSDC_MAX_OUTPUTS` being visible from included dependencies. Null CRTC entries are possible when outputs are skipped or initialization is partial.

## Test Signals
Compile tests and probe/remove/IRQ tests validate this API contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_hwdb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_hwdb.c

## Purpose
`vs_hwdb.c` maps VeriSilicon DC model/revision/customer identity registers to driver capabilities, currently display count and supported DRM framebuffer formats.

## Important APIs, Types, and Functions
The public function is `vs_fill_chip_identity(struct regmap *regs, struct vs_chip_identity *ident)`. Static data includes RGB format arrays with and without YUV444 capability placeholders, `struct vs_formats` instances, and `vs_chip_identities[]` for DC8200 revisions/customer IDs.

## Control Flow
The function reads model, revision, and customer ID from top registers, linearly searches the identity table, matches either exact customer ID or wildcard `~0U`, copies the identity into the caller, overwrites the customer ID with the actual hardware value, and returns 0. No match returns `-EINVAL`.

## State and Persistence Behavior
The table is static read-only driver data. The selected `vs_chip_identity` persists in `struct vs_dc` and feeds output count, pixel-clock lookup count, and plane format list.

## Dependencies and Integration Points
The file depends on regmap reads, DRM fourcc constants, top-register definitions, and `vs_hwdb.h`. `vs_dc_probe()` uses it before creating CRTCs and planes.

## Risks
Wildcard entries can shadow more specific entries if ordered incorrectly. The `with_yuv444` and `no_yuv444` arrays are currently identical aside from TODO comments, so advertised capabilities may not yet reflect hardware YUV support. Unsupported revisions fail probe entirely.

## Test Signals
Mock regmap tests should cover exact match, wildcard match, unknown identity, table ordering, actual customer ID preservation, and format-list selection used by primary-plane init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_hwdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_hwdb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_hwdb.h

## Purpose
`vs_hwdb.h` declares the hardware database structures for VeriSilicon DC capability selection.

## Important APIs, Types, and Functions
It defines `struct vs_formats`, `struct vs_chip_identity`, and `vs_fill_chip_identity()`. `struct vs_chip_identity` carries model, revision, customer ID, display count, and a pointer to supported DRM formats.

## Control Flow
Probe code fills a `vs_chip_identity` through `vs_fill_chip_identity()` and later CRTC/plane code consults its display count and format array.

## State and Persistence Behavior
The populated identity persists in `struct vs_dc`. Format arrays are static data owned by the implementation.

## Dependencies and Integration Points
The header depends on regmap and fixed-width types. It integrates DC probe with plane format advertisement and output creation.

## Risks
Consumers trust `formats` to be non-NULL and `display_count` to fit `VSDC_MAX_OUTPUTS`. Future capability fields must preserve initialization for existing entries.

## Test Signals
Compile tests plus hardware identity probing and plane creation with the selected format list validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_hwdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_plane.c

## Purpose
`vs_plane.c` provides shared VeriSilicon plane helpers for translating DRM formats into DC color/swizzle fields and computing DMA start addresses for a framebuffer source rectangle.

## Important APIs, Types, and Functions
The public functions are `drm_format_to_vs_format(u32 drm_format, struct vs_format *vs_format)` and `vs_fb_get_dma_addr(struct drm_framebuffer *fb, const struct drm_rect *src_rect)`. It maps common 16/32-bit RGB/XRGB/ARGB/BGR/RGBA formats to `enum vs_color_format` and `enum vs_swizzle`.

## Control Flow
Format translation selects a hardware color format first, then a channel swizzle based on fourcc ordering, defaults to ARGB swizzle for formats where swizzle is not meaningful, and clears UV swizzle. DMA address calculation gets plane 0's DMA GEM object, starts from `dma_addr + fb->offsets[0]`, then adds x offset using `drm_format_info_min_pitch()` and y offset using framebuffer pitch.

## State and Persistence Behavior
The helpers do not persist state. Their outputs are immediately used by plane register programming. DMA addresses refer to persistent DMA GEM backing memory while the framebuffer is alive.

## Dependencies and Integration Points
The file depends on DRM framebuffer DMA helpers, GEM DMA objects, fourcc metadata, and `vs_plane.h`. `vs_primary_plane.c` consumes both helpers during atomic update.

## Risks
Unexpected formats only warn and leave `color` potentially unchanged if caller provided uninitialized storage. Only plane 0 is handled. Source coordinates are 16.16 fixed-point and are shifted before address calculation; scaling is disallowed elsewhere, so this is safe only with matching atomic checks.

## Test Signals
Unit tests should cover every advertised fourcc, swizzle mapping, DMA address calculation for nonzero offsets/src x/y, and rejection prevention for unadvertised formats in plane init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_plane.h

## Purpose
`vs_plane.h` defines VeriSilicon plane format enums, position/size packing macros, shared plane helper prototypes, and the primary-plane initializer declaration.

## Important APIs, Types, and Functions
It defines `VSDC_MAKE_PLANE_SIZE()`, `VSDC_MAKE_PLANE_POS()`, `enum vs_color_format`, `enum vs_swizzle`, `struct vs_format`, `drm_format_to_vs_format()`, `vs_fb_get_dma_addr()`, and `vs_primary_plane_init()`.

## Control Flow
Primary-plane code calls the helper functions and macros during atomic updates to encode framebuffer format, top-left/bottom-right coordinates, size, stride, and DMA address.

## State and Persistence Behavior
The header contains no runtime state. Encoded values become persistent hardware register state after regmap writes.

## Dependencies and Integration Points
It depends on DRM device, framebuffer, plane, and rect definitions. It is included by common plane and primary-plane implementation files.

## Risks
Position/size macros mask to 15 bits, so validation must keep dimensions and coordinates within hardware range. Color enum values must match hardware register encoding.

## Test Signals
Compile coverage and plane atomic update register-value tests validate the definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_primary_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_primary_plane.c

## Purpose
`vs_primary_plane.c` implements the VeriSilicon primary plane. It validates no-scaling plane state, enables/disables the framebuffer layer, writes format/address/stride/position/size/blend registers, and allocates the primary plane with hardware-supported formats.

## Important APIs, Types, and Functions
The public API is `vs_primary_plane_init()`. Important callbacks are `vs_primary_plane_atomic_check()`, `vs_primary_plane_atomic_enable()`, `vs_primary_plane_atomic_disable()`, `vs_primary_plane_atomic_update()`, and `vs_primary_plane_commit()`.

## Control Flow
Atomic check fetches the new plane and CRTC state and calls `drm_atomic_helper_check_plane_state()` with no scaling and clipping allowed. Enable sets FB enable and display ID bits then commits. Update disables the plane if not visible; otherwise it translates the DRM format, writes color/swizzle/UV fields, computes DMA address, writes address/stride/top-left/bottom-right/size, disables blending, and commits. Init allocates a managed universal primary plane with the format list from chip identity and attaches helper funcs.

## State and Persistence Behavior
Software state is standard DRM plane state. Hardware state persists in FB config, address, stride, geometry, blend, and config-ex commit registers. Framebuffer memory is DMA-backed and remains owned by DRM GEM helpers.

## Dependencies and Integration Points
The file depends on DRM atomic/GEM helper APIs, regmap, `vs_crtc`, `vs_dc`, common plane helpers, and primary-plane register definitions. It is created by `vs_crtc_init()`.

## Risks
`vs_primary_plane_atomic_disable()` sets `FB_EN` instead of clearing it, which looks suspicious for a disable path and should be verified against hardware semantics. Atomic update assumes a non-NULL framebuffer when visible. Blend is always disabled, and only a single primary plane is implemented. Register commits rely on `VSDC_FB_CONFIG_EX_COMMIT` behavior.

## Test Signals
Tests should cover visible and invisible plane updates, disable behavior on hardware/readback, format/swizzle programming, DMA source offsets, pitch programming, clipping without scaling, and supported format advertisement from HWDB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_primary_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_primary_plane_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_primary_plane_regs.h

## Purpose
`vs_primary_plane_regs.h` defines VeriSilicon framebuffer/primary-plane register offsets and bitfields.

## Important APIs, Types, and Functions
Key macros include `VSDC_FB_ADDRESS`, `VSDC_FB_STRIDE`, `VSDC_FB_CONFIG` fields for format/swizzle/tile/rotation/scale/YUV, `VSDC_FB_SIZE`, `VSDC_FB_CONFIG_EX` commit/enable/zpos/display ID bits, position registers, and blend-disable bit.

## Control Flow
`vs_primary_plane_atomic_update()` writes these registers and then sets the commit bit. Enable/disable paths also use config-ex enable/display/commit bits.

## State and Persistence Behavior
The macros describe persistent display-controller plane state. There is no software state.

## Dependencies and Integration Points
It depends on Linux bit macros and common plane packing macros from `vs_plane.h` for values written to size/position registers.

## Risks
`VSDC_FB_CONFIG_TILE_MODE(v)` shifts by 14 while the mask is bits 21:17, which appears inconsistent and should be reviewed before tile-mode support is used. Display ID mask currently covers one bit, matching two outputs only.

## Test Signals
Register encoding tests should validate format, swizzle, display ID, enable/disable, geometry, and tile-mode macros before adding tiled formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_primary_plane_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/Kconfig

## Purpose
`vgem/Kconfig` declares the virtual GEM provider driver used for software-renderer and buffer-sharing workflows without physical graphics hardware.

## Important APIs, Types, and Functions
The symbol is `DRM_VGEM`, a tristate depending on `DRM` and `MMU` and selecting `DRM_GEM_SHMEM_HELPER`.

## Control Flow
When enabled, the adjacent Makefile builds the `vgem` module. Userspace can then open a render node backed by shmem GEM objects and synthetic fences.

## State and Persistence Behavior
No runtime state is stored here; build configuration persists in the kernel/module image.

## Dependencies and Integration Points
The selected shmem helper matches VGEM's coherent GEM backing. The option integrates with Mesa/software rendering and dma-buf sharing tests.

## Risks
Without `MMU` or DRM shmem helper support the driver cannot provide expected mmap/dma-buf behavior. Build coverage must keep the dependency list current.

## Test Signals
Kconfig build tests for built-in/module/disabled states and IGT VGEM tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/Makefile

## Purpose
`vgem/Makefile` builds the virtual GEM provider module from its driver and fence implementation.

## Important APIs, Types, and Functions
It defines `vgem-y := vgem_drv.o vgem_fence.o` and `obj-$(CONFIG_DRM_VGEM) += vgem.o`.

## Control Flow
Kbuild links VGEM core and fence files into one module when the Kconfig symbol is enabled.

## State and Persistence Behavior
There is no runtime state in the Makefile.

## Dependencies and Integration Points
It is controlled by `DRM_VGEM` and must stay synchronized with VGEM source file names.

## Risks
Missing objects cause unresolved VGEM ioctl or lifecycle symbols.

## Test Signals
Module and built-in builds validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_drv.c

## Purpose
`vgem_drv.c` implements the virtual GEM DRM render driver. It creates a faux device, registers a DRM render-capable GEM driver, creates coherent shmem GEM objects, and manages per-file VGEM fence state.

## Important APIs, Types, and Functions
Important functions are `vgem_open()`, `vgem_postclose()`, `vgem_gem_create_object()`, `vgem_init()`, and `vgem_exit()`. The driver exposes `DRM_IOCTL_VGEM_FENCE_ATTACH` and `DRM_IOCTL_VGEM_FENCE_SIGNAL` through `vgem_ioctls`, uses `DEFINE_DRM_GEM_FOPS`, and embeds `struct drm_device` in a file-static `struct vgem_device`.

## Control Flow
Module init creates a faux device, opens a devres group, coerces a 64-bit DMA mask, allocates a managed DRM device, stores the faux device pointer, and registers DRM. Open allocates `struct vgem_file` and initializes fence IDR/mutex. Postclose signals/cleans all remaining fences and frees file state. GEM object creation allocates a shmem object and marks it write-combined/coherent for dma-buf sharing. Exit unregisters DRM, releases devres, and destroys the faux device.

## State and Persistence Behavior
Global `vgem_device` persists for module lifetime. Each file has an IDR of outstanding synthetic fences. GEM objects are shmem-backed and persist while handles/dma-bufs reference them. There is no hardware state.

## Dependencies and Integration Points
The file depends on DRM core, DRM GEM shmem helpers, faux devices, dma-buf, shmem/vmalloc infrastructure, and VGEM fence functions. It is used heavily by graphics tests and software renderers as a buffer-sharing endpoint.

## Risks
Open failure must free file state after fence init failures. `vgem_gem_create_object()` relies on coherent/cache behavior because VGEM has no explicit CPU access ioctls. Module exit assumes the global device was successfully initialized. Fence ioctls are render-node allowed and must validate handles and flags in the fence file.

## Test Signals
IGT VGEM tests, GEM create/mmap/dma-buf export/import, open/close leak checks, module load/unload, and fence attach/signal tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_drv.h

## Purpose
`vgem_drv.h` declares VGEM per-file fence state and ioctl helper prototypes shared by the driver and fence implementation.

## Important APIs, Types, and Functions
It defines `struct vgem_file` with `idr fence_idr` and `mutex fence_mutex`, includes UAPI `vgem_drm.h`, and declares `vgem_fence_open()`, `vgem_fence_attach_ioctl()`, `vgem_fence_signal_ioctl()`, and `vgem_fence_close()`.

## Control Flow
`vgem_open()` initializes `struct vgem_file` with `vgem_fence_open()`, ioctls operate on its IDR, and `vgem_postclose()` calls `vgem_fence_close()`.

## State and Persistence Behavior
The per-file IDR persists for an open DRM file and owns references to active dma-fences until signal, timeout, or close.

## Dependencies and Integration Points
The header depends on DRM GEM/cache headers and the VGEM UAPI. It is the contract between `vgem_drv.c`, `vgem_fence.c`, and userspace ioctl structures.

## Risks
ID allocation and lifetime must remain per-file so fence handles cannot cross DRM file boundaries. UAPI structure changes are ABI-sensitive.

## Test Signals
Compile tests and ioctl tests using multiple DRM file descriptors validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_fence.c

## Purpose
`vgem_fence.c` implements synthetic dma-fence creation, attachment to GEM reservation objects, signaling, timeout, and per-file cleanup for VGEM.

## Important APIs, Types, and Functions
Key type: `struct vgem_fence`, embedding `dma_fence`, spinlock, and timer. Public functions are `vgem_fence_open()`, `vgem_fence_attach_ioctl()`, `vgem_fence_signal_ioctl()`, and `vgem_fence_close()`. Internal helpers include `vgem_fence_create()`, `vgem_fence_timeout()`, and `vgem_fence_release()`.

## Control Flow
Attach ioctl validates flags/padding, looks up the GEM handle, creates a fence with a 10-second timer, checks reservation-object conflicts for read/write usage, reserves and adds the fence under the reservation lock, stores it in the file IDR, and returns an ID. Signal ioctl validates flags, removes the fence from IDR with `idr_replace(..., NULL, id)`, returns `-ENOENT` for missing IDs, returns `-ETIMEDOUT` if the timer already signaled it, signals the fence, and drops the reference. Close iterates all remaining IDR entries, signals and puts each, then destroys IDR/mutex.

## State and Persistence Behavior
Fences persist in dma-resv objects and the per-file IDR until signaled, timed out, or closed. The timeout timer guarantees eventual signaling to avoid indefinite hangs.

## Dependencies and Integration Points
The file integrates Linux dma-fence, dma-resv, DRM GEM handle lookup, and VGEM UAPI flags. Consumers see fences through dma-buf reservation objects.

## Risks
Attach checks reservation signaled state before taking the reservation lock, so races with other users need careful dma-resv semantics review. Timed-out fences remain removable by signal ioctl but report `-ETIMEDOUT`. IDR replacement leaves NULL entries, and all callers must handle `ERR_PTR` results from `idr_replace()`.

## Test Signals
Tests should cover read/read sharing, read/write conflicts, invalid flags/pad, missing handles, timeout behavior, signal-after-timeout, double signal, close cleanup, and dma-buf consumers waiting on attached fences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/Kconfig

## Purpose
`virtio/Kconfig` declares VirtIO GPU support and the optional KMS modesetting subfeature. It controls build availability for virtual GPU devices used by QEMU/KVM/Xen-style VMMs.

## Important APIs, Types, and Functions
Symbols are `DRM_VIRTIO_GPU` and `DRM_VIRTIO_GPU_KMS`. The main driver depends on `DRM`, `VIRTIO_MENU`, and `MMU`, selects `VIRTIO`, DRM client/KMS/shmem helpers, and `VIRTIO_DMA_SHARED_BUFFER`. KMS depends on the main symbol and defaults to enabled.

## Control Flow
Kconfig decides whether the `virtio-gpu` object is built. If KMS is disabled, runtime init masks mode-setting/atomic features and operates as a render/headless device.

## State and Persistence Behavior
There is no runtime state in this file; configuration persists in kernel/module capabilities.

## Dependencies and Integration Points
The selections match runtime use of virtqueues, shmem GEM, dma-buf UUID sharing, DRM clients, and KMS helpers.

## Risks
Disabling KMS changes driver feature bits and userspace-visible behavior. Missing selected helpers would cause link failures. `MMU` is required for GEM mmap/shmem behavior.

## Test Signals
Builds with KMS enabled/disabled and module/built-in configurations validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/Makefile

## Purpose
`virtio/Makefile` links the VirtIO GPU DRM driver from core, KMS, GEM, VRAM, display, virtqueue, fence, object, debugfs, plane, ioctl, PRIME, trace, and submit sources.

## Important APIs, Types, and Functions
The key build variable is `virtio-gpu-y`, listing `virtgpu_drv.o`, `virtgpu_kms.o`, `virtgpu_gem.o`, `virtgpu_vram.o`, `virtgpu_display.o`, `virtgpu_vq.o`, `virtgpu_fence.o`, `virtgpu_object.o`, `virtgpu_debugfs.o`, `virtgpu_plane.o`, `virtgpu_ioctl.o`, `virtgpu_prime.o`, `virtgpu_trace_points.o`, and `virtgpu_submit.o`. `obj-$(CONFIG_DRM_VIRTIO_GPU)` links the module.

## Control Flow
Kbuild compiles and links the listed objects when `DRM_VIRTIO_GPU` is enabled.

## State and Persistence Behavior
No runtime state lives here.

## Dependencies and Integration Points
The list includes files outside this research item (`virtgpu_vq.c`, `virtgpu_vram.c`) that provide command transport and VRAM/blob support used by researched files.

## Risks
Omitting transport or trace objects would create missing symbols or absent tracepoints. The object list must remain synchronized with declarations in `virtgpu_drv.h`.

## Test Signals
Allmodconfig, module build, and tracepoint build validation cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_debugfs.c

## Purpose
`virtgpu_debugfs.c` exposes VirtIO GPU feature, fence, and host-visible memory information through DRM debugfs files.

## Important APIs, Types, and Functions
Key functions are `virtio_gpu_features()`, `virtio_gpu_debugfs_irq_info()`, `virtio_gpu_debugfs_host_visible_mm()`, and `virtio_gpu_debugfs_init()`. Helpers format booleans and integers. Debugfs entries are `virtio-gpu-features`, `virtio-gpu-irq-fence`, and `virtio-gpu-host-visible-mm`.

## Control Flow
DRM debugfs init registers the info files for a minor. Reads recover `virtio_gpu_device` from `minor->dev->dev_private`, print negotiated features, capsets/scanouts, last/current fence IDs, or dump the DRM MM allocator for the host-visible region.

## State and Persistence Behavior
The file exposes live driver state but owns none. Output reflects current feature flags, fence counters, and host-visible MM allocations.

## Dependencies and Integration Points
It depends on DRM debugfs, seq_file, string yes/no helpers, DRM printers, and `virtgpu_drv.h`. It is wired into `struct drm_driver` under `CONFIG_DEBUG_FS`.

## Risks
Debugfs reads are diagnostic and mostly lockless; host-visible MM dumping should be safe with DRM MM expectations but can race with allocations if not externally protected. Missing `dev_private` during teardown would be problematic if reads race unplug.

## Test Signals
Debugfs smoke tests should read all entries with virgl/blob/host-visible combinations and during device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_display.c

## Purpose
`virtgpu_display.c` implements VirtIO GPU KMS display objects: CRTCs, connectors, encoders, framebuffers, mode discovery/validation, scanout setup, and modeset initialization/finalization.

## Important APIs, Types, and Functions
Important public functions are `virtio_gpu_modeset_init()` and `virtio_gpu_modeset_fini()`. Internal callbacks cover CRTC mode set/enable/disable/flush, connector modes/detect/destroy, encoder no-ops, `vgdev_output_init()`, `virtio_gpu_framebuffer_init()`, and `virtio_gpu_user_framebuffer_create()`.

## Control Flow
Modeset init initializes mode_config, sets host-byte-order fb quirk, bounds modes to 32..8192, disables modifiers, creates output objects for each scanout, initializes vblank, and resets mode config. Each output gets primary/cursor planes, CRTC, connector, optional EDID property, virtual encoder, and default enabled 1024x768 info for output 0. Connector modes prefer EDID; otherwise they add generic modes and a preferred CVT mode matching host display info. CRTC flush marks modeset-needed and arms/sends vblank events. Plane update code performs actual scanout commands.

## State and Persistence Behavior
Persistent state is `virtio_gpu_output` per scanout, connector EDID, CRTC/encoder/connector/plane objects, and mode_config. `needs_modeset` bridges CRTC flush to plane update. Framebuffers own GEM references until destroyed.

## Dependencies and Integration Points
The file depends on DRM atomic, EDID, fb, vblank, simple KMS helpers, VirtIO GPU commands from `virtgpu_vq.c`, and planes from `virtgpu_plane.c`.

## Risks
`virtio_gpu_user_framebuffer_create()` returns `NULL` rather than `ERR_PTR(ret)` on framebuffer init failure, which is unusual for `fb_create`. Connector init/register return values are not all checked. Modeset and plane update are coupled because the protocol cannot fully separate them. Preferred-mode filtering is heuristic around host-provided dimensions.

## Test Signals
KMS tests should cover EDID and no-EDID modes, hotplug display-info updates, vblank events, addfb format restrictions, multi-scanout initialization, output disable scanout clearing, and framebuffer failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_drv.c

## Purpose
`virtgpu_drv.c` is the VirtIO GPU module/virtio-driver entry point and DRM driver definition. It handles probe/remove/shutdown/config-change, PCI VGA quirks, feature negotiation table, module parameter modeset gating, and DRM driver callbacks.

## Important APIs, Types, and Functions
Important functions are `virtio_gpu_probe()`, `virtio_gpu_remove()`, `virtio_gpu_shutdown()`, `virtio_gpu_config_changed()`, `virtio_gpu_driver_init()`, and `virtio_gpu_driver_exit()`. It defines virtio ID/features tables, `virtio_gpu_driver`, DRM fops, and the `struct drm_driver driver`.

## Control Flow
Module init may acquire legacy VGA arbitration for virtio-vga, registers the virtio driver, then releases VGA resources. Probe rejects firmware-only or disabled modeset cases, allocates a DRM device on the parent DMA-capable device, applies PCI aperture quirks for virtio-vga, sets max DMA segment size, calls `virtio_gpu_init()`, registers DRM, and starts DRM clients. Remove unplugs DRM, atomic-shuts down, deinitializes virtio state, and drops the DRM reference. Config change schedules work in `virtgpu_kms.c`.

## State and Persistence Behavior
Module parameter `modeset` persists for module lifetime. The DRM device persists from probe until remove/release. Virtio feature bits are negotiated once per device and copied into `virtio_gpu_device` during init.

## Dependencies and Integration Points
The file integrates virtio core, PCI/VGA aperture handling, DRM core/client/fbdev shmem, atomic shutdown, debugfs, GEM object creation, PRIME import, ioctls, and lifecycle functions implemented in other VirtIO GPU files.

## Risks
Probe uses the parent device for DRM DMA behavior, which is intentional but sensitive to virtio transport assumptions. Feature table exposes virgl only on little-endian builds. Shutdown only unplugs DRM and stops further device talk; full cleanup happens on remove. Modeset gating must align with firmware-driver policy.

## Test Signals
Tests should cover virtio-gpu-pci and virtio-vga probe, aperture removal, modeset parameter values, feature negotiation, config-change work scheduling, remove/unplug races, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_drv.h

## Purpose
`virtgpu_drv.h` is the central internal header for VirtIO GPU. It defines object, fence, queue, output, framebuffer, plane-state, device, file-private, capset, and command interfaces shared across KMS, GEM, ioctl, PRIME, object, fence, submit, vq, and VRAM code.

## Important APIs, Types, and Functions
Key definitions include driver version/name constants, state constants, `MAX_CAPSET_ID`, `MAX_RINGS`, `struct virtio_gpu_object_params`, `struct virtio_gpu_object`, `struct virtio_gpu_object_array`, `struct virtio_gpu_fence_driver`, `struct virtio_gpu_fence`, `struct virtio_gpu_vbuffer`, `struct virtio_gpu_output`, `struct virtio_gpu_framebuffer`, `struct virtio_gpu_plane_state`, `struct virtio_gpu_queue`, `struct virtio_gpu_device`, and `struct virtio_gpu_fpriv`. It declares all cross-file APIs for init, ioctls, GEM arrays, virtqueue commands, modeset, planes, fences, objects, PRIME, debugfs, VRAM, and submit.

## Control Flow
The header does not execute flow, but it defines the call graph: `virtgpu_drv.c` probes and calls KMS init; ioctl and plane paths create objects and command buffers; vq functions emit commands and complete fences; PRIME and VRAM paths manage dma-buf sharing and host-visible memory; submit path parses userspace execbuffers.

## State and Persistence Behavior
`struct virtio_gpu_device` is the persistent per-device state: virtio device, DRM device, scanouts, queues, fence timeline, ID allocators, response waitqueue, feature flags, host-visible memory manager, work items, capset cache, and locks. `struct virtio_gpu_fpriv` persists per DRM file for virgl context state, ring configuration, and debug name. `struct virtio_gpu_object` persists with GEM objects and tracks host resource ID, blob type, UUID state, and attachment.

## Dependencies and Integration Points
The header depends on Linux virtio GPU protocol definitions, DRM core/GEM/shmem/ioctl/fourcc/framebuffer/probe helpers, and UAPI `virtgpu_drm.h`. It bridges all source files in the driver and unresearched transport/VRAM files.

## Risks
This is a high-coupling ABI-like internal contract; field lifetime and locking comments must stay accurate. Object kind checks rely on `obj->funcs` pointer identity. Fixed scanout/ring/capset limits must match protocol. Functions declared here often transfer ownership of object arrays, fences, or command buffers to vq completion paths.

## Test Signals
Whole-driver build coverage, sparse/lockdep, object lifetime tests, multi-context/ring submit tests, PRIME import/export, KMS, and debugfs tests validate this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_fence.c

## Purpose
`virtgpu_fence.c` implements the VirtIO GPU dma-fence timeline used for control-queue commands and optional per-ring context fences.

## Important APIs, Types, and Functions
Public APIs are `virtio_gpu_fence_alloc()`, `virtio_gpu_fence_emit()`, and `virtio_gpu_fence_event_process()`. Internal dma-fence ops provide driver/timeline names and a defensive `signaled` callback warning if a fence leaks before emission.

## Control Flow
Fence allocation partially initializes a dma-fence with context `base_fence_ctx + ring_idx` and seqno 0. Emission under the fence driver spinlock assigns the next fence ID/seqno, takes a reference, links it into the pending list, traces emission, and adds fence fields to the virtio command header. Completion processing records last fence ID, finds the matching pending fence, signals older fences in the same context, sends any reserved DRM fence events, removes signaled fences from the list, and drops references.

## State and Persistence Behavior
`virtio_gpu_fence_driver` persists in `virtio_gpu_device` with current/last fence IDs, timeline context, pending fence list, and spinlock. Individual fences persist until host completion signals them or cleanup drops them.

## Dependencies and Integration Points
The file depends on dma-fence tracepoints, DRM event sending, virtio GPU command header flags, and locking state initialized in `virtgpu_kms.c`. Submit, object creation, transfers, plane flushes, and vq code allocate/emit fences.

## Risks
Fences must not be exposed before `virtio_gpu_fence_emit()` sets a nonzero seqno. Completion only signals strictly older fences in the same context plus the matched fence, so context/ring correctness is critical. Lost host completions leave fences pending. DRM event ownership is tied to fence completion under spinlock.

## Test Signals
Tests should cover monotonic fence IDs, per-ring contexts, out-of-order completions, event delivery, debugfs last/current fence values, leaked pre-emit fence warnings, and command headers with/without ring info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_gem.c

## Purpose
`virtgpu_gem.c` implements GEM object creation for dumb and resource objects, context attach/detach on GEM open/close, and helper arrays for batches of GEM objects used by command submission and delayed cleanup.

## Important APIs, Types, and Functions
Important functions are `virtio_gpu_mode_dumb_create()`, `virtio_gpu_gem_object_open()`, `virtio_gpu_gem_object_close()`, `virtio_gpu_array_alloc()`, `virtio_gpu_array_from_handles()`, `virtio_gpu_array_add_obj()`, `virtio_gpu_array_lock_resv()`, `virtio_gpu_array_unlock_resv()`, `virtio_gpu_array_add_fence()`, `virtio_gpu_array_put_free()`, and delayed free work helpers.

## Control Flow
Dumb create accepts only 32 bpp, computes pitch/size, selects a 2D host format, optionally uses shareable guest blob resources when blob support exists without virgl, creates the object, and returns handle/pitch. GEM open creates a virgl context if needed and attaches the resource to the file context. Close detaches from the context. Object arrays are allocated from handles, lock all reservation objects with ww locking when needed, reserve fence slots, add fences, and drop references either immediately or through a workqueue.

## State and Persistence Behavior
GEM handles own references to `virtio_gpu_object` instances. Per-file virgl contexts track attached resources on host side. Object arrays are transient command payload/lifetime containers and may be held until vq completion before references are dropped.

## Dependencies and Integration Points
The file depends on DRM GEM handle lookup, dma-resv locking, VirtIO GPU object creation, context attach/detach commands, and notify paths. Submit, ioctl transfer, plane, object, and vq code use object arrays.

## Risks
On GEM create handle failure, the code calls `drm_gem_object_release()` instead of the full object free path; this is a pattern worth reviewing for resource-ID cleanup in error cases. Reservation locking failures must unlock and drop refs. Delayed free work must be flushed before device teardown. Context attach can fail only by allocation here; host command completion is asynchronous.

## Test Signals
Tests should cover dumb create validation, blob-backed dumb resources, GEM open/close with virgl contexts, object array duplicate/missing handles, reservation deadlock avoidance, fence insertion, and delayed free flushing during remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_ioctl.c

## Purpose
`virtgpu_ioctl.c` implements most userspace VirtIO GPU ioctls: map, getparam, resource create/info, 3D transfers, wait, capset query, blob resource creation, context initialization, and ioctl table registration.

## Important APIs, Types, and Functions
Important functions are `virtio_gpu_create_context()`, `virtio_gpu_map_ioctl()`, `virtio_gpu_getparam_ioctl()`, `virtio_gpu_resource_create_ioctl()`, transfer ioctls, `virtio_gpu_wait_ioctl()`, `virtio_gpu_get_caps_ioctl()`, `verify_blob()`, `virtio_gpu_resource_create_blob_ioctl()`, and `virtio_gpu_context_init_ioctl()`. The execbuffer ioctl is declared in `virtgpu_submit.c` but registered here.

## Control Flow
Getparam copies negotiated feature values to userspace. Resource create validates 2D-only constraints without virgl, allocates a fence, creates a host resource/GEM object, creates a handle, and returns resource/BO handles. Transfers look up object arrays, validate blob/stride rules, optionally create context and fences, enqueue host transfer commands, and notify. Get caps validates capset/version, reuses or fetches a cached capset, waits for response validity, then copies caps to userspace. Blob creation validates feature/flag/memory combinations, optionally submits host3D creation command data, creates guest or VRAM object, assigns UUID for cross-device use, and returns handles. Context init copies parameter array, validates capset/ring/mask/debug-name uniqueness, allocates fence contexts, creates the host context, and notifies.

## State and Persistence Behavior
The file mutates per-file `virtio_gpu_fpriv` context state, per-device capset cache, object/blob UUID state, and host resources. Userspace handles persist in DRM GEM tables; cap caches persist until release; submitted commands complete asynchronously through virtqueues/fences.

## Dependencies and Integration Points
It depends on UAPI `virtgpu_drm.h`, sync files, usercopy, DRM syncobj indirectly through submit, GEM objects, VirtIO GPU command helpers, response waitqueues, and feature flags initialized in KMS.

## Risks
Userspace input validation is extensive and security-sensitive: flags, sizes, capset IDs, ring masks, blob memory modes, and user pointers must be exact. `num_params * sizeof(...)` can overflow if type sizes change, though `num_params > 4` is checked after computing `len`. Resource creation error paths using `drm_gem_object_release()` need lifecycle scrutiny. Capset waits can time out and return `-EBUSY`.

## Test Signals
DRM ioctl fuzzing, getparam matrix tests, resource create invalid 2D/3D fields, blob flag/memory combinations, context-init duplicate and ring-mask cases, capset cache/timeouts, transfer stride/blob validation, and wait ioctl nowait/blocking behavior are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_kms.c

## Purpose
`virtgpu_kms.c` initializes and tears down per-device VirtIO GPU state, virtqueues, feature flags, host-visible memory, capsets, display info, workqueues, IDs, locks, KMS, and per-file virgl contexts.

## Important APIs, Types, and Functions
Public functions include `virtio_gpu_init()`, `virtio_gpu_deinit()`, `virtio_gpu_release()`, `virtio_gpu_driver_open()`, and `virtio_gpu_driver_postclose()`. Important helpers are `virtio_gpu_config_changed_work_func()`, `virtio_gpu_init_vq()`, `virtio_gpu_get_capsets()`, and `virtio_gpu_cleanup_cap_cache()`.

## Control Flow
Init requires VirtIO 1.0, allocates `virtio_gpu_device`, initializes locks/IDAs/waitqueues/works/fence driver/lists, records negotiated features, reserves host-visible shared memory and initializes `drm_mm` if present, finds control and cursor virtqueues, allocates vbuffers, reads scanout/capset counts, disables KMS if configured or no scanouts, initializes modeset, marks device ready, queries capsets, EDIDs, and display info, then returns. Deinit flushes works, resets the virtio device, and deletes vqs. Release frees KMS EDIDs, vbuffers, cap caches, and host-visible MM. Open allocates per-file virgl context IDs only when virgl is enabled; postclose destroys host context and frees the ID.

## State and Persistence Behavior
This file owns initialization of persistent `virtio_gpu_device` state: feature flags, queues, pending lists, capsets, display info, fence timeline, work items, host-visible allocator, and per-file contexts. Deinit stops transport; release cleans managed allocations after DRM references drain.

## Dependencies and Integration Points
It depends on virtio config/vqs/rings, DRM managed allocation, KMS display init, vbuffer allocation from `virtgpu_vq.c`, capset/display/EDID commands, dma-fence contexts, IDA, workqueues, and host-visible shared-memory regions.

## Risks
Error paths before/after vq creation must free the right subset. `capset_id_mask |= 1 << id` uses an int literal and should be reviewed for IDs near 63. Feature logging and KMS masking must match user-visible getparam behavior. Device reset during deinit must race safely with outstanding fences/works.

## Test Signals
Probe failure injection at each resource step, KMS disabled builds, host-visible region allocation conflicts, capset invalid ID/timeouts, display-info waits, open/postclose context lifecycle, and remove while commands are pending validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_object.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_object.c

## Purpose
`virtgpu_object.c` implements VirtIO GPU GEM object allocation, host resource ID allocation/freeing, shmem memory-entry construction, resource creation commands, detach waiting, and object cleanup/free callbacks.

## Important APIs, Types, and Functions
Key functions are `virtio_gpu_resource_id_get()`, `virtio_gpu_cleanup_object()`, `virtio_gpu_create_object()`, `virtio_gpu_object_create()`, `virtio_gpu_detach_object_fenced()`, and `virtio_gpu_is_shmem()`. It defines shmem GEM object funcs including free/open/close/export/pin/vmap/mmap operations.

## Control Flow
Resource IDs come either from a monotonic atomic workaround for old virglrenderer or from an IDA. Object creation rounds size to pages, creates a shmem GEM object, allocates a resource ID, builds virtio memory entries from the shmem sg table using DMA addresses or physical addresses depending on DMA quirk, optionally locks a one-object reservation for fenced creation, emits blob/3D/2D resource create and attach commands, and returns the object. Free emits unref for created host resources and defers actual cleanup to completion; otherwise it directly frees shmem/VRAM/private object state. Fenced detach emits detach, notifies, waits for the fence, and drops it.

## State and Persistence Behavior
`virtio_gpu_object` stores persistent host resource ID, attachment/created/blob/dumb flags, UUID state, and optional imported sg table. Resource IDs persist until cleanup. Host resource lifetime is asynchronous and tied to command completion.

## Dependencies and Integration Points
The file depends on DRM GEM shmem helpers, DMA mapping/scatterlist APIs, module parameter `virglhack`, VirtIO command emitters, VRAM helpers, PRIME export, GEM open/close context attach, and fence infrastructure.

## Risks
The virgl workaround intentionally leaks/reuses no IDs and can eventually wrap. `virtio_gpu_object_create()` does not free `ents` after successful command submission because ownership is expected to transfer to vq command buffers; that ownership must remain true. Fenced detach waits uninterruptibly. Error paths must release resource IDs and GEM objects exactly once.

## Test Signals
Tests should cover resource ID allocation with/without workaround, DMA-quirk and normal sg entry building, blob/virgl/2D creation, creation failure injection, object unref completion cleanup, detach waits, shmem versus VRAM cleanup, and mmap/vmap/export behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_plane.c

## Purpose
`virtgpu_plane.c` implements VirtIO GPU primary and cursor plane behavior, including format translation, atomic validation, damage-based uploads, scanout commands, cursor commands, imported dma-buf preparation, fences, and DRM panic scanout support.

## Important APIs, Types, and Functions
Public APIs are `virtio_gpu_translate_format()` and `virtio_gpu_plane_init()`. Important callbacks/helpers include plane state duplicate, `virtio_gpu_plane_atomic_check()`, dumb BO update helpers, resource flush helpers, `virtio_gpu_primary_plane_update()`, imported object prepare/cleanup, `virtio_gpu_plane_prepare_fb()`, `virtio_gpu_plane_cleanup_fb()`, `virtio_gpu_cursor_plane_update()`, `virtio_drm_get_scanout_buffer()`, and `virtio_panic_flush()`.

## Control Flow
Plane init allocates a managed universal plane with primary or cursor formats and helper funcs, enabling damage clips for primary planes. Atomic check disallows scaling and marks full update when framebuffer changes. Prepare_fb prepares GEM, allocates fences for dumb/imported/blob paths, and attaches imported dmabuf memory if needed. Primary update handles nofb scanout clearing, merges damage, uploads dumb BO damage to host, updates scanout when FB/source or CRTC modeset changed, and flushes the damaged rectangle. Cursor update uploads new dumb cursor contents synchronously, then sends update or move cursor command. Cleanup releases fences and unpins imported buffers.

## State and Persistence Behavior
Plane state embeds an optional VirtIO fence for the pending flush/upload. `virtio_gpu_output` stores cursor command state and `needs_modeset`. Host scanout state persists until another set_scanout or disable command. Imported buffers are pinned while in plane state.

## Dependencies and Integration Points
The file depends on DRM atomic/damage/GEM helpers, virtio-dma-buf import, DRM panic helpers, VirtIO GPU command helpers, PRIME import support, and object/fence arrays.

## Risks
`virtio_gpu_resource_flush()` ignores return from `virtio_gpu_array_lock_resv()`, which can lead to command emission without a locked reservation on failure. Imported-object attach/unpin lifetime is subtle with dma-buf dynamic attachments. Panic paths use atomic allocation/transport helpers and must remain minimal. Cursor upload waits synchronously and may stall atomic commits.

## Test Signals
KMS tests should cover damage clips, full update on FB change, dumb and blob scanout, cursor update/move/hotspot, imported dma-buf scanout and invalidation, panic screen flush, reservation-lock failure injection, and no-scaling validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_prime.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_prime.c

## Purpose
`virtgpu_prime.c` implements PRIME/dma-buf export and import for VirtIO GPU, including virtio-dma-buf UUID support, VRAM map hooks, dynamic import attachments, imported-object resource creation, and invalidation handling.

## Important APIs, Types, and Functions
Public functions are `virtio_gpu_resource_assign_uuid()`, `virtgpu_gem_prime_export()`, `virtgpu_dma_buf_import_sgt()`, `virtgpu_gem_prime_import()`, and `virtgpu_gem_prime_import_sg_table()`. Important internals include `virtgpu_virtio_get_uuid()`, dma-buf map/unmap ops, `virtgpu_dma_buf_unmap()`, `virtgpu_dma_buf_free_obj()`, `virtgpu_dma_buf_init_obj()`, and `virtgpu_dma_buf_move_notify()`.

## Control Flow
Export assigns a resource UUID for non-blob objects when supported, rejects UUID for non-cross-device blobs, then exports with `virtio_dma_buf_export()` and takes DRM/GEM refs. UUID queries wait until async assignment leaves initializing state. Import returns the original GEM object for same-device virtio dma-bufs, falls back to generic PRIME import without blob support, or creates a private imported object with the exported reservation object, dynamically attaches the dma-buf, pins/maps it, converts its sg table into virtio memory entries, creates a shareable guest blob resource, and unpins. Move notifications detach/unmap existing imported mappings.

## State and Persistence Behavior
Exported objects track `uuid_state` and `uuid`. Imported objects store the dma-buf reservation object, attachment, sg table, host resource ID, and guest-blob state. Imported mappings persist until invalidation/free or object cleanup.

## Dependencies and Integration Points
The file depends on DRM PRIME/dma-buf helpers, `virtio_dma_buf`, DMA reservation locking, VRAM map helpers, object create/detach commands, response waitqueue, and resource UUID command support.

## Risks
`virtgpu_gem_prime_import()` leaks the allocated object/attachment reference on `virtgpu_dma_buf_init_obj()` failure by returning `ERR_PTR(ret)` without local cleanup after init failure already calls free only for some paths; this should be reviewed. UUID wait can block indefinitely if host never responds. Dynamic import invalidation must hold the dma-resv lock as asserted. Cross-device sharing requires correct blob flags.

## Test Signals
Tests should cover same-device import, generic fallback without blob support, cross-device blob export, UUID success/failure/timeouts, imported dma-buf invalidation, VRAM export map/unmap, attachment cleanup failure injection, and dma-buf reservation locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_prime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_submit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_submit.c

## Purpose
`virtgpu_submit.c` implements `VIRTGPU_EXECBUFFER` submission parsing for virgl contexts, including command buffer copy, BO list lookup/locking, in-fence waits, syncobj timeline dependencies, out-fence fd creation, DRM fence events, command submission, and cleanup.

## Important APIs, Types, and Functions
The public function is `virtio_gpu_execbuffer_ioctl()`. Internal state is `struct virtio_gpu_submit` and `struct virtio_gpu_submit_post_dep`. Important helpers include `virtio_gpu_parse_deps()`, `virtio_gpu_parse_post_deps()`, `virtio_gpu_process_post_deps()`, `virtio_gpu_fence_event_create()`, `virtio_gpu_init_submit_buflist()`, `virtio_gpu_init_submit()`, `virtio_gpu_wait_in_fence()`, `virtio_gpu_lock_buflist()`, and cleanup/complete helpers.

## Control Flow
The ioctl requires virgl, validates flags and optional ring index against per-file context init, creates a context if needed, initializes submit state and optional out fence/event/fd, copies BO handles and command buffer from userspace, parses output syncobjs, waits and optionally records resettable input syncobjs, waits input fence fd, locks BO reservations, submits the command through `virtio_gpu_cmd_submit()`, notifies the host, installs the out fence fd, updates output syncobjs/timeline points, marks transferred ownership, and runs cleanup for remaining local references.

## State and Persistence Behavior
Submission state is transient. Host command execution and dma-fence completion persist asynchronously. Syncobjs are reset on cleanup after successful dependency parsing, and output syncobjs receive the submitted fence. Per-file ring fence contexts persist in `virtio_gpu_fpriv`.

## Dependencies and Integration Points
The file depends on DRM syncobj/timeline APIs, sync_file, dma-fence unwrap/wait, GEM object arrays from `virtgpu_gem.c`, command transport, UAPI execbuffer flags, and context/ring state initialized by context-init ioctl.

## Risks
Cleanup unconditionally resets parsed input syncobjs, so error ordering must match UAPI expectations. Out-fence allocation is conditional on several flags; callers expecting synchronization must request it or provide BO handles/syncobjs. Waiting foreign fences in ioctl can block. Ring-index event logic depends on `ring_idx_mask` semantics. User-provided strides are used with bounded copy but must remain validated by UAPI flag masks.

## Test Signals
Tests should cover invalid flags/rings, command copy faults, missing BO handles, reservation lock failures, in-fence fd waits, input syncobj reset behavior on success/failure, output syncobj timeline points, out-fence fd installation, DRM fence event delivery, and multi-ring submissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_submit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_trace.h

## Purpose
`virtgpu_trace.h` declares VirtIO GPU tracepoints for command queueing and command responses on virtqueues.

## Important APIs, Types, and Functions
It defines trace system `virtio_gpu`, an event class `virtio_gpu_cmd`, and events `virtio_gpu_cmd_queue` and `virtio_gpu_cmd_response`. Captured fields include virtio device index, virtqueue index/name, command type, flags, fence ID, context ID, free descriptor count, and vbuffer sequence number.

## Control Flow
Transport code includes this header and emits queue/response events around virtqueue operations. `virtgpu_trace_points.c` instantiates the tracepoints by defining `CREATE_TRACE_POINTS`.

## State and Persistence Behavior
Tracepoints do not own driver state. They expose snapshots of command headers and queue state to ftrace/perf consumers.

## Dependencies and Integration Points
The header depends on Linux tracepoint infrastructure, virtqueue and VirtIO GPU command header definitions from `virtgpu_drv.h`, and a relative `TRACE_INCLUDE_PATH` for generated trace code.

## Risks
Trace fields must remain safe to read at emit time. The relative include path is fragile if the source tree layout changes. Adding fields changes trace ABI expectations for tooling.

## Test Signals
Build with tracing enabled, enable both trace events during command submission, and verify decoded type/fence/context/queue fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_trace_points.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_trace_points.c

## Purpose
`virtgpu_trace_points.c` instantiates the VirtIO GPU tracepoints declared in `virtgpu_trace.h`.

## Important APIs, Types, and Functions
It includes `virtgpu_drv.h`, defines `CREATE_TRACE_POINTS`, and includes `virtgpu_trace.h`.

## Control Flow
During compilation, this single translation unit causes tracepoint storage and registration code to be generated. Other files include the trace header without defining storage.

## State and Persistence Behavior
Tracepoint registration state is generated by the kernel tracing infrastructure. This file has no driver-specific runtime state.

## Dependencies and Integration Points
It depends on the trace header and Kbuild object list including this file exactly once.

## Risks
If omitted from the Makefile, tracepoint references will not link. If another file also defines `CREATE_TRACE_POINTS` for the same header, duplicate definitions result.

## Test Signals
Kernel build/link with `CONFIG_TRACEPOINTS`, and runtime visibility of `virtio_gpu_cmd_queue` and `virtio_gpu_cmd_response` events, validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_trace_points.c -->
