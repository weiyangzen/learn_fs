# subset-b-004123 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_ci.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_ci.c

Purpose: Implements EN50221 common-interface/CAM support for the NetUP Universal Dual DVB-CI PCIe card. It maps two CAM slots into BAR1 windows, exposes the DVB CA callbacks needed by `dvb_ca_en50221`, and acknowledges CI-related interrupts from the bridge.

Important APIs, types, and functions: `netup_ci_interrupt()` clears CI interrupt status with `CAM_CTRLSTAT_CLR`. `netup_unidvb_ci_register()` initializes one `struct netup_ci_state`, fills `struct dvb_ca_en50221` callbacks, points attribute and I/O windows at slot-specific BAR1 offsets, calls `dvb_ca_en50221_init()`, and enables `NETUP_UNIDVB_IRQ_CI`. `netup_unidvb_ci_unregister()` releases the CA state. Callback functions include `netup_unidvb_ci_read_attribute_mem()`, `netup_unidvb_ci_write_attribute_mem()`, `netup_unidvb_ci_read_cam_ctl()`, `netup_unidvb_ci_write_cam_ctl()`, `netup_unidvb_ci_slot_reset()`, `netup_unidvb_ci_slot_ts_ctl()`, and `netup_unidvb_poll_ci_slot_status()`.

Control flow: Registration is per slot and is called by the core after DVB adapters are registered. Runtime DVB CA operations are direct MMIO byte accesses into the configured slot windows. Slot reset asserts `BIT_CAM_RESET`, waits up to five seconds for `BIT_CAM_READY`, and retries three times before returning success regardless of final readiness. Status polling reads `CAM_CTRLSTAT_READ_SET` and reports present/ready flags to the DVB CA layer. TS enable clears the CAM bypass bit so transport stream data is routed through the CAM.

State and persistence: Software state is held in `dev->ci[num]`: slot number, device pointer, BAR1 config and I/O bases, cached status, and the CA callback object. Hardware CAM state lives in bridge control registers and CAM memory windows and persists only while the card remains powered/configured.

Dependencies and integration points: Depends on `netup_unidvb.h` definitions, the core driver's BAR mappings and frontend adapters, Linux MMIO helpers, and the DVB CA EN50221 framework. Interrupt dispatch is owned by `netup_unidvb_core.c`, which calls `netup_ci_interrupt()` when `NETUP_UNIDVB_IRQ_CI` is reported.

Risks: Reset timeout does not return an error if the CAM never becomes ready, so upper layers can see a successful reset with a nonready slot. Attribute/control memory accesses do not validate `slot` or `addr` beyond the CA framework's expectations. Interrupt clearing uses a fixed `0x101` mask and assumes both slots/bridge bits match that value. There is no locking around CAM window accesses in this file.

Test signals: Useful validation includes probing both CI slots, polling with absent, present, and ready CAM states, reset timeout behavior, TS bypass bit transitions for slot 0 and slot 1 shift handling, unregister/re-register cleanup, and interrupt acknowledgment observed through `REG_ISR`/`CAM_CTRLSTAT` traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_ci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_core.c

Purpose: Main PCI driver for NetUP Universal Dual DVB-CI cards. It probes two supported hardware revisions, maps BARs, allocates coherent DMA memory, registers I2C/SPI/CI/DVB components, attaches demodulators and tuners, and streams transport packets through videobuf2 DVB queues.

Important APIs, types, and functions: `struct netup_dma_regs` describes the bridge DMA register block, and `struct netup_unidvb_buffer` wraps VB2 buffers on the driver's free list. `netup_unidvb_initdev()` and `netup_unidvb_finidev()` are the PCI probe/remove paths. DMA helpers include `netup_unidvb_dma_init()`, `netup_unidvb_dma_enable()`, `netup_dma_interrupt()`, `netup_unidvb_dma_worker()`, `netup_unidvb_ring_copy()`, and `netup_unidvb_dma_timeout()`. DVB setup is handled by `netup_unidvb_dvb_init()`, `netup_unidvb_dvb_setup()`, and `netup_unidvb_dvb_fini()`. VB2 queue callbacks are registered in `dvb_qops`. `netup_unidvb_isr()` multiplexes SPI, I2C, DMA, and CI interrupts.

Control flow: Probe requests helper modules, checks PCI revision and card vendor, creates the device context and workqueue, enables PCI bus mastering and 32-bit DMA, requests and maps BAR0/BAR1, allocates a shared two-channel coherent DMA ring, enables bridge GPIO/PCIe interrupts, optionally registers SPI flash access, then initializes I2C, DVB frontends, CI, DMA engines, and the shared IRQ. If the firmware revision is old, probe enables SPI for firmware access and exits after partial initialization. Streaming starts when VB2 starts the queue, enabling the DMA engine and interrupt mask. Each DMA interrupt records the ring head, computes bytes since the previous head with wrap handling, queues worker processing, and the worker copies full 128-packet buffers to VB2.

State and persistence: Persistent driver state is in `struct netup_unidvb_dev`: PCI identity, BAR mappings, hardware revision, old firmware flag, workqueue, DMA allocation, I2C buses, frontends, CI slots, SPI host, and two `struct netup_dma` streams. Each DMA stream tracks register base, coherent ring offset, physical address high bits, last hardware head, pending byte count/offset, a timer, spinlock, and queued VB2 buffers. Hardware tuner and DMA configuration is register state and is rebuilt on probe.

Dependencies and integration points: Integrates with PCI, DMA API, MMIO, Linux workqueues/timers, VB2 DVB helpers, DVB frontend drivers `cxd2841er`, `horus3a`, `ascot2e`, `helene`, and `lnbh25`, plus local NetUP I2C/SPI/CI helpers. `adapter_nr` comes from DVB module options. GPIO tuner control callbacks are passed to tuner configs and account for revision 1.4 inverted tuner selection.

Risks: `netup_unidvb_dvb_init()` assigns `fes[i]->dvb.name` to a stack buffer, which is suspicious if the DVB helper stores the pointer rather than copying it. DMA worker holds the spinlock while copying from MMIO to VB2 buffers, which can lengthen interrupt-disabled sections. Lost-interrupt handling coalesces data but may discard or duplicate if `data_size` exceeds ring size. Some initialization failures collapse to `-EIO`, and old-firmware probe returns success after incomplete setup. Remove frees IRQ after several components are torn down, so interrupt masking must be reliable.

Test signals: Hardware tests should cover both supported PCI IDs/revisions, old firmware SPI-only mode, module parameter `spi_enable`, frontend attach combinations, DMA wraparound, lost interrupt logging, VB2 start/stop cleanup, CI setup failure rollback, I2C/SPI IRQ dispatch, and remove while streaming. Fault injection should target DMA allocation, BAR mapping, request_irq, and individual frontend attach failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_i2c.c

