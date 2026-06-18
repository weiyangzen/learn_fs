# sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/ata.h

Purpose: declares the MPC52xx BestComm ATA DMA task wrapper used by the PATA driver to configure and run ATA receive/transmit DMA buffer descriptors.

Important APIs and types: `struct bcom_ata_bd` contains status, source physical address, and destination physical address. Public functions are `bcom_ata_init()`, `bcom_ata_rx_prepare()`, `bcom_ata_tx_prepare()`, `bcom_ata_reset_bd()`, and `bcom_ata_release()`.

Control flow: the ATA driver allocates a task with queue length and max buffer size, prepares it for RX or TX per command, queues descriptors through generic BestComm helpers, resets descriptor state between commands, and releases the task on teardown.

State and persistence: state is runtime DMA task and descriptor ring content. Physical addresses refer to DMA buffers and FIFO/register endpoints; no persistent storage is owned here.

Dependencies and integration points: depends on `struct bcom_task` from `bestcomm.h`, BestComm engine/private task images, and the MPC52xx ATA/PATA driver.

Risks and test signals: risks include wrong RX/TX preparation, descriptor address direction mistakes, stale status bits after reset, and queue length/max buffer mismatches. Tests should cover PIO fallback, DMA read/write, error reset, task IRQ handling, unaligned/scattered transfers, and release during probe failure.
