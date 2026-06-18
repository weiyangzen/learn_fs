# Research group subset-b-003604

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dpio_phy_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dpio_phy_regs.h

### Purpose

`vlv_dpio_phy_regs.h` is the Valleyview/Cherryview DPIO PHY register definition layer used by the i915 display PHY programming code. It does not execute logic; it names sideband register offsets and field encodings for VLV/CHV common, PLL, PCS, and TX register blocks.

### Important APIs, types, and functions

The public surface is preprocessor-only: base-address helpers such as `_VLV_PLL()`, `_CHV_PLL()`, `_VLV_PCS()`, `_VLV_TX()`, register macros such as `VLV_PLL_DW3()`, `VLV_PCS01_DW10()`, `CHV_CMN_DW14()`, and field helpers built from `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. Key fields cover PLL divisors (`DPIO_*_DIV`), calibration/lock bits, PCS reset/data-width/swing/de-emphasis controls, lane stagger/deskw, common-lane powerdown, and CHV buffer enable state.

### Control flow

There is no runtime control flow. Consumers compute a register offset, call `vlv_dpio_get()`, then access it through `vlv_dpio_read()`/`vlv_dpio_write()` from `vlv_sideband.c`. The macros are heavily used by `display/intel_dpio_phy.c` for PLL setup, HDMI/DP lane signal-level programming, power sequencing, and CHV/VLV PHY-specific read-modify-write sequences.

### State and persistence behavior

The header owns no software state. It describes persistent hardware PHY state in IOSF sideband registers: PLL divider programming, common lane powerdown, TX swing/de-emphasis, lane reset, lane skew/stagger, clock channel selection, and lock/frequency-lock indicators. Incorrect values can persist until the PHY is reprogrammed, power-gated, or reset.

### Dependencies

It depends on `intel_display_reg_defs.h` for `_PIPE()`, `REG_BIT`, masks, and field preparation helpers. Semantically it depends on DPIO sideband routing from `vlv_sideband.h` and on platform topology from `intel_dpio_phy.c`.

### Integration points

The primary integration point is the VLV/CHV display PHY implementation. The register constants are passed to `vlv_dpio_read()` and `vlv_dpio_write()` and are protected by `vlv_dpio_get()`/`vlv_dpio_put()` sideband access bracketing. They are independent from the MIPI DSI controller register map but share the same platform family and sideband access mechanism.

### Risks

Field mistakes here can misprogram the PHY without compiler errors. The VLV and CHV address formulas are similar but not interchangeable; using the wrong macro can target the wrong common lane or PLL channel. Some macros encode broadcast/group/per-lane views of related registers, so a consumer must intentionally choose whether programming should affect one lane, one channel group, or the broadcast aperture.

### Test signals

Useful validation signals are i915 display build coverage, HDMI/DP link training on VLV/CHV hardware, PHY power-cycle/resume tests, PLL lock checks, and register readback traces around `intel_dpio_phy.c` signal-level and reset sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dpio_phy_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi.c

### Purpose

`vlv_dsi.c` implements the i915 MIPI DSI encoder/connector path for Valleyview, Cherryview, Broxton, and Geminilake. It wires a VBT-described DSI panel into DRM, implements the MIPI host transfer path, computes display state, programs DSI controller timing registers, sequences panel power/reset/backlight VBT commands, handles DSI device-ready/ULPS transitions, and applies known DMI panel quirks.

### Important APIs, types, and functions

Public entry points are `vlv_dsi_init()`, `vlv_dsi_wait_for_fifo_empty()`, and `vlv_dsi_min_cdclk()`. Encoder hooks include `intel_dsi_compute_config()`, `intel_dsi_pre_enable()`, `bxt_dsi_enable()`, `intel_dsi_disable()`, `intel_dsi_post_disable()`, `intel_dsi_get_hw_state()`, and `intel_dsi_get_config()`. The MIPI host API is `intel_dsi_host_ops`, with `intel_dsi_host_transfer()` packing `mipi_dsi_msg` payload/header data into LP or HS generic FIFOs. Important helpers include `set_dsi_timings()`, `intel_dsi_prepare()`, `intel_dsi_unprepare()`, `dpi_send_cmd()`, `vlv_dphy_param_init()`, and platform-specific device-ready helpers for VLV, BXT, and GLK.

### Control flow

Initialization starts in `vlv_dsi_init()`: VBT detection chooses the DSI port, the driver allocates `intel_dsi` and `intel_connector`, registers an encoder, initializes one DSI host per active port, loads VBT panel data, optionally uses GOP fastboot pclk readback, computes D-PHY parameters, initializes GPIO/VBT state, registers the connector, adds fixed mode and panel/backlight properties, and applies DMI quirks.

Modeset compute uses panel and pfit helpers, clears unsupported mode flags, sets pipe bpp from DSI pixel format, selects DSI transcoders on BXT/GLK, and delegates PLL calculation to `bxt_dsi_pll_compute()` or `vlv_dsi_pll_compute()`. Pre-enable powers the panel, enables underrun reporting, reinitializes the PLL, performs platform IO/regulator setup, executes VBT power/reset/init sequences, enters LP-11 device-ready state, sends initial DCS commands, enables command or video mode, and enables backlight. Disable and post-disable reverse the flow: backlight off, video shutdown or tear-off, FIFO drain, port disable, unprepare, display-off sequence, LP-00 transition, regulator/PLL shutdown, reset assertion, panel power-off delay, and timestamp persistence in `panel_power_off_time`.

### State and persistence behavior

State lives in `struct intel_dsi`, `struct intel_connector`, `struct intel_crtc_state`, VBT panel data, DSI controller registers, and sideband/PHY registers. The driver persists computed D-PHY timing fields in `intel_dsi` (`dphy_reg`, `lp_byte_clk`, switch counts, timeout counts), tracks panel power-off timing for required power-cycle delays, and stores per-panel quirk adjustments in VBT-derived panel structures. Hardware state readout reconstructs active pipe and port clock from registers, with platform guards to avoid BXT/GLK register access when the DSI PLL has invalid dividers.

### Dependencies

The file depends on DRM atomic/connector helpers, DRM MIPI DSI packet helpers, i915 display core types, panel/VBT helpers, backlight, pfit/scaler, FIFO underrun reporting, DSI PLL helpers from `vlv_dsi_pll.h`, controller register definitions from `vlv_dsi_regs.h`, and IOSF sideband helpers from `vlv_sideband.h`.

### Integration points

It registers `DRM_MODE_ENCODER_DSI` and `DRM_MODE_CONNECTOR_DSI` objects into the i915 display pipeline. `intel_dsi_host_transfer()` is used by MIPI DSI device/panel code to send DCS/generic messages. VBT sequence execution integrates with board-specific GPIO, I2C, and panel command tables. The encoder hooks integrate with atomic modeset, backlight update, fastboot state readout, and shutdown.

### Risks

The code is highly sequence-sensitive: device-ready, ULPS, PHY latch, regulator, PLL, and panel commands must occur in the required order with hardware delays. BXT/GLK can hang if DSI registers are accessed without a valid PLL divider. Dual-link and burst-mode timing conversions round between pixels and byte clocks, creating readout mismatches that the code partially compensates for. Several comments mark known uncertainty around command reads/writes, MIPI timeout formulas, and D-PHY switch counts. DMI quirks intentionally mutate fixed modes and VBT sequences; broad matches could affect unrelated systems.

### Test signals

Test signals include boot/fastboot on VLV/CHV/BXT/GLK DSI panels, suspend/resume panel recovery, backlight on/off sequencing, DCS command reads/writes in LP and HS mode, dual-link panels, command-mode panels, FIFO-empty waits, underrun absence, PLL lock/readout, DMI-quirked tablets, and mode validation against fixed panels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi.h

### Purpose

`vlv_dsi.h` exposes the small public interface for the VLV/BXT/GLK DSI implementation to the rest of i915 display code while allowing non-i915 builds to compile with inert stubs.

### Important APIs, types, and functions

It forward-declares `enum port`, `struct intel_crtc_state`, `struct intel_display`, and `struct intel_dsi`. When `I915` is enabled it declares `vlv_dsi_wait_for_fifo_empty()`, `vlv_dsi_min_cdclk()`, and `vlv_dsi_init()`. Otherwise it provides no-op or zero-return inline stubs.

### Control flow

There is no runtime control flow beyond stub selection at compile time. Callers can unconditionally include the header and rely on the build configuration to provide either the real DSI implementation or inert functions.

### State and persistence behavior

The header stores no state. The real functions manage DSI panel, encoder, hardware, and clock state in `vlv_dsi.c`.

### Dependencies

It depends only on type forward declarations and the `I915` build macro. The implementation depends on the broader DRM/i915 display subsystem.

### Integration points

`vlv_dsi_init()` is called from display initialization to create DSI outputs when VBT reports a panel. `vlv_dsi_min_cdclk()` feeds cdclk constraints for DSI modes. `vlv_dsi_wait_for_fifo_empty()` is used during DSI disable paths.

### Risks

The stubs hide DSI behavior in non-i915 builds, so callers must not rely on side effects when `I915` is disabled. Signature drift between the header and implementation would break display initialization.

### Test signals

Build tests with and without `I915` defined, plus display initialization tests that confirm DSI panels are discovered only through the real implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_pll.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_pll.c

### Purpose

`vlv_dsi_pll.c` computes, programs, disables, and reads back MIPI DSI PLL and escape-clock configuration for VLV/CHV and BXT/GLK platforms. It bridges pixel-clock requirements from `intel_dsi` into platform-specific PLL divider registers and provides assertions for PLL state.

### Important APIs, types, and functions

Public functions are `vlv_dsi_pll_compute()`, `vlv_dsi_pll_enable()`, `vlv_dsi_pll_disable()`, `vlv_dsi_get_pclk()`, `vlv_dsi_reset_clocks()`, `bxt_dsi_pll_compute()`, `bxt_dsi_pll_enable()`, `bxt_dsi_pll_disable()`, `bxt_dsi_get_pclk()`, `bxt_dsi_reset_clocks()`, `bxt_dsi_pll_is_enabled()`, `assert_dsi_pll_enabled()`, and `assert_dsi_pll_disabled()`. Internal helpers include `dsi_clk_from_pclk()`, `dsi_calc_mnp()`, `vlv_dsi_pclk()`, `bxt_dsi_pclk()`, `bxt_dsi_program_clocks()`, and `glk_dsi_program_esc_clock()`.

### Control flow

VLV/CHV compute converts pixel clock to DSI link rate, searches M/N/P divisors within platform ranges, converts M through `lfsr_converts[]`, sets port clock gates and VCO enable, and stores values in `config->dsi_pll`. Enable writes CCK sideband PLL control/divider registers, waits after ungating, enables VCO, polls `DSI_PLL_LOCK`, and logs failure. Disable clears VCO and gates the LDO. Readback reads CCK control/divider and reconstructs pclk.

BXT/GLK compute derives an 8-bit PLL ratio from DSI clock and 19.2 MHz reference, checks BXT or GLK min/max ranges, selects DSIA/DSIC 16x-by-2 outputs, and optionally sets PVD ratio. Enable writes `BXT_DSI_PLL_CTL`, programs BXT per-port clock dividers or GLK TX escape clocks, enables `BXT_DSI_PLL_DO_ENABLE`, and waits for `BXT_DSI_PLL_LOCKED`. Disable clears the enable bit and waits for lock deassertion.

### State and persistence behavior

Computed PLL state is persisted in `struct intel_crtc_state::dsi_pll` and reflected in hardware registers. VLV/CHV state lives in CCK sideband registers; BXT/GLK state lives in display MMIO PLL and clock divider registers. Clock reset helpers clear escape/rx/tx divider state and force `CLOCKSTOP` in the DSI EOT register.

### Dependencies

The file depends on `intel_de.h` for MMIO access, `intel_dsi.h` for DSI format/lane data, `vlv_dsi_pll_regs.h` for BXT/GLK PLL and clock registers, and `vlv_sideband.h` for CCK sideband access on VLV/CHV.

### Integration points

`vlv_dsi.c` calls these functions during mode computation, pre-enable, post-disable, fastboot/get-config, and unprepare. `intel_gvt` code includes the PLL register header for virtualized register handling, so register definitions must remain stable across display and virtualization paths.

### Risks

Clock math is hardware-range-sensitive. Wrong rounding or divider bounds can produce an unusable link rate or a PLL that never locks. BXT/GLK register access can hang when the PLL appears enabled but dividers are invalid, which is why `bxt_dsi_pll_is_enabled()` validates divider fields. The VLV `lfsr_converts[]` table is a fragile encoding contract. Dual-link and burst-mode pclk comments note that crtc clock reconstruction is approximate.

### Test signals

Useful signals are PLL lock/unlock waits, pclk readback matching programmed modes, DSI modeset on VLV/CHV/BXT/GLK, fastboot with BIOS-programmed PLLs, invalid-divider recovery, suspend/resume clock reset, and debug assertions for enabled/disabled PLL state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_pll.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_pll.h

### Purpose

`vlv_dsi_pll.h` declares the DSI PLL control API used by VLV/CHV/BXT/GLK DSI code. It separates PLL computation, enable/disable, clock readback, clock reset, and assertion helpers from the main DSI encoder implementation.

### Important APIs, types, and functions

The VLV path exposes `vlv_dsi_pll_compute()`, `vlv_dsi_pll_enable()`, `vlv_dsi_pll_disable()`, `vlv_dsi_get_pclk()`, and `vlv_dsi_reset_clocks()`. The BXT/GLK path exposes `bxt_dsi_pll_compute()`, `bxt_dsi_pll_enable()`, `bxt_dsi_pll_disable()`, `bxt_dsi_get_pclk()`, `bxt_dsi_reset_clocks()`, and `bxt_dsi_pll_is_enabled()`. Assertion helpers are `assert_dsi_pll_enabled()` and `assert_dsi_pll_disabled()`.

### Control flow

There is only compile-time stub control flow. In non-i915 builds, `bxt_dsi_pll_is_enabled()` returns false and assertions do nothing. Real control flow is in `vlv_dsi_pll.c`.

### State and persistence behavior

The header stores no state. The declared functions operate on `struct intel_crtc_state::dsi_pll`, DSI clock fields, and hardware PLL registers.

### Dependencies

It includes `<linux/types.h>` for `u32`/`bool` and forward-declares `enum port`, `struct intel_crtc_state`, `struct intel_display`, and `struct intel_encoder`.

### Integration points

`vlv_dsi.c` depends on this API for mode compute and encoder power sequencing. Platform-specific PLL implementation details remain hidden behind the function pair naming.

### Risks

Wrong platform selection at call sites can program the wrong register block. Non-i915 stubs must remain harmless because they short-circuit state checks used before DSI register access.

### Test signals

Build coverage for i915 and non-i915 configurations, plus modeset tests that exercise both VLV and BXT function families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_pll_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_pll_regs.h

### Purpose

`vlv_dsi_pll_regs.h` defines BXT/GLK DSI PLL, TX escape clock, and MIPI clock-divider MMIO registers used by `vlv_dsi_pll.c`.

### Important APIs, types, and functions

The header exports MMIO macros for `MIPIO_TXESC_CLK_DIV1`, `MIPIO_TXESC_CLK_DIV2`, `BXT_MIPI_CLOCK_CTL`, `BXT_DSI_PLL_CTL`, and `BXT_DSI_PLL_ENABLE`. Field macros cover TX ESCLK dividers, RX upper/lower dividers, 8x-by-3 dividers, PLL ratio/PVD/DSIA/DSIC output selection, ratio bounds (`BXT_DSI_PLL_RATIO_MIN/MAX`, `GLK_DSI_PLL_RATIO_MIN/MAX`), `BXT_REF_CLOCK_KHZ`, enable, and lock bits.

### Control flow

There is no runtime flow. `bxt_dsi_pll_enable()` writes `BXT_DSI_PLL_CTL`, programs dividers from `BXT_MIPI_CLOCK_CTL` or GLK TXESC registers, then sets `BXT_DSI_PLL_DO_ENABLE` and polls `BXT_DSI_PLL_LOCKED`.

### State and persistence behavior

The constants describe persistent PLL and escape-clock hardware state. Divider fields remain programmed until reset or explicit cleanup by `bxt_dsi_reset_clocks()` and PLL disable paths.

### Dependencies

It includes `vlv_dsi_regs.h` for `_MIPI_PORT()` and MMIO helper definitions. Consumers depend on `intel_de_read/write/rmw()` for register access.

### Integration points

Main consumers are `vlv_dsi_pll.c`, GVT MMIO tables, and GVT handlers. This makes the header part of both physical display programming and virtualized register exposure.

### Risks

Incorrect shift/mask definitions can cause invalid dividers and possible DSI register access hangs on BXT/GLK. DSIA/DSIC fields differ by port and by platform because GLK does not have the same DSIC clock behavior as BXT.

### Test signals

Compile coverage of display and GVT, PLL lock tests, register readback during DSI modeset, and validation that clock dividers are cleared during post-disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_pll_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_regs.h

### Purpose

`vlv_dsi_regs.h` is the MIPI DSI controller and port-control register map for VLV/CHV/BXT/GLK DSI outputs. It names DSI MMIO bases, port A/C address selection, D-PHY timing registers, FIFO status, generic packet FIFOs, device-ready/ULPS controls, BXT transcoder timing registers, and GLK MIPI IO status bits.

### Important APIs, types, and functions

The header exports macros such as `MIPI_DEVICE_READY()`, `MIPI_INTR_STAT()`, `MIPI_DSI_FUNC_PRG()`, `MIPI_DPI_RESOLUTION()`, `MIPI_*_COUNT()`, `MIPI_DPI_CONTROL()`, `MIPI_EOT_DISABLE()`, `MIPI_GEN_FIFO_STAT()`, `MIPI_DPHY_PARAM()`, `MIPI_CTRL()`, `BXT_MIPI_TRANS_HACTIVE()`, `BXT_MIPI_PORT_CTRL()`, `VLV_MIPI_PORT_CTRL()`, and many associated bit fields. Key fields include `DEVICE_READY`, `ULPS_STATE_*`, FIFO full/empty bits, video formats, command-mode widths, D-PHY timing masks, `DPI_ENABLE`, dual-link mode, lane configuration, BXT pipe select, GLK PHY/power status, and generic packet data/control fields.

### Control flow

The header has no runtime flow. It enables the DSI code to compute per-port register addresses from `display->dsi.mmio_base` and `enum port`, then perform wait/read/write sequences through `intel_de_*()` helpers.

### State and persistence behavior

The registers described hold live DSI controller state: packet FIFO status, interrupt status/enables, device-ready and ULPS state, D-PHY timing, video timing counts, command/video mode selection, lane count/channel/pixel format, port enable, BXT/GLK IO power/reset status, and read-return buffers. The base selected by `display->dsi.mmio_base` persists as platform initialization state.

### Dependencies

It depends on `intel_display_reg_defs.h` and on `PORT_A`/`PORT_C` conventions from display code. `vlv_dsi.c` and `vlv_dsi_pll_regs.h` are the main local consumers.

### Integration points

This register map is the core integration layer between the DSI encoder and the hardware. It is used for MIPI host transfers, D-PHY programming, panel enable/disable sequencing, modeset timing programming, BXT/GLK hardware readout, FIFO drain waits, and GLK MIPI IO power management.

### Risks

Several register fields are platform-specific but share names and address-selection helpers. Using a VLV port-control macro for BXT or vice versa can program the wrong register. FIFO and interrupt bits directly gate packet transfer waits; bad masks can cause silent timeouts or missed read data. MIPI data return and command-length macros expose packed fields where off-by-one or shift errors corrupt panel commands.

### Test signals

Test signals include DSI register read/write tracing during modeset, generic DCS command transactions, FIFO-empty/full wait behavior, interrupt status changes for packet sent/read data, BXT/GLK hardware state readout, and dual-port/dual-link mode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_sideband.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_sideband.c

### Purpose

`vlv_sideband.c` implements DPIO sideband read/write routing for VLV/CHV display PHY access. It maps logical `enum dpio_phy` values to IOSF sideband units and wraps raw sideband access with a warning for suspicious all-ones reads.

### Important APIs, types, and functions

The public functions are `vlv_dpio_read(struct drm_device *drm, enum dpio_phy phy, int reg)` and `vlv_dpio_write(struct drm_device *drm, enum dpio_phy phy, int reg, u32 val)`. The private helper `vlv_dpio_phy_to_unit()` selects `VLV_IOSF_SB_DPIO` or `VLV_IOSF_SB_DPIO_2` based on platform and PHY.

### Control flow

For Cherryview, `DPIO_PHY0` maps to `VLV_IOSF_SB_DPIO_2` and the other PHY maps to `VLV_IOSF_SB_DPIO`; on Valleyview all DPIO PHY accesses route to `VLV_IOSF_SB_DPIO`. Reads call `vlv_iosf_sb_read()`, warn if the result is `0xffffffff`, and return the value. Writes call `vlv_iosf_sb_write()`.

### State and persistence behavior

The file owns no persistent state. It mutates hardware sideband registers selected by callers, and those values persist in the DPIO PHY until reprogramming or reset.

### Dependencies

It depends on `intel_display_core.h`, `intel_display_types.h`, `intel_dpio_phy.h`, and `vlv_sideband.h`. The underlying IOSF sideband implementation supplies locking and actual access.

### Integration points

The functions are used by DPIO PHY programming code and any caller using VLV/CHV DPIO register definitions. Access should be bracketed with `vlv_dpio_get()`/`vlv_dpio_put()` from the header to acquire the relevant sideband units.

### Risks

The all-ones read warning is heuristic; the comment notes some registers may validly return all ones. A wrong PHY-to-unit mapping can write the wrong PHY on CHV. Callers must avoid unbracketed sideband access if the IOSF layer requires mutual exclusion or power/forcewake handling.

### Test signals

PHY register readback on VLV/CHV, no unexpected all-ones warnings during link training, and successful HDMI/DP DPIO programming on both Cherryview PHYs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_sideband.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_sideband.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_sideband.h

### Purpose

`vlv_sideband.h` provides typed convenience wrappers for VLV/CHV IOSF sideband units used by display code: BUNIT, CCK, CCU, DPIO, FLISDSI, NC, and PUNIT.

### Important APIs, types, and functions

Inline APIs include `vlv_bunit_get/read/write/put()`, `vlv_cck_get/read/write/put()`, `vlv_ccu_get/read/write/put()`, `vlv_dpio_get/read/write/put()`, `vlv_flisdsi_get/read/write/put()`, `vlv_nc_get/read/put()`, and `vlv_punit_get/read/write/put()`. Real DPIO access is declared when `I915` is enabled; otherwise stubs return zero or do nothing.

### Control flow

Each wrapper calls `vlv_iosf_sb_get()` with the bit for the unit, performs `vlv_iosf_sb_read()` or `vlv_iosf_sb_write()` with the unit ID, and releases through `vlv_iosf_sb_put()`. Multi-unit DPIO get/put covers both DPIO units.

### State and persistence behavior

The header stores no software state. It controls access to persistent sideband register state and participates in sideband unit locking/reference tracking through `vlv_iosf_sb_get/put()`.

### Dependencies

It includes Linux bit/type helpers plus `vlv_iosf_sb.h` and `vlv_iosf_sb_reg.h` for unit IDs and access functions. DPIO functions also depend on `enum dpio_phy`.

### Integration points

`vlv_dsi.c` uses FLISDSI wrappers for bandgap/rcomp programming. `vlv_dsi_pll.c` uses CCK wrappers for VLV DSI PLL registers. `intel_dpio_phy.c` uses DPIO wrappers for PHY registers. PUNIT/BUNIT/CCU/NC wrappers support other VLV/CHV display power and clock paths.

### Risks

Get/put mismatches can leave sideband units locked or unprotected. The non-i915 DPIO stub signature uses `int phy`, so callers should rely on normal i915 builds for type checking. Sideband reads/writes are low-level hardware operations with little validation.

### Test signals

Static build coverage, lockdep around IOSF get/put users, DSI PLL lock on CCK access, DSI bandgap programming through FLISDSI, and DPIO PHY programming success on VLV/CHV.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_sideband.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_busy.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_busy.c

### Purpose

`i915_gem_busy.c` implements the `DRM_IOCTL_I915_GEM_BUSY` uAPI. It reports whether a GEM object has active native i915 read or write fences and encodes the active engine classes in the legacy busy bitfield.

### Important APIs, types, and functions

The exported function is `i915_gem_busy_ioctl()`. Helpers include `__busy_read_flag()`, `__busy_write_id()`, `__busy_set_if_active()`, `busy_check_reader()`, and `busy_check_writer()`. The code understands both single i915 fences and `dma_fence_array` composite fences from parallel submission.

### Control flow

The ioctl looks up the GEM object by handle under RCU, iterates the reservation object with `dma_resv_iter` for read usage, resets `args->busy` if the iterator restarts, and translates write fences to both read and write busy bits while translating read fences to read bits. Native i915 fences are checked against current hardware completion via `i915_request_completed()`. Non-i915 fences are ignored for busy reporting.

### State and persistence behavior

No persistent state is modified. The ioctl samples reservation fences and writes the result to the caller-provided busy field. Because iteration is lockless/restartable, it may observe a moving view of object activity but tries to maintain uABI forward-progress behavior by querying hardware status.

### Dependencies

It depends on DMA fence/reservation APIs, `intel_engine` for engine class IDs, i915 request/fence helpers, and GEM object lookup helpers.

### Integration points

The ioctl is registered in `i915_driver.c` with render-node access. It complements wait/set-domain ioctls but intentionally trades complete foreign-fence visibility for native engine-class detail.

### Risks

Foreign DMA fences are ignored, so the ioctl can report idle while another driver still owns unresolved work. Composite fence handling returns zero if a child is not an i915 composite request, which can under-report mixed fences. Engine class IDs must fit the legacy 16-bit read mask.

### Test signals

igt busy ioctl tests, parallel submission tests, read/write fence reservation tests, lockless lookup races with handle close, and comparisons against wait ioctl behavior for foreign fences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_busy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_clflush.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_clflush.c

### Purpose

`i915_gem_clflush.c` flushes CPU cache lines for GEM objects when domain transitions require memory to become coherent with GPU access. It can perform the flush synchronously or schedule it as reservation-fence-backed work.

### Important APIs, types, and functions

The public function is `i915_gem_clflush_object()`. Internal pieces are `struct clflush`, `__do_clflush()`, `clflush_work()`, `clflush_release()`, `clflush_ops`, and `clflush_work_create()`. The work object uses `dma_fence_work` and pins object pages until release.

### Control flow

The caller must hold the object lock. The function skips flushing on discrete graphics, non-struct-page objects, or cache-coherent reads unless forced. If async operation is allowed and a reservation fence slot can be reserved, it creates clflush work, waits on prior reservation fences, adds a kernel fence, commits the work, and clears `cache_dirty`. Otherwise it flushes immediately if pages are resident. If pages are not resident, it asserts the object remains CPU-write-domain dirty for future acquire-time flush.

### State and persistence behavior

The function mutates `obj->cache_dirty`, adds kernel fences to `obj->base.resv`, pins/unpins pages for async flushing, and calls `i915_gem_object_frontbuffer_flush()` after `drm_clflush_sg()`. It does not persist data itself, but it ensures CPU cache state is written back before GPU-visible use.

### Dependencies

It depends on DRM cache helpers, i915 object/page/domain/frontbuffer helpers, `i915_sw_fence_work`, reservation fences, and tracing.

### Integration points

`i915_gem_domain.c` calls it during domain transitions, and execbuffer calls it when objects need cache cleanup before GPU execution. Frontbuffer flush integration matters for display scanout coherency.

### Risks

Incorrectly skipping flushes can expose stale CPU cache contents to GPU or display. Async flushing must pin pages and install reservation fences correctly so later GPU work waits. The DGFX path warns if `cache_dirty` appears because discrete memory is expected to follow different coherency rules.

### Test signals

Domain transition tests, execbuffer cache-dirty paths, frontbuffer update tests, async fence ordering, object eviction during async flush, and coherency tests on LLC/non-LLC systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_clflush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_clflush.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_clflush.h

### Purpose

`i915_gem_clflush.h` declares the GEM object cache flush API and its behavior flags.

### Important APIs, types, and functions

It declares `i915_gem_clflush_object(struct drm_i915_gem_object *obj, unsigned int flags)` and defines `I915_CLFLUSH_FORCE` and `I915_CLFLUSH_SYNC`.

### Control flow

There is no runtime control flow in the header. The flags direct the implementation to force flushing despite read coherency or to require synchronous flushing.

### State and persistence behavior

The header stores no state. The implementation mutates object cache-dirty state and reservation fences.

### Dependencies

It includes Linux type definitions and forward-declares i915 object/device types.

### Integration points

Included by GEM domain and execbuffer paths that need cache-coherency transitions.

### Risks

Flag misuse changes correctness/performance tradeoffs. Omitting `I915_CLFLUSH_SYNC` where immediate CPU/GPU ordering is required can introduce stale data hazards.

### Test signals

Build coverage and GEM coherency/domain-transition tests for forced and synchronous flush paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_clflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_context.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_context.c

### Purpose

`i915_gem_context.c` implements i915 GEM context uAPI, context lifetime, engine-set construction, VM handles, delayed proto-context realization, scheduler attributes, persistence/cancellation behavior, SSEU configuration, protected-content constraints, reset stats, and module cache setup.

### Important APIs, types, and functions

Public functions include `i915_gem_init__contexts()`, `i915_gem_context_open()`, `i915_gem_context_close()`, `i915_gem_context_release()`, `i915_gem_context_lookup()`, `i915_gem_context_create_ioctl()`, `i915_gem_context_destroy_ioctl()`, `i915_gem_context_getparam_ioctl()`, `i915_gem_context_setparam_ioctl()`, `i915_gem_context_reset_stats_ioctl()`, `i915_gem_vm_create_ioctl()`, `i915_gem_vm_destroy_ioctl()`, `i915_gem_user_to_context_sseu()`, `i915_gem_engines_iter_next()`, and module init/exit.

Core internal flows include proto-context creation/registration/finalization, user engine parsing (`set_proto_ctx_engines_*()`), default/user engine realization, `intel_context_set_gem()`, stale-engine fenced release, `kill_engines()`, `context_close()`, and parameter get/set handlers for live and proto contexts.

### Control flow

File open initializes xarrays for real contexts, proto contexts, and VM handles, then creates/registers context 0 immediately. Context create validates flags and ban state, builds a proto-context with default user flags, applies `CONTEXT_CREATE_EXT_SETPARAM` extensions, and either registers the proto-context for lazy finalization or creates a real context immediately on newer graphics versions. `i915_gem_context_lookup()` first checks the real context xarray; if absent, it locks the proto-context table, creates the real context, registers it, erases the proto entry, and closes the proto state.

Real context creation allocates a context, creates or references a VM, copies user flags and scheduler attributes, builds either default engines or user-defined physical/balanced/parallel engines, sets GEM backpointers and VM references in each `intel_context`, optionally creates a shared timeline syncobj, and takes PXP runtime wakerefs for protected contexts. Close removes the context from xarrays/lists, unpins engines, fences active contexts until idle, clears handle lookup tables, revokes or kills outstanding work depending on persistence and hangcheck, and releases references through deferred work.

### State and persistence behavior

Persistent per-file state lives in `drm_i915_file_private::{context_xa, proto_context_xa, vm_xa, proto_context_lock}`. Persistent per-context state includes refs, VM, RCU engine array, scheduler priority, user flags, protected-content wakeref, syncobj, hang/reset counters, LUT radix tree, client links, and stale engine list. Hardware persistence is through `intel_context` objects and in-flight requests that may outlive userspace handles until fenced idle release completes.

### Dependencies

The file depends on xarray, kref, RCU, mutexes, radix tree, DRM syncobj, shmem helpers, i915 scheduler/request/context/engine APIs, PPGTT creation, GuC/execlists capability checks, PXP, user-extension parsing, reset/heartbeat helpers, and i915 client accounting.

### Integration points

Context lookup is used by execbuffer and perf paths. The context ioctls are registered in `i915_driver.c`. VM create/destroy exposes per-file PPGTT handles used by context parameters. Engine arrays map execbuf engine indices to physical, virtual, or parallel `intel_context` instances. Protected-content flags integrate with PXP and runtime PM. Client runtime accounting accumulates per-engine execution time during engine release.

### Risks

The delayed proto-context model is concurrency-sensitive: context lookup, setparam, destroy, and create finalization all synchronize through `proto_context_lock`. Live context state is split across `ctx->mutex`, `engines_mutex`, RCU, and stale-engine fences, so ordering mistakes can leak contexts or allow use-after-close. Persistence disabling depends on preemption and engine reset support. Parallel engines require permanent pinning after ring-size setup. Protected content requires bannable and non-recoverable constraints plus PXP liveness. Some getparam/setparam reads are intentionally unserialized or debug-only, carrying race risk by design.

### Test signals

Signals include igt context create/destroy/setparam/getparam, VM create/destroy, engine arrays with load-balance/bond/parallel extensions, GuC and non-GuC paths, SSEU validation on Gen11, persistent and non-persistent close behavior, client ban handling, protected-content creation, execbuf lookup races with destroy, reset stats after hangs, and selftests included under `CONFIG_DRM_I915_SELFTEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_context.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_context.h

