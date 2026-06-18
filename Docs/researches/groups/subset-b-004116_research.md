# subset-b-004116 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-i2c.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-i2c.c

### Purpose
`cx88-i2c.c` provides the primary bit-banged I2C adapter for Conexant cx2388x/cx88 cards. It exposes the chip's internal I2C pins through Linux `i2c-algo-bit` so tuner, demodulator, EEPROM, audio, RTC, and IR helper drivers can be discovered and controlled by the rest of the cx88 media stack.

### Important APIs, Types, And Functions
The module parameters are `i2c_debug`, `i2c_scan`, and `i2c_udelay`; the last is clamped to at least 5 usec before adapter registration. The low-level callbacks `cx8800_bit_setscl()`, `cx8800_bit_setsda()`, `cx8800_bit_getscl()`, and `cx8800_bit_getsda()` manipulate `MO_I2C` through `core->i2c_state`. `cx8800_i2c_algo_template` packages those callbacks for `i2c_bit_add_bus()`. `do_i2c_scan()` probes all 7-bit addresses and prints known device hints from `i2c_devs`. The exported initializer is `cx88_i2c_init()`.

### Control Flow
Initialization copies the algorithm template into `core->i2c_algo`, wires `core->i2c_adap` to the PCI device and V4L2 device, creates a synthetic `core->i2c_client`, drives SCL/SDA high, and calls `i2c_bit_add_bus()`. If registration succeeds, selected Hauppauge HVR boards receive a four-byte transfer to the analog/digital tuner at address `0xc2 >> 1` to enable the analog demodulator. Optional scan mode then performs zero-length reads for diagnostic discovery.

### State, Persistence, And Dependencies
The lasting state is in `struct cx88_core`: adapter/client objects, `i2c_algo`, `i2c_state`, and `i2c_rc`. There is no persistent storage; bus state is hardware register state. The file depends on `cx88.h` register helpers, `MO_I2C`, Linux I2C core, `i2c-algo-bit`, PCI parent device lifetime, and V4L2 adapter data.

### Integration Points
This adapter is created by cx88 core setup before board-specific subdevices are attached. Other files use `core->i2c_rc` to skip I2C work on registration failure, and use `core->i2c_adap` for V4L2 I2C subdevice creation, IR receiver probing, WM8775/tvaudio probing, and tuner/demodulator access.

### Risks
The bit state cache must remain synchronized with `MO_I2C`; direct register writes elsewhere could confuse subsequent bit operations. Too-low `i2c_udelay` is guarded, but high bus capacitance or board wiring may still need slower timing. `do_i2c_scan()` is diagnostic only and may produce side effects on fragile devices. The Hauppauge tuner write is board-specific magic and lacks transfer result handling.

### Test Signals
Useful signals are successful `i2c_bit_add_bus()` registration, visible tuner/EEPROM subdevice probes, `i2c_scan=1` output on known cards, verified HVR analog tuner enablement, no I2C timeout regressions at default delay, and clean failure behavior when the adapter cannot register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-input.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-input.c

### Purpose
`cx88-input.c` implements remote-control input support for cx2388x boards. It handles GPIO-polled scancode remotes, raw IR sampling through the chip's IR sample FIFO, and I2C-attached IR receiver discovery.

### Important APIs, Types, And Functions
`struct cx88_IR` stores the `rc_dev`, core pointer, user count, GPIO masks, polling interval, raw sampling flag, hrtimer, and last GPIO sample. Public functions are `cx88_ir_init()`, `cx88_ir_fini()`, `cx88_ir_start()`, `cx88_ir_stop()`, `cx88_ir_irq()`, and `cx88_i2c_init_ir()`. Key helpers include `cx88_ir_handle_key()`, `cx88_ir_work()`, `cx88_ir_open()`, `cx88_ir_close()`, and `get_key_pvr2000()`.

### Control Flow
`cx88_ir_init()` allocates an rc-core device, switches on `core->boardnr`, and configures one of many board-specific key maps, GPIO registers, key masks, polling periods, or raw-sampling addresses. Polling remotes start an hrtimer that repeatedly calls `cx88_ir_handle_key()`. Raw-sampling remotes enable `PCI_INT_IR_SMPINT`, program `MO_DDS_IO` from `ir_samplerate`, enable `MO_DDSCFG_IO`, and feed pulse/space durations from `MO_SAMPLE_IO` in `cx88_ir_irq()`. GPIO decoding normalizes a few special board layouts, extracts masked bits, and emits `rc_keydown_notimeout()`, `rc_keyup()`, or NECX scancodes where needed. `cx88_i2c_init_ir()` probes known I2C receiver addresses with read-style SMBus transactions and instantiates `ir_video`/Hauppauge Z8 devices.

