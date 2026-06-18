# subset-b-003602 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vbt_defs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vbt_defs.h

### Purpose
`intel_vbt_defs.h` is the private packed-layout contract for parsing Intel Video BIOS Table (VBT) and BIOS Data Block (BDB) contents in `intel_bios.c`. It enumerates BDB block IDs and describes the byte-exact records for general features, child devices, display lists, panel data, backlight, power features, eDP, MIPI, compression, generic DTDs, and PRD data. The include guard deliberately rejects inclusion unless `_INTEL_BIOS_PRIVATE` is defined, keeping these firmware-facing structures local to BIOS parsing.

### Important APIs, Types, And Functions
There are no functions; the important ABI types are `struct vbt_header`, `struct bdb_header`, `enum bdb_block_id`, `struct child_device_config`, `struct bdb_general_definitions`, the LFP/eDP/MIPI/backlight/power structs, and `struct dsc_compression_parameters_entry`. Device-type, DVO-port, DP-AUX, DP-link-rate, eDP-link-rate, and DSC helper macros encode firmware values into symbolic constants. All externally consumed structures are `__packed`, and many use flexible arrays or version-annotated tail fields.

### Control Flow
Control flow lives in `intel_bios.c`; this header shapes that parser. Typical parsing reads the VBT header, follows `bdb_offset` to a BDB header, finds blocks by `enum bdb_block_id`, checks BDB version and block length, then casts byte ranges to these packed structs. Variable-size tables such as child device arrays, toggle lists, LFP pointer tables, DTD lists, and MIPI sequence data require parser-side length checks before field access.

### State, Persistence, And Dependencies
The data persists in firmware/OpRegion-provided VBT blobs and is copied into driver-owned `display->vbt` state by the parser. This header depends on Linux fixed-width integer types, bit helpers available through the driver include chain, and `intel_dsi_vbt_defs.h` for MIPI config/PPS definitions. The packed layout and version comments are the key persistence contract.

### Integration Points
`intel_bios.c` uses these definitions to discover connectors, DDC/AUX mapping, eDP link training and power sequencing, panel type, backlight method and limits, PSR/DRRS/VRR feature bits, compression capabilities, and generic timings. DSC parsing uses the compression block to seed slice and rate-control capability state consumed by `intel_vdsc.c`.

### Risks
The major risk is silent firmware-layout drift: adding or reading a field without BDB version and block-size gating can consume absent bytes or misinterpret obsolete meanings. Bitfields in packed firmware structs are compiler-layout-sensitive but established in this driver. Flexible array and zero-length array members must never be indexed without a validated count. Several constants have reused numeric IDs across BDB versions, so parser code must branch by version.

### Test Signals
Useful signals are VBT parser unit/fuzz tests with truncated blocks, old and new BDB versions, child device records of different sizes, eDP/DSC/backlight feature permutations, and real-machine boot logs confirming connector mapping, panel power sequencing, backlight ranges, and DSC capability discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vbt_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vdsc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vdsc.c

### Purpose
`intel_vdsc.c` implements Intel display-stream-compression source programming. It validates DSC availability, derives slice layout and PPS/rate-control parameters, writes PPS and RC registers for one or more VDSC engines, enables compressed or uncompressed joiner paths, emits DP/DSI PPS packets, reads hardware state back into `intel_crtc_state`, and contributes CDCLK/prefill constraints.

### Important APIs, Types, And Functions
Public entry points include `intel_dsc_source_support()`, `intel_dsc_get_slice_config()`, `intel_dsc_compute_params()`, `intel_dsc_enable_on_crtc()`, `intel_dsc_enabled_on_link()`, `intel_dsc_power_domain()`, `intel_dsc_get_num_vdsc_instances()`, `intel_dsc_dsi_pps_write()`, `intel_dsc_dp_pps_write()`, `intel_dsc_su_et_parameters_configure()`, `intel_uncompressed_joiner_enable()`, `intel_dsc_enable()`, `intel_dsc_disable()`, `intel_dsc_get_config()`, `intel_vdsc_state_dump()`, `intel_vdsc_min_cdclk()`, and `intel_vdsc_prefill_lines()`. Internal helpers compute RC tables, PPS register addresses, and DSS control register selection.

### Control Flow
Atomic check code first marks compression enabled and calls `intel_dsc_compute_params()`, which sets picture/slice dimensions, validates slice constraints, derives color format flags, chooses DSC 1.1/1.2 rate-control setup or local interpolation for Xe_LPD+, and computes mux/scale fields. Commit programming calls `intel_dsc_pps_configure()` to write PPS 0-10, 16, and MTL+ PPS 17/18, then writes RC threshold/range arrays to the proper pipe/transcoder engine registers. `intel_dsc_enable()` sets DSS bits for VDSC0/1/2, small joiner, bigjoiner, or ultrajoiner; disable clears DSS controls. Readback obtains the right power domain, reads DSS state, infers streams per pipe, verifies replicated PPS values, and reconstructs `drm_dsc_config`.

