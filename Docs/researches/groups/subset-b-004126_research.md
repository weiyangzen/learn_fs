# Research: subset-b-004126

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-video.c

Purpose: implements the V4L2 video, VBI-facing format negotiation, radio, controls, vb2 streaming, decoder setup, and interrupt completion logic for Philips/NXP SAA7134 analog TV cards. It translates user-facing V4L2 state into SAA7134 decoder/scaler/DMA register writes and exports shared handlers used by other saa7134 modules.

Important APIs, types, and functions: `formats[]` maps V4L2 fourcc values to SAA7134 output mode bits, byte/word swap flags, and planar YUV layout. `tvnorms[]` maps video standards to decoder timing and crop defaults. `set_tvnorm()`, `video_mux()`, `saa7134_set_decoder()`, `set_size()`, and `saa7134_set_tvnorm_hw()` program input, timing, cropping, and scaler registers. The vb2 path is `queue_setup()`, `buffer_init()`, `buffer_prepare()`, `saa7134_vb2_buffer_queue()`, `saa7134_vb2_start_streaming()`, `saa7134_vb2_stop_streaming()`, and `buffer_activate()`. V4L2 ioctl handlers cover format, input, standard, tuner, frequency, crop/selection, register debug, and radio RDS reads. Exported handlers include `saa7134_querycap()`, `saa7134_s_std()`, `saa7134_s_input()`, `saa7134_g_tuner()`, and streaming helpers.

Control flow: initialization in `saa7134_video_init1()` creates controls, initializes DMA queues and vb2 queues, sets the default BGR24 720x576 interlaced format, and allocates page tables. `saa7134_video_init2()` applies the default norm/input and audio mute/volume. Open switches the hardware into radio or video input mode. Format setting validates against current crop and field mode, then records `dev->fmt`, `width`, `height`, and `field`. Streaming validates dimensions, optionally enables media-controller tuner links, builds a scatter-gather page table, and `buffer_activate()` programs scaler and DMA channel registers. IRQ completion waits for the required field(s), finishes the current buffer, and starts the next queued buffer.

State and persistence: runtime state lives in `struct saa7134_dev`: current norm, input, crop rectangles, controls, vb2 queues, DMA queue state, and automute/nosignal flags. No persistent storage is written; module parameters (`video_debug`, `gbuffers`, `noninterlaced`, `secam`) shape runtime behavior until module unload. Control values are mirrored in `dev->ctl_*` and in hardware registers.

Dependencies and integration points: relies on `saa7134.h`, `saa7134-reg.h`, videobuf2 DMA-SG, V4L2 controls/ioctls/events, media controller links, tuner/audio subdevices through `saa_call_all()`, empress MPEG support, VBI queue ops, and common saa7134 page-table/buffer helpers. It also coordinates with TS capture by rejecting planar video streaming when empress TS use would collide on DMA resources.

Risks: DMA requires page-aligned USERPTR buffers and uses page-table programming that is sensitive to scatterlist offsets. Crop arithmetic and scaler limits can reject or clamp unexpected sizes. Planar formats share hardware resources with MPEG paths. Automute depends on signal-change IRQ status bits and may mute audio on marginal signals. `saa7134_querystd()` intersects the caller-provided mask with detected standard, so callers must initialize `*std` correctly.

Test signals: build with relevant saa7134 options; probe a supported board; verify `/dev/video*`, `/dev/vbi*`, and radio node registration; run `v4l2-ctl --all`, enumerate formats/inputs, set standards and crop rectangles, stream MMAP/DMABUF/read for packed and planar formats, test VBI capture, radio RDS read/poll, tuner frequency changes, and signal-loss automute. Watch dmesg for buffer timeout, page alignment, DMA collision, and media-link errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134.h

Purpose: central private header for the SAA7134 driver family. It defines board IDs, media/input/audio/video data structures, device state, DMA queues, helper macros, conditional DVB/IR/media-controller state, and cross-file prototypes used by core, video, VBI, TS, audio, input, and board modules.

