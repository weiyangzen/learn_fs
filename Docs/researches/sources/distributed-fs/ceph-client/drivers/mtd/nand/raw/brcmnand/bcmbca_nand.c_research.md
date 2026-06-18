# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/bcmbca_nand.c

Purpose: BCMBCA platform glue for the shared Broadcom NAND controller. It provides controller-ready interrupt hooks and a cache read helper that avoids unsafe unaligned memory access.

Important APIs/types/functions: `struct bcmbca_nand_soc` embeds `brcmnand_soc` and maps an interrupt base. `bcmbca_nand_intc_ack` and `bcmbca_nand_intc_set` handle `BCMBCA_CTLRDY`. `bcmbca_read_data_bus` uses direct `memcpy` only when cache and destination meet architecture alignment requirements, falling back to `memcpy_fromio`.

Control flow: probe maps `nand-int-base`, installs interrupt and `read_data_bus` hooks, then calls `brcmnand_probe`. The core invokes the data hook during flash-cache PIO reads.

State and persistence: mapped interrupt base and hooks persist. Alignment requirement is compile-time selected: 8 bytes on ARM64, 4 bytes otherwise.

Dependencies/integration: OF compatible `brcm,nand-bcm63138`, named resource `nand-int-base`, and `struct brcmnand_soc` integration.

Risks/test signals: interrupt clear polarity, architecture alignment assumptions, and data corruption if NAND cache is copied incorrectly. Test aligned/unaligned buffers, controller-ready IRQs, MTD I/O, OOB reads, and suspend/resume.
