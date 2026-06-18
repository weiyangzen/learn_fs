# Research: subset-b-001194

Grouped source research for subset B work item `subset-b-001194`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci224.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci224.c

## Purpose
This Comedi PCI driver supports Amplicon PCI224 and PCI234 analog-output boards. It exposes one AO subdevice with instruction writes and asynchronous command output, maps the board's two PCI I/O BARs, programs the on-board 82C54 pacer, and services DAC FIFO interrupts. PCI224 has 16 12-bit AO channels with partly software-selectable ranges; PCI234 has 4 16-bit AO channels with hardware-selectable ranges.

## Important APIs, Types, and Functions
`struct pci224_board` describes model-specific channel count, resolution, range table, hardware DACCON range bits, and range compatibility checks. `struct pci224_private` persists BAR2 base, AO command state, spinlock, scan buffers, interrupt state, `daccon`, enabled-channel mask, and interrupt-enable shadow. Key functions are `pci224_ao_insn_write()`, `pci224_ao_set_data()`, `pci224_ao_cmdtest()`, `pci224_ao_cmd()`, `pci224_ao_start()`, `pci224_ao_handle_fifo()`, `pci224_ao_stop()`, `pci224_ao_munge()`, `pci224_interrupt()`, and `pci224_auto_attach()`. The driver registers through `module_comedi_pci_driver()`.

## Control Flow
Probe enters `amplc_pci224_pci_probe()`, which calls Comedi PCI auto-config and then `pci224_auto_attach()`. Attach enables PCI resources, records BAR2/BAR3, allocates scan-order buffers, globally resets the DAC, configures default FIFO-enabled software-triggered output, allocates an 82C54 pacer, creates the AO subdevice, and optionally requests a shared IRQ. Instruction writes enable one channel, update hardware range bits, reset the FIFO, mangle user samples into the board's 16-bit two's-complement or unsigned format, write `PCI224_DACDATA`, and trigger conversion via `PCI224_SOFTTRIG`.

For asynchronous AO, `pci224_ao_cmdtest()` validates trigger sources, external-trigger exclusivity, timer limits, scan-end count, stop semantics, and channel-list range compatibility. `pci224_ao_cmd()` enables channels, computes hardware scan order by channel number, resets the FIFO with scan trigger temporarily disabled, configures the pacer for timer scans, and arms either an internal trigger callback or an external-start interrupt. `pci224_ao_start()` enables DAC FIFO interrupts. The IRQ handler masks active sources, handles external start/stop and FIFO service, then reenables the shadowed interrupt mask. `pci224_ao_handle_fifo()` derives conservative FIFO room from status bits, pulls scans from the Comedi buffer, writes them in hardware channel order, switches the scan trigger from none to timer or external after preloading, and raises EOA or overflow events. `pci224_ao_stop()` disables board interrupts, waits for any other-CPU IRQ handler to leave, disables channels, and restores instruction-write configuration.

## State and Persistence Behavior
Persistent runtime state is kernel-resident only: Comedi subdevice state/readback, `devpriv->daccon`, `ao_enab`, scan buffers, interrupt-enable shadow, `AO_CMD_STARTED`, and the 8254 divisors. Hardware state persists in DACCON, channel-enable, FIFO, interrupt source, and counter registers until reset, command cancellation, detach, or a subsequent instruction/command. No disk state is written.

## Dependencies and Integration Points
The file depends on Comedi PCI/device APIs, Comedi async buffers/events, `comedi_8254`, Linux PCI IRQ handling, and port I/O helpers. It integrates with the Comedi AO command contract through `do_cmd`, `do_cmdtest`, `cancel`, `munge`, `insn_write`, and `dev->write_subdev`. Timer-based scans use cascaded 82C54 counters Z2-2 and Z2-0.

