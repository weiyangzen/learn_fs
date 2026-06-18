# sources/distributed-fs/ceph-client/drivers/gpib/include/quancom_pci.h

## Purpose

`quancom_pci.h` defines the small Quancom PCI interrupt control/status register contract used by Quancom GPIB boards.

## Important APIs and Constants

- `QUANCOM_IRQ_CONTROL_STATUS_REG` is the register offset, `0xfc`.
- `QUANCOM_IRQ_ASSERTED_BIT` reports an asserted IRQ.
- `QUANCOM_IRQ_ENABLE_BIT` enables IRQ generation; any write clears the interrupt according to the comment.

## Control Flow and Integration

`ines_gpib.c` uses this header for Quancom variants. Its interrupt handler checks the asserted bit and writes the enable bit back to clear/re-enable. Attach writes the enable bit, and detach writes zero when disabling.

## State and Persistence Behavior

No in-memory state is defined. IRQ enable/asserted state is in the device register.

## Dependencies

The header is self-contained with an include guard.

## Risks and Test Signals

Because any write clears the interrupt, careless writes can lose pending state. Test signals are Quancom attach, IRQ clear/re-enable behavior, no interrupt storm, and detach disabling interrupt generation.
