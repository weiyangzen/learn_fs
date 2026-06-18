<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/shx3.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/shx3.h

Purpose: defines the SH-X3 GPIO and pin-function namespace used by board and driver code.

Important APIs/types/functions: GPIO_PA6, GPIO_PA5, GPIO_PA4, GPIO_PA3, GPIO_PA2, GPIO_PA1, GPIO_PA0, GPIO_PB6, GPIO_PB5, GPIO_PB4, GPIO_PB3, GPIO_PB2, GPIO_PB1, GPIO_PB0, GPIO_PC6, GPIO_PC5, GPIO_PC4, GPIO_PC3, GPIO_PC2, GPIO_PC1.

Control flow: there is no executable flow; platform code includes the enumerations when requesting GPIOs, pin functions, hardware-block clock/power gates, or DMA slave IDs.

State and persistence: no software state is stored here; the constants name SoC pins, module-stop domains, DMA request lines, and fixed hardware capabilities.

Dependencies/integration: integrates CPU subtype pinmux, GPIO, clock/power, DMA, and board setup code that must share stable numeric identifiers.

Risks: enum order is an ABI-like in-kernel contract for pinctrl/GPIO tables; inserting values in the wrong place misroutes pins or DMA request IDs.

Test signals: build the matching CPU subtype, probe pinctrl/GPIO users, and test peripherals using listed pins, hardware blocks, or DMA slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/shx3.h -->