### State, Persistence, And Dependencies
State is in `core->ir`, the rc-core device, hrtimer state, `core->pci_irqmask`, and `core->init_data` for I2C IR. The driver does not persist learned codes. It depends on rc-core, `ir_extract_bits()`, I2C SMBus, cx88 GPIO/sample registers, and board ID constants from `cx88.h`.

### Integration Points
The video driver starts/stops IR during suspend/resume and final removal. Core interrupt handling routes IR sample interrupts to `cx88_ir_irq()`. I2C IR setup depends on the primary I2C adapter from `cx88-i2c.c`. Userspace sees standard rc-core input devices with board-specific key maps.

### Risks
Most behavior is board-table-driven; incorrect masks or polling intervals cause missing or repeated keys. `cx88_ir_fini()` unregisters then explicitly frees `ir->dev`, which is a lifetime-sensitive rc-core pattern. Polling timers must be cancelled on last close and suspend. Sample decoding assumes 32-bit sample layout and fixed samplerate math. I2C receiver probing avoids quick writes deliberately; changing this could break devices that only answer reads.

### Test Signals
Test with representative raw-sampling Hauppauge/TBS/TeVii boards, GPIO-polled WinFast/PixelView/PowerColor boards, and Leadtek PVR2000 I2C IR. Check open/close user counts, suspend/resume restart, `ir-keytable` events, NECX scancodes, no hrtimer activity after close, and no interrupt storm when raw sampling is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-mpeg.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-mpeg.c

### Purpose
`cx88-mpeg.c` is the PCI function #2 manager for cx2388x MPEG transport-stream hardware. It owns MPEG DMA setup, transport-stream interrupts, buffer queue helpers, power-management hooks, and a registration/arbitration layer used by `cx88-dvb` and `cx88-blackbird` subdrivers.

### Important APIs, Types, And Functions
Exported DMA helpers are `cx8802_start_dma()`, `cx8802_buf_prepare()`, `cx8802_buf_queue()`, and `cx8802_cancel_buffers()`. Driver-manager exports are `cx8802_get_driver()`, `cx8802_register_driver()`, and `cx8802_unregister_driver()`. Internal control includes `cx8802_stop_dma()`, `cx8802_restart_queue()`, `cx8802_mpeg_irq()`, `cx8802_irq()`, `cx8802_request_acquire()`, and `cx8802_request_release()`.

### Control Flow
Probe obtains a shared `cx88_core`, rejects boards without MPEG support, allocates `cx8802_dev`, initializes PCI/DMA/IRQ state, adds the device to `cx8802_devlist`, stores `core->dvbdev`, and asynchronously requests DVB/blackbird modules based on `core->board.mpeg`. Subdrivers register a `cx8802_driver`; the manager validates callbacks/access mode, clones the registration per live device, installs manager callbacks, and calls the subdriver probe under `core->lock`. Starting DMA configures SRAM channel 28, writes TS packet length, programs DVB or blackbird-specific `TS_*` and pinmux registers, resets counters, enables PCI/TS interrupts, and starts the TS DMA engine. IRQ handling acknowledges PCI/TS bits, delegates shared core interrupts, wakes queued vb2 buffers on RISC1, and stops DMA on opcode/general errors.

### State, Persistence, And Dependencies
Persistent runtime state is `cx8802_dev`, `mpegq.active`, `vb2_mpegq`, packet size/count, `ts_gen_cntrl`, suspend state, `drvlist`, and `core->active_type_id`/`active_ref`/input snapshots. There is no disk persistence. Dependencies include PCI, DMA masks, videobuf2, cx88 SRAM/RISC helpers, board metadata, and optional module autoloading.

### Integration Points
DVB and blackbird modules use this file as the owner of function #2 hardware and must acquire/release access before programming shared resources. `cx88-video.c` checks `core->dvbdev->vb2_mpegq` before changing analog format. The shared `cx88_core_irq()` handles non-TS bits in the same PCI interrupt path.

### Risks
Hardware arbitration is subtle: DVB acquisition changes `core->input` to the DVB input and release restores `last_analog_input`. Incorrect active reference accounting can strand hardware in the wrong mode or allow blackbird/DVB conflicts. DMA error handling stops engines but does not fully drain buffers except cancel paths. Module autoload work must be flushed on remove. Resume contains FIXME reinitialization notes and relies on queue restart.

### Test Signals
Exercise DVB and blackbird attach/detach, concurrent access refusal, stream start/stop, buffer completion counts from `MO_TS_GPCNT`, IRQ loop guard, suspend/resume with active queues, module autoload, and board-specific TS pinmux/SOP programming for HVR/Pinnacle/DVICO boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-mpeg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-reg.h -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-reg.h

