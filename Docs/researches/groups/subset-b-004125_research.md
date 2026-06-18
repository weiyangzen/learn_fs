# subset-b-004125 Research

Grouped research report for the requested SAA7134 media driver subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-core.c

Purpose: implements the PCI/core layer for Philips/NXP SAA7130/7133/7134/7135 analog TV capture cards. It owns PCI probe/remove, MMIO mapping, IRQ dispatch, device list and MPEG-submodule registration, DMA page-table helpers, common vb2 buffer queue transitions, power management, media-controller entity creation, and V4L2 video/VBI/radio device registration.

Important APIs, types, and functions: module parameters select device numbers, board/tuner overrides, PCI latency, ALSA loading, and page-aligned USERPTR support. Exported globals `saa7134_devlist`, `saa7134_devlist_lock`, `saa7134_dmasound_init`, and `saa7134_dmasound_exit` coordinate auxiliary modules. GPIO helpers `saa7134_track_gpio()` and `saa7134_set_gpio()` are shared by board setup, DVB, audio, and GO7007 paths. DMA helpers `saa7134_pgtable_alloc()`, `saa7134_pgtable_build()`, `saa7134_pgtable_free()`, `saa7134_buffer_count()`, `saa7134_buffer_startpage()`, and `saa7134_buffer_base()` translate vb2 scatter-gather buffers into the SAA7134 page-table format. Queue helpers `saa7134_buffer_queue()`, `saa7134_buffer_finish()`, `saa7134_buffer_next()`, `saa7134_buffer_timeout()`, and `saa7134_stop_streaming()` are used by video, VBI, TS, and MPEG capture queues. `saa7134_set_dmabits()` is the central hardware gate for DMA task enable bits and IRQ masks. `saa7134_ts_register()` and `saa7134_ts_unregister()` export the MPEG ops registry used by `saa7134-dvb`, `saa7134-empress`, and `saa7134-go7007`.

Control flow: `saa7134_initdev()` allocates `struct saa7134_dev`, registers `v4l2_device`, enables PCI, sets a 32-bit DMA mask, chooses the board from PCI ID or module override, maps BAR0, runs early board and hardware init, requests the shared IRQ, registers the SAA7134 I2C adapter, runs late board/hardware init, instantiates encoder/RDS subdevices, attaches any already-loaded MPEG ops, registers video/VBI/radio nodes, optionally builds media-controller entities, initializes DMA sound, schedules async submodule loads, and finally registers the media device. The remove path `saa7134_finidev()` flushes async module work, tears down DMA sound, disables IRQ/DMA/peripherals, detaches MPEG ops, unregisters I2C and video nodes, frees the IRQ and MMIO mapping, unregisters media/V4L2 state, and frees the device. `saa7134_irq()` loops over pending IRQ reports, acknowledges them, dispatches video, VBI, TS/MPEG, signal-change, and GPIO-IR work, preserves ALSA DMA interrupts for the sound module, and disables noisy sources if the loop limit is hit.

State and persistence: runtime state lives in `struct saa7134_dev`: board identity, tuner/audio config, MMIO pointers, locks, DMA queues, media/V4L2 devices, I2C adapter/client, subdevices, input/remote state, MPEG ops, suspend flags, and per-queue page tables. `saa7134_devcount` assigns transient device numbers; `mops_list` persists loaded MPEG-op providers for future hotplug. There is no filesystem persistence. Hardware state is programmed in MMIO registers and must be reconstructed after probe/resume.

Dependencies and integration points: depends on PCI, V4L2, vb2 DMA-SG, media controller, I2C, IRQ, DMA mapping, PM, and board metadata from `saa7134.h`/board tables. It calls into video, VBI, TS, TV audio, input, board, and optional ALSA/MPEG modules, while those modules call back into core DMA/GPIO/MPEG registration helpers.

Risks: error unwind must match probe ordering, because partially registered V4L2/media/I2C/IRQ resources are common on unsupported boards. `saa7134_set_dmabits()` is concurrency-sensitive and assumes `dev->slock`; wrong DMA/IRQ bits can cross-talk between video, VBI, ALSA, and TS. IRQ storms are mitigated but can mask legitimate events. Suspend/resume reuses active buffers and temporarily drops DMA audio, so stream recovery depends on queue state being consistent. Async module loading means media topology can change after the base device appears.

