# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5424.c

Purpose: IPQ5424 TLMM static pinctrl table for the Qualcomm MSM pinctrl core. It maps 50 GPIOs to serial, PCIe, audio, QSPI/SDC, debug, test, WCI, and QDSS functions.

Important APIs, types, and tables: `PINGROUP()` uses the modern 0x1000 register stride and standard TLMM bit positions. `ipq5424_pins[]` lists GPIO 0-49 and `DECLARE_MSM_GPIO_PINS()` creates one-pin group arrays. The function enum and `ipq5424_functions[]` include I2C/SPI/UART names, PTA functions with uppercase identifiers, PCIe0-3, MDIO/MDC master/slave, audio primary/secondary, CXC, WCI, QDSS, PWM, QSPI, SDC, and test functions. `ipq5424_groups[]` has 50 entries, with several intentionally blank GPIOs. `ipq5424_pinctrl` advertises `.ngpios = 50`.

Control flow: the platform driver is registered at `arch_initcall`. A DT node compatible with `qcom,ipq5424-tlmm` triggers `ipq5424_pinctrl_probe()`, which delegates to `msm_pinctrl_probe()`.

State and persistence: no local mutable state. Static metadata persists in the module image; actual mux/config state persists in TLMM registers and common `pinctrl-msm` objects.

Dependencies and integration: depends on Linux OF/platform driver APIs and `pinctrl-msm.h`. Integration is through device-tree pinctrl states naming the functions/groups here, gpiolib line registration, and TLMM GPIO IRQ support from the common core.

Risks: this newer table mixes regular lowercase function names with uppercase `PTA0_0`, `PTA0_1`, `PTA0_2`, `PTA10`, and `PTA11`, so DT binding/name matching must be checked carefully. Multiple blank/reserved-looking GPIOs still appear in `.ngpios`; consumers can request them as GPIO unless constrained externally. PCIe0-3 and audio duplicate function alternatives increase the chance of board DTS selecting the wrong pad.

Test signals: kernel build catches enum/function inconsistencies; probe for `qcom,ipq5424-tlmm`; debugfs shows 50 groups; GPIO direction/value and IRQ tests; peripheral tests for SPI0/SPI1/SPI10/SPI11, UART0/1, I2C, PCIe0-3 wake/clock, MDIO/MDC, QSPI/SDC, audio, PWM, WCI, and QDSS.