### Purpose
`cx88-reg.h` is the register and bitfield map for cx2388x/cx88 hardware. It gives the rest of the driver symbolic names for PCI function control, DMA engines, video/audio/TS/VIP/host blocks, GPIO/I2C, RISC instructions, interrupt masks, audio mode constants, and video format constants.

### Important APIs, Types, And Functions
This header contains no functions; its API is preprocessor constants. Major groups include PCI config aliases (`F0_*` to `F4_*`), DMA interrupt/status registers (`MO_PCI_INT*`, `MO_VID_INT*`, `MO_TS_INT*`), DMA channel pointers/counts, video registers (`MO_INPUT_FORMAT`, scaling/filter/capture registers), audio DSP registers (`AUD_*`), TS registers (`MO_TS_*`, `TS_*`), GPIO/I2C registers (`MO_GP*`, `MO_I2C`), RISC opcodes (`RISC_WRITE`, `RISC_JUMP`, `RISC_IRQ1`), and capability constants such as `PCI_INT_IR_SMPINT`, `EN_BTSC_*`, `CX23880_CAP_CTL_*`, and `ColorFormat*`.

### Control Flow
There is no executable control flow. The constants drive control flow in other files by selecting register offsets and bit masks for DMA start/stop, interrupt acknowledgement, audio-standard programming, input muxing, and I2C/IR bit-banging.

### State, Persistence, And Dependencies
The header has no mutable state. Its values are an implicit ABI between driver code and the cx2388x memory-mapped register layout. It is included by `cx88.h`, which wraps these offsets with `cx_read()`, `cx_write()`, and related helpers.

### Integration Points
Every cx88 functional module depends on this header: video/VBI use video DMA and capture bits, MPEG uses TS registers and channel 28, input uses GPIO/IR sample registers, I2C uses `MO_I2C`, audio uses `AUD_*`, and core code uses RISC opcodes and SRAM channel register addresses.

### Risks
Misdefined offsets or masks cause direct hardware misprogramming and can manifest as silent capture failure, bus errors, IRQ storms, or corrupt DMA. Comments include a FIXME about possible host register typos, so host-related definitions deserve caution. Duplicate-style aliases such as `AUD_APB_IN_RATE_ADJ`/`AUD_I2SCNTL` intentionally share an offset and must not be "cleaned up" blindly.

### Test Signals
Validation is indirect: successful capture, VBI, MPEG TS, audio, I2C, and IR operation across boards. Register-dump comparisons against known hardware docs, IRQ mask/status sanity, RISC DMA completion, and `CONFIG_VIDEO_ADV_DEBUG` register reads are useful when touching this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-tvaudio.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-tvaudio.c

### Purpose
`cx88-tvaudio.c` programs the cx2388x audio DSP for analog TV/radio standards and manages stereo/SAP/NICAM mode selection. It converts V4L2 tuner audio mode requests into low-level `AUD_*` register recipes and runs a background monitor for standards that need software stereo follow-up.

### Important APIs, Types, And Functions
Public functions are `cx88_set_tvaudio()`, `cx88_newstation()`, `cx88_get_stereo()`, `cx88_set_stereo()`, and `cx88_audio_thread()`. Register helpers include `set_audio_registers()`, `set_audio_start()`, and `set_audio_finish()`. Standard-specific programming functions are `set_audio_standard_BTSC()`, `set_audio_standard_NICAM()`, `set_audio_standard_A2()`, `set_audio_standard_EIAJ()`, and `set_audio_standard_FM()`. `cx88_detect_nicam()` samples `AUD_NICAM_STATUS2`.

### Control Flow
Audio-standard setup mutes, writes `AUD_INIT`/reset, applies static `struct rlist` register sequences, restarts audio DMA to avoid buzz, enables I2S output for blackbird or DAC output for analog, then restores shadowed volume. `cx88_set_tvaudio()` selects recipes from `core->tvaudio`: BTSC, A2/NICAM by world standard, EIAJ, FM, or I2S ADC. For BG/DK/M/I/L, it programs A2 mono first, then NICAM, samples NICAM status up to six times, and either keeps NICAM or falls back to A2 mono. `cx88_get_stereo()` reads `AUD_STATUS`, maps hardware mode to V4L2 tuner fields, and may call `cx88_dsp_detect_stereo_sap()` for software detection. `cx88_set_stereo()` honors manual override and adjusts standard-specific `AUD_CTL` bits or reprograms BTSC/NICAM recipes. The kthread wakes once per second, freezes cleanly, and auto-switches A2 mono/stereo only when no manual mode is set.