Test signals: PCI bind/unbind on known and unknown board IDs, module-parameter board/tuner overrides, video/VBI/radio node creation, I2C EEPROM and subdevice discovery, IRQ delivery under capture, VBI and TS streaming, MPEG submodule late load/unload, ALSA coexistence, media graph registration, suspend/resume with active buffers, and fault-injection of probe failures at MMIO, IRQ, I2C, and video registration stages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-dvb.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-dvb.c

Purpose: supplies the DVB/ATSC/SBTVD MPEG transport-stream submodule for SAA7134 cards. It creates a DVB frontend backed by the shared TS DMA queue, attaches the demodulator/tuner/LNB stack for each supported board, and registers the resulting DVB bus through `vb2_dvb`.

Important APIs, types, and functions: module parameters include `antenna_pwr`, `use_frontend`, and DVB adapter numbering. The file is structured around many board-specific `*_config` objects for mt352, tda1004x/tda10046, tda827x, tda10086, nxt200x, mt312, zl10353, qt1010, lgdt3305, tda10048, tda18271, lgs8gxx, s5h1411, mb86a20s, and satellite LNB helpers. Helper functions program GPIO antenna power, tuner PLLs, I2C gates, demod firmware callbacks, tuner init/sleep methods, LNB voltage wrappers, and frontend attachment. `dvb_init()` and `dvb_fini()` are exposed through a `struct saa7134_mpeg_ops` with type `SAA7134_MPEG_DVB`.

Control flow: `dvb_register()` registers `dvb_ops` with core, causing `dvb_init()` to run for matching devices. `dvb_init()` initializes `dev->frontends`, allocates frontend 1, initializes `fe0->dvb.dvbq` with `saa7134_ts_qops`, and switches on `dev->board`. Each case attaches the correct demodulator first, then attaches tuner, PLL, I2C gate, and LNB-control helpers as needed. Some hybrid cards set GPIOs before attach or override frontend ops such as `sleep`, `set_voltage`, `enable_high_lnb_voltage`, and `i2c_gate_ctrl`. After successful attach, it installs `saa7134_tuner_callback`, registers the DVB bus, then calls frontend init/sleep and tuner sleep so firmware loads and hybrid boards return to analog mode. `dvb_fini()` restores a few board-specific states, unregisters the DVB bus, and releases the vb2 queue.

State and persistence: state is runtime-only and stored in `dev->frontends`, `fe0->dvb.frontend`, the TS vb2 queue, `dev->original_demod_sleep`, `dev->original_set_voltage`, `dev->original_set_high_voltage`, `dev->eedata`, and GPIO/MMIO/I2C device state. Firmware requested by demods is loaded via the kernel firmware interface but not persisted by this file.

Dependencies and integration points: integrates with the core MPEG ops list, `saa7134-ts.c` for DMA, the SAA7134 I2C adapter, V4L2 tuner callbacks, many DVB frontend/tuner modules, firmware loading, and optional media-controller DVB registration. Board definitions in `saa7134.h` determine which switch case is reachable.

Risks: the large board switch is fragile: a wrong I2C address, gate polarity, GPIO mode, TS serial/parallel expectation, or tuner IF config prevents lock or can leave hybrid hardware in the wrong analog/digital mode. Several ops wrappers preserve original frontend callbacks and must not recurse. Failure paths deallocate frontends and release queues; missing release on partial attach would leak resources. `use_frontend` selects terrestrial versus satellite on multi-frontend boards but the file still allocates only one frontend.

Test signals: module load on each supported board family, frontend registration under `/dev/dvb`, successful firmware request for tda1004x/tda10048-style devices, I2C attach logs, channel scan and lock for DVB-T/DVB-S/ATSC/SBTVD, analog mode after DVB close on hybrid cards, LNB voltage switching for satellite boards, antenna power behavior for Pinnacle 300i, and TS streaming through the vb2 queue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-dvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-empress.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-empress.c

Purpose: implements the Empress MPEG encoder support module for SAA7134 boards that expose a hardware MPEG stream through the common TS DMA path. It registers an additional V4L2 MPEG capture node and bridges MPEG format ioctls to the encoder subdevice and existing analog controls.

