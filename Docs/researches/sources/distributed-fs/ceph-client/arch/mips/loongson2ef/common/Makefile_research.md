# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/Makefile

Purpose: builds shared Loongson2EF platform support and optional CS5536, serial, RTC, PCI, and suspend components.

Important APIs/types/functions: always includes setup/init/env/time/reset/irq/bonito-irq/mem/machtype/platform; optional objects include `pci.o`, `serial.o`, `uart_base.o`, `rtc.o`, `cs5536/`, and `pm.o`.

Control flow: object inclusion follows `CONFIG_PCI`, `CONFIG_LOONGSON_UART_BASE`, `CONFIG_EARLY_PRINTK`, `CONFIG_LOONGSON_MC146818`, `CONFIG_CS5536`, and `CONFIG_SUSPEND`.

State and persistence: build-system only.

Dependencies and integration: provides common boot, interrupt, memory, PCI, and platform-device infrastructure for board subdirectories.

Risks: `serial.o` can be selected by two symbols, so kbuild de-duplication matters. CS5536 VSM directory is required for 2F southbridge PCI config virtualization.

Test signals: Loongson2E/2F config link checks and optional feature matrix builds.
