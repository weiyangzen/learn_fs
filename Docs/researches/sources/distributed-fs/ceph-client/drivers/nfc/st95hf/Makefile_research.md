# sources/distributed-fs/ceph-client/drivers/nfc/st95hf/Makefile

## Purpose
This Makefile maps `CONFIG_NFC_ST95HF` to the ST95HF transceiver driver objects.

## Important build objects
- `obj-$(CONFIG_NFC_ST95HF) += st95hf.o` emits the driver when enabled.
- `st95hf-objs := spi.o core.o` combines SPI transport and digital-core logic into one module/object.

## Control flow and integration
Unlike the ST_NCI and ST21NFCA families in this subset, ST95HF does not split a shared core and physical module here; SPI and core are linked into the same `st95hf` object.

## State, dependencies, and risks
There is no runtime state in the Makefile. Build correctness depends on `spi.o` and `core.o` sharing internal symbols cleanly under one module.

## Test signals
Build `CONFIG_NFC_ST95HF=y` and `m`, run modpost, and verify the linked module includes both SPI and core code paths.
