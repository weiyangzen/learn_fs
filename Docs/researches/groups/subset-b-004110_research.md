# Research Report: subset-b-004110

This grouped report covers the exact source files assigned to `subset-b-004110`. Each file section is source-tree aligned and bounded for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dvb-bt8xx.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dvb-bt8xx.c

Purpose: Implements the Bt8xx DVB adapter glue between the bttv subdevice layer, the BT878 DMA core, Linux DVB demux/net devices, and board-specific frontend/tuner chips. It turns completed BT878 DMA transport-stream blocks into DVB software demux input and registers one DVB adapter per supported bttv board.

Important APIs/functions: `dvb_bt8xx_probe()` allocates `struct dvb_bt8xx_card`, maps bttv board type to GPIO/DMA mode fields, matches the companion `bt878` DMA device, and calls `dvb_bt8xx_load_card()`. `dvb_bt8xx_load_card()` registers the DVB adapter, demux, dmxdev, hardware/memory frontends, DVB net device, work item, and frontend. `frontend_init()` is the central board switch for MT352/ZL10353, LGDT330x, NXT6000, SP887x, DST, CX24110, and OR51211 frontends plus simple tuner attachments and tuner callbacks. `dvb_bt8xx_start_feed()`/`stop_feed()` reference count active demux feeds and start/stop BT878 DMA. `dvb_bt8xx_work()` consumes `finished_block` ring-buffer slots via `dvb_dmx_swfilter()` or `_204()`.

Control flow: module init registers a bttv sub-driver named `dvb`; probe selects board parameters, finds matching BT878 core by PCI slot/subsystem IDs, then builds the DVB stack. Streaming begins on the first demux feed, the BT878 core fills a cyclic buffer, and the bottom-half work drains all blocks between `last_block` and `finished_block` into DVB demux filtering. Remove stops DMA, cancels work, unregisters DVB net/demux/frontend/adapter objects, and frees card state.

State/persistence: Runtime state is in `struct dvb_bt8xx_card` plus BT878 fields such as `last_block`, `finished_block`, `block_bytes`, and `TS_Size`. `nfeeds` is protected by `card->lock`; the BT878 GPIO lock is initialized in probe. No on-disk persistence exists. Module parameters are `debug` and DVB adapter numbering.

Dependencies/integration: Depends on bttv subdevices, `bt878`, DVB core/demux/net APIs, I2C, frontend drivers, tuner-simple, firmware requests for SP887x and OR51211, and board IDs from bttv. It directly toggles bttv GPIO lines for resets, relays, and frontend mode selection.

Risks: Board support is a large hard-coded switch with chip-specific magic values and GPIO timing. Feed reference counting assumes balanced DVB demux callbacks; underflow would stop DMA incorrectly. Firmware request paths depend on the BT878 PCI device. Matching BT878 to bttv uses PCI slot/subsystem equality and may fail if another driver such as ALSA bt87x already owns the DMA core. Workqueue draining depends on coherent BT878 ring indices.

Test signals: Probe/remove on each supported board, frontend attach success/failure logs, DVB adapter registration, transport-stream capture, first-feed start and last-feed stop, firmware loading for affected boards, GPIO reset behavior, and error unwinds in `dvb_bt8xx_load_card()` are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dvb-bt8xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dvb-bt8xx.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dvb-bt8xx.h

Purpose: Defines the private card object for the bt8xx DVB adapter and gathers the external frontend, tuner, bttv, DVB, I2C, and mutex declarations needed by `dvb-bt8xx.c`.

Important APIs/types: `struct dvb_bt8xx_card` is the driver-owned state container. It holds synchronization (`lock`), feed count (`nfeeds`), card naming, `dvb_adapter`, BT878 pointer, bttv index, demux/dmxdev/frontend objects, BT878 GPIO/DMA mode masks, I2C adapter, DVB net state, and the attached `struct dvb_frontend *fe`.

Control flow: This header has no executable flow. Its fields are filled during probe, consumed during streaming/feed callbacks, and unwound during remove.

State/persistence: All fields are volatile per-device kernel state. The most important lifecycle-sensitive members are `bt`, `i2c_adapter`, `demux`, `dmxdev`, `dvbnet`, and `fe`, because cleanup order in the C file depends on them being initialized consistently.

Dependencies/integration: Includes bttv and a broad set of frontend headers (`mt352`, `sp887x`, `dst_common`, `nxt6000`, `cx24110`, `or51211`, `lgdt330x`, `zl10353`, `tuner-simple`). This tight coupling mirrors the board switch in the implementation.

Risks: The struct is shared across asynchronous work, DVB callbacks, and remove. Any future field additions that affect streaming need clear locking or teardown ordering. The header exposes no helper API, so the implementation must maintain lifecycle discipline manually.

Test signals: Compile coverage with all selected frontend dependencies, probe/remove smoke tests, and DVB streaming tests that exercise fields across feed start/stop and workqueue processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dvb-bt8xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/Kconfig

Purpose: Declares the `VIDEO_COBALT` kernel configuration option for the Cisco Cobalt PCIe V4L2 driver.

Important APIs/types: The symbol is a tristate module option. It depends on V4L2 device support, I2C, PCI MSI, complex MTD mappings, sound, MTD, and either a GPIOLIB/non-conflicting ADV7511 setup or compile-test. It selects media controller support, V4L2 subdevice API, I2C algorithm support, ALSA PCM, ADV7604/ADV7511/ADV7842 subdevice drivers, and vb2 DMA scatter-gather support.

Control flow: Kconfig selection determines whether `cobalt.o` is built and which framework/subdevice dependencies are enabled. At runtime the module registers a PCI driver for Cisco Cobalt devices.

State/persistence: No runtime state; it controls build-time availability and module linkage.

Dependencies/integration: The dependencies match the implementation: MSI is used for interrupts, MTD map support for NOR flash, ALSA PCM for audio nodes, ADV subdevices for HDMI input/output, and vb2 DMA-SG for buffer handling.

Risks: The `DRM_I2C_ADV7511=n` dependency avoids collision with a DRM ADV7511 driver, but can surprise users with unmet dependencies. Selecting many subdrivers increases build surface and may hide missing optional hardware until probe time.

Test signals: Kconfig allmodconfig/allyesconfig coverage, compile-test builds, module autoload, and dependency-resolution checks when ADV7511 DRM support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/Makefile

Purpose: Defines the object composition for the Cobalt driver module.

Important APIs/types: `cobalt-objs` links driver initialization, IRQ, V4L2, I2C, Omnitek DMA, flash, CPLD, and ALSA PCM implementation objects. `obj-$(CONFIG_VIDEO_COBALT) += cobalt.o` binds the aggregate module to Kconfig.

Control flow: Build system flow only; no runtime behavior.

State/persistence: No state. The object list controls which subsystems are linked into the single module.

Dependencies/integration: The file is the integration point between Kconfig and the C sources. It ensures ALSA support is built into the Cobalt module rather than as a separate module.

Risks: Missing any object from `cobalt-objs` would produce unresolved symbols or silently omit device functionality. Adding optional support here requires matching Kconfig dependencies.

Test signals: Module link success, modpost symbol checks, and load-time availability of V4L2, ALSA, MTD, I2C, DMA, and IRQ paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-main.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-main.c

