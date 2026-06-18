# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_16xx.c

## Purpose

This driver supports ADDI-DATA APCI-1648 and APCI-1696 TTL digital I/O boards. It splits 48 or 96 digital channels into COMEDI DIO subdevices of up to 32 channels each.

## Important APIs, types, and functions

The board table `apci16xx_boardtypes[]` describes board names and total channel counts. Register macros compute per-subdevice input, output, and direction registers. Main callbacks are `apci16xx_insn_config()`, `apci16xx_dio_insn_bits()`, and `apci16xx_auto_attach()`.

## Control Flow

PCI auto-attach selects board data from context, enables the PCI device, stores BAR 0 as `dev->iobase`, computes the number of subdevices needed for all channels, allocates them, and initializes each as readable/writable DIO. Each subdevice defaults all channels to input by writing zero to its direction register. Direction configuration maps the target channel to an eight-bit port mask and updates the whole port via `comedi_dio_insn_config()` before writing `s->io_bits` to the per-subdevice direction register. Bit I/O updates output state when the mask changes, then reads current input state from the input register.

## State and Persistence

State is held in each subdevice's `io_bits` and `state` plus the hardware direction and output registers. There is no private allocation and no persistent storage. Detach uses generic PCI cleanup and does not explicitly reset outputs.

## Dependencies and Integration Points

The file depends on COMEDI PCI helpers and generic COMEDI DIO helpers. It integrates through PCI IDs for APCI-1648 and APCI-1696.

## Risks

The calculation of the last subdevice's channel count deserves attention for non-multiple-of-32 boards; for these board counts it produces 16 for APCI-1648's second subdevice and three full subdevices for APCI-1696. Direction granularity is eight channels, not per channel, and users need query behavior to reflect grouped configuration. Lack of explicit detach reset may leave output states until PCI removal/hardware reset.

## Test Signals

Test signals include correct subdevice/channel counts for both boards, default input direction after attach, grouped direction changes per 8-bit port, output writes, input reads, DIO query results, and clean behavior under `CONFIG_HAS_IOPORT`/PCI resource variants.
