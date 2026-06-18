# subset-b-003749 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_tcon_top.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_tcon_top.c

## Purpose

`sun8i_tcon_top.c` implements the Allwinner TCON TOP component driver used by the sun4i DRM stack. The block routes display-engine mixers to TCON outputs, selects HDMI's TCON source, gates TCON-TV/DSI clocks, handles reset and bus-clock lifetime, and exports helper symbols used by other sun4i display components.

## Important APIs, Types, and Functions

- `struct sun8i_tcon_top_quirks`: per-compatible feature flags for a second TCON-TV gate and DSI gate.
- `sun8i_tcon_top_set_hdmi_src(struct device *dev, int tcon)`: exported helper that selects HDMI source TCON 2 or TCON 3 via `TCON_TOP_GATE_SRC_REG`.
- `sun8i_tcon_top_de_config(struct device *dev, int mixer, int tcon)`: exported helper that routes display engine mixer 0/1 to a selected TCON output using `TCON_TOP_PORT_SEL_REG`.
- `sun8i_tcon_top_register_gate(...)`: creates clock gate hardware from DT parent and output names.
- `sun8i_tcon_top_bind()` / `sun8i_tcon_top_unbind()`: component lifecycle hooks that allocate state, deassert reset, enable bus clock, clear routing registers, register gate clocks, and publish the clock provider.
- `sun8i_tcon_top_of_table`: exported OF match table used by the driver and by `sun4i_drv` to identify TCON TOP nodes.

## Control Flow

Probe only registers a component. During component bind, the driver obtains SoC quirks from OF match data, allocates `struct sun8i_tcon_top` and `clk_hw_onecell_data`, initializes the shared register spinlock, acquires reset and bus clock resources, maps MMIO, deasserts reset, enables the bus clock, and clears the port-selection and gate/source registers. It then registers clock gates for `tcon-tv0`, optional `tcon-tv1`, and optional `dsi`, validates all gate handles, adds an OF clock provider, and stores driver data.

The exported routing helpers first verify that `dev->of_node` matches the TCON TOP table and that caller-provided indices are in range. They then take `reg_lock`, perform read-modify-write updates to shared routing/source registers, and release the lock. Unbind unregisters the clock provider and gates, disables the bus clock, and asserts reset.

## State and Persistence Behavior

Persistent state is device-managed except for registered clocks that are explicitly unregistered on error and unbind. Hardware state persists in TCON TOP MMIO registers until reprogrammed or reset. `reg_lock` serializes access to registers shared between gate clocks and routing helpers. The bind path intentionally clears registers that may have non-zero firmware/reset defaults.

## Dependencies and Integration Points

This file depends on Linux component, platform, reset, clock, OF, OF graph, bitfield, and MMIO helpers. It integrates with the Allwinner DT binding `dt-bindings/clock/sun8i-tcon-top.h`, the common sun4i DRM component graph, and other display blocks that call `sun8i_tcon_top_de_config()` or `sun8i_tcon_top_set_hdmi_src()`. The clock output names and parent names must match DT properties.

## Risks and Edge Cases

- The exported helpers assume `dev_get_drvdata(dev)` is initialized; calling them before bind or after unbind would dereference invalid state.
- `mixer` is only checked for `> 1`; negative values are not rejected but are unlikely through normal unsigned-like caller paths.
- `tcon` validation allows values 0..3 for mixer routing but only 2..3 for HDMI source; mismatched caller assumptions can produce `-EINVAL`.
- Gate registration relies on ordered `clock-output-names`; missing or reordered names fail bind.
- Error unwind unregisters only non-error gate pointers and reasserts reset, but any future non-devm resources need matching unwind additions.

## Test Signals

Build coverage should include all three compatibles. DT integration tests should verify required clock names, output names, reset, and MMIO resources. Runtime tests should exercise mixer-to-TCON routing, HDMI source selection, optional DSI/TCON-TV1 clocks, bind error unwind, and unbind cleanup. Lockdep or stress tests should verify concurrent gate enable/disable and routing updates do not race.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_tcon_top.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_tcon_top.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_tcon_top.h

## Purpose

`sun8i_tcon_top.h` defines the TCON TOP register layout, bit masks, runtime state, OF match export, and public routing helpers for Allwinner TCON TOP support.

## Important APIs, Types, and Definitions

- Register offsets: `TCON_TOP_TCON_TV_SETUP_REG`, `TCON_TOP_PORT_SEL_REG`, and `TCON_TOP_GATE_SRC_REG`.
- Field masks and bits: DE0/DE1 port masks, HDMI source mask, and TCON-TV0/TCON-TV1/DSI gate bit positions.
- `CLK_NUM`: fixed onecell clock count of three possible clock outputs.
- `struct sun8i_tcon_top`: stores bus clock, onecell clock data, MMIO base, reset control, and `reg_lock`.
- `sun8i_tcon_top_of_table`: shared OF match table.
- `sun8i_tcon_top_set_hdmi_src()` and `sun8i_tcon_top_de_config()`: exported cross-module control functions.

## Control Flow and State

The header is consumed by the TCON TOP driver and other sun4i display components. It establishes that all register access goes through a `struct sun8i_tcon_top` instance and that shared register updates are protected by `reg_lock`. It does not own resources directly but defines the persistent state allocated by the C file.

## Dependencies and Integration Points

It requires Linux clock-provider, reset, and spinlock declarations, and it expects bit macros such as `GENMASK()` and `BIT()` to be available through included kernel headers. It integrates with TCON TOP DT compatibles, clock-provider registration, and HDMI/display-engine routing callers.

## Risks and Edge Cases

- Register offsets and bit positions are hardware ABI. Any incorrect value breaks routing or clock gating silently.
- `CLK_NUM` must remain synchronized with DT binding indices and the C file's clock registration.
- The public helpers expose `struct device *` rather than a private type, so callers can pass non-TCON devices and rely on runtime validation.

## Test Signals

Compile tests should catch signature drift with callers. Hardware tests should validate each bit mask against observed register changes. Binding tests should ensure clock indices and output names stay synchronized with this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_tcon_top.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_layer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_layer.c

## Purpose

`sun8i_ui_layer.c` implements DRM plane support for Allwinner UI layers, which handle RGB framebuffer scanout in the DE2/DE3/DE33 mixer pipeline. It validates plane state, programs layer attributes, coordinates, scaling, and DMA address registers, and creates UI planes with alpha and z-position properties.

## Important APIs, Types, and Functions

- `sun8i_ui_layer_init_one()`: allocates and initializes one `struct sun8i_layer` as a DRM universal plane.
- `sun8i_ui_layer_atomic_check()`: rejects unsupported or YUV formats and checks plane scaling constraints.
- `sun8i_ui_layer_atomic_update()`: disables invisible planes or programs attributes, coordinates, scaler, and buffer address.
- `sun8i_ui_layer_update_attributes()`: maps DRM formats to mixer hardware formats and programs alpha mode/value and enable bit.
- `sun8i_ui_layer_update_coord()`: computes source/destination sizes and fractional phases, chooses UI scaler or VI scaler on DE33, and enables/disables scaling.
- `sun8i_ui_layer_update_buffer()`: programs pitch and low DMA address for plane 0.
- `sun8i_ui_layer_formats`: supported RGB formats for UI planes.

## Control Flow

