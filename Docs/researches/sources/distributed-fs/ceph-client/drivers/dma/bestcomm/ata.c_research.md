# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/ata.c

Purpose: BestComm ATA task wrapper. It allocates a BestComm task, loads ATA microcode, initializes task variables/increments, and exposes helpers to switch RX/TX transfer direction.

Important APIs/types/functions: `bcom_ata_init`, `bcom_ata_rx_prepare`, `bcom_ata_tx_prepare`, `bcom_ata_reset_bd`, and `bcom_ata_release` are exported. `struct bcom_ata_var` maps microcode variables such as task enable register, BD ring base/last/start, and buffer size. `struct bcom_ata_inc` contains signed source/destination/byte increments.

Control flow: init disables BestComm prefetch because ATA DMA cannot tolerate it, allocates a BD-backed task, resets descriptors, loads `bcom_ata_task`, sets task variables to physical addresses and SDMA control register offsets, configures task pragma and auto-start, programs ATA RX/TX initiator priorities, and clears pending task interrupt state. RX/TX prepare updates increments and retargets the microcode initiator to the matching ATA initiator.

State and persistence: State lives in the `bcom_task`, SRAM BD ring, microcode variable/inc areas, and task indices. Reset clears all BDs and rewinds indices. No persistent storage exists.

Dependencies/integration: Depends on `bestcomm.c` core APIs, `bcom_ata_task` microcode, MPC52xx SDMA registers, and exported ATA BestComm header definitions. Consumers are ATA platform drivers using BestComm DMA.

Risks: Prefetch must stay disabled for ATA. The wrapper assumes `bcom_eng` is initialized. Physical address truncation would matter only if platform assumptions changed. Direction preparation must be called before enabling the task for each transfer direction.

Test signals: ATA DMA read/write on MPC5200, descriptor ring reset behavior, interrupt clear/auto-start verification, RX/TX data integrity, and module unload after `bcom_ata_release`.
