# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/gen_bd.c

Purpose: Generic BestComm buffer-descriptor task wrapper for peripherals such as MPC52xx PSC. It provides RX/TX task allocation, reset, release, and PSC-specific convenience constructors.

Important APIs/types/functions: Exported APIs include `bcom_gen_bd_rx_init`, `bcom_gen_bd_rx_reset`, `bcom_gen_bd_rx_release`, `bcom_gen_bd_tx_init`, `bcom_gen_bd_tx_reset`, `bcom_gen_bd_tx_release`, `bcom_psc_gen_bd_rx_init`, and `bcom_psc_gen_bd_tx_init`. Runtime layouts are generic RX/TX var/inc structures and `bcom_gen_bd_priv` carrying FIFO, initiator, IPR, and max buffer size.

Control flow: RX/TX init allocate a `bcom_task` with generic BD ring and private data, then reset. Reset disables the task, loads the proper microcode image, patches enable/FIFO/BD variables, sets increments, clears BDs and ring indices, programs task pragmas and auto-start, writes the caller-specified initiator priority, selects the initiator, and clears pending task interrupt. PSC helper functions translate PSC index to fixed initiator/IPR table entries and call the generic constructors.

State and persistence: Runtime state is per-task and stored in SRAM BD rings plus BestComm variable/inc areas. Reset clears descriptors and indices. No persistent storage.

Dependencies/integration: BestComm core and SRAM APIs, generic BD microcode arrays, MPC52xx PSC constants, and drivers using PSC or generic FIFO DMA.

Risks: `bcom_psc_gen_bd_tx_init` does not bounds-check `psc_num` unlike RX, so callers must pass a valid PSC index. Initiator/IPR values are platform constants and wrong values can stall transfers. Microcode variable offsets must stay synchronized with wrapper structures.

Test signals: PSC RX/TX DMA across all valid PSC ports, invalid PSC index coverage for RX and caller-side TX validation, BD ring wrap, reset after transfer, interrupt delivery, and FIFO data integrity.
