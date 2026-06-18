<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/lantiq_soc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/lantiq_soc.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/lantiq_soc.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-lantiq/xway`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 63 macros including `_LTQ_XWAY_H__`, `SOC_ID_DANUBE1`, `SOC_ID_DANUBE2`, `SOC_ID_TWINPASS`, `SOC_ID_AMAZON_SE_1`, `SOC_ID_AMAZON_SE_2`, `SOC_ID_ARX188`, `SOC_ID_ARX168_1`, `SOC_ID_ARX168_2`, `SOC_ID_ARX182`, `SOC_ID_GRX188`, `SOC_ID_GRX168`, `SOC_ID_VRX288`, `SOC_ID_VRX282`, `SOC_ID_VRX268`, `SOC_ID_GRX268`, `SOC_ID_GRX288`, `SOC_ID_VRX288_2`, `SOC_ID_VRX268_2`, `SOC_ID_GRX288_2`, `SOC_ID_GRX282_2`, `SOC_ID_VRX220`, `SOC_ID_ARX362`, `SOC_ID_ARX368`, and 39 more; 0 structs: none; 0 enums: none; 3 callable helpers/prototypes: `ltq_pmu_enable`, `ltq_pmu_disable`, `ltq_get_cp1_base`; 1 extern variables: `ltq_cgu_membase`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `ltq_pmu_enable`, `ltq_pmu_disable`, `ltq_get_cp1_base`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `lantiq.h`. Major macro families are `SOC_ID (30)`, `SOC_TYPE (9)`, `LTQ_EBU (6)`, `LTQ_MPS (2)`, `ltq_cgu (2)`, `BS_EXT (1)`, `BS_FLASH (1)`, `BS_MII0 (1)`. Typed contracts include no structs. Callable helpers or declarations include `ltq_pmu_enable`, `ltq_pmu_disable`, `ltq_get_cp1_base`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/lantiq_soc.h -->
