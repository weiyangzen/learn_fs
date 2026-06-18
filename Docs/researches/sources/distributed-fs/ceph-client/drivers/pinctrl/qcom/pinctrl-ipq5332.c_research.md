# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5332.c

Purpose: IPQ5332 TLMM pinctrl description for the shared MSM pinctrl driver. The file is static SoC data for GPIO muxing, GPIO mode, pin configuration, and GPIO IRQ register layout.

Important APIs, types, and tables: `PINGROUP()` defines 10 mux slots per GPIO and modern TLMM offsets: control at `REG_SIZE * id`, IO at `+0x4`, interrupt config/status at `+0x8/+0xc`, mux/pull/drive/OE bits at 2/0/6/9, and two-bit detection. `ipq5332_pins[]` and matching `gpioN_pins[]` describe GPIO 0-52. The function enum and `ipq5332_functions[]` cover BLSP, audio primary/secondary, PCIe0-2, QSPI/SDC, MDIO/MDC, PWM, QDSS A/B, WCI/WSI, PTA, MAC, core voltage, TRNG/PRNG, and test/debug functions. `ipq5332_groups[]` has 53 pingroups and `ipq5332_pinctrl` sets `.ngpios = 53`.

Control flow: `ipq5332_pinctrl_init()` is registered as an `arch_initcall`, making TLMM available early. The platform driver matches `qcom,ipq5332-tlmm`; probe calls `msm_pinctrl_probe()` with the static SoC data.

State and persistence: the file stores no runtime state. Persistent hardware effects are register writes performed by the common core when consumers request mux/config/IRQ operations. The static arrays must remain valid for the driver lifetime.

Dependencies and integration: uses `pinctrl-msm.h` macros and `struct msm_pinctrl_soc_data`. It is consumed by device tree pinctrl states and GPIO users, and indirectly by interrupt consumers through the common TLMM irqchip support.

Risks: IPQ5332 has many overlapping mux choices on audio, BLSP, PCIe, and QDSS pins; wrong mux slot order can silently select a different peripheral. GPIO 43 has a ninth-slot `gcc_plltest`, making it an example where late mux positions matter. Empty placeholders `_` rely on the `msm_mux__` sentinel being valid in the common core.

Test signals: successful kernel build, module OF table for `qcom,ipq5332-tlmm`, probe without resource errors, pinctrl debugfs showing 53 GPIOs, gpiolib line tests, IRQ edge/level tests, and board smoke tests for PCIe0-2 wake/clock pins, QSPI/SDC, BLSP buses, MDIO/MDC, audio, WCI/WSI, PWM, and QDSS trace/CTI pins.