Purpose: Creates and tears down ALSA card objects for Cobalt audio-capable streams, binding each audio stream to a `struct snd_cobalt_card` and its PCM device.

Important APIs/functions: `cobalt_alsa_init()` creates an ALSA `snd_card`, allocates private `snd_cobalt_card` state, sets card names, creates the PCM device through `snd_cobalt_pcm_create()`, stores `s->alsa`, and registers the card. `cobalt_alsa_exit()` frees the ALSA card and clears the stream pointer. Private free callbacks clear back-pointers so stream state does not retain stale ALSA references.

Control flow: Called from Cobalt node registration for non-dummy audio streams. Init proceeds in ALSA-driver order but deliberately assigns `s->alsa` before `snd_card_register()` to avoid races with userspace opening the device. Error paths free `snd_card` and allocation state.

State/persistence: `struct snd_cobalt_card` persists while the ALSA card exists and points back to the owning `cobalt_stream`. It stores runtime counters and substream pointers defined in `cobalt-alsa.h`. No persistent configuration is written.

Dependencies/integration: Integrates kernel ALSA core with the Cobalt stream model and V4L2 device logging. PCM behavior is implemented in `cobalt-alsa-pcm.c`.

Risks: The error path calls both `snd_card_free(sc)` and `kfree(cobsc)` even though card private free may also free private data depending on initialization stage; any changes here need careful ownership review. Card names assume one ALSA card per audio stream and use Cobalt instance/video channel.

Test signals: ALSA card creation/removal for HDMI input and HSMA output audio streams, open/close after registration, error injection around `snd_card_new`, private-data cleanup, and module unload with active or recently closed PCM devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-pcm.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-pcm.c

Purpose: Implements ALSA PCM capture and playback operations for Cobalt audio streams by running the stream's vb2 queue in a kernel thread and translating FPGA HDMI audio sample layout to/from ALSA ring buffers.

Important APIs/functions: `snd_cobalt_pcm_create()` creates either a capture or playback PCM based on `s->is_output`, resets the corresponding audio IP block, installs PCM ops, and uses managed vmalloc buffers. Capture flow uses `snd_cobalt_pcm_capture_open()`, `vb2_thread_start()`, `alsa_fnc()`, and `cobalt_alsa_announce_pcm_data()`. Playback flow uses `snd_cobalt_pcm_playback_open()`, `alsa_pb_fnc()`, trigger state `alsa_pb_channel`, and `cobalt_alsa_pb_pcm_data()`. `sample_cpy()` and `pb_sample_cpy()` remap channel order and 16/32-bit sample packing.

Control flow: On first open, a vb2 thread begins dequeuing queued video-style audio buffers. Capture copies each FPGA frame into the ALSA runtime DMA area, advances `hwptr_done_capture`, tracks period progress, and calls `snd_pcm_period_elapsed()` when needed. Playback copies from ALSA ring memory into outgoing FPGA buffer slots only while trigger state is active. Close stops the vb2 thread when the open count drops to zero.

State/persistence: State is in `struct snd_cobalt_card`: open counters, capture/playback substreams, hardware pointer, period counters, playback buffer size/period/position, and active trigger flag. No state persists across device removal.

Dependencies/integration: Depends on ALSA PCM core, vb2 queue/thread APIs, Cobalt stream reset bits, and the V4L2/vb2 DMA setup from `cobalt-v4l2.c`.

Risks: Capture copy updates most ALSA counters under `snd_pcm_stream_lock_irqsave()` but performs the memory copy before locking; playback uses `pb_count` for iteration and period signaling, so unusual runtime sizes need testing. Channel remapping is hard-coded to Cobalt HDMI ordering. Trigger start returns `-EBUSY` if already active. The queue is shared with V4L2-style setup, so format/queue changes could affect audio behavior.

Test signals: `arecord`/`aplay` at 48 kHz, S16_LE and S32_LE, 1-8 channels, period elapsed cadence, wraparound copying, repeated open/close, trigger start/stop, vb2 thread start failure, and audio IP reset observation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-pcm.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-pcm.h

Purpose: Declares the Cobalt ALSA PCM creation entry point.

Important APIs/types: `snd_cobalt_pcm_create(struct snd_cobalt_card *cobsc)` is called by `cobalt_alsa_init()` after the ALSA card and private card state exist.

Control flow: Header-only declaration; implementation creates capture or playback PCM devices depending on the associated stream direction.

State/persistence: No state; the function consumes and initializes fields in `struct snd_cobalt_card`.

Dependencies/integration: Depends on `struct snd_cobalt_card` from `cobalt-alsa.h` and ALSA PCM core in the implementation.

Risks: The header intentionally exposes only one creation API, so future PCM helper exports require explicit declaration here.

Test signals: Compile/link checks between ALSA main and PCM objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa.h

Purpose: Defines Cobalt ALSA private card state and the stream-level ALSA lifecycle API.

Important APIs/types: `struct snd_cobalt_card` stores the owning `cobalt_stream`, ALSA `snd_card`, capture counters, capture substream, playback buffer sizing/position, playback active flag, playback open count, and playback substream. It declares `cobalt_alsa_init()` and `cobalt_alsa_exit()`.

Control flow: The struct fields are initialized by ALSA card creation, then updated by PCM open/close/prepare/trigger/pointer and vb2 thread callbacks.

State/persistence: All fields are runtime-only and tied to one audio stream. `alsa_record_cnt` and `alsa_playback_cnt` protect vb2 thread start/stop. `hwptr_done_capture` and `pb_pos` are ALSA hardware pointer sources.

Dependencies/integration: Bridges `cobalt_stream` from the Cobalt core to ALSA `snd_card`/`snd_pcm_substream` state. Included by node registration, ALSA main, and PCM implementation.

Risks: There is no explicit lock in this struct; the PCM code relies on ALSA stream locks and vb2 thread serialization. Any new shared fields need a clear locking model.

Test signals: Compile coverage, concurrent ALSA open/close, pointer accuracy, and teardown with active substreams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-cpld.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-cpld.c

Purpose: Provides Cobalt CPLD access, board status reporting, and programmable HSMA output clock setup through the CPLD/SI570-style oscillator registers.

Important APIs/functions: `cobalt_cpld_status()` reads CPLD revision and prints supported revision 3/4/5 status via `cpld_info_ver3()`. `cobalt_cpld_set_freq()` finds a valid oscillator multiplier, computes RFREQ/hsdiv/n1 register values, writes SI570 registers, triggers the write/reset sequence, verifies readback, and returns whether the requested output frequency is in range. Internal helpers `cpld_read()` and `cpld_write()` use Cobalt bus accessors.

Control flow: Status is invoked from V4L2 log-status. Output streaming calls `cobalt_cpld_set_freq()` before programming the HSMA output sync generator. Frequency programming searches the multiplier table for a DCO within 4.85-5.67 GHz with minimal remainder error, writes six oscillator registers, toggles clock-control bits, and retries readback mismatch up to three times.

State/persistence: CPLD and oscillator register values persist in hardware while powered/configured. Driver software keeps no cache. Status reads board serial, program revision, temperatures, and voltage ADC values.

Dependencies/integration: Uses `cobalt_bus_read32()`/`cobalt_bus_write32()` from `cobalt-driver.h`, Cobalt logging macros, and Cobalt output setup in `cobalt-v4l2.c`.

