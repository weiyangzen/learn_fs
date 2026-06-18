# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-ldb.c

## Purpose
Implements the i.MX53/i.MX6 LVDS Display Bridge component for the IPUv3 DRM stack. It parses LVDS channel nodes, configures split/dual-channel mode, bus mapping and width, LVDS DI muxes, clocks, and bridge connectors.

## Important APIs, types, and functions
- `struct imx_ldb` stores the GPR regmap, two channels, DI clocks, DI mux clocks and original parents, PLL clocks, cached `ldb_ctrl`, and optional i.MX6 LVDS bus mux descriptors.
- `struct imx_ldb_channel` stores channel number, child OF node, bridge pointer, and bus format.
- Encoder helpers include `imx_ldb_encoder_atomic_mode_set()`, `imx_ldb_encoder_enable()`, `imx_ldb_encoder_disable()`, and `imx_ldb_encoder_atomic_check()`.
- Probe/bind helpers include `imx_ldb_probe()`, `imx_ldb_bind()`, `imx_ldb_register()`, `imx_ldb_get_clk()`, `of_get_bus_format()`, and `imx_ldb_ch_set_bus_format()`.

## Control flow
Probe obtains the GPR syscon regmap, resets `IOMUXC_GPR2`, records optional i.MX6 mux descriptors, detects `fsl,dual-channel`, captures available `di*_sel` mux clocks and their original parents, and iterates LVDS child nodes. Each enabled child with a valid `reg` becomes a channel, gets a downstream bridge from the output port or a legacy bridge fallback, and resolves bus format from `fsl,data-mapping`/`fsl,data-width` or later panel data.

Bind registers each populated channel. Registration allocates an LVDS encoder, parses possible CRTCs from the channel node, obtains DI/PLL clocks, adds encoder helpers, attaches the downstream bridge without a connector, creates a bridge connector, and attaches it. Mode set computes serial and DI clock rates, sets PLL and DI clocks for single or dual mode, updates VS polarity bits, and applies data-width/JEIDA/SPWG mapping. Enable sets DI mux parents, enables dual clocks, programs channel-to-DI routing and optional external LVDS mux bits, then writes `IOMUXC_GPR2`. Disable clears channel enable bits, disables dual clocks, and restores the DI mux parent.

## State and persistence
`ldb_ctrl` is the persistent software image of the LVDS control register. Clock parent state is saved at probe and restored on encoder disable. Channel bus format persists from DT or display info. Hardware state persists in GPR2/GPR3 and clock tree configuration.

## Dependencies and integration points
Depends on syscon/regmap for IOMUXC GPR registers, common clock framework, DRM bridge connector helpers, panel/legacy bridge helpers, OF graph parsing, and `imx_crtc_state` for passing RGB bus format and bus flags to the IPU CRTC.

## Risks
Dual-channel mode ignores the second output child and assumes both channels are driven from the first logical channel. Clock parent changes and GPR writes are highly SoC- and device-tree-dependent. Invalid or missing data mapping fails probe unless a bridge can later provide bus formats. Mode clock warnings do not reject over-limit modes. Disable restores only the mux inferred from channel/mux registers.

## Test signals
Validation should cover i.MX53 and i.MX6q compatible data, single- and dual-channel LVDS, SPWG 18-bit, SPWG 24-bit, JEIDA 24-bit mappings, panel-provided bus formats, external LVDS mux ports, DI0/DI1 routing, clock parent restoration, and probe deferral for downstream bridges.
