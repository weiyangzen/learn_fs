# subset-b-004120 research

This grouped report covers the ivtv Conexant CX23415/CX23416 PCI video driver files under `sources/distributed-fs/ceph-client/drivers/media/pci/ivtv`. Each section preserves the original source path so the reconciliation step can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-cards.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-cards.c

## Purpose
`ivtv-cards.c` is the board database for the ivtv driver. It describes supported Hauppauge, AVerMedia, Yuan, Adaptec, I/O Data, GotView, ASUS, Buffalo, Sony, and related CX23415/CX23416 cards, including PCI IDs, V4L2 capabilities, physical inputs and outputs, tuner choices, I2C probe addresses, GPIO masks, and board-specific comments.

## Important APIs, Types, and Functions
The file instantiates many `struct ivtv_card` descriptors and matching `struct ivtv_card_pci_info` tables, plus common tuner I2C probe sets such as `ivtv_i2c_std`, `ivtv_i2c_radio`, and `ivtv_i2c_tda8290`. Exported helpers are `ivtv_get_card()`, `ivtv_get_input()`, `ivtv_get_output()`, `ivtv_get_audio_input()`, and `ivtv_get_audio_output()`.

## Control Flow
There is little procedural control flow. Probe code in `ivtv-driver.c` indexes `ivtv_card_list` directly or scans each card's `pci_list` to select a descriptor. Once selected, input and output query helpers translate descriptor entries into V4L2-facing names, types, audio sets, and standards. Variant descriptors for PVR-350 V1 and CX23416GYC no-GR/no-YCS sit after standard cards so runtime detection can switch to them without altering normal card numbering.

## State and Persistence
State is static, read-mostly kernel data. It is not persisted and has no runtime locking. The selected `itv->card`, `itv->card_name`, `itv->card_i2c`, and derived input counts in `struct ivtv` are runtime pointers into this table.

## Dependencies and Integration Points
The descriptors encode dependencies on V4L2 standards/capabilities, tuner IDs, GPIO subdev behavior, and media subdevice-specific routing constants for `cx25840`, `saa711x`, `saa717x`, `msp3400`, `wm8775`, `cs53l32a`, `m52790`, and `upd64031a`. Driver probe, routing, I2C registration, GPIO control, tuner setup, and ioctl enumeration all consume this file.

## Risks and Edge Cases
Incorrect bit flags or input mux constants can silently register the wrong subdevice, route audio/video from the wrong physical jack, or omit radio and IR support. Hauppauge cards rely on EEPROM more than PCI IDs, while some non-Hauppauge IDs collide and are refined by probed subdevices. Unsupported cards such as AVerMedia M104 intentionally expose zero V4L2 capabilities to abort probe after identification.

## Test Signals
Useful signals are correct autodetection logs, expected `/dev/video*` and radio nodes, valid `VIDIOC_ENUMINPUT`/`VIDIOC_ENUMOUTPUT` names and standards, tuner selection for PAL/NTSC/SECAM, GPIO-controlled mux switching, IR subdevice registration, and board-specific capture from every advertised physical input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-cards.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-cards.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-cards.h

## Purpose
`ivtv-cards.h` defines the card descriptor contract used by ivtv probe, routing, GPIO, I2C, and ioctl enumeration code. It assigns stable card indices, PCI vendor/device constants, hardware capability bits, logical input/output identifiers, and the structures used by `ivtv-cards.c`.

## Important APIs, Types, and Functions
Important definitions include `IVTV_CARD_*` card IDs, `IVTV_HW_*` bitmasks, input constants such as `IVTV_CARD_INPUT_VID_TUNER`, V4L2 capability aliases `IVTV_CAP_ENCODER` and `IVTV_CAP_DECODER`, and descriptor structs `ivtv_card`, `ivtv_card_video_input`, `ivtv_card_audio_input`, `ivtv_card_output`, `ivtv_card_pci_info`, GPIO helper structs, and tuner I2C structs. It declares the card/input/output query functions implemented in `ivtv-cards.c`.