## Risks
The source comment documents a real first-scan false-trigger risk when switching the DAC scan trigger from none to timer/external while the source is high. FIFO room is inferred from coarse fill-level states, so buffer underrun and EOA handling rely on conservative thresholds. Range changes on PCI224 affect all channels, including channels not in the current instruction. Interrupt stop logic busy-waits on another CPU's handler and depends on correct `intr_cpuid` tracking. The macro `PCI224_INTR_LEVEL_BITS` references a non-existent `PCI224_INTR_DACFIFO`, but it is not used. Timer-resource conflicts are less explicit than in `amplc_pci230.c` because this board has only AO streaming.

## Test Signals
Useful tests include PCI ID probe for both models, AO instruction write/readback over all channels and ranges, command validation failures for duplicate channels and incompatible ranges, timer-paced AO at min and max periods, external start/scan/stop triggers with inversion cases, finite-count EOA after FIFO drains, cancellation during active IRQ load, no IRQ operation fallback, and underrun behavior when the Comedi output buffer starves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci224.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci230.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci230.c

## Purpose
This Comedi PCI driver supports Amplicon PCI230/PCI230+ and PCI260/PCI260+ multifunction boards. It provides AI streaming and instruction reads, optional AO streaming and writes on PCI230-class boards, optional 8255 DIO on PCI230-class boards, 82C54 timer-based pacing, external trigger routing, and hardware-version-specific workarounds for original and plus boards.

## Important APIs, Types, and Functions
`struct pci230_board` captures PCI ID, AI/AO resolution, minimum plus-board hardware version, and DIO presence. `struct pci230_private` stores spinlocks for ISR/resource/AI/AO stop paths, BAR3 DAQ base, hardware version, ADC/DAC control shadows, ADC gain and FIFO threshold shadows, interrupt-enable shadow, resource ownership, and AI/AO running flags. Central functions include `pci230_ai_insn_read()`, `pci230_ao_insn_write()`, `pci230_ai_cmdtest()`, `pci230_ai_cmd()`, `pci230_ai_start()`, `pci230_handle_ai()`, `pci230_ai_stop()`, `pci230_ao_cmdtest()`, `pci230_ao_cmd()`, `pci230_ao_start()`, `pci230_handle_ao_nofifo()`, `pci230_handle_ao_fifo()`, `pci230_ao_stop()`, `pci230_interrupt()`, and `pci230_auto_attach()`.

## Control Flow
Attach detects plus models by PCI region size and hardware version, enables PCI, stores BAR2/BAR3, configures extended functions for PCI260+ external gates and PCI230+ v2 DAC FIFO, resets ADC/DAC FIFOs, requests IRQ, allocates an 82C54 pacer, and creates AI, AO, and DIO subdevices according to board capabilities. AI instruction reads program one channel, gain, unipolar/bipolar and single-ended/differential mode, then use counter Z2-CT2 rather than the built-in software trigger to avoid differential-trigger bugs.

AI command validation enforces trigger compatibility, scan/convert timing limits, all-same reference and polarity, valid repeated ascending channel subsequences, pairwise range restrictions for single-ended channels, and the PCI230+/260+ hardware-version bug requiring multi-channel sequences to start at channel 0. `pci230_ai_cmd()` claims needed counters, programs channel enables/gains, resets FIFO twice with a settling delay, sets CT2 as an initially high conversion source, optionally configures CT0/CT1/CT2 for scans and conversions, and starts immediately or via `inttrig`. `pci230_ai_start()` enables ADC interrupts, switches to the real conversion source, updates FIFO interrupt threshold, and opens timer gates or installs software trigger callbacks. `pci230_handle_ai()` drains FIFO data into the Comedi buffer, detects FIFO overrun, updates trigger level, and raises EOA.