Atomic check obtains the new plane and CRTC states, validates that the framebuffer format maps to a hardware format and is not YUV, then sets min/max scale depending on `cfg->scaler_mask`. Atomic update disables the layer if the plane is not visible; otherwise it writes attributes first, then size/scaler configuration, then buffer pitch/address. Scaling is enabled when source and destination sizes differ or fractional source phases are present. DE33 UI channels reuse `sun8i_vi_scaler_setup()` and `sun8i_vi_scaler_enable()`; older DE variants use `sun8i_ui_scaler_*()`.

## State and Persistence Behavior

The DRM plane state is transient per atomic transaction; persistent layer identity lives in `struct sun8i_layer` fields initialized once: type, logical index, physical channel, overlay, regmap, and mixer configuration. Hardware registers persist until the next atomic update or disable. The file does not store shadow state beyond the DRM plane state managed by DRM helpers.

## Dependencies and Integration Points

This file depends on DRM atomic, plane, framebuffer, GEM DMA, format, blend, and probe helpers; `sun8i_mixer` for channel bases and format mapping; `sun8i_ui_scaler` for UI scaling; and `sun8i_vi_scaler` for DE33 scaling. It is called by mixer layer initialization and feeds the mixer hardware that later commits through the sunxi engine.

## Risks and Edge Cases

- `sun8i_ui_layer_update_attributes()` ignores the return value of `sun8i_mixer_drm_format_to_hw()` because atomic check should have validated it.
- Only the lower 32 bits of DMA addresses are programmed here; platforms needing high address registers require support elsewhere.
- Scaling ratios use `state->src_w / state->crtc_w` and `state->src_h / state->crtc_h`; zero or invalid dimensions should be excluded by DRM atomic checks.
- DE33's use of the VI scaler means UI and VI scaler behavior must remain compatible for RGB formats.
- Fractional phases trigger scaling even at equal integer sizes; tests should confirm visual alignment.

## Test Signals

Atomic tests should cover every advertised RGB format, alpha property behavior, no-scaling and scaling paths, fractional source offsets, invisible-plane disable, unsupported YUV rejection, and zpos limits. Hardware tests should verify pitch/address programming and scaler enable decisions on DE2/DE3/DE33.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_layer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_layer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_layer.h

## Purpose

`sun8i_ui_layer.h` defines UI layer register address macros, attribute bit fields, alpha mode constants, forward declarations, and the UI plane creation API.

## Important APIs, Types, and Definitions

- `SUN8I_MIXER_CHAN_UI_LAYER_*()`: per-overlay attribute, size, coordinate, pitch, low-address, bottom-address, and fill-color register offsets.
- `SUN8I_MIXER_CHAN_UI_TOP_HADDR()` / `BOT_HADDR()`: high-address register offsets for UI channels.
- `SUN8I_MIXER_CHAN_UI_OVL_SIZE()`: overlay size register offset.
- Attribute bits and masks: enable bit, alpha mode, framebuffer format offset/mask, and alpha value field.
- `sun8i_ui_layer_init_one()`: external constructor for UI planes.

## Control Flow and State

The header is a register contract. Runtime control flow is in `sun8i_ui_layer.c`; consumers use these macros to compute offsets from a mixer channel base and overlay index. The macros assume the hardware's 0x20-byte per-layer stride and fixed channel register layout.

## Dependencies and Integration Points

It includes DRM plane declarations and forward-declares `struct sun8i_mixer` and `struct sun8i_layer`. It depends on `BIT()`/`GENMASK()` visibility through included kernel headers and integrates with the mixer register map, DRM plane initialization, and alpha property handling.

## Risks and Edge Cases

- Register macros do not validate overlay indices; callers must ensure the target layer exists.
- Alpha constants must match hardware encoding and the C file's property programming.
- High-address registers are defined but not programmed by the UI layer implementation in this subset, which matters for DMA addresses above 32 bits.

## Test Signals

Compile tests should catch constructor signature drift. Register-level tests should validate each macro against hardware documentation or known-good traces, especially address stride and alpha/format fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_layer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_scaler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_scaler.c

## Purpose

`sun8i_ui_scaler.c` programs the GSU scaler used by Allwinner UI layers on DE2/DE3 mixers. It selects the correct scaler unit base, converts DRM 16.16 scale/phase values to hardware 20-bit fractional values, writes input/output sizes and steps, and loads horizontal filter coefficients.

## Important APIs, Types, and Functions

- `lan2coefftab16`: 15 sets of 16 filter coefficients derived from Allwinner BSP code.
- `sun8i_ui_scaler_base()`: computes the UI scaler MMIO base after accounting for VI scaler units and DE2 vs DE3 unit sizes.
- `sun8i_ui_scaler_coef_index()`: maps hardware scale step to a coefficient-table set.
- `sun8i_ui_scaler_enable(struct sun8i_layer *layer, bool enable)`: writes GSU enable and coefficient-ready bits.
- `sun8i_ui_scaler_setup(...)`: writes size, step, phase, and horizontal coefficients.

## Control Flow

Callers compute source/destination dimensions, scale, and phase from DRM plane state, then invoke `sun8i_ui_scaler_setup()` before enabling the unit. Setup derives the scaler base from layer channel and configuration, shifts phase and scale from 16 fractional bits to 20 fractional bits, writes output/input sizes and H/V step/phase registers, selects a coefficient block from `hscale`, and writes 16 horizontal coefficients. Enable then toggles `SUN8I_SCALER_GSU_CTRL`.

## State and Persistence Behavior

The file has no heap state. Persistent state is entirely in hardware registers. Coefficient tables are static read-only data. Repeated setup calls overwrite the same scaler unit for the layer's channel; disable clears the control register.

## Dependencies and Integration Points

It depends on `sun8i_ui_scaler.h` and `sun8i_vi_scaler.h` for constants and the VI scaler base/size definitions used to offset UI scalers. It integrates with `sun8i_ui_layer_update_coord()` and regmap-backed mixer MMIO.

## Risks and Edge Cases

- Base calculation depends on `cfg->vi_scaler_num` and channel ordering; wrong mixer configuration maps writes to the wrong scaler.
- Only horizontal coefficients are explicitly loaded; hardware may use fixed/default vertical coefficients, but this should be confirmed for supported SoCs.
- Scale-to-coefficient mapping is coarse and table-bound; extreme down/up scaling relies on atomic min/max checks.
- Width/height macros subtract one, so zero dimensions would underflow if DRM checks failed.

## Test Signals

Tests should validate base offsets for DE2 and DE3 configurations, coefficient index boundaries, scale and phase conversion from 16.16 to hardware 20-bit fractions, equal-size fractional-phase scaling, and disable clearing the control register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_scaler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_scaler.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_scaler.h

## Purpose

`sun8i_ui_scaler.h` declares UI scaler limits, register offsets, control bits, size encoding, and setup/enable functions for the Allwinner GSU scaler.

## Important APIs, Types, and Definitions

- `DE2_UI_SCALER_UNIT_SIZE` and `DE3_UI_SCALER_UNIT_SIZE`: per-unit address spacing.
- `SUN8I_UI_SCALER_SCALE_MIN` / `SCALE_MAX`: atomic scaling bounds expressed for DRM 16.16 inputs.
- `SUN8I_UI_SCALER_SCALE_FRAC` and `PHASE_FRAC`: hardware fractional widths.
- `SUN8I_SCALER_GSU_*`: control, size, step, phase, and horizontal coefficient register macros.
- `SUN8I_SCALER_GSU_CTRL_EN` and `COEFF_RDY`: control bits.
- `sun8i_ui_scaler_enable()` and `sun8i_ui_scaler_setup()`: public scaler controls.

## Control Flow and State

