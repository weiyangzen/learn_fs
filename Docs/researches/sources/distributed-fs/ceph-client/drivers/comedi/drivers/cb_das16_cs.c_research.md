# sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_das16_cs.c

## Purpose
This Comedi PCMCIA driver supports Computer Boards PC-CARD DAS16/16 variants, including the AO model. It provides polling analog input, optional bit-banged analog output, nibble-configurable digital I/O, and an 8254 counter subdevice. The code is instruction-oriented; it does not implement asynchronous AI/AO commands.

## Important APIs, Types, and Functions
`struct das16cs_board` captures card name, PCMCIA card ID, AO presence, and 4-bit versus 8-bit DIO. `struct das16cs_private` stores software shadows for `MISC1` and `MISC2`. `das16cs_ai_insn_read()` programs mux, reference mode, gain, software conversion, and polls EOC. `das16cs_ao_insn_write()` bit-bangs a 16-bit serial DAC value through `MISC1` chip-select, clock, and data bits. `das16cs_dio_insn_bits()` and `das16cs_dio_insn_config()` handle DIO data and direction, with low/high nibble grouping. `das16cs_counter_insn_config()` selects internal 100 kHz or external counter clock. `das16cs_auto_attach()` configures PCMCIA resources and all four subdevices.

## Control Flow
The PCMCIA probe calls `comedi_pcmcia_auto_config()`, which reaches `das16cs_auto_attach()`. Attach matches the card ID, enables PCMCIA I/O and IRQ resources, stores the I/O base, allocates private register shadows, allocates an 8254 pacer at `DAS16CS_TIMER_BASE`, and creates AI, optional AO, DIO, and counter subdevices. AI reads set a single-channel mux, disable interrupts, select single-ended or differential mode, set gain bits in `MISC2`, trigger software conversions by writing the AI data register, wait for `DAS16CS_MISC1_EOC`, and read 16-bit samples. AO writes select the non-target DAC line high, clock out bits MSB-first using delays, and finally raise both chip selects to latch the output. DIO config delegates to Comedi's DIO helper and mirrors group direction into `MISC2`.

## State and Persistence Behavior
The private `misc1` and `misc2` shadows preserve output/control bit state across instructions. AO subdevice readback stores last written DAC values. DIO state and direction live in `s->state`/`s->io_bits` and in the hardware DIO and MISC2 registers. The 8254 subdevice persists counter programming, with counters 1 and 2 marked busy for internal pacer use. No filesystem state is written.

## Dependencies and Integration Points
The file depends on Comedi PCMCIA helpers, Comedi 8254 helpers, Comedi DIO/readback APIs, Linux delay functions, and PCMCIA ID matching for manufacturer 0x01c5 cards 0x0039 and 0x4009. It integrates through `module_comedi_pcmcia_driver()`.

## Risks
The driver is marked experimental. The PCMCIA ID table does not include the fallback board entry with unknown device ID, so unmatched variants may not bind. Register shadows are not initialized from hardware before first use, so initial control writes assume zeroed defaults. AO bit-banging uses fixed `udelay(1)` timing and does not serialize against other operations beyond Comedi instruction flow. DIO direction is per nibble, which can surprise per-channel configuration users.

## Test Signals
Test card-ID matching for AO and non-AO cards, AI polling in all ranges and single-ended/differential modes, timeout when EOC never asserts, AO serial write and readback on both channels for AO hardware, DIO low/high nibble direction transitions, counter clock source set/get, and detach/reinsert PCMCIA resource handling.
