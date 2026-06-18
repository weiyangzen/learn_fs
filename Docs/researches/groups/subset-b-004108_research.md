# subset-b-004108 research

This grouped report covers the requested B2C2 FlexCop PCI DMA code and bt8xx media PCI driver support files. Each section preserves the original source path so the reconciliation lane can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/flexcop-dma.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/flexcop-dma.c

## Purpose
`flexcop-dma.c` provides the exported DMA buffer lifecycle and DMA register programming helpers for B2C2 FlexCopII/FlexCopIII PCI digital TV devices. It allocates one coherent DMA area and exposes it to the hardware as two equal sub-buffers so the PCI ISR can alternate or stream through halves.

## Important APIs, Types, and Functions
The public API is `flexcop_dma_allocate()`, `flexcop_dma_free()`, `flexcop_dma_config()`, `flexcop_dma_xfer_control()`, `flexcop_dma_control_timer_irq()`, and `flexcop_dma_config_timer()`, all exported except the internal `flexcop_dma_remap()`. The functions operate on `struct flexcop_dma`, `struct flexcop_device`, `struct pci_dev`, `flexcop_dma_index_t`, `flexcop_dma_addr_index_t`, `flexcop_ibi_value`, and `flexcop_ibi_register`.

## Control Flow
Allocation rejects odd byte sizes, allocates coherent memory with `dma_alloc_coherent()`, and splits it into `cpu_addr0`/`dma_addr0` and `cpu_addr1`/`dma_addr1`. Configuration writes the shifted DMA base addresses and transfer size into either the DMA1 or DMA2 register block. Transfer control selects DMA1 or DMA2, reads the current start registers, toggles sub-address 0 and/or 1 start bits, and writes the values back. Timer setup disables remap, writes the DMA timer cycle count, and timer IRQ control toggles DMA1/DMA2 timer enable bits in `ctrl_208`.

## State and Persistence
Software state is the coherent buffer metadata stored in `struct flexcop_dma`. Hardware state is volatile FlexCop IBI register contents for DMA base, size, remap, start, and timer bits. There is no persistence across remove, suspend, or process lifetime.

## Dependencies and Integration Points
The file depends on PCI DMA APIs and the FlexCop bus abstraction supplied by `flexcop.h`: `read_ibi_reg()`, `write_ibi_reg()`, register names such as `dma1_000`, `dma2_010`, and logging macros. `flexcop-pci.c` calls these helpers during probe, stream start/stop, and IRQ-driven demux feeding.

## Risks and Edge Cases
The code assumes the hardware DMA address fields are word-addressed and stores addresses shifted right by two; non-word-aligned DMA addresses would be invalid for the device. `flexcop_dma_config()` and `flexcop_dma_xfer_control()` reject combined DMA1/DMA2 requests, while timer IRQ control accepts a mask. `flexcop_dma_free()` assumes a successfully initialized `pdev` and buffer metadata. Size must be even, and DMA1 sizes used by the PCI path must also be compatible with 188-byte MPEG-TS packet framing.

## Test Signals
Useful signals are successful coherent allocation/free, correct DMA1/DMA2 register writes, no transfer on invalid DMA masks, timer IRQ enable/disable visibility in `ctrl_208`, stream delivery from both sub-buffers, and clean device removal without DMA API warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/flexcop-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/flexcop-pci.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/flexcop-pci.c

## Purpose
`flexcop-pci.c` is the PCI bus driver for B2C2 FlexCop digital TV devices. It maps the PCI register window, wires the generic FlexCop core to PCI register accessors, allocates DMA buffers, services DMA/timer interrupts, and feeds MPEG transport stream data into the DVB demux.

## Important APIs, Types, and Functions
`struct flexcop_pci` stores the PCI device, init-state flags, MMIO mapping, two DMA descriptors, active DMA page, streaming counters, IRQ lock, delayed watchdog work, and the owning `struct flexcop_device`. Core functions include `flexcop_pci_read_ibi_reg()`, `flexcop_pci_write_ibi_reg()`, `flexcop_pci_isr()`, `flexcop_pci_stream_control()`, `flexcop_pci_dma_init()`, `flexcop_pci_dma_exit()`, `flexcop_pci_init()`, `flexcop_pci_exit()`, `flexcop_pci_probe()`, and `flexcop_pci_remove()`.