### State, Persistence, And Dependencies
State is in `core->tvaudio`, `audiomode_manual`, `audiomode_current`, `use_nicam`, `astat`, `last_change`, shadow audio registers, and the audio kthread pointer. Dependencies include cx88 register helpers, V4L2 tuner modes, `cx88_start_audio_dma()`/`cx88_stop_audio_dma()`, DSP stereo detection, and module parameters `always_analog` and `radio_deemphasis`.

### Integration Points
`cx88-video.c` calls this file during initial setup, input changes, radio open, and frequency changes. V4L2 tuner get/set operations expose its stereo decisions to userspace. Blackbird cards depend on I2S pass-through setup for MPEG encoder audio.

### Risks
The register tables are hardware-specific and sparsely documented. Reprogramming resets audio state and must preserve mute/volume through shadow registers. NICAM detection is timing-sensitive. Manual mode prevents automatic kthread changes, so forgotten resets would leave stale audio modes; `cx88_newstation()` clears this on channel/input changes. The `always_analog` option can alter blackbird pass-through expectations.

### Test Signals
Test BTSC stereo/SAP, PAL BG/DK/I/L with and without NICAM, FM deemphasis settings, I2S ADC audio-route boards, blackbird I2S output, tuner mode get/set via V4L2, channel-change reset behavior, kthread freeze/stop, and audible regressions such as buzz after DMA restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-tvaudio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-vbi.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-vbi.c

### Purpose
`cx88-vbi.c` implements V4L2 vertical blanking interval capture for cx8800 analog video devices. It defines VBI format negotiation, videobuf2 queue operations, RISC program creation, VBI DMA start/stop, and queue restart.

### Important APIs, Types, And Functions
Externally used functions are `cx8800_vbi_fmt()`, `cx8800_stop_vbi_dma()`, `cx8800_restart_vbi_queue()`, and exported `cx8800_vbi_qops`. Internal helpers are `cx8800_start_vbi_dma()`, `queue_setup()`, `buffer_prepare()`, `buffer_finish()`, `buffer_queue()`, `start_streaming()`, and `stop_streaming()`.

### Control Flow
Format negotiation returns fixed grey samples with `VBI_LINE_LENGTH`, offset 244, and NTSC/PAL-specific sampling rate, start lines, and line counts. Buffer setup selects a single plane sized to line count times line length times two fields. `buffer_prepare()` validates plane size, sets payload, and builds a RISC program with `cx88_risc_buffer()`. Queued buffers are linked into `dev->vbiq.active`; the first loops to itself and later buffers patch the previous RISC jump to chain DMA. Streaming starts by programming SRAM channel 24, enabling VBI capture bits in `MO_VBOS_CONTROL` and `VID_CAPTURE_CONTROL`, enabling video interrupts, and starting VBI DMA. Stop paths clear capture/DMA/interrupt bits and return all active buffers with `VB2_BUF_STATE_ERROR`.

### State, Persistence, And Dependencies
State lives in `dev->vbiq`, `dev->vb2_vbiq`, buffer RISC memory, and hardware counters/registers. The output is transient DMA data delivered through vb2 buffers. Dependencies include `cx88_risc_buffer()`, `cx88_sram_channel_setup()`, `cx88_wakeup()` in the video IRQ path, V4L2 standards, and DMA coherent allocation for RISC programs.

### Integration Points
`cx88-video.c` registers the VBI video device, initializes the vb2 queue with these ops, routes VBI ioctls to `cx8800_vbi_fmt()`, handles VBI RISC1 interrupts in `cx8800_vid_irq()`, and restarts VBI after resume.

### Risks
`start_streaming()` assumes at least one queued buffer because vb2 min queued buffers are configured in the video driver. Video and VBI share `MO_VID_DMACNTRL` and video interrupt masks, so stop paths must not inadvertently disrupt another active stream beyond intended shared bits. Line counts depend on current `core->tvnorm`; changing standards while queues are busy is guarded by video format logic elsewhere.

