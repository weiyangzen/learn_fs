# sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_gsbi.c

## Purpose

`qcom_gsbi.c` configures the Qualcomm GSBI wrapper used by older SoCs to route a serial block to SPI, UART, I2C, or other protocols and to program TCSR CRCI mux bits for ADM DMA routing. After programming the wrapper, it populates child devices below the GSBI node.

## Important APIs, Types, and Functions

`struct gsbi_info` holds the enabled interface clock, selected protocol mode, CRCI field, and optional TCSR regmap. `struct crci_config` and SoC tables (`config_ipq8064`, `config_apq8064`, `config_msm8960`, `config_msm8660`) encode per-GSBI ADM CRCI masks. `gsbi_probe()` is the only runtime function. The DT match table binds `qcom,gsbi-v1.0.0`, while TCSR syscon nodes are matched by `qcom,tcsr-*`.

## Control Flow

Probe maps the GSBI register, optionally resolves `syscon-tcsr`, reads `cell-index`, validates it is 1 through 12, reads `qcom,mode`, optionally reads `qcom,crci`, enables the `iface` clock, writes `(mode << 4) | crci` to `GSBI_CTRL_REG`, updates matching TCSR CRCI bits to zero for SPI and to the mask for other modes, issues a write memory barrier, stores drvdata, and calls `of_platform_populate()` for child controllers.

## State and Persistence Behavior

The driver keeps only probe-lifetime state through devm resources and drvdata. Hardware state persists in the GSBI control register and optional TCSR CRCI registers until reset or later firmware/kernel writes. There is no remove callback and no attempt to restore prior TCSR settings.

## Dependencies and Integration Points

It depends on DT properties `cell-index`, `qcom,mode`, optional `qcom,crci`, optional `syscon-tcsr`, the `iface` clock, MMIO, regmap/syscon, and child platform population. The protocol values come from `dt-bindings/soc/qcom,gsbi.h`; child serial drivers depend on this wrapper being configured before their probe.

## Risks and Edge Cases

Missing TCSR is tolerated, so DMA CRCI routing can remain firmware/default configured. `regmap_update_bits()` failures are ignored, which can hide broken syscon mappings. The CRCI mask arrays assume `cell-index - 1` maps directly to table columns. Because there is no remove path, unbinding the driver will not disable the clock or depopulate children beyond devm cleanup behavior.

## Test Signals

Test DTs should cover every supported TCSR compatible, missing/invalid `cell-index`, missing `qcom,mode`, optional `qcom,crci`, SPI versus non-SPI CRCI behavior, failed clock enable, child population, and register readback of GSBI/TCSR values.
