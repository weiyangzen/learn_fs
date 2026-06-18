# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imxrt1170.c

## Purpose
Provides the static pin descriptor table and platform-driver registration for the i.MXRT1170 IOMUXC. Like the RT1050 driver, it is a thin SoC descriptor layer over the common i.MX pinctrl implementation.

## Important APIs, Types, and Functions
`enum imxrt1170_pads` declares reserve pads plus EMC_B1/B2, AD, SD_B1/B2, and display-bank pads. `imxrt1170_pinctrl_pads[]` maps them to `struct pinctrl_pin_desc` entries. `imxrt1170_pinctrl_info` points the common core at the pin table and at `fsl,imxrt1170-iomuxc-gpr`. `imxrt1170_pinctrl_of_match[]`, `imxrt1170_pinctrl_probe()`, `imxrt1170_pinctrl_driver`, and `imxrt1170_pinctrl_init()` complete the OF platform-driver binding.

## Control Flow
`arch_initcall()` registers the driver during early platform initialization. When the OF core instantiates an IOMUXC platform device with `fsl,imxrt1170-iomuxc`, the probe path calls `imx_pinctrl_probe(pdev, &imxrt1170_pinctrl_info)`. All parsing of pin groups, mux values, config values, and register writes happens in the common i.MX code.

## State and Persistence Behavior
No dynamic state is stored here. The static SoC info and pin table persist for the life of the kernel. Hardware mux/config state is stored in IOMUXC registers and represented in common-core per-device structures after probe.

## Dependencies and Integration Points
Depends on the generic pinctrl framework, OF platform matching, and `pinctrl-imx.h`. It is consumed by RT1170 board device trees and peripheral drivers using named/default/sleep pinctrl states for memory, analog, SD/MMC, and display pins.

## Risks
The enum and pin descriptor array must match the binding include files and hardware reference manual. Any missing pad, reserve-count error, or bank-name mismatch can shift pin numbers and misconfigure unrelated hardware. The driver also assumes the common i.MX backend understands the RT1170 binding format and GPR syscon.

## Test Signals
Probe on RT1170 hardware or DT emulation, correct `/sys/kernel/debug/pinctrl` pin names, successful pinctrl state selection for SD, EMC, AD, and display pads, no OF pin-parse failures, and regression builds with `CONFIG_PINCTRL_IMXRT1170` or the enclosing Freescale pinctrl options are the main signals.