## Control Flow
The header is declarative, but it constrains runtime control flow by requiring hardware bit positions to remain gapless and descriptor arrays to use sentinel zero entries. Card variant IDs are placed after `IVTV_CARD_LAST` so probe can use user-visible card numbers for normal cards while still supporting refined internal variants.

## State and Persistence
No mutable state lives here. Constants define how `struct ivtv` caches card identity, subdevice masks, tuner tables, and GPIO behavior at runtime.

## Dependencies and Integration Points
The header depends on V4L2 types and tuner IDs pulled indirectly through `ivtv-driver.h`. It integrates with the I2C hardware arrays in `ivtv-i2c.c`, GPIO setup in `ivtv-gpio.c`, stream capability decisions in `ivtv-driver.c`, and V4L2 input/output ioctl helpers.

## Risks and Edge Cases
The `IVTV_HW_BIT_*` enum explicitly disallows gaps because bit numbers index parallel arrays in `ivtv-i2c.c`; adding or reordering bits without updating those arrays breaks subdevice registration. Card index changes affect module parameter cardtype numbering. Descriptor array limits cap cards at six video inputs, three audio inputs, and three tuner choices.

## Test Signals
Compile-time coverage should catch missing struct fields, but functional tests should validate new hardware bits against I2C arrays, cardtype module parameter numbering, input enumeration bounds, and probe behavior for both standard card IDs and post-`IVTV_CARD_LAST` variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-cards.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-controls.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-controls.c

## Purpose
`ivtv-controls.c` implements ivtv-specific V4L2 and cx2341x control callbacks. It bridges generic MPEG encoder/decoder controls to ivtv firmware calls, VBI MPEG insertion state, video decoder format changes, audio sample-clock programming, and volatile decoder timing controls.

## Important APIs, Types, and Functions
The exported operation tables are `ivtv_cxhdl_ops` for `cx2341x_handler` callbacks and `ivtv_hdl_out_ops` for decoder output controls. Key functions are `ivtv_s_stream_vbi_fmt()`, `ivtv_s_video_encoding()`, `ivtv_s_audio_sampling_freq()`, `ivtv_s_audio_mode()`, `ivtv_g_pts_frame()`, `ivtv_g_volatile_ctrl()`, and `ivtv_s_ctrl()`.

## Control Flow
When the cx2341x control handler changes VBI insertion, sliced MPEG buffers are allocated lazily and the sliced service set is defaulted if needed. Video encoding changes program the active video subdev width, halving width for MPEG-1. Audio sampling changes broadcast a matching clock frequency to audio subdevices. Decoder volatile controls read cached timing if valid or ask firmware for current PTS/frame when decoding is active. Decoder audio playback menu changes are translated into `CX2341X_DEC_SET_AUDIO_MODE`.

## State and Persistence
Mutable state is in `struct ivtv`: `vbi.sliced_mpeg_data`, `vbi.insert_mpeg`, `dualwatch_stereo_mode`, `audio_stereo_mode`, `audio_bilingual_mode`, `last_dec_timing`, and `i_flags`. Allocated VBI insertion buffers persist until driver remove frees them.

## Dependencies and Integration Points
The file depends on the cx2341x control framework, V4L2 controls, media bus subdev format calls, ivtv mailbox APIs, and VBI helpers from `ivtv-vbi.h`. Probe installs these ops in `ivtv-driver.c`; file operations consume inserted VBI buffers while reading MPEG.

## Risks and Edge Cases
The sliced VBI buffer size is hardcoded as 2049 bytes, and partial allocation must unwind correctly. Timing controls return zero when idle, so users must distinguish idle from valid zero values. Firmware timing reads can fail with `-EIO`. MPEG-1 width adjustment assumes the video decoder accepts active format updates during control changes.

## Test Signals
Validate VBI MPEG insertion allocation and cleanup, default sliced service selection for 50 Hz and 60 Hz, MPEG-1/MPEG-2 format changes reaching the decoder subdev, audio sampling clock updates, decoder PTS/frame volatile controls while idle and decoding, and decoder audio playback mode firmware calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-controls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-controls.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-controls.h

