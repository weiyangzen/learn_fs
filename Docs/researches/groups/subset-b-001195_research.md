# subset-b-001195 Comedi driver research

Grouped research for Linux Comedi low-level drivers and helper modules under the Ceph client source tree. Each source file section preserves the source path in the title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcidas64.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcidas64.c

Purpose: Implements the Comedi PCI auto-configured driver for Measurement Computing/ComputerBoards PCI-DAS64xx, PCI-DAS60xx, and PCI-DAS4020 analog I/O boards using a PLX9080 PCI bridge. It exposes AI, AO, DIO/8255, calibration DACs, AD8402 pots on 64xx boards, and EEPROM memory subdevices. It supports simple single-sample instructions and command-mode AI, plus command-mode AO on non-4020 boards with AO hardware.

Important APIs/types/functions: The core data model is `struct pcidas64_board`, `struct hw_fifo_info`, `struct pcidas64_private`, and `struct ext_clock_info`. Board metadata in `pcidas64_boards[]` binds PCI IDs to AI/AO channel counts, speed limits, range tables/codes, FIFO geometry, layout (`LAYOUT_60XX`, `LAYOUT_64XX`, `LAYOUT_4020`), and optional 8255 presence. Key entry points are `auto_attach()`, `detach()`, `setup_subdevices()`, `ai_rinsn()`, `ai_cmdtest()`, `ai_cmd()`, `ai_cancel()`, `ao_winsn()`, `ao_cmdtest()`, `ao_cmd()`, `ao_inttrig()`, `ao_cancel()`, `handle_interrupt()`, `handle_ai_interrupt()`, and `handle_ao_interrupt()`. Hardware helpers include PLX DMA setup (`init_plx9080()`, `alloc_and_init_dma_members()`, `load_first_dma_descriptor()`, `dma_start_sync()`), AI pacing/queue helpers (`set_ai_pacing()`, `setup_channel_queue()`, `check_adc_timing()`), FIFO/DMA drains, I2C bit-banging for 4020 calibration/range devices, serial EEPROM reads, and calibration DAC writes.

Control flow: PCI probe calls `comedi_pci_auto_config()`, then `auto_attach()` enables PCI, maps PLX BAR0, main BAR2, and DIO/counter BAR3, computes PLX local-space addresses for chained DMA descriptors, allocates coherent AI/AO DMA rings, initializes PLX DMA/interrupt registers and board STC registers, requests the shared IRQ, and creates ten Comedi subdevices. AI instruction reads disable AI pacing, configure calibration/range/queue state for either 6xxx or 4020 layout, trigger conversions, wait via `comedi_timeout()`, and read from pipe/FIFO registers. AI command setup disables prior pacing, aborts DMA1, loads internal or external channel queues, programs convert/scan counters, enables interrupts, starts DMA unless EOS wakeup forces PIO, configures trigger/gate bits, and optionally writes the software start register. The interrupt handler reads PLX and board status, drains DMA1 rings or PIO FIFO for AI, drains/fills DMA0 for AO, maps EOA/error conditions into Comedi async events, and clears PLX doorbell/DMA interrupts. AO instruction writes program DAC range and write per-channel registers; AO command setup programs channel selection, interval counters, DMA0 descriptor chain, DAC control bits, and starts through an internal trigger callback that primes FIFO/DMA before enabling the DAC engine.

State and persistence: Runtime state is mostly cached hardware register images in `pcidas64_private`: interrupt enable bits, ADC control bits, FIFO-size bits, hardware config bits, DAC control bits, PLX control/interrupt bits, current calibration source, 4020 I2C range bits, external trigger polarity, AI command-running flag, AI FIFO segment length, external master-clock divisor/chanspec, and AO bounce/DMA ring indices. Coherent DMA buffers/descriptors persist for device lifetime and are freed in detach. Comedi readback arrays persist the last AO/calibration/pot values. Hardware FIFO, DMA, trigger, range, calibration, and EEPROM/I2C state persists until reset or later driver writes; no durable host-side state is written.

Dependencies and integration points: Depends on `linux/comedi/comedi_pci.h`, `linux/comedi/comedi_8255.h`, Linux PCI/DMA/IRQ APIs, and `plx9080.h`. It integrates with Comedi auto-configuration, async command buffers, subdevice readback, calibration utilities, `subdev_8255_mm_init()`/`subdev_8255_cb_init()`, PCI vendor CB device IDs, PLX9080 local bus/DMA/interrupt registers, and board-specific analog front-end calibration hardware. The external AI queue and AO FIFO share hardware resources, so AI external-queue commands and AO commands are explicitly blocked from running together.