### Purpose

`i915_gem_context.h` is the public internal header for GEM context operations, flag accessors, engine lookup helpers, VM helpers, ioctl declarations, iterator macros, and module setup.

### Important APIs, types, and functions

It defines inline flag helpers for closed, no-error-capture, bannable, recoverable, persistence, user-engines, and protected-content checks. It declares context open/close/release, VM and context ioctls, `i915_gem_context_lookup()`, ref helpers, VM helpers (`i915_gem_context_vm()`, `i915_gem_context_has_full_ppgtt()`, `i915_gem_context_get_eb_vm()`), engine array lock/get helpers, `for_each_gem_engine`, LUT handle allocation, module init/exit, and `i915_gem_user_to_context_sseu()`.

### Control flow

Inline helpers wrap bit operations, kref get/put, RCU-protected VM/engine access, and mutex acquisition. `i915_gem_context_get_engine()` uses an RCU read-side section to safely fetch and ref an `intel_context` by index.

### State and persistence behavior

The header does not own state but exposes safe access to `struct i915_gem_context` fields defined in `i915_gem_context_types.h`. Ref and lock helpers directly affect context lifetime and engine-array mutation ordering.

### Dependencies

It includes `i915_gem_context_types.h`, GT `intel_context.h`, scheduler, device info, and core GEM driver headers.