## Control Flow
Probe allocates a FlexCop core object with bus-private storage, installs PCI register and bus callbacks, applies module parameters for PID filtering and debug, enables the PCI device, maps BAR0, requests the shared IRQ, initializes the FlexCop core, allocates DMA1 and DMA2 buffers, routes SRAM destinations to those DMAs, and optionally schedules the IRQ watchdog. Stream start configures both DMA engines, configures the DMA1 timer, starts both DMA1 subaddresses, resets the last cursor, and enables DMA1 timer IRQs. The ISR reads `irq_20c`, logs error bits, then either passes a completed DMA page on page-change IRQ or computes the current DMA cursor on timer IRQ and feeds newly written byte ranges, including wraparound handling. Stream stop disables timer IRQs and stops DMA1 transfers. Remove cancels watchdog work, frees DMA memory, shuts down the core, releases PCI resources, and frees the core object.

## State and Persistence
Runtime state lives in `struct flexcop_pci`: initialization flags gate cleanup, `active_dma1_addr` selects the next page-buffer half, `last_dma1_cur_pos` tracks streaming progress for timer mode, and watchdog counters detect stalled IRQs. Hardware state is PCI BAR MMIO and DMA engine registers. No state is persisted beyond the lifetime of the device.

## Dependencies and Integration Points
The driver integrates with PCI core via `module_pci_driver()`, the FlexCop common core via `flexcop_device_initialize()`/`exit()` and callback fields, the DVB demux via `flexcop_pass_dmx_packets()` and `flexcop_pass_dmx_data()`, FlexCop SRAM and PID filter helpers, Linux workqueues, shared IRQ handling, spinlocks, and the coherent DMA helpers from `flexcop-dma.c`.

## Risks and Edge Cases
The ISR returns `IRQ_NONE` when no DMA status bits are set, which matters because the IRQ is shared. The timer IRQ path drops out if the hardware cursor reports a position beyond the allocated ring. Watchdog recovery resets PID filters while holding the demux lock, so feed-list integrity and lock ordering are important. DMA2 is allocated and routed for CA data but normal stream start only actively transfers DMA1. Cleanup relies on `init_state` to avoid double-free paths after partial probe failure.

## Test Signals
Validate PCI probe/remove, BAR mapping, shared IRQ registration, DMA allocation failure unwinding, transport stream delivery with PID filtering enabled and disabled, timer wraparound data feeding, watchdog PID-filter reset after stalled interrupts, and absence of DMA/IRQ use after remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/flexcop-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/Kconfig

## Purpose
This Kconfig file exposes the analog `bttv` driver and the DVB/ATSC `bt878` support under the bt8xx PCI media driver family. It encodes the core build-time dependencies and optional subdevice selections needed for Brooktree/Conexant Bt848/Bt878 cards.

## Important APIs, Types, and Functions
There are no C APIs here. The important symbols are `VIDEO_BT848`, which builds the `bttv` module, and `DVB_BT8XX`, which builds DVB support for Bt878-based cards. `VIDEO_BT848` selects helpers such as `I2C_ALGOBIT`, `VIDEOBUF2_DMA_SG`, `VIDEO_TUNER`, `VIDEO_TVEEPROM`, radio support, and optional audio subdrivers. `DVB_BT8XX` depends on `VIDEO_BT848` and selects supported DVB frontends and simple tuner support when subdriver autoselect is enabled.

## Control Flow
The configuration dependency flow requires PCI, I2C, V4L2 video device support, RC core, and radio support before analog Bt848 support is visible. DVB support then layers on top of `VIDEO_BT848` and `DVB_CORE`, ensuring the base bt8xx capture/card infrastructure is present before the MPEG/DVB path is built.

## State and Persistence
Kconfig choices persist in the kernel configuration, not in runtime driver state. The symbols determine whether object files are compiled in, built as modules, or omitted.

## Dependencies and Integration Points
This file connects bt8xx drivers to the broader media stack, including V4L2, DVB core, I2C tuner/audio subdevices, RC input, videobuf2 DMA scatter-gather support, and radio adapters. The `DVB_BT8XX` entry mirrors the card list in `bttv-cards.c` and the device IDs in `bt878.c`.

## Risks and Edge Cases
Because `DVB_BT8XX` depends on `VIDEO_BT848`, disabling analog support also removes DVB support for these bridge chips. The `MEDIA_SUBDRV_AUTOSELECT` selections affect which frontend and audio modules are available automatically; minimal configs may require manual subdriver selection. `VIDEO_BT848` also depends on `MEDIA_RADIO_SUPPORT`, which can surprise users who only need capture boards.