Risks: This driver has high hardware-state coupling. DMA ring handling depends on PLX register semantics and coherent descriptor fields; missed chain-end or index checks can cause underrun, stale samples, or data loss. 4020 I2C access fakes ACK and has no bus mutex despite comments, so concurrent EEPROM/I2C users would be risky. AI timing validation must match 24-bit counter off-by-two/off-by-three semantics. External queue use has documented interaction with DAC FIFO. IRQ handling reads `HW_STATUS_REG`, which also clears interrupts, so ordering matters. Detach disables PLX interrupts and unmaps before freeing DMA, which is intentional but sensitive to in-flight IRQs. Some TODO paths, such as hardware sample counter and user counter support, are disabled or unused.

Test signals: Probe should map all BARs, allocate DMA, request IRQ, and expose correct subdevices for each PCI ID/layout. AI instruction tests should cover normal input, calibration source reads, 4020 range switching, dither, and timeout handling. AI command tests should cover internal versus external queues, 4020 1/2/4-channel constraints, external start/stop, `TRIG_OTHER` master clock configuration, DMA streaming, PIO/EOS wakeup, FIFO overrun, and cancel. AO tests should cover immediate writes, range codes, DMA command streaming, underrun recovery, external update/start triggers, and cancellation. Calibration tests should verify caldac/AD8402 readback caching and EEPROM reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcidas64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcidda.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcidda.c

Purpose: Provides PCI auto-configured Comedi support for Measurement Computing PCI-DDA02/04/08 boards in 12-bit and 16-bit variants. The implemented feature set is simple analog output plus two 8255 DIO subdevices; command-mode streaming is not supported.

Important APIs/types/functions: Board selection uses `enum cb_pcidda_boardid`, `struct cb_pcidda_board`, and `cb_pcidda_boards[]`. Per-device state lives in `struct cb_pcidda_private`, holding the DAC I/O base, cached calibration register bits, current AO range per channel, and a software copy of 128 EEPROM words. Key functions are `cb_pcidda_auto_attach()`, `cb_pcidda_ao_insn_write()`, `cb_pcidda_read_eeprom()`, `cb_pcidda_serial_out()`, `cb_pcidda_serial_in()`, `cb_pcidda_write_caldac()`, and `cb_pcidda_calibrate()`.

Control flow: PCI probe passes the table `driver_data` board index to `comedi_pci_auto_config()`. Attach enables the PCI device, stores BAR2 as `dev->iobase` for 8255 access and BAR3 as the DAC/calibration I/O base, allocates three subdevices, configures the AO subdevice from board metadata, initializes two 8255 subdevices at offsets 0 and `I8255_SIZE`, reads all EEPROM calibration words through bit-banged serial I/O, and calibrates each AO channel. AO writes recalibrate only if the requested range differs from cached `ao_range[channel]`, program the DAC control register with channel/range/unipolar bits, then write each sample to the channel data register.

State and persistence: The driver caches EEPROM contents, last selected range per AO channel, and the last output value only through hardware state; there is no Comedi readback allocation for AO. Calibration DAC settings are written from EEPROM on attach and whenever range changes. Persistent hardware data is the EEPROM calibration table; host-side state exists only for the attached device lifetime.

Dependencies and integration points: Depends on Comedi PCI helpers and `comedi_8255` for DIO. It integrates with CB PCI IDs `0x0020` through `0x0025`, the Comedi range model, and MCC/CB calibration EEPROM/caldac serial protocol. Detach is delegated to `comedi_pci_detach()`.

Risks: Serial EEPROM/caldac programming is timing-sensitive and uses port I/O delays but no locking. `ao_range[]` starts zeroed, so attach calibration writes range 0 for all channels. Range-to-EEPROM index math assumes the board's calibration layout exactly matches six ranges per channel. AO readback is not supported, so users cannot query last output through Comedi readback. Test failures are likely to show as incorrect output scaling or calibration drift rather than probe failures.

Test signals: Validate all six PCI IDs choose the correct channel count/resolution, AO writes update every channel over all six ranges, range changes trigger calibration writes, both 8255 subdevices configure/read/write banks, and EEPROM reads produce stable calibration words.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcidda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcimdas.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcimdas.c