### Integration points

Execbuffer, perf, reset, object LUT, and ioctl code use this API to look up contexts, hold refs, choose engines, and access VMs. `for_each_gem_engine()` standardizes iteration over sparse engine arrays.

### Risks

Misusing protected RCU helpers without required locks can race context close or engine replacement. `i915_gem_context_get_eb_vm()` falls back to GGTT when full PPGTT is absent, so callers must understand address-space semantics. Flag helpers expose policy bits whose invariants are enforced in `i915_gem_context.c`.

### Test signals

Compiler/lockdep coverage, execbuffer context lookup tests, engine-index validation, and refcount leak checks around get/put paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_context_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_context_types.h

### Purpose

`i915_gem_context_types.h` defines the data structures backing GEM context uAPI and internal engine mappings: engine arrays, iterators, proto engines, proto contexts, and realized GEM contexts.

### Important APIs, types, and functions

Key types are `struct i915_gem_engines`, `struct i915_gem_engines_iter`, `enum i915_gem_engine_type`, `struct i915_gem_proto_engine`, `struct i915_gem_proto_context`, and `struct i915_gem_context`. Important fields include RCU/fence-backed engine arrays, physical/balanced/parallel engine descriptions, proto VM/user flags/scheduler/user engines/PXP state, live context engines/syncobj/VM/client/ref/release work/user flags/protected content/scheduler/hang counters/LUT/name/stale engines.

