# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/adf_dh895xcc_hw_data.h

Purpose: declares DH895xCC PF constants used by the PCI driver and hardware-data initializer.

Important definitions: BAR IDs are SRAM 0, PMISC 1, and ETR 2. Fuse constants define SKU extraction, accelerator and AE masks, maximum 6 accelerators, 12 engines, and 32 ETR banks. VF2PF macros translate ERR source/mask registers for lower and upper VF groups. AE-to-function mapping register counts and AE frequency are defined. Firmware filenames are `qat_895xcc.bin` and `qat_895xcc_mmp.bin`.

Control flow and integration: constants feed `adf_dh895xcc_hw_data.c` and `adf_drv.c` during probe, capability setup, interrupt handling, and module firmware declaration.

State and persistence: no runtime state; the constants shape `adf_hw_device_data` fields and hardware CSR access.

Risks and test signals: wrong BAR IDs or mask macros would cause register access to the wrong aperture or lost VF interrupts. Tests should compare constants against hardware documentation and validate that module firmware names match installed firmware files.