## Purpose
`ivtv-controls.h` exposes the ivtv control operation tables and decoder timing helper to the rest of the driver.

## Important APIs, Types, and Functions
It declares `ivtv_cxhdl_ops`, `ivtv_hdl_out_ops`, and `ivtv_g_pts_frame(struct ivtv *itv, s64 *pts, s64 *frame)`.

## Control Flow
The header has no executable control flow. `ivtv-driver.c` wires these ops into the cx2341x and V4L2 control handlers during probe, and control callbacks later call into firmware, subdevs, and VBI state.

## State and Persistence
No state is stored here. The declarations operate on `struct ivtv` state owned by `ivtv-driver.h`.

## Dependencies and Integration Points
Consumers must include this after the core ivtv types are visible. It links control setup in `ivtv-driver.c` with the implementation in `ivtv-controls.c` and with ioctl/control users that need timing values.

## Risks and Edge Cases
The header is small, so risk is primarily ABI drift inside the driver: changing operation names or callback signatures without updating probe and control setup will break compilation. `ivtv_g_pts_frame()` depends on decoder firmware state even though that dependency is not visible from the prototype.

## Test Signals
Build coverage should confirm the operation tables match V4L2 and cx2341x callback signatures. Runtime signals are successful control handler initialization and valid decoder PTS/frame control reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-controls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-driver.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-driver.c

## Purpose
`ivtv-driver.c` is the main PCI driver. It handles module parameters, PCI device matching, card autodetection, EEPROM processing, core `struct ivtv` initialization, MMIO setup, GPIO and I2C bring-up, subdevice loading, IRQ and stream registration, first-open firmware initialization, and device removal.

## Important APIs, Types, and Functions
Important globals include `ivtv_first_minor`, `ivtv_ext_init`, `ivtv_debug`, optional `ivtv_fw_debug`, module parameter arrays, and `ivtv_pci_driver`. Core helpers include `ivtv_process_options()`, `ivtv_process_eeprom()`, `ivtv_init_struct1()`, `ivtv_init_struct2()`, `ivtv_setup_pci()`, `ivtv_load_and_init_modules()`, `ivtv_probe()`, `ivtv_init_on_first_open()`, and `ivtv_remove()`. Utility exports include IRQ mask helpers, output-mode helpers, EEPROM read, wait helpers, and first-open initialization.

## Control Flow
Module init validates parameters and registers a PCI driver for Conexant vendor/device IDs. Probe allocates `struct ivtv`, registers a V4L2 device, parses options, identifies a card by user parameter, Hauppauge EEPROM, or PCI subsystem IDs, initializes locks/workers/control handlers, configures PCI and MMIO windows, initializes GPIO and I2C, loads subdevices, chooses tuner/radio/std settings, registers IRQ and V4L2 streams, and schedules optional ivtv-alsa loading. Firmware is intentionally loaded on first open, where the driver retries firmware init, configures initial frequency/input/std, initializes decoder output on CX23415 cards, enables interrupts, and sets up controls. Remove stops streams, halts firmware, shuts down IRQ/DMA/worker resources, unregisters streams/subdevices, and frees VBI buffers and the V4L2 device.

## State and Persistence
Runtime state is per PCI function in `struct ivtv`. Persistent external state is limited to module parameters and card EEPROM reads; driver state itself is volatile. The driver caches selected card descriptors, standards, tuner settings, stream buffers, IRQ masks, firmware mailbox pointers, VBI/YUV state, and subdevice pointers. `IVTV_F_I_INITED` and `IVTV_F_I_FAILED` gate first-open initialization.

## Dependencies and Integration Points
The file integrates with PCI, V4L2 device/control frameworks, cx2341x firmware API, tveeprom, I2C, GPIO, irq handling, DMA/UDMA, stream registration, routing/ioctl helpers, ivtv-alsa extension loading, and optional ivtvfb/IR exported symbols.