### Control flow

The header has no executable control flow, but its comments describe the proto-context delayed-realization model. User configuration starts in `i915_gem_proto_context` and is converted into an immutable or semi-mutable `i915_gem_context` when lookup/submission requires a real context.

### State and persistence behavior

These structures hold most persistent GEM context state. Engine arrays are freed through RCU/fence completion. Proto contexts persist in `proto_context_xa` until finalized or destroyed. Live contexts persist while referenced by userspace handles, requests, engine arrays, VM mappings, and release work.

### Dependencies

It depends on Linux atomic/list/llist/kref/mutex/radix-tree/rbtree/RCU types, GT `intel_context_types.h`, scheduler attributes, and i915 software fences.

### Integration points

The definitions are consumed by `i915_gem_context.c`, execbuffer, request/context code, client accounting, LUT/VMA mapping, and scheduler integration. The uAPI comments document compatibility assumptions for Mesa, media driver, and compute-runtime behavior.

### Risks

The structures encode locking contracts: proto modifications exposed to userspace require `proto_context_lock`, `engines` uses RCU plus `engines_mutex`, and handle LUTs use `lut_mutex`. Field layout and semantics affect uAPI compatibility. Protected content, persistence, and recoverability flags have cross-field invariants that must be maintained by setters.

### Test signals

