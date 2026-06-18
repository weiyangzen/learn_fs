# subset-b-001193 Research

Grouped code research for Comedi driver sources under `sources/distributed-fs/ceph-client/drivers/comedi/drivers`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci9111.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci9111.c Research

## Purpose
Implements the Comedi PCI auto-config driver for the ADLink PCI-9111HR multifunction board. It exposes analog input, one analog output, 16 digital inputs, and 16 digital outputs. AI supports synchronous instruction reads and interrupt-driven command acquisition through the board FIFO and 8254 pacer.

## Important APIs, Types, and Functions
`struct pci9111_private_data` stores PLX local-config I/O base, scan-delay bookkeeping, FIFO chunk counters, and a bounce buffer. `pci9111_auto_attach()` enables PCI resources, allocates the 8254 pacer, requests IRQs, and creates four subdevices. `pci9111_ai_do_cmd_test()` validates Comedi trigger combinations; `pci9111_ai_do_cmd()` programs channel/range scan state, the pacer, FIFO, and PLX interrupt routing. `pci9111_interrupt()` drains half-full FIFO events, checks overflow, sets Comedi async events, and clears interrupts. Instruction paths are `pci9111_ai_insn_read()`, `pci9111_ao_insn_write()`, `pci9111_di_insn_bits()`, and `pci9111_do_insn_bits()`.

## Control Flow, State, and Persistence
Attach stores hardware bases from PCI BAR1/BAR2, resets triggers, requests shared IRQ if available, and initializes subdevice capabilities. AI commands require channel lists starting at channel 0, consecutive channels, and a uniform range/reference. Timer conversion mode configures cascaded 8254 counters and uses FIFO half-full interrupts; scan-begin timer spacing is represented as `scan_delay`, and extra samples are discarded in `pci9111_handle_fifo_half_full()`. Instruction AI selects channel/range, resets FIFO, soft-triggers each conversion, waits for EOC, and munges offset-binary data. AO and DO persist only through Comedi readback/state fields and hardware registers; there is no disk persistence.

## Dependencies and Integration Points
Depends on `comedi_pci`, `comedi_8254`, PLX9052 register definitions, Linux IRQ APIs, and raw I/O port access. It integrates with Comedi through `module_comedi_pci_driver`, `comedi_pci_auto_config`, async callbacks, and subdevice readback allocation.

## Risks and Test Signals
The file itself marks the driver experimental and TODOs real testing. Risk concentrates around FIFO overflow handling, timing conversion, external trigger coverage, and the scan-delay discard path. Useful tests include `cmdtest` rejection of nonconsecutive or mixed chanlists, instruction AI timeout behavior, IRQ-source rejection for shared interrupts, FIFO overflow event reporting, AO readback consistency, and detach resetting triggers before PCI teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci9111.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci9118.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci9118.c Research

## Purpose
Implements the Comedi driver for ADLink PCI-9118DG/HG/HR boards. It supports AI, AO, DI, and DO subdevices, with AI offering both instruction reads and complex command acquisition using AMCC S5933 bus-master DMA or interrupt-driven samples.

## Important APIs, Types, and Functions
`struct pci9118_boardinfo` identifies 12-bit, 16-bit, and high-gain variants. `struct pci9118_private` holds AMCC base, DMA capability flags, AI mode state, trigger configuration, S&H settings, DMA buffer positions, and timing limits. `pci9118_ai_cmdtest()` validates trigger compatibility and timing. `pci9118_ai_cmd()` builds real scan lengths with front/back padding for sample-and-hold and 32-bit DMA alignment, chooses acquisition mode, programs the chanlist, DMA, pacer, and trigger sources. `pci9118_interrupt()` handles AMCC aborts, hardware AI error bits, external start/stop triggers, DMA completion, and sample transfer. `pci9118_common_attach()` creates subdevices for both manual and auto attachment.

## Control Flow, State, and Persistence
Manual attach locates an AMCC device by bus/slot; auto attach uses PCI ID context but can only pick the first board type because all supported boards share the same ID. Attach enables PCI bus mastering, maps AMCC and board BARs, allocates an 8254 pacer, resets the board, requests IRQs, and tries to allocate up to two coherent DMA buffers. AI command setup validates channel/reference/range constraints, configures external mux and software sample-hold additions, chooses one of several hardware modes, and starts immediately, waits for internal trigger, or enables external trigger. DMA state persists in `dmabuf[]`, `dma_actbuf`, `ai_act_dmapos`, and `usedma` during acquisition only.

