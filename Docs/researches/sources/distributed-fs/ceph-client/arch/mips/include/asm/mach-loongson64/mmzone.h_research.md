<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/mmzone.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/mmzone.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/mmzone.h` defines machine memory-zone and node data hooks for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 4 macros including `_ASM_MACH_LOONGSON64_MMZONE_H`, `NODE_ADDRSPACE_SHIFT`, `pa_to_nid`, `nid_to_addrbase`; 0 structs: none; 0 enums: none; 1 callable helpers/prototypes: `prom_init_numa_memory`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `prom_init_numa_memory`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `NODE_ADDRSPACE (1)`, `_ASM (1)`, `nid_to (1)`, `pa_to (1)`. Typed contracts include no structs. Callable helpers or declarations include `prom_init_numa_memory`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is sparsemem, NUMA bootmem setup, pgdat/node data lookup, and platform memory discovery.

## Risks
node-ID and PFN translation mistakes can corrupt memory placement or early page allocator state; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/mmzone.h -->