Important APIs, types, and functions: `empress_nr[]` selects MPEG device numbers. `saa7134_empress_qops` wraps TS queue helpers, adding encoder-specific start/stop behavior. Format handlers advertise and configure only `V4L2_PIX_FMT_MPEG`. `ts_fops` and `ts_ioctl_ops` expose read, mmap, poll, vb2 buffer ioctls, tuner/input/std controls, and event subscription. `empress_init()` and `empress_fini()` are installed in `empress_ops` for core MPEG registration.

Control flow: loading the module calls `saa7134_ts_register(&empress_ops)`. For matching devices, `empress_init()` allocates a video device, combines selected analog controls with encoder-subdevice controls, initializes `dev->empress_vbq` with DMA-SG memory, registers the MPEG V4L2 node, and schedules a signal-status update. Streaming calls `saa7134_ts_start_streaming()`, sends a board-specific leading-null-byte setting to subdevices via `core.init`, unmutes I2S audio, and marks `dev->empress_started`. Stop calls `saa7134_ts_stop_streaming()`, toggles `SAA7134_SPECIAL_MODE` to reset the path, mutes audio, and clears the started flag.

State and persistence: maintains `dev->empress_dev`, `dev->empress_ctrl_handler`, `dev->empress_vbq`, `dev->empress_workqueue`, and `dev->empress_started`. It uses the shared `dev->ts_q` DMA queue and encoder subdevice state. No persistent storage is used.

Dependencies and integration points: depends on the core MPEG ops registry, common TS DMA helpers, vb2 DMA-SG, V4L2 controls/events/ioctls, analog tuner/input/std helpers from the base driver, the optional `saa6752hs` encoder subdevice created by core, and audio mute/I2S registers.

Risks: Empress shares TS resources with DVB/TS code, so queue and stop sequencing must leave channel 5 clean. USERPTR is deliberately excluded because SAA7134 DMA requires page-start-aligned buffers. Signal updates are currently diagnostic only. Resetting `SPECIAL_MODE` on stop may affect other active paths if board state assumptions are wrong.

Test signals: MPEG device node registration, `VIDIOC_ENUM_FMT` reporting MPEG only, buffer allocation/streamon/read/mmap, encoder subdevice control propagation, audio unmute/mute around streaming, signal-change work execution, module unload while idle and while previously streamed, and media topology updates after late module load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-empress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-go7007.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-go7007.c

Purpose: integrates Micronas GO7007 MPEG encoder chips connected to SAA7134-based PCI boards. It implements the GO7007 host-port interface over SAA7134 GPIOs, programs the SAA7134 TS/DMA path for compressed video pages, boots/registers the GO7007 encoder, and exposes it through GO7007's V4L2 infrastructure.

Important APIs, types, and functions: `struct saa7134_go7007` stores the bridge subdev, parent SAA7134 device, two page buffers, and their DMA addresses. `board_voyager` describes the encoder board capabilities. Low-level HPI helpers `gpio_write()` and `gpio_read()` drive address, read, write, idle, reset, and video commands. `saa7134_go7007_hpi_ops` implements GO7007 callbacks for interface reset, interrupt read/write, stream start/stop, and firmware download. `saa7134_go7007_irq_ts_done()` replaces generic TS completion for GO7007 streams. `saa7134_go7007_init()` and `saa7134_go7007_fini()` are registered through `saa7134_mpeg_ops`.

Control flow: module init registers GO7007 MPEG ops with core. Device init allocates a GO7007 object and bridge context, fills board/bus/name/HPI callbacks, initializes a V4L2 subdev, allocates two zeroed pages for ping-pong compressed data reception, boots firmware via `go7007_boot_encoder()`, registers the encoder, registers the bridge subdev with the GO7007 V4L2 device, and stores `dev->empress_dev = &go->vdev`. Streaming maps the two pages for DMA, configures video port and TS interface registers, points DMA channel 5 at top/bottom pages, enables the TS FIFO and DMA IRQs, and lets IRQ completion sync and parse the filled page before rearming its DMA base. Stop disables TS FIFO/IRQs/interface and unmaps both pages. Firmware download writes up to 64-byte chunks through HPI and polls status.

State and persistence: runtime state includes the GO7007 encoder object, bridge context, two page buffers, DMA mappings, GO7007 interrupt values, encoder status, optional audio state, and SAA7134 GPIO/TS registers. Firmware `go7007/go7007tv.bin` is required at boot time but not persisted by the driver.

