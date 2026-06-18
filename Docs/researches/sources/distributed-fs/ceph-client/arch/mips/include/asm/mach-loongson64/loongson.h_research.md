<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson.h` declares board, firmware, memory, and platform-data contracts for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 136 macros including `__ASM_MACH_LOONGSON64_LOONGSON_H`, `delay`, `LOONGSON_REG`, `LOONGSON3_REG8`, `LOONGSON3_REG32`, `LOONGSON_FLASH_BASE`, `LOONGSON_FLASH_SIZE`, `LOONGSON_FLASH_TOP`, `LOONGSON_LIO0_BASE`, `LOONGSON_LIO0_SIZE`, `LOONGSON_LIO0_TOP`, `LOONGSON_BOOT_BASE`, `LOONGSON_BOOT_SIZE`, `LOONGSON_BOOT_TOP`, `LOONGSON_REG_BASE`, `LOONGSON_REG_SIZE`, `LOONGSON_REG_TOP`, `LOONGSON3_REG_BASE`, `LOONGSON3_REG_SIZE`, `LOONGSON3_REG_TOP`, `LOONGSON_LIO1_BASE`, `LOONGSON_LIO1_SIZE`, `LOONGSON_LIO1_TOP`, `LOONGSON_PCILO0_BASE`, and 112 more; 1 structs: `loongson_system_configuration`; 4 enums: `loongson_fw_interface`, `loongson_cpu_type`, `loongson_bridge_type`; 8 callable helpers/prototypes: `void`, `mach_prepare_reboot`, `mach_prepare_shutdown`, `prom_dtb_init_env`, `prom_lefi_init_env`, `szmem`, `mach_irq_dispatch`, `mach_i8259_irq`; 6 extern variables: `cpu_clock_freq`, `loongson3_smp_ops`, `loongson_fdt_blob`, `loongson_chipcfg`, `loongson_chiptemp`, `loongson_freqctrl`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `void`, `mach_prepare_reboot`, `mach_prepare_shutdown`, `prom_dtb_init_env`, `prom_lefi_init_env`, `szmem`, `mach_irq_dispatch`, `mach_i8259_irq`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/io.h`, `linux/init.h`, `linux/irq.h`, `boot_param.h`. Major macro families are `LOONGSON_GENCFG (20)`, `LOONGSON_ICU (19)`, `LOONGSON_PCICMD (10)`, `LOONGSON_PCIMAP (10)`, `LOONGSON_PCI (8)`, `LOONGSON_MEM (4)`, `LOONGSON_REG (4)`, `LOONGSON3_REG (3)`. Typed contracts include `loongson_system_configuration`. Callable helpers or declarations include `void`, `mach_prepare_reboot`, `mach_prepare_shutdown`, `prom_dtb_init_env`, `prom_lefi_init_env`, `szmem`, `mach_irq_dispatch`, `mach_i8259_irq`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity; the file contains 136 macros, so broad edits have high review cost and should be grouped by register block or bit-field family; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson.h -->