Purpose: Implements the Comedi driver for ComputerBoards/Measurement Computing PCIM-DAS1602/16 and PCIe-DAS1602/16 boards. It supports simple software-triggered AI, two AO channels, an 8255 DIO block, four main-connector DI lines, four main-connector DO lines, and an exposed 8254 counter subdevice.

Important APIs/types/functions: Per-device BAR state is `struct cb_pcimdas_private` with `daqio` and `BADR3`. Key functions are `cb_pcimdas_auto_attach()`, `cb_pcimdas_ai_insn_read()`, `cb_pcimdas_ai_eoc()`, `cb_pcimdas_ao_insn_write()`, `cb_pcimdas_di_insn_bits()`, `cb_pcimdas_do_insn_bits()`, `cb_pcimdas_counter_insn_config()`, `cb_pcimdas_pacer_clk()`, `cb_pcimdas_is_ai_se()`, and `cb_pcimdas_is_ai_uni()`. The driver uses `comedi_8254_io_alloc()` and `comedi_8254_subdevice_init()` for counters.

Control flow: Attach enables PCI, maps BAR2/BAR3/BAR4 I/O bases, allocates an 8254 pacer using a jumper-detected 1 MHz or 10 MHz base, and creates six subdevices. AI instruction reads force polled pacer mode, enable conversions, program gain and mux for one channel, issue a soft trigger for each requested sample, wait for EOC via `comedi_timeout()`, and read the 16-bit AI register. AO writes store the last sample in Comedi readback and write directly to the AO register. Counter configuration allows user counter clock source selection between internal 100 kHz and external pin 21; counters 1 and 2 are marked busy because they are reserved internally for the pacer.

State and persistence: State is limited to BAR addresses, 8254 object state, DO `s->state`, AO readback, and hardware registers. Board jumpers select AI single-ended versus differential mode, AI unipolar versus bipolar range table, AO output ranges, and pacer clock frequency; those settings are read or assumed at attach but not persisted by the driver.

Dependencies and integration points: Depends on Comedi PCI, generic 8255 and 8254 helpers, and PLX9052 register definitions. It integrates with PCI vendor CB IDs `0x0056` and `0x0115`, Comedi immediate instruction APIs, and the 8254 counter API. No IRQ or command streaming path is wired despite hardware registers existing for FIFO/interrupt/pacer modes.

Risks: The driver intentionally supports only simple AI and does not use FIFO/interrupt acquisition, so high-rate or multi-channel command expectations will fail. Jumper-derived range/polarity/mux state is trusted at attach. AO range is not software-readable and represented as possible jumper choices. Counter busy marking protects internal pacer counters; regressions there could let users disturb AI timing. Test signals include AI reads in both jumper modes, AO readback/write, 8255 DIO, main DI/DO nibble behavior, counter clock source get/set, and probe on both PCI and PCIe variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcimdas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcimdda.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcimdda.c

Purpose: Provides Comedi support for the Measurement Computing PCIM-DDA06-16 analog output board. It exposes six 16-bit AO channels and one 8255 DIO subdevice. Command-mode AO is not supported.

Important APIs/types/functions: The file defines the PCI ID `PCI_ID_PCIM_DDA06_16`, channel register macro `PCIMDDA_DA_CHAN()`, and 8255 base `PCIMDDA_8255_BASE_REG`. Functional entry points are `cb_pcimdda_auto_attach()`, `cb_pcimdda_ao_insn_write()`, and `cb_pcimdda_ao_insn_read()`.

Control flow: PCI probe auto-configures the Comedi driver. Attach enables PCI, uses BAR3 as `dev->iobase`, allocates two subdevices, initializes the AO subdevice with readable/writable flags and bipolar 5 V range, allocates AO readback, and initializes an 8255 DIO subdevice at offset `0x0c`. AO writes emit LSB then MSB to the channel's two byte registers; if the board jumper is in immediate update mode, MSB latches output. AO reads perform an input from the channel register to trigger simultaneous transfer when the board jumper is in simultaneous XFER mode, then return Comedi readback data.

State and persistence: Driver state is `dev->iobase` plus Comedi AO readback and DIO state. Hardware jumper state controls both output range and update mode and is invisible to software. The driver assumes factory default bipolar 5 V for the range table.

Dependencies and integration points: Depends on Comedi PCI helpers and `subdev_8255_io_init()`. It integrates with PCI vendor CB device ID `0x0053`, legacy I/O-mapped DAC registers, and Comedi readback helpers. Detach uses `comedi_pci_detach()`.

