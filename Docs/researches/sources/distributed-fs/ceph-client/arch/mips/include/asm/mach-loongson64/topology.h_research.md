<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/topology.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/topology.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/topology.h` defines or delegates NUMA/topology helpers for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `_ASM_MACH_TOPOLOGY_H`, `cpu_to_node`, `cpumask_of_node`, `cpumask_of_pcibus`, `node_distance`; 1 structs: `pci_bus`; 0 enums: none; 1 callable helpers/prototypes: `pcibus_to_node`; 2 extern variables: `__node_cpumask`, `__node_distances`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `pcibus_to_node`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `asm-generic/topology.h`. Major macro families are `cpumask_of (2)`, `_ASM (1)`, `cpu_to (1)`, `node_distance (1)`. Typed contracts include `pci_bus`. Callable helpers or declarations include `pcibus_to_node`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is scheduler topology, NUMA node lookup, cpumask helpers, and memory-zone placement.

## Risks
incorrect CPU/node mappings hurt locality or break NUMA memory accounting; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/topology.h -->