### State, Persistence, And Dependencies
Runtime state is held in `intel_crtc_state->dsc` and persisted to display engine MMIO registers for the active pipe/transcoder. Link-side PPS is persisted in DP SDP or DSI commands. Dependencies include DRM DSC helpers, fixed-point helpers, QP lookup tables, DP/DSI encoder helpers, power-domain helpers, `intel_de` MMIO accessors, and register definitions from `intel_vdsc_regs.h`.

### Integration Points
DP, eDP, DSI, MST, PSR selective update, bigjoiner/ultrajoiner, CDCLK calculation, state dump, and modeset readback all consume this module. `intel_bios.c` seeds slice capabilities from VBT, DP code writes PPS infoframes, DSI code sends MIPI compression mode, and PSR uses SU parameter programming.

### Risks
Slice layout is constrained by hardware engine count, joined-pipe topology, and format-specific DSC spec limits; mistakes can produce invalid PPS or underrun. PPS replication must target all active VDSC engines, including BMG DSC2. Native 4:2:0 doubles bpp internally and must be undone on readback. Power-domain selection differs for ICL eDP/DSI and Gen12 pipe A. Joiner and DSC enable sequencing is sensitive because DSS bits define pipe combining.

### Test Signals
High-value tests are modeset bring-up with single, dual, triple-engine and joined-pipe DSC; RGB, YCbCr444, and native 420; DP PPS SDP capture; DSI PPS command validation; suspend/resume readback; CDCLK minimum checks; PSR SU updates; and negative checks for invalid slice dimensions or unsupported pipe/transcoder combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vdsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vdsc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vdsc.h

### Purpose
`intel_vdsc.h` declares the display-stream-compression interface used by display modeset, DP/DSI encoders, PSR, state dump, and clock/prefill code. It hides the PPS/register implementation in `intel_vdsc.c` while exposing the state transitions needed by the wider i915 display stack.

### Important APIs, Types, And Functions
The header forward-declares `intel_crtc_state`, `intel_display`, `intel_encoder`, `intel_dsb`, `intel_dsc_slice_config`, and related types. It exports capability helpers, slice configuration helpers, enable/disable hooks, PPS writers for DSI and DP, PSR selective-update parameter programming, state dump, min-CDCLK and prefill calculations, and `intel_dsc_get_pixel_rate_with_dsc_bubbles()`.

### Control Flow
Callers use this header during three phases: atomic check computes slice/PPS parameters, commit enables DSC or uncompressed joiners and sends link PPS, and modeset readback reconstructs active DSC configuration. Clock and guardband code call the exported min-CDCLK and prefill helpers after compression state has been chosen.

### State, Persistence, And Dependencies
The header owns no state. Its API operates on caller-owned `intel_crtc_state` and hardware state programmed by the implementation. It depends only on `linux/types.h` plus forward declarations, keeping compile-time coupling low.

### Integration Points
Primary users are `intel_dp`, `intel_dp_mst`, `intel_dsi`, `intel_psr`, `intel_crtc_state_dump`, clock calculation, and modeset setup/readout. The interface is the boundary between encoder policy and low-level VDSC register programming.

### Risks
The API assumes callers have already populated `crtc_state->dsc` consistently before enabling. Calling link PPS writers without `compression_enable` is harmless but means no PPS is emitted. Slice count and VDSC instance helpers depend on `slice_config` having been computed or read back first.

### Test Signals
Compile coverage across DP, MST, DSI, PSR, and display dump paths is important. Runtime signals include successful DSC mode enable/disable, PPS packet emission, readback state matching the atomic state, and min-CDCLK changes when DSC is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vdsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vdsc_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vdsc_regs.h

### Purpose
`intel_vdsc_regs.h` defines the MMIO addresses and bitfield helpers for Intel VDSC, display stream splitter, joiner, PPS, RC threshold/range, and Lunar Lake selective-update parameter registers. It is the register contract consumed by `intel_vdsc.c` and related display code.

### Important APIs, Types, And Functions
The header defines `DSS_CTL1/2`, pipe-local `ICL_PIPE_DSS_CTL1/2`, joiner bits such as `BIG_JOINER_ENABLE`, `PRIMARY_BIG_JOINER_ENABLE`, `ULTRA_JOINER_ENABLE`, and VDSC engine enable bits. It also defines PPS register selectors (`DSCA_PPS`, `DSCC_PPS`, `ICL_DSC0_PPS`, `ICL_DSC1_PPS`, `BMG_DSC2_PPS`) and field macros for PPS 0-10, 16, 17, and 18. RC buffer threshold and range parameter register groups are declared for DSCA/DSCC and pipe-local ICL DSC engines.

