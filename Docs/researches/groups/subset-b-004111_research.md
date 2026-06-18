# subset-b-004111 research

This grouped report covers cx18 CX23418 PCI media driver support files under `sources/distributed-fs/ceph-client/drivers/media/pci/cx18`. Each file section preserves its original source path so the reconciliation lane can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-core.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-core.h

## Purpose
This header defines the internal interface and register map for the integrated cx23418 A/V decoder core. It gives the rest of the driver stable names for decoder input routing, audio routing, VBI slicer timing state, and hundreds of decoder, IR, video, VBI, audio, and firmware-download registers.

## Important APIs, Types, and Functions
Key types are `enum cx18_av_video_input`, `enum cx18_av_audio_input`, and `struct cx18_av_state`. `struct cx18_av_state` embeds a `v4l2_subdev`, a V4L2 control handler, current standard/input/audio mode fields, chip revision, initialization state, and VBI slicer line delay/offset. The file is mostly constants such as `CXADEC_CHIP_CTRL`, `CXADEC_DL_CTL`, `CXADEC_VBI_LINE_CTRL*`, `CXADEC_I2S_IN_CTL`, and `CXADEC_I2S_OUT_CTL`.

## Control Flow
There is no executable control flow in this header. Runtime users include the A/V core implementation, decoder firmware loader, VBI configuration, card input tables, and audio/video routing helpers. The register constants make those users program the same decoder address space coherently.

## State and Persistence
The persistent runtime state is in `cx18_av_state` inside `struct cx18`. It tracks the active video/audio input, detected video standard, radio mode, controls, and line offset needed to translate decoder-reported VBI slicer lines into V4L2 field lines. All hardware register state is volatile and rebuilt during probe, first open, standard changes, or firmware reloads.

## Dependencies and Integration Points
The header depends on V4L2 subdev and control APIs and is included by the main driver header. It integrates decoder state with `cx18-cards.c` board routing, `cx18-av-firmware.c` firmware upload, `cx18-av-vbi.c` sliced/raw VBI setup, and ioctl paths that set standards and formats.

## Risks and Edge Cases
Register constants are hardware contracts; a wrong value can break firmware download, clocking, routing, or VBI capture. The video input enums are bit-coded, so card tables must use valid luma/chroma combinations. VBI line comments encode important timing assumptions for 525-line and 625-line systems; changing delay or offset calculations without hardware validation can shift sliced data to the wrong line.

## Test Signals
Useful signals are successful A/V subdev probe, firmware load and verification, correct audio/video input switching on every supported board, working raw and sliced VBI formats, and stable standard changes between 50 Hz and 60 Hz modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-firmware.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-firmware.c

## Purpose
This file loads and verifies the digital firmware for the cx23418 integrated A/V decoder 8051 core. It also programs post-load decoder audio routing, I2S timing, standard detection defaults, and the host audio mux.

## Important APIs, Types, and Functions
`cx18_av_loadfw()` is the exported entry point called through the A/V subdev core `load_fw` path. `cx18_av_verifyfw()` re-enters decoder firmware upload mode and reads back the firmware image byte-by-byte through `CXADEC_DL_CTL`. Constants include firmware name `v4l-cx23418-dig.fw`, `CX18_AUDIO_ENABLE`, AI1 mux bit masks, and decoder registers from `cx18-av-core.h`.

## Control Flow
`cx18_av_loadfw()` requests firmware from the PCI device, retries full image upload up to five times, and retries each byte write up to `CX18_MAX_MMIO_WR_RETRIES`. It resets the Mako core, enables 8051 upload mode, writes each byte through `CXADEC_DL_CTL`, starts firmware execution, optionally verifies the load, then writes decoder pin, I2S, standard-detection, MiniMe, and audio mux registers. It releases firmware before returning.

## State and Persistence
The firmware image is transient. Hardware state persists until reset or power management changes: the 8051 program RAM, decoder pins, I2S controls, standard-detection settings, and host `CX18_AUDIO_ENABLE` mux. There is no on-disk persistence.

## Dependencies and Integration Points
This code depends on Linux firmware loading, `cx18_av_read/write` helpers from the A/V core, main MMIO helpers for host registers, and `struct cx18_av_state` for logging through the decoder subdev. It is part of first-open initialization after CPU/APU firmware loading.

## Risks and Edge Cases
Firmware writes are known to have byte errors, so retry logic is central. Verification reuses upload-mode side effects and must leave the decoder in a runnable state afterward. If firmware is missing, analog capture cannot initialize. The AI1 mux toggle is hardware-specific; incorrect masks can mute or misroute audio. Verification failure is logged but the code still attempts to start firmware only if verification succeeded.

## Test Signals
Test by booting with and without `v4l-cx23418-dig.fw`, observing load and verify messages, checking analog audio after first capture, switching standards, and ensuring repeated first-open firmware reloads do not leave the mux in an invalid state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-vbi.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-vbi.c

## Purpose
This file implements A/V decoder VBI subdev operations. It configures raw VBI and sliced VBI capture registers, reports the current sliced VBI service layout, and decodes VIP ancillary data lines into V4L2 sliced VBI records.

## Important APIs, Types, and Functions
Entry points are `cx18_av_g_sliced_fmt()`, `cx18_av_s_raw_fmt()`, `cx18_av_s_sliced_fmt()`, and `cx18_av_decode_vbi_line()`. `struct vbi_anc_data` describes the ancillary payload layout from the decoder. `decode_vps()` converts biphase-coded VPS bytes. The file maps hardware line-control nibbles to V4L2 services for teletext, WSS, closed captions, and VPS.

## Control Flow
Format getters read decoder line-control registers and translate them into V4L2 `service_lines`. Raw mode runs `cx18_av_std_setup()`, writes the slicer delay, and sets output control for raw active VBI. Sliced mode also runs standard setup, selects ancillary data output, clears impossible service lines for PAL/NTSC, programs `CXADEC_VBI_LINE_CTRL*`, and adjusts VBI timing. Decode flow validates the ancillary preamble and DID, converts slicer line numbers with `slicer_line_offset`, maps SDID to V4L2 service type, validates parity for captions, and decodes VPS when needed.

## State and Persistence
State is split between decoder registers and `cx18_av_state` VBI timing fields. The requested service lines live in hardware until reconfigured. Decoded VBI data is per-line transient and handed to upper VBI code.