Purpose: Provides the internal two-bus I2C controller driver for NetUP Universal Dual DVB-CI cards. It adapts the bridge's TWI/FIFO register block to Linux `i2c_adapter` transfers used by the demodulator, tuner, and LNB drivers.

Important APIs, types, and functions: `struct netup_i2c_regs` and `struct netup_i2c_fifo_regs` define the packed MMIO layout for clock, control/status, address/control, length, TX FIFO, and RX FIFO registers. `netup_i2c_interrupt()` decodes completion, address NACK, data NACK, RX FIFO, and TX FIFO interrupt causes and wakes waiters. `netup_i2c_xfer()` is the `i2c_algorithm.master_xfer` implementation. `netup_i2c_reset()`, `netup_i2c_start_xfer()`, `netup_i2c_fifo_tx()`, and `netup_i2c_fifo_rx()` implement the transfer state machine. `netup_i2c_register()` and `netup_i2c_unregister()` create or remove both adapters.

Control flow: Adapter registration initializes spinlock/waitqueue, maps bus 0 or bus 1 register base under BAR0, resets the controller/FIFOs, clones the static adapter template, and calls `i2c_add_adapter()`. A transfer serially processes each `i2c_msg`, starting the hardware command, then repeatedly drops the spinlock and waits up to one second for interrupt-driven state transitions. WANT_READ drains the RX FIFO, WANT_WRITE fills the TX FIFO, DONE optionally drains final read bytes, and ERROR or timeout aborts.

State and persistence: `struct netup_i2c` stores the adapter, register pointer, current message pointer, transfer byte count, waitqueue, spinlock, and state enum. There is no persistent bus transaction history. TWI clock divider and FIFO reset state are hardware registers reset at adapter init/remove or when the state is unexpectedly non-DONE.

Dependencies and integration points: Used by `netup_unidvb_core.c` after BAR mapping and before frontend attachment. The shared PCI ISR dispatches `NETUP_UNIDVB_IRQ_I2C0` and `NETUP_UNIDVB_IRQ_I2C1` to `netup_i2c_interrupt()`. Exposes `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`.

Risks: The transfer path uses a spinlock across state setup and FIFO access, but waits outside the lock; state transitions rely on IRQ ordering and correct re-enabling of TWI IRQ bits. Only one active message is tracked per adapter, so concurrent transfers depend on I2C core serialization. FIFO count fields are trusted. Timeouts leave hardware reset only on the next transfer's initial state check. The adapter class is `I2C_CLASS_HWMON`, which may invite probing unrelated to media use.

Test signals: Validate write-only, read-only, and write-then-read message sequences; FIFO refill/drain for messages larger than 16 bytes; address and data NACK handling; timeout recovery on missing IRQ; reset before new transfers after stale states; unregister while idle; and two independent bus register bases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_spi.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_spi.c

Purpose: Implements an internal SPI controller for NetUP Universal Dual DVB-CI cards, primarily to expose the onboard FPGA flash as an MTD SPI NOR device for firmware maintenance.

Important APIs, types, and functions: `struct netup_spi_regs` describes a 1024-byte data window plus control/status and clock-divider registers. `struct netup_spi` stores the SPI controller, register base, spinlock, waitqueue, and transfer state. `netup_spi_init()` allocates/registers the SPI host, enables SPI interrupts, and creates an `m25p128` child device with a read-only 16 MiB partition. `netup_spi_transfer()` implements `transfer_one_message` by fragmenting transfers into <=1024-byte hardware operations. `netup_spi_interrupt()` acknowledges completion and wakes the transfer waitqueue. `netup_spi_release()` unregisters and masks IRQs.

Control flow: Initialization attaches a devm SPI host to the PCI device, sets mode capabilities, assigns one chip select, maps the controller at BAR0 offset `0x4000`, programs clock divider `2`, enables `NETUP_UNIDVB_IRQ_SPI`, registers the controller, then instantiates the flash device. Each SPI transfer resets chip select, iterates message transfers and fragments, copies TX data or zero fill into MMIO, starts hardware with interrupt mask/start/optional last-CS bits, waits up to six seconds, copies RX data if requested, updates `actual_length`, and finalizes the message.

State and persistence: Software state is minimal: START vs DONE for the active fragment and the host pointer stored in `ndev->spi`. Flash contents are persistent hardware state, but the driver marks the partition read-only via `MTD_CAP_ROM`. Controller configuration is rebuilt at init.

Dependencies and integration points: Probe calls `netup_spi_init()` when the module parameter asks for SPI or when old firmware is detected. Interrupts are dispatched by `netup_unidvb_core.c`. Integrates with SPI controller APIs, SPI flash board-info plumbing, MTD partition metadata, and the local NetUP register/IRQ definitions.

Risks: `netup_spi_transfer()` sets `spi->state` without taking the spinlock used by the interrupt handler, relying on simple ordering around MMIO start and waitqueue wakeups. Timeout returns `-EIO` but does not explicitly reset the controller before later messages. `spi_new_device()` uses legacy board-info with modalias `m25p128`, which may depend on SPI NOR compatibility naming. The flash partition name is a static buffer rewritten per card and shared across instances.

Test signals: Validate fragmented transfers around 1024-byte boundaries, RX-only zero-fill behavior, timeout handling, IRQ-not-mine path, last-CS handling across multi-transfer messages, controller unregister while idle, multiple cards if supported, and MTD child creation with the expected partition name and read-only flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ngene/Kconfig

Purpose: Defines the `DVB_NGENE` kernel configuration option for Micronas nGene PCIe bridge cards.

Important APIs, types, and functions: This is Kconfig metadata rather than C code. `config DVB_NGENE` is a tristate option named "Micronas nGene support". It depends on `DVB_CORE`, `PCI`, and `I2C`, and conditionally selects many DVB frontend, tuner, LNB, and CI helper drivers under `MEDIA_SUBDRV_AUTOSELECT`.

Control flow: Build-time only. When enabled as built-in or module, Kbuild compiles the nGene composite object from the local Makefile. Autoselected dependencies ensure common supported card frontends are available when the media subsystem is configured to autoselect subdrivers.

State and persistence: No runtime state. The selected value persists in the kernel configuration and controls whether `ngene.o` is built.

Dependencies and integration points: Integration is with the media Kconfig tree. The selected symbols match attach paths in `ngene-cards.c`, including STV090x/STV6110x, LGDT330x, DRXK, TDA18271/TDA18212, STV0367, CXD2841ER, STV0910/STV6111, LNB controllers, and CXD2099 CI.

Risks: If `MEDIA_SUBDRV_AUTOSELECT` is disabled, users must manually enable the exact demod/tuner modules required by their PCI subsystem ID. Dependency coverage must stay aligned with new card-info entries; missing `select`s cause runtime attach failures that look like absent hardware.

