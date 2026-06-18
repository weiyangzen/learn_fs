# Research: subset-b-004130

This grouped report covers the TW686x PCI capture driver files and the Zoran ZR36057/ZR36067 MJPEG driver files listed in work item `subset-b-004130`. Each section is delimited for deterministic split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-core.c

## Purpose
`tw686x-core.c` is the PCI driver core for Intersil/Techwell TW6864/TW6865/TW6868/TW6869 video frame grabber devices. It owns module parameters, PCI probe/remove, device lifetime, interrupt dispatch, and the shared DMA channel enable/reset path used by the video and audio subdrivers. The file is intentionally conservative around hardware access because the header comments document stress-test failures where DMA register programming while streaming could freeze the host or the PCIe link could disappear.

## Important APIs, Types, And Functions
The public functions exported to sibling source files are `tw686x_enable_channel()` and `tw686x_disable_channel()`, both operating on `struct tw686x_dev` and channel bit numbers. Module parameters are `dma_interval`, written to `DMA_TIMER_INTERVAL`, and `dma_mode`, parsed through `tw686x_dma_mode_set()` as `memcpy`, `contig`, or `sg`. `tw686x_irq()` is the central IRQ handler. `tw686x_probe()` allocates `struct tw686x_dev`, channel arrays, enables PCI/MMIO/DMA, resets hardware, initializes video and audio, requests the IRQ, and stores drvdata. `tw686x_remove()` tears down IRQ, media devices, timer, MMIO, PCI resources, and marks `dev->pci_dev = NULL` under `dev->lock` before dropping the final V4L2 reference.

## Control Flow
Probe starts with allocation and 32-bit DMA mask setup, maps BAR0, resets system and decoder blocks, disables DMA, configures FIFO/error handling and DMA timing, then calls `tw686x_video_init()` and `tw686x_audio_init()`. IRQ handling reads `INT_STATUS` and `VIDEO_FIFO_STATUS`, returns `IRQ_NONE` if neither standard interrupts nor FIFO errors are present, then coalesces video channel events, audio requests, and DMA timeout handling. Video requests go to `tw686x_video_irq()` with `pb_status` and FIFO state; audio requests go to `tw686x_audio_irq()`. Channels needing reset are disabled via `tw686x_reset_channels()` and re-enabled later by `tw686x_dma_delay()`.

## State And Persistence
Persistent runtime state is in `struct tw686x_dev`: PCI pointer, MMIO base, DMA mode ops selected by video init, per-channel arrays, audio settings, a shared spinlock, `dma_delay_timer`, and pending DMA enable/command register images. No disk state exists. The delayed DMA state is volatile but critical: `pending_dma_en` and `pending_dma_cmd` coalesce channel changes to avoid programming DMA too rapidly.

## Dependencies And Integration Points
The file integrates with Linux PCI, DMA mapping, IRQ, timer, V4L2 device lifetime, and the sibling TW686x video/audio layers. It depends on register offsets and bit definitions from `tw686x-regs.h` and structures/prototypes from `tw686x.h`. The PCI ID table encodes channel count and second-generation SG table behavior through `driver_data`.

## Risks
The core risk is hardware instability from register writes during streaming; the timer-based delayed enable and reset throttling are explicit mitigations. Hot-unplug is handled by setting `pci_dev` to NULL after resources are unavailable, so userspace file handles must honor that state in vb2 paths. IRQ reset uses `reset_ch = ~0` on DMA timeout; callers rely on channel masks being bounded later. Audio init failure is only a warning, so video-only operation is possible but audio regressions could be missed.

## Test Signals
Useful signals are successful module load/probe, one video node per channel, working capture in all three `dma_mode` values, no host lockups under repeated stream on/off, DMA timeout recovery logs, FIFO-error recovery logs, and clean hot-unplug/removal while file handles remain open. Interrupt behavior can be observed through frame delivery continuity and absence of stale DMA channels after stream stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-regs.h

## Purpose
`tw686x-regs.h` is the register map and bit-definition header for the TW686x driver. It translates the chip's DMA controller and video decoder register layout into symbolic offsets used by `tw686x-core.c`, `tw686x-video.c`, and the audio driver. It also provides per-channel register-array macros for devices with up to eight channels.

## Important APIs, Types, And Functions
There are no functions or types, only macros. `REG8_1`, `REG8_2`, and `REG8_8` build constant eight-element register arrays for contiguous, two-step, and eight-step channel register blocks. `VDREG8` and `VDREG2` build video-decoder register arrays. Named register offsets include `INT_STATUS`, `PB_STATUS`, `DMA_CMD`, `VIDEO_FIFO_STATUS`, `DMA_CHANNEL_ENABLE`, `DMA_TIMER_INTERVAL`, `VDMA_CHANNEL_CONFIG`, `VDMA_P_ADDR`, `VDMA_B_ADDR`, `DMA_PAGE_TABLE0_ADDR`, `DMA_PAGE_TABLE1_ADDR`, `SDT`, `SDT_EN`, and per-channel scaler/crop/status registers. Important bit and mode macros include `DMA_CMD_ENABLE`, `INT_STATUS_DMA_TOUT`, `TW686X_VIDSTAT_HLOCK`, `TW686X_VIDSTAT_VDLOSS`, standard IDs, `TW686X_FIELD_MODE`, `TW686X_FRAME_MODE`, `TW686X_SG_MODE`, and `TW686X_FIFO_ERROR()`.

## Control Flow
This header does not execute. Its definitions drive all MMIO control flow: the core IRQ path reads `INT_STATUS`, `PB_STATUS`, and `VIDEO_FIFO_STATUS`; video setup writes `VDMA_CHANNEL_CONFIG`, `VDMA_WHP`, `PHASE_REF`, `SDT`, `VIDEO_FIELD_CTRL`, and control registers; DMA mode setup writes either direct frame-buffer addresses or SG page-table addresses. The array macros allow the same video code to index channel-specific offsets by `vc->ch`.

## State And Persistence
No runtime state is stored here. The header is a compile-time contract between C code and hardware. Mistakes in constants persist as wrong hardware programming until rebuilt, which is riskier than ordinary software state because register writes can corrupt DMA or freeze affected systems.

## Dependencies And Integration Points
The header assumes Linux bit helpers such as `BIT()` and size macros like `SZ_512`/`SZ_4K` are available through including translation units. It is included by `tw686x.h`, which then makes register helpers visible to the rest of the TW686x module. It is tightly coupled to chip datasheet semantics and to the `struct tw686x_dev` MMIO pointer arithmetic in `reg_read()`/`reg_write()`.

## Risks
Register arrays are compound literals, so callers should use them as immediate constants and not persist pointers beyond expression lifetimes. The `TW686X_FIFO_ERROR(x)` macro treats any non-low-byte bits as FIFO error state; code using it must preserve the device-specific encoding. Header comments and core comments indicate DMA programming mistakes can trigger severe hardware failure modes.

