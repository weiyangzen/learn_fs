# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/iproc_nand.c

Purpose: iProc platform glue for the shared Broadcom NAND controller. It handles iProc-specific controller-ready interrupt registers and APB endian/mode switching around NAND FIFO and parameter-page accesses.

Important APIs/types/functions: `struct iproc_nand_soc` embeds `brcmnand_soc`, maps IDM and external register blocks, and uses `idm_lock` for IO-control updates. `iproc_nand_intc_ack` acknowledges controller-ready in the external block. `iproc_nand_intc_set` toggles interrupt-read-enable. `iproc_nand_apb_access` switches APB little-endian mode according to CPU endianness and parameter-vs-data access.

Control flow: probe allocates glue state, initializes the spinlock, maps `iproc-idm` and `iproc-ext`, installs IRQ and data-bus preparation hooks, then calls `brcmnand_probe`. Core PIO/data operations call prepare/unprepare to toggle APB mode under lock.

State and persistence: mapped IDM/ext bases, hook table, and spinlock persist. Hardware IO-control state changes around data access and IRQ enable; core PM restores and reuses hooks on resume.

Dependencies/integration: OF compatible `brcm,nand-iproc`, named resources `iproc-idm` and `iproc-ext`, and `struct brcmnand_soc`.

Risks/test signals: APB endian mode left wrong, missing locking around IDM IO control, LE/BE parameter-read differences, and IRQ bit mistakes. Test parameter-page reads on LE/BE, page/OOB transfers, controller-ready IRQs, suspend/resume, and APB mode stress.
