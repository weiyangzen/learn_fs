# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_oldi.c

## Purpose

`tidss_oldi.c` implements a DRM bridge for TIDSS OLDI/LVDS transmitters described under the `oldi-transmitters` DT node. It configures OLDI link mode, serial clock, IO power, input bus-format negotiation, and bridge-chain attachment for single-link and dual-link LVDS paths.

## Important APIs, Types, and Functions

- `struct tidss_oldi` stores parent TIDSS device, bridge, downstream bridge, link type, selected bus format, OLDI instance IDs, parent VP, serial clock, and IO-control regmap.
- `oldi_bus_formats[]` maps LVDS media bus formats to data width, OLDI map field, and TIDSS input bus format.
- Bridge funcs: `tidss_oldi_bridge_attach()`, `tidss_oldi_atomic_pre_enable()`, `tidss_oldi_atomic_post_disable()`, `tidss_oldi_atomic_get_input_bus_fmts()`, and `tidss_oldi_mode_valid()`.
- Hardware helpers: `tidss_oldi_set_serial_clk()`, `tidss_oldi_tx_power()`, and `tidss_oldi_config()`.
- DT helpers: `get_oldi_mode()` resolves single, clone, dual, and secondary modes; `get_parent_dss_vp()` finds the connected DSS VP.
- Lifecycle: `tidss_oldi_init()` discovers/registers bridges; `tidss_oldi_deinit()` removes them and clears external-clock flags.

## Control Flow

Probe calls `tidss_oldi_init()` before modeset discovery. The function finds `oldi-transmitters`, iterates available child OLDI nodes, identifies their parent DSS VP through graph port 0, fetches downstream sink bridge from port 1, determines companion/link mode from `ti,companion-oldi`, `ti,secondary-oldi`, and LVDS dual-link pixel order, rejects unsupported and current clone configurations, allocates/registers a bridge for usable primary OLDI nodes, acquires IO-control regmap and serial clock, records the bridge in `tidss->oldis`, and marks the parent VP as externally clocked.

During atomic bus negotiation, the bridge maps output LVDS format to the DSS input RGB format and stores the selected OLDI bus format. Pre-enable configures the DISPC OLDI bits for single/dual link, sets the serial clock to seven times pixel clock, and powers IO. Post-disable powers IO down, sets serial clock to the idle frequency, and clears DISPC OLDI config.

## State and Persistence Behavior

Each registered OLDI bridge persists in `tidss->oldis[]`. `oldi->bus_format` is selected during atomic bus-format negotiation and later consumed by pre-enable, so a valid negotiation must precede enable. `tidss->is_ext_vp_clk[parent_vp]` persists while the OLDI bridge exists and tells DISPC to skip internal VP clock checks. Hardware OLDI config and IO power are enabled only during active bridge state.

## Dependencies and Integration Points

The file depends on OF graph helpers, DRM bridge APIs, LVDS dual-link parsing, clocks, syscon regmap, media bus formats, `tidss_dispc` OLDI configuration helpers, and OLDI bit definitions from `tidss_dispc_regs.h`. KMS discovery later sees these registered bridges as downstream endpoints.

## Risks and Edge Cases

- Clone mode code exists for hardware power/config but initialization rejects clone because DRM cannot represent the needed dual encoder pipelines here.
- `companion_instance` is initialized once before the loop; failed or skipped nodes must not leak stale values into later nodes.
- `of_clk_get_by_name()` obtains a clock reference but deinit does not explicitly `clk_put()`; managed lifetime depends on OF clock handling and device cleanup.
- Pre-enable ignores return values from `tidss_oldi_config()` and `tidss_oldi_set_serial_clk()`, so enable can continue after logged failures.
- `oldi->bus_format` can be NULL if the downstream bridge does not call `atomic_get_input_bus_fmts()` before pre-enable.

## Test Signals

Tests should cover single-link, primary/secondary dual-link, rejected clone, invalid companion reg, missing downstream bridge, missing IO syscon/serial clock, unsupported output bus formats, serial clock round-rate validation, pre-enable/post-disable register changes, and deinit clearing bridges and external VP clock flags.