Important APIs, types, and functions: key types are `struct saa7134_dev`, `struct saa7134_board`, `struct saa7134_input`, `struct saa7134_tvnorm`, `struct saa7134_format`, `struct saa7134_buf`, `struct saa7134_dmaqueue`, `struct saa7134_pgtable`, `struct saa7134_dmasound`, `struct saa7134_ts`, and `struct saa7134_mpeg_ops`. Macros like `card(dev)`, `card_in(dev,n)`, `card_is_empress()`, `saa_readb()`, `saa_writeb()`, and `saa_call_all()` form the local API. It declares exported video handlers, VBI/TS queue operations, audio control functions, i2c registration, page-table helpers, buffer lifecycle helpers, and optional RC/DVB hooks.

Control flow: this header has no executable flow, but it defines the structure used by probe/init/fini paths. `struct saa7134_dev` is the shared state object passed between all modules. Core code fills PCI, MMIO, board, i2c, and media state; video/VBI/TS modules attach queue state and video devices; audio/input modules add tvaudio, OSS/ALSA, and remote-control behavior; MPEG ops allow empress/DVB/go7007 modules to plug into signal-change and TS interrupts.

State and persistence: all persistent-in-memory driver state is organized here. Board descriptors provide static configuration for input routing, tuner addresses, MPEG mode, video output, and GPIO masks. Device state includes locks, resources, video devices, vb2 queues, page tables, controls, crop rectangles, tvaudio scan thread, IRQ-related flags, suspend state, media entities, DVB frontends, and gate-control callbacks. Nothing is persisted across unloads except hardware-side side effects.

Dependencies and integration points: includes Linux PCI/I2C/video/input/mutex/PM QoS headers, V4L2 core/control/fh/device APIs, tuner and RC core, videobuf2 DMA-SG, ALSA PCM/core, optional DVB vb2 support, and local tuner config. It exports the contract that lets separate `.c` files share register access, subdevice calls, and module hooks.

Risks: because register access macros assume a local `dev` variable, misuse in a different scope can silently target the wrong object or fail compilation. The long board-ID enum is ABI-like inside the driver: card module parameters and board tables must remain consistent. Many fields are shared across IRQ, worker, ioctl, and streaming contexts, so lock ownership must follow established usage. Optional compile-time branches alter structure contents and call availability.

Test signals: successful allmodconfig-style builds across combinations of `CONFIG_VIDEO_SAA7134_DVB`, `CONFIG_VIDEO_SAA7134_RC`, and `CONFIG_MEDIA_CONTROLLER`; no missing prototypes; probe of analog-only, radio, empress, and DVB variants; no lockdep splats during open/stream/close; and correct board selection with `card=<n>`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/Kconfig

Purpose: declares the selectable SAA7146-based board drivers for Hexium Gemini, Hexium Orion/HV-PCI6, and Siemens-Nixdorf MXB in the kernel media PCI configuration menu.

Important APIs, types, and functions: this is Kconfig metadata rather than C code. `VIDEO_HEXIUM_GEMINI`, `VIDEO_HEXIUM_ORION`, and `VIDEO_MXB` are tristate symbols. All depend on `PCI`, `VIDEO_DEV`, and `I2C`, and all select `VIDEO_SAA7146_VV`. MXB additionally selects tuner and board-specific I2C subdrivers (`VIDEO_TUNER`, `VIDEO_SAA711X`, `VIDEO_TDA9840`, `VIDEO_TEA6415C`, `VIDEO_TEA6420`) when media subdriver autoselection is enabled.

Control flow: configuration choice controls which object files the adjacent Makefile builds and which runtime module can register a `saa7146_extension`. There is no runtime flow here.

State and persistence: Kconfig selections persist in the kernel `.config`; no runtime state is stored. The tristate value determines built-in, module, or excluded behavior.

Dependencies and integration points: integrates with the media subsystem Kconfig tree and the shared `VIDEO_SAA7146_VV` core. The select statements are important because the C drivers call V4L2/SAA7146 helper APIs and, for MXB, instantiate specific I2C subdevices by name.

Risks: underselecting a dependency can produce link failures or runtime missing-subdevice behavior. Overselecting legacy drivers can increase build surface. MXB uses conditional subdriver autoselect, so manual configurations must still include the needed subdevice modules.

Test signals: `make menuconfig` visibility, `make olddefconfig` dependency resolution, module builds for `hexium_gemini`, `hexium_orion`, and `mxb`, and modprobe behavior with the expected helper modules available.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/Makefile

