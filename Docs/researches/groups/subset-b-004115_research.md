# subset-b-004115 Research

Grouped research for the listed Conexant media driver files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821.h

## Purpose
This header is the central private interface for the Conexant CX25821 PCIe bridge driver. It defines the board limits, video norms, channel/resource masks, DMA buffer shapes, I2C adapter representation, per-channel V4L2 state, upstream video/audio bookkeeping, SRAM channel descriptors, MMIO helpers, logging macros, and cross-file function prototypes used by the CX25821 capture and output implementation.

## Important APIs, Types, And Data
The main persistent in-kernel object is `struct cx25821_dev`, which embeds the `v4l2_device`, PCI identity and MMIO mappings, I2C buses, board metadata, current analog input and TV norm, spin/mutex locks, an array of `struct cx25821_channel`, audio upstream state, and two `cx25821_video_out_data` entries for upstream video. `struct cx25821_channel` owns one `video_device`, a vb2 queue, control handler, DMA queue, selected format, dimensions, field mode, and optional video-output state. `struct cx25821_buffer` wraps `vb2_v4l2_buffer` with a list node, bytes-per-line, RISC memory, and active format.

The hardware-facing interfaces are `struct cx25821_riscmem` for coherent RISC programs, `struct cx25821_i2c` for the three hardware I2C masters, and `struct sram_channel` for SRAM/FIFO/register layout. Inline helper `get_cx25821()` recovers the device from a `v4l2_device`. Register macros `cx_read`, `cx_write`, `cx_andor`, `cx_set`, and `cx_clear` assume a local variable named `dev` and access `dev->lmmio`.

The exported prototypes cover I2C registration/read/write, GPIO setup, Medusa decoder initialization and controls, SRAM/RISC setup, vb2 buffer release, device lookup/unregister, IRQ-bit printing, audio SRAM setup, and pixel format programming.

## Control Flow
The header does not execute control flow itself, but it defines the contracts used during probe, streaming, interrupt handling, and teardown. Probe code fills `cx25821_dev`, initializes PCI/MMIO, registers I2C buses, configures board-specific Medusa video decoders, initializes per-channel `video_device` and vb2 queue state, and binds SRAM descriptors. Streaming paths allocate `cx25821_buffer` objects, build RISC programs through the declared helpers, program SRAM channels, then rely on IRQ and DMA queues to complete buffers. Video and audio upstream paths store their running flags, frame indices, RISC/data-buffer pointers, and wait queues inside `cx25821_video_out_data` and the audio fields of `cx25821_dev`.

## State And Persistence
All state is volatile kernel driver state. Persistent hardware-facing state lives in PCI registers, SRAM channel command/CDT areas, DMA buffers, and attached decoder/tuner I2C devices while the driver is loaded. The header's `_audio*` and `vid_out_data[]` fields track stream progress, file/status flags, frame counters, and DMA allocations; mistakes in cleanup can leave stale coherent memory, mapped pages, or running DMA. The `channels[MAX_VID_CHANNEL_NUM]` array is fixed-size, with comments distinguishing the maximum configured channels from currently capture-only channels.

## Dependencies And Integration Points
The file integrates the Linux PCI, I2C, interrupt, mutex, V4L2 device/control, videobuf2-v4l2, and videobuf2-dma-sg APIs. It depends on local register/SRAM/audio headers: `cx25821-reg.h`, `cx25821-medusa-reg.h`, `cx25821-sram.h`, and `cx25821-audio.h`. Cross-file dependencies include board definitions, SRAM channel tables, I2C implementation, Medusa decoder programming, buffer/RISC helpers, ALSA integration via `struct snd_card *card`, and V4L2 video node registration.

## Risks And Test Signals
Important risks are macro fragility from implicit `dev`, fixed-size board/channel arrays, duplicated capture/output state with manual DMA ownership, and many integer fields representing hardware state without type-level constraints. RISC and SRAM helpers must preserve alignment, FIFO line counts, and DMA lifetime rules. Useful test signals are successful module probe/unprobe without leaks, V4L2 node enumeration for every expected channel, streaming start/stop on multiple channels, TV norm and control changes reaching Medusa decoders, IRQ error-path logging, and DMA API/debug checks under capture and upstream output workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/Kconfig

## Purpose
Defines the kernel configuration surface for the Conexant 2388x cx88 media driver family. It separates the common analog/video driver, DMA audio ALSA support, Blackbird hardware MPEG encoder support, DVB/ATSC support, optional VP-3054 secondary I2C support, and the shared MPEG transport helper module.

