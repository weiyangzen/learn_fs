# sources/distributed-fs/ceph-client/drivers/firmware/broadcom/Kconfig

## Purpose
This Kconfig file defines the build-time selection model for Broadcom firmware/data helpers under `drivers/firmware/broadcom`: bcm47xx NVRAM access, bcm47xx SPROM fallback synthesis, and a BNXT OP-TEE firmware manager.

## Important Symbols
`BCM47XX_NVRAM` is a bool enabled for BCM47XX, BCM_5301X, or compile testing. It describes a text-like `name=value` flash partition reader. `BCM47XX_SPROM` is a bool depending on `BCM47XX_NVRAM` and selecting `GENERIC_NET_UTILS`; it provides SPROM fallback data to SSB/BCMA for SoC devices whose board configuration is stored in CFE/NVRAM rather than device-local SPROM. `TEE_BNXT_FW` is a tristate depending on Broadcom iProc with OP-TEE or compile-test TEE, defaulting to `ARCH_BCM_IPROC`, and builds the BNXT trusted-app client.

## Control Flow, State, And Persistence
There is no runtime control flow. The file persists build policy by constraining which C objects can be compiled and whether code is builtin or modular. The NVRAM/SPROM options are bools because the code is used early and by built-in bus fallback registration. The BNXT firmware manager can be a module through the tee client driver model.

## Dependencies And Integration Points
The symbols align directly with the sibling Makefile targets. SPROM depends on NVRAM because it reads NVRAM keys to synthesize `struct ssb_sprom`; BNXT depends on OP-TEE/TEE infrastructure and platform architecture support. The help text is the first integration contract for kernel configurators and defconfig maintainers.

## Risks And Test Signals
Mis-specified dependencies can produce link-time failures or silently omit early platform data. Useful validation is `olddefconfig` coverage for BCM47XX and BCM_5301X, compile-test builds for all three symbols, and ensuring `BCM47XX_SPROM` cannot be selected without the NVRAM provider.