## Test Signals
Validation is indirect: correct standards detection, frame sizes, DMA modes, frame parity, FIFO reset behavior, audio DMA period sizing, and video controls all demonstrate that register offsets and bit masks match the hardware. Compile coverage also catches missing macro dependencies, but not semantic register mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-video.c

## Purpose
`tw686x-video.c` implements the TW686x V4L2 video capture side. It registers one video device per hardware channel, manages videobuf2 queues, programs per-channel format/standard/input/framerate registers, implements three DMA strategies, and services video interrupts by completing and refilling P/B buffers.

## Important APIs, Types, And Functions
The file defines supported formats UYVY, RGB565, and YUYV through `struct tw686x_format`. DMA behavior is selected through `struct tw686x_dma_ops` instances: `memcpy_dma_ops`, `contig_dma_ops`, and `sg_dma_ops`. Key vb2 functions are `tw686x_queue_setup()`, `tw686x_buf_queue()`, `tw686x_buf_prepare()`, `tw686x_start_streaming()`, and `tw686x_stop_streaming()`. V4L2 ioctl handlers include `tw686x_g_fmt_vid_cap()`, `tw686x_try_fmt_vid_cap()`, `tw686x_s_fmt_vid_cap()`, `tw686x_s_std()`, `tw686x_querystd()`, `tw686x_s_parm()`, and input enumeration/setters. Externally visible functions are `tw686x_video_init()`, `tw686x_video_free()`, and `tw686x_video_irq()`.

## Control Flow
Video init chooses DMA ops from `dev->dma_mode`, registers `v4l2_device`, optionally sets up SG table sizing, initializes each `struct tw686x_video_channel`, programs NTSC/full-size/default input/default framerate, initializes vb2 and controls, allocates and registers a `video_device`, then writes global decoder/video-mode registers. When userspace streams, queued vb2 buffers move to `vidq_queued`; `start_streaming` refills both hardware P/B slots, schedules the core delayed DMA enable, and initializes sequence/parity. IRQ handling validates signal state, FIFO status, and expected P/B parity. A good IRQ calls `tw686x_buf_done()` and then the active DMA mode's `buf_refill()` for the same parity slot.

## State And Persistence
Per-channel state includes queued and current buffers, DMA descriptors, optional SG descriptor tables, V4L2 controls, current format, standard, dimensions, channel/input numbers, fps, sequence, current P/B slot, and no-signal state. State is volatile and protected by `vc->qlock` for queues and by `dev->lock` for shared device presence/DMA register state. Format and standard changes are rejected while the queue is busy.

## Dependencies And Integration Points
The file uses V4L2, videobuf2 vmalloc/contig/sg memory backends, Linux DMA mapping, and the core TW686x channel enable/disable functions. In memcpy mode, hardware writes to coherent internal buffers and data is copied into vmalloc-backed userspace buffers. In contiguous mode, hardware writes directly to vb2 DMA-contig buffers. In SG mode, per-frame descriptor tables are filled from vb2 DMA-SG scatterlists and pointed to by page-table registers.

## Risks
The SG path caps descriptor count at 256 and entry size at 4096 bytes; unsupported scatterlist shapes fail the buffer with `VB2_BUF_STATE_ERROR`. The memcpy path allocates two coherent frame buffers per channel and copies on IRQ, increasing memory bandwidth. Hot-unplug protection depends on checking `dev->pci_dev` under lock in queue/start/stop/free paths. Several operations return `-EBUSY` while streaming, so tests must cover userspace reconfiguration attempts. P/B parity mismatch or FIFO errors trigger channel resets, which are necessary but can drop frames.

## Test Signals
Exercise each pixel format, NTSC/PAL/SECAM standard changes, standard detection when idle, half/full width and height, frame interval requests, input switching, and stream-on/off. DMA mode matrix testing is essential: `dma_mode=memcpy`, `contig`, and `sg` should all produce monotonic timestamps/sequences and recover from no-signal/FIFO-error events. Hot-unplug or forced remove while buffers are queued should complete buffers with errors rather than dereferencing a stale PCI device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x.h

## Purpose
`tw686x.h` is the shared internal header for the TW686x driver. It defines the device, video-channel, audio-channel, buffer, DMA descriptor, format, and DMA-ops structures used across the core, video, and audio source files, plus inline register helpers and exported sibling-function prototypes.

## Important APIs, Types, And Functions
Important types are `struct tw686x_dev`, `struct tw686x_video_channel`, `struct tw686x_audio_channel`, `struct tw686x_dma_ops`, `struct tw686x_dma_desc`, `struct tw686x_sg_desc`, `struct tw686x_v4l2_buf`, and `struct tw686x_audio_buf`. Constants describe device type bits (`TYPE_MAX_CHANNELS`, `TYPE_SECOND_GEN`), audio page/period limits, and DMA mode IDs. Inline helpers `reg_read()` and `reg_write()` access `dev->mmio + reg`; `max_channels()` extracts the low nibble of `dev->type`; `is_second_gen()` identifies chips with per-channel SG tables. Prototypes connect core/video/audio files.

## Control Flow
This file does not implement runtime control flow, but its structures shape it. The core allocates `struct tw686x_dev` and channel arrays, video init fills `struct tw686x_video_channel`, audio init fills `struct tw686x_audio_channel`, vb2 paths manipulate `struct tw686x_v4l2_buf`, and DMA implementations use `struct tw686x_dma_ops` callbacks. `reg_read()`/`reg_write()` are used throughout to program hardware.

## State And Persistence
The header centralizes volatile driver state. `struct tw686x_dev` owns device lifetime, the V4L2 and ALSA handles, MMIO pointer, selected DMA ops, audio parameters, delayed DMA timer, and pending DMA register snapshots. Video channels own vb2 queue state and capture settings. Audio channels own ALSA substream state, current page buffers, descriptors, and locks. There is no persistent storage outside kernel memory and device registers.

## Dependencies And Integration Points
The header pulls in Linux PCI, timer, mutex, V4L2, videobuf2, and ALSA PCM headers. It includes `tw686x-regs.h`, making register constants available to all users. The media-facing APIs are V4L2 for video and ALSA for audio; the lower-level integration is PCI MMIO and DMA.

## Risks
Because `reg_read()` and `reg_write()` perform raw MMIO through `dev->mmio`, callers must ensure device presence and locking where needed. The hot-unplug design relies on shared convention around `dev->pci_dev == NULL`, not compiler-enforced ownership. The P/B buffer arrays in audio and video are fixed at two entries, so all control paths must keep parity state consistent. `struct tw686x_sg_desc` packs flags and length into little-endian fields, making endian correctness essential.

## Test Signals
Compile coverage should include all sibling TW686x files because this header defines cross-file contracts. Runtime signals include correct max-channel behavior for 4- and 8-channel chips, second-generation SG table selection, valid V4L2/ALSA device registration, and safe behavior when remove races with open vb2 queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/Kconfig

## Purpose
`zoran/Kconfig` declares configuration options for the deprecated Zoran ZR36057/ZR36067 Video4Linux MJPEG driver and board-specific support variants. It controls whether the core driver and optional codec modules are built into the `zr36067` object.