Test signals: Kconfig tests should verify `DVB_NGENE=m` builds `ngene.ko`, dependencies prevent invalid configurations without PCI/I2C/DVB core, and all attach targets referenced in `ngene-cards.c` are either selected automatically or documented for manual selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ngene/Makefile

Purpose: Describes how Kbuild assembles the nGene PCIe bridge driver.

Important APIs, types, and functions: `ngene-objs` lists `ngene-core.o`, `ngene-i2c.o`, `ngene-cards.o`, and `ngene-dvb.o` as the composite module parts. `obj-$(CONFIG_DVB_NGENE) += ngene.o` wires the composite object to the Kconfig option. Two `ccflags-y` entries add DVB frontend and tuner include paths.

Control flow: Build-time only. Kbuild compiles each source file, links them into `ngene.o`, and emits a module or built-in object based on `CONFIG_DVB_NGENE`.

State and persistence: No runtime state. The Makefile controls object composition and include search paths.

Dependencies and integration points: The include flags support local C includes such as `stv090x.h`, `cxd2841er.h`, `tda18212.h`, and tuner headers included from `ngene-cards.c`. File ordering does not encode runtime sequencing; runtime entry points are exported through `ngene.h` and PCI module registration in `ngene-cards.c`.

Risks: Any new source added to the nGene driver must be added to `ngene-objs`. The explicit include paths mirror media-tree layout and can hide missing fully qualified include updates during refactors.

Test signals: Build `CONFIG_DVB_NGENE=y` and `m`, check the composite object includes all four source objects, and run include-path cleanup builds after moving frontend/tuner headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-cards.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-cards.c

Purpose: Provides nGene card-specific metadata, frontend/tuner probing and attachment, EEPROM helpers, PCI ID matching, and module registration. It is the board database that tells the generic nGene core how each supported PCI subsystem ID should be initialized.

Important APIs, types, and functions: `struct ngene_info` instances such as `ngene_info_cineS2`, `ngene_info_satixS2v2`, `ngene_info_duoFlex`, `ngene_info_m780`, and `ngene_info_terratec` describe stream IO types, firmware version, MSI support, demod/tuner callbacks, configs, LNB addresses, and TS feature selectors. Attachment helpers include `demod_attach_stv0900()`, `demod_attach_stv0910()`, `demod_attach_stv0367()`, `demod_attach_cxd28xx()`, `demod_attach_drxk()`, `demod_attach_lg330x()`, `demod_attach_drxd()`, and tuner attach variants. Probe helpers include `port_has_xo2()`, `init_xo2()`, `port_has_stv0900()`, `port_has_drxk()`, `port_has_stv0367()`, and exported `ngene_port_has_cxd2099()`.

Control flow: The PCI table maps `(vendor, device, subvendor, subdevice)` to an `ngene_info` pointer. `ngene_probe()` in the core consumes that pointer to load firmware, configure buffers, and initialize channels. Per-channel initialization calls the selected `demod_attach[n]` and `tuner_attach[n]`. DuoFlex-style ports are detected dynamically by probing XO2, STV0900, DRXK, or STV0367 hardware, then selecting the right attach path and tuner. Module init registers the PCI driver and PCI error handlers.

State and persistence: Most data is static const board configuration. EEPROM helper functions read and write board calibration tags, notably oscillator deviation for DRXD-based boards. Dynamic state is written into `chan->fe`, `chan->demod_type`, `chan->gate_ctrl`, `chan->i2c_client[0]`, and frontend config callbacks.

Dependencies and integration points: Integrates with many DVB frontend/tuner/LNB modules through `dvb_attach()` and `dvb_module_probe()`. It depends on nGene firmware I2C adapters from `ngene-i2c.c`, channel state from `ngene.h`, and core lifecycle from `ngene-core.c`. PCI error callbacks log and request reset/disconnect outcomes.

Risks: The probing matrix is hardware-specific and order-sensitive; false-positive I2C responses can select the wrong demod path. Several attach failures detach partial frontends locally, but callers must still release module-probed I2C clients during channel cleanup. XO2 support rejects CI modules, so attached DuoFlex CI hardware is intentionally unsupported. EEPROM writes are byte-at-a-time with polling and could block probe-time paths if misused. Some attach helper return values are ignored in dynamic probe branches after logging.

Test signals: Validate every PCI ID selects the intended `ngene_info`; simulate I2C probes for STV0900, DRXK, STV0367, XO2 Sony/STV0910 modules, and CXD2099 CI; verify tuner attach dispatch by `demod_type`; check EEPROM read/write tag bounds and polling; and test failure cleanup for demod attach, tuner attach, and module-probed tuner clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-cards.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-core.c

Purpose: Implements the generic nGene PCIe bridge engine: firmware command transport, interrupt handling, DMA ring allocation, stream control, DVB channel registration, CI attachment, and PCI probe/remove/shutdown behavior.

Important APIs, types, and functions: Public entry points are `ngene_probe()`, `ngene_remove()`, `ngene_shutdown()`, `ngene_command()`, `ngene_command_gpio_set()`, `set_transfer()`, and `FillTSBuffer()`. Core internals include `irq_handler()`, `ngene_command_mutex()`, `ngene_command_load_firmware()`, `ngene_command_stream_control()`, `AllocCommonBuffers()`, `ngene_get_buffers()`, `ngene_start()`, `ngene_stop()`, `init_channel()`, `release_channel()`, `cxd_attach()`, and `cxd_detach()`.

Control flow: Probe enables PCI, allocates `struct ngene`, maps buffers and BAR0, starts the bridge, optionally attaches CXD2099 CI, sends buffer configuration firmware commands, and initializes channels. Startup initializes shared memory, requests IRQ, loads version-specific firmware, optionally switches to MSI, and registers two firmware-backed I2C adapters. Streaming is triggered by DVB feed start/stop or CI setup; `set_transfer()` chooses TS input/output mode, assigns exchange callbacks, and calls `ngene_command_stream_control()` to program firmware buffer descriptors. IRQ handling acknowledges command completions, enqueues UART events, and schedules per-channel bottom halves for ready DMA buffers.

State and persistence: `struct ngene` owns firmware interface DMA memory, command synchronization, event queue, I2C switching state, adapters, channels, CI state, ringbuffers, and optional vmalloc DVB ringbuffers. Each `struct ngene_channel` stores state machine values, DMA descriptors, demux/frontends, callback pointers, TS offset scratch, and running/user counts. Firmware command state is transient; firmware and stream configuration must be rebuilt on probe/resume.