Context uAPI tests, RCU/list debug coverage, engine replacement/destruction tests, proto-context SETPARAM compatibility tests, and memory-leak/refcount validation during context close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_context_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_create.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_create.c

### Purpose

`i915_gem_create.c` implements GEM buffer creation uAPIs, dumb-buffer creation, memory-region placement selection, protected-content and PAT create extensions, object initialization, and handle publication.

### Important APIs, types, and functions

Public functions are `__i915_gem_object_create_user()`, `i915_gem_dumb_create()`, `i915_gem_create_ioctl()`, and `i915_gem_create_ext_ioctl()`. Important helpers are `object_max_page_size()`, `object_set_placements()`, `i915_gem_publish()`, `__i915_gem_object_create_user_ext()`, `set_placements()`, `ext_set_placements()`, `ext_set_protected()`, and `ext_set_pat()`.

### Control flow

Object creation flushes free objects, rounds size to the maximum min-page-size across placements, rejects zero/too-large sizes, allocates an object, stores placement regions, calls the first memory region's `init_object()` with user-clear flags, applies extension flags, traces creation, and publishes a GEM handle. Dumb create computes format/stride/size, chooses local memory when available or system memory otherwise, creates a user object, and returns handle/size. `GEM_CREATE_EXT` parses user extensions, defaults placement to system memory, validates `NEEDS_CPU_ACCESS`, sets GPU-only allocation for non-system/multi-placement cases, optionally sets PAT index, and publishes the object.