## Dependencies and Integration Points
Uses `amcc_s5933.h` for AMCC registers, Linux DMA coherent allocation, Comedi PCI, Comedi 8254, and Comedi async buffering. It integrates manual `attach`, PCI `auto_attach`, shared IRQs, Comedi readback, and `pci_dev_get()/pci_dev_put()` lifetime management.

## Risks and Test Signals
High-risk areas are DMA length alignment, odd scan lengths, external trigger start/stop transitions, sample-and-hold padding, big-endian DMA sample munging, and board-type ambiguity on auto attach. Tests should exercise `cmdtest` fixups, forced non-DMA fallback, AMCC abort interrupt handling, finite versus never-ending stop conditions, AO reset/readback at midscale, mux limits, and cleanup of coherent buffers on detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci9118.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adq12b.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adq12b.c Research

## Purpose
Provides a legacy ISA-style Comedi driver for the MicroAxial ADQ12-B acquisition/control card. It exposes synchronous analog input, 5 digital inputs, and 8 digital outputs; pacer hardware is documented but not supported.

## Important APIs, Types, and Functions
`struct adq12b_private` caches `last_ctreg` so channel/range changes can be avoided unless necessary. `adq12b_attach()` validates and requests the configured I/O range, allocates private data and three subdevices, and chooses AI range/reference shape from configuration options. `adq12b_ai_insn_read()` programs channel/range, waits for mux settling, triggers conversions through ADC register reads, and polls `adq12b_ai_eoc()`. DIO paths are `adq12b_di_insn_bits()` and `adq12b_do_insn_bits()`.

## Control Flow, State, and Persistence
The attach path is entirely manual through Comedi config options: base address, bipolar/unipolar mode, and single-ended/differential mode. AI reads update the CTREG only when the requested channel/range changes, then perform repeated conversion/poll/read cycles. DO writes iterate over changed bits from `comedi_dio_update_state()` and write encoded channel/value commands to the output buffer register. Runtime state is limited to cached CTREG and Comedi subdevice output state.

## Dependencies and Integration Points
Uses legacy `comedidev`, raw I/O port access, `comedi_check_request_region()`, `comedi_timeout()`, and `module_comedi_driver()`. It detaches through `comedi_legacy_detach`.

## Risks and Test Signals
Risks include stale mux/range state, timeout on EOC polling, and bit-by-bit output register programming. Tests should verify valid base-address stepping, range table selection, differential channel count, mux settle behavior after channel changes, repeated AI retriggering, DI masking to five bits, and DO writes only for changed output bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adq12b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1710.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1710.c Research

## Purpose
Implements PCI auto-config support for Advantech PCI-1710 family multifunction boards, including PCI-1710/HG, PCI-1711, PCI-1713, and PCI-1731. It supports AI command and instruction modes, optional AO, digital I/O, and a user 8254 counter depending on board variant.

## Important APIs, Types, and Functions
`struct boardtype` describes variant capabilities and range tables. `struct pci1710_private` stores control-register mirrors, external-trigger transition state, mux scan value, active chanlist, AO range mirror, and FIFO transfer size. `pci1710_ai_check_chanlist()` enforces continuous/repeating scan segments and differential-channel constraints. `pci1710_ai_cmdtest()` validates timer/external conversion commands; `pci1710_ai_cmd()` programs scan ranges, FIFO, IRQ control, pacer, and optional external-start state. `pci1710_irq_handler()` dispatches FIFO or every-sample handlers. `pci1710_auto_attach()` creates variant-dependent subdevices.

## Control Flow, State, and Persistence
Attach chooses the board from PCI match data, enables BAR2, allocates a 10 MHz 8254 pacer, resets hardware, optionally requests IRQ, and builds subdevices. AI instruction reads enable software trigger, clear FIFO/IRQ, program a single-channel scan, soft-trigger conversions, validate embedded channel tags, and then disable software triggering. Command mode stores a compressed scan segment, programs ranges by channel, clears FIFO, sets one-sample or half-FIFO IRQ behavior, and starts the 8254 when appropriate. Persistent runtime mirrors are `ctrl`, `ctrl_ext`, `mux_scan`, `act_chanlist[]`, `saved_seglen`, `da_ranges`, and Comedi readback/state.

## Dependencies and Integration Points
Uses Comedi PCI, Comedi 8254, Linux shared IRQs, and AMCC header inclusion for this device family. Integrates through `module_comedi_pci_driver`, subdevice command callbacks, Comedi async buffers, and 8254 subdevice support.