Dependencies and integration points: Consumes card metadata from `ngene-cards.c`, I2C adapters from `ngene-i2c.c`, TS exchange/demux helpers from `ngene-dvb.c`, and the packed firmware ABI from `ngene.h`. Integrates with PCI/MSI, request_firmware, DMA coherent allocation, DVB adapter/frontend/demux/net APIs, workqueues, and CXD2099 CA module probing.

Risks: Command completion relies on shared-memory done bytes and a two-second timeout; failures dump state but many callers collapse to generic errors. DMA allocation paths can leak partially allocated buffer pages inside a ring if a mid-ring allocation fails before later cleanup has full metadata. `init_channel()` returns `0` on some `err:` paths after logging and cleanup, which may hide frontend registration failures. CI paths start TS output and channel 2 input during initialization and depend on cleanup ordering. Shutdown workaround sends a firmware memory write while disabling interrupts, which is inherently chipset-specific.

Test signals: Hardware or emulation tests should cover firmware versions 15-18, MSI and shared IRQ modes, command timeout diagnostics, buffer config variants with/without CI, stream start/stop for TSIN and TSOUT, bottom-half buffer progression, DVB feed user counts, channel init failure cleanup, CXD2099 present/uninitialized/absent cases, suspend/shutdown workaround, and remove while feeds are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-dvb.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-dvb.c

Purpose: Contains nGene DVB-facing stream exchange and demux helper code, plus a CI transport-stream character device used when a CI expansion is present.

Important APIs, types, and functions: `ngene_dvbdev_ci` defines a DVB device with `ci_fops` for read/write/poll of TS ringbuffers. `tsin_exchange()` receives TS input buffers from the core DMA bottom half and feeds demux or CI ringbuffers. `tsout_exchange()` supplies TS output buffers from userspace ringbuffer data or filler packets. `ngene_start_feed()` and `ngene_stop_feed()` control hardware transfer based on demux users. `my_dvb_dmx_ts_card_init()` and `my_dvb_dmxdev_ts_card_init()` initialize DVB demux and dmxdev plumbing.

Control flow: Userspace reads and writes CI TS data through DVB device file operations backed by `dev->tsin_rbuf` and `dev->tsout_rbuf`. DMA bottom halves call `tsin_exchange()` for TS input; if CI is enabled on channel 2, it strips filler packets, optionally repairs 188-byte packet offset shifts, and writes complete packets to `tsin_rbuf`. Otherwise it calls `dvb_dmx_swfilter()`. TS output reads whole-packet-aligned data from `tsout_rbuf`, fills missing capacity with `TS_FILLER`, optionally swaps words, and returns the buffer to firmware.

State and persistence: State includes `ci_tsfix` module parameter, device ringbuffers, per-channel `tsin_offset` and `tsin_buffer`, demux user counts, and channel running state controlled by the core. There is no persistent hardware configuration in this file.

Dependencies and integration points: Called by `ngene-core.c` as buffer exchange callbacks. Uses DVB ringbuffer, DVB demux, DVB dmxdev, DVB net, and generic DVB device open/release helpers. The CI path depends on `dev->ci.en` being set by core CXD2099 attachment.

Risks: `ts_write()` waits for ringbuffer free space >= `count`; very large writes can block indefinitely if `count` exceeds buffer capacity. CI offset repair uses filler-packet matching and a small scratch buffer; malformed streams can cause repeated offset changes or packet drops. `ngene_start_feed()` honors `cmd_timeout_workaround` and `running`, so firmware-version behavior differs. Helper init functions overwrite `ret` and do not check every intermediate demux frontend operation.

Test signals: Exercise CI read/write/poll readiness, large and unaligned write counts, TS output filler insertion, DF_SWAP32 paths, demux start/stop user counts, CI offset repair on shifted packet boundaries, disabled `ci_tsfix`, filler stripping, and demux init failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-dvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-i2c.c

Purpose: Implements Linux I2C adapters for nGene channels by translating I2C transfers into firmware commands sent through the core `ngene_command()` API.

Important APIs, types, and functions: `ngene_command_i2c_read()` builds `CMD_I2C_READ` firmware commands, validates the returned address byte, and copies read data. `ngene_command_i2c_write()` builds `CMD_I2C_WRITE`. `ngene_i2c_set_bus()` switches external I2C bus routing through GPIO commands when card metadata requests it. `ngene_i2c_master_xfer()` is the adapter transfer implementation, and `ngene_i2c_init()` registers one adapter for a channel.

Control flow: `ngene_i2c_master_xfer()` locks `dev->i2c_switch_mutex`, switches bus to the channel number if needed, then supports three patterns: write followed by read, single write, and single read. Successful firmware commands return `num`; unsupported patterns or command failures return `-EIO`. Adapter initialization sets the channel as adapter data, names it "nGene", assigns algorithm callbacks, sets the PCI device parent, and calls `i2c_add_adapter()`.

State and persistence: I2C routing state is `dev->i2c_current_bus`. The function also uses channel number and card `i2c_access` flags. No transfer queue or cache is maintained in this file; firmware and hardware own actual bus state.

Dependencies and integration points: Depends on `ngene_command()` and `ngene_command_gpio_set()` from core, card metadata from `struct ngene_info`, and Linux I2C core. Two adapters are registered by `ngene_start()` and later removed by `ngene_stop()`.

Risks: Only simple I2C transfer shapes are supported; SMBus emulation may generate patterns not accepted here despite `I2C_FUNC_SMBUS_EMUL` being advertised. Read length and write length are packed into firmware buffers sized for short commands, so callers rely on I2C core/device drivers to keep transactions within protocol limits. Bus switching uses GPIO commands and must remain serialized with the mutex.

Test signals: Validate accepted single write, single read, and write-read transfers; reject multi-message non-read patterns; bus switching for cards with `i2c_access & 2`; firmware error mapping; returned-address mismatch; and concurrent transfers on both registered adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene.h

Purpose: Shared private header for the nGene driver. It defines hardware register offsets, firmware command ABI structures, DMA/ringbuffer descriptors, stream/channel/device state structures, card metadata, and cross-file prototypes.

Important APIs, types, and functions: Key structures include `struct ngene_command`, packed firmware payload structs such as `FW_I2C_READ`, `FW_STREAM_CONTROL`, and `FW_CONFIGURE_FREE_BUFFERS`, DMA structures `SBufferHeader` and `SRingBufferDescriptor`, per-channel `struct ngene_channel`, CI state `struct ngene_ci`, device state `struct ngene`, and board descriptor `struct ngene_info`. It defines stream enums, mode/flag bits, firmware opcodes, buffer size constants, shared-memory offsets, DEMOD_TYPE values, and prototypes for functions implemented in core/cards/i2c/dvb files.

Control flow: The header has no executable control flow. Its packed command and descriptor layouts are consumed by firmware command construction, DMA descriptor allocation, and channel setup across the implementation files.

