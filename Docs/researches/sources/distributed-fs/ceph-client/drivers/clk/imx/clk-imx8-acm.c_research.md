# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8-acm.c

## Purpose
This platform driver exposes the i.MX8 Audio Clock Mux (ACM) registers as common-clock muxes for i.MX8QM, i.MX8QXP, and i.MX8DXL. It routes audio recovery clocks, external MCLKs, SAI/ESAI/SPDIF bit clocks, PLL dividers, ASRC muxes, and MCLK outputs for ADMA audio peripherals.

## Important APIs, Types, And Functions
`struct clk_imx8_acm_sel` describes one ACM mux: clock name, DT ID, parent table, register offset, shift, and width. `struct imx8_acm_soc_data` selects the SoC-specific mux list and mutable MCLK parent table. `struct imx8_acm_priv` stores power-domain attachments, SoC data, base address, and saved registers. `imx8_acm_clk_probe()` maps registers, attaches multiple PM domains, enables runtime PM, registers muxes with `devm_clk_hw_register_mux_parent_data_table()`, patches MCLK parent entries to point at the earlier `acm_aud_clk0_sel` and `acm_aud_clk1_sel` clocks, and registers the onecell provider. `clk_imx_acm_attach_pm_domains()` and `_detach_pm_domains()` manage additional power domains and stateless runtime-PM device links.

## Control Flow
Probe obtains the OF match data, maps the ACM resource, allocates private and onecell state, attaches all listed power domains when more than one exists, powers the block with runtime PM, and iterates over the SoC mux table. The first two audio selector muxes are registered before downstream MCLK muxes; once registered, their `clk_hw` pointers are inserted into the SoC MCLK parent data so child muxes can use them as parents. On success, `devm_of_clk_add_hw_provider()` publishes all ACM clocks, then runtime PM releases the device. Error paths drop runtime PM and detach domains.

## State And Persistence
Clock state is stored in hardware ACM mux registers. Runtime suspend saves every mux register listed by `soc_data->sels` into `priv->regs[]`; runtime resume writes them back. Power-domain device links persist for driver lifetime and are explicitly removed in remove/error paths. The parent tables for MCLK selectors are static mutable data patched at probe time, so each SoC data instance assumes one driver instance per compatible.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/imx8-clock.h`, OF compatibles `fsl,imx8qm-acm`, `fsl,imx8qxp-acm`, and `fsl,imx8dxl-acm`, named firmware clocks in `clk_parent_data.fw_name`, optional dummy or unavailable `.index = -1` parent slots, genpd power domains, runtime PM, and the common clock framework. Audio drivers consume the exported `IMX_ADMA_ACM_*` clock IDs to select SAI/ESAI/SPDIF/MQS master clocks.

## Risks And Test Signals
The main risks are parent-table order mismatches with hardware selectors, static MCLK parent mutation in multi-instance scenarios, missing power-domain links causing register access while unpowered, and suspend/resume restoring stale mux values after firmware changes. Test signals include successful ACM probe on each compatible, no `devm_clk_hw_register_mux_parent_data_table()` errors, audio playback/capture across SAI/ESAI/SPDIF/MQS, MCLK parent switching through clk APIs, runtime PM suspend/resume preserving selected parents, and genpd traces showing all ACM domains active during register access.
