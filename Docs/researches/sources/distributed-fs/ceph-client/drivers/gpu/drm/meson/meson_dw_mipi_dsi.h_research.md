# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_mipi_dsi.h

Purpose: Defines Meson MIPI-DSI TOP register offsets, reset/clock bits, DPI/VENC color mode fields, component selectors, and status/interrupt registers for the DW MIPI-DSI glue driver.

Important APIs, types, and functions: No functions or structs are exported. Important constants include `MIPI_DSI_TOP_SW_RESET`, reset bits for DWC/intr/DPI/timing, `MIPI_DSI_TOP_CLK_CNTL`, `MIPI_DSI_TOP_CNTL`, `VENC_IN_COLOR_*`, `DPI_COLOR_*`, `MIPI_DSI_TOP_*` field masks, status/measurement registers, interrupt control/status, and `MIPI_DSI_TOP_MEM_PD`.

Control flow: The consumer toggles software reset bits, enables sysclk/pixclk, clears memory power-down, and writes `MIPI_DSI_TOP_CNTL` after selecting DSI pixel format in `dw_mipi_dsi_phy_init()`.

State and persistence: Constants define latched TOP-level DSI configuration: reset state, manual/automatic halt settings, DPI format, VENC data width, component ordering, sync polarity, and memory power. The header also documents interrupt status/clear layout, though the current driver does not request or service DSI TOP interrupts.

Dependencies and integration points: Used by `meson_dw_mipi_dsi.c` with Linux `FIELD_PREP()` and bit macros. It bridges generic MIPI pixel formats to Meson hardware color-mode values.

Risks: Field layout comments include active-reset semantics where names can be misleading, so the driver must write matching assert/deassert sequences. Unused interrupt and measurement constants may lag hardware behavior if future interrupt handling is added.

Test signals: TOP reset pulse should leave DWC/DPI/timing blocks released, `MIPI_DSI_TOP_CLK_SYSCLK_EN` and `PIXCLK_EN` should be set, and RGB888/RGB666 formats should map to expected `DPI_COLOR_*` and `VENC_IN_COLOR_*` values.