AO supports direct no-FIFO writes and command output. Older boards use CT1 interrupts and immediate DAC writes; hardware version 2+ uses the DAC FIFO. `pci230_ao_cmd()` claims CT1 for timer pacing, programs range and FIFO/channel enable state, gates CT1 until start, and installs an internal start trigger. `pci230_ao_start()` preloads FIFO when available, selects timer/external/software scan trigger, gates timers, and enables the relevant interrupt source. `pci230_interrupt()` masks active sources, dispatches CT1, DAC FIFO, and ADC handlers, reenables the shadow mask, then calls Comedi event handling.

## State and Persistence Behavior
State is held in private shadows for ADC/DAC control, interrupt enables, gains, FIFO threshold, resource owner masks, and running flags. Shared 82C54 counters are protected by `res_spinlock` so AI and AO commands do not simultaneously use the same timer. Hardware register state persists across commands until cancel/reset paths restore FIFOs, trigger sources, timers, and interrupt enables. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on Comedi PCI, Comedi async buffers/events, `comedi_8254`, `comedi_8255`, Linux IRQs, and port I/O. It integrates with the PCI bus through Amplicon IDs 0x0000 and 0x0006, and with Comedi through AI read, AI command, AO write, AO command, DIO 8255, and read/write subdevice registration.

## Risks
The command matrix is complex, and bugs can appear in timer resource ownership, trigger-source combinations, or hardware-version detection. The code has several hardware workarounds: double ADC FIFO reset, settling delay, CT2 software trigger substitution, plus-board channel-0 sequence requirement, and optional v2 DAC FIFO support. Interrupt stop paths spin until another CPU's ISR exits. Some capabilities depend on detected `hwver`, making behavior differ across cards with identical PCI IDs. Buffer underruns/overruns are surfaced as Comedi errors but can also leave hardware FIFOs needing reset.

## Test Signals
Test PCI230, PCI230+, PCI260, and PCI260+ detection; AI insn reads in single-ended and differential modes; AI commands for timer, external, internal, finite, and continuous cases; channel-list rejection cases; simultaneous AI/AO resource conflicts; AO commands on old no-FIFO and v2 FIFO hardware; cancellation from process and interrupt context; 8255 DIO availability only on PCI230-class boards; and error paths for FIFO overrun/underrun and unavailable IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci230.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci236.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci236.c

## Purpose
This file is the PCI-specific wrapper for the Amplicon PCI236 digital I/O board. The board presents a single 8255 DIO device plus an interrupt-backed pseudo-DI subdevice implemented by shared helper code in `amplc_pc236.h`/common source. This wrapper handles PCI probing, PLX9052 local interrupt control, BAR discovery, and delegation to the common PC236 attach logic.

## Important APIs, Types, and Functions
The driver defines `PCI236_INTR_DISABLE` and `PCI236_INTR_ENABLE` bit patterns for the PLX9052 `INTCSR` register. `pci236_intr_update_cb()` enables/disables and clears the local interrupt latch. `pci236_intr_chk_clr_cb()` checks `PLX9052_INTCSR_LI1STAT`, clears the interrupt, and returns whether this device interrupted. `pc236_pci_board` supplies the board name and callbacks to the common layer. `pci236_auto_attach()` allocates `struct pc236_private`, enables PCI, records PLX local config and I/O bases, and calls `amplc_pc236_common_attach()`.

## Control Flow
`amplc_pci236_pci_probe()` invokes Comedi PCI auto-config, which calls `pci236_auto_attach()`. Attach sets the board descriptor, enables the PCI device, stores the PLX local configuration register base from BAR1, stores the 8255 I/O base from BAR2, and delegates subdevice setup and IRQ registration to `amplc_pc236_common_attach(dev, iobase, pci_dev->irq, IRQF_SHARED)`. During command or interrupt use, the common layer calls the wrapper's interrupt callbacks to update or clear PLX9052 local interrupt 1. Removal uses `comedi_pci_detach()`.

## State and Persistence Behavior
The only wrapper-specific persistent state is `pc236_private->lcr_iobase`, plus the common layer's private state such as IRQ enable flag. Hardware interrupt enable and latch state persist in the PLX9052 `INTCSR` register until changed by callbacks or detach. DIO port state is managed by the common PC236 code and the 8255 registers. No disk-backed state exists.