## Risks and Test Signals
Primary risks are chanlist validation, embedded channel dropout detection, FIFO full/empty handling, external-start transition from EXT to timer/software control, and board variants with missing AO/DIO. Test signals include `cmdtest` rejection of noncontinuous scans, `pci1710_ai_read_sample()` channel mismatch errors, CMDF_WAKE_EOS every-sample behavior, FIFO half-full transfer count, AO range/readback mirror, counter clock-source config, and reset clearing FIFO/interrupts/outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1710.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1720.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1720.c Research

## Purpose
Provides PCI auto-config support for the Advantech PCI-1720U isolated 4-channel analog output board. It also exposes the 4-bit BoardID switch as a digital input subdevice.

## Important APIs, Types, and Functions
`pci1720_ao_insn_write()` programs per-channel range bits, writes 12-bit DAC data as LSB/MSB bytes, waits for conversion settling, and updates Comedi readback. `pci1720_di_insn_bits()` reads the board ID register. `pci1720_auto_attach()` enables PCI BAR2, allocates AO and BoardID DI subdevices, allocates AO readback, and disables synchronized output mode.

## Control Flow, State, and Persistence
The driver intentionally does not reset analog outputs on attach so jumper-selected hot-reset behavior can preserve hardware output state. Each AO instruction write reads the current range register, updates only the target channel bits, writes the sample, and records the last value in `s->readback`. There is no command streaming or IRQ state. Runtime persistence is limited to hardware DAC/range registers and Comedi AO readback.

## Dependencies and Integration Points
Uses Comedi PCI helpers, raw I/O port access, `comedi_alloc_subdev_readback()`, and `module_comedi_pci_driver()`.

## Risks and Test Signals
The file status is untested. Risks include unsynchronized-output mode being the only supported mode, range register read/modify/write affecting adjacent channels, and current-sink range semantics depending on jumpers. Tests should verify BoardID reads, per-channel range isolation, DAC byte order, readback updates, no attach-time output reset, and sync control set to immediate update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1720.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1723.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1723.c Research

## Purpose
Implements the Advantech PCI-1723 Comedi driver. It exposes an 8-channel 16-bit analog output subdevice and a 16-channel grouped digital I/O subdevice.

## Important APIs, Types, and Functions
`pci1723_ao_insn_write()` writes DAC samples to channel registers and updates readback. `pci1723_dio_insn_config()` configures a whole 8-bit group based on the requested channel, using Comedi DIO helpers and the board DIO control register. `pci1723_dio_insn_bits()` updates output state and reads back the DIO data register. `pci1723_auto_attach()` enables PCI, allocates subdevices, resets AO synchronously to midscale +/-10 V, and initializes DIO direction/state from hardware.

## Control Flow, State, and Persistence
Attach performs a synchronous AO reset: it enters sync mode, sets each channel range, writes midscale data, strobes sync, then returns to async mode. DIO configuration maps channels 0-7 and 8-15 to low/high byte direction bits; `s->io_bits` is the software mirror, while `s->state` mirrors output data. AO state persists in DAC registers and Comedi readback. DIO direction and state are read during attach and then updated through instruction calls.

## Dependencies and Integration Points
Uses Comedi PCI auto attach, Comedi DIO helpers, raw I/O port operations, and subdevice readback allocation.

## Risks and Test Signals
Risks include attach-time AO reinitialization despite TODO notes about reading initial ranges/values, grouped DIO direction surprises when configuring one channel, and unimplemented calibration/current ranges. Tests should check AO reset/readback midscale, DIO group direction encoding, DIO readback after writes, PCI BAR2 enablement, and no unsupported sync mode exposed to users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1723.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1724.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1724.c Research

## Purpose
Provides the Comedi PCI driver for the Advantech PCI-1724U. It exposes 32 analog output channels plus internal calibration subdevices for offset and gain.

## Important APIs, Types, and Functions
`adv_pci1724_insn_write()` is shared by normal AO, offset calibration, and gain calibration; it takes the target DAC mode from `s->private`, waits for DAC idle with `adv_pci1724_dac_idle()`, writes a combined control/data word, and updates readback. `adv_pci1724_auto_attach()` enables PCI, reads/logs the board ID, allocates three subdevices, assigns mode-specific private data, and allocates readback.

## Control Flow, State, and Persistence
Attach creates subdevice 0 for user AO, subdevice 1 for offset calibration, and subdevice 2 for gain calibration. All three use the same write path and the same 14-bit data width. Writes disable synchronous mode before programming a channel, poll `DACSTAT` until idle, and then issue a mode/channel/group/data control word. State persists in DAC/calibration hardware and per-subdevice readback arrays only.

