# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/fec.c

Purpose: BestComm task wrapper for MPC52xx FEC Ethernet RX and TX DMA. It allocates task/BD resources, loads FEC RX/TX microcode, patches runtime variables, and exports reset/release helpers.

Important APIs/types/functions: Exported functions are `bcom_fec_rx_init`, `bcom_fec_rx_reset`, `bcom_fec_rx_release`, `bcom_fec_tx_init`, `bcom_fec_tx_reset`, and `bcom_fec_tx_release`. Runtime layouts are `bcom_fec_rx_var/inc`, `bcom_fec_tx_var/inc`, and private `bcom_fec_priv`. `self_modified_drd()` finds a TX descriptor word to be patched by microcode.

Control flow: RX init allocates a task with FEC BD size and private FIFO/max buffer data, then calls reset. RX reset disables the task, loads RX image, patches enable/FIFO/BD variables and increments, clears BDs and indices, sets pragma/auto-start/IPR, and clears pending interrupts. TX init is similar but uses `BCOM_FLAGS_ENABLE_TASK`. TX reset loads TX image, sets FIFO and enable, stores the physical address of the self-modified DRD, initializes BD ring variables and increments, configures TX pragma/auto-start/IPR, and clears interrupts.

State and persistence: State lives in `bcom_task`, its private FIFO/maxbuf fields, SRAM microcode variable/inc areas, and BD rings. Reset is destructive to BD contents and indices.

Dependencies/integration: BestComm core APIs, FEC microcode arrays, MPC52xx SDMA/FEC constants, and the network FEC driver that manages packet BDs.

Risks: TX depends on `self_modified_drd()` finding the third DRD from the end; microcode edits can break this. RX/TX variable structures must match microcode offsets. Reset while the network driver owns active BDs must be coordinated externally.

Test signals: FEC RX/TX traffic, descriptor ring wrap, packet-size boundary tests, reset under link cycling, interrupt clearing, and error-free unload.
