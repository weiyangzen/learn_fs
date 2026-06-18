# sources/distributed-fs/ceph-client/drivers/edac/layerscape_edac.c Research

## Purpose
`layerscape_edac.c` is a thin platform-driver wrapper for Freescale/NXP Layerscape and i.MX9 DDR memory-controller EDAC support. It binds device-tree compatible strings to the shared Freescale DDR EDAC probe/remove implementation and selects a sane EDAC reporting mode.

## Important APIs, Types, and Functions
The Open Firmware match table accepts `"fsl,qoriq-memory-controller"` and `"nxp,imx9-memory-controller"`, passing `TYPE_IMX9` for i.MX9-specific handling in shared code. The `platform_driver` named `"fsl_ddr_mc_err"` delegates `.probe` to `fsl_mc_err_probe` and `.remove` to `fsl_mc_err_remove`, both declared in `fsl_ddr_edac.h`.

`fsl_ddr_mc_init()` is the only local setup function. It checks GHES ownership, normalizes `edac_op_state` to polling or interrupt mode, registers the platform driver, and logs registration failure. `fsl_ddr_mc_exit()` unregisters the platform driver.

## Control Flow
Module init runs before platform binding. If GHES devices are present, it returns `-EBUSY` to avoid conflicting firmware-first reporting. Otherwise, it ensures unsupported opstates fall back to interrupt mode, registers the platform driver, and lets the platform bus invoke shared probe for matching DT nodes. Exit simply unregisters the driver.

## State and Persistence
This file has no private persistent state beyond platform-driver registration. Device-specific state is owned by the shared Freescale DDR EDAC implementation. The module parameter `edac_op_state` controls polling vs interrupt behavior.

## Dependencies and Integration Points
It depends on `edac_module.h`, `fsl_ddr_edac.h`, Open Firmware matching, platform bus registration, and GHES arbitration. Its primary integration point is the shared Freescale DDR EDAC driver, not local hardware access.

## Risks and Edge Cases
Most behavioral risk is delegated. Local risks are configuration-level: wrong compatible data would route a platform to the wrong shared behavior, and forcing invalid opstates to interrupt mode may surprise callers expecting NMI or other states. GHES conflict handling prevents duplicate reporting.

## Test Signals
Verify module init returns `-EBUSY` under GHES, DT nodes bind for both compatibles, `TYPE_IMX9` data reaches shared probe, `edac_op_state` normalizes to `EDAC_OPSTATE_INT` for invalid inputs, shared probe/remove run, and platform-driver unregister cleans bindings on module unload.
