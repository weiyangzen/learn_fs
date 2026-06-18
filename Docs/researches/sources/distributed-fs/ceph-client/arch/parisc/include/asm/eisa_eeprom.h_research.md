# sources/distributed-fs/ceph-client/arch/parisc/include/asm/eisa_eeprom.h

Purpose: describes PA-RISC EISA EEPROM record layouts and constants used to decode EISA slot configuration.

Important APIs/types/functions: defines packed resource structures for board IDs, functions, memory, IRQ, DMA, port, and initialization data plus constants for EISA configuration tags.

Control flow: EISA setup reads EEPROM bytes, interprets records through these layouts, and registers resources for legacy drivers.

State and persistence: EEPROM contents are platform firmware/hardware state; decoded resources persist in kernel device/resource structures. Dependencies and integration: used by EISA bus probing and resource assignment.

Risks and test signals: structure packing or endian mistakes misroute IRQ/DMA/IO ranges. Test by decoding known EEPROM dumps and comparing registered resources to firmware setup screens.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