## Important APIs, Types, And Data
The public API is Kconfig symbols: `VIDEO_CX88`, `VIDEO_CX88_ALSA`, `VIDEO_CX88_BLACKBIRD`, `VIDEO_CX88_DVB`, `VIDEO_CX88_ENABLE_VP3054`, `VIDEO_CX88_VP3054`, and `VIDEO_CX88_MPEG`. `VIDEO_CX88` is the base tristate and selects common V4L2/I2C/tuner/eeprom/vb2 dependencies. ALSA, Blackbird, and DVB features are separate tristates layered on the base symbol. `VIDEO_CX88_MPEG` is an internal helper selected when either DVB or Blackbird is enabled.

## Control Flow
There is no runtime control flow, but the dependency graph determines which source files are built and which attach paths can run. Enabling base cx88 builds the common and analog video modules. Enabling ALSA adds PCI function-1 audio capture. Enabling Blackbird adds cx23416 MPEG encoder support and selects `VIDEO_CX2341X`. Enabling DVB selects `VIDEOBUF2_DVB` and optionally pulls in the many demodulator/tuner frontend modules when `MEDIA_SUBDRV_AUTOSELECT` is active. VP3054 support is gated by DVB and MT352 availability.

## State And Persistence
Kconfig choices persist in the kernel build configuration and determine module availability, autoload aliases, and symbol dependencies. There is no runtime state in this file. The most important state effect is that a board with both DVB and Blackbird hardware needs `VIDEO_CX88_MPEG` so the shared cx8802 transport layer is present.

## Dependencies And Integration Points
The base driver depends on `VIDEO_DEV`, `PCI`, `I2C`, and `RC_CORE`; it selects `I2C_ALGOBIT`, `VIDEOBUF2_DMA_SG`, `VIDEO_TUNER`, `VIDEO_TVEEPROM`, and optionally `VIDEO_WM8775`. ALSA depends on `SND` and selects `SND_PCM`. DVB depends on `DVB_CORE` and optionally selects frontend modules such as MT352, ZL10353, OR51132, CX22702, LGDT330X, NXT200X, CX24123, ISL6421, S5H1411, CX24116, STV0299, STV0288, STB6000, STV0900, STB6100, DS3000, TS2020, and simple tuners.

## Risks And Test Signals
The main risks are missing optional frontend selects, dependency drift when source files include new frontend headers, and configurations where a board is detected but its demod/tuner module was not built. Test signals are `allyesconfig`/`allmodconfig` builds, targeted minimal configs for analog-only, ALSA, Blackbird, DVB, and VP3054 cards, and module-load tests that confirm declared module names (`cx8800`, `cx88-alsa`, `cx88-blackbird`, `cx88-dvb`) are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/Makefile

## Purpose
Builds the cx88 driver modules and maps Kconfig symbols to their object files. It keeps the common cx88 core separate from analog video, cx8802 MPEG transport, ALSA audio, Blackbird MPEG encoder, DVB, and optional VP3054 I2C glue.

## Important APIs, Types, And Data
The make variables define module composition: `cx88xx-objs` contains `cx88-cards.o`, `cx88-core.o`, `cx88-i2c.o`, `cx88-tvaudio.o`, `cx88-dsp.o`, and `cx88-input.o`; `cx8800-objs` contains analog video and VBI; `cx8802-objs` contains MPEG transport support. Conditional `obj-$(CONFIG_...)` lines build `cx88xx.o`, `cx8800.o`, `cx8802.o`, `cx88-alsa.o`, `cx88-blackbird.o`, `cx88-dvb.o`, and `cx88-vp3054-i2c.o`.

## Control Flow
There is no runtime flow; build flow follows the kernel kbuild rules. Base cx88 always links common code and analog capture when `CONFIG_VIDEO_CX88` is enabled. The cx8802 transport module appears only when `CONFIG_VIDEO_CX88_MPEG` is set by DVB or Blackbird. ALSA, Blackbird, DVB, and VP3054 compile independently as optional modules that bind to shared exported symbols from `cx88xx` and `cx8802`.

## State And Persistence
The file contributes only build artifacts. Persistent effects are generated `.o` and `.ko` files and module dependency metadata. There is no runtime state.

