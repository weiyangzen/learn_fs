# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-mio.c

Purpose: UniPhier Media I/O and SD clock data. It describes SD rate parents, per-channel SD mux/gate clocks, MIO DMA, USB2 link, and USB2 PHY gates.

Important APIs/types/functions: exports `uniphier_ld4_mio_clk_data[]` and `uniphier_pro5_sd_clk_data[]`. Macros `UNIPHIER_MIO_CLK_SD_FIXED`, `UNIPHIER_MIO_CLK_SD()`, `UNIPHIER_MIO_CLK_USB2()`, and `UNIPHIER_MIO_CLK_USB2_PHY()` expand to fixed-factor, mux, and gate data.

Control flow: the core driver selects these arrays for MIO/SD compatible strings. Fixed SD rates are internal parents; each SD channel has an unindexed mux selecting among eight SD rates and an indexed gate exposing `sdN`. LD4-style data includes three SD channels, MIO DMA, and USB2/PHY gates; Pro5-style SD data exposes two SD channels.

State and persistence: no executable state; table entries drive helper allocations and syscon register bit usage at probe.

Dependencies/integration: depends on parent system clocks such as `sd-133m`, `sd-200m`, and `usb2`; integrated through `clk-uniphier-core.c`.

Risks: SD mux masks/values are nonuniform across parent groups and must match hardware. Channel register offsets scale by `0x200`, so wrong channel numbers affect unrelated registers.

Test signals: SD rate switching for each channel, gate enable bits at `0x20 + 0x200 * ch`, USB2/PHY gate toggles, and compatible mapping to the right data array.