### Test Signals
Use `v4l2-ctl --stream-mmap --stream-from` or equivalent VBI capture on NTSC and PAL norms, verify buffer sizes and timestamps, confirm no active buffers remain after streamoff, test suspend/resume with VBI active, and check VBI RISC1 interrupt completions through `MO_VBI_GPCNT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-vbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-video.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-video.c

### Purpose
`cx88-video.c` is the main V4L2 analog video/radio driver for cx2388x function #0. It registers video, VBI, and optional radio devices; manages capture formats, controls, input muxing, tuner frequency, videobuf2 capture queues, video interrupts, power management, and helper subdevice setup.

### Important APIs, Types, And Functions
Public functions include `cx88_video_mux()`, `cx88_querycap()`, `cx88_enum_input()`, and `cx88_set_freq()`. Capture internals include `formats[]`, `format_by_fourcc()`, `start_video_dma()`, `stop_video_dma()`, `restart_video_queue()`, vb2 ops, `cx8800_vid_irq()`, and `cx8800_irq()`. V4L2 ioctl handlers cover video format, standards, inputs, tuner, frequency, debug registers, and radio. Probe/remove and PM are `cx8800_initdev()`, `cx8800_finidev()`, `cx8800_suspend()`, and `cx8800_resume()`.

### Control Flow
Probe allocates `cx8800_dev`, enables PCI/DMA, gets the shared core, requests the shared IRQ, builds audio/video controls, attaches WM8775/tvaudio/RTC/IR helper modules as needed, sets default BGR24 format, stores `core->v4ldev`, initializes NTSC and input 0 under `core->lock`, creates vb2 queues, registers video/VBI/radio devices, and starts the TV-audio kthread for tuner boards. Video streaming prepares RISC buffers according to field layout, chains active buffers, programs SRAM channel 21, applies scaler and color format, enables capture/interrupt bits, and wakes buffers from RISC1 interrupts. Input changes update GPIOs, mux bits, S-video filter/AFE bits, external WM8775 routing, and I2S ADC mode for baseband audio. Frequency changes notify tuner subdevices, cache returned frequency, wait briefly, and reset TV audio.

### State, Persistence, And Dependencies
State is shared between `cx8800_dev` and `cx88_core`: current format, width/height/field, input, tuner frequency, control handlers, video/VBI queues, IRQ masks, WM8775/RTC subdevices, kthread, and active RISC buffers. There is no disk persistence. Dependencies include V4L2 core/ioctls/events, videobuf2 DMA-SG, PCI DMA, cx88 core/SRAM/RISC helpers, tuner and audio subdevices, and constants from `cx88-reg.h`.

### Integration Points
The file coordinates with `cx88-vbi.c` for VBI qops, `cx88-tvaudio.c` for audio setup, `cx88-input.c` for IR suspend/remove behavior, `cx88-mpeg.c` through `core->dvbdev` busy checks, and board metadata from `cx88-cards.c`. Userspace interacts through `/dev/video*`, `/dev/vbi*`, and optional `/dev/radio*`.

### Risks
Shared registers and interrupt masks make video/VBI concurrency delicate. Format changes reject busy video, VBI, and MPEG queues, but input/frequency changes still affect shared analog state. Buffer chaining patches DMA RISC jump addresses in active buffers and must be protected by queue lock expectations. Remove/suspend ordering must stop kthread, IR, DMA, IRQs, and device registration without use-after-free. Some probe failures after `core` acquisition must clear `core->v4ldev`.

### Test Signals
Run V4L2 compliance, video capture in every advertised pixel format and field mode, standard changes, input switching, tuner/radio open/frequency operations, control writes including WM8775 propagation, streamoff error cleanup, IRQ error injection if possible, suspend/resume with active video/VBI, and concurrent DVB busy checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-vp3054-i2c.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-vp3054-i2c.c

### Purpose
`cx88-vp3054-i2c.c` implements a secondary bit-banged I2C bus for the DNTV Live! DVB-T Pro VP-3054 design. That board wires GPIO0 to SCL and GPIO1 to SDA, separate from the normal cx88 I2C adapter.

### Important APIs, Types, And Functions
The exported functions are `vp3054_i2c_probe()` and `vp3054_i2c_remove()`. Low-level `i2c-algo-bit` callbacks are `vp3054_bit_setscl()`, `vp3054_bit_setsda()`, `vp3054_bit_getscl()`, and `vp3054_bit_getsda()`. `vp3054_i2c_algo_template` defines timing and callback wiring. State is stored in `struct vp3054_i2c_state`.

### Control Flow
Probe returns success without action unless `core->boardnr` is `CX88_BOARD_DNTV_LIVE_DVB_T_PRO`. For the VP-3054 board, it allocates state, copies the bit-bang algorithm, initializes adapter parent/name/owner/data, drives SCL/SDA high, and registers the bus with `i2c_bit_add_bus()`. The set callbacks update cached `state` bits and write `MO_GP0_IO`, using output-enable bits to drive low and external pullups/tristate for high. Remove deletes the adapter and frees state only for the matching board.

### State, Persistence, And Dependencies
State is in `dev->vp3054`, its adapter/algorithm, and cached GPIO line state. There is no persistent storage. The file depends on `cx88.h`, `cx88-vp3054-i2c.h`, `i2c-algo-bit`, GPIO register `MO_GP0_IO`, and the cx8802 device because the bus belongs to the MPEG/DVB side.

### Integration Points
The optional header stubs allow callers to invoke probe/remove unconditionally when `CONFIG_VIDEO_CX88_VP3054` may be disabled. DVB frontend code for the DNTV Live DVB-T Pro can use this adapter to reach board-specific demod/tuner devices.

### Risks
GPIO0/GPIO1 are shared hardware pins; any other GPIO programming on the board could disrupt this bus. The high/low implementation relies on external pullups and output-enable bits, so inverted or changed board wiring would break transfers. Registration failure frees state and clears `dev->vp3054`; callers must handle absent secondary bus.

### Test Signals
On VP-3054 hardware, verify the secondary adapter appears, frontend I2C devices respond, bus reads/writes succeed under load, and removal unloads cleanly. On all other boards, probe/remove should be no-ops with no adapter side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-vp3054-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-vp3054-i2c.h -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-vp3054-i2c.h

### Purpose
`cx88-vp3054-i2c.h` declares the secondary VP-3054 I2C state and probe/remove interface. It also provides compile-time stubs when VP-3054 support is disabled.

### Important APIs, Types, And Functions
`struct vp3054_i2c_state` contains an `i2c_adapter`, an `i2c_algo_bit_data`, and cached GPIO `state`. When `CONFIG_VIDEO_CX88_VP3054` is enabled, the header declares `vp3054_i2c_probe()` and `vp3054_i2c_remove()`. Otherwise, inline versions return success or do nothing.

### Control Flow
The header has no runtime control flow beyond the conditional inline stubs selected by `IS_ENABLED(CONFIG_VIDEO_CX88_VP3054)`. This lets common DVB/driver code compile and call the functions without scattering preprocessor conditionals.

### State, Persistence, And Dependencies
The state structure is owned by `cx8802_dev->vp3054` when enabled. The header assumes `struct cx8802_dev`, `struct i2c_adapter`, `struct i2c_algo_bit_data`, and `u32` are visible through the including cx88 headers.

### Integration Points
It is included by `cx88-vp3054-i2c.c` and by any cx88 DVB-side code that probes/removes the VP-3054 secondary bus. The stubs preserve source compatibility for builds without the feature.

### Risks
The header lacks a local include guard in this snapshot, relying on include ordering/once-like usage; repeated direct inclusion could redefine the struct or inline functions. Any change to `struct vp3054_i2c_state` affects the implementation and `cx8802_dev` field lifetime.

### Test Signals
Build with `CONFIG_VIDEO_CX88_VP3054=y/m` and disabled to confirm both real declarations and stubs compile. Runtime tests are covered by the `.c` file: adapter creation on DNTV Live DVB-T Pro and no-op behavior otherwise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-vp3054-i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88.h -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88.h

### Purpose
`cx88.h` is the central private header for the cx2388x/cx88 driver family. It defines shared board IDs, board/input metadata, core/device structures, DMA buffer types, register access macros, subdevice call helpers, and cross-file function prototypes.

### Important APIs, Types, And Functions
Key types are `struct cx88_core`, `struct cx8800_dev`, `struct cx8802_dev`, `struct cx8802_driver`, `struct cx88_board`, `struct cx88_input`, `struct cx88_buffer`, `struct cx88_dmaqueue`, and `struct sram_channel`. Key enums include `cx88_board_type`, `cx8802_board_access`, `cx88_itype`, `cx88_audio_chip`, `cx88_tvaudio`, and FM deemphasis. Macros include `CX88_NORMS`, VBI constants, board IDs, `INPUT(nr)`, `call_hw()`, `call_all()`, WM8775 control wrappers, `cx_read()`/`cx_write()`/`cx_andor()`/shadow-register helpers, and `norm_maxw()`/`norm_maxh()`.

### Control Flow
The header itself does not execute, but it encodes control contracts. `call_hw()` opens optional I2C gates around V4L2 subdevice calls when I2C is available. Register macros assume a local variable named `core`, shaping all source files that use them. `cx8802_driver` callbacks define acquisition/release/probe/remove flow between MPEG manager and mini-drivers.

### State, Persistence, And Dependencies
`struct cx88_core` is the shared state across PCI functions: MMIO mappings, shadow audio registers, I2C adapter/client, V4L2 device/control handlers, board config, tuner/audio/input state, IR/I2C init data, locks, DVB/video cross-pointers, and MPEG active ownership. `cx8800_dev` owns analog video/VBI/radio devices and queues. `cx8802_dev` owns MPEG/DVB/blackbird queues and optional VP3054 state. Dependencies include Linux PCI/I2C/V4L2/videobuf2 headers, tuner/IR/WM8775/cx2341x interfaces, `cx88-reg.h`, and `xc2028.h`.

### Integration Points
Every cx88 source file includes this header. It is the contract between core, cards, video, VBI, input, tvaudio, MPEG, DVB, blackbird, ALSA, and optional VP3054 code. Userspace-visible behavior is indirectly shaped by constants such as supported norms, VBI dimensions, board tables, and device capabilities.

### Risks
Because register macros depend on lexical `core`, refactors can silently break or misdirect MMIO access. `core` state is shared across PCI functions and guarded by `core->lock` in only some paths, so field ownership must be respected. Board ID additions must stay synchronized with board tables. Optional compile-time sections change `struct cx8802_dev` layout. Shadow registers are required for write-only audio controls and must be updated through shadow helpers.

### Test Signals
Full cx88 build coverage across feature combinations (`DVB`, `BLACKBIRD`, `VP3054`) is essential. Runtime signals include correct board detection, V4L2 control registration, I2C subdevice calls through gates, video/VBI/MPEG queue operation, suspend/resume, and absence of cross-function active-type conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/Kconfig

### Purpose
`ddbridge/Kconfig` exposes Digital Devices PCIe bridge support to the kernel media configuration system. It defines the main `DVB_DDBRIDGE` tristate and an optional MSI default-setting knob.

### Important APIs, Types, And Functions
The primary symbol is `DVB_DDBRIDGE`, which depends on `DVB_CORE`, `PCI`, and `I2C`. With `MEDIA_SUBDRV_AUTOSELECT`, it selects many frontend/tuner/CAM helpers: LNBP21, STV6110x, STV090x, DRXK, TDA18271C2DD, STV0367, CXD2841ER, STV0910, STV6111, LNBH25, TDA18212, MXL5XX, and CXD2099. `DVB_DDBRIDGE_MSIENABLE` is a bool depending on `DVB_DDBRIDGE` and `PCI_MSI`.

### Control Flow
There is no runtime control flow. Kconfig selection determines which objects and dependent modules are built and whether MSI is enabled by default in the driver.

### State, Persistence, And Dependencies
The persistent state is build configuration. The help text documents supported Digital Devices bridge products and warns that default MSI may cause I2C errors with some SATA controllers, while module option `msi=0` can still disable it.

### Integration Points
The Makefile consumes `CONFIG_DVB_DDBRIDGE` to build `ddbridge.o` and `ddbridge-dummy-fe.o`. The selected subdrivers line up with frontend/CAM attach paths in the ddbridge source, including CXD2099 CI support in `ddbridge-ci.c`.

### Risks
Overselecting subdrivers can increase module footprint but avoids missing dependencies for automatic board support. Enabling MSI by default is explicitly experimental and may trade interrupt performance for I2C stability issues on some systems. Missing `MEDIA_SUBDRV_AUTOSELECT` requires users to configure needed demod/tuner drivers manually.

### Test Signals
Check `allyesconfig`/`allmodconfig` and minimal configs, module autoload with common Digital Devices cards, build behavior with/without `MEDIA_SUBDRV_AUTOSELECT`, and runtime interrupt/I2C stability with `DVB_DDBRIDGE_MSIENABLE` enabled and overridden by `msi=0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/Makefile