Purpose: maps SAA7146 Kconfig symbols to the board-driver objects and adds the media I2C include path needed by local board sources.

Important APIs, types, and functions: `obj-$(CONFIG_VIDEO_MXB) += mxb.o`, `obj-$(CONFIG_VIDEO_HEXIUM_ORION) += hexium_orion.o`, and `obj-$(CONFIG_VIDEO_HEXIUM_GEMINI) += hexium_gemini.o` are the build rules. `ccflags-y += -I$(srctree)/drivers/media/i2c` lets `mxb.c` include local headers such as `tea6415c.h` and `tea6420.h`.

Control flow: build-system only. Enabled symbols cause Kbuild to compile and link the corresponding module or built-in object.

State and persistence: no runtime state. The built artifacts persist in the build tree.

Dependencies and integration points: relies on the Kconfig symbols and on headers from `drivers/media/i2c`. The resulting object modules register with the SAA7146 extension framework at module init.

Risks: removing the include path breaks MXB compilation. Incorrect object mapping would silently omit a selected driver. Since each source is a single-object module, link errors surface directly in that object.

Test signals: `make M=drivers/media/pci/saa7146` with each symbol as `m` or `y`; verify generated modules are named `mxb`, `hexium_orion`, and `hexium_gemini`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/hexium_gemini.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/hexium_gemini.c

Purpose: V4L2/SAA7146 extension driver for Hexium Gemini frame grabber cards. It registers a PCI extension, configures SAA7146 port/DMA defaults, initializes a Samsung KS0127B decoder over I2C, exposes nine analog camera inputs, and delegates capture mechanics to `saa7146_vv`.

Important APIs, types, and functions: `struct hexium` stores the video device, I2C adapter, current input, current standard, and type. `hexium_ks0127b[]` is the decoder power-on register table. `hexium_pal`, `hexium_ntsc`, `hexium_secam`, and `hexium_input_select[]` encode standard/input writes. `hexium_init_done()`, `hexium_set_input()`, and `hexium_set_standard()` perform I2C programming. V4L2 entry points are `vidioc_enum_input()`, `vidioc_g_input()`, and `vidioc_s_input()`. Module flow uses `hexium_attach()`, `hexium_detach()`, `std_callback()`, `saa7146_register_extension()`, and `saa7146_unregister_extension()`.

Control flow: module init registers `hexium_extension`. On matching PCI subsystem IDs, attach allocates state, enables SAA7146 I2C pins, registers an I2C adapter, configures GPIO and DD1 stream registers, initializes the decoder table, sets PAL/input 0, initializes `saa7146_vv`, installs custom input ioctls into `vv_data.vid_ops`, and registers a video node. Standard changes from the shared vv layer call `std_callback()` to push KS0127B standard registers.

State and persistence: `cur_input` and `cur_std` are in-memory only. Decoder registers and SAA7146 registers retain hardware state until changed or reset. `hexium_num` tracks active devices for logging. No persistent storage is used.

Dependencies and integration points: depends on `saa7146_vv`, SAA7146 I2C helpers, Linux I2C SMBus transfer APIs, PCI matching, and V4L2 video-device registration. The `vv_data` structure links this board driver to common capture and standard handling.

Risks: I2C programming errors are often logged but not always fatal, so bad decoder state can lead to capture timeouts. Gemini Dual is explicitly not fully supported. `hexium_set_input()` assumes validated input indexes. Global `vv_data` is modified during attach, so this follows the legacy single-driver pattern rather than per-device immutable ops. Attach cleanup is mostly correct but depends on each failure path unwinding I2C/vv/device registration in order.

Test signals: build/load module, confirm PCI ID binding for subsystem `0x17c8:0x2401/0x2402`, enumerate nine inputs, switch each input while watching I2C errors, set PAL/NTSC/SECAM and validate frame geometry, stream from `/dev/video*`, and unload/reload while checking adapter and video-node cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/hexium_gemini.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/hexium_orion.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/hexium_orion.c

Purpose: V4L2/SAA7146 extension driver for Hexium HV-PCI6 and Orion frame grabber cards. It detects old and newer Orion variants, initializes a Philips SAA7110 decoder, exposes nine camera inputs, and registers a common SAA7146 video capture device.