### State and persistence behavior

Created objects persist through GEM handles. The code sets `obj->mm.placements`, `obj->mm.n_placements`, allocation flags such as `I915_BO_ALLOC_USER`, `I915_BO_ALLOC_GPU_ONLY`, `I915_BO_PROTECTED`, and optional PAT state (`pat_set_by_user`). `i915_gem_publish()` drops the allocation reference after handle creation because the handle holds the object alive.

### Dependencies

It depends on DRM fourcc/print helpers, display dumb framebuffer stride limits, GEM ioctl declarations, local/system memory region APIs, PXP, tracing, and generic user-extension parsing.

### Integration points

The ioctls are registered in `i915_driver.c`. Memory region placement integrates with LMEM/SMEM object backends. Protected object creation integrates with PXP enablement. PAT setting is limited to Xe_LPG and newer graphics versions.

### Risks

Placement validation must reject duplicates, private regions, invalid classes, and missing system memory fallback for CPU-accessible multi-region objects. Size rounding to region page size can change returned object size. Protected-content objects require PXP availability. PAT indices are platform-specific and must respect `max_pat_index`.

### Test signals

igt GEM create/create-ext tests, memory-region placement tests on LMEM systems, dumb framebuffer creation, protected-content create failures/success, PAT index validation on supported hardware, handle leak tests, and size/stride boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_create.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_create.h

