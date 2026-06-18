# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5210.c

Purpose: IPQ5210 TLMM pinctrl data driver. It publishes 54 GPIO pins and their mux alternatives to the shared Qualcomm MSM pinctrl core.

Important APIs, types, and tables: `PINGROUP()` creates `struct msm_pingroup` rows with the modern 0x1000-per-GPIO register layout and standard TLMM bit assignments. `ipq5210_pins[]` covers GPIO 0-53. The function enum and `ipq5210_functions[]` expose PON/GPN optics signals, QUP serial engines, audio primary/secondary clocks, PCIe, QSPI/SDC, PWM, QRNG, QDSS, MDIO/MDC master/slave lanes, LEDs, PPS, and test outputs. Group arrays define the legal pins per function, including broad `gpio_groups[]`. `ipq5210_groups[]` has indexed entries `[0]` through `[53]`, and `ipq5210_tlmm` sets `.ngpios = 54`.

Control flow: `arch_initcall(ipq5210_tlmm_init)` registers the platform driver named `ipq5210-tlmm`. A matching device tree node with `qcom,ipq5210-tlmm` calls `ipq5210_tlmm_probe()`, which passes `ipq5210_tlmm` to `msm_pinctrl_probe()`. Removal is the generic platform-driver unregister path through `module_exit()`.

State and persistence: no mutable driver-private state is defined here. Static mux and register metadata persist for the module lifetime; runtime state is in common pinctrl/gpio/irq data and TLMM registers.

Dependencies and integration: includes `<linux/of.h>`, `<linux/platform_device.h>`, and `pinctrl-msm.h`. It integrates with pinctrl DT bindings, gpiolib, and the msm TLMM IRQ path. Board DTS must choose function names from the table and respect pins with empty mux alternatives.

Risks: optical/PON and QUP mappings are dense and easy to misroute if DT uses a legal function on the wrong physical board pin. The table contains explicit empty pingroups such as 24, 25, 29, and 32, so consumers should not assume every GPIO supports a peripheral mux. Incorrect `.nfuncs = 10` or mux ordering would program the wrong function field without local validation.

Test signals: compile and module alias generation; boot log probe for `qcom,ipq5210-tlmm`; pinctrl debugfs reports 54 groups and expected functions; GPIO line direction/value tests; interrupt tests on representative pins; peripheral validation for QUP SE0-SE5, PON/GPN loss/tx signals, QSPI/SDC, PCIe wake/clock request, MDIO/MDC, PWM/LED, PPS, and QDSS.
