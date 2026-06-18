# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_pcidio.c

## Purpose
`ni_pcidio.c` is the Comedi PCI driver for National Instruments PCI-DIO-32HS, PXI/PCI-6533, and PCI-6534 high-speed 32-bit digital I/O boards. It supports simple per-line DIO and timed input streaming, primarily through MITE DMA. PCI-6534 additionally requires firmware upload to its FPGAs before normal operation.

## Important APIs, Types, And Functions
The file defines register offsets and bit masks for the DIO protocol engine, FIFO, interrupt flags, port direction/data registers, DMA line control, timing registers, and PCI-6534 firmware/FPGA registers. `struct nidio_board` identifies supported board names, firmware requirements, and DIO speed. `struct nidio96_private` stores MITE attachment, board type, DIO state, cached OP mode bits, a DI MITE channel/ring, and a lock.

DMA helpers are `ni_pcidio_request_di_mite_channel()`, `ni_pcidio_release_di_mite_channel()`, `setup_mite_dma()`, and `ni_pcidio_poll()`. Interrupt handling is in `nidio_interrupt()`, which syncs/acks MITE, drains PIO FIFO data when needed, translates group flags into Comedi events, and calls `comedi_handle_events()`.

Instruction handlers are `ni_pcidio_insn_config()` for DIO direction and timing constraints, `ni_pcidio_insn_bits()` for packed 32-bit port read/write, `ni_pcidio_cmdtest()` for validating streaming commands, `ni_pcidio_cmd()` for programming timed or external-request input acquisition, `ni_pcidio_inttrig()` for internal command start, `ni_pcidio_cancel()` for stopping DMA/interrupts, and `ni_pcidio_change()` for MITE buffer updates.

PCI-6534 firmware support is implemented by `pci_6534_load_fpga()`, `pci_6534_reset_fpga()`, `pci_6534_reset_fpgas()`, `pci_6534_init_main_fpga()`, and `pci_6534_upload_firmware()`, using `comedi_load_firmware()` and the declared firmware filenames.

## Control Flow
PCI probe calls `ni_pcidio_pci_probe()`, which delegates to Comedi PCI auto-config. `nidio_auto_attach()` selects the board by driver data, enables PCI resources, allocates private state, attaches MITE, allocates a DI ring, optionally uploads PCI-6534 firmware, resets board DIO/interrupt state, allocates one DIO subdevice, assigns instruction/command/poll callbacks, and requests the shared IRQ.

For simple DIO, Comedi instruction calls update `s->io_bits` and `s->state`, then write `PORT_PIN_DIRECTIONS(0)` or `PORT_IO(0)` and read back `PORT_IO(0)`. For streaming input, `ni_pcidio_cmdtest()` accepts `TRIG_NOW`/`TRIG_INT` starts, `TRIG_TIMER`/`TRIG_EXT` scan begins, `TRIG_NOW` conversion, counted scan ends, and counted or continuous stop. `ni_pcidio_cmd()` forces ports to input, configures all four FIFOs as a 32-bit data path, programs internal or external REQ protocol registers, sets transfer count for counted acquisitions, sets up MITE DMA, clears/enables interrupts, and either starts immediately or installs `ni_pcidio_inttrig()`.

The interrupt handler loops while status reports data left, but caps work to avoid interrupt livelock. It handles transfer-ready PIO fallback, count-expired EOA, waited errors, primary/secondary terminal count EOA, and then reports events to Comedi.

## State And Persistence Behavior
Runtime state is transient and device-local: MITE ring/channel ownership, cached `OP_MODEBits`, subdevice direction/state, and IRQ registration. Firmware blobs are loaded into PCI-6534 FPGA hardware on attach but are not persisted by the driver. The driver declares firmware requirements with `MODULE_FIRMWARE`, so availability is an external deployment concern.

## Dependencies And Integration Points
The driver uses Comedi PCI helpers, Comedi async buffers/events, Linux IRQ/MMIO APIs, MITE DMA helpers, and kernel firmware loading through `comedi_load_firmware()`. The PCI id table maps NI vendor/device ids to board entries, and `module_comedi_pci_driver()` wires the Comedi and PCI driver lifecycles together.

## Risks
The file comments state handshaking is not supported and DMA mostly works only for timed input. DMA channel selection is constrained to channels 1-2. The interrupt handler includes work caps, indicating risk of excessive interrupt processing. PCI-6534 attach can fail if firmware files are missing or FPGA status polling times out. The code contains old comments and some broad assumptions around transfer widths, external trigger semantics, and continuous stop behavior.

## Test Signals
Tests should cover PCI id binding, attach/detach with and without firmware, firmware failure paths, DIO direction and packed bit operations, command validation for timer and external REQ modes, DMA setup/cancel/reuse, interrupt-driven EOA and error events, polling synchronization, and partial attach cleanup after MITE or IRQ failures.
