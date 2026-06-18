# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-spi.h

## Purpose
Defines the classic Freescale SPI controller register layout and bitfields used by `spi-fsl-spi.c` and CPM helpers. It covers mode, event, mask, command, TX/RX data, and GRLIB-specific capability/native chip-select registers.

## Important APIs, Types, And Functions
`struct fsl_spi_reg` describes the register block: `cap`, `mode`, `event`, `mask`, `command`, `transmit`, `receive`, and `slvsel`. Bitfields include `SPMODE_*` for loop, clock polarity/phase, divider, bit order, master/enable, word length, prescaler, and QE CPU operation; `SPCAP_*` for GRLIB capabilities; default `SPMODE_INIT_VAL`; and event/mask bits `SPIE_NE/NF` and `SPIM_NE/NF`.

## Control Flow
The header has no runtime control flow. Its constants drive mode construction, interrupt masking, event handling, and GRLIB capability interpretation in the implementation.

## State And Persistence
No state is owned by the header. It defines the shape of MMIO state used by the controller hardware.

## Dependencies And Integration Points
Used by `spi-fsl-spi.c` for register access and by `spi-fsl-cpm.c` to start CPM transfers through the command register. It relies on big-endian register access wrappers from `spi-fsl-lib.h`.

## Risks
Incorrect bit definitions would directly corrupt controller mode, interrupt, or chip-select behavior. GRLIB fields share the same register block but are variant-specific, so code must only interpret them on matching hardware.

## Test Signals
Register layout compile coverage, mode bit programming for CPOL/CPHA/LSB/loop/word length, interrupt mask/event handling, and GRLIB capability/native CS parsing are the main signals.