## Dependencies and Integration Points
This file depends on Comedi PCI helpers, Linux IRQ flags, `amplc_pc236` common code, and `plx9052.h` register definitions. It integrates with the PCI vendor/device table for Amplicon 0x0009 and exposes the board through `module_comedi_pci_driver()`.

## Risks
Correct interrupt behavior depends on PLX9052 bit polarity and the common layer's expectations. Enabling interrupts also clears the latch, so ordering matters around command arming. Because the pseudo-DI interrupt subdevice depends on a physical IRQ, configurations without a connected interrupt leave that function unused. The wrapper delegates most validation to common code, so regressions in callback semantics can break both PCI and any related PC236 variants.

## Test Signals
Probe/remove a PCI236 card, verify BAR1/BAR2 selection, exercise 8255 DIO group direction and bit I/O through common code, run the pseudo-DI external-trigger command on port C bit 3, verify shared IRQ filtering, and confirm interrupt disable/enable clears stale latches without losing a real rising edge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci236.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci263.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci263.c

## Purpose
This compact Comedi PCI driver supports the Amplicon PCI263 relay output board. It exposes one 16-channel digital-output subdevice where each bit controls a reed relay and where the output state can be read back from the board's two output registers.

## Important APIs, Types, and Functions
The register map is two byte-wide output ports: `PCI263_DO_0_7_REG` and `PCI263_DO_8_15_REG`. `pci263_do_insn_bits()` is the only subdevice operation; it uses `comedi_dio_update_state()` to merge mask/data writes into `s->state`, writes low and high bytes to hardware, and returns the current state in `data[1]`. `pci263_auto_attach()` enables PCI resources, records BAR2 as `dev->iobase`, allocates one subdevice, initializes its Comedi metadata, and reads the initial relay state. PCI registration is through `amplc_pci263_pci_table` and `module_comedi_pci_driver()`.

## Control Flow
Probe calls Comedi PCI auto-config and then `pci263_auto_attach()`. Attach enables the PCI device, sets up a single writable digital-output subdevice with 16 one-bit channels, and seeds `s->state` from the two hardware bytes so software readback starts in sync with relay hardware. During `insn_bits`, Comedi provides a mask and desired bits; the driver updates `s->state` only if requested bits changed, writes both output bytes, then reports the shadow state.

## State and Persistence Behavior
State is limited to `s->state`, which mirrors the relay output latch. The relay contacts and output latch persist in hardware while the board is powered and are read during attach. There is no private allocation, interrupt state, command state, or disk persistence.

## Dependencies and Integration Points
The file depends on Comedi PCI helpers, Comedi DIO instruction helpers, `range_digital`, PCI vendor ID definitions, and byte port I/O. It integrates with Amplicon PCI device ID 0x000c and exposes a standard `COMEDI_SUBD_DO` subdevice.

## Risks
The driver always writes both bytes after a masked state update, so concurrent users must rely on Comedi serialization around instructions. Relay outputs are physical actuators: stale initial hardware state or unexpected writes can change external circuits. There is no debounce, timing, or relay-settling handling because this is a simple latch driver.

## Test Signals
Validate PCI attach/detach, initial state readback from both bytes, masked writes to low and high relay channels, no hardware write when `comedi_dio_update_state()` reports no change, readback consistency after repeated writes, and behavior across module unload/reload with relays left in nonzero states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci263.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/c6xdigio.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/c6xdigio.c

## Purpose
This legacy Comedi driver supports the Mechatronic Systems C6x_DIGIO DSP daughter card attached at a manually configured base address, typically on a parallel-port-like interface. It exposes two PWM output channels and two 24-bit encoder/counter input channels. The code includes optional PnP registration for standard and ECP printer ports, but actual Comedi attachment still uses the user-supplied I/O base.

