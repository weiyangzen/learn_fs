# subset-b-004128 research

This grouped report covers SOLO6x10 PCI video/audio support and TTPci SAA7146 budget DVB modules. Each section preserves the original source path so reconciliation can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-g723.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-g723.c

## Purpose
`solo6x10-g723.c` exposes the SOLO6x10 hardware G.723 audio encoder as an ALSA capture card, mapping each video channel to one mono 8 kHz u8 PCM capture substream.

## Important APIs, Types, and Functions
`struct solo_snd_pcm` stores per-open capture state, a small coherent bounce buffer, and the owning `solo_dev`. `solo_g723_config()` programs the audio sample clock, FDMA base, interrupt cadence, and I2S/multi-channel mode. ALSA callbacks `snd_solo_pcm_open()`, `close()`, `trigger()`, `pointer()`, and `copy()` implement the PCM device, while `solo_g723_isr()` advances active substreams. Mixer callbacks use `tw28_get_audio_gain()` and `tw28_set_audio_gain()` for per-camera capture volume.

## Control Flow
Initialization creates an ALSA card named from the V4L2 display node, registers one capture PCM with `nr_chans` substreams, adds a multi-count "Capture Volume" control, registers the card, and enables the SOLO audio block. Opening a substream allocates a coherent 48-byte DMA buffer and swaps the substream chip pointer from the global `solo_dev` to per-open state. Start/stop trigger transitions maintain `snd_users`; the first active user enables `SOLO_IRQ_G723` and the last disables it. On each audio interrupt, active substreams receive `snd_pcm_period_elapsed()`. ALSA copy requests use P2M DMA to fetch 48-byte channel slices out of the 32-page hardware G.723 ring and copy them into the user iterator.

## State and Persistence
Runtime state is volatile: ALSA card/PCM objects, `snd_users`, per-open `solo_snd_pcm.on`, and the hardware audio registers. No audio data or settings are persisted beyond TW28 register state in hardware.

## Dependencies and Integration Points
The file depends on ALSA core/PCM/control APIs, SOLO register helpers, P2M DMA from `solo6x10-p2m.c`, SDRAM offsets from `solo6x10-offsets.h`, and TW28 audio gain helpers from `solo6x10-tw28.c`.

## Risks and Edge Cases
The copy path assumes ALSA requests are aligned to `G723_FRAMES_PER_PAGE`; partial periods would copy nothing for the fractional remainder. `solo_g723_isr()` walks substreams through mutable chip pointers, so open/close and interrupt ordering depends on ALSA stream locking. A P2M timeout or mapping error propagates as a failed PCM copy.

## Test Signals
Useful checks are ALSA card registration, one capture substream per video channel, interrupt enable only while streams are running, advancing PCM pointers across all 32 pages, successful capture reads for every channel, volume control writes reflected in TW28 gain registers, and clean shutdown disabling audio control and `SOLO_IRQ_G723`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-g723.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-gpio.c

## Purpose
`solo6x10-gpio.c` configures board GPIO lines for video reset, internal video functions, relay outputs, and sensor inputs, optionally exporting a 24-line gpiolib chip.

## Important APIs, Types, and Functions
`solo_gpio_mode()` programs the two SOLO GPIO configuration registers, handling low GPIOs as two-bit modes and high GPIOs as one-bit sensor direction plus enable bits. `solo_gpio_set()` and `solo_gpio_clear()` update `SOLO_GPIO_DATA_OUT`. `solo_gpio_config()` applies the board default reset/relay/input layout. Under `CONFIG_GPIOLIB`, `solo_gpiochip_get_direction()`, `solo_gpiochip_get()`, and `solo_gpiochip_set()` implement a `gpio_chip` whose logical offset 0 maps to hardware GPIO8.

## Control Flow
Initialization always calls `solo_gpio_config()`: pulse GPIO4/5 for video reset, set GPIO0-3 to internal video mode, set GPIO8-15 as relay outputs cleared low, and set GPIO16-31 as inputs. If gpiolib is enabled, a dynamic-base chip named `solo6x10_gpio` is registered with 24 exported lines. Exit removes the chip, clears reset lines, and reapplies the default hardware configuration.

## State and Persistence
State lives in the SOLO GPIO registers and the embedded `gpio_chip` inside `struct solo_dev`. There is no persistent storage. Output levels are reset by init/exit and otherwise reflect hardware register state.

## Dependencies and Integration Points
The file integrates with the PCI device via `solo_dev`, kernel gpiolib when enabled, and the rest of the driver through board reset sequencing before TW28 decoder initialization.