Risks: The output range and simultaneous-transfer mode cannot be detected, so the reported Comedi range may be wrong if jumpers differ. The read path has side effects by design because reads can latch simultaneous AO updates. Only byte-wide register ordering is correct for the board; changing to word writes could break hardware. Test signals include AO channel write/readback, simultaneous transfer latch behavior, 8255 DIO configuration, and probe/remove with BAR3 resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcimdda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_8254.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_8254.c

Purpose: Implements reusable Comedi support for Intel 8254-compatible programmable interval timers. Other Comedi drivers allocate this helper to program counters for pacing or expose them as counter subdevices.

Important APIs/types/functions: Exported APIs include `comedi_8254_io_alloc()`, `comedi_8254_mm_alloc()`, `comedi_8254_subdevice_init()`, `comedi_8254_set_mode()`, `comedi_8254_write()`, `comedi_8254_read()`, `comedi_8254_status()`, `comedi_8254_load()`, `comedi_8254_ns_to_timer()`, `comedi_8254_cascade_ns_to_timer()`, `comedi_8254_update_divisors()`, `comedi_8254_pacer_enable()`, and `comedi_8254_set_busy()`. Internal I/O callbacks cover 8/16/32-bit PIO and MMIO spacing with `regshift`. Subdevice instruction handlers are `comedi_8254_insn_read()`, `comedi_8254_insn_write()`, and `comedi_8254_insn_config()`.

Control flow: Allocation validates register width, chooses an I/O callback, allocates `struct comedi_8254`, records context/oscillator/register spacing, defaults oscillator base to 10 MHz timing if omitted, and resets all counters to mode 0 binary. Read latches a counter and reads LSB then MSB. Write loads LSB then MSB. Mode/load functions validate counter and mode/value limits before writing the control word. Pacer support programs two cascaded counters in mode 2 when enabled and mode 0 when disabled, writing counter2 before counter1 to avoid early expiry. Timer conversion helpers round requested nanoseconds according to Comedi command flags and store pending divisors; `update_divisors()` commits those values for programming.

State and persistence: `struct comedi_8254` stores callback, context, I/O width, register shift, oscillator base, current/next divisors, and per-counter busy flags. The helper does not persist state beyond kernel object lifetime; counter hardware state persists until reprogrammed or reset. Busy flags prevent generic user instructions from changing counters reserved by a parent driver for pacing.

Dependencies and integration points: Depends on Linux I/O accessors, Comedi core subdevice APIs, and `linux/comedi/comedi_8254.h`. It is an exported GPL helper consumed by low-level drivers such as `cb_pcimdas`. External drivers remain responsible for gate routing, clock routing, IRQs, and any extra instruction configuration through `i8254->insn_config`.

Risks: Counter semantics around initial count zero, two-byte load order, mode validation, and cascaded divisor rounding are correctness-sensitive. `comedi_8254_cascade_ns_to_timer()` searches divisor pairs and must avoid overflow and invalid divisors. Busy flag enforcement is local to generic instruction handlers; parent drivers must set it correctly. Test signals include mode/status/read/write instructions, nanosecond rounding modes, cascaded pacer rates, busy-counter rejection, PIO/MMIO widths, and parent-driver pacing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_8254.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_8255.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_8255.c

Purpose: Implements reusable Comedi support for 8255 programmable peripheral interface digital I/O chips. It lets parent drivers expose a 24-channel DIO subdevice backed by I/O ports, MMIO registers, or a custom callback.

Important APIs/types/functions: The private state is `struct subdev_8255_private`, storing callback context and I/O callback. Exported initializers are `subdev_8255_io_init()`, `subdev_8255_mm_init()`, `subdev_8255_cb_init()`, and `subdev_8255_regbase()`. Core handlers are `subdev_8255_insn()`, `subdev_8255_insn_config()`, and `subdev_8255_do_config()`. Built-in callbacks are `subdev_8255_io()` and `subdev_8255_mmio()`.

Control flow: Initialization allocates subdevice private storage, records the callback/context, configures the subdevice as readable/writable 24-bit DIO, installs instruction handlers, and writes the initial 8255 control word. Bit instructions update Comedi DIO state from `data[0]/data[1]`, write only the affected 8-bit ports, then read ports A/B/C and return a 24-bit value. Config instructions map the requested channel to one of four direction groups: A, B, C-low, or C-high; they call the generic Comedi DIO config helper with that mask and rewrite the 8255 mode-0 control word.