## Dependencies and Integration Points
Uses Comedi PCI, raw 32-bit port I/O, `comedi_timeout()`, Comedi internal calibration subdevice flags, and `module_comedi_pci_driver()`.

## Risks and Test Signals
Risks include calibration values strongly changing real output range, busy-wait timeout behavior, and the nominal 0-20 mA versus 4-20 mA range distinction being calibration-dependent rather than hardware-distinct. Tests should cover board ID read, DAC idle timeout, mode selection per subdevice, readback allocation for all three subdevices, maxdata/range mapping, and sync mode forced off before writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1724.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1760.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1760.c Research

## Purpose
Implements the Advantech PCI-1760 relay and isolated digital input driver. It exposes digital input, relay digital output, PWM configuration, and currently leaves counter support unused.

## Important APIs, Types, and Functions
`pci1760_send_cmd()` and `pci1760_cmd()` implement the board mailbox protocol with feedback matching, clear-between-identical-commands, retries, and timeout returns. `pci1760_di_insn_bits()` reads input status from IMB3. `pci1760_do_insn_bits()` updates relay outputs using `PCI1760_CMD_SET_DO`. `pci1760_pwm_insn_config()` handles arm/disarm, PWM period configuration, status queries, and rounding feedback. `pci1760_reset()` disables interrupts, counters, filters, pattern matching, and initializes counter-related values. `pci1760_auto_attach()` creates four subdevices.

## Control Flow, State, and Persistence
Attach enables PCI BAR0, resets board features through mailbox commands, creates DI/DO/PWM/unused-counter subdevices, and reads current output state with `GET_DO`. Mailbox commands write OMB0-3 and poll IMB2 for command echo, returning IMB0/1 feedback. PWM state is maintained in hardware; the driver derives divisors from nanosecond requests with a 100 usec base and returns `-EAGAIN` when rounded periods differ. DO state is mirrored in Comedi `s->state`.

## Dependencies and Integration Points
Uses Comedi PCI auto attach, Linux bit/time helpers, raw byte I/O, and Comedi PWM instruction config semantics.

## Risks and Test Signals
The driver status is untested. Risks center on firmware mailbox timeouts, retry limits, identical-command clearing, PWM rounding contract, and reset-time command failures being ignored. Tests should cover command timeout paths, DO state readback after `GET_DO`, PWM period rounding and `-EAGAIN`, arm count validation, reset command sequence, and DI reads from the continuously updated mailbox byte.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1760.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci_dio.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci_dio.c Research

## Purpose
Implements a table-driven Comedi PCI driver for many Advantech digital I/O boards in the PCI-173x, PCI-175x, and PCI-176x families. It builds DI, DO, 8255 DIO, board-ID, 8254 counter, and edge-trigger interrupt subdevices according to board descriptors.

## Important APIs, Types, and Functions
`struct dio_boardtype` describes subdevice counts, register offsets, IRQ sources, ID registers, counter base, and 16-bit access mode. `pci_dio_auto_attach()` enables PCI, chooses BARs, resets board-specific interrupt/output features, requests IRQs when supported, and instantiates subdevices from descriptor arrays. `pci_dio_interrupt()` handles PCI-173x-style edge flags and dispatches to `process_irq()`. Async interrupt subdevices use `pci_dio_asy_cmdtest()`, `pci_dio_asy_cmd()`, and `pci_dio_asy_cancel()`. DI/DO helpers handle byte or word register widths. `pci_dio_override_cardtype()` detects PCI-1753 expansion boards.

## Control Flow, State, and Persistence
Probe may temporarily enable/request BAR2 to detect PCI-1753E expansion. Attach stores `boardtype`, resets interrupt registers and channel-freeze controls, and initializes output registers to zero. DI/DO subdevices map directly to descriptor offsets. 8255 groups are delegated to `subdev_8255_io_init()`. IRQ subdevices maintain per-subdevice spinlocks, port offsets, and `cmd_running` flags; command start configures rising/falling edge through `scan_begin_arg & CR_INVERT`, enables interrupt bits, and ISR writes one sample from the port when active. State is in interrupt control mirrors, output `s->state`, and subdevice private offsets.

## Dependencies and Integration Points
Uses Comedi PCI, Comedi 8255/8254 helpers, Linux shared IRQs, raw byte/word I/O, and PCI match data. Integrates through Comedi async command callbacks for edge-trigger DI subdevices.