## Dependencies and Integration Points
It depends on `cx18_av_std_setup()`, decoder MMIO helpers, Linux bit/parity helpers, and V4L2 subdev VBI operations. It integrates with `cx18-ioctl.c` sliced/raw format ioctls and with higher-level VBI processing that inserts sliced data into MPEG private streams or exposes sliced VBI to userspace.

## Risks and Edge Cases
The code assumes a VIP ancillary layout and ignores lines with bad preambles or unsupported SDIDs. PAL and NTSC legal line ranges differ and are forcibly cleared. Slicer line delay/offset must match `cx18_av_std_setup()` or data will be attributed to the wrong field line. VPS decoding mutates the payload buffer in place.

## Test Signals
Exercise `VIDIOC_G/S_FMT` for raw and sliced VBI, confirm service-line sanitization for 525/625 standards, capture closed captions and WSS/VPS, and verify malformed ancillary data produces zero type/line rather than corrupt output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-vbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-cards.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-cards.c

## Purpose
This file is the board database for cx18-supported CX23418 capture cards. It defines card-specific PCI IDs, video/audio input routing, tuner choices, GPIO reset and mux settings, I2C probing addresses, DDR timing, and user-visible card names/comments.

## Important APIs, Types, and Functions
Static `struct cx18_card` instances describe Hauppauge HVR-1600 variants, Compro H900, Yuan MPC718, Conexant Raptor PAL, Toshiba Qosmio DVB-T/Analog, Leadtek PVR2100 and DVR3100H, and GoTView PCI DVD3 Hybrid. Public helpers are `cx18_get_card()`, `cx18_get_input()`, and `cx18_get_audio_input()`. The file also defines standard tuner I2C address sets `cx18_i2c_std` and `cx18_i2c_nxp`.

## Control Flow
Probe code asks `cx18_get_card()` by user-selected index or autodetected PCI/EEPROM result. Once selected, `cx18_init_struct2()` counts valid video/audio inputs from the table. Ioctl enumeration calls `cx18_get_input()` and `cx18_get_audio_input()` to fill V4L2 descriptors from the active table.

## State and Persistence
The card table is static read-only state. At runtime, `struct cx18` holds a pointer to the selected card, derived names, I2C address table, input counts, active input, audio input, tuner standard, and GPIO values initialized from the selected entry.

## Dependencies and Integration Points
The file depends on V4L2 standards, tuner IDs, `cx18-av-core.h` input enums, `cx18-cards.h` structures, and CS5345 mux constants. It drives probe decisions in `cx18-driver.c`, GPIO behavior in `cx18-gpio.c`, tuner and subdevice registration in `cx18-i2c.c`, firmware DDR setup in `cx18-firmware.c`, and DVB frontend selection in `cx18-dvb.c`.

## Risks and Edge Cases
Many boards have comments saying experimenters are needed or settings are guesses. Wrong DDR timing can prevent firmware or DMA from working. Wrong GPIO reset masks can hold tuners, demods, or IR chips in reset. Hauppauge cards are refined by EEPROM rather than subsystem IDs, so defaulting to the wrong HVR-1600 variant can select the wrong digital frontend or DDR timing.

## Test Signals
Validate every card entry with PCI autodetection or forced `cardtype=`, input and audio enumeration, tuner setup, GPIO reset behavior, DDR initialization, analog capture, and DVB registration on hybrid boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-cards.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-cards.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-cards.h

## Purpose
This header defines board-description structures and hardware flag constants used by the cx18 driver to adapt one PCI core to many capture-card layouts.

## Important APIs, Types, and Functions
Hardware flags include `CX18_HW_TUNER`, `CX18_HW_TVEEPROM`, `CX18_HW_CS5345`, `CX18_HW_DVB`, `CX18_HW_418_AV`, `CX18_HW_GPIO_MUX`, `CX18_HW_GPIO_RESET_CTRL`, and `CX18_HW_Z8F0811_IR_HAUP`. Types include `cx18_card_video_input`, `cx18_card_audio_input`, `cx18_card_pci_info`, GPIO init/reset/audio descriptors, tuner descriptors, tuner I2C address tables, `cx18_ddr`, and the aggregate `struct cx18_card`. Public prototypes are `cx18_get_input()`, `cx18_get_audio_input()`, and `cx18_get_card()`.

## Control Flow
The header has no executable flow. It defines the contract consumed by card tables, PCI probe, subdevice registration, V4L2 input enumeration, GPIO reset/mux code, I2C probing, and DDR initialization.

## State and Persistence
`struct cx18_card` instances are static configuration. Their data is copied or referenced by `struct cx18` at probe time and remains the source of truth for board capabilities until device removal.

## Dependencies and Integration Points
It depends on V4L2 capability and standard identifiers plus tuner IDs. It is an integration point between `cx18-cards.c`, `cx18-driver.c`, `cx18-gpio.c`, `cx18-i2c.c`, `cx18-firmware.c`, `cx18-dvb.c`, and ioctl input/audio handling.

## Risks and Edge Cases
Array size constants cap the number of inputs and tuners; adding a board with more routes requires structure changes. Hardware flags are bit positions that must stay aligned with arrays in `cx18-i2c.c`. GPIO masks assume no overlap between active-low and active-high reset lines.

## Test Signals
Compile-time signals include all board initializers matching structure fields and no out-of-range array use. Runtime signals include correct `VIDIOC_ENUMINPUT`, `VIDIOC_ENUMAUDIO`, subdevice creation, reset behavior, and firmware DDR stability per card.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-cards.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-controls.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-controls.c

## Purpose
This file implements cx18 callbacks for the shared `cx2341x_handler` MPEG encoder control framework. It translates control changes into decoder, audio, and VBI-side state changes.

## Important APIs, Types, and Functions
The exported object is `cx18_cxhdl_ops`. Callback functions are `cx18_s_stream_vbi_fmt()`, `cx18_s_video_encoding()`, `cx18_s_audio_sampling_freq()`, and `cx18_s_audio_mode()`. They operate on `struct cx2341x_handler` embedded in `struct cx18`.

## Control Flow
When a V4L2 MPEG control changes, the cx2341x core calls these hooks. VBI format changes are rejected while analog capture is active, allocate the sliced-MPEG insertion ring on demand, enable or disable IVTV-style VBI insertion only for supported MPEG-2 PS stream types, and install default service lines when none are configured. Video encoding changes update the decoder pad format width for MPEG-1 half-width mode. Audio sample frequency changes call all audio subdevices to adjust clock frequency. Audio mode changes cache dualwatch stereo mode.