## Dependencies And Integration Points
The Makefile relies on Kconfig to provide valid symbol combinations. It adds include paths for `drivers/media/tuners` and `drivers/media/dvb-frontends`, which are needed by cx88 board, tuner, and DVB attach code. The object grouping reflects integration contracts: card/core/I2C/audio/input helpers live in the common module, while video, MPEG transport, ALSA, Blackbird, and DVB are separable front ends over shared hardware.

## Risks And Test Signals
Risks are missing objects when new symbols are exported, stale include paths if media frontend layout changes, and accidental module split changes that break symbol resolution. Test signals are kernel builds for every Kconfig combination, `modpost` symbol checks, and module dependency inspection showing optional modules depending on `cx88xx` and, for DVB/Blackbird, `cx8802`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-alsa.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-alsa.c

## Purpose
Implements ALSA PCM capture for the cx2388x audio PCI function (`14f1:8801` and `14f1:8811`). It exposes the cx88 digital/analog-TV audio stream as an ALSA capture device, programs the downstream audio SRAM/RISC DMA path, handles audio interrupts, and provides mixer controls for volume, mute, DAC output, and optional WM8775 ALC.

## Important APIs, Types, And Data
`struct cx88_audio_dev` owns the ALSA card, shared `cx88_core`, PCI device, IRQ, register lock, period counter, DMA sizing, active `cx88_audio_buffer`, and current PCM substream. `struct cx88_audio_buffer` stores bytes-per-line, RISC memory, vmalloc capture buffer, scatterlist, SG length, and page count. The ALSA callback table `snd_cx88_pcm_ops` implements open, close, hw_params, hw_free, prepare, trigger, pointer, and mmap page translation. PCI binding is through `cx88_audio_pci_driver`.

Important functions include `_cx88_start_audio_dma()`, `_cx88_stop_audio_dma()`, `cx8801_irq()`, `cx8801_aud_irq()`, `cx88_alsa_dma_init/map/unmap/free()`, `snd_cx88_hw_params()`, `snd_cx88_card_trigger()`, `snd_cx88_pointer()`, `snd_cx88_pcm()`, mixer get/put helpers, `snd_cx88_create()`, and `cx88_audio_initdev()`.

## Control Flow
Probe creates an ALSA card, enables the PCI function, obtains the shared `cx88_core` with `cx88_core_get()`, sets a 32-bit DMA mask, requests the shared IRQ, creates one capture PCM, adds mixer controls, and registers the card. Opening a substream constrains periods to powers of two and fixes the hardware format to 48 kHz stereo S16_LE. `hw_params` frees any old buffer, computes period and total DMA sizes, allocates a vmalloc_32 buffer, builds a page scatterlist, maps it for DMA, creates a RISC data-buffer program, and patches the final jump to loop with `RISC_IRQ1 | RISC_CNT_INC`.

On `SNDRV_PCM_TRIGGER_START`, `_cx88_start_audio_dma()` disables audio DMA, programs SRAM channel `SRAM_CH25`, sets `MO_AUDD_LNGTH`, resets the GP counter, enables audio interrupt bits, clears stale status, enables PCI audio interrupts, enables the RISC controller, and starts downstream FIFO/RISC DMA. The IRQ handler loops until relevant PCI status is clear or `MAX_IRQ_LOOP` is reached, routes shared core IRQs to `cx88_core_irq()`, and routes audio IRQs to `cx8801_aud_irq()`. Audio IRQ handling acknowledges status, stops DMA on RISC opcode errors, resets the counter on sync errors, and on downstream RISC1 updates `chip->count` from `MO_AUDD_GPCNT` before calling `snd_pcm_period_elapsed()`. Stop disables downstream FIFO/RISC and audio IRQ masks.

## State And Persistence
Runtime state is held in ALSA core objects, `cx88_audio_dev`, the shared `cx88_core`, DMA mappings, coherent RISC memory, and audio control registers. `atomic_t count` is the ALSA position source and depends on the hardware GP counter and period count being a power of two. `substream->runtime->dma_area` points at vmalloc memory, not PCI coherent memory; scatterlist mapping supplies the hardware addresses. Mixer state is mirrored in hardware registers `AUD_VOL_CTL` and `AUD_BAL_CTL`, with shadow writes through `cx_swrite`; optional WM8775 controls are propagated through V4L2 control calls.

## Dependencies And Integration Points
The driver integrates Linux PCI, ALSA PCM/control APIs, vmalloc/scatterlist DMA mapping, V4L2 cx88 shared core helpers, cx88 SRAM/RISC helpers, and optional `wm8775` subdevice controls. It depends on the base cx88 core already describing the board and MMIO region. It deliberately checks `MO_AUD_DMACNTRL` interactions with the common audio DMA path in `cx88-core.c`, because ALSA owns downstream RISC DMA while analog TV audio setup may enable other audio FIFOs.