## Risks and Edge Cases
The first eight hardware GPIOs are intentionally hidden because GPIO0-3 and reset lines are board-internal. There is no explicit lock around read-modify-write register updates, so concurrent gpiolib set operations could race if multiple callers manipulate relays at once. `solo_gpiochip_get_direction()` returns `-1` for unsupported modes rather than a conventional errno.

## Test Signals
Verify video decoders reset during probe, relay GPIO offsets 0-7 drive hardware GPIO8-15, input offsets 8-23 read GPIO16-31, gpiolib registration/removal succeeds, and exit leaves board-internal lines in a known reset/default state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-i2c.c

## Purpose
`solo6x10-i2c.c` implements two Linux I2C adapters backed by the SOLO6x10 on-chip IIC controller, used mainly for Techwell TW28xx decoders and SAA7128 video encoder access.

## Important APIs, Types, and Functions
Convenience helpers `solo_i2c_readbyte()` and `solo_i2c_writebyte()` issue common register transactions. The hardware state machine is driven by `solo_i2c_start()`, `solo_i2c_flush()`, `solo_i2c_handle_read()`, `solo_i2c_handle_write()`, and `solo_i2c_stop()`. `solo_i2c_isr()` advances transactions from the top-level IRQ handler. `solo_i2c_master_xfer()` is the Linux I2C algorithm entry point and serializes transfers through `i2c_mutex`.

## Control Flow
`solo_i2c_init()` enables the controller with a fixed prescale, initializes wait state, and registers two adapters. A master transfer identifies which adapter is being used, stores the message array in `solo_dev`, enables `SOLO_IRQ_IIC`, emits the address phase, and waits up to half a second for `IIC_STATE_STOP`. Each hardware interrupt checks error bits, reads or writes the next byte, starts the next message when needed, or stops and wakes the waiter. Completion returns the count of messages consumed.

## State and Persistence
All in-flight transfer state is stored in `struct solo_dev`: `i2c_state`, `i2c_id`, current message pointer, message count, byte index, wait queue, and mutex. There is no persistent state. Hardware IIC control/data registers are reset around every transfer.

## Dependencies and Integration Points
This file depends on Linux I2C core, SOLO IRQ mask helpers, `SOLO_IIC_*` register definitions, and wait queue scheduling. TW28 setup/control and SAA7128 programming rely on these adapters.

## Risks and Edge Cases
The source itself warns that the implementation does too much in interrupt context and does not use hardware busy/status as robustly as it should. `solo_i2c_readbyte()` ignores `i2c_transfer()` failure and returns an uninitialized byte on hard failure. Interrupted or timed-out waits return a partial message count rather than a negative errno, which can mask bus problems for callers.

## Test Signals
Test adapter registration, TW and SAA bus transactions, repeated-start read sequences, `I2C_M_NOSTART` behavior, timeout/error handling, IRQ disable and wakeup on stop, and cleanup after partial adapter registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-jpeg.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-jpeg.h

## Purpose
`solo6x10-jpeg.h` provides static JPEG header data and quantization tables used by the SOLO encoder V4L2 path to prepend complete MJPEG frames to hardware JPEG entropy payloads.

## Important APIs, Types, and Functions
The header exports `jpeg_header[]`, `SOF0_START`, `DQT_START`, `DQT_LEN`, and `jpeg_dqt[4][DQT_LEN]`. There are no functions. `solo_update_mode()` in `solo6x10-v4l2-enc.c` modifies SOF0 dimensions and copies one quantization table according to `solo_g_jpeg_qp()`.

## Control Flow
The base header is copied into each `solo_enc_dev` during encoder allocation. Whenever video standard, format, or JPEG quality changes, encoder code patches width/height bytes and replaces the DQT segment before `buf_finish()` copies the header into the beginning of user buffers.

## State and Persistence
The arrays are read-only static data. Mutable state is in each encoder instance's `jpeg_header` and `jpeg_len`; no persistent data exists.

## Dependencies and Integration Points
The constants are tightly coupled to byte offsets expected by `solo6x10-v4l2-enc.c`. The hardware only supplies compressed JPEG payload data, so these software tables are required to make captured MJPEG buffers decodable by userspace.

## Risks and Edge Cases
`SOF0_START` and `DQT_START` are hard-coded offsets into `jpeg_header[]`; changing the base header without adjusting offsets would corrupt emitted MJPEG. The QP index must remain in range 0-3, as enforced by the JPEG QP helpers outside this header.