## Risks and Edge Cases
Probe has many staged failure exits, so resource ownership must stay aligned with devm-managed MMIO, manually allocated workers, IRQs, I2C adapters, and controls. Card autodetection may default to PVR-150 for unknown hardware. PVR-500 radio correction depends on PCI slot heuristics. Firmware failures are deferred until first open, meaning device nodes may exist before hardware is usable. `ivtv_set_output_mode()` allows only the first decoder output mode until reset.

## Test Signals
Test clean module load/unload, parameter validation, cardtype ignore and force modes, Hauppauge EEPROM variants, unknown card fallback logs, PCI latency and MMIO failures, I2C/subdevice detection, IRQ registration, stream node creation, first-open firmware retry and failure flags, capture and decoder startup, ivtv-alsa callback loading, and remove while capture/decoding is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-driver.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-driver.h

## Purpose
`ivtv-driver.h` is the central internal header for the ivtv driver. It defines the CX23415/CX23416 memory map, stream types, debug macros, options, mailbox and DMA structures, stream queue state, VBI/YUV state, the main `struct ivtv`, register access macros, subdevice call wrappers, and core prototypes.

## Important APIs, Types, and Functions
Important types are `ivtv_options`, `ivtv_mailbox`, `ivtv_mailbox_data`, `ivtv_api_cache`, `ivtv_buffer`, `ivtv_queue`, `ivtv_stream`, `ivtv_open_id`, `ivtv_user_dma`, `vbi_info`, `yuv_playback_info`, and `ivtv`. It defines per-buffer, per-stream, and per-device bit flags, output modes, stream type IDs, register offsets, `file2id()`, `to_ivtv()`, `ivtv_raw_vbi()`, `read_reg()`/`write_reg()`/sync variants, and `ivtv_call_hw()` wrappers.

## Control Flow
The header controls behavior through flags and macros rather than functions. Stream and device flags drive capture, decode, DMA, PIO, VBI insertion, firmware initialization, and event handling. Register macros assume local functions have an `itv` pointer in scope and map symbolic operations onto MMIO access.

## State and Persistence
`struct ivtv` is the full runtime state container: PCI/V4L2 identity, card descriptor pointers, MMIO mappings, controls, standards, locks, streams, counters, ALSA hooks, IRQ worker state, DMA state, mailbox/cache state, I2C adapter/client state, program index cache, VBI and YUV data, and OSD/ivtvfb hooks. The state is volatile and rebuilt on probe/first open.

## Dependencies and Integration Points
This header pulls in Linux PCI, interrupt, I2C, scatterlist, kthread, locking, user access, and V4L2/cx2341x/tuner/IR interfaces. Nearly every ivtv source file depends on it, and exported symbols in `ivtv-driver.c` expose selected helpers to ivtvfb, ivtv-alsa, and IR support.

## Risks and Edge Cases
Because this header centralizes layout and flags, mistakes have broad effects. Some flag values are shared or surprising, such as `IVTV_F_S_PIO_HAS_VBI` reusing bit 1 like the DMA VBI flag. MMIO macros depend on implicit variable naming and do not perform bounds checks. Large embedded arrays in `struct ivtv` make allocation size and zero-initialization assumptions important.

## Test Signals
Build all ivtv objects and extension modules to catch signature drift. Runtime validation should cover stream flag transitions, DMA/PIO queue movement, VBI raw versus sliced mode decisions, register sync behavior on real hardware, firmware mailbox access, YUV/OSD state restoration, and concurrent open/close/read/write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-fileops.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-fileops.c

## Purpose
`ivtv-fileops.c` implements V4L2 file operations and stream lifetime management for ivtv capture, VBI, radio, MPEG decode, YUV decode, and VBI output devices. It handles open/close/read/write/poll, stream claiming, start/stop, buffer copying, MPEG VBI insertion, radio switching, and audio mute helpers.