Dependencies and integration points: depends on GO7007 core/private APIs, V4L2 subdev/device APIs, DMA mapping, SAA7134 register/GPIO helpers, core MPEG ops attach/detach, and TS IRQ dispatch in `saa7134-core.c`. It intentionally uses `dev->empress_dev` as the video-device handle for GO7007, so it shares that slot with Empress-style MPEG support.

Risks: HPI over GPIO is timing/order sensitive; hung status polling returns generic failures. Stream start must unwind the first DMA mapping if the second fails. IRQ parsing assumes `dev->empress_dev` points to a valid GO7007 V4L2 device and that streaming state is active. The fini path manually frees pages and unregisters nested V4L2 objects, so ordering mistakes can produce use-after-free on late IRQs or audio cleanup.

Test signals: firmware boot success, GO7007 V4L2 node registration, HPI interrupt read/write sanity, stream start/stop with DMA mapping, IRQ-driven page parsing without lost-buffer floods, module unload after streaming, audio removal when enabled, and behavior when firmware is missing or the encoder reset signature is not `0x55aa`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-go7007.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-i2c.c

Purpose: implements the SAA7134 on-chip I2C master as a Linux `i2c_adapter`, reads board EEPROM data, optionally scans the bus, and instantiates I2C IR clients.

Important APIs, types, and functions: module parameters `i2c_debug` and `i2c_scan` control tracing and bus probing. Internal `enum i2c_status` and `enum i2c_attr` mirror hardware status/command fields in `SAA7134_I2C_ATTR_STATUS`. Helpers read/write status and attributes, classify idle/busy/error states, reset error state, and send/receive individual bytes. `saa7134_i2c_xfer()` is the adapter `master_xfer`; `functionality()` advertises SMBus emulation. `saa7134_i2c_register()` and `saa7134_i2c_unregister()` are called by core probe/remove.

Control flow: transfer starts by checking for idle bus or resetting error status. For each `i2c_msg`, it sends a START/address unless `I2C_M_NOSTART` permits continuation. Reads receive each byte with CONTINUE; writes send each data byte with CONTINUE. A special repeated-start quirk sends `0xfe` before many read messages, avoiding an SAA7134 I2C issue seen with mt352-like devices, and address `0x19` receives one extra discard byte for Samsung S5H1411. At the end it issues STOP, waits for idle, and delays one millisecond. Registration copies adapter/client templates, binds `dev` as `algo_data`, adds the adapter, reads EEPROM address `0xa0`, optionally scans every address, and calls `saa7134_probe_i2c_ir()`.

State and persistence: `dev->i2c_adap`, `dev->i2c_client`, and `dev->eedata` hold runtime adapter/client and EEPROM bytes. EEPROM contents are read from hardware and retained in memory for board-specific logic, but this file does not write persistent storage.

Dependencies and integration points: used by core board detection/init, tuner/demod/encoder/RDS subdevice creation, DVB frontend attach, IR probing, and board-specific EEPROM quirks. It relies on SAA7134 MMIO accessors and Linux I2C core callbacks.

Risks: byte-level I2C sequencing is hardware-specific and has explicit quirks; changing repeated-start behavior can break demods/tuners. The adapter advertises SMBus emulation although transfers are implemented as raw I2C messages. Error returns are coarse and may not preserve the exact failing message index. The Medion MD7134 gate workaround is needed before EEPROM reads because the demod EEPROM address can clash with the card EEPROM.

Test signals: EEPROM dump during probe, successful tuner/demod/subdevice I2C attach, optional `i2c_scan` discovery output, transfer failure logs under missing devices, MD7134 reboot/probe stability, S5H1411 reads, mt352 repeated-start reads, and clean adapter deletion on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-input.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-input.c

Purpose: provides infrared remote-control support for SAA7134 cards through the Linux rc/input subsystem. It supports GPIO scancode remotes, GPIO raw-edge decoders, and I2C IR receiver clients with board-specific key readers.

Important APIs, types, and functions: module parameters `disable_ir`, `ir_debug`, and `pinnacle_remote` control probing and remote variant selection. `build_key()` extracts GPIO scancodes using board masks and reports keydown/keyup events. I2C key readers handle FlyDVB Trio, MSI TV@nywhere Plus, Kworld PC150U, PurpleTV, Behold M6xx NECX, and Pinnacle grey/color packet formats. `saa7134_input_irq()`, `saa7134_input_timer()`, `saa7134_ir_open()`, and `saa7134_ir_close()` manage IRQ/polling/raw operation. `saa7134_input_init1()`, `saa7134_input_fini()`, and `saa7134_probe_i2c_ir()` are called from core and I2C setup.

