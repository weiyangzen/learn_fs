# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200.c Research

Provides the ISA front-end driver for Amplicon 200 Series digital I/O boards PC212E, PC214E, PC215E, PC218E, and PC272E. It supplies board descriptors and delegates actual subdevice setup to `amplc_dio200_common_attach()`.

`dio200_isa_boards[]` describes each board’s subdevice count, subdevice types (`sd_8255`, `sd_8254`, `sd_intr`), register offsets, valid interrupt-source masks, and clock/gate selection availability. `dio200_attach()` requests a 0x20-byte I/O region and calls the shared attach helper with the optional IRQ. The Comedi driver structure advertises manual attach names and uses `comedi_legacy_detach`.

Manual attach validates base address, then common code creates 8255, 8254, and interrupt subdevices according to the selected board table entry. This file itself holds no runtime state beyond static board metadata. Persistence is delegated to common subdevice state and hardware registers.

Dependencies are `amplc_dio200.h` and legacy Comedi APIs, with tight integration to `amplc_dio200_common.c`. Risks are descriptor correctness for board-specific subdevice order, interrupt masks, and clock/gate feature flags. Tests should instantiate each board name, verify subdevice count/type/order, validate I/O region boundaries, exercise optional IRQ/no-IRQ behavior, and confirm common attach receives the expected IRQ flags and offsets.