## Test Signals
Validate MJPEG buffers start with SOI/JFIF-compatible markers, dimensions match CIF/D1 and PAL/NTSC modes, DQT bytes change with JPEG QP controls, and common decoders can parse captured MJPEG frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-jpeg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-offsets.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-offsets.h

## Purpose
`solo6x10-offsets.h` defines the SOLO SDRAM memory map used by display capture, encoder OSD, motion detection, G.723 audio, raw capture pages, encoder reference frames, MPEG4/H.264 output, and JPEG output.

## Important APIs, Types, and Functions
The header is macro-only. Key macros include `SOLO_DISP_EXT_ADDR/SIZE`, `SOLO_EOSD_EXT_ADDR_CHAN()`, `SOLO_MOTION_EXT_ADDR()`, `SOLO_G723_EXT_ADDR()`, `SOLO_CAP_EXT_ADDR()`, `SOLO_CAP_EXT_SIZE()`, `SOLO_EREF_EXT_ADDR()`, `SOLO_MP4E_EXT_ADDR/SIZE()`, `SOLO_JPEG_EXT_ADDR/SIZE()`, and `SOLO_SDRAM_END()`.

## Control Flow
There is no runtime control flow here. Callers evaluate the macros after `solo_dev` has type, channel count, and detected `sdram_size`. `solo_p2m_init()` validates `SOLO_SDRAM_END()` against detected SDRAM before higher-level capture/encode features rely on the map.

## State and Persistence
The layout is deterministic from `solo_dev->type`, `nr_chans`, and `sdram_size`. It does not persist state, but it defines where hardware and software share all frame/audio buffers.

## Dependencies and Integration Points
The macros are consumed by P2M DMA, live V4L2 display, encoder V4L2, G.723 audio, motion detection, and OSD code. They depend on constants from `solo6x10.h` such as `SOLO_DEV_6010` and channel counts.

## Risks and Edge Cases
The map uses `clamp()` to reserve minimum MPEG/JPEG regions, so small SDRAM devices can have constrained encoder space. `__SOLO_JPEG_MIN_SIZE` is defined twice with the same value, which is harmless but easy to trip over during maintenance. Any change to channel count or SDRAM detection can shift later regions and break DMA if not validated.

## Test Signals
Check `solo_p2m_init()` accepts the detected SDRAM size, display/audio/encoder offsets do not overlap, MPEG and JPEG wrap logic handles the computed sizes, and 32 MB cards still reserve a usable capture and encode layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-p2m.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-p2m.c

## Purpose
`solo6x10-p2m.c` implements the SOLO PCI-to-memory DMA engine abstraction used to move data between host memory and SOLO SDRAM, and it detects usable on-card SDRAM size at probe time.

## Important APIs, Types, and Functions
Module parameters `multi_p2m` and `desc_mode` opt into multiple channels and descriptor mode on SOLO6010. Public APIs are `solo_p2m_dma()`, `solo_p2m_dma_t()`, `solo_p2m_fill_desc()`, and `solo_p2m_dma_desc()`. Interrupt paths are `solo_p2m_isr()` and `solo_p2m_error_isr()`. `solo_p2m_test()` writes/reads SDRAM patterns, while `solo_p2m_init()` configures engines and detects memory size.

## Control Flow
Single-buffer callers map CPU memory with the PCI DMA API, fill a descriptor, and delegate to `solo_p2m_dma_desc()`. The descriptor path chooses P2M channel 0 unless multi-channel 6010 mode is enabled, locks that channel, starts hardware descriptor mode for eligible multi-descriptor transfers or manually starts descriptor 1, waits for completion, handles errors/timeouts, stops the engine, restores config, and unlocks. The ISR either completes a transfer or programs the next descriptor in manual mode. Init configures all P2M channels, enables their IRQs, then probes 128/64/32 MB SDRAM configurations by resetting the chip and verifying test patterns at high addresses.

## State and Persistence
Each `solo_p2m_dev` stores a mutex, completion, descriptor cursor, descriptor pointer, and error flag. `solo_dev` stores detected `sdram_size`, timeout count, P2M wait duration, and the atomic channel counter. State is volatile and reset at driver initialization.

## Dependencies and Integration Points
The file depends on PCI DMA mapping, SOLO P2M and SDRAM control registers, IRQ dispatch from the core driver, and SDRAM layout macros. V4L2 display, V4L2 encoder, ALSA G.723, OSD, and motion code depend on these DMA APIs.