Control flow: early core init calls `saa7134_input_init1()` for GPIO remotes. It switches on `dev->board`, selects an rc keymap, GPIO masks, polling interval, and raw-decode mode, then allocates `struct saa7134_card_ir` plus `struct rc_dev`, fills PCI identity and rc properties, and registers the rc device. Opening the rc device applies board-specific GPIO output setup, marks the remote running, and starts a timer for polling remotes. IRQs from core call `saa7134_input_irq()`, which either builds a scancode or stores a raw IR edge. I2C adapter registration calls `saa7134_probe_i2c_ir()`, which creates `ir_video` clients with optional platform data and custom `get_key` callbacks for supported boards.

State and persistence: runtime state lives in `dev->remote`, `struct saa7134_card_ir` masks, polling timer, last GPIO value, raw decode flag, `rc_dev`, and `dev->init_data` for I2C clients. Keymap names reference kernel rc maps. There is no persistent state.

Dependencies and integration points: integrates with core IRQ GPIO16/GPIO18 dispatch, SAA7134 GPIO registers and rescan bit, I2C adapter/client creation, `ir-kbd-i2c`, rc-core keymaps/protocol decoders, and board definitions. Raw mode relies on rc-core IR decoders via `RC_DRIVER_IR_RAW`.

Risks: the board switch is large and mask values are easy to regress. Some remotes require GPIO setup in open rather than init so resume works. Polling timers must be deleted before freeing the rc device. I2C get-key callbacks sometimes modify client address or depend on GPIO lines before I2C reads. Raw edge polarity uses `mask_keydown`; wrong masks break protocol decoding.

Test signals: rc device registration for each supported board, keydown/keyup events from GPIO remotes, timer polling cadence, GPIO IRQ handling on GPIO16/GPIO18, raw IR decoding through rc-core, I2C client instantiation and key reads, suspend/resume with rc device open, `disable_ir=1`, and Pinnacle grey/color remote selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-reg.h

Purpose: defines SAA7130/7133/7134/7135 PCI IDs, MMIO register offsets, and bit masks used by the SAA7134 driver family. It is the hardware register contract shared by core, video, VBI, TS, audio, I2C, input, DVB, Empress, GO7007, and ALSA-related code.

Important APIs, types, and definitions: PCI IDs are defined if missing from PCI headers. Register macros include DMA channel base/pitch/control (`SAA7134_RS_*`), FIFO/threshold, SAA7133/7135 audio registers, `SAA7134_MAIN_CTRL` task/PLL/processing enable bits, AV status, IRQ enable/report/status bits, video decoder/scaler registers, task-specific VBI/video/scaler paths, clipping/output format registers, I2C control/data registers, analog audio/NICAM/I2S/DSP registers, video port controls, TS interface registers, GPIO mode/status/rescan registers, special/test modes, and SAA7135 DSP status/clear bits.

Control flow: this header has no runtime flow; other files include it to compute byte or dword MMIO offsets for `saa_readb`, `saa_writeb`, `saa_readl`, `saa_writel`, and bit-update helpers. Some 32-bit register offsets are pre-shifted with `>> 2`, while many 8-bit registers are byte offsets.

State and persistence: no storage is declared. The definitions describe hardware state maintained in MMIO registers and manipulated by implementation files.

Dependencies and integration points: included by SAA7134 implementation files and depends on consistent MMIO accessor conventions in `saa7134.h`. The split between byte offsets and dword offsets is central to correct register access.

Risks: wrong offset units or bit masks can corrupt unrelated hardware blocks, especially DMA channel programming, IRQ masking, GPIO control, and audio DSP access. Duplicate-style definitions for SAA7135 DSP clear bits also appear in TV audio code and must stay semantically aligned. Because many macros are raw constants, compiler type checking provides little protection.

Test signals: successful build of all SAA7134 modules, correct probe-time hardware initialization, DMA IRQ completion, I2C transfers, GPIO IR events, TS/VBI/video capture, audio mute/stereo behavior, GO7007 HPI GPIO traffic, and register traces matching datasheet expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-ts.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-ts.c