State and persistence: State lives in Comedi `s->state` and `s->io_bits`, plus callback context in `s->private`. Hardware port directions and output latches persist until rewritten or reset. Only 8255 mode 0 is supported; no durable state is stored.

Dependencies and integration points: Depends on `linux/comedi/comedidev.h` and `linux/comedi/comedi_8255.h`. It is used by multiple board drivers in this work item, including `cb_pcidda`, `cb_pcimdas`, `cb_pcimdda`, `cb_pcidas64`, and `daqboard2000`.

Risks: Direction masks must match 8255 grouping rules; individual-bit direction changes are widened to hardware banks. Callback users must implement port numbering and write/read return semantics correctly. I/O-port support is conditional on `CONFIG_HAS_IOPORT`, while MMIO/callback paths remain available. Test signals include all four direction groups, partial-bit writes preserving other ports, port readback after output writes, callback-backed 8255 devices, and parent-driver attach paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_8255.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_bond.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_bond.c

Purpose: Implements a virtual Comedi driver that bonds DIO subdevices from one or more existing Comedi devices into a single linear DIO subdevice. It is meant to simplify userspace access when digital lines are spread across multiple boards/subdevices.

Important APIs/types/functions: `struct bonded_device` records a referenced Comedi device, minor, subdevice index, and channel count. `struct comedi_bond_private` stores display name, dynamic bonded-device pointer array, device count, and total channel count. Core functions are `bonding_attach()`, `bonding_detach()`, `do_dev_config()`, `bonding_dio_insn_bits()`, and `bonding_dio_insn_config()`.

Control flow: Manual attach parses `comedi_devconfig` options as a list of Comedi minors. `do_dev_config()` rejects invalid, duplicate, or self minors, opens each source device with `comedi_open_from()`, finds all DIO subdevices, obtains channel counts, appends `bonded_device` records with `krealloc()`, and builds a board name string like `minor:subdev`. Attach creates one DIO subdevice whose channel count is the sum of all bonded DIO channels. Bit instructions translate a base channel and up to 32 bits into per-source masks/data and call `comedi_dio_bitfield2()` on the underlying subdevices. Config instructions locate the underlying subdevice/channel and delegate to `comedi_dio_config()` or `comedi_dio_get_config()`.

State and persistence: Runtime state is the open references to underlying Comedi devices, the dynamic bonded-device array, aggregate channel count, and generated name. Underlying device output/configuration state is changed directly through Comedi library calls and persists in those devices. Detach closes each source minor once and frees bond records.

Dependencies and integration points: Depends on Comedi core and in-kernel comedilib APIs (`comedi_open_from()`, `comedi_close_from()`, `comedi_find_subdevice_by_type()`, `comedi_dio_bitfield2()`, `comedi_dio_config()`). It is manually configured and does not bind to hardware itself.

Risks: It only supports DIO and no command paths. Error handling during `do_dev_config()` can return after opening devices or allocating records; detach later cleans normal attached state, but partially failed attach paths depend on core cleanup. Bitfield operations are limited to a 32-channel window starting at the requested base channel. Underlying devices can disappear or change behavior independently. Test signals include bonding multiple minors, duplicate/self-minor rejection, cross-subdevice bitfield reads/writes spanning boundaries, DIO config/query translation, and detach closing each source minor exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_bond.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_isadma.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_isadma.c

Purpose: Provides reusable ISA DMA allocation, programming, polling, and cleanup helpers for Comedi drivers that still use legacy ISA DMA channels.

Important APIs/types/functions: Exported APIs are `comedi_isadma_alloc()`, `comedi_isadma_free()`, `comedi_isadma_program()`, `comedi_isadma_disable()`, `comedi_isadma_disable_on_sample()`, `comedi_isadma_poll()`, and `comedi_isadma_set_mode()`. The code operates on `struct comedi_isadma` and `struct comedi_isadma_desc` from `comedi_isadma.h`.

Control flow: Allocation validates one or two descriptors, allocates a flexible `struct comedi_isadma`, selects a DMA-capable device (`dev->hw_dev` or a class device coerced to a 24-bit DMA mask), requests one or two ISA DMA channels, allocates coherent buffers for each descriptor, and initializes the DMA mode. `comedi_isadma_program()` claims the ISA DMA lock, clears the flip-flop, sets mode/address/count, and enables the channel. Disable stops the channel and returns residue. Disable-on-sample repeatedly re-enables short transfers until residue aligns with sample size or appears stalled. Poll reads residue, with special handling for `isa_dma_bridge_buggy`, and converts it to a byte position. Free releases coherent buffers and DMA channels.