The header is consumed by the UI layer implementation. It defines register computations from a scaler base; the C file computes that base and writes the registers. No runtime state is declared here beyond the implicit hardware state encoded by the macros.

## Dependencies and Integration Points

It includes `sun8i_mixer.h` for `struct sun8i_layer` and mixer configuration. The scale bounds are used by DRM atomic plane checks in `sun8i_ui_layer.c`.

## Risks and Edge Cases

- The scale bounds and fractional constants must remain consistent with DRM's 16.16 source rectangles and the hardware's 20-bit scaler fields.
- Register macros assume valid base addresses and coefficient indices.
- The header lacks an include guard comment with the symbol name but is otherwise guarded.

## Test Signals

Compile and static analysis should catch prototype drift. Unit-style tests or register traces should cover register offset calculations and scale-bound acceptance/rejection in atomic checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_scaler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_layer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_layer.c

## Purpose

`sun8i_vi_layer.c` implements DRM plane support for Allwinner VI layers, which handle RGB and YUV/video framebuffer scanout. It validates plane formats and scaling, programs attributes, chroma-aware dimensions and phases, scaler/coarse-scaler state, CSC configuration, DMA addresses for multi-plane formats, alpha/color properties, and z-order.

## Important APIs, Types, and Functions

- `sun8i_vi_layer_init_one()`: allocates and registers a VI plane with format list, optional alpha, zpos, and color encoding/range properties.
- `sun8i_vi_layer_atomic_check()`: validates hardware format support and scaling constraints.
- `sun8i_vi_layer_atomic_update()`: disables invisible planes or programs attributes, coordinate/scaler state, CSC, and DMA buffers.
- `sun8i_vi_layer_update_coord()`: aligns source geometry for chroma subsampling, decides whether scaling is required, computes coarse downscaling, and sets VI scaler registers.
- `sun8i_vi_layer_update_attributes()`: writes format, RGB/YUV mode, enable, and alpha/global alpha fields.
- `sun8i_vi_layer_update_buffer()`: writes pitch and low DMA address for each framebuffer plane.
- `sun8i_vi_layer_formats` and `sun8i_vi_layer_de3_formats`: supported format sets for DE2 versus DE3+.

## Control Flow

Atomic check obtains the new plane and CRTC states, validates format mapping, then allows scaling only for channels present in `cfg->scaler_mask`. Atomic update disables if not visible; otherwise it writes attributes, coordinate/scaler state, CSC, and buffer addresses. Coordinate update derives integer sizes and fractional phases from DRM source/destination rectangles. For subsampled formats, it rounds source offsets and sizes to chroma alignment and folds the remainder into phase. Scaling is required for size changes, subsampling, or fractional phase. When scaling is active, the function estimates VI scaler vertical ability from mixer module clock, frame rate, display height, and max source/destination width; if insufficient, it enables vertical coarse downscaling. It also coarse-downscales horizontally when the source width exceeds the channel scanline limit. Fine scaling is then programmed through `sun8i_vi_scaler_setup()`, and coarse ratios are written to HDS/VDS registers.

## State and Persistence Behavior

Persistent software state lives in the allocated `struct sun8i_layer` and DRM plane properties. Hardware state includes VI layer attribute/size/pitch/address registers, scaler state, coarse downscale registers, and CSC registers. The implementation resets coarse downscale values to zero when not needed by writing all four HDS/VDS registers each update.

## Dependencies and Integration Points

This file depends on DRM atomic, blend, color, framebuffer, GEM DMA, and plane helpers; `sun4i_crtc` and `sunxi_engine` to reach the mixer clock; `sun8i_mixer` for channel base and format mapping; `sun8i_csc` for color conversion; and `sun8i_vi_scaler` for fine scaling. It integrates with DRM color encoding/range properties and mixer configuration quirks such as `de2_fcc_alpha`, `scanline_yuv`, and `de_type`.

## Risks and Edge Cases

- Format mapping is trusted in update after atomic check.
- DMA high-address registers are not programmed in this file; addresses above 32 bits require support elsewhere or suitable DMA constraints.
- The vertical ability calculation divides by mode timing and dimensions; invalid CRTC modes should be impossible but are a dependency.
- Coarse scaling changes `src_w/src_h` before fine scale computation; visual quality and exact phase behavior need hardware validation.
- Chroma phase handling is split between this file and `sun8i_vi_scaler.c`; subsampled crop tests are important.
- `de2_fcc_alpha` uses a global alpha register, so multiple users of that global hardware path could interact if not constrained by mixer design.

## Test Signals

Tests should cover RGB/YUV formats, DE2 vs DE3+ format lists, alpha property presence, color encoding/range properties, chroma subsampled source offsets, scaler disable/enable decisions, coarse scaling thresholds, CSC configuration calls, multi-plane DMA pitch/address programming, and scanline-limit handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_layer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_layer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_layer.h

## Purpose

`sun8i_vi_layer.h` defines VI layer register offsets, alpha/format/coarse-scaling fields, FCC global alpha definitions, forward declarations, and the VI plane constructor.

## Important APIs, Types, and Definitions

- `SUN8I_MIXER_CHAN_VI_LAYER_*()`: per-overlay attribute, size, coordinate, pitch, and low-address register offsets.
- `SUN8I_MIXER_CHAN_VI_OVL_SIZE()` and HDS/VDS macros: overlay size and coarse downscale registers.
- `SUN8I_MIXER_FCC_GLOBAL_ALPHA_REG`: global alpha register used by some DE2 FCC paths.
- Attribute bits: enable, RGB mode, framebuffer format field, DE3 alpha mode/value fields.
- `SUN8I_MIXER_CHAN_VI_DS_N()` and `DS_M()`: coarse scaling numerator/denominator encoding.
- `sun8i_vi_layer_init_one()`: public VI plane constructor.

## Control Flow and State

The macros compute register addresses from a channel base, overlay index, and plane index. The C implementation uses them during atomic updates to configure VI scanout and coarse scaling. No software state is stored in the header, but the macros define persistent hardware state layout.

## Dependencies and Integration Points

It includes DRM plane definitions and forward-declares sun8i types. It integrates with `sun8i_vi_layer.c`, `sun8i_mixer` channel base calculation, and hardware CSC/scaler programming.

## Risks and Edge Cases

- Register macros assume valid overlay and plane indices; invalid indices would compute unintended offsets.
- FCC global alpha is not per-plane in the macro, matching hardware global behavior and requiring higher-level constraints.
- High DMA address registers are not declared here, unlike the UI layer header.

## Test Signals

Register-trace tests should verify per-plane pitch/address offsets, coarse downscale register encodings, RGB/YUV mode bit behavior, and DE3 alpha field programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_layer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_scaler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_scaler.c

## Purpose

`sun8i_vi_scaler.c` programs the VSU scaler used by Allwinner VI layers, and by DE33 UI layers for RGB scaling. It provides filter coefficient tables, scaler base selection for DE2/DE3/DE33, coefficient selection, enable control, scale mode selection, luma/chroma size and step programming, chroma phase adjustment for YUV420, and coefficient loading.

## Important APIs, Types, and Functions

- Coefficient tables: `lan3coefftab32_left/right`, `lan2coefftab32`, `bicubic8coefftab32_left/right`, and `bicubic4coefftab32`.
- `sun8i_vi_scaler_base()`: selects scaler base from mixer type and layer channel.
- `sun8i_vi_scaler_coef_index()`: maps scale step to one of 15 coefficient blocks.
- `sun8i_vi_scaler_set_coeff()`: chooses luma/chroma coefficient families based on subsampling and writes Y horizontal, Y vertical, chroma horizontal, and chroma vertical coefficient registers.
- `sun8i_vi_scaler_enable(struct sun8i_layer *layer, bool enable)`: writes VSU enable and coefficient-ready bits.
- `sun8i_vi_scaler_setup(...)`: converts DRM scale/phase values, selects DE3+ scale mode, writes sizes, steps, phases, chroma parameters, and coefficients.