## Risks And Test Signals
Risks include IRQ storms, stale DMA mappings after failed `hw_params`, period-size assumptions tied to FIFO geometry, race windows between ALSA trigger and shared IRQ handling, and mismatched WM8775/control state. The code has a FIXME asking whether volume put is always called with IRQs enabled. Test signals are ALSA card creation, successful 48 kHz stereo capture, period interrupts advancing monotonically, clean start/stop/reopen cycles, mmap capture, mixer control readback, no DMA API warnings, and no `IRQ loop detected`, sync, or RISC opcode errors under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-alsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-blackbird.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-blackbird.c

## Purpose
Implements support for Blackbird reference-design MPEG encoder cards that combine a cx2388x bridge with a cx23416 hardware MPEG encoder. It loads cx23416 firmware through the cx2388x host port, sends encoder mailbox commands through the cx2341x API layer, exposes a V4L2 MPEG capture node, and coordinates access to shared cx8802 MPEG hardware with DVB users.

## Important APIs, Types, And Data
The file defines Blackbird/cx23416 command enums, firmware size and register constants, host-port register helpers, a `cx2341x_mbox_func` implementation (`blackbird_mbox_func()`), and a `cx8802_driver` named `cx8802_blackbird_driver`. `blackbird_qops` is the vb2 queue implementation for MPEG buffers. `mpeg_fops`, `mpeg_ioctl_ops`, and `cx8802_mpeg_template` define the V4L2 device surface.

Key functions are `host_setup()`, `memory_write/read()`, `register_write/read()`, `blackbird_api_cmd()`, `blackbird_find_mailbox()`, `blackbird_load_firmware()`, `blackbird_initialize_codec()`, `blackbird_codec_settings()`, `blackbird_start_codec()`, `blackbird_stop_codec()`, vb2 queue callbacks, V4L2 ioctl handlers, `cx8802_blackbird_advise_acquire/release()`, `blackbird_register_video()`, and `cx8802_blackbird_probe/remove()`.

## Control Flow
Module init registers the Blackbird mini-driver with cx8802. Probe rejects boards without `CX88_MPEG_BLACKBIRD`, initializes a `cx2341x_handler`, adds shared video controls, sets up the host port, attempts codec initialization, applies the current TV norm and input mux, initializes a DMA SG vb2 queue, and registers a V4L2 MPEG capture device. Firmware initialization pings the encoder; if ping fails, it resets `MO_SRST_IO`, requests `v4l-cx2341x-enc.fw` via `CX2341X_FIRM_ENC_FILENAME`, verifies exact size and magic, writes firmware dwords over the host memory port, verifies by checksum readback, releases VPU/SPU reset, finds the mailbox signature, and pings/reads version.

Mailbox commands validate a signature word before the mailbox, reject a busy mailbox, mark it busy, write command, timeout, and input words, wait up to one second for firmware completion, read outputs and return code, then clears the flag. Streaming starts by acquiring shared MPEG hardware from cx8802, initializing firmware/codec settings, issuing refresh/initialize/start capture commands, then starting cx8802 DMA from the first active buffer. Stop cancels DMA buffers, sends stop capture, clears cx2341x busy state, releases hardware, and marks queued buffers in error.

V4L2 ioctls constrain format to `V4L2_PIX_FMT_MPEG`, negotiate width/height/field against the current norm, prevent format changes while analog or MPEG queues are busy, forward tuner/frequency/std/input operations to shared cx88 helpers, and restart the codec around frequency changes when already streaming.

## State And Persistence
State is volatile in `struct cx8802_dev`: mailbox address, cx2341x control handler state, MPEG queue, transport packet sizing, current width/height inherited from `cx88_core`, and shared DMA queue. The cx23416 firmware persists only in encoder SDRAM until reset/power loss. Hardware state spans cx88 host-port registers, MPEG transport DMA registers, cx23416 mailbox memory, V4L2 controls, and current tuner/input/std state in `cx88_core`.

## Dependencies And Integration Points
The file depends on the shared cx88 core, cx8802 MPEG DMA helpers, Linux firmware loader, V4L2/vb2 DMA SG, and `media/drv-intf/cx2341x.h`. Board gating is driven by `cx88-cards.c` through `board.mpeg`. Hardware arbitration integrates with cx8802 via `request_acquire`/`request_release`; HVR1300 acquire/release paths switch GPIO ownership between the cx22702 DVB demod and the cx23416 encoder.