State and persistence: State is the allocated DMA object, descriptor array, requested channels, coherent buffer virtual/bus addresses, max sizes, current DMA index, and direction mode. Hardware DMA controller state persists while a transfer is programmed; host objects are freed explicitly.

Dependencies and integration points: Depends on Linux ISA DMA APIs (`request_dma()`, `claim_dma_lock()`, `set_dma_*()`, `get_dma_residue()`), DMA mapping APIs, and Comedi device metadata. Parent drivers supply channel numbers, direction, and max buffer size, then use descriptors for device-specific transfers.

Risks: ISA DMA requires 24-bit addressable buffers and global DMA lock discipline. Residue reads can race hardware rollover; poll mitigates by reading twice. `comedi_isadma_disable_on_sample()` can spin briefly if hardware stalls mid-sample. Channel 0 is treated as no secondary channel in allocation/free logic, so callers must pass valid legacy DMA channels consistently. Test signals include allocation/failure cleanup, single and double-buffer channels, read/write mode setup, residue/poll behavior, sample-aligned disable, and parent hardware DMA transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_isadma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_parport.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_parport.c

Purpose: Implements a legacy manually configured Comedi driver for standard PC parallel ports. It exposes data pins as bidirectional DIO, status pins as DI, control pins as DO, and optionally an interrupt-backed DI command subdevice using ACK/pin 10.

Important APIs/types/functions: Register offsets are `PARPORT_DATA_REG`, `PARPORT_STATUS_REG`, and `PARPORT_CTRL_REG`; control bits include IRQ enable and bidirectional enable. Important functions are `parport_attach()`, `parport_data_reg_insn_bits()`, `parport_data_reg_insn_config()`, `parport_status_reg_insn_bits()`, `parport_ctrl_reg_insn_bits()`, `parport_intr_cmdtest()`, `parport_intr_cmd()`, `parport_intr_cancel()`, and `parport_interrupt()`.

Control flow: Attach requests an I/O region from user-supplied option 0 and optionally requests an IRQ from option 1. It allocates three subdevices without IRQ, or four with IRQ. Subdevice 0 maps the 8-bit data register as DIO; its config handler toggles the parallel-port bidirectional control bit depending on `s->io_bits`. Subdevice 1 reads five status bits shifted down from the status register. Subdevice 2 writes four control output bits while preserving IRQ/bidir control bits. Optional subdevice 3 supports a narrow command interface with `TRIG_NOW` start and `TRIG_EXT` scan begin; command start enables IRQ, cancel disables it, and the interrupt handler writes a dummy zero sample then calls `comedi_handle_events()`.

State and persistence: State is the requested I/O base, optional IRQ, DIO `s->state`/`s->io_bits`, and hardware data/control registers. Attach initializes data and control registers to zero. No durable state exists beyond hardware latch values and Comedi runtime state.

Dependencies and integration points: Depends on Comedi legacy attach/detach, I/O-port access, and Linux IRQ APIs. Users must supply I/O base and optional IRQ through Comedi configuration. It integrates with Comedi async buffers only for the optional interrupt subdevice.

Risks: Parallel-port electrical behavior and inverted status/control lines are hardware-specific; the driver exposes raw register bits with limited normalization. Optional IRQ request failure is non-fatal and silently results in no command subdevice. Command samples are dummy wakeups, not captured status values. Test signals include I/O region rejection, data DIO input/output mode switching, status/control bit reads/writes, IRQ command start/cancel, and interrupt-generated Comedi events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_parport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_test.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_test.c

Purpose: Implements a virtual Comedi test driver that generates deterministic fake analog input waveforms, loopback analog output state, and simulated open-collector DIO. It can auto-configure a synthetic device at module load or be manually configured.

Important APIs/types/functions: Module parameters are `noauto`, `amplitude`, and `period`. `struct waveform_private` holds AI/AO timers, waveform amplitude/period/current phase, AI/AO timing, parent device pointer, AO loopback values, and timer-enable flags. Important functions are `waveform_common_attach()`, `waveform_attach()`, `waveform_auto_attach()`, `waveform_detach()`, `fake_sawtooth()`, `fake_squarewave()`, `fake_flatline()`, `waveform_ai_timer()`, `waveform_ai_cmdtest()`, `waveform_ai_cmd()`, `waveform_ai_cancel()`, `waveform_ao_timer()`, `waveform_ao_cmdtest()`, `waveform_ao_cmd()`, `waveform_ao_inttrig_start()`, `waveform_ao_cancel()`, and DIO instruction/config handlers.

