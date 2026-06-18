# sources/distributed-fs/ceph-client/drivers/soc/ti/Kconfig

## Purpose

`drivers/soc/ti/Kconfig` defines the TI SoC driver configuration menu and feature symbols for Keystone Navigator QMSS/DMA, AMx3 power management, Wakeup M3 IPC, K3 ring accelerator, K3 SoC info, PRUSS platform support, and the internal TI SCI Interrupt Aggregator MSI domain.

## Important APIs, Types, and Functions

This is build metadata, not C code. Top-level `menuconfig SOC_TI` gates most visible TI SoC driver options. Symbols include `KEYSTONE_NAVIGATOR_QMSS`, `KEYSTONE_NAVIGATOR_DMA`, `AMX3_PM`, `WKUP_M3_IPC`, `TI_K3_RINGACC`, `TI_K3_SOCINFO`, `TI_PRUSS`, and `TI_SCI_INTA_MSI_DOMAIN`.

Dependencies encode architecture and subsystem requirements: Keystone options depend on `ARCH_KEYSTONE`; AMx3 PM depends on AM33xx/AM43xx plus Wakeup M3 IPC, EMIF SRAM, SRAM, and OMAP RTC; WKUP M3 IPC depends on remoteproc and mailbox support; K3 RingACC depends on K3 or compile test plus TI SCI INTA irqchip; K3 SoC info selects `SOC_BUS` and `MFD_SYSCON`; PRUSS covers AM33xx/AM43xx/DRA7xx/Keystone/K3 or compile test.

## Control Flow

Kconfig evaluation exposes `SOC_TI`; if selected, it exposes the driver options inside the menu. Selected/tristate values drive `drivers/soc/ti/Makefile` object inclusion. `TI_SCI_INTA_MSI_DOMAIN` sits outside the menu as an internal bool selected by code that needs the MSI domain.

## State and Persistence Behavior

The file contributes to persistent kernel build configuration in `.config`. It does not create runtime state. Symbol values determine whether code is built in, modular, or absent.

## Dependencies and Integration Points

It integrates with architecture symbols, mailbox, remoteproc, SRAM, RTC, TI SCI interrupt aggregator, MFD syscon, SOC bus, and PRUSS users. The matching Makefile maps these symbols to concrete objects.

## Risks and Edge Cases

Incorrect dependencies can expose drivers on unsupported platforms or hide them from valid builds. `TI_SCI_INTA_MSI_DOMAIN` is invisible and must be selected by its users; otherwise `ti_sci_inta_msi.o` will not build. The Keystone DMA help text contains a typo ("Say y tp") but this is documentation-only.

## Test Signals

Run Kconfig build coverage for Keystone, AM33xx/AM43xx, K3, PRUSS, and `COMPILE_TEST` combinations. Confirm expected prompts, selected dependencies, module/built-in object inclusion, and absence of unmet direct dependency warnings.
