<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx93-blk-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx93-blk-ctrl.c

## Purpose

`imx93-blk-ctrl.c` implements i.MX91/i.MX93 media block-control PM domains. It controls block reset and clock-gate bits, shared bus clocks, runtime PM for the parent media slice, and QoS priority registers for media pipelines.

## Important APIs, types, and functions

`struct imx93_blk_ctrl` stores device, regmap, bus clocks, domains, and onecell data. `struct imx93_blk_ctrl_domain_data` describes clocks, reset/clock masks, and QoS entries. `imx93_blk_ctrl_power_on()` enables bus/domain clocks, resumes the provider, ungates clocks, releases reset, and applies QoS. `imx93_blk_ctrl_power_off()` reverses this. Probe builds genpds and registers a onecell provider.

## Control flow

Probe selects i.MX91 or i.MX93 data, maps registers, gets shared media bus clocks, skips unsupported i.MX91 domains, initializes remaining genpds with cleanup actions, enables runtime PM, registers the provider, and populates child devices. Power transitions enable clocks before register access and use runtime PM for the parent slice.

## State and persistence behavior

State persists in genpd status, clock counts, runtime PM usage, `BLK_SFT_RSTN`, `BLK_CLK_EN`, and LCDIF/PXP/ISI QoS registers. i.MX91 leaves skipped onecell entries NULL.

## Dependencies and integration points

It depends on genpd, runtime PM, regmap access tables, clocks, OF platform population, and `fsl,imx93-power.h`. It matches i.MX91 and i.MX93 media block-control compatibles.

## Risks and edge cases

`BLK_CLK_EN` polarity is inverted: clear ungates and set gates. Power-on assumes QoS setup cannot fail. Skipped domains must not be referenced by consumers. Shared clocks/runtime PM must be active before register writes.

## Test signals

Validate i.MX91 skip mask, i.MX93 all-domain registration, onecell indexes, clock failures, reset/clock polarity, runtime PM parent interactions, QoS values, child population, and devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx93-blk-ctrl.c -->
