<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma_v.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma_v.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma_v.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `_ASM_RC32434_DMA_V_H_`, `DMA_CHAN_OFFSET`, `IS_DMA_USED`, `DMA_COUNT`, `DMA_HALT_TIMEOUT`; 0 structs: none; 0 enums: none; 4 callable helpers/prototypes: `rc32434_halt_dma`, `rc32434_start_dma`, `rc32434_chain_dma`, `__raw_writel`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `rc32434_halt_dma`, `rc32434_start_dma`, `rc32434_chain_dma`, `__raw_writel`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `asm/mach-rc32434/dma.h`, `asm/mach-rc32434/rc32434.h`. Major macro families are `DMA_CHAN (1)`, `DMA_COUNT (1)`, `DMA_HALT (1)`, `IS_DMA (1)`, `_ASM (1)`. Typed contracts include no structs. Callable helpers or declarations include `rc32434_halt_dma`, `rc32434_start_dma`, `rc32434_chain_dma`, `__raw_writel`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma_v.h -->