## Important APIs, Types, and Functions
Exported or externally used functions include `ivtv_claim_stream()`, `ivtv_release_stream()`, `ivtv_start_capture()`, `ivtv_stop_capture()`, `ivtv_start_decoding()`, `ivtv_v4l2_open()`, `ivtv_v4l2_close()`, `ivtv_v4l2_read()`, `ivtv_v4l2_write()`, `ivtv_v4l2_enc_poll()`, `ivtv_v4l2_dec_poll()`, `ivtv_mute()`, and `ivtv_unmute()`. Internal helpers include `ivtv_get_buffer()`, `ivtv_copy_buf_to_user()`, `ivtv_update_pgm_info()`, `ivtv_dualwatch()`, `ivtv_schedule()`, and `ivtv_schedule_dma()`.

## Control Flow
Open performs first-open firmware initialization, checks firmware health, rejects incompatible simultaneous MPEG/YUV decode opens, allocates a per-file `ivtv_open_id`, and performs radio or YUV setup. Read serializes on `serialize_lock`, starts capture on demand, then drains full/io buffers or injected VBI MPEG buffers to userspace. Write claims decoder streams, fixes output mode, starts decode, copies userspace data into buffers or performs YUV UDMA frame transfers, and schedules DMA when firmware asks for data. Close stops capture or decode, unwinds radio mode, releases V4L2 file handles, clears stream flags, and releases claimed streams.

## State and Persistence
State lives in `ivtv_stream` flags and queues, per-open `ivtv_open_id`, atomics for capturing/decoding, VBI insertion counters, program index cache, output mode, radio-user flag, speed flags, and wait queues. Nothing persists across device removal.

## Dependencies and Integration Points
The file depends on queue helpers, stream firmware start/stop helpers, IRQ/DMA/UDMA, VBI processing, routing/ioctl helpers, YUV support, firmware health checks, V4L2 events, and tuner/subdevice calls.

## Risks and Edge Cases
Automatic VBI stream claiming must not conflict with application VBI reads. Blocking paths temporarily drop `serialize_lock`, so wakeups and flags must be correct. MPEG VBI insertion scans packet boundaries and can return partial buffers. Decoder output mode is exclusive across MPEG/YUV/UDMA paths. Radio open is rejected during capture. Nonblocking read/write must return `-EAGAIN` without leaking claimed state.

## Test Signals
Validate blocking and nonblocking reads/writes, poll-triggered capture start, close during active capture/decode, embedded sliced VBI insertion, standalone VBI capture, radio open/close switching, simultaneous decoder stream exclusion, YUV frame-sized writes and UDMA, firmware-dead open rejection, stream queue flushes, and poll event behavior for old and new V4L2 event APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-fileops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-fileops.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-fileops.h

## Purpose
`ivtv-fileops.h` declares the V4L2 file-operation entry points and stream utility functions implemented in `ivtv-fileops.c`.

## Important APIs, Types, and Functions
The header exposes open/read/write/close functions, encoder and decoder poll functions, capture/decode start and stop helpers, mute/unmute helpers, and shared stream claim/release utilities used by ivtv core code and ivtv-alsa.

## Control Flow
No executable control flow lives here. Stream registration code installs these callbacks into video devices, while other modules call claim/release and start/stop helpers to coordinate shared stream ownership.

## State and Persistence
The functions declared here mutate `struct ivtv`, `struct ivtv_stream`, and `struct ivtv_open_id` state, but the header itself stores none.

## Dependencies and Integration Points
It requires Linux file and poll types plus ivtv core structs from `ivtv-driver.h`. It integrates stream registration, file operations, ALSA PCM capture sharing, and driver remove shutdown paths.

## Risks and Edge Cases
The stream claim/release helpers are exported and shared, so callers must obey ivtv locking and stream type rules. Signature drift here affects video device registration and any extension modules.

## Test Signals
Build with ivtv stream registration and ivtv-alsa enabled. Runtime tests should show correct callbacks on every registered V4L2 node and balanced stream claim/release behavior across file and ALSA users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-fileops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-firmware.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-firmware.c

## Purpose
`ivtv-firmware.c` loads, starts, halts, verifies, and restarts CX23415/CX23416 encoder and decoder firmware. It also initializes the MPEG decoder with a canned MPEG stream and restores selected hardware state after firmware restart.