## Risks and Test Signals
Risks include descriptor mistakes affecting many boards, board-specific interrupt register differences, PCI-1753E detection side effects, shared IRQ filtering only implemented for PCI-173x-style flags, and reset clearing outputs. Tests should cover each board descriptor’s subdevice count, byte versus word DI/DO access, output zeroing, ID-register subdevice creation, counter creation, IRQ edge polarity command args, cancel disabling interrupt bits, and override detection fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci_dio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/aio_aio12_8.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/aio_aio12_8.c Research

## Purpose
Provides a legacy Comedi driver for ACCES I/O PC-104 AIO12-8, AI12-8, and AO12-4 boards. It supports synchronous AI/AO, 8255 DIO, and 8254 counter subdevices, with board variants enabling AI and/or AO.

## Important APIs, Types, and Functions
`struct aio12_8_boardtype` encodes variant names and AI/AO availability. `aio_aio12_8_attach()` requests the I/O region, allocates an 8254 pacer, creates four subdevices, and marks absent AI/AO subdevices unused. `aio_aio12_8_ai_read()` programs ADC mode/range/channel, polls `aio_aio12_8_ai_eoc()`, reads 12-bit data, and munges bipolar two's-complement samples. `aio_aio12_8_ao_insn_write()` enables DAC reference and writes AO registers. `aio_aio12_8_counter_insn_config()` reports clock-source information.

## Control Flow, State, and Persistence
Manual attach validates a 32-byte I/O region, initializes 8254 access, then creates AI, AO, 8255 DIO, and 8254 counter subdevices. AI reads clear the EOC latch by reading status, then perform setup/start/wait/read for each sample. AO writes enable the DAC reference before writing the target DAC and updating readback. Counter config is read-only for clock source reporting. Runtime state is limited to AO readback, 8255 state managed by the helper, and hardware registers.

## Dependencies and Integration Points
Uses legacy Comedi device APIs, `comedi_8255`, `comedi_8254`, `comedi_timeout()`, raw I/O ports, and `module_comedi_driver()`.

## Risks and Test Signals
The driver is marked experimental and only supports synchronous operations. Risks include ADC EOC timeout, bipolar munging correctness, variant subdevice availability, and counter clock metadata. Tests should validate region alignment, AI/AO variant masking, ADC range/channel control byte construction, bipolar offset munging, AO readback, 8255 initialization, and counter clock-source responses for channels 0-2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/aio_aio12_8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/aio_iiro_16.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/aio_iiro_16.c Research

## Purpose
Implements a legacy Comedi driver for the ACCES I/O 104-IIRO-16 isolated input/relay output board. It supports 16 relay outputs, 16 digital inputs, and optional change-of-state interrupt streaming.

## Important APIs, Types, and Functions
`aio_iiro_16_read_inputs()` reads both input bytes. `aio_iiro_16_cos()` is the IRQ handler; it verifies IRQ enable status, reads inputs, packs status bits above the 16 input bits, writes a long sample, and handles Comedi events. `aio_iiro_enable_irq()` toggles board IRQ behavior. `aio_iiro_16_cos_cmdtest()`, `_cmd()`, and `_cancel()` implement the async COS command. `aio_iiro_16_do_insn_bits()` and `_di_insn_bits()` implement relay and input instruction access. `aio_iiro_16_attach()` configures optional IRQ and subdevices.

## Control Flow, State, and Persistence
Attach requests an 8-byte I/O region, disables board IRQs, optionally requests a valid legacy IRQ, creates DO and DI subdevices, and reads initial relay state. If IRQ exists, the DI subdevice becomes command-capable and uses `SDF_LSAMPL` because samples include status bits. Command start enables IRQ by reading the IRQ register; cancel disables by writing zero. Relay state persists in hardware registers and Comedi `s->state`; async command state is implicit in board IRQ enable.

## Dependencies and Integration Points
Uses legacy Comedi APIs, Linux IRQ handling, raw I/O ports, and Comedi async buffering.

## Risks and Test Signals
The driver is experimental. Risks include legacy IRQ validation, IRQ enable/disable side effects based on read versus write operations, and packed sample interpretation. Tests should cover valid IRQ mask handling, IRQ_NONE when status lacks IRQE, relay state initialization and writes, input byte ordering, COS command trigger validation, and cancel disabling further interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/aio_iiro_16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amcc_s5933.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amcc_s5933.h Research

## Purpose
Defines AMCC S5933 PCI controller register offsets and bit masks used by Comedi drivers that need mailbox, FIFO, interrupt, nonvolatile RAM, and bus-master DMA control.

