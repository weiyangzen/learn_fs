# sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/gen_bd.h

Purpose: declares generic BestComm buffer-descriptor task wrappers, including PSC convenience wrappers, for devices that can use simple FIFO-to-buffer or buffer-to-FIFO DMA tasks.

Important APIs and types: `struct bcom_gen_bd` contains descriptor status and buffer physical address. RX/TX initialization functions take queue length, FIFO physical address, initiator, priority, and RX max buffer size. Reset and release functions are provided for both directions. `bcom_psc_gen_bd_rx_init()` and `bcom_psc_gen_bd_tx_init()` pick PSC-specific initiators/FIFOs from a PSC number.

Control flow: client drivers initialize generic RX/TX tasks, queue buffers with the public BestComm ring helpers, process completed descriptors in IRQ paths, reset tasks on stream stop, and release on driver teardown.

State and persistence: state is volatile DMA descriptor ring state and task configuration.

Dependencies and integration points: depends on BestComm core, `phys_addr_t`, PSC/audio/serial style drivers, and task initiator definitions from private BestComm code.

Risks and test signals: risks include wrong initiator/IPR selection, max buffer mismatch, queue cleanup during stop, and PSC wrapper mapping errors. Tests should cover audio/PSC playback and capture, ring reset, transfer underflow/overflow, probe-failure unwind, and concurrent stream start/stop.