## Risks And Test Signals
Risks include firmware absence or wrong image, mailbox corruption or timeouts, host-port read/write timing failures, shared hardware conflicts with DVB, stream stop paths leaving queued buffers or busy controls inconsistent, and only one explicit board-specific acquire path. Test signals are firmware upload success, version logging, `/dev/video*` MPEG node registration, `VIDIOC_STREAMON` producing MPEG packets, clean `VIDIOC_STREAMOFF`, format/frequency changes while idle, expected `-EBUSY` while queues are active, and successful arbitration on HVR1300-class shared boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-blackbird.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-cards.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-cards.c

## Purpose
Provides cx88 board identification, static board configuration, PCI subsystem matching, EEPROM decoding, board-specific GPIO/reset/tuner setup, tuner callback routing, PCI quirks, MMIO resource acquisition, and allocation of the shared `cx88_core`. It is the hardware knowledge base that maps generic cx2388x chips to concrete analog, radio, DVB, and Blackbird board layouts.

## Important APIs, Types, And Data
Static module parameters `card[]`, `tuner[]`, `radio[]`, `latency`, and `disable_ir` allow override of autodetection, tuner type, radio tuner type, PCI latency, and IR support. `cx88_boards[]` is a large `struct cx88_board` table describing board names, tuner/radio types and addresses, TDA9887 config, audio chip, I2S input, analog/radio input muxes, GPIO values, MPEG capabilities, and multi-frontend counts. `cx88_subids[]` maps PCI subsystem vendor/device IDs to board IDs.

Exported or cross-file functions include `cx88_tuner_callback()`, `cx88_setup_xc3028()`, `cx88_get_resources()`, and `cx88_core_create()`. Internal helpers include `leadtek_eeprom()`, `hauppauge_eeprom()`, `gdi_eeprom()`, board-specific tuner reset callbacks for XC2028/XC4000/XC5000, `dvico_fusionhdtv_hybrid_init()`, `cx88_card_setup_pre_i2c()`, `cx88_card_setup()`, and `cx88_pci_quirks()`.

## Control Flow
`cx88_core_create()` allocates and initializes the shared core, registers a `v4l2_device`, initializes video and audio control handlers, reserves and maps PCI MMIO, resolves board number from module override or PCI subsystem ID, copies the board descriptor, fills default frontend count for DVB boards, applies tuner/radio overrides, resets hardware, runs pre-I2C board GPIO setup, initializes I2C, optionally instantiates tuner subdevices, performs board-specific setup, initializes IR unless disabled, and returns the core to callers.

Board setup is layered. Pre-I2C setup brings hidden demods/tuners out of reset or selects GPIO states needed for I2C visibility. Post-I2C setup reads EEPROMs for Hauppauge, GDI, and Leadtek boards; toggles board-specific reset pins; sends special I2C init sequences for DViCO hybrid hardware; configures radio and TV tuners through `call_all(core, tuner, s_type_addr, ...)`; applies TDA9887 config; configures XC2028/3028 firmware parameters through `cx88_setup_xc3028()`; and finally places tuners in standby. Tuner callbacks route reset/power commands from tuner and DVB frontend drivers back to board-specific GPIO sequences.

## State And Persistence
The file initializes long-lived shared state in `struct cx88_core`: board number and board descriptor, model, tuner formats, PCI bus/slot, IRQ mask, MMIO pointers, V4L2 control handlers, I2C adapter/client, optional gate control and IR state, and current defaults for width/height/field. Persistent external state is limited to hardware registers, GPIO latch values, I2C-attached tuner/demod state, and PCI configuration bytes such as latency/device-control quirks while the device is active.

## Dependencies And Integration Points
It depends on cx88 register/core declarations, tuner headers (`tea5767.h`, `xc4000.h`), V4L2 I2C subdevice helpers, tveeprom parsing, kernel PCI quirk flags, and board IDs defined in the shared cx88 header. It feeds all other cx88 modules: analog video uses input mux/GPIO/tuner data, ALSA uses shared core/audio chip state, DVB uses `board.mpeg`, `num_frontends`, tuner callbacks, and gate control, and Blackbird uses `CX88_MPEG_BLACKBIRD` capability plus shared hardware arbitration.