## Control Flow

Layer code computes dimensions and 16.16 scale/phase values, then calls setup. Setup derives the hardware base, shifts scale and phase into 20-bit fractional units, packs input/output sizes, computes chroma phases, selects DE3+ UI or normal scale mode depending on subsampling, writes luma output/input/step/phase registers, writes chroma input size and scaled steps using format `hsub`/`vsub`, writes chroma phases, and calls `sun8i_vi_scaler_set_coeff()`. Enable then toggles the VSU control register.

## State and Persistence Behavior

Software state is static read-only coefficient data only. Hardware scaler registers persist per channel until overwritten or disabled. `sun8i_vi_scaler_enable(false)` clears the control register but does not clear size, phase, or coefficient registers.

## Dependencies and Integration Points

The file depends on `sun8i_vi_scaler.h`, `drm_format_info` subsampling fields, mixer configuration (`de_type`, channel), regmap writes, and layer code in both `sun8i_vi_layer.c` and DE33 paths in `sun8i_ui_layer.c`.

## Risks and Edge Cases

- `sun8i_vi_scaler_set_coeff()` accepts `vstep` but uses `hstep` again for vertical coefficient selection. If vertical and horizontal scale ratios differ, vertical filters may be selected from the wrong ratio.
- Y horizontal coefficients are always loaded from lanczos-like tables even when chroma/subsampled paths select bicubic tables; this appears intentional for luma but should be validated.
- YUV420 chroma vertical phase subtracts a quarter-scale offset using unsigned arithmetic; small phases can wrap by design or bug depending on hardware expectations.
- Chroma sizes use integer `src_w / hsub` and `src_h / vsub`; caller alignment is required for subsampled formats.
- DE33 base calculation uses `DE33_CH_SIZE` from mixer configuration headers; mismatched channel size constants corrupt register targeting.
- Zero dimensions would underflow size macros if upstream DRM checks failed.

## Test Signals

Regression tests should cover anisotropic scaling to detect the `vstep`/`hstep` coefficient-selection risk, all subsampling modes, YUV420 phase behavior, DE2/DE3/DE33 base offsets, UI-mode vs normal-mode selection, enable/disable writes, and visual output for RGB and YUV crops with fractional phases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_scaler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_scaler.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_scaler.h

## Purpose

`sun8i_vi_scaler.h` defines VSU scaler address constants, scale limits, register offsets, control bits, DE3+ scale-mode constants, edge/angle helper macros, and public setup/enable APIs.

## Important APIs, Types, and Definitions

- Unit bases and sizes: `DE2_VI_SCALER_UNIT_BASE/SIZE`, `DE3_VI_SCALER_UNIT_BASE/SIZE`, and `DE33_VI_SCALER_UNIT_BASE`.
- Scale constants: min/max scale, 20-bit scale/phase fractional widths, coefficient count of 32, and size packing macro.
- Register macros for VSU control, DE3+ scale mode and thresholds, luma/chroma input sizes, steps, phases, and coefficient banks.
- Control bits: `SUN8I_SCALER_VSU_CTRL_EN` and `COEFF_RDY`.
- Scale modes: UI, normal, and edge-directed scaling.
- `sun8i_vi_scaler_enable()` and `sun8i_vi_scaler_setup()` public APIs.

## Control Flow and State

The header defines the hardware register contract used by `sun8i_vi_scaler.c` and layer code. It stores no software state, but its constants directly determine atomic scale bounds and register address computation.

## Dependencies and Integration Points

It includes DRM FourCC definitions and `sun8i_mixer.h`. It integrates with VI layer atomic checks, DE33 UI scaling, and mixer type/channel configuration.

## Risks and Edge Cases

- Scale limits assume DRM 16.16 rectangles and hardware 20-bit fields.
- `SUN50I_SCALER_VSU_*_SHIFT()` masks use `& 0xF` after shifting; if these unused macros become used, reviewers should confirm the intended mask position.
- Register-bank offsets must match hardware across DE2, DE3, and DE33.

## Test Signals

Compile tests should catch prototype drift. Register tests should validate VSU offsets and coefficient bank spacing. Atomic tests should verify accepted scale ranges match hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_scaler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sunxi_engine.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sunxi_engine.h

## Purpose

`sunxi_engine.h` defines the common abstraction for sunxi display engines used by the sun4i DRM driver. It describes optional/mandatory engine operations and provides inline wrappers for commit, layer initialization, color correction, and mode setting.

## Important APIs, Types, and Functions

- `struct sunxi_engine_ops`: callback table for `atomic_begin`, `atomic_check`, `commit`, mandatory `layers_init`, color correction enable/disable, `vblank_quirk`, and `mode_set`.
- `struct sunxi_engine`: common engine state with ops, OF node, regmap, numeric id, and list linkage.
- `sunxi_engine_commit()`: invokes optional commit callback.
- `sunxi_engine_layers_init()`: invokes mandatory layer creation callback or returns `ERR_PTR(-ENOSYS)`.
- `sunxi_engine_apply_color_correction()` / `disable_color_correction()`: optional RGB/YUV correction controls.
- `sunxi_engine_mode_set()`: optional per-mode update hook.

## Control Flow

CRTC and driver code hold a `struct sunxi_engine *` and call these inline wrappers instead of directly checking each callback. Optional hooks no-op when absent. Layer initialization is treated as required and returns an error pointer if missing. The engine list field supports discovery/association of engines elsewhere in the driver.

## State and Persistence Behavior

The engine object persists for the display engine lifetime. It references a device tree node and regmap owned elsewhere, carries a stable id, and participates in a list. The header itself does not implement locking or reference management; callers must coordinate lifecycle and list access.

## Dependencies and Integration Points

It forward-declares DRM types and depends on kernel list and error-pointer helpers being visible to including translation units. It integrates with sun4i CRTC atomic paths, mixer backends, TCON/TV output color correction, vblank handling, and layer construction.

## Risks and Edge Cases

- `layers_init` is documented mandatory but only enforced at runtime.
- Optional callbacks silently no-op, so missing ops can produce display behavior differences without obvious failures.
- The `vblank_quirk` callback runs in interrupt context per documentation; implementers must avoid sleeping.
- No locking contract is specified for `list` or mutable fields.

## Test Signals

Compile tests should cover all engine implementations. Integration tests should verify missing optional callbacks no-op safely, missing `layers_init` fails cleanly, color correction is applied/removed around TV encoder use, and vblank callbacks satisfy interrupt-context constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sunxi_engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/Kconfig

## Purpose

`sysfb/Kconfig` declares the DRM firmware/system framebuffer driver menu. It configures the shared helper module and concrete coreboot, EFI, Open Firmware, simple framebuffer, and VESA DRM drivers.

## Important APIs, Types, and Definitions

- `menu "Drivers for system framebuffers"` depends on `DRM`.
- `DRM_SYSFB_HELPER`: hidden tristate selected by concrete drivers.
- `DRM_COREBOOTDRM`: coreboot framebuffer DRM driver.
- `DRM_EFIDRM`: EFI framebuffer DRM driver, gated by EFI and `!SYSFB_SIMPLEFB || COMPILE_TEST`.
- `DRM_OFDRM`: Open Firmware display driver, gated by OF and PPC or compile test.
- `DRM_SIMPLEDRM`: generic simple platform-provided framebuffer DRM driver.
- `DRM_VESADRM`: x86 VESA framebuffer DRM driver, gated by x86 and `!SYSFB_SIMPLEFB || COMPILE_TEST`.