### Purpose

`i915_gem_create.h` declares the dumb-buffer creation entry point used by DRM mode-setting helpers.

### Important APIs, types, and functions

It forward-declares `struct drm_file`, `struct drm_device`, and `struct drm_mode_create_dumb`, and declares `i915_gem_dumb_create()`.

### Control flow

There is no runtime control flow. The implementation computes stride/size, creates a GEM object, and publishes a handle.

### State and persistence behavior

The header stores no state; the implementation creates persistent GEM handles.

### Dependencies

The header has only type forward declarations. Consumers depend on `i915_gem_create.c` for implementation.

### Integration points

Used by DRM driver setup for dumb framebuffer creation.

### Risks

Signature mismatch would break DRM dumb-create plumbing. The narrow header intentionally does not expose create-ext internals.

### Test signals

Build coverage and DRM dumb-buffer creation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_create.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_dmabuf.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_dmabuf.c

### Purpose

`i915_gem_dmabuf.c` implements PRIME/dma-buf export and import for i915 GEM objects, including attachment mapping, CPU access synchronization, mmap/vmap support, imported-object page acquisition, and local object fast-path import.

### Important APIs, types, and functions

Public entry points are `i915_gem_prime_export()` and `i915_gem_prime_import()`. The `dma_buf_ops` implementation provides attach/detach, map/unmap, mmap, vmap/vunmap, begin/end CPU access, and release. Imported dma-buf objects use `i915_gem_object_dmabuf_ops` with `i915_gem_object_get_pages_dmabuf()` and `i915_gem_object_put_pages_dmabuf()`.

