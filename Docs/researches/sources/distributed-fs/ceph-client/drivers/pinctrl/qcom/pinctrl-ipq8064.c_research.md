# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq8064.c

Purpose: IPQ8064 pinctrl data driver for an older Qualcomm IPQ TLMM layout. It describes 69 GPIO-capable groups plus three SDC3-only pin groups.

Important APIs, types, and tables: unlike newer IPQ drivers, the file uses `IPQ_MUX_*` function IDs and a `PINGROUP()` with 0x10 GPIO register stride starting at control offset `0x1000`, IO `0x1004`, interrupt config/status `0x1008/0x100c`, and a separate interrupt target register at `0x400 + 0x4 * id`. Interrupt detection width is one bit and ack-high is enabled. `SDC_PINGROUP()` describes SDC3 clock/cmd/data groups with mux/OE/IRQ fields disabled. `ipq8064_pins[]` lists GPIO 0-68 plus SDC3_CLK/CMD/DATA pins 69-71, but `.ngpios = NUM_GPIO_PINGROUPS` limits GPIO registration to 69.

Control flow: `ipq8064_pinctrl_init()` registers the platform driver early. Matching `qcom,ipq8064-pinctrl` calls `ipq8064_pinctrl_probe()`, delegating to `msm_pinctrl_probe()`.

State and persistence: static const data only. Runtime hardware state persists in the older TLMM register block and common pinctrl/gpio/irq structures.

Dependencies and integration: uses `pinctrl-msm.h`, platform/OF APIs, and the common msm core. Function coverage includes GSBI buses, PCIe control pins, RGMII/MDIO, NAND/SDC1, SDC3 dedicated groups, USB FS/HSIC, TSIF, MI2S/audio, NSS SPI, SATA/SPDIF, SSBI/SPMI, PDM, and PS_HOLD.

Risks: this file is structurally different from the newer REG_SIZE drivers; copying modern offsets or interrupt width would break IPQ8064. SDC3 groups are not GPIOs and have disabled IRQ/OE fields, so generic code paths must respect negative bit positions. `.npins` is 72 while `.ngpios` is 69, which is intentional and should not be “fixed” casually.

Test signals: build and OF alias for `qcom,ipq8064-pinctrl`; debugfs should expose GPIO groups and SDC3 groups distinctly; GPIO and IRQ tests on GPIO 0-68; SDC3 pinconf validation; board tests for GSBI serial, NAND/SDC1/SDC3, PCIe control, MDIO/RGMII, USB, SATA/SPDIF, and PS_HOLD behavior.
