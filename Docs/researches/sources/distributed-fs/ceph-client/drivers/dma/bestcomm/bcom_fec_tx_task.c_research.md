# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_fec_tx_task.c

Purpose: Static BestComm FEC transmit microcode image exposed as `u32 bcom_fec_tx_task[]`.

Important data: The array holds a BestComm task header, TX descriptors, VAR defaults, and INC defaults. The comments decode the microcode sequence that reads transmit BDs, moves data from memory to the FEC FIFO, updates descriptor state, and signals completion.

Control flow: No native C control flow. `bcom_fec_tx_reset()` loads the image, locates a self-modified DRD within the copied descriptor stream, and patches task variables including FIFO, enable register, BD ring bounds, BD start, and the DRD physical address.

State and persistence: Compiled read-only data only. Runtime state lives in BestComm SRAM descriptors and caller-owned BDs after loading.

Dependencies/integration: Used by the FEC task wrapper, BestComm loader, and MPC52xx FEC networking path.

Risks: TX uses a self-modified descriptor, so descriptor order/count must match `self_modified_drd()` expectations. Microcode and wrapper variable layouts are tightly coupled. Broken interrupt/TFD semantics could cause stuck TX queues.

Test signals: FEC transmit throughput and packet integrity, completion interrupt behavior, reset after TX activity, and verification that `self_modified_drd()` finds the intended descriptor.
