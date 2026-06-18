<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/mmzone.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/mmzone.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/mmzone.h` defines machine memory-zone and node data hooks for `mach-ip27`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 3 macros including `_ASM_MACH_MMZONE_H`, `pa_to_nid`, `hub_data`; 4 structs: `hub_data`, `node_data`, `pglist_data`; 0 enums: none; 1 callable helpers/prototypes: `DECLARE_BITMAP`; 1 extern variables: `__node_data`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `DECLARE_BITMAP`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `asm/sn/addrs.h`, `asm/sn/arch.h`, `asm/sn/agent.h`, `asm/sn/klkernvars.h`. Major macro families are `_ASM (1)`, `hub_data (1)`, `pa_to (1)`. Typed contracts include `hub_data`, `node_data`, `pglist_data`. Callable helpers or declarations include `DECLARE_BITMAP`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is sparsemem, NUMA bootmem setup, pgdat/node data lookup, and platform memory discovery.

## Risks
node-ID and PFN translation mistakes can corrupt memory placement or early page allocator state; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/mmzone.h -->