## Important APIs, Types, and Functions
The hardware interface has data, status, and control offsets. `c6xdigio_chk_status()` polls bit 7 of the status register until it toggles away from the expected context or times out. `c6xdigio_write_data()` emits command/data bytes and waits for the handshake. `c6xdigio_pwm_write()` serializes a clamped PWM value in 2-bit chunks. `c6xdigio_encoder_read()` reads eight 3-bit chunks to assemble a 24-bit encoder value. Instruction handlers are `c6xdigio_pwm_insn_write()`, `c6xdigio_pwm_insn_read()`, and `c6xdigio_encoder_insn_read()`. `c6xdigio_init()` initializes PWM and resets encoders.

## Control Flow
Module init registers the Comedi driver and, when PnP is enabled, registers a minimal PnP driver for printer-port IDs while ignoring PnP registration failure. Attach requests a 3-byte I/O region at `it->options[0]`, allocates two subdevices, initializes the PWM subdevice as writable and the encoder subdevice as readable `SDF_LSAMPL`, and calls `c6xdigio_init()`. PWM writes clamp values to 2..498, send five two-bit payloads with alternating handshake status expectations, then send an idle command. PWM readback uses packed values in `s->state` rather than private storage. Encoder reads issue an encoder command, read 3 status bits per handshake phase, assemble a 24-bit value, and convert two's-complement hardware format to Comedi offset-binary via `comedi_offset_munge()`.

## State and Persistence Behavior
The driver has no private struct. PWM readback for two channels is packed into the PWM subdevice's `s->state` as two 16-bit fields. Encoder values are read directly from hardware and not cached. Hardware PWM and encoder state persists on the attached daughter card until reset or overwritten. The module-level `c6xdigio_pnp_registered` flag records whether PnP unregister is needed.

## Dependencies and Integration Points
It depends on legacy Comedi attach/detach, `comedi_check_request_region()`, low-level port I/O, optional Linux PnP APIs, and Comedi counter/PWM subdevice conventions. It does not use interrupts despite including interrupt headers.

## Risks
The busy-wait timeout is only 20 polling iterations and has no delay, so slow hardware can fail with `-EBUSY`. Several helper return values are ignored in PWM/encoder paths, so handshake errors may not propagate to users. `c6xdigio_pwm_insn_write()` appears to clear state with `s->state &= (0xffff << (16 * chan))`, which preserves the selected channel bits instead of preserving the other channel; that can corrupt packed readback. Attach calls init even if the daughter card is absent, as noted by the source comment.

## Test Signals
Test manual attach with valid and invalid I/O bases, handshake timeout behavior, PWM clamping and readback on both channels, packed readback preservation when channels are written alternately, encoder reads for positive and negative two's-complement values, init/reset command sequences, PnP registration failure tolerance, and module exit unregister ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/c6xdigio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_das16_cs.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_das16_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcidas.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcidas.c

## Purpose
This Comedi PCI driver supports Measurement Computing PCI-DAS boards using the AMCC S5933 PCI controller. It provides analog input instructions and commands, optional analog output instructions and FIFO commands, 8255 DIO, serial EEPROM reads, and multiple calibration subdevices for caldac, trim potentiometer, and optional DAC08 devices.

## Important APIs, Types, and Functions
`struct cb_pcidas_board` describes each PCI-DAS variant: speed limits, FIFO size, resolution, alternate range table, AO/FIFO support, calibration hardware, and 1602 trigger behavior. `struct cb_pcidas_private` stores 8254 AO pacer, BAR bases, control-register shadows, AMCC interrupt-control shadow, AI/AO bounce buffers, and selected calibration source. Key functions include `cb_pcidas_ai_insn_read()`, `cb_pcidas_ai_cmdtest()`, `cb_pcidas_ai_cmd()`, `cb_pcidas_ai_interrupt()`, `cb_pcidas_ai_cancel()`, AO instruction and command handlers, EEPROM/calibration instruction handlers, `cb_pcidas_interrupt()`, `cb_pcidas_auto_attach()`, and `cb_pcidas_detach()`.

