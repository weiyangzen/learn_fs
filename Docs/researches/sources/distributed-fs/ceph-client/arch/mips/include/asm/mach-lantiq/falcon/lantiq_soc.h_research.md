<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/lantiq_soc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/lantiq_soc.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/lantiq_soc.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-lantiq/falcon`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 21 macros including `_LTQ_FALCON_H__`, `SOC_ID_FALCON`, `SOC_TYPE_FALCON`, `LTQ_ASC0_BASE_ADDR`, `LTQ_EARLY_ASC`, `LTQ_RST_CAUSE_WDTRST`, `LTQ_STATUS_BASE_ADDR`, `FALCON_CHIPID`, `FALCON_CHIPTYPE`, `FALCON_CHIPCONF`, `SYSCTL_SYS1`, `SYSCTL_SYSETH`, `SYSCTL_SYSGPE`, `BS_FLASH`, `BS_SPI`, `ltq_ebu_w32`, `ltq_ebu_r32`, `ltq_sys1_w32`, `ltq_sys1_r32`, `ltq_sys1_w32_mask`, `LTQ_EBU_PCC_ISTAT`; 0 structs: none; 0 enums: none; 2 callable helpers/prototypes: `pinctrl_falcon_get_range_size`, `pinctrl_falcon_add_gpio_range`; 2 extern variables: `ltq_ebu_membase`, `ltq_sys1_membase`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `pinctrl_falcon_get_range_size`, `pinctrl_falcon_add_gpio_range`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/pinctrl/pinctrl.h`, `lantiq.h`. Major macro families are `ltq_sys1 (3)`, `ltq_ebu (2)`, `BS_FLASH (1)`, `BS_SPI (1)`, `FALCON_CHIPCONF (1)`, `FALCON_CHIPID (1)`, `FALCON_CHIPTYPE (1)`, `LTQ_ASC0 (1)`. Typed contracts include no structs. Callable helpers or declarations include `pinctrl_falcon_get_range_size`, `pinctrl_falcon_add_gpio_range`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/lantiq_soc.h -->