## Important APIs, Types, And Functions
This is Kconfig metadata, not C code. The primary symbol is `VIDEO_ZORAN`, a tristate depending on `PCI`, `I2C_ALGOBIT`, `VIDEO_DEV`, `DEBUG_FS`, and not `ALPHA`. It selects `VIDEOBUF2_DMA_CONTIG` and conditionally selects I2C decoder/encoder drivers for supported boards. Boolean board symbols include `VIDEO_ZORAN_DC30`, `VIDEO_ZORAN_ZR36060`, `VIDEO_ZORAN_BUZ`, `VIDEO_ZORAN_DC10`, `VIDEO_ZORAN_LML33`, `VIDEO_ZORAN_LML33R10`, and `VIDEO_ZORAN_AVS6EYES`.

## Control Flow
Build-time control flow is dependency driven. Enabling `VIDEO_ZORAN` builds the core driver. Enabling `VIDEO_ZORAN_DC30` includes support for the ZR36050 MJPEG codec and ZR36016 VFE path. Enabling `VIDEO_ZORAN_ZR36060` unlocks boards using the ZR36060 codec; board-specific options under it select the needed I2C subdevice drivers.

## State And Persistence
Kconfig choices persist in the kernel configuration and determine compiled capabilities. They do not create runtime state directly, but they decide whether `codec_init()` in `zoran_card.c` can register codec implementations or returns unsupported errors.

## Dependencies And Integration Points
The file integrates with the Linux media Kconfig tree, PCI, bit-banged I2C, V4L2, videobuf2 DMA-contig, debugfs, and numerous media I2C subdevice drivers. The help text points users to Zoran driver documentation and states the module name as `zr36067`.

## Risks
Missing board options can produce runtime probe failures when `zoran_card.c` attempts to initialize a codec compiled out of the build. The driver is explicitly marked deprecated and depends on `DEBUG_FS`, making it unavailable in configurations that omit debugfs. Conditional `select` usage means board options may pull in legacy I2C components.

## Test Signals
Build tests should cover `VIDEO_ZORAN=m`, `VIDEO_ZORAN_DC30=y`, and `VIDEO_ZORAN_ZR36060=y` combinations, plus individual board selections. Runtime probe should confirm expected codec support messages rather than "support is not enabled" errors for configured boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/Makefile

## Purpose
`zoran/Makefile` defines how the Zoran MJPEG driver object is assembled. It maps Kconfig symbols to the core object list and optional codec implementation objects.

## Important APIs, Types, And Functions
There are no runtime APIs. `zr36067-objs` always includes `zoran_device.o`, `zoran_driver.o`, `zoran_card.o`, and `videocodec.o`. `obj-$(CONFIG_VIDEO_ZORAN) += zr36067.o` emits the module/built-in object. Conditional object additions are `zr36067-$(CONFIG_VIDEO_ZORAN_DC30) += zr36050.o zr36016.o` and `zr36067-$(CONFIG_VIDEO_ZORAN_ZR36060) += zr36060.o`.

## Control Flow
Build flow follows Kbuild aggregation. The core driver is linked whenever `VIDEO_ZORAN` is enabled. Codec source files are compiled into the same final object only when their corresponding Kconfig symbols are enabled, matching the `#ifdef CONFIG_VIDEO_ZORAN_*` guards in `zoran_card.c`.

## State And Persistence
The file contributes build-time state only. Its choices persist in the generated kernel build artifacts and determine which `zr36016_init_module()`, `zr36050_init_module()`, or `zr36060_init_module()` symbols are available to the core code.

## Dependencies And Integration Points
It integrates with Linux Kbuild and `Kconfig`. The object composition matches logical layers: card/probe, V4L2/vb2 driver, hardware register engine, videocodec registry, and optional codec chips.

## Risks
If Kconfig and Makefile conditions drift, probe can compile references that are unavailable or omit codec implementations that board configuration expects. Since codec "modules" are linked into `zr36067.o` rather than separate loadable modules here, initialization/cleanup naming is internal and called manually by `zoran_card.c`.

## Test Signals
`make M=drivers/media/pci/zoran` or equivalent kernel builds should be checked for core-only, DC30, and ZR36060-enabled configurations. Link errors around codec init/cleanup functions would indicate Kconfig/Makefile mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/videocodec.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/videocodec.c

## Purpose
`videocodec.c` implements a small in-driver registry that binds Zoran master devices to hardware codec implementations. Codec templates register once, masters attach to matching templates, and each attachment receives a duplicated `struct videocodec` with per-attachment private data.

## Important APIs, Types, And Functions
Internal lists are `struct codec_list` for registered codec templates and `struct attached_list` for live attachments. Global state is `codeclist_top`. Exported functions are `videocodec_attach()`, `videocodec_detach()`, `videocodec_register()`, `videocodec_unregister()`, and `videocodec_debugfs_show()`. Attach uses `kmemdup()` on the template, appends an instance suffix to `codec->name`, sets `codec->master_data`, and calls the codec's `setup()` callback. Detach calls `unset()`, unlinks the attachment, frees the duplicated codec, and decrements `attached`.

## Control Flow
Codec implementations call `videocodec_register()` from their init helpers. During PCI probe, `zoran_card.c` builds a `struct videocodec_master` with bus read/write callbacks and calls `videocodec_attach()`. Attach scans registered templates and accepts one where `(master->flags & codec->flags) == master->flags`, then invokes setup to verify hardware and allocate private state. Driver removal calls `videocodec_detach()` and later unregisters templates through codec cleanup helpers.

## State And Persistence
All state is in global linked lists and dynamically allocated codec instances. There is no locking in this file, so it assumes serialized registration/attachment through the driver probe/remove path. Debugfs rendering walks the same lists and prints registered templates plus attached masters.

## Dependencies And Integration Points
This layer depends on `videocodec.h` callbacks, Zoran logging helpers via `videocodec_to_zoran()`, and codec implementations in `zr36016.c`, `zr36050.c`, and `zr36060.c`. It bridges the master bus access functions in `zoran_card.c` with codec-specific register programming.

## Risks
The matching expression requires the codec flags to include every flag requested by the master, but it does not check codec type directly; card probe performs type validation after attach. Lack of locking would be unsafe if multiple probe/remove or debugfs paths could concurrently mutate/traverse the lists. `videocodec_register()` derives a Zoran pointer from a template codec that may not yet have master data, so logging paths rely on current assumptions about call context.