## Risks And Test Signals
Risks are dominated by board-table accuracy: wrong GPIOs can hide I2C devices, reset the wrong demod, mute audio, or route the wrong RF/input path. EEPROM parsing and module overrides can silently change tuner selection. Multi-function boards such as HVR1300/HVR3000/HVR4000 have fragile GPIO interactions between DVB and Blackbird or between DVB-S and DVB-T. Test signals are correct autodetection logs, successful I2C probe without touching excluded RTC/IR addresses, expected tuner/demod attachments, working analog inputs/radio/audio routes, board-specific DVB frontend registration, IR operation unless disabled, and clean core refcount teardown across multiple PCI functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-cards.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-core.c

## Purpose
Implements the shared cx2388x core services used by analog video, ALSA, MPEG, DVB, input, and board modules. It builds RISC DMA programs, defines SRAM FIFO layouts, programs SRAM channels, provides debug/IRQ helpers, resets and shuts down hardware, computes scaling and TV norm register values, manages common analog audio DMA, initializes video devices, and owns shared-core reference management.

## Important APIs, Types, And Data
Exported APIs include `cx88_risc_buffer()`, `cx88_risc_databuffer()`, `cx88_sram_channels[]`, `cx88_sram_channel_setup()`, `cx88_sram_channel_dump()`, `cx88_print_irqbits()`, `cx88_core_irq()`, `cx88_wakeup()`, `cx88_shutdown()`, `cx88_reset()`, `cx88_set_scale()`, `cx88_start_audio_dma()`, `cx88_stop_audio_dma()`, `cx88_set_tvnorm()`, `cx88_vdev_init()`, `cx88_core_get()`, and `cx88_core_put()`. Module parameters `core_debug`, `nicam`, and `nocomb` adjust logging, audio assumptions, and comb filtering.

The SRAM layout table maps channels 21-28/27 to video Y/packed, U, V, VBI, audio in/out, MPEG, and audio RDS FIFOs with command/control/CDT/fifo register addresses. Global `cx88_devlist`, `cx88_devcount`, and `devlist` mutex maintain one shared core per PCI bus/slot across multiple PCI functions.

## Control Flow
RISC buffer creation estimates worst-case instruction storage, allocates coherent memory, and writes field/data transfer instructions through `cx88_risc_field()`. That helper walks DMA scatterlists line by line, emits resync/write instructions, splits lines at SG boundaries, optionally emits periodic IRQ/count increments, and leaves room for the caller to patch a loop jump. SRAM setup aligns bytes-per-line to 8 bytes, chooses up to six FIFO lines, writes CDT entries, programs command descriptors, and fills pointer/count registers.

`cx88_reset()` shuts down DMA and interrupts, clears status, initializes all SRAM channels with safe defaults, configures input/filter/FIFO/AGC defaults, resets onboard parts through `MO_SRST_IO`, and returns hardware to a baseline. `cx88_set_tvnorm()` refuses changes while video/VBI/MPEG queues are busy, computes PLL/subcarrier/AGC/HTOTAL/VBI/scaling values for PAL/NTSC/SECAM variants, calls `set_tvaudio()`, notifies I2C video subdevices, and grabs chroma AGC control for SECAM. `cx88_set_scale()` programs horizontal/vertical delay, scale, active size, and filter bits based on norm, field mode, input type, requested dimensions, and `nocomb`.

Audio helpers set up shared analog audio FIFOs unless ALSA downstream RISC DMA is already active. Shared IRQ handling currently dispatches IR sample interrupts and prints unexpected bits. Buffer wakeup timestamps and completes the first active vb2 buffer. `cx88_core_get()` either finds an existing core for the same PCI slot and reserves the MMIO resource for the requesting function, or calls `cx88_core_create()`. `cx88_core_put()` releases the function resource and destroys the core only when the refcount reaches zero.

## State And Persistence
Shared state is in `cx88_core`: MMIO mapping, board/tuner/input/tvnorm, current dimensions/field, V4L2 device/control handlers, I2C/IR state, DMA queues owned by higher layers, and refcount membership in `cx88_devlist`. Hardware state persists in cx2388x registers and SRAM command/FIFO areas while the device is active. RISC memory is coherent DMA memory owned by callers and freed by buffer finish paths. `cx88_start_audio_dma()` can leave audio FIFOs running for analog audio detection/playthrough, unless ALSA owns downstream RISC mode.