Important APIs, types, and functions: `struct hexium` carries video device, I2C adapter, card type, and current input. `hexium_saa7110[]` is the default decoder register table. `hexium_input_select[]` holds eight-register routing sequences per input. `hexium_probe()` performs variant detection and I2C setup for old generic IDs and known subsystem IDs. `hexium_init_done()` writes the decoder defaults; `hexium_set_input()` applies input routing; the V4L2 handlers enumerate/get/set input. `hexium_attach()` initializes `saa7146_vv` and registers the video node; `hexium_detach()` unwinds it.

Control flow: module init registers the extension. Probe rejects SAA7146 revision 0, allocates state, enables I2C pins, configures DD1, registers an I2C adapter, toggles decoder/control GPIOs, then identifies the card from subsystem IDs or by probing an SAA7110 at I2C address `0x4e`. Attach assumes successful probe state in `dev->ext_priv`, initializes vv, installs input ioctl hooks, registers the video device, initializes decoder registers, and selects input 0.

State and persistence: current input and card type persist only while the driver is loaded. Hardware decoder routing and SAA7146 register writes are volatile. `hexium_num` is a module-global active-device counter.

Dependencies and integration points: integrates with SAA7146 extension registration, SAA7146 I2C adapter preparation, SMBus byte-data transfers, V4L2 input ioctls, PCI subsystem matching, and the shared `saa7146_vv` capture framework.

Risks: old-card detection binds generic `0x0000:0x0000` subsystem IDs after probing, which is inherently risky if hardware is misidentified. Attach does not fully release vv if `saa7146_register_device()` fails. `std_callback()` is a no-op, so standard-specific decoder changes are not applied beyond common vv timing. I2C errors during default initialization are logged but not fatal.

Test signals: probe known Orion subsystem IDs and old-card detection, verify rejection of revision 0 hardware, enumerate/switch all nine inputs, stream PAL/NTSC/SECAM through the common vv layer, monitor dmesg for SAA7110 write failures, and unload/reload while checking I2C adapter cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/hexium_orion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/mxb.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/mxb.c

Purpose: V4L2/SAA7146 extension driver for the Siemens-Nixdorf Multimedia eXtension Board. It coordinates SAA7146 video/VBI capture with multiple I2C subdevices for video decoding, tuner control, audio demodulation, and audio crosspoint routing.

Important APIs, types, and functions: `struct mxb` stores video/VBI devices, I2C adapter, subdev pointers, current input/audio/mute/frequency/mode. Static tables define four video inputs, six audio inputs, video-to-audio mapping, TEA6420 routing, SAA7146 port selections, and SAA7146 standards. `mxb_probe()` creates the I2C adapter and required subdevices. `mxb_init_done()` mutes audio, initializes tuner/video decoder/audio mode, optional SAA7740 sound module, and SAA7146 port registers. V4L2 handlers implement input, tuner, frequency, audio, querystd, and advanced register debug. `std_callback()` pushes standard changes to SAA7111A, tuner, and GPIO.

Control flow: module init registers an SAA7146 extension with I2C IRQ usage. Attach initializes `saa7146_vv`, probes all MXB I2C devices, installs video and VBI ioctl hooks, registers the video device, optionally registers VBI for nonzero SAA7146 revisions, logs the board, and runs board initialization. Input switching changes SAA7146 HPS source/sync, routes the TEA6415C crosspoint where needed, selects the SAA7111A input, updates allowed norms, and routes audio if unmuted. Frequency and tuner ioctls call into tuner/audio subdevices.

State and persistence: current input, audio source, mute state, tuner mode, and clamped frequency are kept in `struct mxb`. Module parameter `freq` supplies initial tuning. Hardware state persists only in volatile SAA7146 and I2C subdevice registers. `mxb_num` counts attached boards.

Dependencies and integration points: depends on `saa7146_vv`, `tuner`, `saa7111`, `tda9840`, `tea6415c`, `tea6420`, V4L2 subdev calls, I2C transfer APIs, and SAA7146 device registration. The Kconfig autoselects the needed media I2C drivers when enabled.

