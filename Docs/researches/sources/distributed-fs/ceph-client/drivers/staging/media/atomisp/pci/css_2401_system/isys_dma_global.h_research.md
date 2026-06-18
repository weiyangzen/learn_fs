# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/isys_dma_global.h

Purpose: defines public ISYS 2401 DMA connection, extension, port, and device configuration types.

Important APIs/types/functions: macros name IBUF-to-DDR/VMEM connections and zero/sign extension values. `isys2401_dma_port_cfg_t` stores stride, elements, cropping, and width. `isys2401_dma_connection`, `isys2401_dma_extension`, and `isys2401_dma_cfg_t` describe channel, connection, extension, and transfer height. `N_ISYS2401_DMA_CHANNEL_PROCS` declares channel limits per DMA ID.

Control flow: no direct flow. DMA setup code consumes these types before writing registers.

State and persistence: caller-owned config only; hardware persistence occurs after register writes in private/public DMA helpers.

Dependencies and integration: depends on CSS type support and generated system DMA channel/ID types.

Risks and test signals: comments note duplicated definitions from CSS DMA until a device library exists, so divergence is possible. Tests should compare with DMA v2 expectations and validate port configuration for DDR and VMEM connections.