State and persistence: The header defines the software state containers but does not instantiate state. `struct ngene` is the top-level runtime object. `struct ngene_channel` persists per stream until device removal. Packed firmware and DMA descriptor fields mirror hardware/firmware-visible state and must preserve layout.

Dependencies and integration points: Pulls in Linux I2C, interrupt, scatterlist, DVB frontend/demux/net/ringbuffer/CA headers, workqueues, and the CXD2099 CA header. It is included by every nGene source file and forms the internal ABI between them.

Risks: Many structures are packed hardware/firmware contracts; field reordering, alignment changes, or type-size changes can break DMA or command exchange. The header mixes legacy analog/audio fields with current DVB paths, increasing maintenance surface. `struct ngene_info` uses arrays indexed by stream number, so card metadata must stay exactly aligned with `MAX_STREAM`.

Test signals: Build coverage should include all nGene source files after any header edit. Higher-value validation includes `sizeof`/offset checks for packed firmware structs against firmware documentation, channel array index tests for each card_info, and DMA descriptor ring tests that confirm physical pointers match the expected packed fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pluto2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/pluto2/Kconfig

Purpose: Defines the `DVB_PLUTO2` build option for Pluto2 FPGA-based PCI DVB-T cards such as the Satelco Easywatch Mobile Terrestrial receiver.

Important APIs, types, and functions: `config DVB_PLUTO2` is a tristate depending on `DVB_CORE`, `PCI`, and `I2C`. It selects `I2C_ALGOBIT` and `DVB_TDA1004X`.

Control flow: Build-time only. Enabling the option builds `pluto2.o` through the local Makefile and makes the driver available as built-in or module.

State and persistence: No runtime state. Kernel configuration controls whether the driver is compiled.

Dependencies and integration points: The selected dependencies match `pluto2.c`, which uses a bit-banged I2C adapter and the TDA10046 frontend driver.

Risks: The tuner is programmed directly in `pluto2.c` rather than through a separate selected tuner module, so Kconfig dependency coverage is small. Users still need appropriate TDA10046 firmware at runtime if the frontend requests it.

Test signals: Confirm valid module/built-in builds, impossible configs without PCI/I2C/DVB core are rejected, and enabling `DVB_PLUTO2` pulls in `I2C_ALGOBIT` and `DVB_TDA1004X`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pluto2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pluto2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/pluto2/Makefile

Purpose: Kbuild metadata for the Pluto2 DVB-T PCI driver.

Important APIs, types, and functions: `obj-$(CONFIG_DVB_PLUTO2) += pluto2.o` ties the single C file to the Kconfig option. `ccflags-y` adds the DVB frontend include directory.

Control flow: Build-time only. Kbuild compiles `pluto2.c` when `CONFIG_DVB_PLUTO2` is enabled.

State and persistence: No runtime state.

Dependencies and integration points: The include path supports `#include "tda1004x.h"` from `pluto2.c`.

Risks: Any future split of Pluto2 code into multiple sources must update this Makefile. Include path dependency should be revisited if frontend headers move.

Test signals: Compile with `CONFIG_DVB_PLUTO2=y` and `m`, and ensure the output contains only the intended `pluto2` object/module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pluto2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pluto2/pluto2.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/pluto2/pluto2.c

Purpose: Implements the Satelco/SCM Pluto2 PCI DVB-T receiver driver. It handles PCI/MMIO setup, bit-banged I2C, TDA10046 frontend attachment, a directly programmed TUA6034 tuner, PID filtering, one small DMA buffer, interrupts, DVB demux/net registration, and cleanup.

Important APIs, types, and functions: `struct pluto` stores PCI, DVB, I2C, IRQ, and DMA state. Register helpers `pluto_readreg()`, `pluto_writereg()`, and `pluto_rw()` wrap MMIO. I2C bit callbacks are `pluto_setsda()`, `pluto_setscl()`, `pluto_getsda()`, and `pluto_getscl()`. Streaming paths are `pluto_start_feed()`, `pluto_stop_feed()`, `pluto_irq()`, and `pluto_dma_end()`. Hardware lifecycle helpers include `pluto_hw_init()`, `pluto_hw_exit()`, `pluto_reset_frontend()`, and `pluto_reset_ts()`. `frontend_init()` attaches/registers the TDA10046 frontend and tuner callback.

Control flow: Probe allocates state, enables PCI, enables card interrupts in config space, sets 32-bit DMA, requests regions, maps BAR0, requests IRQ, initializes hardware/DMA/interrupts, registers the bit-banged I2C adapter, registers a DVB adapter, reads revision/serial/MAC, initializes demux frontends, attaches frontend, and starts DVB net. IRQ handling checks `REG_TSCR`, rejects non-device interrupts, handles dead/ejected reads of `0xffffffff`, calls `pluto_dma_end()` on DMA completion, counts overflow, resets TS logic on overflow, and acknowledges interrupts. Feed start/stop toggles PID filter registers and full-TS mode.

State and persistence: Driver state includes user counts, full-TS counts, overflow/dead flags, bit-bang bug workaround state, mapped DMA address, and a fixed embedded `dma_buf`. PID filter register state is derived from active feeds. MAC/revision/serial are read from hardware but not persisted by the driver.

Dependencies and integration points: Integrates with PCI, DMA mapping, shared IRQs, I2C bit algorithm, DVB demux/dmxdev/frontend/net APIs, TDA10046 firmware callback, and direct tuner programming through frontend tuner ops.

Risks: `pluto_hw_init()` ignores the return value of `pluto_dma_map()`, so DMA mapping failure may not stop initialization. The DMA buffer is embedded in a `kzalloc` structure and mapped with `dma_map_single`, making cache synchronization correctness essential. Hardware workarounds infer packet counts by scanning for `0x47` and reset TS logic on invalid counters, which can drop data. `pluto_stop_feed()` decrements counters without guarding against imbalance. Serial printing uses `printk(KERN_CONT)`.

Test signals: Validate probe and all rollback labels, DMA mapping failure handling, IRQ none/handled/dead paths, overflow reset path, invalid packet counter recovery, PID filter programming for indexed and full-TS feeds, bit-banged I2C SDA workaround behavior, tuner frequency/bandwidth programming, frontend firmware request, MAC/revision reads, and remove while feeds are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pluto2/pluto2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt1/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/pt1/Kconfig

Purpose: Defines the `DVB_PT1` build option for Earthsoft PT1/PT2 PCI DVB cards.

Important APIs, types, and functions: `config DVB_PT1` is a tristate depending on `DVB_CORE`, `PCI`, and `I2C`. It autoselects `DVB_TC90522`, `DVB_PLL`, and `MEDIA_TUNER_QM1D1B0004` when `MEDIA_SUBDRV_AUTOSELECT` is enabled.