## Important APIs, Types, and Functions
This header exports only macros. Key groups include PCI operation registers (`AMCC_OP_REG_OMB*`, `IMB*`, `FIFO`, `MWAR`, `MWTC`, `MRAR`, `MRTC`, `INTCSR`, `MCSR`), add-on operation registers (`AIMB*`, `AOMB*`, `AFIFO`, `AMWAR`, `AINT`, `AGCSTS`), interrupt control bits (`INTCSR_*`, `AINT_*`), FIFO/status bits (`AGCSTS_*`), nonvolatile RAM commands (`MCSR_NV_*`), and convenience DMA/interrupt aliases such as `EN_A2P_TRANSFERS`, `RESET_A2P_FLAGS`, `ANY_S593X_INT`, `MASTER_ABORT_INT`, and `TARGET_ABORT_INT`.

## Control Flow, State, and Persistence
There is no executable control flow or state. The header is compile-time hardware documentation. Drivers persist relevant AMCC state by writing these registers directly, for example DMA address/count setup and interrupt-status clearing.

## Dependencies and Integration Points
Includes no Linux headers directly but assumes standard integer types such as `u32` are available through including drivers. It is integrated by PCI DAQ drivers such as `adl_pci9118.c` and `adv_pci1710.c`.

## Risks and Test Signals
Risks are macro accuracy, overlapping historical aliases, and comments noting cleanup for bits drawn from different registers. Tests are indirect: compile coverage for users, DMA setup register writes using expected offsets, interrupt abort path recognition, and no conflicting definitions when included with Linux/Comedi headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amcc_s5933.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200.c Research

## Purpose
Provides the ISA front-end driver for Amplicon 200 Series digital I/O boards PC212E, PC214E, PC215E, PC218E, and PC272E. It supplies board descriptors and delegates actual subdevice setup to `amplc_dio200_common_attach()`.

## Important APIs, Types, and Functions
`dio200_isa_boards[]` describes each board’s subdevice count, subdevice types (`sd_8255`, `sd_8254`, `sd_intr`), register offsets, valid interrupt-source masks, and clock/gate selection availability. `dio200_attach()` requests a 0x20-byte I/O region and calls the shared attach helper with the optional IRQ. The Comedi driver structure advertises manual attach names and uses `comedi_legacy_detach`.

## Control Flow, State, and Persistence
Manual attach validates base address, then common code creates 8255, 8254, and interrupt subdevices according to the selected board table entry. This file itself holds no runtime state beyond static board metadata. Persistence is delegated to common subdevice state and hardware registers.

## Dependencies and Integration Points
Includes `amplc_dio200.h` and legacy Comedi APIs. It integrates tightly with `amplc_dio200_common.c`, which consumes `struct dio200_board` layout and handles IRQ commands, counters, and DIO.

## Risks and Test Signals
Risks are descriptor correctness for board-specific subdevice order, interrupt masks, and clock/gate feature flags. Tests should instantiate each board name, verify subdevice count/type/order, validate I/O region boundaries, exercise optional IRQ/no-IRQ behavior, and confirm common attach receives the expected IRQ flags and offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200.h Research

## Purpose
Defines the shared contract between Amplicon DIO200 ISA, PCI, and common helper code.

## Important APIs, Types, and Functions
`enum dio200_sdtype` identifies supported subdevice descriptor types: none, interrupt, 8255, 8254, and timer. `DIO200_MAX_SUBDEVS` and `DIO200_MAX_ISNS` size board descriptor arrays. `struct dio200_board` carries board name, main PCI BAR, subdevice count, per-subdevice type/info arrays, and feature flags for interrupt-source registers, clock/gate selection, and PCIe enhanced behavior. It declares `amplc_dio200_common_attach()` and `amplc_dio200_set_enhance()`.

## Control Flow, State, and Persistence
The header has no runtime control flow. Its structures determine how front-end drivers describe hardware to the common attach path. The bitfields become persistent per-board metadata in static descriptor tables.

## Dependencies and Integration Points
Depends only on Linux types and forward-declares `struct comedi_device`. Included by `amplc_dio200.c`, `amplc_dio200_common.c`, and `amplc_dio200_pci.c`.

## Risks and Test Signals
Risks include descriptor array bounds and ABI coupling between front ends and common helper. Tests are compile-time and attach-time: every board descriptor should stay within max subdevices, valid interrupt source masks should fit `DIO200_MAX_ISNS`, and PCI front ends should provide `mainbar` only where common setup expects it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200_common.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200_common.c Research

## Purpose
Implements common subdevice, interrupt, 8255, 8254, PCIe timer, and I/O abstraction logic for Amplicon DIO200 ISA and PCI(e) drivers.

