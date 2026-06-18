# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-milos.c

## Purpose
Defines the main TLMM pin controller for Qualcomm Milos. It describes a modern 168-GPIO controller plus UFS reset and SDC2 groups, large QUP/CCI/UIM/QDSS/audio/navigation/WCN/PCIe function coverage, PDC wake interrupt mappings, and eGPIO ownership handoff support.

## Important APIs, Types, And Data
The file uses `pinctrl-msm.h` and the shared MSM TLMM core. `PINGROUP()` creates 12-function GPIO groups with 0x1000 register spacing, two-bit interrupt detection, I2C strong-pull support at bit 13, eGPIO present/enable bits at 11/12, wakeup present/enable bits, and KPSS target value 3 at target bit 8. `SDC_QDSD_PINGROUP()` describes storage-card pads, while `UFS_RESET()` describes a non-GPIO UFS reset group with an output bit. `milos_pdc_map[]` maps many GPIOs to PDC wake IRQs. `milos_tlmm` sets `.ngpios = 168`, attaches the wake map, and sets `.egpio_func = 11`.

## Control Flow
`arch_initcall(milos_tlmm_init)` registers the `milos-tlmm` platform driver. OF match `qcom,milos-tlmm` calls `milos_tlmm_probe()`, which delegates to `msm_pinctrl_probe()`. The common core registers pinctrl/pinmux/pinconf functions, creates a gpiochip for GPIOs 0-167, installs the TLMM summary IRQ handler, and, if a `wakeup-parent` domain exists, maps listed GPIOs to PDC parent IRQs. eGPIO mux selections are interpreted by the shared core as a request to release TLMM ownership rather than simply writing a normal mux field.

## State And Persistence
This file is static topology. Runtime state includes TLMM registers, IRQ routing, PDC parent IRQ mappings, and the shared core's bitmaps. eGPIO behavior persists in hardware ownership bits: selecting the eGPIO mux clears TLMM ownership when the present bit says the pin supports it, while selecting normal functions reclaims ownership. I2C strong pull-up is encoded through a wider pull mask in the common pinconf conversion.

## Dependencies And Integration Points
Integrates with device tree via `qcom,milos-tlmm`, generic pinctrl state consumers, gpiolib, irqdomain wake-parent plumbing, PDC wake IRQ handling, and the shared MSM core. It complements `pinctrl-milos-lpass-lpi.c`, which owns low-power audio pins. Device-tree consumers depend on group names `gpio0` through `gpio166`, `ufs_reset`, and `sdc2_*`, and on function names such as `qup*_se*`, `cci_i2c_*`, `uim*`, `qdss_*`, `pcie*_clk_req_n`, `egpio`, and `sdc*`.

## Risks
Milos has a broad blast radius because the table controls many shared SoC interfaces. eGPIO support is especially sensitive: a wrong `.egpio_func`, mux slot, or present/enable bit can leave pins owned by the wrong block. Wake IRQ map mistakes can break suspend wake or route interrupts to the wrong PDC line. Dummy groups preserve index alignment, so removing or reordering them would corrupt pin numbering. UFS reset and SDC groups have invalid normal IRQ fields and must stay outside `.ngpios`.

## Test Signals
Good signals include successful probe, correct 168-line gpiochip registration, PDC wake testing for mapped GPIOs, eGPIO handoff tests on supported high-numbered pins, QUP/CCI/UIM/WCN/PCIe/QDSS pinmux validation, UFS reset behavior, SDC2 card operation, I2C strong pull-up pinconf checks, and debugfs confirmation that dummy/non-GPIO groups are not exposed as GPIO lines.