Control flow: Build-time only. Enabling the option builds the `earth-pt1` module/object through the local Makefile.

State and persistence: No runtime state. The option persists in kernel configuration.

Dependencies and integration points: The selected frontend/tuner dependencies match the module-probed demod and tuner devices used by `pt1.c`: TC90522 demods, QM1D1B0004 satellite tuners, and DVB PLL terrestrial tuners.

Risks: With subdriver autoselect disabled, missing demod/tuner modules cause probe-time frontend attachment failures. The help text explains the lack of MPEG decoder and requirement for software decode.

Test signals: Kconfig build tests for module and built-in, dependency rejection without DVB core/PCI/I2C, and autoselect coverage for all `dvb_module_probe()` names used in `pt1.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt1/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt1/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/pt1/Makefile

Purpose: Kbuild metadata for the Earthsoft PT1/PT2 driver.

Important APIs, types, and functions: `earth-pt1-objs := pt1.o` declares a composite object even though it currently has one source. `obj-$(CONFIG_DVB_PT1) += earth-pt1.o` ties it to Kconfig. Include flags add DVB frontend and tuner directories.

Control flow: Build-time only.

State and persistence: No runtime state.

Dependencies and integration points: Include paths support local includes for `tc90522.h`, `qm1d1b0004.h`, and `dvb-pll.h`.

Risks: Future source splits require updating `earth-pt1-objs`. The object name differs from the directory and config symbol, so packaging/tests should check for `earth-pt1`.

Test signals: Build with `CONFIG_DVB_PT1=y/m`, verify include paths and module naming, and run dependency builds with frontend/tuner headers moved or disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt1/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt1/pt1.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/pt1/pt1.c

Purpose: Implements the Earthsoft PT1/PT2 PCI DVB driver for four adapters. It initializes board RAM and custom I2C sequencing, registers four DVB adapters/frontends, manages tuner/demod power, polls DMA table buffers in a kernel thread, reconstructs transport packets from device-specific 32-bit units, and supports suspend/resume.

Important APIs, types, and functions: `struct pt1` is board state; `struct pt1_adapter` is per-frontend state; `struct pt1_table`, `struct pt1_table_page`, and `struct pt1_buffer_page` describe DMA table/buffer pages. Key functions include `pt1_probe()`, `pt1_remove()`, `pt1_init_tables()`, `pt1_thread()`, `pt1_filter()`, `pt1_start_feed()`, `pt1_stop_feed()`, `pt1_init_frontends()`, `pt1_update_power()`, `pt1_set_voltage()`, `pt1_sleep()`, `pt1_wakeup()`, and `pt1_i2c_xfer()`. Hardware bring-up helpers include sync, identify, unlock, PCI/RAM reset, RAM enable, and stream control register writes.

Control flow: Probe enables PCI, maps registers, allocates four DVB adapter/demux contexts, registers a custom I2C adapter, initializes hardware I2C command memory, syncs/unlocks/resets/enables RAM, powers and releases frontend reset, module-probes demods and tuners, initializes demod blocks, and builds circular DMA table chains. Feed start starts the polling thread if needed and enables the adapter stream. The thread scans the current DMA buffer page; when the device marks a page complete, `pt1_filter()` extracts adapter index, start markers, overflow and continuity bits, reconstructs 21 TS packets at a time, feeds the demux, then advances table/buffer indices and notifies hardware.

State and persistence: Board state tracks register mapping, custom I2C running state, DMA table ring, polling thread, current table/buffer indices, power/reset bits, and frontend clock type. Each adapter tracks partial TS packet reconstruction counters, demux user count, frontend module clients, saved frontend ops, SEC voltage, and sleep state. Hardware DMA table state and power register state are rebuilt on probe and resume.

Dependencies and integration points: Uses PCI, DMA coherent allocation, vmalloc, kthreads/freezer, custom I2C algorithm, DVB demux/dmxdev/frontend APIs, module-probed TC90522 demods, QM1D1B0004 satellite tuner, and DVB PLL terrestrial tuner. PM sleep hooks reinitialize hardware and frontends after suspend.

Risks: The custom I2C engine does not support standalone read messages or reads longer than four bytes. `pt1_alloc_page()` uses `BUG_ON()` for DMA address assumptions, which can crash if hardware constraints are violated. Polling every ~10 ms can add latency and CPU overhead. `pt1_update_power()` comments that sleep bits should depend on adapter sleep but currently always sets per-adapter bits. Cleanup assumes all four adapters/frontends were initialized when called through some paths. Resume returns success even after failed reinitialization.

Test signals: Validate PT1 vs PT2 clock-specific demod config, four adapter frontend/tuner attach paths, power/voltage/sleep hooks, start/stop feed balance, kthread freezer resume stream restoration, DMA table allocation and circular PFNs, packet reconstruction including start markers and continuity loss logging, custom I2C accepted/rejected transfer patterns, suspend/resume hardware reinit, and all probe error labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt1/pt1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt3/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/pt3/Kconfig

Purpose: Defines the `DVB_PT3` build option for Earthsoft PT3 PCIe DVB cards.

Important APIs, types, and functions: `config DVB_PT3` is a tristate depending on `DVB_CORE`, `PCI`, and `I2C`. It autoselects `DVB_TC90522`, `MEDIA_TUNER_QM1D1C0042`, and `MEDIA_TUNER_MXL301RF` when media subdriver autoselection is enabled.

Control flow: Build-time only. Enabling the option builds the composite `earth-pt3` driver.

State and persistence: No runtime state.

Dependencies and integration points: Dependency selections match the module-probed TC90522 demods plus satellite and terrestrial tuners used by PT3.

Risks: Manual dependency selection is needed if `MEDIA_SUBDRV_AUTOSELECT` is off. The option depends on I2C because PT3 exposes a custom I2C adapter implemented in `pt3_i2c.c`.

Test signals: Kconfig coverage should build `DVB_PT3` as module and built-in, verify dependency rejection, and confirm all module probe names in `pt3.c` are covered by autoselect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt3/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/pt3/Makefile

Purpose: Kbuild metadata for the Earthsoft PT3 PCIe driver.

Important APIs, types, and functions: `earth-pt3-objs += pt3.o pt3_i2c.o pt3_dma.o` defines the composite object. `obj-$(CONFIG_DVB_PT3) += earth-pt3.o` attaches it to Kconfig. Include flags add DVB frontend and tuner headers.

Control flow: Build-time only. Kbuild compiles the main, I2C, and DMA helper source files into one module/object.

State and persistence: No runtime state.

Dependencies and integration points: Mirrors the source split in `pt3.h`: main frontend/probe code, I2C command translator, and DMA descriptor/ring handling.

Risks: Any source split or helper removal must keep `earth-pt3-objs` synchronized. Include paths assume the media tree's frontend/tuner header layout.

Test signals: Build tests should verify all three objects are linked, both module and built-in modes work, and missing helper objects cause obvious link failures rather than silent feature loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3.c

Purpose: Main Earthsoft PT3 PCIe driver. It probes the board, maps register/internal-memory BARs, registers the custom I2C adapter, creates four DVB frontend/demux adapters, attaches TC90522 demods and Sharp-can tuners, coordinates shared tuner/LNA/LNB power, starts/stops per-frontend DMA polling threads, and implements suspend/resume.

Important APIs, types, and functions: `pt3_probe()` and `pt3_remove()` are PCI lifecycle entry points. `adap_conf` defines four frontend/tuner addresses and initial tuning frequencies. Frontend helpers include `pt3_attach_fe()`, `pt3_fe_init()`, `pt3_demod_write()`, `pt3_set_tuner_power()`, `pt3_set_lna()`, and `pt3_set_voltage()`. Streaming helpers include `pt3_fetch_thread()`, `pt3_start_streaming()`, `pt3_stop_streaming()`, `pt3_start_feed()`, and `pt3_stop_feed()`. Adapter allocation/cleanup is handled by `pt3_alloc_adapter()` and `pt3_cleanup_adapter()`.

Control flow: Probe checks PCI revision, enables the device with managed PCI helpers, sets 64-bit coherent DMA, maps BAR0 registers and BAR2 internal memory, validates FPGA interface version, clamps `num_bufs`, allocates I2C command buffer, registers I2C, allocates each adapter and attaches its frontend/tuner, runs the board-wide frontend/tuner initialization sequence, and reports firmware/interface version. Feed start increments `num_feeds`; the first feed starts a kernel fetch thread and DMA. The thread initializes buffer canaries, drops initial access units, repeatedly calls `pt3_proc_dma()`, and sleeps about 10 ms. Feed stop stops DMA and thread when the last feed is gone.

State and persistence: `struct pt3_board` stores PCI device, two BAR mappings, shared lock, LNB and LNA reference counts, per-FE DMA buffer count, I2C adapter/buffer, and four adapters. Each `struct pt3_adapter` owns DVB frontend/demux state, module-probed I2C clients, streaming thread pointer, feed count, current shared power state, and DMA buffers/descriptors. Hardware power and tuning state is reinitialized on probe/resume.

Dependencies and integration points: Uses PCI managed resource APIs, DMA coherent API, DVB demux/frontend APIs, I2C core with `pt3_i2c_master_xfer()`, and DMA helpers from `pt3_dma.c`. Frontend/tuner modules are loaded through `dvb_module_probe()` for `tc90522`, `qm1d1c0042`, and `mxl301rf`.

Risks: `one_adapter` mode makes frontend-to-adapter lookup scan all four adapters and relies on `dvb_adap.priv` pointing to the board. Shared LNA/LNB reference counts are adjusted under lock but also cache per-adapter booleans, so failed user operations could desynchronize counts. Suspend frees DMA buffers while fetch threads may still exist if feeds are active; it stops DMA but does not stop the thread in this file. `pt3_start_streaming()` starts the thread before starting DMA; if DMA start were to fail later, the thread must be stopped by cleanup paths.

Test signals: Validate revision/interface rejection, BAR mapping, `num_bufs` clamp, one-adapter and four-adapter modes, all four frontend attach addresses, board-wide ROM initialization commands, shared LNA/LNB counts under concurrent frontend controls, feed start/stop balance, DMA start failure handling, suspend/resume with active feeds, and probe rollback after partial adapter creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3.h

Purpose: Internal header for the Earthsoft PT3 driver, defining FPGA registers, I2C command-buffer limits, DMA descriptor formats, per-adapter and board state, adapter configuration structures, and cross-file prototypes.

Important APIs, types, and functions: Register macros cover system, I2C, RAM, and per-frontend DMA register blocks. I2C state is `struct pt3_i2cbuf`. DMA types include `struct xfer_desc`, `struct xfer_desc_buffer`, and `struct dma_data_buffer`, with constants for 188-byte TS packets, 4096-byte transfers, 47 transfers per data buffer, and 2..16 data buffers. Runtime state is `struct pt3_adapter` and `struct pt3_board`. Prototypes expose DMA functions from `pt3_dma.c` and I2C functions from `pt3_i2c.c`.

Control flow: No executable control flow. The macros and structures are used by `pt3.c`, `pt3_dma.c`, and `pt3_i2c.c` to coordinate the driver.

State and persistence: Defines but does not allocate state. `struct pt3_board` persists for the PCI device lifetime; `struct pt3_adapter` persists for each of four frontends. DMA descriptor structures are shared with hardware and therefore have a fixed layout.

Dependencies and integration points: Includes Linux atomic/types and DVB demux/frontend/dmxdev headers, plus TC90522, MXL301RF, and QM1D1C0042 tuner/frontend headers. It is the private contract between the PT3 source files.

Risks: DMA constants must satisfy the comment that `(num_bufs * DATA_BUF_SZ) % TS_PACKET_SZ == 0`; changes can break demux packet alignment. DMA transfers must not cross 4 GiB, so `DATA_XFER_SZ` and descriptor construction are hardware constraints. `PT3_I2C_MAX` and command nibble packing must stay aligned with internal memory layout.

Test signals: Compile all PT3 files after header edits, validate descriptor struct size against `DESCS_IN_PAGE`, assert data-buffer divisibility by TS packet size, and run DMA ring construction tests for min/max `num_bufs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3_dma.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3_dma.c

