<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/gpio.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/gpio.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/gpio.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 21 macros including `_RC32434_GPIO_H_`, `RC32434_UART0_SOUT`, `RC32434_UART0_SIN`, `RC32434_UART0_RTS`, `RC32434_UART0_CTS`, `RC32434_MP_BIT_22`, `RC32434_MP_BIT_23`, `RC32434_MP_BIT_24`, `RC32434_MP_BIT_25`, `RC32434_CPU_GPIO`, `RC32434_AF_SPARE_6`, `RC32434_AF_SPARE_4`, `RC32434_AF_SPARE_3`, `RC32434_AF_SPARE_2`, `RC32434_PCI_MSU_GPIO`, `GPIO_RDY`, `GPIO_WPX`, `GPIO_ALE`, `GPIO_CLE`, `CF_GPIO_NUM`, `GPIO_BTN_S1`; 1 structs: `rb532_gpio_reg`; 0 enums: none; 3 callable helpers/prototypes: `rb532_gpio_set_ilevel`, `rb532_gpio_set_istat`, `rb532_gpio_set_func`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `rb532_gpio_set_ilevel`, `rb532_gpio_set_istat`, `rb532_gpio_set_func`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `RC32434_AF (4)`, `RC32434_MP (4)`, `RC32434_UART0 (4)`, `CF_GPIO (1)`, `GPIO_ALE (1)`, `GPIO_BTN (1)`, `GPIO_CLE (1)`, `GPIO_RDY (1)`. Typed contracts include `rb532_gpio_reg`. Callable helpers or declarations include `rb532_gpio_set_ilevel`, `rb532_gpio_set_istat`, `rb532_gpio_set_func`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/gpio.h -->