Risks: all required subdevices must be present or probe aborts. The optional SAA7740 initialization disables fast I2C IRQ mode globally in `extension.flags`, which affects later behavior. Error unwinding in attach can leak probe-created I2C state on some registration failures. Audio routing tables are index-sensitive. VBI availability depends on SAA7146 revision. Advanced register debug can directly alter device registers.

Test signals: load with helper subdrivers present; confirm video and, on revision >0, VBI node registration; enumerate four inputs and six audio sources; switch each video/audio input and verify crosspoint routing; tune frequency and read back clamped value; set PAL-BG/PAL-I/NTSC/SECAM; stream video and VBI; test mute control; inspect dmesg for missing I2C devices and SAA7740 detection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/mxb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/Kconfig

Purpose: declares the `VIDEO_SAA7164` driver option for NXP SAA7164 PCIe bridge TV cards.

Important APIs, types, and functions: `VIDEO_SAA7164` is a tristate symbol. It depends on `DVB_CORE`, `VIDEO_DEV`, `PCI`, and `I2C`; selects `I2C_ALGOBIT`, `FW_LOADER`, `VIDEO_TUNER`, `VIDEO_TVEEPROM`, and optional tuner/demod frontends (`DVB_TDA10048`, `DVB_S5H1411`, `MEDIA_TUNER_TDA18271`) under `MEDIA_SUBDRV_AUTOSELECT`.

Control flow: build configuration controls whether the monolithic `saa7164` module/built-in is compiled. Runtime firmware loading and board support are in the C files.

State and persistence: Kconfig state persists in `.config`; no runtime state.

Dependencies and integration points: couples the PCI bridge driver to DVB, V4L2, I2C, firmware loader, tveeprom, and frontend/tuner drivers used by supported Hauppauge boards.

Risks: missing firmware loader or frontend selections can produce a driver that builds but cannot initialize real hardware completely. Optional autoselect only helps when enabled; custom minimal configs need manual frontend coverage.

Test signals: `make olddefconfig` and module build with `CONFIG_VIDEO_SAA7164=m`; verify expected helper modules and firmware loader support are present.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/Makefile

Purpose: builds the SAA7164 driver as a single composite object from card, core, I2C, DVB, firmware, bus, command, API, buffer, encoder, and VBI implementation files.

Important APIs, types, and functions: `saa7164-objs` lists all linked objects: `saa7164-cards.o`, `saa7164-core.o`, `saa7164-i2c.o`, `saa7164-dvb.o`, `saa7164-fw.o`, `saa7164-bus.o`, `saa7164-cmd.o`, `saa7164-api.o`, `saa7164-buffer.o`, `saa7164-encoder.o`, and `saa7164-vbi.o`. `obj-$(CONFIG_VIDEO_SAA7164) += saa7164.o` gates the module. Include flags expose tuner and DVB frontend headers.

Control flow: Kbuild compiles listed objects and links them into `saa7164.ko` or built-in code depending on the Kconfig symbol.

State and persistence: no runtime state; only build products.

Dependencies and integration points: include paths are required for tuner/frontend integration used by the DVB and board setup code. The object list defines which implementation files participate in the single module namespace.

Risks: omitting an object produces missing symbols or disabled functionality; stale include paths break builds when frontend headers move. Since all objects link into one module, global variables and symbols share a namespace.

Test signals: `make M=drivers/media/pci/saa7164`; inspect `saa7164.ko` symbol resolution; test both module and built-in configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-api.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-api.c

Purpose: high-level firmware API layer for the SAA7164 bridge. It wraps `saa7164_cmd_send()` requests for firmware status/debug, encoder configuration, audio/video controls, DIF setup, descriptor enumeration, virtual I2C register access, GPIO manipulation, EEPROM reads, and per-port hardware descriptor caching.

Important APIs, types, and functions: public functions include `saa7164_api_get_load_info()`, `saa7164_api_collect_debug()`, `saa7164_api_set_debug()`, `saa7164_api_set_vbi_format()`, `saa7164_api_set_encoder()`, `saa7164_api_get_encoder()`, `saa7164_api_set_aspect_ratio()`, `saa7164_api_set_usercontrol()`, `saa7164_api_get_usercontrol()`, `saa7164_api_set_videomux()`, `saa7164_api_audio_mute()`, `saa7164_api_set_audio_volume()`, `saa7164_api_set_audio_std()`, `saa7164_api_set_audio_detection()`, `saa7164_api_configure_dif()`, `saa7164_api_initialize_dif()`, `saa7164_api_transition_port()`, `saa7164_api_get_fw_version()`, `saa7164_api_read_eeprom()`, `saa7164_api_enum_subdevs()`, `saa7164_api_i2c_read()`, `saa7164_api_i2c_write()`, and GPIO bit helpers. Descriptor parsing uses many `tmComRes*DescrHeader` structs to fill `struct saa7164_port`.