Purpose: Implements PT3 DMA buffer allocation, circular descriptor construction, DMA engine start/stop, and polling-time processing of newly written transport-stream access units.

Important APIs, types, and functions: `pt3_alloc_dmabuf()` allocates coherent data buffers and descriptor pages, then builds a circular xfer descriptor list. `pt3_free_dmabuf()` releases them. `pt3_init_dmabuf()` writes canary bytes at access-unit boundaries and resets indices. `pt3_start_dma()` and `pt3_stop_dma()` program per-FE DMA registers. `pt3_proc_dma()` detects completed access units and feeds packets to DVB demux. `get_dma_base()` maps adapter index to hardware DMA register order.

Control flow: Allocation creates `pt3->num_bufs` coherent data buffers, marks them unwritten, calculates descriptor page count, fills descriptors with 4096-byte transfers, chains descriptor pages, and loops the last descriptor back to the first. Start writes descriptor low/high addresses and sets DMA control. Stop writes stop control and polls status up to five times. Processing checks whether the current canary is still present; if not, it advances access-unit by access-unit until it reaches an unwritten canary, feeding complete 128-packet units to demux and resetting canaries as it consumes.

State and persistence: Per-adapter DMA state includes data buffers, descriptor pages, buffer index, offset, allocated counts, and initial discard count set by the fetch thread. Hardware descriptor and DMA control registers are programmed on each start.

