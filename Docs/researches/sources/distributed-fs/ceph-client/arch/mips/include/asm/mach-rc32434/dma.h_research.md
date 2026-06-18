<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 45 macros including `__ASM_RC32434_DMA_H`, `DMA0_BASE_ADDR`, `DMA_DESC_SIZ`, `DMA_DESC_COUNT_BIT`, `DMA_DESC_COUNT_MSK`, `DMA_DESC_DS_BIT`, `DMA_DESC_DS_MSK`, `DMA_DESC_DEV_CMD_BIT`, `DMA_DESC_DEV_CMD_MSK`, `DMA_DESC_DEV_CMD_BYTE`, `DMA_DESC_DEV_CMD_HLF_WD`, `DMA_DESC_DEV_CMD_WORD`, `DMA_DESC_DEV_CMD_2WORDS`, `DMA_DESC_DEV_CMD_4WORDS`, `DMA_DESC_DEV_CMD_6WORDS`, `DMA_DESC_DEV_CMD_8WORDS`, `DMA_DESC_DEV_CMD_16WORDS`, `DMA_DESC_COF`, `DMA_DESC_COD`, `DMA_DESC_IOF`, `DMA_DESC_IOD`, `DMA_DESC_TERM`, `DMA_DESC_DONE`, `DMA_DESC_FINI`, and 21 more; 4 structs: `dma_desc`, `dma_reg`, `dma_channel`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `dma_desc`, `dma_reg`, `dma_channel` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are `asm/mach-rc32434/rb.h`. Major macro families are `DMA_DESC (22)`, `DMA_CHAN (16)`, `DMA_STAT (5)`, `DMA0_BASE (1)`, `_ (1)`. Typed contracts include `dma_desc`, `dma_reg`, `dma_channel`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma.h -->
