# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/Kconfig

## Purpose
Defines the build-time configuration symbol for the i.MX IPUv3 core driver. `CONFIG_IMX_IPUV3_CORE` is the switch that enables the base Image Processing Unit support used by i.MX5/i.MX6 display, capture, and image-processing clients.

## Important APIs, Types, and Functions
This file has no C APIs. Its important interface is the `tristate "IPUv3 core support"` Kconfig symbol. It constrains availability to `SOC_IMX5 || SOC_IMX6Q || COMPILE_TEST`, adds a DRM consistency dependency (`DRM || !DRM`) so the core is not built-in while DRM is modular, and selects `BITREVERSE`, `GENERIC_IRQ_CHIP`, and `GENERIC_ALLOCATOR if DRM`.

## Control Flow
Kconfig evaluation decides whether `IMX_IPUV3_CORE` can be disabled, built in, or built as a module. The selected helper symbols then make APIs used by the C implementation available, especially bit reversal for CPMEM/IC bitfield packing, generic IRQ chips for IPU interrupt domains, and genalloc for PRE IRAM allocation when DRM is enabled.

## State and Persistence
The only persistent state is the generated kernel configuration. It determines object inclusion and whether dependent symbols are forced on.

## Dependencies and Integration Points
Integrated directly with `drivers/gpu/ipu-v3/Makefile`, which builds `imx-ipu-v3.o` when this symbol is enabled. It also coordinates with DRM build mode because the IPU core has client devices used by DRM display components.

## Risks
The `DRM || !DRM` dependency is easy to misunderstand but prevents invalid link combinations. Broad `COMPILE_TEST` exposure increases build coverage but may expose architecture assumptions in code paths that normally run only on i.MX SoCs.

## Test Signals
Build matrix signals matter most: i.MX5/i.MX6 built-in, modular, DRM modular, DRM disabled, and COMPILE_TEST builds. Kconfig warnings or unresolved symbols around `bitrev`, generic IRQ chips, or genalloc indicate dependency drift.