## Test Signals
Check `oldconfig`/`menuconfig` visibility, module names (`bttv`, `bt878`, `dvb-bt8xx`, `dst`, `dst_ca`), selected frontend modules under `MEDIA_SUBDRV_AUTOSELECT`, and successful builds for built-in and modular combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/Makefile

## Purpose
The Makefile defines how the bt8xx media PCI drivers are assembled. It groups the many analog bttv implementation files into one `bttv.o` module and conditionally adds the DVB/ATSC-related bt878 modules.

## Important APIs, Types, and Functions
There are no runtime APIs. Important build variables are `bttv-objs`, `obj-$(CONFIG_VIDEO_BT848)`, `obj-$(CONFIG_DVB_BT8XX)`, and `ccflags-y`. `bttv-objs` pulls in driver, card, interface, RISC, VBI, I2C, GPIO, input, audio-hook, and shared RISC memory code.

## Control Flow
Kbuild links `bttv.o` when `CONFIG_VIDEO_BT848` is enabled. When `CONFIG_DVB_BT8XX` is enabled, it builds `bt878.o`, `dvb-bt8xx.o`, `dst.o`, and `dst_ca.o`. Additional include paths expose DVB frontend and tuner headers to these source files.

## State and Persistence
Build state is controlled by kernel configuration and Kbuild dependency tracking. No runtime state exists in this file.

## Dependencies and Integration Points
The file integrates the bt8xx directory with Linux media Kbuild, the DVB frontend include tree, and the media tuner include tree. It also ensures `btcx-risc.o` is linked into the analog bttv module where shared RISC memory helpers are used.

## Risks and Edge Cases
Adding code that uses DVB or tuner internals without matching include paths would break the build. Moving `btcx-risc.o` affects both compile and symbol availability for bttv internals. The DVB object list assumes `CONFIG_DVB_BT8XX` users need the DST support objects as part of the same family.

## Test Signals
Run targeted kernel builds for `CONFIG_VIDEO_BT848=m/y` and `CONFIG_DVB_BT8XX=m/y`, confirm `bttv.o` contains all listed objects, and check that frontend/tuner headers resolve without extra include path changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bt848.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bt848.h

## Purpose
`bt848.h` centralizes PCI IDs, MMIO register offsets, bit masks, input format values, interrupt flags, GPIO/DMA control bits, I2C bits, and Bt848 RISC instruction encodings used by the bttv and bt878 family.

## Important APIs, Types, and Functions
This header defines constants rather than functions. Key groups include PCI IDs for Bt848/Bt849/Fusion879/Bt878/Bt879, video decoder registers such as `BT848_IFORM`, crop/scale/color/control registers, interrupt registers and flags, GPIO/I2C/DMA registers, RISC command flags such as `BT848_RISC_WRITE`, `BT848_RISC_JUMP`, `BT848_RISC_SYNC`, and Bt878 function-specific PCI config bits `BT878_DEVCTRL`, `BT878_EN_TBFX`, and `BT878_EN_VSFX`.

## Control Flow
The header influences control flow indirectly by giving driver code stable names for register programming, interrupt decoding, RISC instruction generation, chipset workarounds, and GPIO/audio/input routing. Files such as `bttv-cards.c`, `bt878.c`, and RISC builders use these constants when writing MMIO or interpreting interrupt status.

## State and Persistence
There is no software state. The constants describe volatile device register state, including video format, scaler, color, GPIO, DMA, I2C, and interrupt state.

## Dependencies and Integration Points
The header integrates with Linux PCI IDs if they are not already defined by the platform headers, and with bt8xx driver source files that program MMIO through `btwrite()`/`btread()` wrappers. Its RISC command definitions must match the hardware engine used by both analog capture and audio/MPEG DMA paths.

## Risks and Edge Cases
Incorrect masks or register offsets can corrupt unrelated hardware state. Some constants overlap between Bt848 and Bt878 variants, so code must choose the correct function and register space. RISC command bit fields combine command, byte-enable, SOL/EOL, IRQ, and status bits; malformed combinations can stall DMA or trigger RISC errors.

