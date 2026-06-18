# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_mio_cs.c

## Purpose
`ni_mio_cs.c` is the PCMCIA/CardBus-facing Comedi driver for National Instruments DAQCard E-Series devices. It supplies the small bus-specific shell around `ni_mio_common.c`: board identification, I/O-window allocation, IRQ request, Comedi registration, and detach cleanup.

## Important APIs, Types, And Functions
The file defines a static `ni_boards[]` table for DAQCard AI-16XE-50, AI-16E-4, 6062E, 6024E, and 6036E. Entries provide `device_id`, analog input channel count, maxdata, FIFO depth, gain lookup table, AI speed, AO capabilities where present, AO ranges, AO speed, dithering flags, and calibration DAC layout.

`ni_getboardtype()` matches the PCMCIA card id to a board entry. `mio_pcmcia_config_loop()` tries 16-bit I/O windows from `0x000` through `0x3e0` in `0x20` increments using `pcmcia_request_io()`. `mio_cs_auto_attach()` selects the board, enables the PCMCIA function, records `dev->iobase`, requests the IRQ with the shared common `ni_E_interrupt()` handler, allocates common private state, and calls `ni_E_init(dev, 0, 1)`. `mio_cs_detach()` calls `mio_common_detach()` and disables the PCMCIA device.

## Control Flow
The module registers a `pcmcia_driver` and a `comedi_driver` through `module_comedi_pcmcia_driver()`. PCMCIA probe calls `cs_attach()`, which invokes `comedi_pcmcia_auto_config()`. Comedi then calls `mio_cs_auto_attach()`: match `link->card_id`, enable the socket and I/O resource, request the card IRQ, allocate private state, and delegate full subdevice setup to `ni_E_init()`. Removal goes through `comedi_pcmcia_auto_unconfig()` and `mio_cs_detach()`.

## State And Persistence Behavior
Persistent hardware identity is represented only by the static board table and PCMCIA ids. Runtime state lives in the Comedi device, PCMCIA `link->priv`, the assigned I/O base, IRQ number, and `struct ni_private` allocated by the common implementation. No data is written to disk. PCMCIA enable/disable and IRQ ownership are balanced across attach/detach.

## Dependencies And Integration Points
The file depends on Linux module and PCMCIA support, `linux/comedi/comedi_pcmcia.h`, `comedi_8255`, `ni_stc.h`, and the included `ni_mio_common.c`. Because `PCIDMA` is not defined, the common code uses port I/O and non-MITE FIFO paths. The common code still supplies all Comedi subdevices, interrupt handling, AI/AO/DIO/calibration/routing behavior.

## Risks
The I/O-window scan is fixed and could fail on unusual resource layouts. The board match uses `card_id`, so unsupported or misreported card ids attach as `-ENODEV`. Since this build has no MITE DMA, high-rate AI/AO behavior relies on FIFO interrupts and may be more sensitive to interrupt latency. All deep device behavior comes from `ni_mio_common.c`, so board-table accuracy is critical for ranges, timing, FIFO depth, and calibration.

## Test Signals
Attach tests should verify each PCMCIA id maps to the expected board name and capabilities. Resource tests should cover successful and failed I/O allocation, IRQ request failure, detach after partial attach, and card removal while commands are active. Functional tests should cover AI direct reads, interrupt-driven AI commands, AO writes on boards with AO, DIO instructions, calibration subdevice exposure, and clean PCMCIA disable on detach.