Purpose: implements the shared MPEG transport-stream DMA queue and hardware programming for SAA7134 cards. DVB, Empress, and generic MPEG paths use it to capture TS packets through DMA channel 5.

Important APIs, types, and functions: module parameters `tsbufs` and `ts_nr_packets` configure buffer count and packets per buffer. Exported vb2 callbacks include `saa7134_ts_buffer_init()`, `saa7134_ts_buffer_prepare()`, `saa7134_ts_queue_setup()`, `saa7134_ts_start_streaming()`, `saa7134_ts_stop_streaming()`, and `saa7134_ts_qops`. Hardware functions `saa7134_ts_init_hw()`, `saa7134_ts_init1()`, `saa7134_ts_start()`, `saa7134_ts_stop()`, `saa7134_ts_fini()`, and IRQ handler `saa7134_irq_ts_done()` are used by core and MPEG modules.

Control flow: core early init calls `saa7134_ts_init1()` on MPEG-capable cards, which clamps module parameters, initializes `dev->ts_q`, marks the queue as needing two buffers, allocates a DMA page table, and initializes TS registers. Queue setup computes one-plane buffer size as `TS_PACKET_SIZE * dev->ts.nr_packets`. Buffer prepare validates plane size, sets payload, and builds the page table entries. Buffer activation alternates top/bottom field targeting between current and next buffers, writes `RS_BA1/BA2(5)`, enables DMA bits, arms a timeout, and starts TS hardware on the first buffer. IRQ completion waits for the expected top/bottom status bit before finishing a buffer and advancing the queue. Stop disables TS hardware and drains queued/current buffers through core stop helpers.

State and persistence: `dev->ts`, `dev->ts_q`, `dev->ts_field`, `dev->ts_started`, DMA page table contents, and TS MMIO registers are runtime-only. No persistent state exists.

Dependencies and integration points: depends on core buffer/page-table helpers, `saa7134_set_dmabits()`, vb2 DMA-SG, board metadata for TS serial/parallel type and forced valid bit, and core IRQ dispatch from `DONE_RA2`. Empress wraps these qops; DVB uses them directly; GO7007 overrides IRQ/start behavior for its encoder.

Risks: TS DMA channel 5 conflicts with planar video capture, so `saa7134_ts_start_streaming()` rejects TS when planar video is busy and requeues buffers. Queue activation needs a next buffer for ping-pong DMA; underflow or field mismatch can stall until timeout. Board `ts_type` and `ts_force_val` must match hardware wiring. Page-table lifetime must cover all queued buffers.

Test signals: TS buffer allocation with clamped sizes, DVB/Empress streamon and read/mmap paths, `-EBUSY` when planar video is active, top/bottom IRQ ordering, timeout recovery, serial and parallel TS board coverage, module unload freeing page tables, and absence of packet-size/payload mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-tvaudio.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-tvaudio.c

Purpose: manages analog TV/radio audio routing, mute/volume, I2S output, stereo/NICAM detection, carrier scanning, and SAA7133/7135 DSP audio standard detection for SAA7134-family cards.

Important APIs, types, and functions: module parameters enable debug, force DDEP audio standard, override audio clock, and fine-tune audio clocks per field. `mainscan[]` and `tvaudio[]` encode TV standards, carrier frequencies, and audio modes. SAA7134 paths include `tvaudio_carr2reg()`, `tvaudio_setcarrier()`, `mute_input_7134()`, `tvaudio_setmode()`, `tvaudio_checkcarrier()`, `tvaudio_getstereo()`, `tvaudio_setstereo()`, and `tvaudio_thread()`. SAA7133/7135 paths use DSP helpers `saa_dsp_writel()`, `mute_input_7133()`, `getstereo_7133()`, and `tvaudio_thread_ddep()`. Public entry points include `saa7134_enable_i2s()`, `saa7134_tvaudio_rx2mode()`, `saa7134_tvaudio_setmute()`, `saa7134_tvaudio_setinput()`, `saa7134_tvaudio_setvolume()`, `saa7134_tvaudio_getstereo()`, `saa7134_tvaudio_init()`, `saa7134_tvaudio_init2()`, `saa7134_tvaudio_close()`, `saa7134_tvaudio_fini()`, and `saa7134_tvaudio_do_scan()`.

