<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/boot_param.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/boot_param.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/boot_param.h` declares board, firmware, memory, and platform-data contracts for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 22 macros including `__ASM_MACH_LOONGSON64_BOOT_PARAM_H_`, `SYSTEM_RAM_LOW`, `SYSTEM_RAM_HIGH`, `SYSTEM_RAM_RESERVED`, `PCI_IO`, `PCI_MEM`, `LOONGSON_CFG_REG`, `VIDEO_ROM`, `ADAPTER_ROM`, `ACPI_TABLE`, `SMBIOS_TABLE`, `UMA_VIDEO_RAM`, `VUMA_VIDEO_RAM`, `MAX_MEMORY_TYPE`, `MEM_SIZE_IS_IN_BYTES`, `LOONGSON3_BOOT_MEM_MAP_MAX`, `MAX_UARTS`, `MAX_SENSORS`, `SENSOR_TEMPER`, `SENSOR_VOLTAGE`, `SENSOR_FAN`, `MAX_RESOURCE_NUMBER`; 26 structs: `efi_memory_map_loongson`, `mem_map`, `efi_cpuinfo_loongson`, `uart_device`, `sensor_device`, `system_loongson`, `irq_source_routing_table`, `interface_info`, `resource_loongson`, `archdev_data`, `board_devices`, `loongson_special_attribute`, `loongson_params`, `smbios_tables`, and 3 more; 2 enums: `loongson_cpu_type`, `loongson_bridge_type`; 3 callable helpers/prototypes: `ls7a_early_config`, `rs780e_early_config`, `virtual_early_config`; 6 extern variables: `loongson_memmap`, `loongson_sysconf`, `eboard`, `einter`, `especial`, `node_id_offset`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `ls7a_early_config`, `rs780e_early_config`, `virtual_early_config`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/types.h`. Major macro families are `SYSTEM_RAM (3)`, `ACPI_TABLE (1)`, `ADAPTER_ROM (1)`, `LOONGSON3_BOOT (1)`, `LOONGSON_CFG (1)`, `MAX_MEMORY (1)`, `MAX_RESOURCE (1)`, `MAX_SENSORS (1)`. Typed contracts include `efi_memory_map_loongson`, `mem_map`, `efi_cpuinfo_loongson`, `uart_device`, `sensor_device`, `system_loongson`, `irq_source_routing_table`, `interface_info`, `resource_loongson`, `archdev_data`, and 7 more. Callable helpers or declarations include `ls7a_early_config`, `rs780e_early_config`, `virtual_early_config`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/boot_param.h -->
