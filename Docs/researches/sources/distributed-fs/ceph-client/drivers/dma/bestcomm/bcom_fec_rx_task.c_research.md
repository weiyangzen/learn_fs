# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_fec_rx_task.c

Purpose: Static BestComm FEC receive microcode image exposed as `u32 bcom_fec_rx_task[]`.

Important data: The image contains the BestComm header, RX task descriptors, default variables, and increments. Comments annotate descriptor instructions used to walk buffer descriptors, move packet data from the FEC FIFO to memory, update status, and trigger interrupts.

Control flow: There is no C execution path. `fec.c` loads this image in `bcom_fec_rx_reset()`, then writes runtime variables for the task enable register, FEC FIFO physical address, BD ring bounds/start, and maximum receive buffer size. Increment values are patched in the wrapper.

State and persistence: The array is immutable module data. Active state is in the copied SRAM image and the caller-managed BD ring.

Dependencies/integration: Integrated with `fec.c`, `bcom_load_image()`, BestComm SRAM layout, and MPC52xx FEC driver expectations for RX buffer descriptors.

Risks: Opaque microcode must remain aligned with `struct bcom_fec_rx_var` and `struct bcom_fec_rx_inc`. Header count corruption or descriptor edits could silently break DMA. Endianness and physical address width assumptions are platform-specific.

Test signals: FEC RX packet reception under load, BD status updates, interrupt generation, reset/reload success, and absence of invalid microcode loader diagnostics.