## Dependencies And Integration Points
This file is central to all cx88 modules. It depends on the shared `cx88.h` register macros, V4L2/vb2, PCI resource management, I2C subdevice notification via `call_all()`, audio standard helpers from `cx88-tvaudio.c`, IR helpers from `cx88-input.c`, and board creation from `cx88-cards.c`. ALSA uses `SRAM_CH25` and `cx88_risc_databuffer()`, DVB/Blackbird use MPEG SRAM and buffer completion paths through cx8802, and analog video uses video/VBI RISC and scaling/norm helpers.

## Risks And Test Signals
Risks include RISC size underestimation, SG-boundary mistakes, FIFO line counts below hardware requirements, TV norm register regressions, racey norm changes if busy checks miss a queue, core refcount/resource leaks across PCI functions, and audio DMA conflicts between ALSA and analog audio paths. Test signals are DMA capture across packed/planar/VBI/audio/MPEG users, `cx88_sram_channel_dump()` consistency during debug, no RISC bus-error IRQs, correct image geometry for multiple norms/fields/sizes, stable audio after norm/input changes, and clean probe/remove ordering for video, audio, DVB, and Blackbird modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-dsp.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-dsp.c

## Purpose
Provides software stereo/SAP detection for cx88 analog TV audio by sampling the audio RDS FIFO and applying fixed-point frequency detection. It supplements the TV audio code by identifying mono, stereo, and dual-language subchannels for A2/A2M/EIAJ-style systems, with BTSC stubs present but not implemented.

## Important APIs, Types, And Data
The exported API is `cx88_dsp_detect_stereo_sap(struct cx88_core *core)`. Internal helpers include `int_cos()` for fixed-point cosine approximation, `int_goertzel()` for tone power, `freq_magnitude()`, `noise_magnitude()`, `detect_a2_a2m_eiaj()`, `detect_btsc()`, and `read_rds_samples()`. Constants define baseband frequencies for A2, A2M, EIAJ, BTSC dual/SAP reference tones, and a noise band. Module parameter `dsp_debug` controls logging.

## Control Flow
Detection first checks that the audio RDS FIFO is enabled in `MO_AUD_DMACNTRL`, that RDS input is enabled in `AUD_CTL`, and that at least 500 ms have passed since the last audio standard change. It then reads a circular set of 16-bit samples from `SRAM_CH27` based on the current FIFO pointer, using all but one FIFO line. Depending on `core->tvaudio`, it runs A2/A2M/EIAJ detection or BTSC detection. A2-style detection computes carrier, stereo, dual, and noise magnitudes using Goertzel filters, compares thresholds, and returns V4L2 tuner subchannel flags or mono. BTSC currently returns `UNSET`.

## State And Persistence
The file keeps no persistent private state. It reads volatile samples from the hardware SRAM audio RDS FIFO and relies on `core->tvaudio` and `core->last_change`. Temporary sample buffers are allocated with `kmalloc_objs()` and freed before returning. Detection results are returned to callers and are not stored here.

## Dependencies And Integration Points
It depends on cx88 core/register definitions, `cx88_sram_channels[SRAM_CH27]`, audio DMA setup from `cx88_start_audio_dma()`, and TV audio mode selection from `cx88_set_tvnorm()`/`cx88-tvaudio.c`. Results integrate with V4L2 tuner reporting through flags such as `V4L2_TUNER_SUB_STEREO`, `V4L2_TUNER_SUB_LANG1`, `V4L2_TUNER_SUB_LANG2`, and `V4L2_TUNER_SUB_MONO`.

## Risks And Test Signals
Risks include unvalidated frequency constants, integer approximation error, FIFO sampling assumptions, false positives from noise thresholds, unsupported BTSC SAP/stereo, and dependence on RDS FIFO enablement. Comments note several frequencies are from a reference driver and probably need testing/adjustment. Test signals are correct stereo/dual/mono detection on known PAL BG/DK, A2M, and EIAJ broadcasts, stable results after the 500 ms settling period, no allocation failures under polling, and no regressions in unsupported modes where `UNSET` is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-dvb.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-dvb.c

## Purpose
Implements DVB/ATSC transport-stream support for cx2388x cards using the cx8802 MPEG DMA engine. It allocates vb2 DVB frontend queues, attaches board-specific demodulators and tuners, controls I2C gates and shared hardware access, configures transport-stream parameters, handles LNB voltage/tone quirks, and registers DVB adapters/frontends for a large matrix of cx88 boards.