Dependencies and integration points: Called from `pt3.c` adapter allocation, feed start/stop, fetch thread, suspend, and resume. Uses PCI DMA coherent API, MMIO register helpers, and DVB software demux filtering.

Risks: Canary-based completion assumes real TS data will not preserve the canary byte at exact access-unit starts; this is a pragmatic hardware protocol but can miss writes if the canary value remains. `pt3_stop_dma()` returns `-EIO` after fixed 250 ms max wait. Allocation failure cleanup depends on counts being updated immediately after each allocation. `get_dma_base()` swaps indices 1 and 2 to match hardware order, which is easy to regress.

Test signals: Validate descriptor ring for min/max buffer counts, page boundary chaining, last descriptor loopback, index remapping for all four adapters, canary initialization and consumption, wraparound packet feeding, initial discard behavior, DMA stop timeout, and allocation failure cleanup after partial data/descriptor allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3_i2c.c

Purpose: Implements the PT3 custom I2C adapter by translating Linux I2C messages into compact FPGA command nibbles written into the board's internal memory, then triggering the FPGA sequencer.

Important APIs, types, and functions: `enum ctl_cmd` defines encoded line-control commands. `cmdbuf_add()`, `put_start()`, `put_byte_write()`, `put_byte_read()`, `put_stop()`, and `translate()` build the command stream in `struct pt3_i2cbuf`. `send_i2c_cmd()` runs a translated command at an internal memory address and waits for status. Exported functions are `pt3_i2c_master_xfer()`, `pt3_i2c_functionality()`, `pt3_i2c_reset()`, `pt3_init_all_demods()`, and `pt3_init_all_mxl301rf()`.

Control flow: Normal transfers reject `I2C_M_RECV_LEN`, translate all messages into command nibbles, copy the command bytes to BAR2 internal memory at `PT3_I2C_BASE`, run the normal command address, then copy read data back from internal memory. Board initialization paths run pretranslated ROM sequences for all demods and for the two MXL301RF tuners. `wait_i2c_result()` polls `REG_I2C_R` until `STAT_SEQ_RUNNING` clears and fails on timeout or sequencer error.

State and persistence: `pt3->i2c_buf` holds transient translated command data. Hardware sequencer state is reset by `pt3_i2c_reset()` and represented by status bits in `REG_I2C_R`. Hidden ROM command sequences persist in the FPGA/board, not in driver memory.

Dependencies and integration points: Registered as the board's I2C algorithm in `pt3.c`. Used by module-probed demod/tuner drivers and by board-wide initialization in `pt3_fe_init()`. Requires both BAR0 registers and BAR2 internal memory to be mapped.

Risks: `memcpy_toio()` length uses `cbuf->num_cmds`, which counts nibbles, not bytes; because commands are packed two per byte and bounded by array writes, this may copy extra stale command bytes beyond the packed stream unless the hardware ignores them after `I_END`. The code bounds data writes in `cmdbuf_add()` but does not fail if too many commands are generated, so oversized I2C messages can silently truncate commands. Only plain I2C functionality is advertised, and SMBus block receive is explicitly unsupported.

Test signals: Validate command translation for write, read, repeated starts, ACK/NACK command positions, odd command counts and end padding, maximum message lengths near `PT3_I2C_MAX`, sequencer timeout/error handling, ROM init command addresses, readback offset ordering, and rejection of `I2C_M_RECV_LEN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/Kconfig

Purpose: Defines build options for Philips SAA713x PCI video capture support and related ALSA audio, remote-control, DVB/ATSC, and go7007 encoder integrations.

Important APIs, types, and functions: `VIDEO_SAA7134` is the main tristate depending on `VIDEO_DEV`, `PCI`, and `I2C`, selecting VB2 DMA scatter-gather, tuner, tveeprom, CRC32, and optional subdevices. `VIDEO_SAA7134_ALSA` enables DMA audio support with ALSA PCM. `VIDEO_SAA7134_RC` enables remote controller support as a bool with dependency constraints for built-in/module combinations. `VIDEO_SAA7134_DVB` enables DVB/ATSC support and autoselects many frontend/tuner/LNB drivers. `VIDEO_SAA7134_GO7007` enables go7007 MPEG encoder support.

Control flow: Build-time only. These symbols control which objects are compiled by the local Makefile and which media subdrivers are available for runtime board variants.

State and persistence: No runtime state. Configuration choices persist in the kernel `.config`.

Dependencies and integration points: Integrates with V4L2, PCI, I2C, remote-control core, ALSA, DVB core, VB2, go7007, frontend/tuner modules, and media autoselect policy. The RC option includes a guard against `RC_CORE=m` with built-in SAA7134.

Risks: The main SAA7134 family supports many boards, so missing autoselect entries can surface as runtime feature loss on specific board variants. Feature symbols are split, so enabling base video does not imply ALSA, DVB, RC, or go7007 support. The RC bool default `y` can surprise minimal builds unless dependencies are adjusted.

Test signals: Kconfig matrix tests should cover base-only, base+ALSA, base+RC, base+DVB, base+go7007, built-in/module dependency combinations, and autoselect coverage for every frontend/tuner referenced by SAA7134 board tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/Makefile

Purpose: Kbuild metadata for the Philips SAA7134 driver family.

Important APIs, types, and functions: `saa7134-y` composes the base driver from card, core, I2C, TS, TV audio, VBI, and video objects. `saa7134-$(CONFIG_VIDEO_SAA7134_RC)` conditionally adds remote input support. Object lines build `saa7134.o` and `saa7134-empress.o` for the base option, plus optional `saa7134-go7007.o`, `saa7134-alsa.o`, and `saa7134-dvb.o`. Include flags add tuner, DVB frontend, and go7007 USB encoder headers.

Control flow: Build-time only. Kbuild links the base composite object and optional feature modules according to the Kconfig symbols.

State and persistence: No runtime state.

Dependencies and integration points: Mirrors the SAA7134 feature split from Kconfig. The base module includes the core analog/video/transport-stream support, while ALSA, DVB, and go7007 integrations are separate modules/objects.

Risks: `obj-$(CONFIG_VIDEO_SAA7134) += saa7134.o saa7134-empress.o` builds empress support whenever the base option is enabled, so dependencies must remain satisfied by the base Kconfig. Conditional RC object composition must match the bool dependency constraints. New board support that needs additional headers or feature objects must update both Kconfig and Makefile.

Test signals: Build all option combinations, verify expected modules are emitted, confirm `saa7134-input.o` appears only when RC is enabled, and run link checks for optional DVB/ALSA/go7007 objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/Makefile -->