## Test Signals
Compile-time usage is broad, so build coverage is essential. Runtime signals include correct video format selection, interrupt bit decoding, GPIO routing, I2C bit-bang behavior, RISC DMA execution, and chipset workaround bits being written only on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bt848.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bt878.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bt878.c

## Purpose
`bt878.c` implements the Bt878 audio/function-1 PCI driver used by bt8xx DVB/ATSC cards to DMA MPEG transport stream data. It allocates a ring buffer and RISC program, starts/stops the audio DMA engine, handles function-1 interrupts, and exposes GPIO/device-control hooks used by downstream DVB components such as DST.

## Important APIs, Types, and Functions
Global exported state is `bt878_num` and `bt878[BT878_MAX]`. Exported functions are `bt878_start()`, `bt878_stop()`, and `bt878_device_control()`. Important internal functions are `bt878_mem_alloc()`, `bt878_mem_free()`, `bt878_make_risc()`, `bt878_risc_program()`, `bt878_irq()`, `bt878_probe()`, `bt878_remove()`, `bt878_init_module()`, and `bt878_cleanup_module()`.

## Control Flow
Module init registers a PCI driver for supported Bt878 function-1 subsystem IDs. Probe bounds the number of devices, enables PCI, reserves and maps BAR0, clears interrupts, requests a shared IRQ, enables bus mastering, stores the device in the static array, allocates a 128 KiB coherent data buffer plus one page for RISC instructions, computes legal line/block sizes, clears the interrupt mask, and increments `bt878_num`. `bt878_start()` writes a circular RISC program, sets packet control bits, installs the RISC start address, enables selected interrupt bits, and enables FIFO/RISC/capture in `BT878_AGPIO_DMA_CTL`. The IRQ handler loops while masked interrupt status exists, ACKs status, logs error classes, records the finished block on `ARISCI`, and queues bottom-half work if a consumer installed it. Remove disables DMA and interrupts, clears status, disables bus mastering, frees IRQ/mapping/resources, marks shutdown, and frees coherent memory.

## State and Persistence
State is per `struct bt878`: PCI identity, MMIO mapping, DMA buffer addresses and sizes, RISC program addresses and write position, block accounting, finished/last block markers, optional bottom-half work, GPIO mutex, and shutdown flag. Runtime state is volatile and reset on module unload or device removal.

## Dependencies and Integration Points
The file depends on PCI, coherent DMA, IRQ sharing, workqueues, bt8xx register definitions from `bt878.h`/`bt848.h`, `bttv_gpio_*()` helpers for function-0 GPIO control, and DST private command definitions. DVB bridge code consumes the exported device array and start/stop routines.

## Risks and Edge Cases
The static `bt878[BT878_MAX]` registry allows only four devices. `bt878_num` is incremented on probe but not compacted on remove, so hotplug churn can exhaust slots. RISC memory is one page, so `bt878_make_risc()` must keep line count and instruction count bounded. The IRQ loop disables the interrupt mask after more than 20 iterations to break lockups. The code disables work if no bottom-half function is installed, and later users must initialize `bh_work` before expecting queued processing.