### Control Flow
There is no executable flow. Callers compose register values with `REG_FIELD_PREP()` macros and select address families based on whether DSC is pipe-local or transcoder/shared. The PPS macros encode the register spacing where PPS indices after 11 have gaps on DSCA/DSCC but not pipe-local ICL/BMG engines.

### State, Persistence, And Dependencies
State persists in hardware registers. This header depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PIPE`, `_PICK_EVEN`, `REG_BIT`, and `REG_GENMASK`. It does not store driver state.

### Integration Points
`intel_vdsc.c` uses these definitions to program PPS, RC thresholds, RC ranges, DSS joiner controls, and PSR SU DSC parameters. Joiner bits interact with bigjoiner/ultrajoiner pipe composition and uncompressed joiner support.

### Risks
Incorrect address selection can program the wrong engine, especially around pipe B/C offsets and BMG DSC2. Field-width errors in PPS macros can truncate DSC parameters. The DSCA/DSCC PPS index gap is easy to overlook. Joiner bit combinations must stay synchronized with `intel_vdsc.c` topology logic.

### Test Signals
Register write traces, display engine register dumps, DSC PPS readback comparisons, multi-engine DSC bring-up, and BMG/MTL/LNL platform coverage are useful. Static build coverage catches macro name drift but not wrong offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vdsc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vga.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vga.c

### Purpose
`intel_vga.c` handles legacy VGA resource ownership and disables the unused VGA plane during display initialization. It coordinates PCI VGA IO decode, bridge VGA routing, vgaarb registration, MMIO-vs-IO access paths, and the `VGACNTRL`/`CPU_VGACNTRL` state needed to prevent legacy VGA decode from interfering with KMS.

### Important APIs, Types, And Functions
Public APIs are `intel_vga_read()`, `intel_vga_disable()`, `intel_vga_register()`, and `intel_vga_unregister()`. Internal helpers select GMCH/VGA control registers, detect VGA decode, check MMIO access support, manipulate PCI command IO decode, manipulate bridge VGA control on dGPUs, and provide acquire/release wrappers around VGA legacy IO.

### Control Flow
`intel_vga_disable()` first checks GMCH-level decode and current VGA plane state. If cleanup is needed, it temporarily enables legacy IO decode or acquires vgaarb resources, turns off VGA sequencer screen output, disables VGA memory access, forces MDA decode for CGA/MDA consistency, releases resources, informs vgaarb on iGPUs, delays for hardware settling, then writes `VGA_DISP_DISABLE`. `intel_vga_set_decode()` is the vgaarb callback that enables or disables legacy VGA decode using bridge control on dGPUs or PCI IO decode on iGPUs.

### State, Persistence, And Dependencies
State persists in PCI config space, bridge control, legacy VGA registers, vgaarb bookkeeping, and display MMIO VGA control registers. Dependencies include Linux PCI, delay, vgaarb, VGA port definitions, DRM logging, `intel_de`, and `intel_vga_regs.h`.

### Integration Points
Display driver load registers with vgaarb, modeset setup disables the VGA plane, CRT load-detect paths can read VGA status via `intel_vga_read()`, and unload unregisters the VGA client. The code is especially relevant when the iGPU coexists with an external VGA-capable GPU.

### Risks
Legacy IO decode is fragile on multi-GPU systems: enabling the iGPU can steal VGA IO cycles from a current external VGA owner, while disabling IO too early can hang some reboot paths. dGPU bridge routing must not be altered incorrectly. Older platforms need `VGA_DISP_DISABLE` set even when decode is already disabled to avoid a stuck pipe. MDA/CGA decode synchronization prevents NoClaim errors after power-well resets.

### Test Signals
Useful coverage includes booting with vgacon, UEFI boots where BIOS left VGA registers dirty, hybrid iGPU+dGPU VGA arbitration, suspend/resume power-well reset, reboot/shutdown on older laptops, and register dumps showing `VGA_DISP_DISABLE` set with VGA memory decode disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vga.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vga.h

### Purpose
`intel_vga.h` declares the small legacy VGA management interface for the i915 display driver. It exposes VGA byte reads, VGA plane disable, and vgaarb client lifecycle hooks.

### Important APIs, Types, And Functions
The exported functions are `intel_vga_read(struct intel_display *, u16 reg, bool mmio)`, `intel_vga_reset_io_mem(struct intel_display *)`, `intel_vga_disable(struct intel_display *)`, `intel_vga_register(struct intel_display *)`, and `intel_vga_unregister(struct intel_display *)`. This source snapshot declares `intel_vga_reset_io_mem()` even though the implementation in the listed `intel_vga.c` is not present, so consumers or other build variants must supply or drop it.

### Control Flow
Initialization code registers the VGA client and later disables the VGA plane. Runtime users can read legacy VGA registers through either MMIO or port IO depending on platform support. Driver unload unregisters from VGA arbitration.

### State, Persistence, And Dependencies
The header owns no state and depends only on `linux/types.h` and an `intel_display` forward declaration. State changes occur in the implementation via PCI config, vgaarb, VGA ports, and display MMIO.

### Integration Points
Used by display driver initialization/uninitialization, modeset setup, and CRT/VGA-related helpers. It forms the compile-time boundary between general display code and legacy VGA handling.

### Risks
The declared-but-not-implemented `intel_vga_reset_io_mem()` is a build/link risk if referenced. Callers must pass the correct `mmio` mode to `intel_vga_read()` or they may hit the wrong access path. VGA functions should be invoked during controlled modeset/init paths because they manipulate global legacy decode.

### Test Signals
Build linkage, driver probe/remove, VGA arbitration logs, and legacy register reads on pre-GEN5 versus newer platforms are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vga_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vga_regs.h

### Purpose
`intel_vga_regs.h` defines display MMIO register addresses and bitfields for the legacy VGA control register variants used by i915 display platforms.

### Important APIs, Types, And Functions
The key register macros are `VGACNTRL`, `VLV_VGACNTRL`, and `CPU_VGACNTRL`. Bitfields include `VGA_DISP_DISABLE`, pre-ILK `VGA_2X_MODE`, pipe selection masks for pre-IVB and CHV, border/CSC/centering/palette controls, legacy 8-bit palette enable, nine-dot disable, and active/blank throttling fields.

### Control Flow
There is no executable flow. `intel_vga.c` selects the platform-specific control register and uses these fields to detect and disable the legacy VGA plane.

### State, Persistence, And Dependencies
The state is hardware MMIO. The header depends on `intel_display_reg_defs.h` for MMIO and bitfield helpers.

### Integration Points
Integrated primarily with `intel_vga_disable()` and any display readback/debug paths that inspect VGA control. Platform conditionals in `intel_vga.c` determine which register and pipe-selection masks apply.

### Risks
Using the wrong pipe-selection mask on CHV or older platforms can misreport the active VGA pipe. Clearing or preserving unrelated bits incorrectly could disturb palette/CSC/centering state, though the current disable path writes only `VGA_DISP_DISABLE`.

### Test Signals
Register dumps before and after `intel_vga_disable()`, platform-specific boot logs for pre-ILK, VLV/CHV, and CPU transcoder platforms, and absence of stuck-pipe behavior on older hardware are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vga_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vrr.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vrr.c

### Purpose
`intel_vrr.c` implements Intel Variable Refresh Rate, fixed-refresh use of the VRR timing generator, dormant CMRR support, VRR guardband computation, DSB push sequencing, PSR frame-change integration, DC-balance firmware programming, and hardware state readback.

### Important APIs, Types, And Functions
Public APIs include capability/range checks, `intel_vrr_compute_config()`, `intel_vrr_compute_guardband()`, timing accessors, fixed-RR programming, transcoder timing enable/disable, VRR enable/disable, push send/check helpers, DC-balance reset/increment helpers, readback, safe-window helpers, and DCB live/final vblank-start helpers. Internal helpers compute vmin/vmax, guardband limits, optimized prefill-based guardband, hardware-adjusted vmin/vmax/flipline, and DCB parameter sets.

### Control Flow
Atomic check first verifies connector and mode eligibility: DP/eDP only, no MST, Ignore MSA DPCD support, monitor range > 10 Hz, no interlace, and VBT VRR bit for eDP. It computes `vmin` from current vtotal and `vmax` from minimum monitor refresh, enables true VRR only when userspace requested it and range permits, otherwise programs fixed refresh through the same timing registers. Guardband computation uses prefill worst-case latency plus PSR/SDP/ALPM minima, capped by hardware and vblank limits. Commit writes transcoder timing registers after `TRANS_DDI_FUNC_CTL`, arms push support, writes AS SDP timing, enables DCB when configured, and enables/disables the VRR timing generator depending on platform generation.

### State, Persistence, And Dependencies
State lives in `intel_crtc_state->vrr`, `->cmrr`, mode flags, live `intel_crtc->dc_balance.flip_count`, and MMIO registers such as `TRANS_VRR_CTL`, `TRANS_VRR_VMIN/VMAX/FLIPLINE`, `TRANS_PUSH`, DCB registers, and CMRR M/N registers. Dependencies include DP DPCD helpers, PSR, ALPM, DMC/PIPEDMC, DSB, vblank timing, watermark latency, prefill, and `intel_vrr_regs.h`.

### Integration Points
The module is called from DP/MST modeset compute and enable paths, vblank timestamp/window logic, DSB waits, color commits, PSR frame change handling, state dumps, and DMC DC-balance event configuration. `skl_prefill` and watermark data feed optimized guardband selection.

### Risks
VRR timing is extremely sequencing-sensitive: programming before the transcoder is ready can hang ICL, push-send must clear before delayed vblank assumptions are used, and Gen12/13 chicken bits have platform-specific meanings. Guardband must not exceed vblank space or hardware field width. Always-use-VRR-TG platforms overwrite adjusted vblank timing, so readback must reconstruct mode values carefully. DC-balance is limited to PIPE A/B and depends on firmware/DMC behavior. CMRR is compiled but intentionally disabled by an unconditional false path.

### Test Signals
Signals include DP/eDP VRR enablement, fixed-RR fallback, vblank timestamp correctness at min/max refresh, DSB/color update push completion, PSR coexistence, DC-balance register programming on supported pipes, suspend/resume readback, and negative tests for MST/interlace/unsupported DPCD/monitor-range cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vrr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vrr.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vrr.h

### Purpose
`intel_vrr.h` declares the VRR interface shared by connector capability checks, atomic modeset computation, transcoder programming, DSB update paths, PSR integration, vblank timing code, and state readback.

### Important APIs, Types, And Functions
The header exports capability/range helpers, atomic modeset change detection, configuration/guardband computation, hardware timing programming, enable/disable hooks, DSB push send/check, DC-balance helpers, fixed-RR detection/programming, readback, safe-window timing, and DCB vblank-start query helpers.

### Control Flow
Callers use these APIs in order: check connector/mode capability, compute VRR state during atomic check, compute guardband after other timing/prefill inputs are known, program transcoder timing, enable VRR/DCB during commit, send pushes for latency-sensitive updates, and read back state during modeset setup or verification.

### State, Persistence, And Dependencies
The header owns no state. It operates on `intel_crtc_state`, `intel_connector`, `intel_atomic_state`, `intel_dsb`, and `intel_display` objects whose state is persisted by `intel_vrr.c` into transcoder and DMC registers. Dependency footprint is intentionally small: `linux/types.h` plus forward declarations.

### Integration Points
Users include DP/MST, vblank, DSB, color, PSR, display state dump, and modeset readout. The safe-window and DCB helpers are especially tied to DSB/vblank scheduling.

### Risks
APIs such as `intel_vrr_vmin_vblank_start()` assume `crtc_state->vrr.guardband` has already been computed. Push helpers must be used only where delayed vblank ordering is respected. DCB helpers require hardware support and a valid live VRR configuration.

### Test Signals
Build coverage across all display modules, VRR atomic transitions setting mode-changed, vblank helper correctness, DSB push polling, PSR frame-change programming, and readback matching programmed fixed-RR/VRR state are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vrr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vrr_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vrr_regs.h

### Purpose
`intel_vrr_regs.h` defines MMIO addresses and bitfields for VRR timing generator control, status, push, Adaptive Sync SDP timing, CMRR, and DC-balance adjustment/live registers.

### Important APIs, Types, And Functions
Key macros include `TRANS_VRR_CTL`, `TRANS_VRR_VMAX`, `TRANS_VRR_VMIN`, `TRANS_VRR_FLIPLINE`, `TRANS_VRR_STATUS`, `TRANS_PUSH`, `TRANS_VRR_VSYNC`, `EMP_AS_SDP_TL`, CMRR M/N register selectors, and DCB config/live selectors for adjusted flipline/vmax and final flipline/vmax. Bit helpers cover VRR enable, flipline enable, CMRR enable, DCB adjustment enable, pipeline-full or Xe_LPD guardband fields, status FSM bits, push send/enable bits, and AS SDP line fields.

### Control Flow
There is no executable flow. `intel_vrr.c` uses these macros to compose timing-control values, poll status, send push commands, program AS SDP positions, and read live DCB adjustment registers.

### State, Persistence, And Dependencies
State persists in transcoder MMIO and DCB live/config register blocks. The header depends on `intel_display_reg_defs.h` for transcoder MMIO selection and bitfield macros.

### Integration Points
Integrated with VRR enable/disable, DSB push scheduling, vblank safe-window logic, PSR frame-change pushes, DMC DC-balance support, and CMRR read/write code.

### Risks
Transcoder register selection must match the active CPU transcoder. Several fields are 13-, 16-, or 20-bit line counters; invalid values can truncate timings. Live DCB registers use different offsets from config registers, and mixing them would break vblank scheduling. Platform-specific interpretation of `VRR_CTL` fields is handled outside this header and must stay aligned.

### Test Signals
MMIO traces during VRR enable/disable, status polling on disable, DSB push-send clearing, AS SDP timing validation, DCB live-register readback, and platform coverage from Gen12 through newer always-VRR-TG platforms are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vrr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_wm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_wm.c

### Purpose
`intel_wm.c` is the generic dispatch and debugfs layer for display FIFO watermark management. It delegates platform-specific watermark computation/programming to `display->funcs.wm`, initializes the correct implementation family, defines common visibility policy, formats latency values, and exposes latency override files in debugfs.

### Important APIs, Types, And Functions
Public wrappers include `intel_update_watermarks()`, `intel_wm_compute()`, `intel_initial_watermarks()`, `intel_atomic_update_watermarks()`, `intel_optimize_watermarks()`, `intel_compute_global_watermarks()`, `intel_wm_get_hw_state()`, `intel_wm_sanitize()`, `intel_wm_plane_visible()`, `intel_print_wm_latency()`, `intel_wm_init()`, and `intel_wm_debugfs_register()`. Debugfs helpers show/write primary, sprite, and cursor latency arrays.

### Control Flow
Most functions check whether a function pointer exists and call it, returning success or false when unsupported. Initialization selects `skl_wm_init()` for display version 9+ and `i9xx_wm_init()` otherwise. `intel_wm_plane_visible()` treats inactive CRTCs as invisible and cursor planes with a framebuffer as visible regardless of `uapi.visible`. Debugfs open methods reject unsupported platform families; reads format units by generation, and writes parse exactly `num_levels` 16-bit latency values under the global modeset lock.

### State, Persistence, And Dependencies
Watermark state is stored in `display->wm`, platform watermark state, and hardware registers owned by implementation backends. Debugfs writes mutate latency arrays in memory and influence later computations. Dependencies include debugfs, DRM logging, i9xx and SKL watermark backends, display core/types, and modeset locking.

### Integration Points
Atomic check/commit paths use compute/update/optimize wrappers. Modeset setup reads/sanitizes hardware state. Display debugfs registration calls `intel_wm_debugfs_register()`, which also delegates to `skl_watermark_debugfs_register()`. VRR optimized guardband uses watermark max-latency data from the SKL backend.

### Risks
Function-pointer dispatch means missing backend hooks silently become no-ops, which is intentional but can hide incomplete platform enablement. Cursor visibility is conservative because frequent cursor updates can outrun watermark logic. Debugfs latency writes can destabilize watermark calculations and are protected only by modeset locking and input count validation.

### Test Signals
Signals include atomic watermark compute/update success on old and Gen9+ platforms, debugfs latency read/write with correct unit formatting, cursor plane update stress, modeset sanitize after firmware state, and underrun-free display operation after latency overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_wm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_wm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_wm.h

### Purpose
`intel_wm.h` declares the common display watermark API used by atomic modeset, driver initialization, modeset setup/readback, plane visibility checks, debug logging, and debugfs registration.

### Important APIs, Types, And Functions
It exports compute, initial, atomic update, optimize, global compute, hardware readback, sanitize, plane visibility, latency printing, initialization, and debugfs registration functions. It forward-declares the core display, CRTC, atomic, CRTC state, and plane state types.

### Control Flow
The header supports the lifecycle implemented in `intel_wm.c`: initialize backend, compute during atomic check, program initial/intermediate/optimized watermarks during commit, read and sanitize on setup, then expose debugfs hooks.

### State, Persistence, And Dependencies
No state is stored in the header. State flows through `intel_display`, `intel_atomic_state`, `intel_crtc`, and plane/CRTC state objects into backend-specific hardware programming. Dependency footprint is limited to Linux types and forward declarations.

### Integration Points
Used by display driver init, modeset setup, atomic commit, plane checks, debugfs, and platform-specific watermark implementations such as i9xx and SKL.

### Risks
Callers must respect backend availability and ordering; e.g. compute before update, sanitize after readback. `intel_wm_plane_visible()` policy should be used consistently by backends to avoid cursor underruns or unnecessary watermarks.

### Test Signals
Build coverage across platform watermark backends and runtime atomic commit paths, plus debugfs and modeset setup tests, validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_wm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_wm_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_wm_types.h

### Purpose
`intel_wm_types.h` defines shared data structures for legacy and SKL-era watermark state, including per-pipe FIFO watermarks, self-refresh watermarks, Valleyview DDL values, and SKL display data buffer entries.

### Important APIs, Types, And Functions
Key types are `enum intel_ddb_partitioning`, `struct ilk_wm_values`, `struct g4x_pipe_wm`, `struct g4x_sr_wm`, `struct vlv_wm_ddl_values`, `struct vlv_wm_values`, `struct g4x_wm_values`, and `struct skl_ddb_entry`. Inline helpers `skl_ddb_entry_size()` and `skl_ddb_entry_equal()` compute DDB block count and equality.

### Control Flow
There is no runtime control flow beyond the inline helpers. Platform watermark code fills these structs during compute/readback and compares/applies them during commit.

### State, Persistence, And Dependencies
Instances of these types are the in-memory representation of hardware watermark and DDB state. The header depends on `intel_display_limits.h` for `I915_MAX_PLANES` and Linux integer types.

### Integration Points
Legacy i9xx/G4x/ILK/VLV watermark backends and SKL watermark code use these structures to stage hardware values. The DDB helpers are shared wherever SKL data-buffer allocations are compared or sized.

### Risks
Array dimensions must match platform pipe/plane limits. `skl_ddb_entry_size()` assumes `end` is exclusive and greater than or equal to `start`; invalid entries can underflow because fields are unsigned. Equality compares only start/end, so callers must compare any associated metadata separately.

### Test Signals
Watermark readback/commit tests, DDB allocation verification, underrun tests under plane changes, and assertions around empty or invalid DDB entries are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_wm_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_prefill.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_prefill.c

### Purpose
`skl_prefill.c` computes display pipe prefill requirements in fixed-point scanlines. It combines fixed frame-start and memory-translation costs with watermark, scaler, DSC, and CDCLK adjustment factors to determine whether vblank is long enough, how much VRR guardband is needed, and what minimum CDCLK is required for prefill.

### Important APIs, Types, And Functions
Public functions are `skl_prefill_init_worst()`, `skl_prefill_init()`, `skl_prefill_vblank_too_short()`, `skl_prefill_min_guardband()`, and `skl_prefill_min_cdclk()`. Internal helpers convert microseconds to `.16` scanlines, initialize fixed components, combine no-CDCLK/scaler/CDCLK stages, and apply `.16` adjustment factors.

### Control Flow
Initialization zeros the context, adds frame-start delay and a fixed 20 us translation-walk cost, then adds DSC prefill. The normal path pulls live WM0/scaler prefill and CDCLK adjustment helpers; the worst path pulls maximum/worst versions for guardband planning. Prefill composition applies second-scaler adjustment, second-scaler lines, first-scaler adjustment, first-scaler lines, WM0, then CDCLK adjustment, and finally fixed overhead. Query functions add caller-specified latency, compare against vblank length, round guardband to whole lines, or ask CDCLK code for a frequency that fits the available prefill window.

### State, Persistence, And Dependencies
State is caller-owned `struct skl_prefill_ctx`, holding `.16` line counts and adjustment factors. No hardware state is written here. Dependencies include CDCLK helpers, display modes, vblank length, VDSC prefill, scaler prefill helpers, and watermark prefill helpers.

### Integration Points
VRR optimized guardband uses `skl_prefill_init_worst()` and `skl_prefill_min_guardband()`. CDCLK and watermark calculations can use the normal context to detect too-short vblank or derive minimum CDCLK. DSC and scaler modules contribute prefill components through their exported helpers.

### Risks
All arithmetic is fixed-point `.16`; mixing raw lines and fixed-point values would skew guardbands. `skl_prefill_min_cdclk()` subtracts fixed overhead from vblank-derived availability, so callers must avoid using it when vblank is shorter than fixed cost. Current constants include a hardcoded 20 us translation cost and simplistic scaler/DSC inputs.

### Test Signals
Useful tests compare guardband/min-CDCLK results across modes, CDCLK changes, watermark latency changes, active scalers, DSC on/off, and VRR guardband limits. Boundary tests should cover very short vblank and high-latency SAGV/package-C states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_prefill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_prefill.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_prefill.h

### Purpose
`skl_prefill.h` declares the fixed-point prefill context and APIs used to estimate display pipeline prefill latency, guardband needs, and minimum CDCLK.

### Important APIs, Types, And Functions
`struct skl_prefill_ctx` stores `.16` scanline prefill components (`fixed`, `wm0`, `scaler_1st`, `scaler_2nd`, `dsc`, `full`) and `.16` adjustment factors (`cdclk`, `scaler_1st`, `scaler_2nd`). The public APIs initialize normal or worst-case contexts, check vblank sufficiency, compute minimum guardband, and compute minimum CDCLK.

### Control Flow
Callers initialize a context from an `intel_crtc_state`, then pass it with a latency value to guardband/vblank checks or to the CDCLK helper. Worst-case initialization is used when scaler assignment or latency may not yet be finalized.

### State, Persistence, And Dependencies
The context is transient stack/caller state; it is not persisted. The header depends only on Linux types and an `intel_crtc_state` forward declaration.

### Integration Points
Used by VRR guardband computation and CDCLK/watermark paths that need a shared prefill estimate. Its structure is filled by `skl_prefill.c` using VDSC, scaler, watermark, and CDCLK modules.

### Risks
Fields are fixed-point scanlines and factors, not raw integers; external callers should treat the struct as produced by the init functions. Adding new pipeline stages requires updating both normal and worst-case initialization.

### Test Signals
Compile coverage for VRR/CDCLK users and runtime checks showing guardband/min-CDCLK changes when watermarks, scalers, DSC, or CDCLK constraints change are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_prefill.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_scaler.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_scaler.c

### Purpose
`skl_scaler.c` manages Skylake-style pipe scalers for CRTC panel fitting, plane scaling, YUV planar conversion/upsampling, CASF, scaling filters, hardware detach/readback, ECC workaround masking, and prefill/downscale limits.

### Important APIs, Types, And Functions
Public APIs include `skl_scaler_mode_valid()`, `skl_update_scaler_crtc()`, `skl_update_scaler_plane()`, `intel_atomic_setup_scalers()`, `skl_scaler_setup_casf()`, `skl_pfit_enable()`, `skl_program_plane_scaler()`, `skl_detach_scalers()`, `skl_scaler_disable()`, `skl_scaler_get_config()`, `adl_scaler_ecc_mask()`, `adl_scaler_ecc_unmask()`, and scaler prefill/max-scale helpers. Internal helpers calculate phases, source/destination size limits, allocate scaler IDs, choose scaler mode, validate scale factors, and program nearest-neighbor coefficients.

### Control Flow
Atomic plane/CRTC check calls `skl_update_scaler_*()` to stage users in `crtc_state->scaler_state.scaler_users` after checking interlace, source/destination limits, pipe source limits, and whether scaling or planar YUV requires a scaler. `intel_atomic_setup_scalers()` counts users, ensures enough hardware scalers, includes planes not otherwise in the transaction when necessary, allocates scaler IDs, chooses modes such as NV12, planar, normal, HQ, dynamic, or CASF-specific scaler 1, and validates h/v scale factors. Commit programming binds a scaler to the pipe or plane, programs phase/window/size/filter registers, or detaches unused scalers. Readback finds pipe-bound scalers and reconstructs pfit/CASF state.

### State, Persistence, And Dependencies
Staged state lives in `intel_crtc_scaler_state`, `intel_scaler`, per-plane `scaler_id`, and `pch_pfit`/CASF state. Persistent state is the `SKL_PS_*` MMIO register set and GLK coefficient tables. Dependencies include CASF, display register definitions, tracepoints, workarounds, framebuffer format helpers, universal plane state, DSB writes, and DRM rectangle scaling helpers.

### Integration Points
Plane check/commit, CRTC panel fitting, CASF sharpness, display readback, ADL scaler ECC workaround paths, VRR/CDCLK prefill calculations, and mode validation for YCbCr420 use this module. `skl_prefill.c` consumes scaler prefill/max-scale helpers.

### Risks
Scaler allocation is a shared scarce resource; stale `scaler_id` or missing existing-plane state can overcommit hardware. Platform limits vary by display version and scaler ID, especially display version 14 where only scaler 0 supports vertical downscale above 1.0. Planar YUV phase and binding must match linked planes. Nearest-neighbor coefficient programming is GLK-style and assumes coefficient table layout. Several max-scale/prefill helpers contain FIXME approximations, so guardband/CDCLK estimates may be conservative or incomplete.

### Test Signals
Useful tests cover simultaneous plane scaling and pfit, CASF needing scaler 1, NV12/planar formats, nearest-neighbor filter programming, downscale limit rejection by platform/scaler ID, scaler detach after plane disable, readback of pfit/CASF state, ADL ECC mask/unmask, and underrun-free operation with VRR prefill.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_scaler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_scaler.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_scaler.h

### Purpose
`skl_scaler.h` declares the public interface for SKL-style pipe scaler staging, atomic setup, programming, disable/readback, CASF setup, mode validation, ECC workaround hooks, and prefill/max-scale estimates.

### Important APIs, Types, And Functions
The header exports scaler update functions for CRTC and plane users, `intel_atomic_setup_scalers()`, programming functions for pfit and plane scalers, detach/disable/readback functions, CASF setup, mode validation, ADL ECC mask/unmask, max-scale queries, and normal/worst-case scaler prefill helpers.

### Control Flow
Callers stage scaler requirements during plane/CRTC atomic checks, call `intel_atomic_setup_scalers()` during CRTC check to allocate IDs and validate scale factors, then program or detach scalers during commit. Readback fills scaler state during modeset setup. Prefill helpers are queried by prefill/VRR logic after scaler use is known or in worst-case mode.

### State, Persistence, And Dependencies
The header owns no state and relies on forward declarations for display, CRTC, plane, atomic, DSB, and mode types. State is held in `intel_crtc_state` and `intel_plane_state`, then persisted by the implementation to scaler MMIO.

### Integration Points
Used by universal plane code, CRTC atomic checks, panel fitter code, CASF, display readback, workarounds, and prefill/VRR calculations.

### Risks
Consumers must preserve the staging/setup/programming ordering; programming with an unallocated `scaler_id` is invalid. Prefill helpers are estimates and should not be treated as exact hardware timing unless implementation improves the FIXME paths.

### Test Signals
Build coverage plus runtime scaling tests for plane and pipe users, CASF, scaler detach/readback, and prefill-driven guardband/CDCLK behavior validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_scaler.h -->
