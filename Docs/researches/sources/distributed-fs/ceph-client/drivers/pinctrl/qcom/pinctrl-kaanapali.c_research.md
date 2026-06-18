# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-kaanapali.c

Purpose: Kaanapali TLMM pinctrl data driver. It is a large static SoC descriptor for 218 GPIO-capable lines plus special UFS reset and SDC2/QDSD groups, with eGPIO and wake IRQ metadata.

Important APIs, types, and tables: `PINGROUP()` creates 12-function GPIO groups; slot 0 is GPIO and slot 11 is eGPIO, with `.egpio_enable = 12`, `.egpio_present = 11`, wakeup-present/enabled interrupt bits, and modern 0x1000 GPIO register stride. `SDC_QDSD_PINGROUP()` models non-GPIO SDC2 pins with disabled mux/OE/IRQ fields. `UFS_RESET()` models a reset line with separate control and IO offsets. `kaanapali_pins[]` contains GPIO 0-216 plus `UFS_RESET`, `SDC2_CLK`, `SDC2_CMD`, and `SDC2_DATA`. `kaanapali_functions[]`, group arrays, and `kaanapali_groups[]` cover camera, QUP/I2C/SPI/UART, QSPI, SDC, UIM, USB, display sync, GNSS, DDR BIST/PXI, QDSS, qlink, coex UART, navigation GPIOs, phase flags, and extensive eGPIO groups. `kaanapali_pdc_map[]` maps many GPIOs to PDC wake IRQs. `kaanapali_tlmm` sets `.ngpios = 218`, wake map fields, and `.egpio_func = 11`.

Control flow: `arch_initcall(kaanapali_tlmm_init)` registers `kaanapali-tlmm`. Compatible `qcom,kaanapali-tlmm` probes through `msm_pinctrl_probe()` using `kaanapali_tlmm`.

State and persistence: this file is static descriptor data. eGPIO mode, wake IRQ routing, UFS reset, SDC pin settings, and regular mux/pinconf state persist in TLMM/PDC hardware and common driver objects.

Dependencies and integration: depends on `pinctrl-msm.h`, OF/platform APIs, and common msm support for wakeirq maps and eGPIO fields. It integrates with PDC wakeup, gpiolib, pinctrl DT states, and storage/display/camera/serial subsystems.

Risks: this is a high-blast-radius table: 221 pin descriptors, 217 GPIO pingroup entries, special UFS/SDC groups, and a long PDC map. Off-by-one errors around `.ngpios = 218` versus special groups 217-220 would break GPIO registration or special pinctrl groups. eGPIO slot position must remain aligned with `.egpio_func = 11`. Wake IRQ map mistakes cause suspend/resume failures that compile tests cannot catch.

Test signals: build and probe for `qcom,kaanapali-tlmm`; debugfs shows GPIO and special groups; eGPIO-capable lines can enter/leave eGPIO mode; wake-from-suspend tests on representative `kaanapali_pdc_map` entries; UFS reset and SDC2 pinconf validation; GPIO/IRQ tests; camera, QUP, QSPI, USB, UIM, display sync, qlink, GNSS/coex, and QDSS board tests.
