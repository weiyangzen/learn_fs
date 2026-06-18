<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/xway_dma.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/xway_dma.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/xway_dma.h` describes low-level controller registers and helper macros for `mach-lantiq/xway`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 10 macros including `LTQ_DMA_H__`, `LTQ_DESC_SIZE`, `LTQ_DESC_NUM`, `LTQ_DMA_OWN`, `LTQ_DMA_C`, `LTQ_DMA_SOP`, `LTQ_DMA_EOP`, `LTQ_DMA_TX_OFFSET`, `LTQ_DMA_RX_OFFSET`, `LTQ_DMA_SIZE_MASK`; 4 structs: `ltq_dma_desc`, `ltq_dma_channel`, `device`; 0 enums: none; 9 callable helpers/prototypes: `ltq_dma_enable_irq`, `ltq_dma_disable_irq`, `ltq_dma_ack_irq`, `ltq_dma_open`, `ltq_dma_close`, `ltq_dma_alloc_tx`, `ltq_dma_alloc_rx`, `ltq_dma_free`, `ltq_dma_init_port`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `ltq_dma_enable_irq`, `ltq_dma_disable_irq`, `ltq_dma_ack_irq`, `ltq_dma_open`, `ltq_dma_close`, `ltq_dma_alloc_tx`, `ltq_dma_alloc_rx`, `ltq_dma_free`, `ltq_dma_init_port`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `LTQ_DMA (8)`, `LTQ_DESC (2)`. Typed contracts include `ltq_dma_desc`, `ltq_dma_channel`, `device`. Callable helpers or declarations include `ltq_dma_enable_irq`, `ltq_dma_disable_irq`, `ltq_dma_ack_irq`, `ltq_dma_open`, `ltq_dma_close`, `ltq_dma_alloc_tx`, `ltq_dma_alloc_rx`, `ltq_dma_free`, `ltq_dma_init_port`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/xway_dma.h -->
