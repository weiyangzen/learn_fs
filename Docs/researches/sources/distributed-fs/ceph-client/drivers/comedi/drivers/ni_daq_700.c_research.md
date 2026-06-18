# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_daq_700.c

## Purpose
`ni_daq_700.c` is a PCMCIA Comedi driver for the NI DAQCard-700. It exposes a fixed 16-channel digital I/O subdevice and a 16-channel single-ended or 8-channel differential analog input subdevice with three bipolar ranges. The IRQ assigned by PCMCIA is not used.

## Important APIs, Types, And Functions
The file defines DAQCard-700 register offsets and `range_daq700_ai`. `daq700_dio_insn_bits()` handles lower-byte outputs and upper-byte inputs. `daq700_dio_insn_config()` forces the fixed output/input split through `s->io_bits = 0x00ff`. `daq700_ai_eoc()` interprets status registers for data-ready, overflow, and busy states. `daq700_ai_rinsn()` configures range/reference/channel, triggers conversions through counter mode writes, clears the FIFO, waits for completion, and converts bipolar offset-binary samples. `daq700_ai_config()` initializes the board. PCMCIA lifecycle is `daq700_auto_attach()`, `daq700_cs_attach()`, and the PCMCIA/Comedi driver tables.

## Control Flow
PCMCIA probe calls `comedi_pcmcia_auto_config()`. Auto attach requests automatic I/O resource assignment, enables the card, records the I/O base, and allocates two subdevices. DIO is fixed: channels 0-7 write to `DIO_W`, channels 8-15 read from `DIO_R`. AI setup writes default command registers to disable scanning, select channel 0, set +/-10 V single-ended mode, configure the onboard counter mode, clear interrupts, and drain FIFO junk.

For each instruction sample, AI read sets differential mode and range bits, selects the mux with scan disabled, delays 2 microseconds for settling, starts conversion by toggling command/counter registers, clears FIFO and junk data, polls `daq700_ai_eoc()`, reads the 12-bit FIFO sample, and XORs bit 11 to convert to Comedi unsigned encoding.

## State And Persistence
DIO output state is kept in `s->state`; direction is fixed by `s->io_bits`. AI has no private state and reprograms mode/channel/range for each instruction. Hardware is initialized once at attach and then reconfigured per AI instruction.

## Dependencies And Integration Points
The file depends on Comedi PCMCIA helpers, Linux delay functions, ISA-style port I/O, and Comedi timeout logic. It registers a PCMCIA manufacturer/card ID pair for auto attach.

## Risks
The driver uses polled AI only, so high-rate acquisition is unsupported. The conversion sequence relies on specific counter-mode writes and a fixed 2 us mux-settling delay. `daq700_ai_eoc()` returns overflow if status register 2 has either low bit set; hardware status interpretation should not be changed casually. DIO direction requests are accepted through Comedi config but then forced back to fixed hardware direction.

## Test Signals
Test signals include PCMCIA resource enable failure, fixed DIO split and readback composition, rejecting attempts to make fixed input channels outputs via the final `io_bits`, AI range hardware encoding where user range 1/2 maps to hardware 2/3, differential mode bit selection, mux settle delay presence, FIFO clear/junk read sequence, timeout paths for busy/no data/overflow, and offset-binary conversion.