## Test Signals
Validate probe/remove for all PCI IDs, DMA allocation failure paths, RISC program wraparound, start/stop register programming, ARISCI block notifications, error interrupt logging, GPIO control commands for DST, IRQ sharing with function 0, and multi-card behavior up to `BT878_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bt878.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bt878.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bt878.h

## Purpose
`bt878.h` declares the Bt878 audio/function-1 register interface and the shared `struct bt878` state used by the DVB bt8xx driver path. It also defines card IDs that bridge `bttv-cards.c`, `bt878.c`, and DVB frontend attachment code.

## Important APIs, Types, and Functions
Important definitions include `BT878_AINT_STAT`, `BT878_AINT_MASK`, audio interrupt bits, `BT878_AGPIO_DMA_CTL`, audio packet and RISC registers, `BT878_MAX`, and `BT878_RISC_SYNC_MASK`. `struct bt878` contains GPIO locking, device numbering, linked bttv number, I2C adapter, PCI/MMIO identity, DMA and RISC memory, packet/block accounting, work item, and shutdown state. Externs expose `bt878_num`, `bt878[]`, `bt878_start()`, and `bt878_stop()`.

## Control Flow
The header has no executable control flow, but it shapes the function-1 lifecycle: attach code locates a `struct bt878`, starts DMA through `bt878_start()`, reacts to block-completion state populated by the IRQ handler, and stops capture through `bt878_stop()`.

## State and Persistence
All state described by the header is runtime kernel memory or volatile hardware MMIO. There is no persistent state. `finished_block` and `last_block` are declared volatile to reflect interrupt and bottom-half interaction.

## Dependencies and Integration Points
The header includes Linux interrupt, PCI, scheduler, spinlock, mutex, and workqueue headers, plus local `bt848.h` and `bttv.h`. It is the contract between the Bt878 function-1 PCI driver, DVB bt8xx glue, and bttv GPIO/I2C infrastructure.

## Risks and Edge Cases
The global array design requires consistent indexing between probe order and users. `BT878_MAX` limits supported cards. The struct exposes raw MMIO and DMA fields, so consumers must not mutate ownership fields after probe. Register definitions are for the audio/function-1 BAR and should not be confused with function-0 video offsets even where names overlap.

## Test Signals
Build consumers against the header, verify exported symbols resolve, start/stop works through the declared API, and block state updates are visible to downstream DVB processing without races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bt878.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/btcx-risc.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/btcx-risc.c

## Purpose
`btcx-risc.c` provides a small shared allocator for coherent RISC instruction memory used by bt848/bt878/cx2388x style capture engines. In this subset, it is linked into `bttv.o` and supports RISC program buffers owned by higher-level capture code.

## Important APIs, Types, and Functions
The exported functions are `btcx_riscmem_alloc()` and `btcx_riscmem_free()`. They operate on `struct btcx_riscmem`, which stores CPU pointer, DMA address, size, and a jump pointer field used by RISC builders. The file also has a `btcx_debug` module parameter and internal allocation counter `memcnt` for debug logging.

## Control Flow
Allocation frees an existing buffer when it is too small for the requested size, allocates coherent DMA memory if no usable buffer exists, records CPU/DMA/size fields, increments `memcnt`, and returns zero. Free is a no-op for null buffers; otherwise it decrements `memcnt`, frees the coherent memory, and zeroes the descriptor.

## State and Persistence
The only module-level state is `memcnt`, used for debugging outstanding RISC memory allocations. Each caller owns its `struct btcx_riscmem`. Memory is coherent DMA memory and persists only until explicit free or device teardown.

## Dependencies and Integration Points
The file depends on PCI coherent DMA APIs, module parameters, and `btcx-risc.h`. Capture paths use the allocated buffers to store hardware RISC instructions that the bt8xx DMA engine fetches.

## Risks and Edge Cases
`btcx_riscmem_alloc()` reuses an existing buffer if it is large enough and does not shrink buffers. Callers must initialize descriptors to zero before first use and must serialize access if a RISC program can be rebuilt concurrently with hardware execution. Debug `memcnt` is not atomic, but allocation/free are expected in driver control paths rather than hot IRQ paths.

## Test Signals
Validate allocation, reuse, grow-and-free behavior, DMA API warnings, zeroed descriptors after free, no leaks in probe/remove cycles, and valid hardware fetches from generated RISC programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/btcx-risc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/btcx-risc.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/btcx-risc.h

## Purpose
`btcx-risc.h` declares the shared RISC DMA memory descriptor and allocator/free APIs for bt8xx/cx-style RISC engines.

## Important APIs, Types, and Functions
`struct btcx_riscmem` stores the allocated byte size, little-endian instruction CPU pointer, optional jump pointer, and DMA address. `struct btcx_skiplist` describes a start/end range for RISC generation helpers outside this file. The declared functions are `btcx_riscmem_alloc()` and `btcx_riscmem_free()`.

## Control Flow
The header has no executable control flow. It defines the contract used by source files that allocate coherent RISC instruction buffers before programming the capture engine.

## State and Persistence
The structs describe runtime DMA memory and generation metadata only. No persistent state is represented.

## Dependencies and Integration Points
Consumers must include Linux types that define `__le32`, `dma_addr_t`, and `struct pci_dev`. The header is included by `btcx-risc.c` and capture code that builds bt8xx RISC instruction lists.

## Risks and Edge Cases
The header does not enforce initialization; callers must zero descriptors before first allocation and avoid using stale `jmp` pointers after realloc/free. The CPU pointer is little-endian instruction memory, so writers must use appropriate endian conversion for hardware opcodes.

## Test Signals
Compile users with the header, allocate/free descriptors through the declared functions, and confirm generated RISC programs use DMA addresses and little-endian instruction stores consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/btcx-risc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-audio-hook.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-audio-hook.c

## Purpose
`bttv-audio-hook.c` contains board-specific GPIO audio routing and volume helpers split out of `bttv-cards.c`. These routines adapt V4L2 tuner audio modes to the analog muxes, stereo/SAP pins, mute pins, and volume chip wiring found on older Bt848/Bt878 cards.

## Important APIs, Types, and Functions
Exported-by-header functions include `winview_volume()`, `gvbctv3pci_audio()`, `gvbctv5pci_audio()`, `avermedia_tvphone_audio()`, `avermedia_tv_stereo_audio()`, `lt9415_audio()`, `terratv_audio()`, `winfast2000_audio()`, `pvbt878p9b_audio()`, `fv2000s_audio()`, `windvr_audio()`, and `adtvk503_audio()`. They operate on `struct bttv`, `struct v4l2_tuner`, and the bttv GPIO helpers/macros from `bttvp.h`.

## Control Flow
Most audio hooks support a query path when `set` is false, filling `audmode` and `rxsubchans` with the modes the board may expose. When `set` is true, they switch on `t->audmode` and write board-specific GPIO masks using `gpio_bits()`, `gpio_inout()`, `gpio_read()`, `gpio_write()`, or `btaor()`. `winview_volume()` bit-bangs an 18-bit command sequence to a PT2254A volume chip with data, clock, and strobe pins.

## State and Persistence
The state is the board GPIO output latch and, for query calls, the caller-provided `v4l2_tuner` fields. Some routines suppress changes while `btv->radio_user` is active. No persistent configuration is stored by this file.

## Dependencies and Integration Points
The functions are referenced from `bttv_tvcards[]` entries through `.audio_mode_gpio` and `.volume_gpio`. They integrate with V4L2 tuner audio mode constants, global bttv GPIO debugging/tracking, and card definitions in `bttv-cards.c`.

## Risks and Edge Cases
The GPIO masks are card-specific and can mute audio or route the wrong source on board revisions with different wiring. Some comments explicitly note untested or variant-sensitive behavior, such as Prolink/FlyVideo stereo paths. Query paths often advertise broad capability because hardware status reporting is limited. GPIO writes must preserve unrelated pins through correct masks.

## Test Signals
Exercise mono/stereo/SAP/lang mode switching per supported card, verify no changes during radio-user paths where guarded, confirm GPIO tracking output matches expected masks, validate WinView volume bit-banging on a scope or known board, and check that audio remains unmuted after input changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-audio-hook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-audio-hook.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-audio-hook.h

## Purpose
`bttv-audio-hook.h` declares the board-specific audio GPIO hook functions used by the bttv card table.

## Important APIs, Types, and Functions
The header includes `bttvp.h` and declares the volume hook `winview_volume()` plus audio mode hooks for Lifetec, AVerMedia, TerraTV, I-O Data GV-BCTV, WinFast, Prolink/FlyVideo, WinDVR, and AD-TVK503 boards. Each audio hook accepts `struct bttv *`, `struct v4l2_tuner *`, and a `set` flag.

## Control Flow
There is no executable control flow. The declarations allow `bttv-cards.c` to assign function pointers in `struct tvcard` initializers and call sites to compile with type checking.

## State and Persistence
The header declares functions that manipulate volatile GPIO state, but it stores no state itself.

## Dependencies and Integration Points
It binds `bttv-audio-hook.c` to `bttv-cards.c` and depends on the private bttv structures and V4L2 tuner definitions made available by `bttvp.h`.

## Risks and Edge Cases
Prototype drift between the header and implementation would break function-pointer assignment or calls. Because this is private driver API, changes must be synchronized with card table fields such as `.audio_mode_gpio` and `.volume_gpio`.

## Test Signals
Build coverage is the primary signal: all card table assignments compile, hooks link into `bttv.o`, and no incompatible pointer type warnings are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-audio-hook.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-cards.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-cards.c

## Purpose
`bttv-cards.c` is the board database and board-specific initialization layer for the bttv Bt848/Bt878 analog capture driver. It maps PCI subsystem IDs and EEPROM data to `struct tvcard` definitions, applies module overrides, configures tuners/audio/radio/remotes, initializes unusual GPIO/I2C/firmware hardware, and implements custom video mux selection for multi-input surveillance and capture boards.

## Important APIs, Types, and Functions
The primary exported data is `bttv_tvcards[]`, with `bttv_num_tvcards` as the size. Important public functions are `bttv_idcard()`, `bttv_init_card1()`, `bttv_init_card2()`, `bttv_init_tuner()`, `bttv_tda9880_setnorm()`, `bttv_check_chipset()`, and `bttv_handle_chipset()`. Key internal helpers cover EEPROM parsing (`identify_by_eeprom()`, `hauppauge_eeprom()`, `avermedia_eeprom()`, `osprey_eeprom()`, `modtec_eeprom()`), board GPIO probing (`flyvideo_gpio()`, `miro_pinnacle_gpio()`), MSP/audio reset and PVR firmware boot (`boot_msp34xx()`, `bttv_reset_audio()`, `pvr_boot()`), TEA575x radio ops, and many mux hooks (`rv605_muxsel()`, `eagle_muxsel()`, `xguard_muxsel()`, `ivc120_muxsel()`, `PXC200_muxsel()`, `kodicom4400r_muxsel()`, `gv800s_muxsel()`, and others).

## Control Flow
Card identification starts in `bttv_idcard()`: it builds a subsystem ID, searches the `cards[]` table, allows the `card[]` module parameter to override detection, logs the selected card, and optionally rewrites audio GPIO configuration from `audioall`, `audiomux[]`, and `gpiomask`. `bttv_init_card1()` runs before I2C bus registration and handles early reset/boot work such as MSP reset, PVR Altera firmware upload, hardware I2C selection for DVB cards, and special unlock sequences. `bttv_init_card2()` runs after I2C registration; it may re-identify unknown boards by EEPROM, probes board-specific GPIO/EEPROM metadata, initializes TEA575x radio and special mux hardware, sets PLL defaults and module overrides, chooses tuner/radio/remote/SVHS/digital-input fields, attaches RDS/audio subdevices, and returns early when no tuner exists. `bttv_init_tuner()` then instantiates tuner subdevices and sends tuner setup/config to all relevant V4L2 subdevices. Mux hooks are called later by input selection paths to program external analog switches through GPIO or I2C.

## State and Persistence
Module parameters provide per-card persistent-in-module configuration arrays for card type, PLL, tuner, SVHS, remote, audio device, and audio mux behavior. Runtime mutable state is written into each `struct bttv`: card type, tuner type, PLL fields, radio/remote flags, GPIO IRQ flag, TEA575x GPIO mapping, TDA9887 config, digital/SVHS input indexes, audio hooks, master-controller pointers, and switch status arrays. Hardware state is GPIO direction/data, I2C-controlled muxes/tuners/audio chips, PCI config workarounds, and optional loaded firmware.

## Dependencies and Integration Points
The file integrates with the bttv private core (`bttvp.h`), V4L2 subdevice creation, media tuner and tvaudio APIs, tveeprom parsing, request_firmware for `hcwamc.rbf`, PCI subsystem IDs and chipset problem flags, GPIO/I2C helper functions, TEA575x radio support, and audio hooks declared in `bttv-audio-hook.h`. DVB-aware cards are marked with `.has_dvb` and align with `bt878.c` and `DVB_BT8XX`.

## Risks and Edge Cases
The large declarative card table carries high regression risk: small changes to `muxsel`, `gpiomask`, tuner type, or flags can break only one board revision. Some boards lack subsystem IDs and rely on EEPROM, GPIO strap reads, or user `card=` overrides. Multi-chip boards use global `master[]` pointers and relative probe ordering; if the expected master chip is not detected in order, mux hooks may do nothing. GPIO mux hooks manipulate shared pins and must preserve unrelated signals. Firmware upload for Hauppauge PVR fails when `hcwamc.rbf` is unavailable. `bttv_tvcards[]` is modified at runtime for audio override parameters, so global card definitions can differ per instance in ways that are not immutable.

## Test Signals
Important signals are correct PCI subsystem detection, user override handling, EEPROM-based reclassification, GPIO strap decoding on FlyVideo/Miro/Pinnacle, PLL/tuner/radio/remote setup logs, successful audio subdevice probing, TEA575x radio detection, PVR firmware upload, per-board mux switching for 4/10/16-input boards, no GPIO IRQ on boards marked `no_gpioirq`, DVB cards avoiding analog-only initialization where required, and chipset workaround writes for ETBF/VSFX/latency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-cards.c -->