## Test Signals
Probe logs should show codec registration and attachment, debugfs should list slave templates and master attachments, and removal should not leave `attached` counts behind. Negative tests include absent codec support, wrong type after attach, busy unregister while attached, and attach failure from codec `setup()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/videocodec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/videocodec.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/videocodec.h

## Purpose
`videocodec.h` defines the internal master/slave API used by the Zoran driver to attach hardware JPEG codecs and video front ends to the ZR36057/ZR36067 PCI controller. It documents expected usage, command IDs, flags, mode IDs, data structures, and helper casts back to `struct zoran`.

## Important APIs, Types, And Functions
Core types are `struct videocodec`, `struct videocodec_master`, `struct vfe_settings`, `struct vfe_polarity`, `struct tvnorm`, `struct jpeg_com_marker`, and `struct jpeg_app_marker`. Flags describe codec capabilities such as JPEG, hardware, VFE, encoder, decoder, IRQ, and picture I/O. Commands include status/mode/VFE/MMAP operations and JPEG target-size, scale, Huffman, quantization, APP, and COM data controls. Function prototypes expose attach/detach/register/unregister and debugfs display. Inline helpers `videocodec_master_to_zoran()` and `videocodec_to_zoran()` recover the owning `struct zoran`.

## Control Flow
The header describes callback control flow: masters provide `readreg()` and `writereg()` callbacks; slaves provide `setup()`, `unset()`, `set_mode()`, `set_video()`, and `control()` plus optional IRQ/image hooks. The Zoran card code constructs masters; codec source files define static `struct videocodec` templates; `videocodec.c` matches and duplicates templates during attach.

## State And Persistence
`struct videocodec` stores registered template fields and live attachment fields including `master_data` and private `data`. `struct videocodec_master` stores the master name, flags, opaque `data`, and register callbacks. JPEG marker structures cap APP/COM payloads at 60 bytes. State is kernel-only and per attachment.

## Dependencies And Integration Points
The header includes Linux debugfs and V4L2 definitions and then includes `zoran.h` for helper casts. It is consumed by all Zoran codec files, `videocodec.c`, `zoran_card.c`, and `zoran_device.c`. The API is explicitly not a userspace ABI; V4L2 ioctls eventually influence it through `zoran_driver.c` settings.

## Risks
The API is loosely typed: `control()` takes integer command IDs plus void pointers and size checks must be correct in every codec implementation. The header itself notes that master/slave data structures are device-dependent. Including `zoran.h` from this header couples the generic-looking codec API back to one driver. Deprecated comments mention procfs even though the implementation now exposes debugfs, a documentation drift signal.

## Test Signals
Build coverage across all codec configurations is the first signal. Runtime signals are correct codec attach, VFE setup, JPEG quality/APP/COM propagation, and debugfs display. Fuzzing or negative ioctl tests around JPEG controls should not pass wrong-size buffers to codec `control()` callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/videocodec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran.h

## Purpose
`zoran.h` is the central private header for the Zoran MJPEG driver. It defines card identities, formats, settings, card capability tables, the main `struct zoran` device state, register access macros, logging helpers, and queue entry types shared by card, device, driver, and codec code.

## Important APIs, Types, And Functions
Important enums are `card_type`, `zoran_codec_mode`, `zoran_map_mode`, GPIO IDs, and guest-bus IDs. Important structures are `struct zr_buffer`, `struct zoran_format`, `struct zoran_v4l_settings`, `struct zoran_jpg_settings`, `struct card_info`, and `struct zoran`. Helpers include `vb2_to_zr_buffer()`, `to_zoran()`, `ZR_DEVNAME()`, `btread()`, `btwrite()`, `btand()`, `btor()`, and `btaor()`. It declares `zoran_queue_init()`, `zoran_queue_exit()`, and `zr_set_buf()`.

## Control Flow
This header shapes nearly all Zoran control flow. `zoran_card.c` fills `struct zoran` and `struct card_info`, `zoran_driver.c` manipulates map mode and vb2 queues, `zoran_device.c` reads/writes ZR36057 registers through `btread`/`btwrite`, and codec files use `struct tvnorm` and JPEG settings through the videocodec layer. `struct zr_buffer` is embedded in vb2 buffer allocations.

## State And Persistence
`struct zoran` contains persistent runtime state for one PCI card: V4L2 device, controls, video node, vb2 queue, bit-banged I2C adapter, decoder/encoder subdevs, attached codec/VFE, locks, card info, norm/input/timing, raw and JPEG settings, queue counters, DMA status rings, interrupt counters, running/map modes, in-use buffers, and debugfs dentry. State persists while the kernel device object is bound and is reset/reinitialized on stream transitions.

## Dependencies And Integration Points
The header depends on PCI, I2C bit algorithm, V4L2 core/control/device APIs, videobuf2 core/V4L2/DMA-contig, debugfs, and the ZR36057 register map. The `card_info` structure integrates external media I2C decoder/encoder names and addresses with GPIO/GPCS mappings and codec IDs.

## Risks
Register access macros assume a local variable named `zr`, which makes them concise but context-sensitive. `struct zoran` is large and shared across IRQ, vb2, ioctl, probe, and remove paths; correct lock choice is essential. Several queue counters are unsigned longs used as ring indices and rely on masks such as `BUZ_MASK_STAT_COM`. Debug counters and operational counters coexist, so regressions can hide if tests only inspect one set.

## Test Signals
Signals include successful probe for each supported `card_type`, correct I2C subdevice discovery, valid debugfs contents, raw and MJPEG queue operation, no leaked `inuse[]` buffers after stream stop, and interrupt counters changing as expected during capture/playback. Static build checks should cover macro users because `btread`/`btwrite` depend on local naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_card.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_card.c

## Purpose
`zoran_card.c` is the PCI/card binding layer for the Zoran driver. It owns module parameters, PCI IDs, board database, bit-banged I2C setup, codec registration/attachment orchestration, V4L2 device allocation, default capture/JPEG settings, debugfs, probe, and remove.

## Important APIs, Types, And Functions
Module parameters include `card[]`, `default_input`, `default_mux`, `default_norm`, `video_nr[]`, and `pass_through`. Board data lives in the static `zoran_cards[]` table of `struct card_info`, including I2C decoder/encoder names, codec IDs, inputs, norms, timing tables, interrupts, GPIO/GPCS maps, VFE polarity, and board init hooks. Important functions are the guest-bus codec read/write callbacks (`zr36060_read/write`, `zr36050_read/write`, `zr36016_read`, exported `zr36016_write()`), `videocodec_init/exit()`, `zoran_check_jpg_settings()`, `zoran_i2c_init/exit()`, `zoran_open_init_params()`, `zr36057_init()`, `zoran_setup_videocodec()`, `zoran_probe()`, and `zoran_remove()`.

## Control Flow
Probe validates DMA mask and vb2 segment size, allocates `struct zoran`, registers V4L2/control state, enables PCI, selects a card by module parameter or PCI subsystem, maps MMIO, requests IRQ, adjusts PCI latency, restarts the chip, registers I2C and subdevices, registers codec templates, resets the JPEG codec, attaches codec and optional VFE via `videocodec_attach()`, initializes hardware resources/video node/status DMA buffers, creates debugfs, and returns bound. Remove reverses this by removing debugfs, releasing queues, detaching codecs/VFE, unregistering codec templates and I2C, disabling bus mastering, resetting GPIO, freeing IRQ/DMA/status buffers, releasing PCI, unregistering video/V4L2, and freeing controls.

## State And Persistence
Card-level settings persist in `struct zoran`: selected card info, norm/input, timing pointer, V4L/JPEG settings, status command buffers (`stat_com`, `stat_comb`) with DMA addresses, attached subdevs/codecs, initialized flag, and debugfs directory. Module parameters persist for the loaded module and affect all probes.

## Dependencies And Integration Points
The file integrates with PCI, DMA, V4L2 core/controls/video devices, debugfs, I2C algo-bit and media I2C subdevs, the videocodec registry, codec files, and low-level ZR36057 helpers from `zoran_device.c`. Kconfig controls which codec init paths compile.

## Risks
Manual error unwinding is long and cross-layered; missing an unwind step can leak IRQs, I2C adapters, DMA buffers, or codec attachments. `zoran_check_jpg_settings()` mutates settings while validating, so callers must distinguish try versus commit behavior. Some old board timing entries include documented U/V shift workarounds. Autodetect cannot identify older ZR36057 boards, requiring `card=X`. Probe failure paths generally return `-ENODEV`, which can hide the precise earlier error.

## Test Signals
Test each supported card selection path, invalid `card[]`, invalid defaults, missing I2C subdevice, missing codec support, debugfs output, and remove after partial probe failures. JPEG settings tests should verify decimation 1/2/4, custom crop alignment, quality clamping, APP/COM length clamping, and DC10_NEW horizontal-decimation restrictions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_card.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_card.h

## Purpose
`zoran_card.h` exposes the small cross-file API owned by `zoran_card.c`. It defines the maximum number of supported cards and declares the video template, JPEG settings validation, default parameter initialization, video-device release, and the ZR36016 write helper needed outside the card file.

## Important APIs, Types, And Functions
`BUZ_MAX` is set to 4 and sizes the `card[]` and `video_nr[]` module parameter arrays. Extern declarations include `zoran_template`, `zoran_check_jpg_settings()`, `zoran_open_init_params()`, `zoran_vdev_release()`, and `zr36016_write()`.

## Control Flow
This header has no runtime flow, but it connects `zoran_driver.c` to the card layer. The V4L2 driver file uses `zoran_template`, `zoran_vdev_release()`, and settings validation/defaults. `zoran_device.c` calls `zr36016_write()` during JPEG start for old DC10/DC30-style ZR36016 plus ZR36050 pipelines.

## State And Persistence
No state is stored here. `BUZ_MAX` affects module-parameter array capacity and therefore limits runtime card instances to four.

## Dependencies And Integration Points
The prototypes rely on `struct zoran`, `struct zoran_jpg_settings`, `struct video_device`, and `struct videocodec` being visible through includers. It is included by `zoran_card.c`, `zoran_device.c`, and `zoran_driver.c`.

## Risks
The `BUZ_MAX` hard cap is noted as "Anybody who uses more than four?" and could reject additional PCI devices in multi-card systems. Exposing `zr36016_write()` is described in the C file as a hack for `zoran_device.c`, signaling tight coupling between the VFE codec and device engine.

## Test Signals
Build coverage confirms prototypes and include ordering. Runtime multi-card tests beyond four devices should fail predictably. DC30/DC10 paths using ZR36016 should exercise the exported write helper during JPEG start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_card.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_device.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_device.c

## Purpose
`zoran_device.c` contains low-level ZR36057/ZR36067 hardware programming. It drives GPIO, guest-bus post-office access, JPEG codec sleep/reset/start, VFE geometry, raw memory grab, MJPEG engine setup, status-command queue feed/reap, interrupt handling, PCI bus mastering, hardware initialization, and chip restart.

## Important APIs, Types, And Functions
Public functions include `GPIO()`, `post_office_wait()`, `post_office_write()`, `post_office_read()`, `jpeg_codec_sleep()`, `jpeg_codec_reset()`, `zr36057_set_memgrab()`, `clear_interrupt_counters()`, `jpeg_start()`, `zr36057_enable_jpg()`, `zoran_feed_stat_com()`, `zoran_irq()`, `zoran_set_pci_master()`, `zoran_init_hardware()`, and `zr36057_restart()`. Key private helpers include `zr36057_init_vfe()`, `zr36057_set_vfe()`, `zr36057_adjust_vfe()`, `zr36057_set_jpg()`, `init_jpeg_queue()`, `count_reset_interrupt()`, and `zoran_reap_stat_com()`.

## Control Flow
Hardware init enables PCI mastering, runs a board init hook, initializes decoder/encoder subdevices, toggles JPEG sleep, initializes VFE, sets the JPEG engine idle, and clears interrupts. Raw capture start arms VSync interrupts, snapshot capture, VFE geometry, DMA target registers, and frame grab. MJPEG start configures decoder/encoder routing, codec/VFE callbacks, JPEG marker/target-size data, ZR36057 JPEG registers, status command rings, interrupts, and codec start pulse. IRQ handling clears interrupt sources; raw mode advances one buffer on VSync, while JPEG mode reaps completed status-command entries and feeds new queued buffers.

## State And Persistence
The file mutates `struct zoran` fields for codec mode, queue heads/tails, sequence/error counters, status rings, interrupt counters, running mode, `inuse[]`, and buffer reserve counts. Hardware register state is repeatedly reset and rebuilt at stream start. Status command memory is coherent DMA shared with the device.

## Dependencies And Integration Points
It depends on ZR36057 register definitions, card GPIO/GPCS metadata, V4L2 subdev decoder/encoder calls, videocodec callbacks for JPEG/VFE programming, vb2 DMA-contig buffer addresses, and PCI chipset quirk flags. It is called by probe/init and vb2 start/stop paths in `zoran_driver.c`.

## Risks
`post_office_wait()` busy-waits without a timeout; the source contains a TODO for this. Raw and JPEG paths manipulate hardware and queue state across IRQ and process contexts, so locking around `queued_bufs_lock` and assumptions around held spinlocks are important. Several legacy comments document hardware-specific color/polarity/timeout quirks. If no buffer is available, raw capture disables interrupts and marks the queue error. Endian conversion of status-command entries is required.

## Test Signals
Signals include raw capture frame delivery, MJPEG capture/playback status ring turnover, interrupt counters, correct encoder/decoder routing under `pass_through`, GPIO-driven codec reset/sleep, no queue leaks after stop, and recovery from empty queue. Hardware fault tests should target post-office timeout behavior and JPEG IRQs arriving in unexpected modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_device.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_device.h

## Purpose
`zoran_device.h` declares the low-level hardware operations implemented by `zoran_device.c` and provides convenience macros for calling the attached V4L2 decoder and encoder subdevices.

## Important APIs, Types, And Functions
Declarations cover GPIO access, guest-bus post-office reads/writes, JPEG codec sleep/reset, raw memory grabbing, interrupt helpers, JPEG start/enable/feed, PCI mastering, hardware initialization, and restart. It also declares `zoran_formats[]` and `pass_through`. Macros `decoder_call()` and `encoder_call()` wrap `v4l2_subdev_call()` on `zr->decoder` and `zr->encoder`.

## Control Flow
The header itself is declarative. Its API is used by `zoran_card.c` during probe/init/remove and by `zoran_driver.c` during vb2 streaming transitions. The subdevice call macros are used to route standards, inputs, streams, and encoder output paths.

## State And Persistence
No state is stored in the header. The declared functions mutate `struct zoran` and hardware registers. `pass_through` is a module-level runtime setting declared here for cross-file access.

## Dependencies And Integration Points
The header assumes visibility of `struct zoran`, `enum zoran_codec_mode`, `irqreturn_t`, and V4L2 subdevice types through includers. It is the boundary between user-facing vb2/V4L2 code and hardware register programming.

## Risks
The subdevice macros do not check whether `decoder` or `encoder` is NULL; callers rely on probe having created required subdevices or on `v4l2_subdev_call()` behavior. Because this API includes functions that must be called with locks held in some paths, call-site discipline is important and not encoded in types.

## Test Signals
Compile coverage across card/device/driver files validates declarations. Runtime signals are correct decoder/encoder routing, working raw/JPEG start/stop, interrupt handling, and behavior changes when `pass_through` is toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_driver.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_driver.c

## Purpose
`zoran_driver.c` implements the user-facing V4L2 and videobuf2 logic for the Zoran driver. It defines supported capture formats, ioctl handlers for format/norm/input/crop negotiation, and vb2 queue operations that start, stop, queue, prepare, and complete buffers for raw or MJPEG capture/playback modes.

## Important APIs, Types, And Functions
The exported data object is `zoran_formats[]`, including RGB555/565, BGR24/32, YUYV, UYVY, and MJPEG. Important helpers are `zoran_v4l2_calc_bufsize()`, `zoran_v4l_set_format()`, `zoran_set_norm()`, `zoran_set_input()`, `zoran_enum_fmt()`, `zoran_try_fmt_vid_out()`, `zoran_try_fmt_vid_cap()`, `zoran_s_fmt_vid_out()`, `zoran_s_fmt_vid_cap()`, selection handlers, `zr_set_buf()`, vb2 ops, `zoran_queue_init()`, and `zoran_queue_exit()`. `zoran_template` wires file and ioctl ops to the V4L2 video device.

## Control Flow
Userspace opens the V4L2 device, negotiates format and controls, requests vb2 buffers, queues them, and starts streaming. Non-MJPEG format selection sets `map_mode = ZORAN_MAP_MODE_RAW`; MJPEG selection sets a JPEG map mode and recalculates compression settings/buffer size. `zr_vb2_start_streaming()` clears status rings and `inuse[]`, restarts/reinitializes hardware, then either starts raw memory grab or configures JPEG mode, feeds queued buffers, starts the codec, and enables interrupts. `zr_set_buf()` completes the previous raw buffer, pulls a new queued buffer, programs top/bottom DMA target registers, and arms frame grab. Stop disables interrupts, idles JPEG/raw hardware, returns in-use and queued buffers with errors, disables PCI mastering, and resets map mode to raw.

## State And Persistence
This file mutates `zr->v4l_settings`, `zr->jpg_settings`, `zr->buffer_size`, `zr->map_mode`, `zr->running`, `zr->vbseq`, `zr->queued`, `zr->prepared`, `zr->buf_in_reserve`, `zr->inuse[]`, and `queued_bufs`. The V4L2 lock serializes ioctl/queue operations, while `queued_bufs_lock` protects the buffer list.

## Dependencies And Integration Points
It depends on V4L2 ioctl2, vb2 DMA-contig, PCI DMA addresses, low-level hardware operations from `zoran_device.c`, card validation/default helpers from `zoran_card.c`, and register definitions via `zoran.h`. External users see standard V4L2 capture ioctls and streaming buffer operations.

## Risks
The file comments say output is temporarily disabled, but MJPEG map modes still distinguish record/play naming in code, so mode naming is easy to misread. Two TODOs note TRY_FMT behavior for invalid pixelformats returns `-EINVAL` instead of substituting a default. Empty raw queues call `vb2_queue_error()`. Format/norm/input changes are rejected while `zr->running != ZORAN_MAP_MODE_NONE`, and tests should cover that. `zoran_v4l_set_format()` compares requested size to `zr->buffer_size` immediately after assigning it, making that availability check redundant.

## Test Signals
V4L2 compliance tests should cover format enumeration, TRY/S_FMT for raw and MJPEG, invalid formats, standard/input changes while idle and busy, crop selection only in compressed mode, vb2 MMAP/DMABUF streaming, empty queue errors, and stop cleanup. Runtime capture should show monotonic timestamps and sequences with correct payload sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36016.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36016.c

## Purpose
`zr36016.c` implements the videocodec slave for the Zoran ZR36016 video front-end processor used with older DC10/DC30-style boards. It provides register read/write helpers, basic hardware probing, mode/video setup, control handling, and registration with the internal videocodec registry.

## Important APIs, Types, And Functions
The file maintains `zr36016_codecs` with a `MAX_CODECS` guard. Register helpers are `zr36016_read()`, `zr36016_write()`, `zr36016_readi()`, and `zr36016_writei()`. Probe/setup helpers are `zr36016_read_version()`, `zr36016_basic_test()`, and `zr36016_init()`. Videocodec callbacks are `zr36016_setup()`, `zr36016_unset()`, `zr36016_set_mode()`, `zr36016_set_video()`, and `zr36016_control()`. Public init/cleanup functions register/unregister the static `zr36016_codec` template.

## Control Flow
`zr36016_init_module()` registers the codec template. When a Zoran master attaches, `zr36016_setup()` allocates `struct zr36016`, runs read/write tests against indirect PAX registers, reads a version nibble, initializes defaults, and calls `zr36016_init()`. `set_video()` records width, height, offsets, and decimation flags from the master. `set_mode()` validates compression/expansion and reinitializes hardware. `zr36016_init()` stops processing, writes mode/setup/window registers, then starts processing.

## State And Persistence
Per-attachment state is `struct zr36016`: name, instance number, parent `struct videocodec`, version, mode, x/y offsets, dimensions, and x/y decimation flags. It is allocated on setup and freed on unset. Hardware register state is rebuilt when mode changes.

## Dependencies And Integration Points
The codec accesses hardware only through `codec->master_data->readreg/writereg`, which are provided by `zoran_card.c` and ultimately use the ZR36057 post-office guest bus. It uses `struct tvnorm`, `struct vfe_settings`, and command IDs from `videocodec.h`.

## Risks
The code trusts the master for many video parameter validity checks and explicitly allows invalid start coordinates. Version validation only accepts version bits without high suspicious bits. Control support is minimal: status/mode/VFE return simple values and MMAP is unsupported. Cleanup warns if codecs remain registered, indicating attachment lifetime mismatches.

## Test Signals
Probe should show successful attach and version logging on boards requiring ZR36016. Negative tests include failed indirect register readback, unsupported mode values, wrong control sizes, and attach count overflow. Streaming through old DC10/DC30 paths should verify that VFE setup changes follow crop/decimation changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36016.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36016.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36016.h

## Purpose
`zr36016.h` defines the private state and register constants for the ZR36016 VFE videocodec implementation. It is used by `zr36016.c` and by card/device glue that must initialize or poke the VFE.

## Important APIs, Types, And Functions
`struct zr36016` stores instance name/number, parent codec pointer, version, mode, offsets, dimensions, and decimation flags. Direct register definitions include `ZR016_GOSTOP`, `ZR016_MODE`, `ZR016_IADDR`, and `ZR016_IDATA`. Indirect register definitions cover setup and active-window registers (`ZR016I_SETUP1`, `ZR016I_SETUP2`, `NAX/PAX/NAY/PAY/NOL`). Mode constants encode input/output color formats and compression/expansion bits. Setup constants encode horizontal/vertical decimation/filtering and CCIR/sync flags. Public prototypes are `zr36016_init_module()` and `zr36016_cleanup_module()`.

## Control Flow
This header is declarative. Its constants are used by `zr36016_init()` to stop/start the chip, set YUV422 conversion, configure decimation, and write window geometry through indirect register access.

## State And Persistence
No state is stored here beyond compiled constants. `struct zr36016` instances are allocated by `zr36016_setup()` and reflect the last requested VFE geometry/mode.

## Dependencies And Integration Points
The struct references `struct videocodec` without including the full header in this file, relying on include order in consumers. Register constants map the ZR36016 guest-bus register interface used through the Zoran master callbacks.

## Risks
Several mode constants overlap or encode the same bit for compression/expansion, matching hardware semantics but easy to misuse. Include-order reliance can be fragile if the header is reused elsewhere. Wrong indirect-register constants would produce bad crop/scale behavior.

## Test Signals
Compile with DC30 support validates include relationships. Runtime testing should verify old-board VFE geometry, decimation, and compression/expansion setup through successful MJPEG capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36016.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36050.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36050.c

## Purpose
`zr36050.c` implements the videocodec slave for the ZR36050 JPEG processor. It configures baseline JPEG compression/decompression tables, target code sizes, APP/COM markers, scaling, and mode state for older Zoran boards that pair the ZR36050 codec with a ZR36016 VFE.

## Important APIs, Types, And Functions
The file maintains `zr36050_codecs` with `MAX_CODECS`. Hardware helpers include `zr36050_read()`, `zr36050_write()`, `zr36050_read_status1()`, `zr36050_read_scalefactor()`, `zr36050_wait_end()`, `zr36050_basic_test()`, and `zr36050_pushit()`. JPEG segment builders are `zr36050_set_sof()`, `zr36050_set_sos()`, and `zr36050_set_dri()`. Codec callbacks are `zr36050_setup()`, `zr36050_unset()`, `zr36050_set_mode()`, `zr36050_set_video()`, and `zr36050_control()`. Public init/cleanup functions register/unregister `zr36050_codec`.

## Control Flow
On attach, setup allocates state, tests SOF memory readback and end status, initializes sampling ratios/default quality parameters, and calls `zr36050_init()`. Compression init writes hardware/master mode, disables IRQs, writes scale/volume parameters, builds SOF/SOS/DRI/DQT/DHT/APP/COM marker data, preloads Huffman tables, waits for completion, computes target net/data bit counts, and enables marker output. Expansion init sets master timing, preloads DHT, waits, then clears marker mode. `set_video()` derives coded width/height and target byte volume from capture dimensions, decimation, and quality.

## State And Persistence
`struct zr36050` stores status, mode, dimensions, bitrate control flag, total/real code volumes, max block volume, sampling ratios, scale factor, restart interval, and APP/COM marker data. State is per codec attachment and persists until unset. Hardware tables are rewritten when mode or video settings change.

## Dependencies And Integration Points
The codec uses master register callbacks from `zoran_card.c`, command IDs and marker structs from `videocodec.h`, and Zoran logging helpers. It is included in the final driver object when `CONFIG_VIDEO_ZORAN_DC30` is enabled and used for DC10_OLD/DC30/DC30_PLUS-style boards.

## Risks
Large fixed JPEG tables are embedded and not user-replaceable except for APP/COM/scale/target-size controls. Wait loops time out after roughly 200 ms but continue by breaking and later checking status. `set_video()` trusts master-supplied decimation enough that invalid zero divisors would be dangerous, though upstream validation should prevent them. Marker length handling assumes earlier clamping to 60 bytes.

## Test Signals
Board probe should pass SOF readback and end-flag tests. Capture tests should vary JPEG quality, target data size, scale factor, APP/COM marker length, and crop/decimation. Negative tests should cover wrong control sizes, unsupported codec mode, and attach failure on bad register readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36050.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36050.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36050.h

## Purpose
`zr36050.h` defines the private state and register map for the ZR36050 JPEG codec implementation. It supplies constants for direct codec registers, marker table indexes, hardware/mode/option/marker/status bits, and component IDs.

## Important APIs, Types, And Functions
`struct zr36050` stores instance identity, parent codec, last status, mode, dimensions, bitrate/volume fields, sampling ratios, scale factor, restart interval, and APP/COM marker data. Register constants cover `ZR050_GO`, hardware/mode/options, target code volume, scale, activity counters, status, SOF/SOS/DRI/DQT/DHT/APP/COM table indexes. Bit definitions cover master/DMA/endian hardware mode, compression/pass/bitrate-control mode, marker enable bits, status masks, and Y/U/V component IDs. Prototypes expose `zr36050_init_module()` and `zr36050_cleanup_module()`.

## Control Flow
The header is not executable. `zr36050.c` uses the constants to probe register memory, build JPEG marker tables, preload Huffman/quantization data, configure compression/expansion, and read status/scale factor.

## State And Persistence
No state is stored by the header. Its struct layout defines per-attachment codec state owned by `zr36050.c`.

## Dependencies And Integration Points
It includes `videocodec.h` for marker structs and codec types. It integrates with `zoran_card.c` through init/cleanup calls and with `videocodec.c` through the registered template.

## Risks
The header contains duplicated definitions for several `ZR050_MO_*` mode bits, which is harmless to the preprocessor because values match but is a maintenance smell. Register constants are hardware-specific and unvalidated at compile time. Incorrect marker-index constants would corrupt generated JPEG headers.

## Test Signals
Compile with `CONFIG_VIDEO_ZORAN_DC30` validates the header. Runtime signals are successful ZR36050 attach, correct status/scale-factor reads, and valid MJPEG output containing expected DQT/DHT/APP/COM markers when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36050.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36057.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36057.h

## Purpose
`zr36057.h` is the register-offset and bitfield header for the ZR36057/ZR36067 PCI controller. It defines the video front end, raw frame grab, GPIO/guest bus, interrupt, JPEG engine, sync, active-area, and post-office registers used by the Zoran low-level device code.

## Important APIs, Types, And Functions
There are no functions or structs. Key register offsets include `ZR36057_VFEHCR`, `VFEVCR`, `VFESPFR`, raw DMA target registers `VDTR`/`VDBR`, `VSSFGR`, `VDCR`, `SPGPPCR`, `GPPGCR1`, `ISR`, `ICR`, `I2CBR`, JPEG registers `JMC`, `JPC`, `VSP`, `HSP`, `FHAP`, `FVAP`, `FPP`, `JCBA`, `JCFT`, `JCGI`, post-office `POR`, and still-transfer `STR`. Bitfields cover polarity, scaler, pixel format, endian, snapshot/frame-grab status, soft reset, interrupt sources/enables, JPEG compression/expansion modes, GO/active/code-transfer control, and post-office pending/time/dir flags.

## Control Flow
This header drives register programming in `zoran_device.c` and `zoran_driver.c`. VFE geometry code writes H/V crop/scaler registers; raw capture writes DMA addresses and `VSSFGR`; IRQ code reads/clears `ISR` and controls `ICR`; JPEG setup writes `JMC`, `JPC`, sync/active-area registers, status command base, and FIFO thresholds; guest-bus access uses `POR`.

## State And Persistence
The header stores no runtime state. Its constants describe hardware register state persisted in the device until reset or overwritten.

## Dependencies And Integration Points
It depends on `BIT()` definitions being available from includers. It is included by `zoran.h`, making the register map available to the whole Zoran driver through `btread`/`btwrite` macros.

## Risks
Wrong bit shifts or masks can corrupt DMA, interrupts, or JPEG engine state. The register map is low-level and lacks type safety. `ZR36057_POR_PO_PEN` is used in a busy-wait loop without timeout in `zoran_device.c`, so post-office register behavior is a reliability-sensitive dependency.

## Test Signals
Hardware tests should exercise raw capture, JPEG capture, interrupt enable/clear, I2C bit-bang, guest-bus codec access, and soft reset. Register-map regressions usually surface as no video, no IRQs, failed codec attach, or malformed MJPEG buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36057.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36060.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36060.c

## Purpose
`zr36060.c` implements the videocodec slave for the ZR36060 JPEG codec and integrated VFE path. It handles hardware probing, JPEG table construction, compression/decompression setup, video timing/scaling/polarity programming, quality-derived target-size calculation, APP/COM marker controls, and registration with the Zoran videocodec registry.

## Important APIs, Types, And Functions
Module parameter `low_bitrate` halves the effective target bitrate for Buz compatibility. Hardware helpers include `zr36060_read()`, `zr36060_write()`, `zr36060_read_status()`, `zr36060_read_scalefactor()`, `zr36060_wait_end()`, `zr36060_basic_test()`, and `zr36060_pushit()`. JPEG builders are `zr36060_set_sof()`, `zr36060_set_sos()`, and `zr36060_set_dri()`. Core setup is `zr36060_init()`. Videocodec callbacks are `zr36060_setup()`, `zr36060_unset()`, `zr36060_set_mode()`, `zr36060_set_video()`, and `zr36060_control()`. Public init/cleanup register/unregister `zr36060_codec`.

## Control Flow
On attach, setup allocates `struct zr36060`, validates device/revision registers, waits for not-busy, initializes default sampling/volume/scale/restart fields, and calls `zr36060_init()`. `set_video()` resets the codec, writes video polarity, horizontal/vertical scaling, black-level registers, sync generator timing, active area, subimage area, computes real target code volume from dimensions/quality and optional `low_bitrate`, and writes max block volume. `set_mode()` validates compression or expansion and calls init. Compression init resets/load state, sets code interface and compression mode, disables interrupts, writes volume/scale, pushes SOF/SOS/DRI/DQT/DHT/APP/COM data, computes target bit counts, enables markers, and configures limited pixel range. Expansion init configures decompression and pushes DHT. Both paths trigger table load and wait for completion.

## State And Persistence
Per-attachment state includes status, mode, dimensions, bitrate flag, target and real code volumes, max block volume, sampling ratios, scale factor, DRI, and marker data. The static `low_bitrate` module parameter is global. Hardware state is rewritten on video and mode changes.

## Dependencies And Integration Points
The codec uses videocodec master read/write callbacks from `zoran_card.c` and is selected by `CONFIG_VIDEO_ZORAN_ZR36060` for BUZ/DC10_NEW/DC10_PLUS/LML/AVS paths. It bridges V4L2 JPEG quality/crop/decimation settings from `zoran_driver.c` and card timing from `zoran_card.c` into codec registers.

## Risks
Several comments mark uncertain hardware parameters (`CHECKME`) and an ignored `bitrate_ctrl` FIXME. `zr36060_basic_test()` uses an AND between failed device and revision comparisons, meaning one matching register can pass the test; that may be intentional tolerance but weakens detection. Division by decimation assumes validated nonzero fields. Wait-end timeout logs but cannot fully recover from stuck hardware.

## Test Signals
Probe should identify the codec and attach. Capture tests should vary `low_bitrate`, JPEG quality, decimation 1/2/4, crop, APP/COM markers, PAL/NTSC timing, and compression/decompression modes. Debug/status reads should show not-busy after table load, and MJPEG payload sizes should track requested quality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36060.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36060.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36060.h

## Purpose
`zr36060.h` defines the private state and register map for the ZR36060 JPEG codec/VFE implementation. It supplies codec state layout, direct register addresses, marker table indexes, load/status/interface/mode/marker/interrupt/video/scaling bit definitions, and init/cleanup prototypes.

## Important APIs, Types, And Functions
`struct zr36060` stores name, instance number, parent codec, status, mode, dimensions, bitrate flag, code-volume fields, max block volume, sampling ratios, scale factor, restart interval, and APP/COM marker data. Register constants cover codec load/status/interface/mode, target volumes, scale, activity counters, identity/revision, video control/polarity/scaling, sync generator, active/subimage windows, and JPEG marker table indexes. Bit definitions include `ZR060_LOAD_LOAD`, `ZR060_CFSR_BUSY`, code interface flags, compression mode flags, marker enables, interrupt masks/status, video polarity/control bits, and scaling flags.

## Control Flow
This header is declarative. `zr36060.c` uses its constants to probe identity, wait for table load completion, configure compression/decompression, write timing and active-area registers, and enable marker output.

## State And Persistence
No state is stored in the header. Its struct layout defines per-attached codec state that persists from setup until unset.

## Dependencies And Integration Points
It includes `videocodec.h` for marker structures and codec APIs. It is used by `zr36060.c` and called through `zoran_card.c` when ZR36060 support is enabled.

## Risks
The register namespace is large and easy to misuse, especially polarity bits where `zr36060.c` notes opposite meaning compared with ZR360x7 counterparts. Invalid constants would manifest as bad sync, wrong color range, no compression, or stuck busy status. The header exposes only init/cleanup; all detailed operations are callback-driven through the videocodec template.

## Test Signals
Build with `CONFIG_VIDEO_ZORAN_ZR36060` validates definitions. Runtime signals include successful identity probe, correct busy/status behavior, stable PAL/NTSC sync, functioning scaling/crop, and valid compressed MJPEG streams with expected marker behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zr36060.h -->