Control flow: most APIs build a typed request, send it to a firmware unit/control selector, then log or cache the result. Encoder setup selects profile, bitrates, aspect ratio, and GOP size. Video mux changes mute, video selector, audio selector, then unmutes. Descriptor enumeration first gets descriptor length, allocates a buffer, fetches descriptors, and walks variable-length descriptor headers to assign TS/encoder/VBI ports, DMA BAR offsets, processing units, tuner units, audio feature units, encoder units, and IF units. Virtual I2C translates Linux bus/address to firmware unit IDs and uses `EXU_REGISTER_ACCESS_CONTROL`.

State and persistence: port configuration fields such as `hwcfg`, `bufcounter`, `pitch`, `bufsize`, `bufoffset`, `bufptr*`, `tunerunit`, `vidproc`, `audfeat`, `encunit`, `ifunit`, and encoder control cache are updated in memory. Firmware and hardware unit state is changed until reset/reconfiguration. EEPROM reads are transient.

Dependencies and integration points: depends on command transport (`saa7164_cmd_send()`), board unit mapping helpers, port arrays, V4L2 MPEG controls and standards, firmware descriptor ABI, I2C emulation, and GPIO reset flows in card setup.

Risks: descriptor walking trusts firmware-provided `len` fields enough that malformed descriptors can confuse parsing. Several APIs log command failures but continue, so partial configuration is possible. `saa7164_api_set_videomux()` indexes a fixed audio input array with `mux_input - 1`, requiring validated mux values. `saa7164_api_set_aspect_ratio()` calls `BUG()` on an unexpected control. Virtual I2C uses fixed 256-byte buffers and validates only some lengths. `saa7164_api_initialize_dif()` appears to leave `ret` unchanged for encoder ports because it sets `std` without assigning `p`, making success semantics worth checking against callers.

Test signals: firmware load followed by descriptor enumeration; compare parsed port BAR offsets with streaming register behavior; exercise V4L2 MPEG controls, mux switching, audio mute/volume/std, DIF configuration for NTSC/PAL/SECAM and DVB; run virtual I2C reads/writes through tuner and demod drivers; read EEPROM; inspect firmware debug collection; inject command failures/timeouts if possible.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-buffer.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-buffer.c

Purpose: allocates, formats, activates, and frees firmware/DMA buffers for SAA7164 streaming ports, plus small user-space staging buffers.

Important APIs, types, and functions: `saa7164_buffer_alloc()` allocates a `struct saa7164_buffer`, coherent DMA data memory, and coherent page-table memory. `saa7164_buffer_dealloc()` frees those resources. `saa7164_buffer_zero_offsets()` clears a hardware write offset. `saa7164_buffer_activate()` assigns a buffer to a hardware buffer slot by writing offset and page-table pointers into BAR registers. `saa7164_buffer_cfg_port()` writes pitch/bufsize/counter registers and activates all buffers on a port queue. `saa7164_buffer_alloc_user()` and `saa7164_buffer_dealloc_user()` handle CPU-only buffers.

Control flow: allocation validates length alignment but then sizes DMA data from fixed `SAA7164_PT_ENTRIES` and streaming parameters. It initializes buffers to `0xff`, computes a CRC for debugging, and fills page-table entries with 4K offsets into the coherent data buffer. Port configuration writes shared stream registers, locks `port->dmaqueue_lock`, iterates free buffers, activates each into a hardware slot, and unlocks.

State and persistence: buffer objects track index, flags (`FREE`/`BUSY`), position, actual size, DMA addresses, page-table addresses, and CRC. Hardware BAR state stores the current buffer counter, pitch, buffer size, per-buffer offsets, and page-table pointers. State is volatile and tied to stream lifecycle.

