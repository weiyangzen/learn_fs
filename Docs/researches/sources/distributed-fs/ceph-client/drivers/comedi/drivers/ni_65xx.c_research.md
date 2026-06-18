# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_65xx.c

## Purpose
`ni_65xx.c` supports a broad family of National Instruments PCI/PXI 65xx static digital I/O boards, including 6509, 6510-6519, 6520/6521, and 6528 variants. Depending on the board table, it exposes fixed DI, fixed DO, configurable DIO, and an optional interrupt change-notification subdevice.

## Important APIs, Types, And Functions
`struct ni_65xx_board` describes board names, port counts, and whether legacy output inversion is applicable. `ni_65xx_boards[]` is the central hardware capability table. `ni_65xx_legacy_invert_outputs` is a read-only module parameter that re-enables older Comedi output inversion behavior for selected 6513-6519 boards.

Port math uses `NI_65XX_PORT_TO_CHAN()`, `NI_65XX_CHAN_TO_PORT()`, and `NI_65XX_CHAN_TO_MASK()`. `ni_65xx_dio_insn_config()` handles deglitch filters and DIO direction. `ni_65xx_dio_insn_bits()` reads/writes port windows and applies `s->io_bits` inversion. Edge support is in `ni_65xx_update_edge_detection()`, `ni_65xx_disable_edge_detection()`, `ni_65xx_intr_insn_config()`, `ni_65xx_intr_cmdtest()`, `ni_65xx_intr_cmd()`, `ni_65xx_intr_cancel()`, and `ni_65xx_interrupt()`. `ni_65xx_mite_init()` manually configures the MITE window without taking a full MITE dependency. Attach/detach and PCI registration are `ni_65xx_auto_attach()`, `ni_65xx_detach()`, `ni_65xx_pci_probe()`, and `module_comedi_pci_driver()`.

## Control Flow
PCI probe passes a board index to Comedi auto attach. Attach enables PCI, opens the MITE BAR0 long enough to point the I/O window at BAR1, maps BAR1, clears edge/overflow state, disables interrupts, optionally requests a shared IRQ, logs the hardware ID, and allocates four subdevices. The first three subdevices are populated according to board capabilities: fixed DI starts at port 0, fixed DO starts after the DI ports, and configurable DIO starts at port 0. The fourth subdevice is always created as a one-channel DI status source and becomes command-capable only when an IRQ exists.

Runtime DIO operations iterate from the chanspec base channel to the last affected port, shift user masks into the hardware port window, update outputs, and read back actual port state. Filter config rounds nanosecond values into 200 ns hardware units, clamps to 20 bits, and writes a global filter interval plus per-port enable bits. Edge commands program rising/falling enable registers and use a dummy sample to wake Comedi async consumers on change events.

## State And Persistence
The board table is static. Direction state for configurable DIO is in hardware `IO_SEL` registers. Output inversion is represented through `s->io_bits`; output values are initialized to logical zero. Filter enable bits are read-modify-written from hardware rather than mirrored in a private struct. Edge masks live in hardware registers. The driver does not allocate private state because it relies on board metadata and subdevice fields.

## Dependencies And Integration Points
The driver depends on Comedi PCI helpers, Linux IRQ handling, BAR MMIO accessors, and Comedi DIO/command callbacks. Its MITE setup is a local minimal register write to `MITE_IODWBSR`; unlike NI MIO/TIO drivers, it does not use the full MITE DMA layer.

## Risks
The file comments warn the interrupt subdevice is probably broken for most boards except possibly 6514. Edge notification covers only configured masks and reports no changed-port payload. Filter interval is board-global, so multiple channels cannot hold independent intervals. Legacy inversion is optional and only applied when both module parameter and board metadata opt in; changing that behavior can break old user space. DIO direction writes apply to whole ports, while Comedi config is per-channel, so mixed direction expectations inside one 8-bit port are unsafe.

## Test Signals
Tests should cover each board table entry producing the correct subdevice layout and channel counts, MITE window setup failure paths, fixed DI/DO port offsets, configurable DIO direction query, output inversion under the module parameter, filter rounding/clamping, edge-mask updates across channel ranges 0-95, interrupt rejection for unrelated status bits, and detach disabling interrupts.