Risks: Large hard-coded multiplier table and timing-sensitive write/reset sequence. `cobalt_cpld_set_freq()` returns true even after all retries are exhausted, as long as a candidate frequency was found, so readback failure is only logged/debugged. Voltage conversions are integer approximations.

Test signals: V4L2 log-status CPLD output, output streaming at common HDMI pixel clocks, invalid pixelclock rejection, oscillator register readback, retry logging, and scope/monitor validation of HSMA clock frequency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-cpld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-cpld.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-cpld.h

Purpose: Declares the Cobalt CPLD status and frequency programming APIs.

Important APIs/types: `cobalt_cpld_status(struct cobalt *cobalt)` logs board/CPLD telemetry. `cobalt_cpld_set_freq(struct cobalt *cobalt, unsigned freq)` programs the HSMA output oscillator and returns success/failure.

Control flow: Consumers call status from diagnostic paths and frequency setup from video output start.

State/persistence: No header state. Functions operate on hardware state behind `struct cobalt`.

Dependencies/integration: Includes `cobalt-driver.h` for the `struct cobalt` definition and bus helpers.

Risks: The header exposes hardware-side effects through a simple boolean API; callers cannot distinguish unsupported frequency from oscillator readback retry failure.

Test signals: Compile/link checks and output streaming paths that call `cobalt_cpld_set_freq()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-cpld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-driver.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-driver.c

Purpose: Implements PCI probe/remove and high-level initialization for the Cisco Cobalt driver, including PCI resource setup, MSI, I2C bus registration, ADV HDMI subdevice creation, stream topology setup, V4L2/ALSA node registration, interrupt enabling, and flash probing.

Important APIs/functions: `cobalt_probe()` is the main lifecycle entry. `cobalt_setup_pci()` enables the PCI device, validates link width, sets DMA mask, requests/maps BARs, disables interrupts, allocates MSI, requests IRQ, and initializes Omnitek DMA. `cobalt_stream_struct_init()` maps logical streams to DMA/video/audio roles. `cobalt_subdevs_init()` creates four ADV7604 HDMI receivers and marks associated video/audio streams live. `cobalt_subdevs_hsma_init()` detects either an ADV7842 HSMA receiver or ADV7511 transmitter and sets `have_hsma_rx`/`have_hsma_tx`. `cobalt_set_interrupt()` programs system interrupt masks. `cobalt_notify()` handles subdevice hotplug and source-change notifications.

Control flow: PCI probe allocates `struct cobalt`, registers the V4L2 device and IRQ workqueue, sets up PCI/MSI, reads HDL info, initializes I2C, initializes stream records, registers input and HSMA subdevices, creates V4L2/ALSA nodes, enables interrupts, services pending subdevice interrupts, probes flash, and returns. Error labels unwind in reverse. Remove unregisters flash, disables interrupts, flushes work, unregisters nodes/subdevices/I2C/MSI/BARs, disables PCI, destroys workqueue, unregisters V4L2, and frees state.

State/persistence: `struct cobalt` owns all runtime state: PCI/V4L2 handles, BAR mappings, card revision, stream array, I2C adapters, HSMA flags, IRQ counters/workqueue, DMA capabilities, HDL info, and MTD pointer. Hardware state includes sysctrl/sysstat bits, reset lines, interrupt masks, and subdevice EDID/configuration.

Dependencies/integration: Integrates PCI core, V4L2 device/subdev/control/event APIs, ADV7604/ADV7842/ADV7511 I2C subdrivers, Omnitek DMA, Cobalt I2C, V4L2 nodes, ALSA, IRQ, flash, and CPLD support.

Risks: Initialization order is hardware-sensitive; interrupts are disabled before subdevice setup and enabled only after nodes register. Probe fails on PCIe link-width mismatch where a seating issue is inferred. `cobalt_ignore_err` can hide missing I2C/subdevice problems by creating dummy nodes. HSMA detection treats absence of RX as possible TX, so board wiring assumptions matter. Error paths must maintain reverse-order cleanup for partially initialized hardware.

Test signals: PCI probe/remove, MSI request/free, BAR mapping including 64-bit BAR fallback, HDL info read, all I2C adapters, ADV subdevice registration, EDID programming, HSMA RX/TX detection, dummy-node behavior under `ignore_err`, flash probe, and suspend-like remove under active users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-driver.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-driver.h

Purpose: Defines the Cobalt driver's core constants, register layout, logging macros, DMA/helper structs, per-stream state, per-card state, and MMIO/bus accessors.

Important APIs/types: `struct cobalt_stream` models one video/audio input/output or dummy stream, including `video_device`, `vb2_queue`, buffer list, subdevice, locks, DV timings, format fields, DMA channel, IRQ masks, descriptor info, stability flags, role flags, parent pointer, and ALSA pointer. `struct cobalt` owns card-wide PCI/V4L2/MMIO/I2C/IRQ/DMA/flash state. Helper types include `cobalt_i2c_data`, `pci_consistent_buffer`, `sg_dma_desc_info`, and `cobalt_buffer`. Inline helpers read/write BAR0/BAR1, sysctrl/sysstat, and Cobalt bus windows.

Control flow: No standalone flow, but the macros and structs drive all Cobalt modules. Stream fields are initialized in `cobalt-driver.c`, consumed by V4L2/vb2/IRQ/ALSA/DMA code, and torn down during node and PCI removal.

State/persistence: This header defines the in-memory state graph for the driver. Persistent hardware state is accessed through sysctrl/sysstat and bus macros. `cobalt_s_bit_sysctrl()` serializes read-modify-write with `pci_lock`.

Dependencies/integration: Includes V4L2/vb2 DMA-SG, PCI, I2C, workqueue, mutex/spinlock, and generated FPGA register-map headers. It is the common dependency for all Cobalt implementation files.

Risks: Many hardware addresses and bit masks are hard-coded. `COBALT_NUM_STREAMS` differs from `DMA_CHANNELS_MAX`, so loops must use the right bound. `cobalt_bus_write32()` takes a `u16 data` parameter despite writing 32 bits, which is surprising and can truncate callers that expect full 32-bit writes. Inline bus macros depend on local variable naming in macro definitions.

Test signals: Build coverage across all Cobalt objects, static analysis for struct/loop bounds, sysctrl concurrent updates, DMA descriptor allocation for all stream types, and register access on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-flash.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-flash.c

Purpose: Exposes the Cobalt board NOR flash as an MTD CFI map through the Cobalt CPU bus window.

Important APIs/functions: `cobalt_flash_probe()` configures a static `map_info`, binds custom read/write/copy callbacks, runs `do_map_probe("cfi_probe")`, sets owner/parent, and registers the MTD device. `cobalt_flash_remove()` unregisters and destroys the MTD map. `flash_read16()`, `flash_write16()`, `flash_copy_from()`, and `flash_copy_to()` translate MTD byte/word accesses to Cobalt bus reads/writes at `COBALT_BUS_FLASH_BASE`.

Control flow: Probe is called after the main Cobalt card is initialized. MTD core subsequently calls map callbacks for reads/writes. Remove tears down only if `cobalt->mtd` exists.

State/persistence: The flash contents are persistent board storage. Driver state is the static `cobalt_flash_map` plus `cobalt->mtd`. `map->virt` is set to BAR1 for each probed card, making the static map unsuitable for multiple cards without serialization/instance separation.

Dependencies/integration: Uses Linux MTD map/CFI APIs and Cobalt bus accessors from `cobalt-driver.h`.

Risks: Static `map_info` is shared across devices, so multiple Cobalt cards could race or overwrite `virt`. `flash_copy_to()` builds 16-bit writes from bytes and logs every copy, which can be noisy. Writes to flash are high risk and depend on correct endian/offset handling.

Test signals: MTD probe success, readback from known flash offsets, erase/write/read cycles on a safe partition, remove cleanup, and multi-card behavior if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-flash.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-flash.h

Purpose: Declares Cobalt NOR flash lifecycle helpers.

Important APIs/types: `cobalt_flash_probe(struct cobalt *cobalt)` registers the flash MTD map. `cobalt_flash_remove(struct cobalt *cobalt)` unregisters and destroys it.

Control flow: Called from Cobalt PCI probe/remove after the device and BARs are live.

State/persistence: No header state; functions operate on persistent NOR flash and `cobalt->mtd`.

Dependencies/integration: Includes `cobalt-driver.h` for the card state and bus accessors used by the implementation.

Risks: The simple lifecycle API does not expose detailed MTD probe errors to the main probe path, which currently ignores flash probe failure.

Test signals: Compile/link checks and MTD device appearance/removal after Cobalt probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-flash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-i2c.c

Purpose: Implements the memory-mapped I2C master controller support for five Cobalt I2C buses, registering Linux `i2c_adapter` instances used by ADV HDMI subdevices.

Important APIs/functions: `cobalt_i2c_init()` resets/enables each controller, sets the 400 kHz prescaler from `ALT_CPU_FREQ`, fills adapter metadata, and calls `i2c_add_adapter()`. `cobalt_i2c_exit()` deletes adapters. `cobalt_xfer()` implements I2C master transfers over one or more `i2c_msg`s. Low-level helpers `cobalt_tx_bytes()`, `cobalt_rx_bytes()`, and `cobalt_stop()` program the core command/status registers and poll TIP, ACK, and arbitration bits.

Control flow: For each message, `cobalt_xfer()` optionally sends the address with START, then reads or writes payload bytes with STOP only on the last message. Address write retries use `adap->retries`; transfer timeouts use `adap->timeout`. On failure it emits a synthetic stop sequence.

State/persistence: Per-bus state is `struct cobalt_i2c_data` with parent card and register base; adapter fields store retries, parent, algo, and name. Hardware state includes prescaler, control, command/status, and bus busy/transfer bits.

Dependencies/integration: Used by Cobalt probe to instantiate ADV7604/ADV7842/ADV7511 subdevices. Depends on Linux I2C core and Cobalt BAR1 register layout.

Risks: Poll loops rely on `adap->timeout`; the template does not set an explicit timeout, so I2C core defaults matter. `cobalt_i2c_exit()` deletes all adapters even if `cobalt_ignore_err` caused a later adapter to have `dev.parent = NULL`, which needs caution. The custom stop workaround is hardware-specific. A bus timeout during init with `ignore_err` returns success early and skips remaining adapters.

Test signals: I2C scan/subdevice probe on all five buses, repeated combined read/write transactions, NACK and arbitration-loss handling, timeout behavior, ignore-error path, and adapter cleanup on partial init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-i2c.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-i2c.h

Purpose: Declares Cobalt I2C adapter lifecycle functions.

Important APIs/types: `cobalt_i2c_init(struct cobalt *cobalt)` registers all hardware I2C adapters. `cobalt_i2c_exit(struct cobalt *cobalt)` unregisters them.

Control flow: Called during Cobalt PCI probe before subdevice creation and during remove/error unwind after subdevice/node cleanup.

State/persistence: No header state. The implementation initializes `cobalt->i2c_adap[]` and `cobalt->i2c_data[]`.

Dependencies/integration: Interfaces the Cobalt core with Linux I2C and downstream ADV subdevice probes.

Risks: The header exposes all-or-nothing init/exit even though `ignore_err` can leave some adapters absent.

Test signals: Compile/link checks and subdevice probe paths requiring the adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-irq.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-irq.c

Purpose: Handles Cobalt MSI interrupts for DMA completions, ADV subdevice events, FIFO/data-loss conditions, and deferred subdevice interrupt servicing.

Important APIs/functions: `cobalt_irq_handler()` is the top-half IRQ handler. It reads/clears DMA interrupt status and system edge status, temporarily masks edge sources, completes DMA buffers per stream, sets ADV IRQ flags, updates counters, queues `cobalt_irq_work_handler()`, and returns handled. `cobalt_dma_stream_queue_handler()` removes the completed buffer, handles unstable capture lock/freewheel/CVI state, timestamps/sequences it, and returns it to vb2. `cobalt_irq_work_handler()` calls subdevice `interrupt_service_routine` and unmasks ADV IRQs. `cobalt_irq_log_status()` logs and resets counters and re-enables lost-data masks.

Control flow: DMA completion removes the oldest queued buffer because descriptor chaining guarantees the interrupt occurs only when DMA can continue. For video capture, initial frames are marked error while measurement, clock-loss, CVI lock, and freewheel state converge; lock loss restarts the freewheel recovery sequence. ADV interrupts are deferred to a single-thread workqueue to avoid doing I2C-heavy subdevice work in hard IRQ context.

State/persistence: Uses per-stream `bufs`, `irqlock`, `flags`, `unstable_frame`, `enable_cvi`, `enable_freewheel`, `skip_first_frames`, and sequence counters. Card-wide IRQ counters persist until log-status resets them.

Dependencies/integration: Works with Cobalt V4L2/vb2 queues, generated FPGA register maps, Omnitek DMA, ADV7604-style subdevice IRQ callbacks, and system status masks from `cobalt-driver.h`.

Risks: The handler assumes a buffer exists on DMA interrupt; empty list logs an error and drops handling. Buffer list manipulation is split before stability checks, so hardware state checks happen outside the lock. FIFO/data-loss masking depends on edge/mask ordering. Stability logic is tied to exact FPGA status semantics and may mark multiple startup frames as errors.

Test signals: Streaming DMA interrupt cadence, buffer DONE/ERROR states during stable and unstable video, cable unplug/replug recovery, ADV source-change event delivery, FIFO-full logs, counter reset in log-status, and interrupt storm/no-interrupt cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-irq.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-irq.h

Purpose: Declares Cobalt IRQ entry points and diagnostics.

Important APIs/types: `cobalt_irq_handler()` is registered with `request_irq()`. `cobalt_irq_work_handler()` is used as the deferred workqueue callback. `cobalt_irq_log_status()` reports and resets IRQ counters.

Control flow: The top half queues the work handler for subdevice interrupt service; diagnostics are called from V4L2 log-status.

State/persistence: No header state; functions operate on `struct cobalt` and `struct cobalt_stream` internals.

Dependencies/integration: Includes Linux interrupt declarations and is consumed by PCI setup, V4L2 status, and workqueue initialization.

Risks: Function declarations depend on `struct cobalt` being visible to includers through `cobalt-driver.h` or prior declarations.

Test signals: Compile/link checks and successful `request_irq()` binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-omnitek.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-omnitek.c

Purpose: Implements support for the Omnitek scatter-gather DMA controller used by Cobalt streams, including channel discovery, descriptor creation, chaining, start, done, abort, allocation, and cleanup.

Important APIs/functions: `omni_sg_dma_init()` reads capability registers, determines channel count, 32/64-bit PCI support, counts memory channels before FIFO channels, aborts active channels, and logs capabilities. `omni_sg_dma_start()`, `is_dma_done()`, and `omni_sg_dma_abort_channel()` control a stream DMA channel. `descriptor_list_create()` converts a vb2 DMA scatterlist into hardware descriptors with line width/stride handling and interrupt-enabled loopback. `descriptor_list_chain()`, `descriptor_list_loopback()`, `descriptor_list_end_of_chain()`, and interrupt enable/disable helpers modify the final descriptor. Allocation/free use coherent DMA memory.

Control flow: V4L2 buffer init allocates/creates descriptors. Queuing loops a descriptor back to itself, disables its interrupt, adds it to the stream list, and chains all queued buffers. Streaming starts DMA at the first descriptor. Stop marks descriptor chains end-of-chain and waits or aborts.

State/persistence: Descriptor memory is per-buffer in `s->dma_desc_info[]`. Controller capabilities populate `cobalt->dma_channels`, `first_fifo_channel`, and `pci_32_bit`. Hardware channel control/status registers carry active/done/abort state.

Dependencies/integration: Tightly integrated with vb2 DMA-SG, Cobalt V4L2 queue ops, IRQ completion, and BAR0 DMA registers.

Risks: Descriptor generation assumes 4-byte alignment for addresses, size, stride, and descriptor bus addresses. The code rejects 64-bit DMA addresses when hardware reports 32-bit PCI mode. Descriptor memory sizing must cover worst-case pages per line; underruns could corrupt memory. `descriptor_list_create()` forces at least two descriptors for one-entry scatterlists. `descriptor_list_chain()` assumes `last_desc_virt` is valid.

Test signals: DMA capability logs, capture/output/audio streaming, high fragmentation USERPTR/DMABUF buffers, 32-bit DMA mask fallback, end-of-chain stop without timeout, abort path, and descriptor validation under max frame size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-omnitek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-omnitek.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-omnitek.h

Purpose: Defines the Omnitek DMA descriptor layout and declares DMA/descriptor helper APIs.

Important APIs/types: `struct sg_dma_descriptor` matches the hardware descriptor format with PCI address, local sync marker, next pointer, byte count, and reserved fields. Public functions initialize DMA, start/abort/check channels, create descriptor lists, chain/loop/end descriptor lists, allocate/free coherent descriptor memory, and toggle descriptor interrupts.

Control flow: Header declarations support V4L2 queue setup, streaming start/stop, and IRQ completion.

State/persistence: No header state. Descriptor instances persist per vb2 buffer while allocated.

Dependencies/integration: Includes Linux scatterlist and Cobalt driver definitions. Used by V4L2 and IRQ modules.

Risks: The descriptor struct must remain exactly aligned with FPGA expectations; field reordering or type changes would break DMA.

Test signals: Build checks and runtime DMA streaming across all stream directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-omnitek.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-v4l2.c

Purpose: Implements the Cobalt V4L2 video node API, vb2 queue operations, format/timing/input/output/EDID ioctls, stream start/stop hardware programming, and node registration/unregistration.

Important APIs/functions: vb2 ops include `cobalt_queue_setup()`, `cobalt_buf_init()`, `cobalt_buf_queue()`, `cobalt_start_streaming()`, and `cobalt_stop_streaming()`. Hardware setup helpers `cobalt_enable_input()`, `cobalt_enable_output()`, `cobalt_dma_start_streaming()`, and `cobalt_dma_stop_streaming()` program packer, CVI, measurement, freewheel, clock-loss, syncgen, CPLD clock, and DMA. Ioctls cover capabilities, log-status, DV timings, formats, input/output selection, EDID, events, parameters, pixel aspect, and selection. `cobalt_nodes_register()` creates all stream nodes; `cobalt_nodes_unregister()` tears them down.

Control flow: Node registration initializes stream locks, default 1080p60 timing, default format, vb2 queue, video-device fields, and either video device registration or ALSA init. Buffer init builds DMA descriptors from vb2 SG tables. Queueing appends buffers under `irqlock` and chains descriptors. Stream-on programs input/output hardware, resets sequence, and starts DMA from the first queued buffer. Stream-off stops event counters/DMA, returns all queued buffers as errors, and disables measurement/freewheel/clock-loss for capture.

State/persistence: Per-stream V4L2 state includes width/height/stride/bpp/pixfmt/colorspace/timings/input/sequence, queued buffer list, descriptor info, and stability flags. Hardware state includes CVI, packer, VMR, freewheel, clock-loss, syncgen, and subdevice formats/EDID. No persistent storage.

Dependencies/integration: Depends on V4L2/vb2 DMA-SG, ADV subdevice pad/video/audio APIs, Cobalt IRQ/DMA/CPLD modules, generated register maps, and ALSA node creation for audio streams.

Risks: Format changes are blocked only when vb2 is busy; callers must keep format and descriptor sizes consistent. `cobalt_s_fmt_vid_cap()` calls `cobalt_enable_input()` even outside streaming. Output pixelclock programming can fail silently aside from logging if `cobalt_cpld_set_freq()` returns false. Dummy nodes expose only debug-register ops. Queue start assumes at least one queued buffer due to vb2 minimums. Stream-off abort timeout is fixed at 100 ms.

Test signals: v4l2-compliance, capture/output streaming with MMAP/USERPTR/DMABUF/read/write, format negotiation, DV timing changes while idle/busy, EDID get/set, HDMI source-change events, log-status coverage, dummy node behavior, ALSA node registration, and stop/abort behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-v4l2.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-v4l2.h

Purpose: Declares Cobalt V4L2 node lifecycle functions.

Important APIs/types: `cobalt_nodes_register(struct cobalt *cobalt)` initializes and registers video and ALSA stream nodes. `cobalt_nodes_unregister(struct cobalt *cobalt)` unregisters video devices and exits ALSA devices.

Control flow: Called from PCI probe after hardware/subdevices are initialized and from remove/error paths before lower-level resources are freed.

State/persistence: No header state. Functions initialize or release state embedded in `struct cobalt_stream`.

Dependencies/integration: Bridges the main driver lifecycle with the V4L2/ALSA stream layer.

Risks: Lifecycle callers must preserve ordering: subdevices and PCI resources must exist during register, and active users must be quiesced before unregister completes.

Test signals: Compile/link checks and Cobalt probe/remove node creation/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-v4l2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00233_video_measure_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00233_video_measure_memmap_package.h

Purpose: Generated-style register map for the FPGA video measurement block used to detect timing stability and active/blanking dimensions.

Important APIs/types: `struct m00233_video_measure_regmap` maps IRQ status, vertical/horizontal timing counters, control, IRQ triggers, hsync timeout, and status registers. Macros define register offsets and bit masks for timing IRQ status/triggers, polarity, measure enable, interrupt enable, update-on-hsync, hsync timeout, and init-done.

Control flow: Cobalt capture start clears/enables measurement, writes `hsync_timeout_val`, and enables selected active-area IRQ triggers. IRQ handling reads `irq_status`, `status`, `vactive_area`, and `hactive_area` to decide whether frames are stable and whether CVI/freewheel can be enabled.

State/persistence: Hardware counters and status bits reflect current video signal timing. Software keeps no cache beyond values read into stream stability decisions.

Dependencies/integration: Included by `cobalt-driver.h`; used in V4L2 log-status/start and IRQ stability handling.

Risks: Struct layout must match FPGA register layout exactly. Timing masks are hard-coded and must match the bitstream. Incorrect measurements lead to skipped/error frames or false lock.

Test signals: Log-status timing values, stable/unstable frame transitions, active-area IRQs on signal changes, and hsync timeout detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00233_video_measure_memmap_package.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00235_fdma_packer_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00235_fdma_packer_memmap_package.h

Purpose: Register map for the FPGA FDMA packer block that converts video bus pixels into DMA memory packing formats.

Important APIs/types: `struct m00235_fdma_packer_regmap` contains a single `control` register. Macros define enable, two-bit pack-format selector, and endian-format bit.

Control flow: `cobalt_enable_input()` writes the control register for YUYV, RGB24, or BGR32 capture formats before streaming.

State/persistence: The control register persists in hardware until changed or reset.

Dependencies/integration: Used by Cobalt V4L2 format setup and log-status through `COBALT_CVI_PACKER()`.

Risks: Pack-format values are encoded by shifts in the caller rather than named enum constants; mismatches with FPGA definitions would corrupt captured pixel layout.

Test signals: Capture in YUYV/RGB24/BGR32, bytesperline correctness, color channel order validation, and log-status packer control value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00235_fdma_packer_memmap_package.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00389_cvi_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00389_cvi_memmap_package.h

Purpose: Register map for the Cobalt video input block that gates/locks the incoming video stream and tracks configured frame size.

Important APIs/types: `struct m00389_cvi_regmap` maps control, frame width/height, freewheel period, error color, and status. Bit masks define enable, sync polarity bits, lock status, and error status.

Control flow: Capture startup programs frame width/height and leaves CVI disabled until the IRQ stability state machine sees correct measurement and clock status. The IRQ handler enables CVI and waits for lock before disabling forced freewheel.

State/persistence: Hardware control and status reflect current capture path state. Stream flags mirror portions of the state machine.

Dependencies/integration: Used by V4L2 start/log-status and IRQ lock handling through `COBALT_CVI()`.

Risks: Enabling CVI too early produces unstable frames; missing lock forces recovery. Register layout must match the FPGA.

Test signals: Lock/no-lock transitions, frame size programming, error status logging, and recovery after signal loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00389_cvi_memmap_package.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00460_evcnt_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00460_evcnt_memmap_package.h

Purpose: Register map for a small FPGA event counter block used by Cobalt input/output paths.

Important APIs/types: `struct m00460_evcnt_regmap` exposes `control` and `count`. Masks define enable and clear bits.

Control flow: Capture start and DMA start clear/enable the counter. Stop disables it. Log-status can read related counts from other blocks.

State/persistence: Counter value is hardware runtime state, reset by clear bit or hardware reset.

Dependencies/integration: Used through `COBALT_CVI_EVCNT()` in V4L2 streaming setup and stop paths.

Risks: Counter semantics depend on FPGA event source; missed clear/enable ordering can produce stale diagnostics.

Test signals: Counter increments during streaming, resets on stream start, and disables on stream stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00460_evcnt_memmap_package.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00473_freewheel_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00473_freewheel_memmap_package.h

Purpose: Register map for the FPGA freewheel block that generates fallback timing/color when input video timing is unstable or missing.

Important APIs/types: `struct m00473_freewheel_regmap` maps control, status, active/total lengths, data width, output color, and measured clock frequency. Masks define enable, forced freewheel mode, and freewheel status.

Control flow: Capture start programs active/total lengths and output color, then enables forced freewheel. IRQ stability handling disables forced mode when CVI locks, enables normal freewheel monitoring, and restarts forced freewheel after lock loss.

State/persistence: Hardware state tracks freewheel mode and clock/timing parameters. Stream flags track the staged transition out of forced freewheel.

Dependencies/integration: Used by V4L2 start/stop/log-status and IRQ stability handling via `COBALT_CVI_FREEWHEEL()`.

Risks: Incorrect active/total length calculations cause bad fallback timing. Freewheel status drives error-frame decisions, so FPGA/software semantic drift can affect capture quality.

Test signals: Forced freewheel on stream start, transition to video passthrough after stable lock, re-entry on signal loss, and log-status status bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00473_freewheel_memmap_package.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00479_clk_loss_detector_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00479_clk_loss_detector_memmap_package.h

Purpose: Register map for the FPGA clock-loss detector used to validate incoming video clock presence.

Important APIs/types: `struct m00479_clk_loss_detector_regmap` exposes control, status, reference-clock count, and required test-clock count. Masks define enable and clock-missing status.

Control flow: Capture start programs reference/test counts based on freewheel clock and expected pixelclock, then enables detection. IRQ handling resets the detector when clock is missing and keeps frames unstable until clock returns.

State/persistence: Hardware status indicates current clock presence. Threshold registers persist until changed.

Dependencies/integration: Used by V4L2 start/stop/log-status and IRQ lock recovery via `COBALT_CVI_CLK_LOSS()`.

Risks: Threshold calculation uses integer scaling and a 0.5 percent lower bound; unusual timings or clock tolerances may false-positive clock loss.

Test signals: Clock present/missing log-status, cable disconnect/reconnect, nonstandard pixelclock tolerance, and detector reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00479_clk_loss_detector_memmap_package.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00514_syncgen_flow_evcnt_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00514_syncgen_flow_evcnt_memmap_package.h

Purpose: Register map for the HSMA video output sync generator, flow-control, and event counter block.

Important APIs/types: `struct m00514_syncgen_flow_evcnt_regmap` maps output control, horizontal/vertical sync/backporch/active/frontporch lengths, error color, read status, and event count. Masks cover parameter load, sync generator enable, output enable, sync polarity, event counter enable/clear, 16-bpp format, error color channels, no-data, and ready-buffer-full status.

Control flow: `cobalt_enable_output()` writes timing parameters from V4L2 DV timings, sets error color, loads parameters, clears counters, and enables sync generation plus flow-control output. DMA start/stop clear/enable/disable the event counter.

State/persistence: Hardware output timing and status persist while output is configured. Stream format/timings are the software source.

Dependencies/integration: Used by Cobalt V4L2 output path through `COBALT_TX_BASE()`, with CPLD clock programming and ADV7511 output subdevice setup.

Risks: Timing registers must match the programmed output pixelclock; mismatches can break HDMI output. Format bit only distinguishes 16 bpp versus other formats, so caller must keep it in sync with packer/subdevice format.

Test signals: HDMI output at 1080p60 and other timings, no-data/ready-buffer-full status, event count increment, YUYV versus BGR32 output, and monitor lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00514_syncgen_flow_evcnt_memmap_package.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/Kconfig

Purpose: Declares build configuration for the Conexant cx23418 MPEG encoder driver and its optional ALSA DMA audio support.

Important APIs/types: `VIDEO_CX18` is a tristate V4L2/DVB/PCI/I2C/RC driver selecting I2C algobit, vb2 vmalloc, tuner/eeprom/cx2341x helpers, and optional auto-selected DVB/tuner subdrivers. `VIDEO_CX18_ALSA` is a separate tristate depending on `VIDEO_CX18` and `SND`, selecting `SND_PCM`.

Control flow: Determines whether `cx18.o` and `cx18-alsa.o` are built and whether supporting subdrivers are auto-selected.

State/persistence: Build-time only.

Dependencies/integration: Mirrors implementation dependencies: V4L2, DVB core, PCI, I2C, RC core, tuner/eeprom helpers, and ALSA PCM.

Risks: ALSA support is split into a separate module that hooks the main driver through an extension callback, so module load ordering affects ALSA device creation.

Test signals: Kconfig dependency resolution, allmodconfig builds, module load with and without `cx18-alsa`, and auto-selected tuner/frontend coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/Makefile

Purpose: Defines cx18 module object composition and include paths.

Important APIs/types: `cx18-objs` links the main driver, board tables, I2C, firmware, GPIO, queues, streams, fileops, ioctl, controls, mailbox, VBI, audio/video, IRQ, AV core/audio/firmware/VBI, SCB, DVB, and IO objects. `cx18-alsa-objs` links ALSA main and PCM objects. `obj-$(CONFIG_VIDEO_CX18)` and `obj-$(CONFIG_VIDEO_CX18_ALSA)` bind modules to Kconfig. Include paths expose DVB frontend and tuner headers.

Control flow: Build-system only.

State/persistence: No state.

Dependencies/integration: Separates core capture driver from optional ALSA module, matching runtime extension callback behavior.

Risks: Missing object entries break symbol resolution or leave driver features unavailable. Include-path reliance can hide header movement issues.

Test signals: Module link success for both configs, modpost checks, and successful load of `cx18` and `cx18-alsa`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-main.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-main.c

Purpose: Implements the optional ALSA module entry point for cx18 PCM capture, creating ALSA card instances for existing cx18 devices and cleaning them up on module unload.

Important APIs/functions: `cx18_alsa_init()` sets the global `cx18_ext_init` callback to `cx18_alsa_load()`. `cx18_alsa_load()` validates the cx18 V4L2 device, checks that the PCM stream is enabled, prevents duplicate ALSA cards, and calls `snd_cx18_init()`. `snd_cx18_init()` creates `snd_card`, allocates `struct snd_cx18_card`, sets names, creates PCM via `snd_cx18_pcm_create()`, stores `cx->alsa`, and registers the card. Exit finds the `cx18` PCI driver and iterates devices to free each ALSA card.

Control flow: Loading `cx18-alsa` installs a hook used by the main cx18 driver to create ALSA devices. Unloading clears the hook after walking devices and calling `snd_card_free()` on existing cards.

State/persistence: `struct snd_cx18_card` is attached to both `snd_card->private_data` and `cx->alsa`. It stores the V4L2 device pointer, ALSA card, PCM counters, substream pointer, and spinlock. No persistent storage.

Dependencies/integration: Depends on cx18 core symbols, V4L2 device embedding, ALSA core, cx18 versioning, and PCM implementation. Uses the existing cx18 PCM encoder stream rather than separate DMA ownership.

Risks: Module load ordering and global callback behavior are subtle. Exit uses `driver_find("cx18", &pci_bus_type)` and does not explicitly handle a missing driver pointer. Private cleanup must clear `cx->alsa` to avoid stale references. The code returns 0 for several error cases after logging, so load can appear successful even if an individual device skipped ALSA.

Test signals: Load `cx18-alsa` before/after `cx18`, ALSA card appears only when PCM stream exists, duplicate load prevention, module unload with devices present, and card name/longname correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-pcm.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-pcm.c

Purpose: Implements the ALSA PCM capture device for cx18, copying PCM packets announced by the cx18 core into ALSA runtime buffers and controlling the underlying cx18 PCM encoder stream.

Important APIs/functions: `snd_cx18_pcm_create()` creates one capture PCM and installs `snd_cx18_pcm_capture_ops`. `snd_cx18_pcm_capture_open()` locks cx18 serialization, claims the PCM stream, sets runtime hardware constraints, installs `cx->pcm_announce_callback`, marks streaming, and starts the V4L2 encode stream. `snd_cx18_pcm_capture_close()` stops the encode stream, clears streaming, releases the stream, and clears the callback. `cx18_alsa_announce_pcm_data()` copies incoming PCM bytes into the ALSA ring, updates hardware and period pointers, and signals period elapsed.

Control flow: ALSA open claims and starts the cx18 PCM stream. cx18 mailbox/stream code calls the announce callback as PCM packets arrive. The callback wraps writes at `runtime->buffer_size`, updates counters under ALSA stream lock, and triggers period notifications. Close stops and releases the cx18 stream.

State/persistence: `snd_cx18_card` tracks `hwptr_done_capture`, `capture_transfer_done`, and active capture substream. cx18 core holds the callback pointer while capture is open.

Dependencies/integration: Uses cx18 stream claiming/start/stop/release APIs, cx18 serialize lock through `snd_cx18_lock()`, ALSA PCM core, and vmalloc managed buffers.

Risks: In `snd_cx18_pcm_capture_open()`, if stream claim succeeds but an early streaming flag path returns 0, the local claim item is not obviously released in this function path; correctness depends on broader stream semantics. `snd_cx18_pcm_trigger()` accepts all commands and does nothing, so ALSA trigger semantics are minimal. Copying occurs before stream locking, similar to many simple drivers but worth race testing.

Test signals: ALSA capture at 48 kHz S16_LE stereo, period wraparound, open when stream already used by V4L2, callback clearing on close, repeated opens, and underrun/stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-pcm.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-pcm.h

Purpose: Declares cx18 ALSA PCM creation and PCM data announcement helpers.

Important APIs/types: `snd_cx18_pcm_create(struct snd_cx18_card *cxsc)` creates the ALSA PCM device. `cx18_alsa_announce_pcm_data(struct snd_cx18_card *card, u8 *pcm_data, size_t num_bytes)` is the callback used by cx18 core/mailbox paths to deliver PCM data to ALSA.

Control flow: ALSA main calls PCM creation during card init; cx18 core invokes the announcement callback while capture is active.

State/persistence: No header state; functions mutate `snd_cx18_card` runtime counters and ALSA runtime buffer state.

Dependencies/integration: Bridges cx18 ALSA module and core PCM packet delivery.

Risks: The callback declaration exposes a raw byte buffer and size; callers must pass complete S16 stereo frames matching ALSA runtime assumptions.

Test signals: Compile/link checks and PCM capture data delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa.h

Purpose: Defines cx18 ALSA private card state, debug macros, and lock helpers shared by cx18 ALSA main/PCM code.

Important APIs/types: `struct snd_cx18_card` stores the owning V4L2 device, ALSA card, capture period/hardware counters, active substream, and spinlock. `snd_cx18_lock()` and `snd_cx18_unlock()` reuse `cx->serialize_lock` so ALSA file operations serialize with V4L2 operations. Debug macros format logs using the cx18 V4L2 device name.

Control flow: ALSA PCM open/close use the lock helpers around stream claim/start/stop and callback changes. Pointer reads use `slock`.

State/persistence: Runtime-only ALSA state attached to `cx->alsa`. No persistent config.

Dependencies/integration: Depends on `to_cx18()` from cx18 core and ALSA card/substream types. Keeps ALSA stream manipulation consistent with cx18 file-operation serialization.

Risks: Debug macros reference a local `v4l2_dev` variable by name, so callers must have one in scope. The struct has limited locking; only pointer reads use `slock`, while other fields rely on ALSA/cx18 serialization.

Test signals: Compile coverage of macros in all call sites, lock ordering with V4L2 opens, and pointer/counter consistency during capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-audio.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-audio.c

Purpose: Selects cx18 board audio input routing across external muxes, audio control subdevices, and the internal CX23418 audio input mux.

Important APIs/functions: `cx18_audio_set_io()` chooses the current audio input from radio or selected video audio input, routes any external mux subdevice, calls the board's audio control hardware through `cx18_call_hw_err(... audio, s_routing ...)`, and programs `CX18_AUDIO_ENABLE` AI1 mux bits for serial1, serial2, or internal 843/I2S path.

Control flow: When input changes, the function selects the board audio descriptor, routes external devices, then updates the internal register. If the desired mux bits already match, it first toggles to an alternate mux value using `cx18_write_reg_expect()` to force hardware state, then writes the desired value.

State/persistence: Uses `cx->audio_input`, radio flag in `cx->i_flags`, card audio input descriptors, and hardware `CX18_AUDIO_ENABLE` register. No durable state.

Dependencies/integration: Depends on cx18 card tables, V4L2 subdevice audio routing, cx18 MMIO helpers, and constants from the cx18 AV decoder.

Risks: Routing is board-table dependent; wrong `audio_input`/`muxer_input` values produce silence or wrong source. The forced toggle is hardware-specific and must preserve unrelated register bits through masks.

Test signals: TV/radio/line-in audio switching, serial audio source selection, external mux calls, register write-expect success, and no-audio regressions across card variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-audio.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-audio.h

Purpose: Declares cx18 audio routing setup.

Important APIs/types: `cx18_audio_set_io(struct cx18 *cx)` selects and programs the current board audio path.

Control flow: Called by cx18 input/routing control paths when audio source selection must be applied.

State/persistence: No header state; implementation updates cx18 and subdevice hardware registers.

Dependencies/integration: Requires `struct cx18` from cx18 core.

Risks: Single API hides several hardware layers, so callers must ensure `cx->audio_input`, radio state, and board tables are valid first.

Test signals: Compile/link checks and audio switching paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-audio.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-audio.c

Purpose: Implements audio path, clock, and V4L2 audio control handling for the cx18 internal A/V decoder block.

Important APIs/functions: `set_audclk_freq()` programs PLL, sample-rate converter, MCLK, audio/video count registers for 32/44.1/48 kHz and for serial versus analog demod inputs. `cx18_av_audio_set_path()` stops the audio microcontroller, resets the audio path, mutes, selects serial or analog demod path, programs audio clock, deasserts reset, and restarts the microcontroller for tuner audio. `cx18_av_s_clock_freq()` changes clock frequency through reset/mute sequencing. Control helpers set volume, bass, treble, balance, and mute. `cx18_av_audio_ctrl_ops` exports the V4L2 control callback.

Control flow: Input routing in `cx18-av-core.c` updates `state->aud_input` and calls `cx18_av_audio_set_path()`. Audio clock changes validate the requested rate, temporarily stop/reset relevant blocks, program PLL/SRC values, and restart. V4L2 audio controls translate generic ranges into CXADEC register values.

State/persistence: `cx->av_state.aud_input` selects serial versus analog behavior; `audclk_freq` caches selected sample rate; control values live in V4L2 control state and hardware registers. Hardware register settings persist until reconfigured/reset.

Dependencies/integration: Uses cx18 AV register helpers from `cx18-av-core.c`, V4L2 control framework, and `cx18_av_state`. It cooperates with video standard/input changes because analog audio autodetection depends on the microcontroller and selected standard.

Risks: PLL/SRC values are hard-coded magic constants and comments document sync sensitivity. Mute handling differs for analog and serial audio because the microcontroller can overwrite mute registers. Unsupported rates return `-EINVAL`. Register sequencing is important to avoid audible artifacts.

Test signals: 32/44.1/48 kHz clock changes, tuner versus line/serial audio, mute/unmute, volume/bass/treble/balance controls, audio/video sync, and absence of pops during path changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-core.c

Purpose: Implements the cx18 internal A/V decoder V4L2 subdevice: register access helpers, firmware/initialization, video standard setup, input routing, tuner/audio status, video controls, scaling, stream enable, log-status, debug register access, and subdevice registration.

Important APIs/functions: Register helpers `cx18_av_read/write`, `write_expect`, 32-bit variants, and `and_or` operate on the CXADEC register window. `cx18_av_initialize()` loads firmware, stops the 8051, initializes PLLs/DLLs/AFE/output/VBI/default controls, and sets up default volume. `cx18_av_std_setup()` computes timing, blanking, filters, burst gate, chroma subcarrier, and VBI line offsets for 525/625-line and PAL/NTSC/SECAM variants. `set_input()` validates composite/S-video/component/audio input encodings, configures AFE mux/ADC/AFE registers, updates state, calls audio path setup, and restarts detection. V4L2 ops cover firmware load/reset, tuner get/set, standard/radio/frequency, audio/video routing, stream enable, pad format scaling, VBI operations, controls, and log-status. `cx18_av_probe()` initializes `cx18_av_state`, controls, subdev ops, and registers the subdevice.

Control flow: Probe initializes defaults and registers the subdevice, then does base PLL init. First `load_fw` or reset performs full firmware and decoder initialization. Standard or frequency changes recompute video timing and restart audio/video detection. Routing changes run through `set_input()`, which programs muxes and audio path together. Format set validates requested scaling against source active size and writes horizontal/vertical scaler registers. Stream enable toggles output registers.

State/persistence: `cx18_av_state` stores revision, selected video/audio input, audio clock, audio mode, radio flag, standard, VBI slicer offsets, initialization flag, controls, and subdevice object. Hardware registers persist while the decoder is configured.

Dependencies/integration: Depends on cx18 core IO helpers, card input enums/tables, firmware loader (`cx18_av_loadfw`), VBI helpers, audio helper ops from `cx18-av-audio.c`, and V4L2 subdev/control frameworks.

Risks: Large amounts of analog-video timing and register programming are magic-number based and standard-specific. Input encodings are bit-packed; invalid combinations must be rejected to avoid bad AFE programming. `cx18_av_set_fmt()` has strict scaling limits and returns `-ERANGE`. Initialization sequencing around firmware, sleep, DLLs, and AFE reset is hardware-sensitive. Control default volume clamps hardware values to avoid V4L2 range errors.

Test signals: Subdevice probe, firmware load once, reset, standard switching across NTSC/PAL/SECAM variants, composite/S-video/component/audio routing, tuner audio mode detection, V4L2 controls, scaling limits, stream enable/disable, VBI format ops, log-status output, and advanced debug register access when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-core.c -->