## Important APIs, Types, and Functions
Key functions are `load_fw_direct()`, `ivtv_halt_firmware()`, `ivtv_firmware_versions()`, `ivtv_firmware_init()`, `ivtv_init_mpeg_decoder()`, `ivtv_firmware_check()`, and internal `ivtv_firmware_copy()`, `ivtv_search_mailbox()`, and `ivtv_firmware_restart()`. The file declares firmware names and required sizes via `MODULE_FIRMWARE()`.

## Control Flow
Firmware init halts existing processors, copies encoder and optional decoder firmware into MMIO memory, releases SPU/VPU reset bits, searches firmware memory for mailbox magic cookies, and pings encoder/decoder firmware. First open retries this path. Decoder initialization sets decoder source parameters, starts playback, asks firmware for a DMA target, loads `v4l-cx2341x-init.mpg`, schedules DMA from host, then stops playback. Health checks ping encoder/audio/decoder paths and, if idle, restart firmware and restore standards, decoder setup, framebuffer, OSD alpha, and output routing.

## State and Persistence
State is firmware image contents in device memory, mailbox pointers in `itv->enc_mbox` and `itv->dec_mbox`, API mailbox cache state, decoder and encoder standards, and OSD/framebuffer restoration hooks. Firmware files are external persistent inputs; loaded state is volatile.

## Dependencies and Integration Points
The file depends on Linux firmware loading, ivtv mailbox/API helpers, cx2341x command IDs, YUV filter checks, ioctl standard setters, OSD helpers, UDMA locking, and `saa7127` output routing.

## Risks and Edge Cases
Firmware size mismatches trigger retries and then fail probe-on-open. Mailbox search relies on magic cookies at 256-byte boundaries. Restart is attempted only when idle; active capture/decoding returns `-EIO`. Decoder audio health uses raw decoder memory counters. Incorrect halt/start ordering can leave firmware dead until reboot on some hardware.

## Test Signals
Validate missing, wrong-size, and correct firmware files; encoder-only CX23416 and encoder/decoder CX23415 paths; mailbox discovery; firmware version logs; decoder init MPEG loading; firmware-dead detection; idle restart with standard/OSD restoration; and active-stream failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-firmware.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-firmware.h

## Purpose
`ivtv-firmware.h` declares the firmware lifecycle API used by driver probe, first open, file operations, and remove paths.

## Important APIs, Types, and Functions
It declares `ivtv_firmware_init()`, `ivtv_firmware_versions()`, `ivtv_halt_firmware()`, `ivtv_init_mpeg_decoder()`, and `ivtv_firmware_check()`.

## Control Flow
The header itself has no executable flow. `ivtv-driver.c` calls init/version/decoder setup on first open and halt on remove. `ivtv-fileops.c` calls `ivtv_firmware_check()` during open to reject or recover dead firmware.

## State and Persistence
No state is held here. The declared functions mutate firmware memory, mailbox pointers, standard/output state, and flags inside `struct ivtv`.

## Dependencies and Integration Points
The prototypes depend on `struct ivtv` from the core header and connect the firmware implementation to the driver lifecycle and exported firmware health checks used by related modules.

## Risks and Edge Cases
The simple interface hides whether calls require idle hardware, loaded firmware files, valid MMIO mappings, or initialized mailbox structures. Calling these helpers too early or while streams are active can fail or disrupt hardware.

## Test Signals
Build coverage should ensure callers see consistent prototypes. Runtime signals include successful first-open firmware initialization, remove-time halt, decoder setup on output-capable cards, and open-time recovery from idle firmware failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-gpio.c

## Purpose
`ivtv-gpio.c` implements GPIO-backed board controls as a V4L2 subdevice. It initializes card-specific GPIO direction/output values and exposes GPIO routing, audio mute, tuner mode, audio clock, and reset hooks for cards whose muxes or tuners are wired to CX2341x GPIO pins.

