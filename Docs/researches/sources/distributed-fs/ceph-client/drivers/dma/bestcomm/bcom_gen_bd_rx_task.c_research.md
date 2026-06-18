# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_gen_bd_rx_task.c

Purpose: Static BestComm generic buffer-descriptor receive microcode image for PSC and other generic BD consumers.

Important data: `bcom_gen_bd_rx_task[]` includes the standard BestComm header, descriptor words, two default VAR words, and four INC words. The instruction comments show BD traversal, FIFO-to-memory movement, descriptor update, and interrupt generation.

Control flow: No C logic. `gen_bd.c` loads the image in `bcom_gen_bd_rx_reset()`, then patches variables for enable register, FIFO, BD ring base/last/start, buffer size, and increments.

State and persistence: Immutable module data. Runtime state is copied into SRAM and combined with the allocated BD ring.

Dependencies/integration: Consumed by generic BD RX wrappers and PSC convenience initializers. Relies on BestComm loader header interpretation and MPC52xx initiator/IPR constants.

Risks: The microcode is opaque and layout-sensitive. Incorrect max buffer size or initiator selection in the wrapper can make an otherwise valid image misbehave. Edits should be treated as regenerated firmware, not ordinary C changes.

Test signals: PSC or generic peripheral RX DMA, BD ring wrap, interrupt delivery, reset/reload, and data-integrity tests across boundary-sized buffers.