## Risks and Edge Cases
Descriptor arrays are one-based in the call convention (`desc[1]` is first), which is unusual and easy to misuse. SOLO6110 is forced to channel 0 and manual descriptor stepping because nonzero P2M and descriptor mode are known-problematic. P2M init resets memory controller state while probing SDRAM, so ordering relative to other hardware setup is important.

## Test Signals
Validate DMA reads and writes, descriptor and manual modes, wrap-sized encoder transfers, P2M error interrupt completion, timeout accounting, multi-P2M 6010 behavior, 6110 channel-0 restriction, and correct SDRAM size detection including rejection when `SOLO_SDRAM_END()` exceeds memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-p2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-regs.h

## Purpose
`solo6x10-regs.h` is the central register map and bitfield definition header for the SOLO6010/SOLO6110 PCI video/audio processor.

## Important APIs, Types, and Functions
The header defines MMIO offsets and field macros for system clock/reset, DMA and SDRAM, IRQ status/masks, P2M engines, video input/output, display windows, motion detection, capture, video encoder/decoder queues, GPIO, IIC, UART, timers, watchdog, and audio. It includes `solo6x10-offsets.h` and Linux bit operations.

## Control Flow
There is no executable control flow. Runtime code uses these macros through `solo_reg_read()` and `solo_reg_write()` from `solo6x10.h` to program hardware blocks.

## State and Persistence
The header does not own state, but every defined register corresponds to volatile device state. Some macros distinguish SOLO6110-only fields such as extended JPEG/MPEG size bits, H.264-related behavior, and timer LSB support.

## Dependencies and Integration Points
All SOLO subsystem files depend on this header for register names and bit packing. The definitions are the integration contract between V4L2 display/encoder, ALSA, I2C, GPIO, P2M DMA, motion, OSD, and the top-level PCI driver.

## Risks and Edge Cases
Bitfield macros mostly shift unchecked input values, so callers must validate ranges. Register comments include undocumented hardware behavior and typos inherited from datasheets, making empirical tests important. Changing a shared macro can affect unrelated subsystems because the header is global to the driver.

## Test Signals
Build coverage across all SOLO files, successful probe on 6010 and 6110 hardware, correct IRQ masks, functional P2M/I2C/GPIO/audio/video blocks, and regression tests around 6110-only fields are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-tw28.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-tw28.c

## Purpose
`solo6x10-tw28.c` detects and configures Techwell TW2815/TW2864/TW2865 video/audio decoder chips and the SAA7128 output encoder used on SOLO6x10 cards, and exposes decoder controls to V4L2/ALSA code.

## Important APIs, Types, and Functions
Large PAL/NTSC register templates feed `tw2865_setup()`, `tw2864_setup()`, and `tw2815_setup()`. `solo_tw28_init()` probes chip IDs and performs setup. `tw28_get_video_status()`, `tw28_has_sharpness()`, `tw28_set_ctrl_val()`, `tw28_get_ctrl_val()`, `tw28_get_audio_gain()`, and `tw28_set_audio_gain()` are exported to other SOLO files. `saa712x_setup()` programs the video output encoder.

## Control Flow
Initialization scans one TW chip per four video channels over the SOLO TW I2C adapter, classifies each chip by ID registers, verifies the expected chip count, configures SAA7128 PAL/NTSC output, and writes the appropriate decoder template for each chip. TW2864/TW2865 setup modifies template fields for channel count, cascade/ALINK/IRQ mode, and chip address before skipping read-only registers and writing with verification. TW2815 setup builds active timing fields, configures audio routing, writes per-channel decoder registers, then writes shared SFR audio/control registers.

## State and Persistence
Detected chip masks `tw2865`, `tw2864`, `tw2815`, and `tw28_cnt` live in `struct solo_dev`. Decoder settings are volatile I2C-programmed hardware registers. Picture and audio gain controls persist only while hardware remains powered.

## Dependencies and Integration Points
The file depends on the SOLO I2C adapters, V4L2 control IDs, `solo_dev->video_type` and `nr_chans`, and TW28 register macros from `solo6x10-tw28.h`. Live and encoded V4L2 nodes use video status and picture controls; ALSA uses audio gain controls.

## Risks and Edge Cases
Probe requires all expected decoder chips; partial detection fails the whole init. Template writes rely on magic hardware tables and selective read-only skips. `tw28_set_ctrl_val()` checks chip number against `TW_NUM_CHIP` but assumes channel numbers are otherwise valid. The sharpness path uses a TW286x macro with the chip number where other calls use the on-chip channel, which deserves hardware regression attention.