## Control Flow and State

Kconfig selection controls which object files are built and which helper subsystems are selected. All concrete drivers select `APERTURE_HELPERS`, DRM client selection, shmem GEM helpers, KMS helpers, and `DRM_SYSFB_HELPER`. EFI and VESA also select `SYSFB` because they consume firmware screen-info platform devices.

## Dependencies and Integration Points

This file integrates with Linux Kconfig, DRM core helpers, sysfb/simplefb infrastructure, architecture firmware paths, and module build selection in the Makefile.

## Risks and Edge Cases

- EFI/VESA are mutually constrained with `SYSFB_SIMPLEFB` except under compile testing; configuration changes can alter which firmware framebuffer driver binds first.
- Hidden `DRM_SYSFB_HELPER` must be selected by every driver using helper symbols.
- Platform constraints are conservative; relaxing them requires build and runtime validation on affected architectures.

## Test Signals

Run allmodconfig/allyesconfig and targeted configs for coreboot, EFI, OF/PPC, simpledrm, and VESA. Verify module dependencies and no unresolved helper symbols. Boot tests should confirm only the intended system framebuffer driver binds for each firmware path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/Makefile

## Purpose

`sysfb/Makefile` maps the sysfb Kconfig symbols to object files and assembles the shared `drm_sysfb_helper` composite object.

## Important APIs, Types, and Definitions

- `drm_sysfb_helper-y`: includes `drm_sysfb.o` and `drm_sysfb_modeset.o`.
- `drm_sysfb_helper-$(CONFIG_SCREEN_INFO)`: conditionally adds `drm_sysfb_screen_info.o`.
- `obj-$(CONFIG_DRM_SYSFB_HELPER)`: builds the helper module/object.
- `obj-$(CONFIG_DRM_COREBOOTDRM/EFIDRM/OFDRM/SIMPLEDRM/VESADRM)`: builds concrete drivers.

## Control Flow and State

Kernel build logic includes helper sources only when selected. `drm_sysfb_screen_info.o` is omitted without `CONFIG_SCREEN_INFO`, matching header guards around screen-info helper declarations.

## Dependencies and Integration Points

It integrates directly with `sysfb/Kconfig` and the source files in this directory. The composite helper must include every exported symbol used by the concrete drivers.

## Risks and Edge Cases

- Adding a new helper source without updating `drm_sysfb_helper-y` creates unresolved symbols.
- Screen-info helper users must remain guarded by `CONFIG_SCREEN_INFO`.
- Concrete object names must match platform driver module expectations and Kconfig symbols.

## Test Signals

Build tests should cover helper-only, each concrete driver as built-in and module, and `CONFIG_SCREEN_INFO=n` where available. `modpost` unresolved-symbol checks are the key signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/corebootdrm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/corebootdrm.c

## Purpose

`corebootdrm.c` implements a simple atomic DRM driver for framebuffers described by coreboot tables. It parses `lb_framebuffer` platform data, validates geometry/format/address, maps the firmware framebuffer, sets up a fixed-mode DRM pipeline, and exposes it through shmem GEM/fbdev helpers.

## Important APIs, Types, and Functions

- `struct corebootdrm_device`: embeds `drm_sysfb_device` plus primary plane, CRTC, encoder, connector, and format list.
- `corebootdrm_get_format_fb()`: maps coreboot bit masks to DRM formats through `pixel_format`.
- Geometry helpers: width, height, pitch, size, address, and orientation validators.
- `corebootdrm_mode_config_init()`: creates mode config, primary plane, CRTC, encoder, and connector, then applies panel orientation quirks.
- `corebootdrm_probe()`: full device creation, memory validation, aperture acquisition, mapping, DRM registration, and client setup.
- `corebootdrm_remove()`: unplug path.

## Control Flow

Probe allocates a managed DRM device, validates that platform data contains a usable LFB entry, resolves format/width/height/pitch/size/address/orientation, fills `drm_sysfb_device`, obtains and validates the platform memory resource, checks that the framebuffer aperture sits inside that resource, acquires the aperture, maps it write-combined, initializes the fixed-mode pipeline, resets mode config, registers the DRM device, and starts DRM clients.

## State and Persistence Behavior

Device state is devm/drmm-managed. The firmware framebuffer mapping persists for the DRM device lifetime through `sysfb->fb_addr`. Hardware scanout state is assumed to have been initialized by coreboot and is not reprogrammed except by CPU writes into the framebuffer. Remove calls `drm_dev_unplug()`.

## Dependencies and Integration Points

It depends on coreboot table structures, aperture helpers, platform devices, DRM shmem GEM helpers, DRM sysfb helpers, fixed-mode connector helpers, and DRM client setup. It binds to the `coreboot-framebuffer` platform device.

## Risks and Edge Cases

- Address validation rejects zero physical address and overflow, but relies on platform resource correctness.
- If `devm_request_mem_region()` fails, the driver warns and maps the resource anyway; this is intentional but can hide resource-description problems.
- Only listed RGB formats are supported; unusual coreboot masks fail.
- The driver assumes firmware keeps display hardware scanning out from the mapped buffer.

## Test Signals

Boot tests on coreboot systems should verify mode, format, orientation, fbdev handoff, aperture conflict handling with native GPU drivers, and damage updates. Fuzz-style tests should cover invalid dimensions, pitch overflow, address overflow, unsupported masks, and missing resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/corebootdrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb.c

## Purpose

`drm_sysfb.c` provides shared validation and format lookup helpers for DRM system framebuffer drivers.

## Important APIs, Types, and Functions

- `drm_sysfb_get_validated_int()`: validates a `u64` value against a caller maximum and `INT_MAX`.
- `drm_sysfb_get_validated_int0()`: additionally rejects zero values.
- `drm_sysfb_get_format()`: matches a generic `pixel_format` against a table of supported `drm_sysfb_format` entries and returns DRM format info.

## Control Flow

Concrete drivers call validation helpers while parsing firmware/platform metadata. Invalid values produce DRM warnings and `-EINVAL`. Format lookup linearly scans a table and warns when no compatible pixel layout exists.

## State and Persistence Behavior

This file is stateless. It exports helper symbols and module metadata only.

## Dependencies and Integration Points

It depends on kernel export/module/minmax/limits helpers, DRM logging, pixel-format helpers through the header, and all sysfb concrete drivers that parse firmware data.

## Risks and Edge Cases

- Return type is `int`; callers must treat negative values as errors and non-negative values as validated data.
- `max` should reflect the true destination field/resource limit; too-large maxima can still permit semantically invalid values.
- Format matching requires exact pixel mask equality.

## Test Signals

Unit-style tests should cover zero rejection, `INT_MAX` clamping, custom maxima, exact format matches, duplicate table ordering, and unsupported pixel formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb_helper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb_helper.h

## Purpose

`drm_sysfb_helper.h` is the shared interface for DRM system framebuffer drivers. It declares metadata parsing helpers, the common `drm_sysfb_device` state, shadow-plane state extensions, fixed-mode CRTC/connector helpers, and macro bundles for plane/CRTC/connector/mode-config callbacks.

## Important APIs, Types, and Definitions