Dependencies and integration points: depends on `struct saa7164_port` descriptor offsets filled by `saa7164-api.c`, DMA coherent allocation, list-based DMA queue state, and low-level `saa7164_writel/readl()` register access. Streaming code in encoder/VBI/DVB paths consumes these buffers.

Risks: `len` is validated but mostly ignored, so callers may assume a requested size that is not actually used. The page-table pointer writes use 32-bit high/low register names in a way marked TODO, so 64-bit DMA addressing is sensitive. `BUG_ON(i > port->hwcfg.buffercount)` should likely be `>=` because activation already rejects `i >= buffercount`; this can attempt one invalid activation before the BUG condition catches later. Freeing non-free buffers logs only a warning. Correct `params->numpagetables`, pitch, and line count are essential to avoid overruns.

Test signals: allocate/deallocate under probe/remove and stream start/stop; verify coherent DMA addresses written into BAR slots; stream TS/PS/VBI long enough to wrap through all buffers; run on systems with DMA addresses above 4GB if supported; enable buffer debug and check offsets advance; exercise failure paths by forcing allocation failures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-bus.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-bus.c

Purpose: implements the PCIe firmware message bus ring-buffer transport used by SAA7164 commands and responses.

Important APIs, types, and functions: `saa7164_bus_setup()` initializes `struct tmComResBusInfo` ring pointers and read/write-position register offsets from firmware descriptors. `saa7164_bus_dump()` logs state. `saa7164_bus_verify()` validates ring positions and intentionally `BUG()`s on corrupt state. `saa7164_bus_set()` writes a command/response header plus payload into the set ring. `saa7164_bus_get()` peeks or consumes a response from the get ring.

Control flow: setup maps command/response rings into `dev->bmmio` and calculates position-register offsets from `intfdesc.BARLocation`. Sending verifies inputs and max size, locks the bus, polls for free space with `mdelay(1)` until timeout, converts header fields to little endian, copies header/payload into the ring with wrap handling, updates write position, restores CPU-endian fields, unlocks, and verifies. Receiving locks the bus, checks empty state, reads a header with wrap handling, converts endian fields, optionally returns after peek, validates the expected header, reads payload with wrap handling, advances read position, unlocks, and verifies.

State and persistence: `dev->bus` holds ring base pointers, sizes, max request size, and register offsets. Hardware/firmware read and write positions persist in BAR registers while the device is running. No disk persistence.

Dependencies and integration points: used directly by `saa7164-cmd.c`. Depends on firmware-provided `busdesc` and `intfdesc`, MMIO accessors, `memcpy_toio/fromio`, and the shared device mutex discipline around `bus->lock`.

Risks: corruption invokes `BUG()`, crashing the kernel. Ring wrap math and free-space checks must match firmware exactly. `saa7164_bus_set()` mutates the caller's message header for endian conversion and restores it later; early exits before restore would be dangerous, though current conversion occurs after space wait. Polling with `mdelay()` can burn CPU during firmware stalls. `saa7164_bus_get()` validates consumed messages against caller expectations, so callers must pass the peeked header back unchanged.

Test signals: firmware command traffic during probe, descriptor enumeration, and streaming; bus debug dumps with sane read/write positions; forced split/wrap cases using large commands near ring end; timeout handling when firmware is unresponsive; no `Unexpected msg miss-match` or bus `BUG()` under concurrent command load.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-cards.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-cards.c

Purpose: board database and board-specific setup helpers for SAA7164-based cards, primarily Hauppauge HVR2200/HVR2250/HVR2255/HVR2205 variants.

Important APIs, types, and functions: `saa7164_boards[]` maps internal board IDs to names, chip revisions, port roles (`SAA7164_MPEG_DVB`, encoder, VBI), and firmware unit/I2C mappings for EEPROMs, tuners, analog demods, and digital demods. `saa7164_subids[]` maps PCI subsystem IDs to board IDs. `saa7164_card_list()` prints valid card choices. `saa7164_gpio_setup()` resets demodulators using firmware GPIO controls. `hauppauge_eeprom()` decodes Hauppauge EEPROM data via `tveeprom_hauppauge_analog()`. `saa7164_card_setup()` reads EEPROM and applies board-specific decode. `saa7164_i2caddr_to_unitid()`, `saa7164_i2caddr_to_reglen()`, and `saa7164_unitid_name()` translate virtual I2C addresses and unit IDs.