## Test Signals
Check detection for TW2815, TW2864, TW2865, PAL and NTSC setup, 4/8/16-channel audio/video routing, SAA7128 programming, video loss reporting per channel, V4L2 brightness/contrast/saturation/hue/sharpness controls, and ALSA capture gain changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-tw28.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-tw28.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-tw28.h

## Purpose
`solo6x10-tw28.h` declares TW28xx decoder constants and the control/status API shared between decoder setup, V4L2 capture/encoder code, and ALSA audio code.

## Important APIs, Types, and Functions
The header defines chip addressing (`TW_NUM_CHIP`, `TW_BASE_ADDR`, `TW_CHIP_OFFSET_ADDR()`), status and control register address macros for TW2815 and TW286x families, and prototypes for `solo_tw28_init()`, video control get/set, sharpness capability, audio gain get/set, and video status.

## Control Flow
There is no runtime control flow. Callers include the header to select proper register offsets and call the TW28 helper functions implemented in `solo6x10-tw28.c`.

## State and Persistence
The header does not store state. It describes accessors for volatile decoder hardware state tracked through `struct solo_dev`.

## Dependencies and Integration Points
It includes `solo6x10.h`, so it inherits the full device structure and V4L2 type context. It is consumed by ALSA G.723, live V4L2 display, V4L2 encoder, and TW28 implementation code.

## Risks and Edge Cases
Macros encode different address layouts for TW2815 and TW286x chips. Passing chip numbers where channel numbers are expected, or vice versa, can address the wrong register. Because the header includes the main driver header, include cycles must remain controlled by include guards.

## Test Signals
Compile all users with both `CONFIG_GPIOLIB` states, exercise picture and audio controls on TW2815 and TW286x boards, and confirm video status reads use the correct family-specific status register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-tw28.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-v4l2-enc.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-v4l2-enc.c

## Purpose
`solo6x10-v4l2-enc.c` exposes one encoded V4L2 capture node per SOLO video channel, delivering MPEG4 on SOLO6010, H.264 on SOLO6110, and MJPEG on both.

## Important APIs, Types, and Functions
`struct solo_enc_dev` from `solo6x10.h` is the primary state object, supplemented by local `struct solo_enc_buf`. Format/header logic lives in `solo_update_mode()`, `solo_fill_mpeg()`, `solo_fill_jpeg()`, and `solo_enc_buf_finish()`. DMA scatter-gather transfer construction is handled by `solo_send_desc()`. Hardware queue processing is `solo_enc_v4l2_isr()`, `solo_ring_thread()`, and `solo_handle_ring()`. User-facing operations are V4L2 ioctl callbacks, vb2 queue callbacks, and control handling in `solo_s_ctrl()`.

## Control Flow
Module init for this subsystem allocates a coherent VOP header buffer, creates one encoder device per channel, initializes controls/queues/descriptors, sets encoder bandwidth budget, and starts a shared ring thread with encoder IRQ enabled. Streaming a channel calls `solo_enc_on()`, which updates mode, checks bandwidth, programs GOP/QP/interval/interlace/capture registers, and enables the channel. The ring thread wakes on encoder IRQs or timeout, drains hardware queue entries, fetches VOP headers by P2M DMA, validates offsets, checks motion status, dequeues a vb2 buffer from the matching channel, and DMAs MPEG/JPEG payload into it.

## State and Persistence
Per-channel state includes selected format, mode, frame interval, GOP, QP, OSD text/header buffers, motion mode/thresholds, vb2 active list, descriptor DMA memory, sequence counter, and bandwidth weight. Shared state includes `enc_idx`, `enc_bw_remain`, ring thread, and VOP header DMA. All state is runtime-only.

## Dependencies and Integration Points
The file depends on V4L2/vb2 DMA-SG APIs, P2M DMA, JPEG static tables, TW28 video status and picture controls, motion threshold helpers, OSD helpers, SOLO encoder registers, and global video standard changes from `solo6x10-v4l2.c`.

## Risks and Edge Cases
`FRAME_BUF_SIZE` is fixed at 400 KiB; oversized encoded frames fail. Descriptor handling assumes DMA segment sizes and wraps are manageable; comments note awkward wrapped descriptors can trigger timeouts, so wrap parts are sometimes sent as immediate DMA operations. Bandwidth accounting is software-only and must stay balanced on start/stop errors. Motion detection uses one region mask and only reports frame sequence, not block coordinates.

