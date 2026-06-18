<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-jazz/floppy.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-jazz/floppy.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-jazz/floppy.h` implements platform floppy controller I/O, DMA, IRQ, and memory helpers for `mach-jazz`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `__ASM_MACH_JAZZ_FLOPPY_H`; 0 structs: none; 0 enums: none; 29 callable helpers/prototypes: `fd_inb`, `fd_outb`, `fd_enable_dma`, `fd_disable_dma`, `fd_request_dma`, `fd_free_dma`, `fd_clear_dma_ff`, `fd_set_dma_mode`, `fd_set_dma_addr`, `fd_set_dma_count`, `fd_get_dma_residue`, `fd_enable_irq`, `fd_disable_irq`, `fd_request_irq`, and 15 more; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `fd_inb`, `fd_outb`, `fd_enable_dma`, `fd_disable_dma`, `fd_request_dma`, `fd_free_dma`, `fd_clear_dma_ff`, `fd_set_dma_mode`, `fd_set_dma_addr`, `fd_set_dma_count`, and 19 more. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/delay.h`, `linux/linkage.h`, `linux/types.h`, `linux/mm.h`, `asm/addrspace.h`, `asm/jazz.h`, `asm/jazzdma.h`. Major macro families are `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include `fd_inb`, `fd_outb`, `fd_enable_dma`, `fd_disable_dma`, `fd_request_dma`, `fd_free_dma`, `fd_clear_dma_ff`, `fd_set_dma_mode`, `fd_set_dma_addr`, `fd_set_dma_count`, `fd_get_dma_residue`, `fd_enable_irq`, and 17 more. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is legacy floppy block drivers, ISA DMA APIs, platform IRQ allocation, and low-memory DMA buffers.

## Risks
DMA residue/count handling and fixed IRQ/DMA assumptions are fragile on non-PC MIPS systems.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise the specific device path: RTC read/write, floppy DMA/IRQ, timer callbacks, or reset assertion/deassertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-jazz/floppy.h -->