## Important APIs, Types, and Functions
Public functions are `ivtv_gpio_init()`, `ivtv_reset_ir_gpio()`, and `ivtv_reset_tuner_gpio()`. Internal subdev callbacks include `subdev_s_clock_freq()`, `subdev_g_tuner()`, `subdev_s_tuner()`, `subdev_s_radio()`, `subdev_s_audio_routing()`, `subdev_s_ctrl()`, `subdev_log_status()`, and `subdev_s_video_routing()`.

## Control Flow
Probe calls `ivtv_gpio_init()` after MMIO mapping. If the card has GPIO init data or an Xceive reset pin, the function writes initial output and direction registers, initializes `itv->sd_gpio`, creates an audio mute control, runs control setup, and registers the subdevice. Later V4L2 routing and tuner callbacks read masks and values from the active card descriptor and update only the relevant GPIO output bits. Reset helpers pulse fixed PVR-150 IR lines or a card-specific Xceive tuner pin.

## State and Persistence
Runtime state is in hardware GPIO registers and the GPIO V4L2 control handler. Descriptor masks and values are static. Register state is volatile and reinitialized on probe.

## Dependencies and Integration Points
The file depends on card descriptors, V4L2 subdev/control APIs, tuner and xc2028 reset interfaces, and ivtv MMIO macros. Routing code in `ivtv-routing.c`, tuner setup, radio switching, and control handlers call into this GPIO subdevice through standard V4L2 subdev operations.

## Risks and Edge Cases
Wrong GPIO masks can mute audio, select the wrong input, hold a tuner in reset, or fail to reset IR hardware. GPIO register updates are read-modify-write without a local lock, so callers rely on higher-level serialization. `subdev_g_tuner()` treats absent detect masks as full stereo/language capability.

## Test Signals
Validate initial GPIO DIR/OUT logs, mute control behavior, tuner/composite/S-Video routing, radio audio routing, audio sample frequency pin changes, detected mono/stereo reporting on supported boards, PVR-150 IR reset, Xceive tuner reset, and subdev log-status output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-gpio.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-gpio.h

## Purpose
`ivtv-gpio.h` declares the GPIO initialization and reset helpers used by the ivtv core, tuner setup, and exported IR support.

## Important APIs, Types, and Functions
The declared functions are `ivtv_gpio_init(struct ivtv *itv)`, `ivtv_reset_ir_gpio(struct ivtv *itv)`, and `ivtv_reset_tuner_gpio(void *dev, int component, int cmd, int value)`.

## Control Flow
There is no executable logic in the header. `ivtv-driver.c` calls `ivtv_gpio_init()` during probe and exports `ivtv_reset_ir_gpio()`. Tuner setup passes `ivtv_reset_tuner_gpio()` as an XC2028 callback when appropriate.

## State and Persistence
The declared functions operate on GPIO MMIO registers and V4L2 GPIO subdev state, but the header stores nothing.

## Dependencies and Integration Points
It depends on `struct ivtv` visibility and connects card descriptor GPIO data to driver probe, tuner reset, and IR reset paths.

## Risks and Edge Cases
Callers must ensure register MMIO is mapped before invoking GPIO helpers. The tuner reset callback receives a generic `void *` and assumes it is an `i2c_algo_bit_data` with `data` pointing to `struct ivtv`.

## Test Signals
Build with XC2028 tuner support and runtime-test GPIO subdev registration, PVR-150 IR reset export, and tuner firmware reset callbacks on cards with `xceive_pin`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-i2c.c

## Purpose
`ivtv-i2c.c` provides ivtv's I2C adapter implementation and subdevice registration logic. It supports both a custom CX23415/16 bit-banging algorithm and the older `i2c-algo-bit` path, then probes/registers video decoders, audio codecs, tuners, EEPROM, ghost-reduction/YCS chips, GPIO pseudo-hardware, and IR receivers.

