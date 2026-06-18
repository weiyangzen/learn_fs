# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq6018.c

Purpose: IPQ6018 pinctrl/TLMM SoC description for 80 GPIOs. It lets the common MSM pinctrl driver expose GPIO, mux, pinconf, and GPIO IRQ services for IPQ6018 boards.

Important APIs, types, and tables: `PINGROUP()` describes a 0x1000-per-GPIO register map with 10 mux choices and standard TLMM bit fields. `ipq6018_pins[]` covers GPIO 0-79. The function enum and generated `ipq6018_functions[]` include QPIC, WCI20-23, MAC variants, audio TX/RX and SoundWire, LPASS PCM/PDM/audio, BLSP0-5, PCIe0 reset/wake/clock, SD card/write protect, MDIO/MDC, PTA, PWM banks, PRNG/TRNG, QDSS A/B, and debug/test signals. `ipq6018_groups[]` has 80 entries; `ipq6018_pinctrl` sets `.ngpios = 80`.

Control flow: `arch_initcall(ipq6018_pinctrl_init)` registers `ipq6018-pinctrl`. Matching `qcom,ipq6018-pinctrl` invokes `ipq6018_pinctrl_probe()`, which calls the common `msm_pinctrl_probe()`.

State and persistence: all state in this file is static descriptor data. Runtime state and persistence are in TLMM registers and common msm pinctrl/gpio/irq data structures.

Dependencies and integration: uses OF/platform/module APIs and `pinctrl-msm.h`. It integrates with DT pin states for networking, QPIC flash, BLSP serial buses, LPASS/audio, PCIe, SD detect/write-protect, QDSS, and GPIO IRQ consumers.

Risks: large mux tables have high transcription risk. Several early GPIOs multiplex QPIC with MAC/WCI/QDSS, so wrong DTS states can disrupt boot media or networking. Audio/SoundWire pins require value-before-OE and mux sequencing from the common core; this file must provide correct mux slots. License string differs from SPDX (`GPL v2` vs `GPL-2.0`), which is conventional in older drivers but still worth preserving intentionally.

Test signals: compile coverage and module device table for `qcom,ipq6018-pinctrl`; boot probe; debugfs showing 80 GPIOs; QPIC boot/flash access, BLSP UART/I2C/SPI, PCIe0 reset/wake, SD card detect/write protect, MDIO/MDC, LPASS/audio, PWM, QDSS, GPIO value/direction, and representative GPIO interrupt tests.