## Control Flow
PCI probe passes a board ID from the device table into Comedi auto-config. Attach enables PCI, records BAR0/BAR1/BAR2/BAR3/BAR4, clears AMCC interrupts, requests a shared IRQ, allocates separate AI and AO 8254 pacers, and creates seven subdevices: AI, optional AO, 8255 DIO, EEPROM memory, 8800 caldac, trim pot, and optional DAC08. Calibration outputs are initialized to midscale. AMCC mailbox interrupt bits are enabled last.

AI instruction reads optionally enable a calibration source, configure channel/range/reference, clear FIFO, software-trigger each conversion, poll EOC, and read samples. AI command validation enforces trigger compatibility, board speed limits, scan-end count, finite stop count, timer divisor normalization, and consecutive same-range channel lists. AI command setup disables calibration, clears trigger/FIFO state, programs mux/gain/reference/pacer source, loads timers for scan or convert pacing, enables selected FIFO interrupts, and configures software or external start trigger including 1602 polarity/mode bits. The AI interrupt handler drains half-full or not-empty FIFO data, handles end-of-burst, detects FIFO overflow, writes into the Comedi buffer, and raises EOA or errors.

AO instruction writes either write directly to per-channel DAC data registers or, for 1602 FIFO boards, clear/load the AO FIFO and arm channel/range bits. AO command support is only enabled for boards with AO FIFO and IRQ. It validates timer or external scan begin, channel order 0 then 1, and finite stop semantics. Command setup enables channels/ranges, clears FIFO, configures the AO pacer, and installs an internal trigger. `cb_pcidas_ao_inttrig()` preloads FIFO, enables half-full/empty interrupts, and starts the DAC. AO interrupts top up the FIFO on half-full and report EOA or underflow on empty.

## State and Persistence Behavior
Control shadows `ctrl`, `ao_ctrl`, and `amcc_intcsr` preserve register bits across interrupt and instruction paths under `dev->spinlock`. AI/AO bounce buffers are fixed arrays in private state. Calibration source and calibration subdevice readbacks persist in kernel memory, while hardware caldac/trimpot/DAC08 outputs persist until changed or reset. Hardware FIFO, trigger, pacer, and AMCC mailbox interrupt state are reset in cancel/detach paths. No disk state is used.

## Dependencies and Integration Points
The driver depends on Comedi PCI, Comedi async buffers/events, `comedi_8254`, `comedi_8255`, AMCC S5933 register definitions, Linux IRQs, delays, and port I/O. It integrates with many Measurement Computing PCI IDs and Comedi calibration/memory subdevice conventions used by `comedi_calibrate`.

## Risks
Interrupt handling spans AMCC mailbox status and board-local status; failure to clear either side can wedge or lose interrupts. AI FIFO draining has a hard 10000-iteration not-empty guard. AO underflow and AI overflow are reported as Comedi errors but depend on timely IRQ service and buffer availability. Control shadows are shared between AI, AO, and calibration paths, requiring correct spinlock coverage. Calibration bitstreams use fixed delays and board-variant assumptions. `cb_pcidas_ao_interrupt()` reads `PCIDAS_AO_REG` through `pcibar4`, although that register is defined under BAR1, which is a suspicious path worth reviewing.

## Test Signals
Test all PCI IDs for correct board descriptors, AI instruction and command acquisition across range/reference modes, external and timer trigger combinations, FIFO half-full/not-empty/EOB paths, finite-count EOA, AI overflow reporting, AO instruction writes on FIFO and no-FIFO boards, AO command FIFO top-up and underflow handling, EEPROM reads, caldac/trimpot/DAC08 readback and hardware writes, 8255 DIO, and detach cleanup of AMCC interrupts and AO pacer allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcidas.c -->