Control flow: late hardware init starts the appropriate audio thread for the PCI device variant. For SAA7134, scan requests wake `tvaudio_thread()`, which resets audio state, applies automute, waits for tuner settling, scans candidate main carriers from the active TV norm, selects a carrier or fallback, probes matching audio modes for stereo/NICAM evidence, programs the chosen mode, and periodically updates stereo selection. For SAA7133/7135, `tvaudio_thread_ddep()` writes DSP standard-detection registers, waits, and logs decoded status. Input changes call `saa7134_tvaudio_setinput()`, which routes the internal audio mux, optional GPIO external mux, and I2S output. Mute/volume calls program the relevant analog or DSP registers.

State and persistence: runtime state includes `dev->input`, `dev->hw_input`, `dev->hw_mute`, `dev->ctl_mute`, `dev->ctl_automute`, `dev->automute`, `dev->ctl_volume`, `dev->last_carrier`, `dev->tvaudio`, and `dev->thread` scan/mode/thread flags. Hardware state lives in audio, DSP, GPIO, and I2S registers. No persistent state exists.

Dependencies and integration points: integrates with V4L2 tuner std/subchannel modes, board input/mute/GPIO/audio-clock metadata, core GPIO tracing, SAA7134 register accessors, kernel kthreads/freezer, Empress MPEG I2S audio output, and exported DSP write support for sound-related modules.

Risks: audio behavior is highly hardware-variant. Carrier scan thresholds can automute valid weak signals or choose the wrong standard. The SAA7133/7135 DSP access path has retry/timeouts and must clear error bits. GPIO external mux updates can affect board input routing. Thread stop/wake logic depends on `scan1/scan2` and suspend flags. Volume support only writes SAA7134 registers, so behavior differs by chip.

Test signals: analog TV audio for PAL/SECAM/NTSC standards, NICAM/stereo/lang detection, mute/automute and volume controls, input switching between TV/line/radio, FM radio standard detection on SAA7133/7135, I2S audio to MPEG encoder, suspend/resume scan wakeups, module unload stopping the thread, and debug logs for carrier scan and DSP status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-tvaudio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-vbi.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-vbi.c

Purpose: implements VBI capture queue setup, scaler programming, DMA setup, and IRQ completion for SAA7134 vertical blanking interval data.

Important APIs, types, and functions: module parameters `vbi_debug` and `vbibufs` control tracing and default buffer count. `task_init()` programs VBI scaler/task registers for Task A and Task B from the active TV norm. The file provides `saa7134_vbi_qops`, `saa7134_vbi_init1()`, `saa7134_vbi_fini()`, and `saa7134_irq_vbi_done()` for core/video integration.

Control flow: core early init calls `saa7134_vbi_init1()`, which initializes the VBI DMA queue and timeout and clamps buffer count. Queue setup computes VBI line count from the active TV norm, clamps it to 17 lines, fixes line length at 2048 bytes, and advertises one plane sized for two fields. Buffer prepare requires page-aligned SG offset, validates plane size, sets payload, and builds DMA page-table entries. Buffer activation programs both VBI tasks, sets output format, configures DMA channels 2 and 3 with top/bottom offsets into the same buffer, enables DMA bits through core, and arms a timeout. IRQ completion records that the first field was seen, waits for the second field, finishes the buffer, and advances the queue.

State and persistence: uses `dev->vbi_q`, `dev->vbi_hlen`, `dev->vbi_vlen`, current TV norm timing, per-buffer `top_seen`, and DMA page-table contents. All state is runtime-only.

Dependencies and integration points: depends on core buffer/page-table/DMA-bit helpers, vb2 DMA-SG, TV norm metadata, scaler/register definitions, and core IRQ dispatch for `DONE_RA0` VBI status. V4L2 device registration and ioctl exposure are handled by the video/core files.

Risks: VBI capture rejects non-page-aligned buffers because DMA programming assumes page-start alignment. TV norm changes affect line counts and scaler timings, so active streaming across norm changes must be coordinated by higher layers. Completion depends on seeing both fields in order; missed IRQs rely on timeout recovery. DMA channels 2 and 3 must stay consistent with `saa7134_set_dmabits()`.

Test signals: VBI device registration, buffer queue setup for PAL/NTSC norms, page-alignment rejection, capture producing two-field payloads of expected size, IRQ completion only after both fields, timeout recovery, norm-change behavior before streaming, and clean timer deletion on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-vbi.c -->
