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