Control flow: Module init registers the Comedi driver and, unless `noauto` is set, registers a small device class, creates a dummy device, and calls `comedi_auto_config()`. Attach sets default or user-provided amplitude/period, allocates three subdevices, initializes AI command-read, AO command-write/readback loopback, and 32-channel DIO, and sets up two kernel timers. AI command validation accepts `TRIG_NOW` start, timer/follow scan timing, now/timer conversion, count scan end, and count/none stop; execution computes microsecond periods and first conversion time, then schedules the AI timer. The AI timer emits samples from the requested chanlist according to waveform phase and Comedi async progress, reschedules itself until stop or overrun, and raises events. AO command validation accepts internal trigger start, timer scan pacing, now conversions, and count/none stop; execution waits for `inttrig`, then the AO timer drains userspace samples, keeps only the latest scan when behind, updates loopback values, and raises EOA/overflow. DIO models paired open-collector wires between lower and upper 16 channels.

State and persistence: State is fully synthetic and per-device: waveform configuration, timers, current waveform phase, next AI conversion time, last AO scan time, loopback sample array, DIO state/io_bits, and module-level auto-created class/device pointer. No hardware or durable persistence exists. Timers are deleted on cancel and detach.

Dependencies and integration points: Depends on Comedi core async buffer APIs, Linux timers, ktime/jiffies, module parameters, and device/class creation for auto-config mode. It is useful for Comedi userspace and core testing where real acquisition hardware is unavailable.

Risks: Timer granularity is jiffy/microsecond based and not real-time precise; `CMDF_PRIORITY` is rejected. AO timer skips intermediate scans when behind, which is intentional but may surprise tests expecting every historical output. Module init returns success after some auto-config setup failures, leaving only driver registration in place. DIO behavior is a model, not hardware-compatible for arbitrary boards. Test signals include auto and manual attach, waveform amplitude/range saturation, AI command timing and stop count, AO inttrig and underrun/overflow paths, loopback reads, DIO paired-wire behavior, cancel from timer and process context, and module exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/contec_pci_dio.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/contec_pci_dio.c

Purpose: Provides a compact PCI auto-configured Comedi driver for the Contec PIO1616L digital I/O board, exposing 16 digital inputs and 16 digital outputs.

Important APIs/types/functions: The register map is `PIO1616L_DI_REG` at offset 0 and `PIO1616L_DO_REG` at offset 2. Functional entry points are `contec_auto_attach()`, `contec_di_insn_bits()`, and `contec_do_insn_bits()`, plus the PCI probe/remove wrapper.

Control flow: PCI probe calls `comedi_pci_auto_config()`. Attach enables the PCI device, uses BAR0 as `dev->iobase`, allocates two subdevices, configures subdevice 0 as 16-channel DI with word reads, and subdevice 1 as 16-channel DO with word writes. DO instruction bits use `comedi_dio_update_state()` to update only masked bits, write `s->state` to the DO register, and return the cached state.

State and persistence: State is only `dev->iobase` and the Comedi DO `s->state`. Hardware output latches persist until changed or reset; no readback register is used for DO. There is no command-mode or interrupt state.

Dependencies and integration points: Depends on Comedi PCI helpers and PCI vendor ID `PCI_VENDOR_ID_CONTEC` with device `0x8172`. Detach uses `comedi_pci_detach()`.

Risks: Minimal driver, but it assumes BAR0 I/O layout and returns cached DO state rather than hardware readback. There is no IRQ, debounce, or edge event support. Test signals include probe, DI word reads, masked DO updates preserving previous bits, remove cleanup, and behavior after reset where cached state may differ from hardware until first write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/contec_pci_dio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dac02.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/dac02.c

Purpose: Implements a legacy manually configured Comedi driver for Keithley Metrabyte DAC-02 compatible boards, exposing two 12-bit analog output channels.

Important APIs/types/functions: The range table `das02_ao_ranges` models jumper-selectable voltage/current/external-reference ranges. Register macros `DAC02_AO_LSB()` and `DAC02_AO_MSB()` address each channel's two DAC registers. Main functions are `dac02_attach()` and `dac02_ao_insn_write()`.