### Control flow

Export fills `DEFINE_DMA_BUF_EXPORT_INFO`, lets object ops veto or prepare dmabuf export, and calls `drm_gem_dmabuf_export()` with the GEM reservation object. Attach requires the object to be migratable to system memory, migrates it there under a ww context, waits for migration, and pins pages. Mapping copies the object's sg table and maps it for the attachment device with `DMA_ATTR_SKIP_CPU_SYNC`. CPU access locks the object, pins pages, transitions to CPU or GTT domain, and retries ww deadlocks. Import returns the original object if the dma-buf came from the same i915 device; otherwise it attaches, refs the dma-buf, allocates a private GEM object, points it at the dma-buf reservation object, and sets GTT read domain.

### State and persistence behavior

Exports share the GEM object's reservation object with the dma-buf. Attach pins pages until detach. Imports persist `obj->base.import_attach`, reuse the external `dma_buf->resv`, and map/unmap pages through dma-buf attachment callbacks. CPU access transitions alter GEM cache/domain state. For some non-coherent cases, imported pages trigger a global `wbinvd_on_all_cpus()`.

### Dependencies

It depends on Linux dma-buf/highmem/dma-resv APIs, DRM GEM PRIME helpers, i915 object/domain/migration/scatterlist helpers, ww locking, and module namespace import for DMA_BUF.

### Integration points

Driver hooks in `i915_driver.c` use `i915_gem_prime_import()`. GEM object ops expose export through `i915_gem_prime_export()`, and GVT uses export for virtual GPU dma-buf sharing. Imported objects integrate with normal i915 object lifetime through custom get/put-pages ops.

### Risks

Migration-to-system-memory failure prevents attach/export use by devices that cannot access LMEM. Cache synchronization is subtle: skipped CPU sync, GTT-domain transitions, and heavy `wbinvd_on_all_cpus()` are platform-dependent. Same-device import intentionally refs the GEM object rather than the dma-buf file, so lifetime assumptions differ from foreign imports. sg-table copying must preserve original entries accurately.

### Test signals

PRIME export/import igt tests, cross-device dma-buf sharing, mmap/vmap CPU access tests, LMEM migration tests, ww-deadlock retry coverage, same-device import fast path, and selftests included under `CONFIG_DRM_I915_SELFTEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_dmabuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_dmabuf.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_dmabuf.h

### Purpose

`i915_gem_dmabuf.h` declares the i915 PRIME dma-buf import/export entry points.

### Important APIs, types, and functions

It forward-declares `struct drm_gem_object`, `struct drm_device`, and `struct dma_buf`, and declares `i915_gem_prime_import()` and `i915_gem_prime_export()`.

### Control flow

There is no runtime control flow in the header. The implementation handles same-device import, foreign attach, export info setup, and dma-buf ops.

### State and persistence behavior

The header stores no state. The implementation creates dma-buf exports and imported GEM objects with shared reservation objects.

### Dependencies

Consumers need DRM GEM and dma-buf types. The implementation depends on Linux dma-buf APIs and i915 GEM object internals.

### Integration points

Used by driver PRIME hooks and GVT export paths.

### Risks

The declarations are part of the cross-driver sharing boundary; signature changes affect DRM driver integration.

### Test signals

Build coverage and PRIME import/export tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_dmabuf.h -->