## State and Persistence
State changes are in `cx->vbi.insert_mpeg`, `cx->vbi.sliced_mpeg_data[]`, `cx->dualwatch_stereo_mode`, decoder subdev format state, and audio subdev clock state. Allocated VBI buffers live until device removal.

## Dependencies and Integration Points
This file depends on `cx2341x_handler`, V4L2 subdev pad and audio operations, cx18 VBI helpers, mailbox-backed control application, and global capture counters. It is installed during `cx18_init_struct1()`.

## Risks and Edge Cases
VBI insertion is intentionally limited to MPEG-2 PS/DVD/SVCD streams; enabling it for TS would corrupt assumptions in file copy splice logic. Buffer allocation is all-or-nothing across 32 frames. The code relies on capture counters to prevent mid-stream changes.

## Test Signals
Change MPEG stream type and VBI insertion controls before and during capture, verify `-EBUSY` while capturing, confirm default sliced service lines are created, and check audio clock changes at 32/44.1/48 kHz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-controls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-controls.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-controls.h

## Purpose
This header exposes the cx18-specific `cx2341x_handler_ops` table to driver initialization code.

## Important APIs, Types, and Functions
The only declared symbol is `extern const struct cx2341x_handler_ops cx18_cxhdl_ops;`. It is consumed by `cx18-driver.c` when initializing `cx->cxhdl`.

## Control Flow
No runtime flow exists in the header. It links the control callback implementation in `cx18-controls.c` into the main device initialization path.

## State and Persistence
The ops table is static read-only code/data. Runtime state affected by those callbacks lives in `struct cx18`, `struct cx2341x_handler`, VBI buffers, and subdevices.

## Dependencies and Integration Points
This is a narrow integration point between the main driver and cx2341x MPEG controls. It assumes including files already know `struct cx2341x_handler_ops`.

## Risks and Edge Cases
Because the header has no include guard and no includes, it relies on include order through `cx18-driver.h` or other media headers. Moving it into a different compilation context could require forward declarations or includes.