- `struct drm_sysfb_format`: maps a generic `pixel_format` to a DRM FourCC.
- Validation and screen-info helper declarations.
- `drm_sysfb_mode()`: fixed display mode constructor.
- `struct drm_sysfb_device`: embeds `drm_device`, optional EDID, fixed mode, native format, pitch, gamma LUT size, and framebuffer address.
- `struct drm_sysfb_plane_state`: extends DRM shadow plane state with a selected blit function.
- Plane helpers: fourcc-list builder, begin access, atomic check/update/disable, scanout-buffer support, reset/duplicate/destroy.
- `struct drm_sysfb_crtc_state`: extends CRTC state with current CRTC input format.
- CRTC and connector helper declarations plus callback macro bundles.

## Control Flow and State

Concrete drivers embed `drm_sysfb_device`, initialize fixed hardware metadata, then wire helper macro bundles into their plane, CRTC, connector, and mode-config function tables. The helpers keep per-plane blit state and per-CRTC format state across atomic transactions.

## Dependencies and Integration Points

It depends on DRM core, GEM shadow framebuffer, modes, iosys-map, and video pixel-format types. It integrates every sysfb concrete driver with DRM atomic helpers, fbdev/shmem helpers, fixed connector probing, and framebuffer conversion routines.

## Risks and Edge Cases

- Macro bundles hide many function-table entries; concrete drivers must add `.destroy` methods and any custom overrides correctly.
- `drm_sysfb_device` assumes one fixed scanout buffer and one fixed mode.
- `fb_gamma_lut_size` is optional; color management only works when concrete drivers also provide palette/gamma write hooks.
- The scanout address can be I/O memory or normal memory; helpers must respect `iosys_map` semantics.

## Test Signals

Build all concrete drivers after helper signature changes. Atomic tests should cover state duplication/destruction, format conversion setup, connector mode probing with and without EDID, scanout-buffer export, and gamma LUT length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb_modeset.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb_modeset.c

## Purpose

`drm_sysfb_modeset.c` implements the shared fixed-mode atomic modesetting helpers for system framebuffer DRM drivers. It builds supported format lists, selects blitters, validates shadow-plane updates, copies damage clips into the firmware scanout buffer, clears disabled planes, handles fixed CRTC/connector behavior, and manages custom plane/CRTC state.

## Important APIs, Types, and Functions

- `drm_sysfb_mode()`: creates a 60 Hz fixed mode and derives physical size from 96 dpi when absent.
- `drm_sysfb_build_fourcc_list()`: normalizes native alpha formats to non-alpha equivalents and appends emulated `XRGB8888`.
- `drm_sysfb_get_blit_func()`: maps source/destination format pairs to memcpy or DRM conversion helpers.
- `drm_sysfb_plane_helper_begin_fb_access()`: starts shadow FB access and stores the blit function for the transaction.
- `drm_sysfb_plane_helper_atomic_check()`: enforces no scaling, sets CRTC format, and reserves conversion buffer when needed.
- `drm_sysfb_plane_helper_atomic_update()`: iterates damage and blits to the scanout buffer.
- `drm_sysfb_plane_helper_atomic_disable()`: clears the disabled region to black.
- State helpers for plane and CRTC reset/duplicate/destroy.
- `drm_sysfb_crtc_helper_mode_valid()` and `atomic_check()`: fixed-mode and primary-plane/gamma validation.
- `drm_sysfb_connector_helper_get_modes()`: applies optional one-block EDID and always returns the fixed mode.

## Control Flow

Concrete drivers initialize one native format and fixed mode. During atomic check, the helper rejects scaling, records the hardware framebuffer format in CRTC state, and reserves a conversion buffer if the userspace framebuffer format differs. Begin-access selects a concrete blitter from the userspace format to the current CRTC format. Atomic update obtains CPU access to the GEM framebuffer, enters the DRM device, iterates damage clips, offsets the destination scanout map, and invokes the blitter. Connector probing reads optional EDID through a custom block reader that suppresses extensions, then reports the fixed firmware mode.

## State and Persistence Behavior

Per-plane state stores the blit function and DRM shadow state, including conversion buffer state. Per-CRTC state stores the effective scanout format, which can differ from native format in VESA palette emulation. The physical firmware framebuffer contents persist in `sysfb->fb_addr`; updates modify it directly. Disable clears only the current source-sized region.

## Dependencies and Integration Points

It depends on DRM atomic, damage, EDID, framebuffer conversion, GEM shadow framebuffer, panic scanout, and probe helpers. It integrates with all sysfb drivers through the callback macro bundles in `drm_sysfb_helper.h`.

## Risks and Edge Cases

- Blit support is intentionally limited: native memcpy or XRGB8888-to-native conversions. Unsupported pairs fail begin access.
- EDID helper only exposes the base block and clears extension count, which is safe for limited firmware EDID but loses extension modes.
- `atomic_disable()` uses `dst.vaddr_iomem` directly and notes a TODO for mapping abstraction; normal-memory mappings may need care.
- Damage handling assumes no scaling and primary plane alignment.
- Clearing disabled planes writes zeros, which may not represent ideal black for every exotic format.

## Test Signals

Tests should cover native format ordering, alpha-to-X format normalization, XRGB8888 emulation, unsupported conversion rejection, damage clip blits, disable clears, fixed-mode validation, gamma LUT length checks, EDID with extension count, and panic scanout buffer reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb_modeset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb_screen_info.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb_screen_info.c

## Purpose

`drm_sysfb_screen_info.c` provides shared parsing helpers for firmware framebuffer metadata stored in Linux `struct screen_info`.

## Important APIs, Types, and Functions

- `drm_sysfb_get_width_si()` and `drm_sysfb_get_height_si()`: validate `lfb_width` and `lfb_height`.
- `drm_sysfb_get_memory_si()`: converts `screen_info` framebuffer resources into a `struct resource`.
- `drm_sysfb_get_stride_si()`: uses `lfb_linelength` or the format minimum pitch and validates against resource size divided by height.
- `drm_sysfb_get_visible_size_si()`: computes `PAGE_ALIGN(height * stride)` and validates against resource size.
- Internal `drm_sysfb_get_validated_size0()`: non-zero and max validation for 64-bit sizes.

## Control Flow

EFI and VESA drivers call these helpers after verifying the firmware video type. Width, height, memory, stride, and visible size are validated before any aperture acquisition or mapping. Missing stride falls back to minimum pitch for the detected format.

## State and Persistence Behavior

This file is stateless and only exports helper symbols when `CONFIG_SCREEN_INFO` includes it in the helper object.

## Dependencies and Integration Points

It depends on Linux screen-info resource helpers, DRM FourCC format helpers, and sysfb validation helpers. It integrates primarily with `efidrm.c` and `vesadrm.c`.

## Risks and Edge Cases

- `height * stride` is computed before `PAGE_ALIGN()` without an explicit overflow helper; validated inputs and resource limits reduce but do not fully document this assumption.
- Stride maximum is `size / height`, so height must already be non-zero.
- The helper returns NULL for missing memory rather than an error pointer.

## Test Signals

Tests should cover missing resources, zero width/height/stride, fallback pitch, resource-size-limited stride, visible-size page alignment, and oversized visible size rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb_screen_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/efidrm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/efidrm.c

## Purpose

`efidrm.c` implements a DRM driver for EFI-provided framebuffers. It parses `sysfb_display_info`/`screen_info`, maps the EFI framebuffer using cache attributes from the EFI memory map, creates a fixed-mode atomic DRM pipeline, and registers DRM clients.

## Important APIs, Types, and Functions