### Purpose
`ddbridge/Makefile` defines how the Digital Devices bridge driver is compiled and linked inside the kernel media tree.

### Important APIs, Types, And Functions
`ddbridge-objs` aggregates `ddbridge-main.o`, `ddbridge-core.o`, `ddbridge-ci.o`, `ddbridge-hw.o`, `ddbridge-i2c.o`, `ddbridge-max.o`, `ddbridge-mci.o`, and `ddbridge-sx8.o` into the `ddbridge` module. `obj-$(CONFIG_DVB_DDBRIDGE)` builds `ddbridge.o` and `ddbridge-dummy-fe.o`. `ccflags-y` adds include paths for `drivers/media/dvb-frontends/` and `drivers/media/tuners/`.

### Control Flow
There is no runtime control flow. Kbuild uses the object list and config symbol to decide module composition and compile include search paths.

### State, Persistence, And Dependencies
Persistent state is build metadata. The Makefile depends on Kbuild variables, the Kconfig symbol `CONFIG_DVB_DDBRIDGE`, and source/header availability in the frontend and tuner directories.

### Integration Points
`ddbridge-ci.c` is one component of the linked module, so CI support is always part of `ddbridge.o` when the driver is built. `ddbridge-dummy-fe.o` is built alongside the main module under the same config symbol.

