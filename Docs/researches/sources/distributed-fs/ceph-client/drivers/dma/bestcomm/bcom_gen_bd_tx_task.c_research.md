# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_gen_bd_tx_task.c

Purpose: Static BestComm generic buffer-descriptor transmit microcode image for generic and PSC transmit paths.

Important data: `bcom_gen_bd_tx_task[]` contains the BestComm task header, TX descriptor stream, four VAR defaults, and six INC defaults. Comments annotate memory-to-FIFO transfer flow, BD/status updates, and interrupt-producing final operations.

Control flow: No C functions. `bcom_gen_bd_tx_reset()` loads the image and patches enable register, FIFO, BD ring base/last/start, source increments, pragma, initiator, and priority.

State and persistence: The array itself is static read-only module data. Mutable runtime state lives in BestComm SRAM after loading.

Dependencies/integration: Used by `gen_bd.c` and PSC helper APIs; depends on BestComm image format and MPC52xx SDMA/FIFO addressing.

Risks: The wrapper and image must agree on variable and increment offsets. TX completion behavior depends on the microcode TFD/INT bits and BD status updates. Since behavior is firmware-like, regression testing is hardware-oriented.

Test signals: Generic/PSC TX DMA, descriptor ring wrap, interrupt-on-completion, data integrity at FIFO, and reset after active or recently completed transfers.