- `struct efidrm_device`: embeds `drm_sysfb_device` and mode objects.
- `efidrm_get_format_si()`: maps `screen_info` pixel masks to supported DRM formats.
- `efidrm_get_mem_flags()`: determines usable EFI cache attributes for the framebuffer range.
- `efidrm_device_create()`: parses metadata, maps memory with WC/UC/WT/WB behavior, initializes plane/CRTC/encoder/connector, and resets mode config.
- `efidrm_probe()` / `efidrm_remove()`: platform bind/unplug flow.

## Control Flow

Device creation requires platform data and `VIDEO_TYPE_EFI`. It allocates a DRM device, validates format, width, height, memory resource, stride, and visible size through sysfb helpers, stores optional firmware EDID, acquires the aperture, optionally requests the memory region, maps memory based on EFI attributes, initializes a one-plane fixed-mode pipeline, attaches EDID property when available, and returns the device for registration.

## State and Persistence Behavior

State is managed by devm/drmm. EFI firmware initializes display hardware; this driver only writes pixels into the mapped framebuffer. The chosen memory mapping persists for the device lifetime. Remove calls `drm_dev_unplug()`.

## Dependencies and Integration Points

It depends on EFI memory map helpers, sysfb platform data, `screen_info`, aperture helpers, DRM shmem/fbdev helpers, EDID helpers, and `drm_sysfb_helper`. It binds to `efi-framebuffer` platform devices.

## Risks and Edge Cases

- Cache attribute selection falls back to WC/UC when EFI memmap lookup fails; incorrect attributes can affect performance or coherency.
- The driver maps `resource_size(mem)` after acquiring only visible size; if `mem` is the larger firmware resource this maps beyond the visible region intentionally but should match resource ownership.
- Only one EDID block is consumed through the shared connector helper.
- Requires `VIDEO_TYPE_EFI`; malformed sysfb platform data is ignored with `-ENODEV`.

## Test Signals

Boot tests should cover UEFI systems with WC, UC, WT, and WB mappings where possible, EDID-present and EDID-absent cases, aperture handoff to native drivers, XRGB8888 emulation, and invalid screen_info values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/efidrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/ofdrm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/ofdrm.c

## Purpose

`ofdrm.c` implements a DRM driver for Open Firmware display nodes. It parses OF framebuffer properties, handles endian-specific formats, heuristically locates the framebuffer resource, maps the scanout buffer, optionally maps model-specific color-map hardware, exposes gamma/color management, and registers a fixed-mode DRM pipeline.

## Important APIs, Types, and Functions

- `enum ofdrm_model`: identifies supported firmware display models such as Mach64, Rage128, Radeon, GXT2000, Avivo, and QEMU.
- `struct ofdrm_device_funcs`: optional color-map mapping and write callbacks.
- `struct ofdrm_device`: embeds `drm_sysfb_device`, model funcs, color-map base, EDID buffer, and mode objects.
- Display parsing helpers: width, height, depth, linebytes, address, EDID, endian, and model detection.
- PCI helpers: find/enable PCI device and release it without managed PCI helpers to avoid native-driver conflicts.
- Color-map helpers for Mach64, Rage128, Rage Mobility M3 A/B, Radeon, GXT2000, Avivo, and QEMU.
- `ofdrm_device_create()`: full probe construction and mode setup.
- `ofdrm_crtc_helper_atomic_flush()`: reloads hardware gamma on color-management changes.

## Control Flow

Probe calls `ofdrm_device_create()`. Creation allocates DRM state, enables a matching PCI device if present, detects the OF display model, chooses color-map funcs, parses endian, width, height, depth, and linebytes, maps depth to a DRM format, computes framebuffer size, chooses a base address from the `address` property plus platform resources or the largest usable resource, acquires and maps the framebuffer range, optionally maps color-map hardware, reads optional EDID, fills `drm_sysfb_device`, creates the fixed primary-plane/CRTC/encoder/connector pipeline, enables CRTC color management if a color-map is available, and resets mode config. Atomic flush writes gamma values through model-specific callbacks when color state changes.

## State and Persistence Behavior

The firmware-initialized framebuffer and display hardware persist while the driver is bound. `cmap_base` persists only if model-specific mapping succeeds. Gamma/palette state is hardware state written on color-management changes. PCI enablement is tied to platform-device lifetime through a devm action so native drivers can later take ownership.

## Dependencies and Integration Points

It depends on OF address/property APIs, optional PCI APIs, aperture helpers, DRM shmem/fbdev helpers, DRM color management, EDID, and sysfb modeset helpers. It binds to OF nodes compatible with `"display"` under platform driver name `of-display`.

## Risks and Edge Cases

- Framebuffer address discovery is heuristic because OF lacks a standard; wrong resources can map the wrong BAR/region.
- `is_avivo()` contains a condition comparing the constant `PCI_VENDOR_ID_ATI_R600 >= 0x9400`, which is always true; model detection should be reviewed.
- `ofdrm_find_fb_resource()` loops with `for (i = 0; pdev->num_resources; ++i)` and relies on `platform_get_resource()` returning NULL to break; the loop condition ignores `i`.
- Some color-map mappings may fail; the driver continues without gamma support.
- Big-endian format translation and `quirk_addfb_prefer_host_byte_order` are subtle cross-architecture behavior.
- `devm_request_mem_region()` failure is fatal here, unlike some other sysfb drivers.

## Test Signals

Test on PPC/Open Firmware machines and QEMU OF VGA. Cover big- and little-endian format parsing, missing `address`, multiple resources, each model-specific palette path, gamma LUT load/fill, EDID parsing, aperture handoff, and native-driver takeover after unplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/ofdrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/simpledrm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/simpledrm.c

## Purpose

`simpledrm.c` implements a DRM driver for `simple-framebuffer` platform devices. It parses either platform data or device-tree properties, keeps firmware-required clocks/regulators/power domains active, maps the framebuffer from reserved memory or I/O memory resources, creates a fixed-mode atomic pipeline, and registers DRM clients.

## Important APIs, Types, and Functions

- `struct simpledrm_device`: embeds `drm_sysfb_device`, optional clocks/regulators/power-domain handles, and mode objects.
- Simplefb parsing helpers for width, height, stride, and format from platform data or OF.
- `simplefb_get_memory_of()`: prefers `memory-region` reserved memory over `reg`.
- Clock helpers: initialize and release clocks referenced by the simplefb node.
- Regulator helpers: discover `*-supply` properties, enable regulators, and release them.
- Generic power-domain helpers: attach/link multiple domains and detach them on cleanup.
- `simpledrm_device_create()`: full hardware resource retention, metadata parsing, memory mapping, and mode setup.
- `simpledrm_probe()` / `simpledrm_remove()`: registration and unplug flow.

## Control Flow

Device creation first allocates a managed DRM device and initializes clocks, regulators, and power domains when using OF rather than platform data. It parses geometry and format from platform data or OF properties, optionally reads panel physical size, computes fallback stride when absent, stores fixed framebuffer metadata, maps reserved system memory via `memremap` when `memory-region` is present or maps an I/O resource with `ioremap_wc` otherwise, initializes one primary plane, CRTC, encoder, and connector, and resets mode config. Probe registers the DRM device and starts clients.

## State and Persistence Behavior

The driver preserves bootloader-programmed display hardware by keeping referenced resources enabled for its lifetime. Clocks/regulators/power-domain attachments are released by devm actions. The framebuffer mapping persists in `sysfb->fb_addr`; scanout contents are updated by shared sysfb blit helpers. Remove unplugs the DRM device.

## Dependencies and Integration Points