## Test Signals
Validate all encoder nodes register, MPEG4/H.264/MJPEG enumeration is device-type correct, CIF/D1 and PAL/NTSC headers are valid, keyframe header prepending works, queue draining survives ring wrap, motion events are delivered, controls program TW28/encoder/motion/OSD state, bandwidth limits reject overcommit, and streaming stop returns queued buffers with error state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-v4l2-enc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-v4l2.c

## Purpose
`solo6x10-v4l2.c` implements the live/raw V4L2 display capture node for SOLO6x10 cards, returning UYVY frames from the display SDRAM page ring and allowing users to select camera or multi-view inputs.

## Important APIs, Types, and Functions
Display window helpers include `solo_win_setup()`, `solo_v4l2_ch()`, and `solo_v4l2_set_ch()`. Buffer flow is `solo_video_in_isr()`, `solo_thread()`, `solo_thread_try()`, and `solo_fillbuf()`. V4L2 ioctls cover querycap, input enumeration/selection, format get/try/set, standard get/set, and motion trace control. `solo_set_video_type()` coordinates global PAL/NTSC reconfiguration across display, encoder, TW28, and encoder V4L2 modes.

## Control Flow
Initialization allocates a video device, creates a V4L2 control handler, initializes a contiguous-DMA vb2 queue, cycles through all channels to erase stale display content, selects input 0, and registers the display node. Streaming starts a display thread and enables video-input IRQ. The thread wakes on IRQs or timeout, checks whether the hardware display write page changed, dequeues a vb2 buffer, and either fills blank erase frames or performs a repeated P2M DMA from display SDRAM to the buffer. Input changes temporarily enable display erase, disable the old channel/multiview window, enable the new layout, and wait through erase frames.

## State and Persistence
Display state in `struct solo_dev` includes current input, erasing counters, old write page, sequence counter, active vb2 list, queue lock, display thread wait queue, and video geometry/standard fields. It is runtime-only and rebuilt during probe or standard changes.

## Dependencies and Integration Points
The file depends on V4L2/vb2 DMA-contig APIs, P2M DMA, TW28 video status, display/encoder/TW28 reinit functions, and SOLO video input/output registers. It is the standard-changing coordinator for encoder nodes.

## Risks and Edge Cases
`solo_set_video_type()` reinitializes multiple subsystems after only checking vb2 busy state; failures from `solo_disp_init()`, `solo_enc_init()`, and `solo_tw28_init()` are not propagated. Input switching busy-waits through erase frames. The display thread uses page changes as the only new-frame signal, so missed or repeated page values affect capture cadence.

## Test Signals
Check `/dev/video` registration, UYVY format reporting, camera and 4-up/16-up input enumeration, video-loss status, streaming with mmap/userptr/read, PAL/NTSC switching while idle and rejection while busy, motion trace register updates, frame blanking after input changes, and clean streamoff buffer return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10.h

## Purpose
`solo6x10.h` is the main internal interface for the SOLO6x10 driver, defining device constants, shared structures, register helpers, IRQ helpers, and subsystem prototypes.

## Important APIs, Types, and Functions
It defines PCI IDs, device type constants, channel/I2C/P2M/encoder constants, custom V4L2 controls, motion-grid sizing, `enum SOLO_I2C_STATE`, `struct solo_p2m_desc`, `struct solo_p2m_dev`, `struct solo_vb2_buf`, `enum solo_enc_types`, `struct solo_enc_dev`, and the central `struct solo_dev`. Inline helpers `solo_reg_read()`, `solo_reg_write()`, `solo_irq_on()`, and `solo_irq_off()` are used throughout the driver.

## Control Flow
The header has no independent control flow, but its prototypes define subsystem lifecycle ordering: display, GPIO, I2C, P2M, V4L2 display, encoder core, encoder V4L2, G.723 audio, ISR handlers, I2C byte access, P2M DMA, video standard setting, motion thresholds, OSD, EEPROM, and JPEG QP helpers.

## State and Persistence
`struct solo_dev` aggregates all runtime state for PCI, MMIO, IRQ masks, V4L2, GPIO, TW28 detection, I2C transfer progress, P2M engines, display capture, encoder nodes, current video geometry, JPEG QP, ALSA audio, sysfs SDRAM, ring threads, VOP header DMA, and active buffer lists. The header itself persists nothing.

## Dependencies and Integration Points
It includes kernel PCI/I2C/mutex/list/wait/atomic/slab/video/gpio headers and V4L2/vb2 media headers, plus the register map. Every SOLO subsystem includes this file.