Control flow: core probe selects a board from subsystem IDs or module parameters, then uses this file's tables for chip revision, port creation, firmware unit mapping, and I2C emulation. GPIO setup resets attached demods by clearing then setting bridge GPIO bits. Card setup reads EEPROM from bus 0 when available and logs known/unknown Hauppauge models. Virtual I2C calls scan the selected board's `unit[]` array for address and register-width translation.

State and persistence: board tables are static read-mostly data. Runtime state affected here includes selected `dev->board`, EEPROM buffer contents during setup, GPIO line state, and firmware I2C unit translation. EEPROM contents are read but not written.

Dependencies and integration points: integrates with `saa7164-api.c` for EEPROM and GPIO firmware commands, `tveeprom`, tuner/frontend drivers through virtual I2C address mapping, PCI subsystem matching, and core port setup.

Risks: incorrect unit IDs or register lengths break all virtual I2C access for that chip. Static EEPROM assumptions still hardcode bus 0/address `0xa0` in the API. Unknown models only warn, so unsupported board variants may proceed with a close-but-wrong profile. GPIO reset unit ID is a TODO constant (`PCIEBRIDGE_UNITID 2`). Duplicate board names with different revisions make logs less specific.

Test signals: autodetect each listed subsystem ID; compare selected board/chiprev/ports to hardware; read EEPROM and verify logged Hauppauge model; attach tuner and demod drivers on all virtual buses; check GPIO reset with frontend probe success; run `card=<n>` override and verify `saa7164_card_list()` output for unknown IDs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-cards.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-cmd.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-cmd.c

Purpose: command/response orchestration layer for SAA7164 firmware messages. It allocates command sequence slots, splits large requests, waits for firmware responses, handles IRQ/deferred dequeue, validates responses, maps firmware error codes, and releases sequence state.

Important APIs, types, and functions: internal helpers include `saa7164_cmd_alloc_seqno()`, `saa7164_cmd_free_seqno()`, `saa7164_cmd_timeout_seqno()`, `saa7164_cmd_timeout_get()`, `saa7164_cmd_dequeue()`, `saa7164_cmd_set()`, and `saa7164_cmd_wait()`. Public functions are `saa7164_irq_dequeue()` for interrupt-side response signaling and `saa7164_cmd_send()` for synchronous firmware commands. It uses `dev->cmds[]` entries containing sequence number, lock, waitqueue, in-use, signalled, and timeout state.

Control flow: `saa7164_cmd_send()` validates parameters, allocates a sequence, fills a command header, sends it through `saa7164_cmd_set()` which chunks payloads by bus max request size, then loops waiting for responses. Wait uses `wait_event_timeout()` on the sequence waitqueue; IRQ/dequeue paths peek bus responses, mark `signalled`, and wake the waiter. The sender peeks the response, dequeues unrelated responses if necessary, handles firmware error flags by reading error data and mapping PVC error codes, validates id/command/control/size, consumes response payload into the caller buffer, and repeats until all split response bytes are received.

State and persistence: command slots in `dev->cmds[]` are transient synchronization state. Timeout flags persist until a slot is freed. Firmware responses are consumed from the bus ring. No persistent storage.

Dependencies and integration points: sits between all high-level API calls and `saa7164_bus_set/get()`. Depends on device locks, per-command locks, waitqueues, `waitsecs`, IRQ/work handling, PVC/SAA error code definitions, and bus ring semantics.

Risks: timeout paths can return without freeing sequence numbers in some branches, relying on timeout cleanup/dequeue behavior. Concurrent responses require careful dequeue; safety loop protects against endless wrong-event handling but can return busy. `buf + offset` arithmetic on `void *` relies on GNU C extension. Split command/response size validation must match firmware exactly. If IRQ dequeue misses a response, synchronous wait can time out even when data is on the bus.

Test signals: normal firmware commands during initialization; debug with concurrent API calls; large descriptor/I2C transfers that split across request sizes; injected wrong-sequence responses; firmware error responses mapped to expected SAA errors; command timeout recovery followed by successful later commands; no leaked in-use command slots after repeated failures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-cmd.c -->