## Important APIs, Types, And Data
The module registers a `cx8802_driver` named `cx8802_dvb_driver` with type `CX88_MPEG_DVB`. Queue operations are in `dvb_qops`, backed by `queue_setup()`, `buffer_prepare()`, `buffer_finish()`, `buffer_queue()`, `start_streaming()`, and `stop_streaming()`. Important hardware arbitration helpers are `cx88_dvb_bus_ctrl()`, `cx88_dvb_gate_ctrl()`, `cx8802_dvb_advise_acquire()`, and `cx8802_dvb_advise_release()`. `dvb_register()` is the central board switch that attaches frontends and tuners.

The file contains many frontend configuration structures for MT352, ZL10353, MB86A16, CX22702, OR51132, LGDT330X, NXT200X, CX24123, S5H1409, S5H1411, XC5000, XC2028/3028, XC4000, CX24116, DS3000/TS2020, STV0900/STB6100, STV0299, STV0288/STB6000, and Samsung-specific STV0299 tuner/LNB control. Module parameters include `debug`, `dvb_buf_tscnt`, and DVB adapter numbering.

## Control Flow
Probe rejects boards without `CX88_MPEG_DVB`, probes optional VP3054 secondary I2C support, sets default TS generator control, allocates one or more frontends according to `core->board.num_frontends`, initializes one vb2 queue per frontend, names the DVB instances, and calls `dvb_register()`. Queue setup uses 188-byte TS packets grouped by four and a configurable TS packet count. Streaming starts cx8802 DMA from the first active MPEG buffer; stop cancels DMA and returns active buffers with error.

`dvb_register()` first verifies I2C availability, sets `core->gate_ctrl`, selects frontend zero, and switches on `core->boardnr`. Each case attaches the required demodulator, optional tuner, optional PLL, optional LNB controller, and board-specific operation overrides. Some boards try alternative demods for hardware revisions, disable I2C gate control so tuners remain reachable, attach XC3028/XC4000 through helper functions after opening gates, or configure multi-frontend shared DVB-S/S2 plus DVB-T devices. After successful attachments, frontend callbacks and `ts_bus_ctrl` are set, tuners are put in standby, and `vb2_dvb_register_bus()` registers adapters/frontends, optionally in shared-MFE mode.

Runtime bus acquisition flows through `cx88_dvb_bus_ctrl()`, which records the active frontend id, asks cx8802 for shared MPEG hardware, and releases it when done. Advise-acquire GPIO logic switches shared boards: HVR1300 toggles between cx23416 and cx22702 bus ownership, HVR3000/HVR4000 switch between DVB-S/S2 parallel TS and DVB-T serial TS by resetting/tri-stating demods, and WinFast DTV2000H Plus selects RF input for DVB-T.

## State And Persistence
State is held in `struct cx8802_dev`: `frontends`, active frontend id, `ts_gen_cntrl`, MPEG DMA queue, optional VP3054 adapter, and PCI/core pointers. Each `vb2_dvb_frontend` holds its DVB frontend and vb2 queue. Hardware state persists in demod/tuner I2C registers, cx88 GPIOs, TS generator control, LNB voltage/tone GPIO or I2C state, and MPEG DMA registers while active. On registration failure, the code deallocates frontends and clears `core->gate_ctrl`; remove unregisters the DVB bus and VP3054 I2C.

## Dependencies And Integration Points
The file depends on the cx88 core/cx8802 MPEG layer, V4L2/vb2 DVB helpers, many DVB frontend and tuner drivers, `dvb-pll`, board configuration from `cx88-cards.c`, tuner callback `cx88_tuner_callback()`, XC3028 setup `cx88_setup_xc3028()`, and optional `cx88-vp3054-i2c`. It shares hardware with Blackbird on some boards through cx8802 arbitration and shares the I2C bus with analog tuner subdevices through gate control.

## Risks And Test Signals
Risks include missing frontend modules, wrong board switch cases, I2C gate mismanagement, multi-frontend active-id mistakes, LNB voltage overrides not chaining previous operations, TS serial/parallel parameter mismatches, and cleanup after partial attach failures. Some board cases deliberately disable gate control or use fallback demods, making regression risk board-specific. Test signals are successful frontend registration for every supported board family, tuning/lock on DVB-T/ATSC/DVB-S/S2 as appropriate, valid TS packet flow without continuity errors, correct MFE switching on HVR3000/HVR4000, working LNB voltage/tone controls, successful VP3054 boards when configured, and clean unregister/reprobe without leaked frontends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-dvb.c -->
