# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc236.c Research

Provides the ISA front-end driver for the Amplicon PC36AT digital I/O board. The board has one 8255 DIO device and an optional interrupt pseudo-DI subdevice.

`pc236_attach()` allocates `struct pc236_private`, requests a 4-byte I/O region, and calls `amplc_pc236_common_attach()` with base address and optional IRQ. `pc236_boards[]` contains the single board name. The Comedi driver uses manual attach and `comedi_legacy_detach`.

Attach is manual: base address and IRQ come from Comedi config. The front-end does not itself create subdevices; the common helper initializes an 8255 subdevice and optionally an interrupt subdevice if IRQ request succeeds. Persistent state is limited to private data allocated here and then managed by the common helper.

Dependencies are `amplc_pc236.h` and legacy Comedi APIs, with direct integration to `amplc_pc236_common.c`. Risks are mostly configuration-related: invalid I/O bases, missing IRQ jumper, or common attach failure after region allocation. Tests should verify region validation, private allocation, optional IRQ behavior, and board-name table setup.