## Important APIs, Types, and Functions
`dio200_read8/write8/read32/write32()` abstract I/O port versus MMIO and PCIe register spacing. `struct dio200_subdev_intr` stores interrupt subdevice offset, valid/enabled source masks, active flag, and spinlock. `dio200_subdev_intr_*()` implement packed interrupt DI commands. `dio200_subdev_8254_*()` configures counter clock/gate sources and initializes 8254 subdevices. `dio200_subdev_8255_*()` manages 8255 group direction and DIO bits. `dio200_subdev_timer_*()` supports enhanced PCIe timestamp timer reads/config. Exported `amplc_dio200_common_attach()` builds subdevices from `struct dio200_board`; `amplc_dio200_set_enhance()` enables PCIe enhanced features.

## Control Flow, State, and Persistence
Common attach checks I/O-port availability when no MMIO exists, allocates the descriptor-defined subdevice array, initializes each subdevice type, and requests IRQ only if an interrupt subdevice is active. Interrupt commands set `active`, optionally wait for `TRIG_INT`, enable chanlist-selected interrupt sources, and on ISR collect/disable/re-enable latched sources before packing triggered bits into scan order. 8254 config stores selected clock/gate sources in the Comedi 8254 object. 8255 config stores direction in `s->io_bits` and writes the 8255 control word.

## Dependencies and Integration Points
Uses Comedi core, Comedi 8254/8255 helpers, Linux IRQs, raw I/O and MMIO APIs, and the descriptor contract from `amplc_dio200.h`. Exports symbols for front-end modules.

## Risks and Test Signals
Risks include PCIe offset shifting, interrupt-source clearing by temporary disable, race handling around `active/enabled_isns`, and clock/gate source bounds differing between ISA/PCI and PCIe. Tests should cover I/O-port-disabled builds, MMIO versus I/O access, packed interrupt channel order, `TRIG_INT` delayed start, stop-count EOA, 8255 group direction writes, 8254 source get/set including periods, PCIe timer reset/clock config, and IRQ request failure fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200_pci.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200_pci.c Research

## Purpose
Provides the PCI and PCIe front-end for Amplicon DIO200-series boards PCI215, PCI272, PCIe215, PCIe236, and PCIe296. It supplies board descriptors, maps PCI resources, performs PCIe setup, and delegates subdevice creation to the common helper.

## Important APIs, Types, and Functions
`enum dio200_pci_model` indexes board variants. `dio200_pci_boards[]` defines per-board BAR, subdevice layout, offsets, feature flags, and PCIe enhanced status. `dio200_pcie_board_setup()` maps PCI BAR0 bridge registers, enables Avalon-MM to PCIe interrupt generation, and calls `amplc_dio200_set_enhance()`. `dio200_pci_auto_attach()` enables PCI, maps MMIO or I/O BARs, performs PCIe setup, and calls `amplc_dio200_common_attach()` with shared IRQ flags.

## Control Flow, State, and Persistence
PCI probe passes match-table driver data to auto attach. Attach selects descriptor metadata, enables PCI, maps either memory or I/O resources from `mainbar`, configures PCIe boards when needed, then common code creates 8255/8254/timer/interrupt subdevices. Runtime state is mostly common-helper state; this file persists only `dev->board_ptr`, `dev->board_name`, and mapped `dev->mmio` or `dev->iobase`.

## Dependencies and Integration Points
Uses Comedi PCI helpers, Linux PCI BAR/MMIO APIs, IRQF_SHARED, and exported DIO200 common symbols. PCI IDs are conditional for legacy I/O-port boards under `CONFIG_HAS_IOPORT`.

## Risks and Test Signals
Risks include BAR selection mistakes, MMIO mapping failure, PCIe bridge interrupt setup assumptions, enhanced feature enable ordering, and conditional exclusion of I/O-port boards. Tests should cover each PCI ID mapping, MMIO and I/O resource paths, PCIe BAR0 size check, interrupt-enable write at offset 0x50, common attach propagation, and detach unmapping through Comedi PCI cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc236.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc236.c Research

## Purpose
Provides the ISA front-end driver for the Amplicon PC36AT digital I/O board. The board has one 8255 DIO device and an optional interrupt pseudo-DI subdevice.

## Important APIs, Types, and Functions
`pc236_attach()` allocates `struct pc236_private`, requests a 4-byte I/O region, and calls `amplc_pc236_common_attach()` with base address and optional IRQ. `pc236_boards[]` contains the single board name. The Comedi driver uses manual attach and `comedi_legacy_detach`.

## Control Flow, State, and Persistence
Attach is manual: base address and IRQ come from Comedi config. The front-end does not itself create subdevices; the common helper initializes an 8255 subdevice and optionally an interrupt subdevice if IRQ request succeeds. Persistent state is limited to private data allocated here and then managed by the common helper.

