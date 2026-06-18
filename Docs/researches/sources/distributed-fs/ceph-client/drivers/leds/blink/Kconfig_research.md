# sources/distributed-fs/ceph-client/drivers/leds/blink/Kconfig

## Purpose
This file defines hardware blink-capable LED controller drivers. In this subset it exposes Broadcom BCM63138-family LED controller support and Intel Lightning Mountain SSO LED/GPIO support.

## Important APIs, Types, and Functions
The Kconfig symbols are `LEDS_BCM63138` and `LEDS_LGM`. `LEDS_BCM63138` is a tristate LED class driver for MMIO Broadcom SoC LED hardware. `LEDS_LGM` is a tristate driver requiring GPIO, LED class, syscon MFD, and OF support for the LGM Serial Shift Output controller.

## Control Flow
When included by the top-level LED Kconfig, these symbols become visible under LED support. Selecting them controls `drivers/leds/blink/Makefile`, which builds `leds-bcm63138.o` and `leds-lgm-sso.o`.

## State and Persistence
Selections persist in `.config` and determine whether the blink drivers are built in, modular, or omitted. Runtime LED state is owned by the corresponding C drivers.

## Dependencies and Integration Points
`LEDS_BCM63138` depends on `LEDS_CLASS`, `HAS_IOMEM`, `OF`, and Broadcom architecture or `COMPILE_TEST` symbols. `LEDS_LGM` depends on `X86 || COMPILE_TEST`, `GPIOLIB`, `LEDS_CLASS`, `MFD_SYSCON`, and `OF`. These dependencies reflect the drivers' MMIO/syscon, GPIO, and LED class integration.

## Risks and Edge Cases
The Broadcom default of `ARCH_BCMBCA` changes built-in default behavior for that platform. LGM depends on syscon regmap access rather than directly mapped resources, so enabling it without the right firmware node layout will still fail at probe. Kconfig dependency mistakes here can affect compile-test coverage for SoC-specific code.

## Test Signals
Run Kconfig builds with Broadcom, x86 LGM, and `COMPILE_TEST` configurations. Confirm selected symbols produce the expected modules and that disabled `NEW_LEDS` hides these entries. Runtime probe should bind OF compatibles `brcm,bcm63138-leds` and `intel,lgm-ssoled`.