### Risks
Forgetting to add new implementation objects here leads to link errors or missing functionality. Include-path changes can mask missing qualified includes. Splitting optional features would require matching Kconfig symbols and conditional object rules.

### Test Signals
Build the driver as built-in and module, verify all listed object files compile, run `modinfo ddbridge` on module builds, and ensure frontend/tuner headers resolve without relying on accidental global include paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-ci.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-ci.c

### Purpose
`ddbridge-ci.c` implements Common Interface (CI/CAM) support for Digital Devices bridge cards. It supports internal CI register-backed interfaces, external XO2 I2C-backed interfaces, and Sony CXD2099-based CI bridges, all exposed through the DVB EN50221 CA API.

### Important APIs, Types, And Functions
Public entry points are `ddb_ci_attach()` and `ddb_ci_detach()`. Internal EN50221 callbacks include `read_attribute_mem()`, `write_attribute_mem()`, `read_cam_control()`, `write_cam_control()`, `slot_reset()`, `slot_shutdown()`, `slot_ts_enable()`, and `poll_slot_status()` for internal CI, with `_xo2` equivalents for XO2. Helpers include `wait_ci_ready()`, `ci_attach()`, `write_creg()`, `ci_xo2_attach()`, and `ci_cxd2099_attach()`. `en_templ` and `en_xo2_templ` are callback templates; `cxd_cfgtmpl` configures CXD2099.