## Dependencies and Integration Points
Includes `amplc_pc236.h` and legacy Comedi APIs. Integrates directly with `amplc_pc236_common.c`.

## Risks and Test Signals
Risks are mostly configuration-related: invalid I/O bases, missing IRQ jumper, or common attach failure after region allocation. Tests should verify region validation, private allocation, optional IRQ behavior, and board-name table setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc236.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc236.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc236.h Research

## Purpose
Defines shared board/private structures and the common attach prototype for Amplicon PC236-family drivers.

## Important APIs, Types, and Functions
`struct pc236_board` contains the board name and optional callbacks for updating interrupt hardware and checking/clearing interrupt status. `struct pc236_private` stores a PLX local configuration I/O base for PCI variants and an `enable_irq` software flag. The header declares `amplc_pc236_common_attach()`.

## Control Flow, State, and Persistence
No executable flow exists in the header. The callback pointers allow ISA and PCI front-ends to share the common interrupt command implementation while providing hardware-specific enable/check behavior. `enable_irq` persists command active state between start/cancel and ISR checks.

## Dependencies and Integration Points
Depends on Linux types and a forward declaration of `struct comedi_device`. Included by front-end and common Amplicon PC236 files.

## Risks and Test Signals
Risks include callback contract ambiguity and private fields used only by some variants. Tests are compile/link coverage plus runtime checks that callbacks are optional for ISA, present for PCI variants, and that `enable_irq` is consistently updated under the common spinlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc236.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc236_common.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc236_common.c Research

## Purpose
Implements common support for Amplicon PC236-family drivers: a primary 8255 DIO subdevice and an optional interrupt-driven pseudo-DI subdevice.

## Important APIs, Types, and Functions
`pc236_intr_update()` toggles software interrupt enable and invokes an optional board callback. `pc236_intr_check()` verifies enabled state and optionally delegates hardware check/clear. `pc236_intr_cmdtest()`, `_cmd()`, and `_cancel()` implement the Comedi async interrupt command. `pc236_interrupt()` writes a zero sample and handles events when the board interrupt is valid. Exported `amplc_pc236_common_attach()` creates subdevices, initializes 8255, and requests IRQ.

## Control Flow, State, and Persistence
Common attach sets `dev->iobase`, allocates two subdevices, initializes subdevice 0 through `subdev_8255_io_init()`, marks subdevice 1 unused, disables interrupts, and turns subdevice 1 into command-capable DI only if IRQ request succeeds. Commands accept `TRIG_NOW`, `TRIG_EXT`, `TRIG_FOLLOW`, `TRIG_COUNT`, and `TRIG_NONE` in a fixed pattern, then simply enable board interrupts until cancel. State persists in `pc236_private.enable_irq` under `dev->spinlock`.

## Dependencies and Integration Points
Uses Comedi 8255 helper, Linux IRQ APIs, Comedi async event buffering, and exported symbol linkage for front-end modules.

## Risks and Test Signals
Risks include generating only zero-valued samples, optional callbacks changing ISR validity, and subdevice 1 being unused when IRQ unavailable. Tests should cover cmdtest trigger validation, start/cancel toggling, IRQ_NONE when disabled, callback invocation under lock, successful sample/event on valid IRQ, and attach behavior with failed IRQ request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc236_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc263.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc263.c Research

## Purpose
Implements a legacy Comedi driver for the Amplicon PC263 16-channel reed-relay output board.

## Important APIs, Types, and Functions
`pc263_do_insn_bits()` updates relay outputs through two byte registers and returns the software state. `pc263_attach()` requests a 2-byte I/O region, allocates one DO subdevice, initializes its metadata, and reads the initial relay state. `pc263_boards[]` and `amplc_pc263_driver` provide manual attach metadata.

## Control Flow, State, and Persistence
Attach validates the configured base address, creates a single `COMEDI_SUBD_DO`, and reads both relay output bytes into `s->state`. Instruction writes use `comedi_dio_update_state()` and only write hardware when requested bits changed. Relay state persists in hardware and Comedi subdevice state; there is no interrupt, command, or reset path.

## Dependencies and Integration Points
Uses legacy Comedi APIs, raw I/O ports, and `comedi_legacy_detach`.

## Risks and Test Signals
Risks are small but include base-region configuration, byte ordering for channels 0-7 versus 8-15, and preserving initial relay state. Tests should cover attach region validation, initial state readback, masked bit updates, output byte ordering, and no unintended writes when the mask is zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc263.c -->
