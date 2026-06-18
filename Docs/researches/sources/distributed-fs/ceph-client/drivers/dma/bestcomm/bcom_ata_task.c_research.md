# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_ata_task.c

Purpose: Static BestComm ATA microcode image compiled as a `u32 bcom_ata_task[]` array for `ata.c` to load into the BestComm engine.

Important data: The array begins with the BestComm task header magic `0x4243544b`, descriptor/variable/increment sizes, followed by task descriptors, default VAR words, and INC words. Comments decode the LCD/DRD/EU operations from the Freescale image source.

Control flow: No C control flow exists. At runtime `bcom_load_image()` validates the header, allocates/copies descriptors into SRAM if needed, clears and populates task variable/increment areas, and then `ata.c` patches runtime variables such as BD base and enable register.

State and persistence: The compiled array is read-only module data. Operational state is created only after the BestComm core copies it to SRAM task descriptor, variable, and increment regions.

Dependencies/integration: Consumed by `bcom_ata_init()` through the external `bcom_ata_task` symbol. It depends on the BestComm task image ABI used by `bestcomm.c`.

Risks: Header sizes must match the actual descriptor/VAR/INC payload or the loader will copy wrong ranges. Since this is opaque microcode, behavioral testing must be end-to-end. Edits to constants without regenerating from known-good Freescale sources are high risk.

Test signals: Successful `bcom_load_image()` during ATA init, ATA DMA data integrity, expected interrupt behavior, and no BestComm invalid-microcode errors.