### Control Flow
Internal CI access writes bridge command registers such as `CI_DO_READ_ATTRIBUTES()`, waits for `CI_READY`, and reads `CI_BUFFER()` or `CI_READDATA()`. Slot reset powers the CAM, asserts reset, enables the interface, delays, and releases reset. XO2 access uses `i2c_read_reg*()`/`i2c_write_reg*()` at address `0x12` or `0x13` based on port type; control register writes update cached `port->creg`. CXD2099 attach clones the config, installs `port->en`, and probes the `cxd2099` module at I2C address `0x40`. `ddb_ci_attach()` dispatches by `port->type`, ensures `port->en`, and calls `dvb_ca_en50221_init()`. Detach unregisters any DVB device, releases EN50221, releases the optional I2C client, frees template-allocated data when owned, and clears `port->en`.

### State, Persistence, And Dependencies
Runtime state is in allocated `struct ddb_ci`, `port->en`, `port->en_freedata`, `port->creg`, and `port->dvb[0].i2c_client[0]`. There is no disk persistence. Dependencies include ddbridge register/IO/I2C helpers, `dvb_ca_en50221`, `dvb_module_probe()`/`release()`, port type constants, and CXD2099 configuration.

### Integration Points
The file is linked into `ddbridge.o` and called from core port setup/teardown when a CI-capable port is detected. It bridges low-level hardware operations to the standard DVB CA interface consumed by userspace CAM tools and demux pipelines.

### Risks
Ready waits return `-1` on timeout but some callers ignore the result after writes, so hardware stalls may surface as later EN50221 errors. Address bounds use `address > CI_BUFFER_SIZE`, leaving `address == CI_BUFFER_SIZE` to wrap via the mask; this boundary should be reviewed against hardware expectations. Ownership differs between CXD2099 (`port->en_freedata = 0`) and locally allocated templates, so detach order is lifetime-sensitive. XO2 I2C failures in reset/shutdown helpers are mostly ignored.

### Test Signals
Test internal, XO2, XO2_B, and Sony external CI ports with CAM insertion/removal, attribute memory reads, CAM control reads/writes, TS enable/bypass, reset/shutdown, timeout behavior, module unload/reload, and EN50221 userspace operations such as `dvb-fe-tool`/CAM menu access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-ci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-ci.h -->
## sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-ci.h

### Purpose
`ddbridge-ci.h` declares the attach/detach interface for Digital Devices bridge CI support.

### Important APIs, Types, And Functions
The header includes `ddbridge.h` for `struct ddb_port` and declares `int ddb_ci_attach(struct ddb_port *port, u32 bitrate);` plus `void ddb_ci_detach(struct ddb_port *port);`.

### Control Flow
The header has no executable control flow. Include guards prevent duplicate declarations. Runtime behavior is implemented in `ddbridge-ci.c`.

### State, Persistence, And Dependencies
No state is stored in the header. It depends on ddbridge core types and the caller-owned `ddb_port` lifetime. The `bitrate` argument is meaningful for CXD2099-backed CI attach and ignored by some other attach paths.

### Integration Points
Core ddbridge port initialization includes this header to attach CI handling for ports with internal, XO2, or Sony CI types, and teardown calls `ddb_ci_detach()` during device removal.

### Risks
The interface is intentionally small, so all ownership rules are implicit: callers must pass an initialized port with DVB adapter and I2C fields ready, and must detach before those resources disappear. Any signature change requires updates across ddbridge setup code.

### Test Signals
Compile coverage confirms declarations match implementation. Runtime validation follows `ddbridge-ci.c`: attach succeeds for CI-capable ports, detach releases EN50221/CXD2099 resources, and non-CI ports are rejected by callers or return errors cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-ci.h -->
