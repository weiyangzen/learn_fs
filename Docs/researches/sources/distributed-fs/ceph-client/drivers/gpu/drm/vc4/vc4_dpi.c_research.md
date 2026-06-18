# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_dpi.c

## Purpose
`vc4_dpi.c` implements the VC4 DPI encoder component. It drives the MIPI DPI type 4 / Nokia ViSSI-style parallel display output block, maps DPI registers, validates the hardware ID, configures bus format and sync polarity, controls pixel/core clocks, attaches the next bridge or panel, and publishes DPI registers through debugfs.

## Important APIs, Types, And Functions
- `struct vc4_dpi` holds the embedded `vc4_encoder`, platform device, mapped registers, pixel/core clocks, and debugfs regset.
- `DPI_READ()` and `DPI_WRITE()` access MMIO and fail KUnit tests if used in unit-test context.
- `vc4_dpi_encoder_enable()` constructs the `DPI_C` control word from connector media bus formats, bus flags, and mode sync flags, writes the register, sets the pixel clock rate to the mode clock, and enables the pixel clock.
- `vc4_dpi_encoder_disable()` disables the pixel clock.
- `vc4_dpi_encoder_mode_valid()` rejects interlaced modes.
- `vc4_dpi_init_bridge()` resolves and attaches a downstream bridge or panel from device tree.
- `vc4_dpi_bind()` allocates and initializes the encoder component, validates `DPI_ID`, acquires clocks, enables the core clock, registers cleanup, initializes the DRM encoder/helper callbacks, attaches the downstream bridge, and stores driver data.
- `vc4_dpi_late_register()` registers the `dpi_regs` debugfs dump.

## Control Flow
The platform driver adds a component in `vc4_dpi_dev_probe()`. During master bind, `vc4_dpi_bind()` maps the DPI registers, validates the hardware ID value `0x00647069`, obtains `core` and `pixel` clocks, enables the core clock for register access, initializes a `DRM_MODE_ENCODER_DPI` encoder, installs helper callbacks, and attaches the next bridge if present in device tree. During a modeset, DRM calls the helper enable path after the CRTC is configured. The enable function discovers the connector currently using this encoder to infer the bus format, writes DPI output format/order/polarity bits, programs the pixel clock, and turns the clock on. Disable only turns off the pixel clock; core clock lifetime is tied to the component bind and devm action.

## State And Persistence Behavior
Long-lived state is limited to `struct vc4_dpi`: mapped registers and clock handles. Runtime hardware state is the `DPI_C` register and clock enable/rate state. The driver does not keep a cached copy of the selected bus format; it re-derives the value on each enable from connector display info.

## Dependencies And Integration Points
The file depends on DRM bridge/panel/of helpers, DRM encoder helpers, connector display-info bus formats and flags, Linux clock framework, component framework, and `vc4_drv.h` shared encoder/debugfs helpers. It integrates with the PixelValve CRTC through `VC4_ENCODER_TYPE_DPI`, allowing `vc4_crtc.c` to set `possible_crtcs` and `clock_select` for compatible PixelValves.

## Risks And Edge Cases
- The bus format is inferred from the connector rather than negotiated through the full bridge chain. Complex bridge chains with non-uniform bus formats can be misconfigured.
- Unknown media bus formats only log an error and keep the current default/partial configuration.
- If no connector or bus format is available, the driver defaults to 18-bit RGB666 output.
- Core clock is enabled for the component lifetime; suspend/runtime PM assumptions differ from encoders that gate all clocks per enable.
- Interlaced modes are rejected; any downstream panel requiring interlace is unsupported.

## Test Signals
- Device-tree probe should verify correct bridge attachment behavior for both connected and absent downstream endpoints.
- Mode tests should cover RGB888, BGR888, RGB/BGR666, RGB565, padded formats, negative-edge pixel data, data-enable polarity, composite sync, and missing sync polarity.
- Runtime hardware checks should confirm `DPI_ID`, `DPI_C`, and pixel-clock rate via debugfs and clock summaries after enable.
- KUnit or mocked tests should avoid direct register macros unless intentionally validating MMIO-guard behavior.
