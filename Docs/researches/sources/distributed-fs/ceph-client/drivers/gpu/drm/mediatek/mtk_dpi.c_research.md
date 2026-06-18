## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dpi.c

### Purpose

`mtk_dpi.c` implements the MediaTek DPI and DP-INTF bridge/encoder component. It programs parallel display output timing, pixel clocks, bus formats, RGB/YUV conversion, polarity, DDR/dual-edge output, pinctrl states, debug test patterns, and bridge connector integration.

### Important APIs, types, and functions

`struct mtk_dpi` holds encoder/bridge/connector objects, MMIO, clocks, mmsys device, mode, SoC config, selected bus format/color settings, pinctrl states, and a power refcount. `struct mtk_dpi_conf` describes PLL factors, register masks, max clock, supported output formats, polarity and input-swap support, direct pin behavior, DP-INTF variants, pixels per iteration, MMSYS edge config, HDMI-clocked variants, and output 1-pixel mode.

Major helpers include timing programming (`mtk_dpi_config_hsync()`, `mtk_dpi_config_vsync_*()`), format programming (`mtk_dpi_config_bit_num()`, `mtk_dpi_config_color_format()`, `mtk_dpi_dual_edge()`), power/clock (`mtk_dpi_power_on/off()`), clock calculation (`mtk_dpi_set_pixel_clk()`), mode setup (`mtk_dpi_set_display_mode()`), bridge ops, debugfs test-pattern ops, and component bind/unbind.

### Control flow

Probe allocates a DRM bridge, loads compatible-specific config, initializes default output format, optionally selects sleep pinctrl, maps registers, gets engine/pixel/pll clocks, gets IRQ, locates downstream bridge through OF graph, registers the DRM bridge, and adds the component. Component bind creates a TMDS encoder, computes possible CRTCs, attaches the DPI bridge chain with no connector, creates a bridge connector, and attaches it to the encoder.

Atomic bridge check chooses output format, bit depth, channel swap, YC map, and RGB/YUV color format. Mode set stores adjusted mode. Enable selects active pins, powers clocks, programs display mode, and enables the block. Disable powers off and returns pins to sleep. Public `mtk_dpi_start/stop()` only power non-HDMI-clocked variants.

### State and persistence behavior

Software state persists selected output format and mode between atomic check/mode_set/enable. `refcount` prevents double clock disable when DPI is used through both DDP start/stop and bridge enable/disable. Hardware state persists in timing generator, size, output setting, color conversion, channel limits, DDR, frequency-control, pattern, and enable registers. Pinctrl state persists at the SoC pinmux level.

### Dependencies

The driver depends on DRM bridge, bridge-connector, atomic helper, EDID, OF graph, MediaTek MMSYS, clocks, pinctrl, debugfs, and `mtk_dpi_regs.h`. It integrates with `mtk_drm_drv.c` as a DDP component and downstream panels/bridges through standard DRM bridge APIs.

### Integration points

DPI/DP-INTF sits near the end of a MediaTek CRTC path and feeds an external bridge, panel, HDMI path, or DP transmitter. Its output bus format negotiation feeds downstream bridge requirements and upstream color conversion. `mtk_dpi_encoder_index()` exposes encoder index to other MediaTek code. Debugfs exposes `dpi_test_pattern` for hardware pattern generation.

### Risks

Clock programming mutates a local `videomode` pixelclock after PLL rounding and divides by `pixels_per_iter`, so porch/timing assumptions must stay consistent with DP-INTF variants. The debugfs write checks unsigned values for `< 0`, which is ineffective but harmless. Power refcounting must stay balanced across DDP and bridge callers. Some configurations are `clocked_by_hdmi`, so register access and clock ownership differ from normal DPI. YUV422 matrix selection uses `mode.hdisplay <= 720` rather than detailed colorimetry.

### Test signals

Validate bridge attach and connector creation, mode-valid clock rejection, output bus-format negotiation for RGB/YUV and 8/10/12-bit formats, DPI and DP-INTF modes at different pixel clocks, pinctrl active/sleep transitions, suspend/resume, debugfs pattern enable/disable, dual-edge RGB888 modes, and interlaced/3D timing paths.