## Risks and Edge Cases
Because this is a broad shared header, changes to `struct solo_dev` or inline IRQ/register helpers have driver-wide impact. `solo_reg_write()` reads PCI status after every MMIO write, likely as a posting flush; removing it could alter hardware timing. `irq_mask` updates are not internally locked, so callers rely on higher-level serialization or low contention.

## Test Signals
Full driver build, probe/remove, suspend-style teardown if available, all subsystem init/exit paths, IRQ mask behavior under concurrent audio/video/I2C/P2M use, and ABI-sensitive V4L2/ALSA/gpio behavior are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/Kconfig

## Purpose
`ttpci/Kconfig` defines build-time configuration options for SAA7146-based "budget" DVB PCI cards, including base support, simple cards, CI cards, and analog-input cards.

## Important APIs, Types, and Functions
The symbols are `DVB_BUDGET_CORE`, `DVB_BUDGET`, `DVB_BUDGET_CI`, and `DVB_BUDGET_AV`. They express dependencies on `DVB_CORE`, `PCI`, `I2C`, `RC_CORE`, and `VIDEO_DEV`, and select SAA7146, EEPROM, frontend, tuner, LNB, and V4L2 helper modules when `MEDIA_SUBDRV_AUTOSELECT` is enabled.

## Control Flow
There is no runtime flow. The configuration graph ensures common core support is built before variant modules and that optional demod/tuner dependencies are selected for known cards.

## State and Persistence
Kconfig selections persist in the kernel `.config`, controlling which modules or built-in objects are produced. No runtime state is owned by this file.

## Dependencies and Integration Points
The file integrates the TTPci budget drivers with the kernel media build system, DVB frontend/tuner libraries, SAA7146 core support, remote-control core, and video-device support for analog capture cards.

## Risks and Edge Cases
Autoselect only pulls known subdrivers when `MEDIA_SUBDRV_AUTOSELECT` is set; otherwise users must enable matching frontends manually. `DVB_BUDGET_CI` depends on `RC_CORE`, so CI cards with IR support cannot be built without remote-control core. `DVB_BUDGET_AV` depends on `VIDEO_DEV` via SAA7146 VV support.

## Test Signals
Check all four symbols build as modules and built-ins, dependency resolution with and without `MEDIA_SUBDRV_AUTOSELECT`, module names matching help text, and successful compilation of selected frontend combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/Makefile

## Purpose
`ttpci/Makefile` maps TTPci budget Kconfig symbols to kernel objects and sets include paths for DVB frontend, tuner, and common media headers.

## Important APIs, Types, and Functions
Object mappings are `budget-core.o`, `budget.o`, `budget-av.o`, and `budget-ci.o` under their corresponding `CONFIG_DVB_*` symbols. `ccflags-y` adds `drivers/media/dvb-frontends/`, `drivers/media/tuners`, and `drivers/media/common`.

## Control Flow
There is no runtime control flow. Kbuild uses this file to compile selected modules and provide include search paths for board-specific frontend headers.

## State and Persistence
The file owns build metadata only. It creates no runtime or persistent kernel state.

## Dependencies and Integration Points
It integrates with Kbuild and the Kconfig options in the same directory. The include paths support direct includes such as `stv0299.h`, `tda1004x.h`, tuner headers, and common TTPci EEPROM support.

## Risks and Edge Cases
Header include paths are broad and may hide missing explicit relative includes. Object selection must stay aligned with Kconfig symbol names and help text module names.

## Test Signals
Validate `make M=drivers/media/pci/ttpci` for each symbol combination, module filenames, and successful builds after moving frontend/tuner/common headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-av.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-av.c

## Purpose
`budget-av.c` supports KNC1/TerraTec/Satelco SAA7146 budget DVB PCI cards with analog video input and optional CI, combining DVB transport capture, frontend attachment, SAA7113 analog capture, and EN50221 CAM access.

## Important APIs, Types, and Functions
`struct budget_av` embeds `struct budget`, analog video state, CI work/status, EN50221 CA object, and a demod reinitialization flag. I2C helpers read/write tuner and decoder registers. CI callbacks implement attribute/control memory access, reset/shutdown, TS enable, and polling. `saa7113_init()` and `saa7113_setinput()` manage analog input. `frontend_init()` selects demod/tuner attachments from many subsystem IDs. `budget_av_attach()`, `budget_av_detach()`, `budget_av_irq()`, and the `saa7146_extension` integrate with the SAA7146 framework.

