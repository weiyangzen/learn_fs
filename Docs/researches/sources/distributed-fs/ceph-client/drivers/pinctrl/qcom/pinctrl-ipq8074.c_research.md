# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq8074.c

Purpose: IPQ8074 TLMM pinctrl table for 70 GPIOs, consumed by the common Qualcomm MSM pinctrl core.

Important APIs, types, and tables: `PINGROUP()` uses 0x1000 register stride and standard mux/pull/drive/OE/value/IRQ bit assignments with 10 mux slots. `ipq8074_pins[]` lists GPIO 0-69. The enum/function table includes QPIC, BLSP0-5, MAC address/sideband signals, WCI2A-D, PCM/audio, QDSS A/B, PCIe0/1 reset/wake/clock, LDO update/enable, SD card/write-protect, MDIO/MDC, PTA, PWM, PRNG/TRNG, CXC, LED, and test functions. `ipq8074_groups[]` maps all 70 pingroups and `ipq8074_pinctrl` sets `.ngpios = 70`.

Control flow: `arch_initcall(ipq8074_pinctrl_init)` registers the `ipq8074-pinctrl` platform driver. Device-tree compatible `qcom,ipq8074-pinctrl` selects this driver; probe delegates to `msm_pinctrl_probe()`.

State and persistence: static SoC data only. Pin ownership, mux state, interrupt state, and GPIO values are handled by common pinctrl/gpiolib/irqchip code and hardware registers.

Dependencies and integration: depends on `pinctrl-msm.h` and Linux OF/platform infrastructure. Integrates with board DTS pinctrl nodes for flash, serial, networking sideband, audio, PCIe, LED/PWM, QDSS, and GPIO interrupt consumers.

Risks: QPIC is present on many low GPIOs and overlaps with serial/WCI/MAC/QDSS functions, so DTS mistakes can affect storage or networking. Several function names use `NA` placeholders rather than `_`, so enum/table consistency with `IPQ_MUX_NA`/common handling is important. LDO update/enable pins on PCIe-adjacent groups should be validated on real hardware to avoid power sequencing regressions.

Test signals: build and module table; successful probe for `qcom,ipq8074-pinctrl`; debugfs reports 70 GPIOs; GPIO and IRQ tests; QPIC access, BLSP buses, PCIe0/1 reset/wake, MDIO/MDC, SD card/write protect, audio/PCM, LED/PWM, QDSS, MAC/WCI sideband, and LDO update/enable board tests.
