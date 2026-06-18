# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/common.h

Purpose: Provides declarations for the shared Orion platform-device registration helpers implemented in `common.c`.

Important APIs: Declares UART0-3, RTC, GE00/01/10/11, I2C0/1, SPI0/1, XOR0/1, EHCI0/1/2, SATA, crypto, and clkdev initialization functions. It forward-declares `struct mv_sata_platform_data` and includes Ethernet and Orion EHCI platform-data headers for typed parameters.

Control flow and state: Machine-specific `mach-*/common.c` code calls these `__init` helpers during boot, passing MMIO bases, physical resource bases, IRQs, clocks, PHY versions, checksum limits, and platform data. The header itself has no state.

Dependencies and integration: Integrates board files with platform devices in `common.c` and downstream Linux drivers. The missing conventional `#define __PLAT_COMMON_H` after the include guard is unusual; the guard tests `#ifndef __PLAT_COMMON_H` but never defines it, so repeated inclusion will reprocess declarations.

Risks and tests: The include-guard omission can cause duplicate declaration processing and should be audited even if harmless for prototypes. ABI drift between this header and `common.c` breaks board builds. Compile tests should cover all legacy Orion machine files that include this header.
