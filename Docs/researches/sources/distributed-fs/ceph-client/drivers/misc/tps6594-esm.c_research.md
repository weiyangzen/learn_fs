# sources/distributed-fs/ceph-client/drivers/misc/tps6594-esm.c

## Purpose
`tps6594-esm.c` enables and monitors the Error Signal Monitor block in TI TPS6594/TPS6593/LP8764 PMICs. It configures ESM registers, reports named ESM IRQs, and handles suspend/resume start/stop.

## Important APIs, Types, and Functions
The IRQ handler is `tps6594_esm_isr()`. Driver lifecycle is `tps6594_esm_probe()` and `tps6594_esm_remove()`. Power-management callbacks are `tps6594_esm_suspend()` and `tps6594_esm_resume()`. It uses the parent `struct tps6594`, its `regmap`, platform resources for named IRQs, and register bits `TPS6594_BIT_ESM_SOC_EN`, `TPS6594_BIT_ESM_SOC_ENDRV`, and `TPS6594_BIT_ESM_SOC_START`.

## Control Flow
Probe reads PMIC revision and rejects revision 1 because GPIO3 cannot be used for SoC ESM there. It loops over platform resources, resolves each named IRQ, and requests threaded one-shot handlers. It then enables ESM SOC mode/driver bits, starts the ESM block, enables runtime PM, and takes a runtime PM reference. Remove stops ESM, clears enable bits, and releases runtime PM. Suspend clears the start bit and drops the runtime PM reference; resume reacquires runtime PM and sets the start bit.

## State and Persistence
No private data is allocated. State is held in parent PMIC registers and devm-managed IRQ registrations. Runtime PM reference state is maintained by the PM core.

## Dependencies and Integration Points
The driver is a platform child named `tps6594-esm` under the TPS6594 MFD. It depends on parent drvdata, regmap, platform IRQ resources named by the MFD, and runtime PM.

## Risks and Edge Cases
The ISR calls `platform_get_irq_byname()` for every resource on every interrupt, which is simple but inefficient and can return errors during interrupt handling. `pm_runtime_get_sync()` return values are ignored. Revision filtering only checks exact `0x08`, so future errata variants require updates.

## Test Signals
Validate revision-1 rejection, successful enable/start register writes, named IRQ logging, suspend clears start and resume restarts, remove disables ESM, and regmap/IRQ request failures return `dev_err_probe()` errors.