It depends on aperture helpers, OF address/reserved-memory/clock APIs, regulators, generic PM domains, simplefb platform data, DRM shmem/fbdev helpers, and `drm_sysfb_helper`. It binds to `simple-framebuffer` platform/OF devices and interacts with `SYSFB_SIMPLEFB` boot-time device creation.

## Risks and Edge Cases

- Clock/regulator errors other than probe deferral are logged but generally non-fatal; display may fail later if firmware/DT descriptions are wrong.
- `memory-region` is preferred over `reg`, and a warning is emitted if both exist.
- Reserved-memory mappings use system-memory `iosys_map`, while resource mappings use I/O-memory maps; helpers must handle both.
- The mapped resource size may exceed the visible framebuffer size; invalid stride/height combinations need validation from input helpers.
- Power-domain handling intentionally only manages multiple domains; single domains are left to the driver core.

## Test Signals

Boot tests should cover platform-data and OF simplefb devices, `memory-region` versus `reg`, panel size properties, missing/zero stride fallback, clock/regulator/power-domain retention, native-driver aperture takeover, and framebuffer updates through damage clips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/simpledrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/vesadrm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/vesadrm.c

## Purpose

`vesadrm.c` implements a DRM driver for VESA BIOS Extension framebuffers described by `screen_info`. It maps the VESA linear framebuffer, creates a fixed-mode atomic pipeline, supports palette/gamma programming through VGA DAC or 32-bit PMI where available, and provides special C8/RGB332 emulation behavior.

## Important APIs, Types, and Functions

- `struct vesadrm_device`: embeds `drm_sysfb_device`, optional 32-bit PMI palette pointer, color-map write callback, and mode objects.
- `vesadrm_get_format_si()`: maps `screen_info` pixel masks to DRM formats, including `C8`.
- Palette/gamma writers: `vesadrm_vga_cmap_write()` and optional `vesadrm_pmi_cmap_write()`.
- Gamma/palette fill/load helpers for component and indexed formats.
- `vesadrm_primary_plane_helper_atomic_check()`: extends sysfb atomic check to switch C8 hardware to RGB332 emulation for XRGB8888 input.
- `vesadrm_crtc_helper_atomic_flush()`: reloads palette/gamma on color-management changes.
- `vesadrm_device_create()`: parses metadata, maps memory, initializes color management and fixed-mode pipeline.

## Control Flow

Device creation requires `VIDEO_TYPE_VLFB`, validates format/geometry/resource/stride/visible size through screen-info helpers, chooses a palette writer using VGA DAC for VGA-compatible modes or VESA PMI on 32-bit x86, stores optional EDID, maps the framebuffer write-combined, initializes mode config, creates the primary plane with custom atomic check, creates a CRTC with custom flush, enables gamma LUT support if a palette writer exists, attaches encoder/connector, and resets mode config. Probe registers the DRM device and starts clients.

## State and Persistence Behavior

The framebuffer and palette hardware are firmware-initialized and persist while bound. `cmap_write` determines whether color management can program hardware. For C8 hardware, CRTC format state can temporarily switch to RGB332 when emulating XRGB8888, and atomic flush reloads the corresponding palette. Remove unplugs the DRM device.

## Dependencies and Integration Points

It depends on x86/sysfb screen_info, VGA I/O ports, optional 32-bit VESA PMI, aperture helpers, DRM color management, DRM shmem/fbdev helpers, EDID, and `drm_sysfb_helper`. It binds to `vesa-framebuffer` platform devices.

## Risks and Edge Cases

- PMI palette writing uses inline assembly and is only available on 32-bit x86.
- If a color-indexed format lacks a writable palette, colors may be incorrect and only a warning is emitted.
- C8/XRGB8888 emulation relies on switching effective CRTC format to RGB332 and reloading palette state.
- VGA port access requires correct mode classification by screen_info helpers.
- As with other screen-info drivers, invalid firmware geometry can cause mapping or visible-size rejection.

## Test Signals

Boot tests should cover VGA-compatible and non-VGA VESA modes, C8 palette updates, RGB332 emulation for XRGB8888 clients, gamma LUT loads for 555/565/888 formats, EDID attachment, aperture handoff, and invalid screen_info rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/vesadrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/Kconfig

## Purpose

`tegra/Kconfig` declares the NVIDIA Tegra DRM driver and its debug/staging options.

## Important APIs, Types, and Definitions

- `DRM_TEGRA`: tristate for the Tegra DRM driver, dependent on Tegra architecture or compile testing, common clock, DRM, and OF.
- Selected subsystems include DRM display helpers, bridge connector, DP AUX bus, KMS helper, MIPI DSI, panel support, Host1x, interconnect, IOMMU IOVA, and optional fbdev DMA helpers.
- Optional audio/CEC selections are tied to Tegra SPDIF or CEC notifier configs.
- `DRM_TEGRA_DEBUG`: enables debug support.
- `DRM_TEGRA_STAGING`: exposes the HOST1X interface to userspace when `STAGING` is enabled.

## Control Flow and State

Kconfig controls whether the composite `tegra-drm` object is built and which optional paths compile. The nested options only appear when `DRM_TEGRA` is enabled.

## Dependencies and Integration Points

It integrates with Host1x, DRM display helper libraries, bridge/panel/MIPI/DP helpers, interconnect/IOMMU infrastructure, fbdev emulation, sound, and CEC subsystems.

## Risks and Edge Cases

- The driver selects many subsystems, so dependency changes can have broad build impacts.
- Staging userspace HOST1X exposure is explicitly optional and should remain gated.
- Debug config changes compile flags in the Makefile.

## Test Signals

Build tests should cover built-in/module Tegra DRM, compile-test builds on non-Tegra architectures, debug enabled/disabled, staging enabled/disabled, fbdev emulation, and optional audio/CEC dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/Makefile

## Purpose

`tegra/Makefile` builds the Tegra DRM driver as a composite module/object and applies debug compile flags.

## Important APIs, Types, and Definitions

- `ccflags-$(CONFIG_DRM_TEGRA_DEBUG) += -DDEBUG`: enables debug code when configured.
- `tegra-drm-y`: lists core DRM, submission, GEM, display, output, engine, firmware, and media accelerator objects.
- `tegra-drm-y += trace.o`: always includes trace support.
- `tegra-drm-$(CONFIG_DRM_FBDEV_EMULATION) += fbdev.o`: conditionally includes fbdev emulation.
- `obj-$(CONFIG_DRM_TEGRA) += tegra-drm.o`: ties the composite object to Kconfig.

## Control Flow and State

Kernel build assembles all listed objects into `tegra-drm`. Optional debug affects compilation through `-DDEBUG`; optional fbdev emulation adds `fbdev.o`.

## Dependencies and Integration Points

The object list covers display controller, outputs (`rgb`, `hda`, `hdmi`, `dsi`, `sor`, `dpaux`), 2D/3D engines, firmware processors (`falcon`, `riscv`), and accelerators (`vic`, `nvdec`, `nvjpg`). It must stay synchronized with Kconfig dependencies and source file additions/removals.

## Risks and Edge Cases

- Removing or renaming any source requires Makefile updates or builds fail.
- Adding new source without updating the composite list can silently omit functionality.
- Debug flag behavior depends on source files checking `DEBUG`/dynamic debug paths.

## Test Signals

Run build tests for `CONFIG_DRM_TEGRA=m/y`, debug on/off, and fbdev emulation on/off. Link checks should catch missing object dependencies; runtime tests should verify all major display/output/engine components register as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/Makefile -->