## Control Flow
Attach allocates state, initializes the common TTPci budget core, configures SAA7146 stream registers, probes SAA7113, and if present initializes SAA7146 VV, registers a V4L2 video device, and sets the analog input. It reads the MAC from EEPROM, stores private adapter data, attaches/registers the appropriate DVB frontend, initializes CI, and installs common budget hooks. IRQ handling delegates MASK10 transport events to the budget core. Detach unregisters analog video, CI, frontend, budget core, and frees state.

## State and Persistence
Runtime state includes current analog input, SAA7113 presence, CI slot state, `dvb_ca_en50221`, frontend pointer in embedded budget state, proposed MAC, and SAA7146 GPIO/video-port state. No persistent data is written; EEPROM MAC is read only.

## Dependencies and Integration Points
The driver depends on `budget-core` DEBI/TS helpers, SAA7146 and SAA7146 VV, DVB core/frontend/tuner modules, I2C, EN50221 CA core, EEPROM/MAC helpers, and board IDs supplied through PCI extension data.

## Risks and Edge Cases
CI polling uses both GPIO card-detect and speculative IO-memory reads because some CAM detect lines are unreliable; the speculative read can upset some CAMs, so it is gated by status/open state. Frontend support is a large board-ID switch with many magic tuner constants. Analog video registration is conditional, so cards without SAA7113 still load as DVB/CI. Some errors from `ciintf_init()` are not fatal to attach.

## Test Signals
Validate PCI ID matching, TS capture IRQs, MAC EEPROM read fallback, frontend registration for DVB-S/S2/C/T variants, analog V4L2 input switching between composite and S-Video, CI CAM insert/reset/ready/removal, TS routing through CAM on enable, and detach cleanup for both analog-present and analog-absent cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-av.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-ci.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-ci.c

## Purpose
`budget-ci.c` supports Technotrend/Hauppauge/Siemens SAA7146 budget DVB PCI cards with Common Interface but without analog video input, including optional MSP430-based IR remote decoding.

## Important APIs, Types, and Functions
`struct budget_ci` embeds common `struct budget`, CI work/status/IRQ state, EN50221 CA object, IR state, and tuner PLL address. `struct budget_ci_ir` tracks rc-core device state and partial RC5 command assembly. IR flow is `msp430_ir_init()`, `msp430_ir_interrupt()`, and `msp430_ir_deinit()`. CI callbacks mirror EN50221 memory/control/reset/TS/poll operations with DEBI addresses. `frontend_init()` attaches board-specific DVB frontends and tuners. `budget_ci_attach()`, `budget_ci_detach()`, and `budget_ci_irq()` integrate with SAA7146.

## Control Flow
Attach allocates state, initializes the common budget core, registers the rc-core IR device, probes/initializes CI, stores adapter private data, attaches/registers the appropriate frontend, and installs common budget hooks. IRQs queue bottom-half work for MSP430 IR on MASK06, delegate TS IRQs on MASK10, and queue CI work on MASK03 when supported. CI init enables DEBI pins, validates CI firmware/version, chooses polling versus IRQ flags, registers EN50221, configures GPIO edge direction, enables interface reset, and emits a synthetic CAM change event. Frontend init switches on subsystem device IDs to attach STV0299/STV0297/TDA1004x/TDA10023/STV0288/STB0899 and matching tuner/LNB helpers.

## State and Persistence
Runtime state includes CI slot status, whether CI IRQs are usable, queued work items, rc-core device, partial RC5 command/device bytes, selected keymap/device filter, tuner PLL address, frontend pointer, and common budget DMA/DVB state. There is no persistent storage.

## Dependencies and Integration Points
The file depends on SAA7146, TTPci budget core, DVB core/frontend/tuner/LNB modules, EN50221 CA core, rc-core, I2C, workqueues, and board-specific headers such as BSBE/BSRU configs.

## Risks and Edge Cases
MSP430 IR bytes can arrive out of order or be lost; the decoder only emits when a command byte is followed by a device byte. CI firmware version `0xa2` lacks interrupts and falls back to polling. Several frontend attach paths must tear down partially attached tuner/LNB chains on failure. `msp430_ir_deinit()` unregisters and frees the rc device, which depends on rc-core ownership semantics staying compatible.

## Test Signals
Check IR keymaps and RC5 filtering for all supported subsystem IDs, CAM insert/remove/reset/ready and FR/DA IRQs, polling-only CI firmware, TS routing through CAM, frontend registration for all listed cards, S2-3200 reset timing, LNB/tuner attach failure cleanup, MASK06/MASK03/MASK10 IRQ dispatch, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-ci.c -->
