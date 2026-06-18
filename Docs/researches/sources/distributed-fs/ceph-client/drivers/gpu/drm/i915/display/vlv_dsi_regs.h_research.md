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