## Test Signals
Build coverage is the primary signal: `cx18-driver.c` must resolve `cx18_cxhdl_ops`, and MPEG control changes should invoke the callbacks documented in `cx18-controls.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-controls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-driver.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-driver.c

## Purpose
This is the main PCI module implementation for cx18. It owns module parameters, PCI probe/remove, board autodetection, global device initialization, first-open firmware bootstrap, stream registration, and cleanup.

## Important APIs, Types, and Functions
Important entry points are PCI callbacks `cx18_probe()` and `cx18_remove()`, module init/exit `module_start()` and `module_cleanup()`, first-open initializer `cx18_init_on_first_open()`, option parsing `cx18_process_options()`, EEPROM handling `cx18_read_eeprom()` and `cx18_process_eeprom()`, PCI setup `cx18_setup_pci()`, and subdevice setup `cx18_init_subdevs()`. It exports `cx18_ext_init` for the ALSA extension and `cx18_msleep_timeout()`.

## Control Flow
Module init validates parameters and registers a PCI driver. Probe allocates `struct cx18`, registers V4L2 device state, selects a card by module option, Hauppauge EEPROM, PCI ID, or default fallback, initializes locks/queues/control handlers, enables PCI and maps the 64 MiB memory window, initializes power, DDR, SCB, GPIO, A/V decoder, I2C, IRQ, tuner, streams, and video devices, then schedules asynchronous `cx18-alsa` loading. First open loads CPU/APU firmware twice for a silicon workaround, resets APU audio, loads A/V decoder firmware, selects input, standard, and initial frequency. Remove stops capture, disables interrupts, cancels work, halts firmware, unregisters streams/I2C/IRQ, unmaps memory, frees VBI buffers and controls, and unregisters V4L2.

## State and Persistence
Runtime state is almost entirely in `struct cx18`: module-derived options, selected card, stream buffers, controls, workqueues, VBI state, MMIO pointers, IRQ masks, I2C adapters, subdev pointers, and capture counters. No state is persisted beyond module/device lifetime.

## Dependencies and Integration Points
It integrates PCI, DMA, V4L2, cx2341x controls, firmware, SCB, mailbox, I2C, GPIO, A/V decoder, stream registration, DVB, and optional ALSA. Board data from `cx18-cards.c` drives many later steps.

## Risks and Edge Cases
Probe has many partial-initialization exits, so cleanup order is critical. `cx18_instance` is incremented before allocation and is not decremented on probe failure. Firmware is delayed until first open, so probe can succeed while capture later fails. The double firmware load and APU reset sequence are hardware workarounds that should not be simplified without regression testing.

## Test Signals
Validate forced and autodetected card types, bad module parameters, missing firmware, repeated open/close, module unload while capturing, IRQ sharing, I2C adapter creation, stream device node registration, and ALSA extension loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-driver.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-driver.h

## Purpose
This is the central internal header for cx18. It defines driver constants, stream types, debug macros, buffer and MDL structures, VBI state, DVB state, I2C callback data, the main `struct cx18`, and cross-file prototypes/macros.

## Important APIs, Types, and Functions
Key constants include card IDs, stream type IDs, PCI IDs, default buffer counts and sizes, debug flags, stream flags, instance flags, VBI constants, and `CX18_MAX_MMIO_WR_RETRIES`. Key structures include `cx18_options`, `cx18_enc_idx_entry`, `cx18_vb2_buffer`, `cx18_buffer`, `cx18_mdl`, `cx18_queue`, `cx18_dvb`, `cx18_in_work_order`, `cx18_stream`, `cx18_open_id`, `vbi_info`, `cx18_i2c_algo_callback_data`, and `cx18`. Inline helpers are `file2id()`, `fh2id()`, `to_cx18()`, and `cx18_raw_vbi()`.

## Control Flow
The header contributes call macros `cx18_call_hw()`, `cx18_call_all()`, and their error-returning variants. These route V4L2 subdev calls by `grp_id`, enabling board-specific subdevices to be addressed by hardware flags.

## State and Persistence
`struct cx18` is the persistent in-memory device state for a PCI function. Per-stream queue state tracks free, busy, full, and idle MDLs; VBI state tracks capture geometry and MPEG insertion buffers; flags and atomics coordinate open, capture, firmware, radio, pause, and stop behavior.

## Dependencies and Integration Points
The header pulls in Linux PCI, interrupt, I2C, workqueue, mutex, V4L2, tuner, DVB, vb2, mailbox, A/V core, and cx23418 firmware API definitions. Nearly every cx18 implementation file depends on this contract.

## Risks and Edge Cases
Structure fields are shared across IRQ, workqueue, file, ioctl, DVB, and ALSA contexts; lock and flag discipline must be preserved. Buffer-size constants encode firmware alignment requirements for YUV and index streams. The debug macros assume a local `cx` or `dev` variable, which affects call-site naming.

## Test Signals
Broad compile coverage is essential. Runtime signals include no queue corruption under concurrent read/poll/stop, correct device state in `VIDIOC_LOG_STATUS`, sane buffer sizing from module options, and stable VBI and DVB data paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-dvb.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-dvb.c

## Purpose
This file provides DVB support for cx18 hybrid cards. It registers DVB adapters/demux devices, attaches board-specific demodulator and tuner frontends, and starts/stops transport stream DMA in response to DVB feed activity.

## Important APIs, Types, and Functions
Public functions are `cx18_dvb_register()` and `cx18_dvb_unregister()`. DVB callbacks are `cx18_dvb_start_feed()` and `cx18_dvb_stop_feed()`. Frontend attach flow lives in static `dvb_register()`. Board-specific config objects cover S5H1409/MXL5005S, S5H1411/TDA18271, ZL10353/XC2028, and MT352 firmware-assisted initialization. `yuan_mpc718_mt352_init()` programs MT352 register pairs from `dvb-cx18-mpc718-mt352.fw`.

## Control Flow
Registration creates a DVB adapter, software demux, dmxdev, hardware and memory frontends, connects the hardware frontend, attaches the physical frontend based on `cx->card->type`, registers it, enables the TS demux clock, and initializes DVB networking. Starting the first feed ensures cx18 firmware is initialized, programs serial DMUX mode for HVR-1600 cards, and starts the TS stream through `cx18_start_v4l2_encode_stream()`. Stopping the last feed stops the encode stream.

## State and Persistence
Per-stream `struct cx18_dvb` stores adapter, demux, dmxdev, frontend, net, feed count, enabled flag, and feed lock. Feed count is volatile and gates DMA start/stop. Frontend firmware state is held by attached demod/tuner drivers.

## Dependencies and Integration Points
The file depends on DVB core, frontend drivers, firmware loading, cx18 streams, I2C adapters, card type tables, GPIO tuner reset callbacks, and MMIO clock/DMUX registers.

## Risks and Edge Cases
Some board support is experimental. MPC718 MT352 requires an external firmware-derived register sequence and enforces a small even firmware size. Start/stop feed reference counting must stay balanced. `dvb_register()` returns `-1` on frontend absence rather than a specific errno. TS DMUX clock and serial/parallel mode settings are board-specific.

## Test Signals
Confirm adapter/frontend registration per hybrid board, firmware-missing behavior on MPC718 MT352, channel scan and lock, feed start/stop under multiple PIDs, module unload after DVB use, and no analog/DVB stream contention beyond documented card limitations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-dvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-dvb.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-dvb.h

## Purpose
This header declares the cx18 DVB registration API used by stream setup and cleanup code.

## Important APIs, Types, and Functions
It includes `cx18-driver.h` for `struct cx18_stream` and declares `int cx18_dvb_register(struct cx18_stream *stream);` and `void cx18_dvb_unregister(struct cx18_stream *stream);`.

## Control Flow
The header has no executable flow. It allows stream/device registration code to conditionally create or tear down DVB support for TS streams.

## State and Persistence
No state is held here. The actual DVB state is `struct cx18_dvb` embedded through `struct cx18_stream`.

## Dependencies and Integration Points
This is the narrow interface between cx18 stream registration and the DVB implementation. It relies on stream setup to allocate/populate `stream->dvb` before registration.

## Risks and Edge Cases
Because it includes the full main driver header, any user inherits many media and Linux dependencies. The API assumes callers do not pass non-TS streams or streams lacking `dvb` allocation.

## Test Signals
Build signals confirm stream setup can call these functions. Runtime signals are successful DVB registration/unregistration on cards with `CX18_HW_DVB` and no calls for analog-only boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-dvb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-fileops.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-fileops.c

## Purpose
This file implements V4L2 file operations and capture read control for cx18 encoder streams. It owns open/close, stream claiming, read, poll, capture start/stop coordination, VBI insertion splice handling, radio open behavior, and audio mute/unmute helpers.

## Important APIs, Types, and Functions
Public functions include `cx18_claim_stream()`, `cx18_release_stream()`, `cx18_start_capture()`, `cx18_stop_capture()`, `cx18_v4l2_open()`, `cx18_v4l2_read()`, `cx18_v4l2_close()`, `cx18_v4l2_enc_poll()`, `cx18_vb_timeout()`, `cx18_mute()`, and `cx18_unmute()`. Internal helpers manage MDL dequeueing, user copies, sliced VBI MPEG private stream insertion, and dual-language stereo watching.

## Control Flow
Open serializes first-open firmware initialization and creates a `cx18_open_id`. Reads and polls lazily start capture, claim the target stream, and for MPEG also claim internal IDX or VBI streams depending on VBI insertion. DMA completions fill `q_full`; reads dequeue MDLs, byteswap/process VBI or MPEG when needed, copy buffers to userspace, and return drained MDLs to firmware. Close stops radio mode, releases vb2 ownership for YUV, stops capture, clears flags, and releases stream claims.

## State and Persistence
State is maintained in stream flags (`CLAIMED`, `STREAMING`, `APPL_IO`, `INTERNAL_USE`, `STREAMOFF`), stream owner IDs, MDL queues, VBI sliced MPEG ring data, capture counters, `search_pack_header`, radio flag, and open file handles. Everything is volatile.

## Dependencies and Integration Points
It depends on queue helpers, stream start/stop helpers, mailbox APIs, VBI processing, audio/video routing, V4L2 events, vb2 for YUV, and subdevice tuner/audio calls. ALSA PCM can claim/release shared streams through exported symbols.

## Risks and Edge Cases
MPEG VBI insertion depends on correctly finding Program Stream pack boundaries and is not valid for TS. Claim/release ordering must preserve internal IDX/VBI streams. Nonblocking reads, signals, EOS, and close while streaming share queue state. Radio open rejects switching during analog capture.

## Test Signals
Exercise blocking and nonblocking read, poll-triggered capture start, encoder stop at GOP end, close during active capture, MPEG reads with and without sliced VBI insertion, VBI single-frame reads, YUV vb2 timeout, and radio open/close transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-fileops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-fileops.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-fileops.h

## Purpose
This header declares cx18 V4L2 file operation helpers and stream claim/release functions shared across stream registration, ioctl, ALSA, and capture code.

## Important APIs, Types, and Functions
Declarations cover `cx18_v4l2_open()`, `cx18_v4l2_read()`, `cx18_v4l2_write()`, `cx18_v4l2_close()`, `cx18_v4l2_enc_poll()`, `cx18_start_capture()`, `cx18_stop_capture()`, `cx18_mute()`, `cx18_unmute()`, `cx18_v4l2_mmap()`, `cx18_clear_queue()`, `cx18_vb_timeout()`, `cx18_claim_stream()`, and `cx18_release_stream()`.

## Control Flow
No executable flow lives here. It publishes entry points used when building `video_device` file operations and when other modules need to participate in stream ownership.

## State and Persistence
The functions manipulate stream flags, queues, file handles, and capture state in `struct cx18`, but the header itself stores no state.

## Dependencies and Integration Points
It depends on Linux file, poll, vm area, vb2 buffer-state, and cx18 stream/open-id types from included driver headers. The `cx18_claim_stream()` and `cx18_release_stream()` declarations are explicitly shared with `cx18-alsa`.

## Risks and Edge Cases
Several declared functions are implemented outside this source slice, so changing prototypes requires coordinated updates. `cx18_v4l2_write()` and mmap/queue helpers must match registered file/ioctl ops even though their implementation is elsewhere.

## Test Signals
Compile/link coverage catches prototype drift. Runtime signals include working open/read/poll/close on all registered V4L2 nodes and ALSA coexistence with PCM stream claims.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-fileops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-firmware.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-firmware.c

## Purpose
This file initializes cx23418 chip clocks, power, DDR memory, and CPU/APU firmware. It also halts firmware during removal and validates firmware writes through MMIO readback.

## Important APIs, Types, and Functions
Public functions are `cx18_firmware_init()`, `cx18_halt_firmware()`, `cx18_init_memory()`, and `cx18_init_power()`. Static loaders are `load_cpu_fw_direct()` for `v4l-cx23418-cpu.fw` and `load_apu_fw_direct()` for segmented `v4l-cx23418-apu.fw`. `struct cx18_apu_rom_seghdr` describes APU firmware segments.

## Control Flow
Power initialization programs PLLs, clock selectors, half-clock selectors, and clock enables. Memory initialization resets DDR, writes board-specific DDR timing from `cx->card->ddr`, enables bus timeout, and configures write memory buffers. Firmware init masks DSP interrupts, stops CPU/APU, enables mailbox interrupts, loads CPU firmware through paged encoder memory, reinitializes SCB, loads APU segments, starts CPU, waits for APU reset release, disables CPU-side ack interrupts, tests firmware with `CX18_CPU_DEBUG_PEEK32`, and initializes GPIO-related firmware state.

## State and Persistence
Hardware clock, reset, DDR, SCB, CPU program, APU program, and interrupt-enable state persist until reset or module removal. `CX18_F_I_LOADED_FW` controls logging across reloads. Firmware files are transient resources.

## Dependencies and Integration Points
It depends on Linux firmware loading, MMIO/page helpers, IRQ enable helpers, SCB initialization, mailbox API, and board DDR tables. It is invoked during probe for power/memory and during first-open firmware bootstrap.

## Risks and Edge Cases
Firmware writes assume 32-bit alignment and validate by readback. APU segment parsing must respect little-endian headers and segment bounds. Board-specific DDR values are critical. Failure after enabling interrupts can leave partial firmware state. The double firmware load is orchestrated by `cx18-driver.c`, so this routine must remain idempotent enough for retries.

## Test Signals
Boot with missing CPU/APU firmware, verify firmware size/version logs, capture after repeated open/close, compare DDR stability per board, and inspect mailbox liveness through the debug peek command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-firmware.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-firmware.h

## Purpose
This header declares firmware, power, and memory initialization functions for the cx18 main driver.

## Important APIs, Types, and Functions
It declares `cx18_firmware_init()`, `cx18_halt_firmware()`, `cx18_init_memory()`, and `cx18_init_power()`.

## Control Flow
The header has no executable control flow. Probe calls power and memory initialization; first open calls firmware initialization; remove calls halt.

## State and Persistence
The functions operate on `struct cx18` and program hardware state, but the header itself holds no state.

## Dependencies and Integration Points
It is included by `cx18-driver.c` and implemented by `cx18-firmware.c`. It assumes a visible declaration of `struct cx18` from the main driver header.

## Risks and Edge Cases
Prototype drift would break the probe and first-open paths. Because firmware loading is delayed until first open, callers must continue to handle runtime errors from `cx18_firmware_init()`.

## Test Signals
Compile/link success and runtime first-open firmware loading are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-gpio.c

## Purpose
This file manages CX23418 GPIO output state and exposes two logical V4L2 subdevices: a GPIO audio multiplexer and a GPIO reset controller.

## Important APIs, Types, and Functions
Public functions are `cx18_gpio_init()`, `cx18_gpio_register()`, and `cx18_reset_tuner_gpio()`. Internal helpers `gpio_write()`, `gpio_update()`, and `gpio_reset_seq()` maintain cached GPIO direction/value and program low/high register banks. Subdev ops implement log status, radio selection, standard-triggered audio muxing, audio routing, and reset commands.

## Control Flow
Probe initializes GPIO from the selected card table, optionally forces the XCeive reset pin high, and registers reset/mux subdevices according to hardware flags. Audio and tuner subdev calls update GPIO mux bits. Reset commands assert/deassert card-specific I2C, Z8F0811 IR, or XC2028 reset lines with configured delays. The XCeive tuner callback bridges tuner-driver reset requests to the reset subdev.

## State and Persistence
`cx->gpio_dir` and `cx->gpio_val` are cached software state protected by `gpio_lock`; hardware GPIO registers mirror that state. Values persist only while the device remains powered and bound.

## Dependencies and Integration Points
The file depends on card GPIO descriptors, MMIO helpers, V4L2 subdev APIs, tuner ID constants, and XC2028 callback command values. It integrates with I2C initialization to reset downstream chips and with audio/video/radio routing.

## Risks and Edge Cases
GPIO register writes are split into low and high halves with masks, so cached state must remain authoritative. Card tables may contain guessed GPIO masks. The mux code has FIXME notes about active/audio input state during radio transitions. Reset timing is hardware-specific.

## Test Signals
Inspect `VIDIOC_LOG_STATUS` GPIO output, test I2C device discovery after reset, exercise radio/line/tuner audio routing, reset XC2028 via tuner callback, and verify no GPIO line is left asserted after probe or resume-like reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-gpio.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-gpio.h

## Purpose
This header declares cx18 GPIO initialization, logical subdevice registration, and tuner reset callback support.

## Important APIs, Types, and Functions
It declares `cx18_gpio_init()`, `cx18_gpio_register()`, and `cx18_reset_tuner_gpio()`. `enum cx18_gpio_reset_type` defines reset commands for I2C devices, Z8F0811 IR, and XC2028 tuners.

## Control Flow
No executable flow lives here. The reset enum values are passed through V4L2 subdev core reset calls and interpreted in `cx18-gpio.c`.

## State and Persistence
GPIO state is held by `struct cx18` and hardware registers, not by the header.

## Dependencies and Integration Points
The header is used by driver probe, I2C setup, DVB frontend configuration, and tuner setup. The reset callback signature matches tuner-driver callback expectations.

## Risks and Edge Cases
Reset enum numeric values are part of internal call contracts. Adding reset types requires updates in the reset controller implementation and all callers.

## Test Signals
Build coverage plus runtime I2C reset, IR reset, and XC2028 reset behavior confirm this interface is wired correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-i2c.c

## Purpose
This file implements the two cx23418 I2C adapters using the Linux bit-banging algorithm over CX23418 I2C registers, and registers card subdevices on those buses.

## Important APIs, Types, and Functions
Public functions are `init_cx18_i2c()`, `exit_cx18_i2c()`, `cx18_i2c_register()`, and `cx18_find_hw()`. Bit operations are `cx18_setscl()`, `cx18_setsda()`, `cx18_getscl()`, and `cx18_getsda()`. Static maps associate cx18 hardware flags with default addresses, bus indices, and device names.

## Control Flow
Initialization builds two `i2c_adapter` and `i2c_algo_bit_data` instances, resets/enables I2C hardware, clears stale interrupts, initializes SCL/SDA high, resets downstream I2C chips through GPIO, and registers both bit-banged buses. Subdevice registration handles tuner probing across radio/demod/TV address lists, creates Z8F0811 IR devices with platform data, and creates fixed-address V4L2 I2C subdevs such as CS5345. Exit disables hardware lines and unregisters adapters.

## State and Persistence
Per-device adapter, algorithm, and callback data live in `struct cx18`. Subdevices registered on the adapters become children of the V4L2 device until cleanup. Hardware line state is volatile.

## Dependencies and Integration Points
The file depends on I2C bit-algo, V4L2 I2C helpers, card I2C tables, GPIO reset subdevice, IRQ register constants, and IR keyboard platform data. It is central to tuner, demod, EEPROM, CS5345, and IR integration.

## Risks and Edge Cases
Hardware flag bit positions must match address/bus/name arrays. Tuner registration considers success if any of three scanned groups succeeds. I2C hardware reset values are magic constants. There is a TODO for interrupt-based I2C, but current logic is polling/bit-banged.

## Test Signals
Use `i2cdetect`-style debug or driver logs to confirm two adapters, verify EEPROM/tuner/CS5345/IR discovery per board, test failure cleanup when second bus registration fails, and confirm GPIO reset improves device discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-i2c.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-i2c.h

## Purpose
This header exposes cx18 I2C adapter lifecycle, subdevice registration, and subdevice lookup helpers.

## Important APIs, Types, and Functions
It declares `cx18_i2c_register()`, `cx18_find_hw()`, `init_cx18_i2c()`, and `exit_cx18_i2c()`.

## Control Flow
No runtime flow is in the header. Probe calls adapter initialization, card subdevice setup calls `cx18_i2c_register()`, and cleanup calls `exit_cx18_i2c()`.

## State and Persistence
I2C state resides in `struct cx18` adapters and V4L2 subdevice lists, not in the header.

## Dependencies and Integration Points
It is used by driver, card/subdevice, fileops, and ioctl code. `cx18_find_hw()` is the shared bridge from hardware flag masks to V4L2 subdev pointers.

## Risks and Edge Cases
Callers must ensure adapters are initialized before registering I2C subdevices. `cx18_find_hw()` returns the first exact `grp_id` match, so subdevices sharing a group would require care.

## Test Signals
Compile/link coverage plus successful I2C adapter registration and hardware subdev discovery in probe are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-io.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-io.c

## Purpose
This file contains non-inline cx18 MMIO utility routines for aligned memset, interrupt mask management, and encoder-memory page selection.

## Important APIs, Types, and Functions
Public functions are `cx18_memset_io()`, `cx18_sw1_irq_enable()`, `cx18_sw1_irq_disable()`, `cx18_sw2_irq_enable()`, `cx18_sw2_irq_disable()`, `cx18_sw2_irq_disable_cpu()`, and `cx18_setup_page()`.

## Control Flow
`cx18_memset_io()` writes an I/O region with byte/word/dword operations chosen to align to CX23418 addresses. SW1/SW2 enable helpers clear stale status, update cached masks, and write PCI interrupt-enable registers. Disable helpers clear cached masks and hardware enables. `cx18_sw2_irq_disable_cpu()` clears CPU-side ack interrupt enables. `cx18_setup_page()` programs the encoder memory page selector based on the target address.

## State and Persistence
The functions update cached IRQ masks in `struct cx18` and hardware interrupt/page registers. Memory contents and page selection are volatile hardware state.

## Dependencies and Integration Points
This code depends on `cx18-io.h` inline read/write helpers and interrupt register constants from `cx18-irq.h`. Firmware loading, mailbox handling, IRQ setup, SCB access, and buffer initialization rely on it.

## Risks and Edge Cases
Interrupt enable helpers assume status bits are write-one-to-clear and masks are synchronized with hardware. Page setup affects subsequent access to paged encoder memory, so callers must restore expected pages around firmware and debug string reads. `cx18_memset_io()` assumes destination alignment behavior important to the chip.

## Test Signals
Validate firmware load across page boundaries, mailbox interrupts waking wait queues, no stale SW1/SW2 interrupts at init, and correct memory clearing or initialization where this memset helper is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-io.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-io.h

## Purpose
This header defines cx18 MMIO access wrappers for reliable CX23418 register and encoder-memory operations. It centralizes readback/retry behavior for writes.

## Important APIs, Types, and Functions
Inline APIs include raw and normal `readl/writel`, `writew`, `writeb`, retrying variants, `_noretry` variants, `cx18_writel_expect()`, `cx18_memcpy_fromio()`, register accessors `cx18_write_reg*()` and `cx18_read_reg()`, and encoder-memory accessors `cx18_write_enc()` and `cx18_read_enc()`. It also declares interrupt mask and page helpers implemented in `cx18-io.c`.

## Control Flow
Write helpers loop up to `CX18_MAX_MMIO_WR_RETRIES`, checking readback after each write. `cx18_writel_expect()` waits for a masked expected value rather than raw equality and ignores all-ones reads when that cannot be a valid expected value. Register helpers apply offsets to `cx->reg_mem`; encoder helpers apply offsets to `cx->enc_mem`.

## State and Persistence
The helpers do not hold state but mutate hardware registers and memory. Their retry behavior is a driver-wide reliability policy for suspect MMIO writes.

## Dependencies and Integration Points
The header depends on `cx18-driver.h` for `struct cx18` and retry limits. It is used by nearly every cx18 implementation file, especially firmware, mailbox, GPIO, I2C, IRQ, and A/V code.

## Risks and Edge Cases
Readback after writes can be expensive but is required for reliability on this hardware. `_noretry` variants bypass protection and should be limited to sequences where readback is not valid or upload protocol needs exact timing. Paged encoder memory access still requires callers to manage `cx18_setup_page()`.

## Test Signals
Stress firmware load, repeated register programming, and capture start/stop under high interrupt load. MMIO debug traces or hardware failures after replacing retrying helpers with raw writes would be high-risk signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-ioctl.c

## Purpose
This file implements the V4L2 ioctl surface for cx18 video, MPEG, tuner, audio, VBI, encoder commands, advanced register access, events, and vb2 YUV operations.

## Important APIs, Types, and Functions
Public helpers are `cx18_service2vbi()`, `cx18_expand_service_set()`, `cx18_get_service_set()`, `cx18_set_funcs()`, `cx18_do_s_std()`, `cx18_do_s_frequency()`, and `cx18_do_s_input()`. The static `cx18_ioctl_ops` table wires many `vidioc_*` callbacks. Internal helpers sanitize video formats, VBI service lines, index data, encoder commands, and status logging.

## Control Flow
Format ioctls clamp video size to hardware limits and select MPEG or YUV pixel formats. Standard changes reject radio/active capture, update 50/60 Hz state, dimensions, VBI geometry, cx2341x controls, and subdev standards. Input/frequency/audio changes mute, update subdevices, and unmute. VBI ioctls configure raw or sliced decoder modes and store VBI state. `VIDIOC_G_ENC_INDEX` drains IDX MDLs into V4L2 index entries. Encoder commands start, stop, pause, or resume firmware capture. `cx18_set_funcs()` installs the ops table on a video device.

## State and Persistence
The ioctls mutate `struct cx18` state: active input, audio input, standard, 50/60 Hz flags, cx2341x dimensions, YUV buffer geometry, VBI format, stream queues, pause flag, and counters. Settings last for the device lifetime or until changed.

## Dependencies and Integration Points
The file integrates V4L2 core, vb2 ioctls, cx2341x controls, A/V decoder subdevs, tuner/audio/video subdevs, GPIO reset, queue helpers, stream start/stop, and mailbox-backed firmware controls.

## Risks and Edge Cases
`cx18_do_s_input()` compares card `video_type` against `V4L2_INPUT_TYPE_TUNER`, while the table uses `CX18_CARD_INPUT_VID_TUNER`; this depends on both being value 1. VBI service-line validation must match decoder hardware constraints. Index buffers assume alignment enforced by module options. Debug register access can alter arbitrary mapped hardware registers under `CONFIG_VIDEO_ADV_DEBUG`.

## Test Signals
Run v4l2-compliance for capture nodes, switch standards/inputs/frequencies, test busy errors during capture, capture raw and sliced VBI, use `VIDIOC_G_ENC_INDEX`, issue encoder pause/resume/stop-at-GOP, and test vb2 YUV buffer ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-ioctl.h

## Purpose
This header declares ioctl helper functions shared by file operations, control callbacks, stream setup, and first-open initialization.

## Important APIs, Types, and Functions
It declares VBI helpers `cx18_service2vbi()`, `cx18_expand_service_set()`, and `cx18_get_service_set()`, video-device setup `cx18_set_funcs()`, and direct state-change helpers `cx18_do_s_std()`, `cx18_do_s_frequency()`, and `cx18_do_s_input()`.

## Control Flow
No executable flow is present. The declared helpers let non-ioctl paths reuse ioctl logic for initial input, standard, and frequency setup.

## State and Persistence
The implementation mutates `struct cx18` device state, VBI state, and subdevice state. The header stores no state.

## Dependencies and Integration Points
It requires V4L2 types such as `v4l2_std_id`, `v4l2_frequency`, `v4l2_sliced_vbi_format`, and `video_device`. It integrates driver initialization, file open/read, and control code with the ioctl implementation.

## Risks and Edge Cases
Because helpers bypass userspace ioctl dispatch, callers must hold the same serialization locks where required. Prototype changes affect several subsystems.

## Test Signals
Build coverage and first-open initialization are direct signals. Runtime should show initial standard/input/frequency setup producing the same state as userspace ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-irq.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-irq.c

## Purpose
This file implements the shared PCI interrupt handler for cx18. It dispatches firmware mailbox commands from CPU/APU to EPU-side driver code and wakes waiters for mailbox acknowledgments.

## Important APIs, Types, and Functions
The exported handler is `cx18_irq_handler()`. Helpers `xpu_ack()` wake CPU/APU mailbox wait queues for SW2 ack bits, and `epu_cmd()` forwards SW1 CPU/APU-to-EPU command interrupts to `cx18_api_epu_cmd_irq()`.

## Control Flow
The IRQ handler reads SW1, SW2, and HW2 status registers masked by cached enable masks, clears any asserted bits, logs high-volume IRQ details when enabled, processes SW1 mailbox commands first because firmware times out incoming mailboxes quickly, leaves HW2 I2C interrupts as a TODO, then processes SW2 acknowledgments. It returns `IRQ_HANDLED` only when at least one masked bit was present.

## State and Persistence
The handler consumes and clears hardware interrupt status bits and wakes wait queues. It relies on `cx->sw1_irq_mask`, `cx->sw2_irq_mask`, and `cx->hw2_irq_mask` maintained by I/O helpers.

## Dependencies and Integration Points
It depends on MMIO helpers, interrupt register constants, mailbox IRQ handling, and SCB mailbox layout. It is registered by `cx18_probe()` and disabled during removal before work queues are drained.

## Risks and Edge Cases
Ordering matters: SW1 command handling before SW2 ack handling prevents firmware-side mailbox timeout. Shared IRQs require returning `IRQ_NONE` for unrelated interrupts. HW2 I2C status is cleared but not otherwise handled. Incorrect masks can drop mailbox completions or cause interrupt storms.

## Test Signals
Capture start/stop and firmware API calls should produce mailbox acks without timeout. Shared IRQ systems should not show spurious handling. High-volume IRQ debug should show SW1/SW2 transitions during DMA and API calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-irq.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-irq.h

## Purpose
This header defines cx18 interrupt bit masks and register offsets used by IRQ, MMIO, firmware, I2C, and mailbox code.

## Important APIs, Types, and Functions
It defines HW2 I2C interrupt bits, HW2 clear/mask registers, SW1 set/status/PCI-enable registers, SW2 set/status/CPU-enable/PCI-enable registers, and declares `irqreturn_t cx18_irq_handler(int irq, void *dev_id);`.

## Control Flow
There is no executable flow. The constants control how code enables, disables, clears, and sends software interrupts between the host/EPU and firmware CPUs/APU.

## State and Persistence
Interrupt state is hardware-resident and cached in `struct cx18`; this header only names bits and offsets.

## Dependencies and Integration Points
It is consumed by `cx18-irq.c`, `cx18-io.c`, `cx18-i2c.c`, `cx18-firmware.c`, and `cx18-mailbox.c`. It forms the shared contract for mailbox wakeups and firmware signaling.

## Risks and Edge Cases
Wrong register offsets or bit masks can hang firmware API calls, miss DMA completions, or make shared IRQ handling noisy. SW1 and SW2 directionality must remain clear to avoid sending interrupts to the wrong processor.

## Test Signals
Firmware API calls, DMA done notifications, and I2C init stale-interrupt clears should work without timeout. Build errors catch declaration mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-mailbox.c

## Purpose
This file implements host-to-firmware and firmware-to-host mailbox communication for cx18. It sends encoder/API commands, handles acknowledgments and timeouts, processes incoming DMA completion/debug commands, and dispatches completed buffers to V4L2, DVB, or ALSA consumers.

## Important APIs, Types, and Functions
Public APIs are `cx18_api()`, `cx18_vapi_result()`, `cx18_vapi()`, `cx18_api_func()`, `cx18_api_epu_cmd_irq()`, and `cx18_in_work_handler()`. `api_info[]` maps cx23418 command IDs to CPU/APU targets and timeout flags. Incoming work helpers include `epu_dma_done_irq()`, `epu_debug_irq()`, `epu_dma_done()`, `cx18_mdl_send_to_dvb()`, `cx18_mdl_send_to_vb2()`, and `cx18_mdl_send_to_alsa()`.

## Control Flow
Outgoing `cx18_api_call()` serializes access to the target mailbox, clears stuck busy state if needed, writes command/args/error/request/ack fields, sends an SW1 interrupt, waits on the matching ack wait queue, reads returned args/error, and applies extra delay for slow commands. Incoming IRQ handling snapshots the firmware mailbox, detects stale self-acked mailboxes, copies MDL ack data or debug strings, acknowledges non-stale mailboxes quickly, and queues work. Workqueue context resolves handles to streams, finds completed MDLs, moves data to DVB demux, vb2 buffers, ALSA callback, or stream `q_full`, reloads firmware queues, and wakes readers.

## State and Persistence
Mailbox request/ack sequence numbers live in SCB memory. Per-device wait queues, mailbox locks, incoming work orders, stream queues, and MDL state coordinate progress. Stale flags record mailbox lag conditions for deferred work.

## Dependencies and Integration Points
The file depends on SCB layout, interrupt helpers, MMIO/page helpers, queue/stream helpers, DVB demux, vb2, optional ALSA PCM callbacks, and cx2341x control translation. It is the bridge between V4L2 controls/streaming and firmware.

## Risks and Edge Cases
Mailbox timing is delicate. Incoming commands must be acknowledged quickly or firmware self-acks and stale data may be processed defensively. Work-order pool exhaustion drops incoming processing. DMA MDL IDs are validated for stale mailboxes, but lost MDLs can still require queue recovery. Outgoing waits are uninterruptible and return `-EINVAL` on ack timeout.

## Test Signals
Stress concurrent capture streams, DVB TS feeding, YUV vb2 capture, ALSA PCM capture, MPEG index rotation, firmware debug messages, API timeout injection, and module removal while DMA completions are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-mailbox.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-mailbox.h

## Purpose
This header defines cx18 mailbox constants, firmware mailbox layouts, MDL acknowledgment layout, and mailbox/API function prototypes.

## Important APIs, Types, and Functions
Constants include `MAX_MB_ARGUMENTS`, `CX2341X_MBOX_MAX_DATA`, reserved handles, and processor IDs `APU`, `CPU`, `EPU`, and `HPU`. `struct cx18_mdl_ack` describes firmware completion data for MDLs. `struct cx18_mailbox` defines request/ack fields, reserved space, command, up to six args, and error. Prototypes include `cx18_api()`, `cx18_vapi_result()`, `cx18_vapi()`, `cx18_api_func()`, `cx18_api_epu_cmd_irq()`, and `cx18_in_work_handler()`.

## Control Flow
No executable flow lives in the header. It defines the shared memory protocol consumed by the outgoing API path, IRQ path, workqueue path, and SCB structures.

## State and Persistence
Mailbox instances live in the firmware SCB memory region and are mirrored into `cx18_in_work_order` objects for deferred handling. The header itself stores no state.

## Dependencies and Integration Points
The mailbox structures are dictated by firmware and must match `cx18-scb.h` layout. The API function declarations connect cx2341x controls, stream management, firmware init, IRQ handling, and incoming work.

## Risks and Edge Cases
Changing structure layout, reserved fields, argument count, or processor IDs would break firmware communication. `CX2341X_MBOX_MAX_DATA` is larger than cx18 mailbox args for compatibility, so callers must respect `MAX_MB_ARGUMENTS` when sending commands.

## Test Signals
Successful firmware API commands, DMA completion processing, no mailbox timeout logs, and correct argument/error propagation are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-mailbox.h -->