Control flow: Attach requests the user-supplied I/O port region in the valid legacy range, allocates one AO subdevice, sets two channels, 12-bit maxdata, range table, write handler, and Comedi readback. AO writes save the unmodified sample in readback, convert bipolar ranges to complementary offset binary by subtracting from maxdata, then write LSB nibble-aligned data followed by MSB to latch the double-buffered DAC.

State and persistence: Runtime state is the I/O base and Comedi AO readback. Physical range selection is controlled by external jumpers and cannot be read by software. DAC output latches persist until overwritten or reset.

Dependencies and integration points: Depends on Comedi legacy attach/detach and I/O-port access. It is manually configured with an I/O port base and has no PCI/PNP discovery, IRQs, calibration, or command path.

Risks: The reported range is user-selected by chanspec but actual electrical range depends on jumpers, so software can request a range that does not match hardware wiring. Bipolar encoding is inverted relative to unipolar and must remain correct. Test signals include valid/invalid I/O base attach, writes to both channels, bipolar/unipolar encoding checks, readback, and latch ordering on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dac02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/daqboard2000.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/daqboard2000.c

Purpose: Implements the Comedi PCI auto-configured driver for IOTech DAQBoard/2000 and DAQBoard/2001 boards. It uploads required FPGA firmware, initializes acquisition/DAC reference state, and exposes simple AI, AO, and 8255-style DIO. Command-mode acquisition is not implemented.

Important APIs/types/functions: Board metadata uses `enum db2k_boardid`, `struct db2k_boardtype`, and `db2k_boardtypes[]`; private state `struct db2k_private` stores the PLX MMIO base. Key functions are `db2k_auto_attach()`, `db2k_detach()`, `db2k_load_firmware()`, `db2k_reset_local_bus()`, `db2k_reload_plx()`, `db2k_pulse_prog_pin()`, CPLD wait/write helpers, `db2k_initialize_adc()`, `db2k_ai_insn_read()`, `db2k_setup_sampling()`, `db2k_ao_insn_write()`, `db2k_ao_eoc()`, and `db2k_8255_cb()`.

Control flow: PCI probe selects board type by subsystem ID and calls Comedi auto-config. Attach enables PCI, maps PLX BAR0 and board BAR2, allocates three subdevices, loads `daqboard2000_firmware.bin` through `comedi_load_firmware()`, initializes ADC/reference DAC state, and configures AI, AO, and callback-backed 8255 DIO. Firmware loading searches for the FPGA start sequence, strips the firmware header, verifies even length and PLX EEPROM presence, then retries up to three times: reset local bus, reload PLX EEPROM, pulse PROG, wait for CPLD init, stream 16-bit words with old/new CPLD timing, wait for FPGA DONE, and reset/reload again. AI instruction reads reset scan/result/config FIFOs, set a long pacer period, write four scan-list control words for the selected channel/range, start scan-list sequencing, wait for config pipe, enable pacer, wait for scanning and FIFO data, read one sample, then disable pacer and stop scan-list loading. AO writes store each sample to the channel DAC setting register and wait until that channel's busy bit clears before updating readback.

State and persistence: State includes mapped PLX and board MMIO, FPGA/CPLD programmed hardware state, reference DAC settings, AO readback, and 8255 DIO state. Several initialization helpers for DMA/counters/timers/DAC disarm are stubs or minimal, reflecting incomplete reverse-engineered functionality. Firmware is external and required at probe time; no persistent host state is written.

Dependencies and integration points: Depends on Comedi PCI, Comedi firmware loading, `comedi_8255` callback initialization, Linux delay/interrupt headers, and `plx9080.h`. Integrates with PCI vendor/subsystem IDs for DAQBoard/2000 and /2001 and requires `MODULE_FIRMWARE("daqboard2000_firmware.bin")` to be available from firmware search paths.

Risks: Firmware upload is mandatory and reverse-engineered; bad firmware headers, odd lengths, CPLD timing, or PLX EEPROM absence block attach. AI setup hardcodes calibration offset/gain words instead of reading EEPROM and performs conservative single-sample polling. Several advanced hardware capabilities and DMA paths are unimplemented. Detach unmaps PLX then delegates board MMIO and PCI cleanup to `comedi_pci_detach()`. Test signals include firmware load on old/new CPLD revisions, FPGA DONE detection, AI instruction reads over all ranges/channels, AO busy timeout/readback, 8255 callback DIO, missing-firmware failure, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/daqboard2000.c -->