## Important APIs, Types, and Functions
Key exported functions are `init_ivtv_i2c()`, `exit_ivtv_i2c()`, `ivtv_i2c_register()`, `ivtv_find_hw()`, and `ivtv_i2c_new_ir_legacy()`. Internal logic includes `hw_addrs`, `hw_devicenames`, `get_key_adaptec()`, `ivtv_i2c_new_ir()`, custom I2C primitives `ivtv_start()`, `ivtv_stop()`, `ivtv_sendbyte()`, `ivtv_readbyte()`, `ivtv_write()`, `ivtv_read()`, `ivtv_xfer()`, and old bit-algo callbacks.

## Control Flow
Probe initializes the adapter with `init_ivtv_i2c()`, choosing the custom algorithm when `options.newi2c > 0`, setting clock timing, binding adapter data to the V4L2 device, setting SCL/SDA high, and registering the bus. `ivtv_load_and_init_modules()` iterates hardware bits and calls `ivtv_i2c_register()`, which handles tuners with board-specific address lists, IR receivers with platform init data, cx25840 with platform data, and other subdevices by fixed or scanned addresses. The custom transfer path serializes the bus with `i2c_bus_lock`, performs combined write-read without an intervening stop, retries operations up to eight times, and returns Linux I2C status.

## State and Persistence
State includes `itv->i2c_adap`, `itv->i2c_algo`, `itv->i2c_client`, `itv->i2c_state`, `itv->i2c_bus_lock`, subdev `grp_id` masks, and IR init data. Hardware line state is volatile. No persistent storage is written.

## Dependencies and Integration Points
The file depends on Linux I2C core, V4L2 I2C subdev helpers, card hardware bit definitions, GPIO reset support, cx25840 platform data, tuner address lists, and IR keymap/protocol helpers. Driver card detection, EEPROM reads, routing, controls, and firmware-adjacent subdev setup all depend on successful I2C registration.

## Risks and Edge Cases
`hw_addrs` and `hw_devicenames` must match `IVTV_HW_BIT_*` ordering. Address collisions are possible, especially legacy Hauppauge IR probing. The custom bus relies on polling MMIO line state and retries to recover stuck SCL/SDA. Combined transaction stop handling is required for chips such as msp3400. `ivtv_find_hw()` matches exact `grp_id`, so duplicate or missing group IDs break later routing.

## Test Signals
Validate both `newi2c` and old bit-algo modes, module parameter clock bounds, EEPROM reads, tuner probing with radio/demod/TV address lists, all declared subdevice `grp_id` values, IR registration and Adaptec key reads, combined write-read transactions, stuck bus recovery logs, and clean adapter deletion on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-i2c.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-i2c.h

## Purpose
`ivtv-i2c.h` declares the ivtv I2C bus and subdevice registration API used by driver probe, EEPROM/card processing, and hardware lookup paths.

## Important APIs, Types, and Functions
It declares `ivtv_i2c_new_ir_legacy()`, `ivtv_i2c_register()`, `ivtv_find_hw()`, `init_ivtv_i2c()`, and `exit_ivtv_i2c()`.

## Control Flow
The header itself has no control flow. `ivtv-driver.c` initializes the adapter, scans/registers hardware bits through `ivtv_i2c_register()`, optionally probes legacy IR, looks up controlling subdevs with `ivtv_find_hw()`, and tears the adapter down on failure or remove.

## State and Persistence
The declared functions mutate I2C adapter/client state, V4L2 subdevice lists, hardware flags, and IR init data in `struct ivtv`; the header stores no state.

## Dependencies and Integration Points
It depends on `struct ivtv` and `struct v4l2_subdev` declarations from the core media stack. It bridges card hardware descriptors to Linux I2C and V4L2 subdevice registration.

## Risks and Edge Cases
Callers must initialize card descriptors and options before `init_ivtv_i2c()` and must not call registration helpers after adapter deletion. `ivtv_find_hw()` requires exact hardware bit masks matching subdevice `grp_id`.

## Test Signals
Build coverage should verify prototype consistency. Runtime tests should confirm adapter creation/removal, subdevice registration from every card hardware bit, legacy IR probing, and successful lookup of video/audio/muxer subdevices after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-i2c.h -->
