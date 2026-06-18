# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq9574.c

Purpose: IPQ9574 TLMM static descriptor for 65 GPIOs, including a reserved GPIO entry for QFPROM LDO control.

Important APIs, types, and tables: `PINGROUP()` is the modern Qualcomm TLMM descriptor macro with 0x1000 stride and standard bit definitions. `ipq9574_pins[]` covers GPIO 0-64. The enum and `ipq9574_functions[]` cover SDC/QSPI, BLSP0-5, PCIe0-3, audio/PDM/WSA, QDSS A/B, MDIO/MDC, MAC, CXC, WCI, PTA/PWM, DDR PHY, TRNG/PRNG, and test/debug functions. `ipq9574_groups[]` maps 65 pingroups. `ipq9574_reserved_gpios[] = { 59, -1 }` marks GPIO59 reserved, and `ipq9574_pinctrl` passes that list to the common core.

Control flow: `arch_initcall(ipq9574_pinctrl_init)` registers the platform driver named `ipq9574-tlmm`. OF compatible `qcom,ipq9574-tlmm` probes through `ipq9574_pinctrl_probe()` and `msm_pinctrl_probe()`.

State and persistence: no local mutable state. Reserved GPIO metadata persists as static data; actual hardware state is maintained in TLMM registers and common core structures.

Dependencies and integration: uses Linux OF/platform/module support and `pinctrl-msm.h`. The reserved GPIO integration is important for the common core to deny or hide GPIO59 from generic consumers while keeping pin metadata available.

Risks: GPIO59 is reserved for QFPROM LDO regulator control; exposing or repurposing it can affect fuse/QFPROM operation. PCIe0-3, SDC/QSPI, audio, BLSP, and QDSS mappings overlap heavily, so DTS pinctrl states need board-level review. The common core trusts the sentinel-terminated reserved list; omitting `-1` would be unsafe.

Test signals: build and module OF table; probe on `qcom,ipq9574-tlmm`; debugfs/gpiolib should reflect 65 GPIO groups with GPIO59 reserved behavior; attempted GPIO59 consumer request should fail or be blocked as expected; GPIO/IRQ tests on non-reserved lines; board smoke for SDC/QSPI, BLSP, PCIe0-3, MDIO/MDC, audio/PDM/WSA, PWM/PTA/WCI, and QDSS.
