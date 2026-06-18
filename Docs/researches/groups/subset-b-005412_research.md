# Research: subset-b-005412

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_hw.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_hw.h

## Purpose
This header is the AV7110 firmware and hardware communication contract for the SAA7146-based full-featured DVB cards. It defines the dual-ported RAM layout, DEBI transfer modes, firmware command classes, command IDs, data-channel message IDs, GPIO assignments, boot protocol constants, and convenience wrappers used by the rest of the AV7110 driver to talk to the onboard ARM firmware.

## Important APIs, Types, and Constants
Important enum groups include `av7110_bootstate`, recording/playback formats, OSD palette modes, video output modes, firmware queue status flags, section filter flags, OSD/PID/MPEG/audio/request/encoder commands, record/play states, and `av7110_command_type`. The command type enum is central because calls to `av7110_fw_cmd()` combine a command class, command ID, argument count, and 16-bit arguments.

The header declares the core hardware entry points implemented elsewhere: `av7110_bootarm()`, `av7110_firmversion()`, `av7110_wait_msgstate()`, `av7110_fw_cmd()`, `av7110_fw_request()`, `av7110_debiwrite()`, `av7110_debiread()`, `av7110_diseqc_send()`, and optional OSD functions when `CONFIG_DVB_AV7110_OSD` is enabled. It also exposes firmware-version helpers `FW_CI_LL_SUPPORT()`, `FW_4M_SDRAM()`, and `FW_VERSION()`.

DEBI helper inlines split interrupt-context and normal-context access. `iwdebi()`, `mwdebi()`, and `irdebi()` are intended for interrupt paths and do not take `av7110->debilock`; `wdebi()` and `rdebi()` wrap DEBI access with `spin_lock_irqsave()`. Mailbox helpers `ARM_ResetMailBox()`, `ARM_ClearMailBox()`, and `ARM_ClearIrq()` operate on the DPRAM IRQ mailbox registers. Firmware wrappers `SendDAC()`, `av7710_set_video_mode()`, `vidcom()`, `audcom()`, and `Set22K()` translate higher-level operations into firmware commands.

## Control Flow and State
The file does not implement a runnable state machine by itself, but it defines the state addresses and command encodings used by the runtime state machines in the AV7110 firmware loader, IRQ handler, DVB frontend glue, IR handling, OSD code, and V4L2 analog module. Boot state is exchanged through `AV7110_BOOT_STATE`, `AV7110_BOOT_SIZE`, `AV7110_BOOT_BASE`, and `AV7110_BOOT_BLOCK`. Firmware commands use `COMMAND` and `COM_BUFF`; asynchronous data uses `RX_*`, `TX_*`, `HANDSHAKE_REG`, `COM_IF_LOCK`, `IRQ_RX`, and `IRQ_TX`.

State is persistent only in the device and firmware while the driver is loaded. The header maps persistent hardware mailboxes and DPRAM offsets, but no Linux-side storage is created here. Synchronization risk centers on correct use of interrupt-safe DEBI helpers versus locked helpers.

## Dependencies and Integration Points
This header depends on `av7110.h`, SAA7146 GPIO constants, Linux locking primitives, and the AV7110 struct layout, including `debi_virt` and `debilock`. It is included by AV7110 firmware, IR, V4L, MPEG/audio, OSD, CI, and DiSEqC code. The constants must stay aligned with firmware expectations; mismatched command IDs or DPRAM offsets would break hardware communication.

## Risks and Test Signals
Primary risks are hardware lockups from incorrect DEBI locking, endian/count mistakes in 16-bit firmware command fields, stale firmware command IDs, and mailbox clearing in the wrong context. Test signals are successful firmware boot/version read, DVB tuning, OSD command execution, DiSEqC tone/burst behavior, IR events, analog audio/video switching, and absence of DEBI timeout or firmware queue overflow logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ipack.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ipack.c

## Purpose
This file implements the AV7110 PES instant repacker. It consumes arbitrary byte chunks, recognizes MPEG PES start codes and headers, accumulates a complete or bounded packet in an `ipack`, optionally repairs AC3 private-stream substream metadata, and emits repacked PES buffers through a caller-supplied callback.

## Important APIs and Functions
`av7110_ipack_init()` allocates the packet buffer with `vmalloc()`, records the callback, clears repack flags, and calls `av7110_ipack_reset()`. `av7110_ipack_reset()` clears parser state fields such as `found`, `cid`, `plength`, flags, PTS bookkeeping, and byte counts. `av7110_ipack_free()` releases the `vmalloc()` buffer. `av7110_ipack_flush()` forces emission for packets with indefinite maximum length when enough bytes have been found.

`av7110_ipack_instant_repack()` is the core streaming parser. It searches for `00 00 01`, validates the stream ID against MPEG program/private/audio/video ranges, reads PES length and MPEG1/MPEG2 header fields, copies header/payload bytes into the packet buffer through `write_ipack()`, emits complete packets, resets state, and recursively processes trailing bytes in the same input chunk. `send_ipack()` finalizes length bytes and invokes `p->func()`. In MPEG2 private stream 1 with `p->repack_subids`, it uses `dvb_filter_get_ac3info()` to recompute AC3 frame counts and offsets.

## Control Flow and State
The parser is incremental. `p->found` is a byte-position state variable through start code, stream ID, PES length, and optional header. `p->mpeg` selects MPEG1 versus MPEG2 header rules. `p->done` marks stream IDs that should be skipped rather than emitted. `p->plength` defaults to `MMAX_PLENGTH - 6` for unspecified PES length, causing flush behavior to be caller-driven. `write_ipack()` handles output buffer overflow by filling the remaining space, sending a partial packet, and recursively writing the rest into a fresh packet with a preserved PES header.

The only persistence is the in-memory `struct ipack` and its allocated buffer. There is no locking in this file; callers must serialize access to an `ipack`.

## Dependencies and Integration Points
It depends on `dvb_filter.h` for stream IDs, flags, `struct ipack`, `MMAX_PLENGTH`, and AC3 parsing declarations, and on `av7110_ipack.h` for public prototypes. It uses `vmalloc()` because packet buffers can be larger than small stack or slab-friendly allocations. The callback integrates with AV7110 MPEG/audio/video paths that need repacked PES output.

## Risks and Test Signals
Risks include malformed PES causing parser desynchronization, AC3 metadata adjustment using insufficient bytes, recursion depth on pathological oversized input, caller-provided buffer sizes too small for expected repack output, and lack of internal locking. Test signals include feeding split start codes across calls, MPEG1 and MPEG2 PES with PTS/DTS, private stream AC3 packets, unspecified-length PES with flush, small output buffer boundaries, malformed stream IDs, and callback byte lengths matching PES length fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ipack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ipack.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ipack.h

## Purpose
This small header exposes the AV7110 PES repacker lifecycle and input functions. It intentionally does not define `struct ipack`; callers include `dvb_filter.h` for the parser state structure and stream constants.

## Important APIs
The public functions are `av7110_ipack_init()`, `av7110_ipack_reset()`, `av7110_ipack_instant_repack()`, `av7110_ipack_free()`, and `av7110_ipack_flush()`. The init callback signature is `void (*func)(u8 *buf, int size, void *priv)`, matching the emitter used by `send_ipack()`.

## Control Flow and State
The header defines no control flow by itself. The lifecycle implied by the API is initialize once, feed byte chunks repeatedly, optionally flush an open indefinite-length packet, reset when needed, and free the allocated buffer.

## Dependencies and Integration Points
It requires a visible `struct ipack` and `u8` type from included kernel/media headers, normally through `dvb_filter.h`. It is used by AV7110 code that needs incremental PES parsing and callback emission.

## Risks and Test Signals
The main API risk is include-order fragility because `struct ipack` is not declared here. Tests should compile all call sites, verify init/free pairing, and exercise reset/flush behavior through `av7110_ipack.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ipack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ir.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ir.c

## Purpose
This file bridges AV7110 firmware IR command words to the Linux rc-core subsystem. It registers an `rc_dev`, configures the AV7110 firmware decoder for RC5, extended RC5, or RCMM, decodes interrupt-delivered firmware values into rc-core scancodes, and reports key events.

## Important APIs and Functions
`av7110_ir_handler()` is called from the AV7110 interrupt/data path with a firmware IR command. It reads `av7110->ir.ir_config`, decodes RC5/RC5 extended/RCMM command, address, scancode, and toggle bits, then calls `rc_keydown()`.

`av7110_set_ir_config()` sends firmware command `COMTYPE_PIDFILTER`/`SetIR` with the selected IR mode. `change_protocol()` is the rc-core protocol switch callback; it accepts `RC_PROTO_BIT_RCMM32` or `RC_PROTO_BIT_RC5`, chooses extended RC5 when firmware version is at least `0x2620`, updates `av7110->ir.ir_config`, and pushes the new mode to firmware. `av7110_ir_init()` allocates and registers the rc device, populating PCI input identity and the Hauppauge keymap. `av7110_ir_exit()` unregisters and frees the rc device.

## Control Flow and State
Initialization allocates `rcdev`, creates an input physical path from the PCI name, sets allowed protocols and `change_protocol`, stores `rcdev` in `av7110->ir.rcdev`, defaults firmware IR decoding to RC5, and registers with rc-core. Interrupt-time decoding is stateless except for the current protocol config. Protocol changes are persisted in `av7110->ir.ir_config` and firmware. Exit tears down the registered device.

## Dependencies and Integration Points
The file depends on `rc-core`, `av7110.h`, and `av7110_hw.h`. Firmware command integration uses `av7110_fw_cmd()`, `COMTYPE_PIDFILTER`, and `SetIR`. Input identity is derived from the SAA7146/PCI device stored in `av7110->dev->pci`.

## Risks and Test Signals
Risks include protocol mismatch between firmware and rc-core, extended RC5 only being valid on newer firmware, double-free if unregister/free semantics change, and event loss when `rcdev` is unset. Test signals are successful rc device registration, `ir-keytable` protocol switching, RC5 and RCMM key events with correct scancodes/toggle behavior, and firmware command failures during protocol changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_v4l.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_v4l.c

## Purpose
This file provides the V4L2 interface for SAA7146-based AV7110 cards, including normal DVB video capture exposure and special analog tuner/input support on DVB-C premium cards. It manages MSP34xx audio processor access, SAA7113 video decoder setup, analog tuner programming, input/output/audio ioctls, sliced WSS VBI output, video standard switching, and SAA7146 video/VBI device registration.

## Important APIs and Functions
`msp_writereg()` and `msp_readreg()` perform I2C transactions to MSP34x0/MSP34x5 audio processors based on `av7110->adac_type`. `ves1820_writereg()`, `tuner_write()`, `ves1820_set_tv_freq()`, and `stv0297_set_tv_freq()` program analog tuner/demodulator hardware, including opening the frontend I2C gate for STV0297.

`av7110_dvb_c_switch()` is the central routing function. It switches between DVB input and analog inputs, updates audio source/volume registers, configures SAA7113 input selection, toggles tuner GPIOs, sends firmware `ADSwitch`, updates SAA7146 HPS source/sync, and swaps active PAL/NTSC timing tables.

V4L2 ioctl handlers cover tuner query/set, frequency get/set, input enumeration/get/set, output enumeration/get/set, audio enumeration/get/set, sliced VBI capabilities and formats, and VBI writes. `av7110_vbi_write()` validates WSS payloads and sends firmware `SetWSSConfig`. `av7110_init_analog_module()` probes MSP devices, initializes MSP/SAA7113/tuner state, chooses analog tuner flags from PCI subsystem IDs, and configures SAA7146 stream registers. `av7110_init_v4l()` initializes SAA7146 video/video-vbi support and installs file operation callbacks. `av7110_exit_v4l()` unregisters devices and releases the SAA7146 video subsystem.

## Control Flow and State
Analog module init probes I2C addresses, sets `adac_type`, optionally sets `analog_tuner_flags`, writes large hardware register tables, and leaves the card in DVB mode. Runtime state is stored in `av7110->current_input`, `current_freq`, `vidmode`, `wssMode`, and `wssData`. `vidioc_s_input()` updates current input then calls `av7110_dvb_c_switch()`. `vidioc_s_frequency()` mutes audio, programs tuner frequency, starts stereo detection, records `current_freq`, and restores volume. VBI format negotiation gates WSS support on firmware version `>= 0x2623`.

State is hardware-persistent while the device is active: MSP/SAA7113/tuner registers, SAA7146 HPS source, firmware WSS mode, and current V4L2 standard. No separate disk persistence exists.

## Dependencies and Integration Points
The file depends on AV7110 core state, `av7110_hw.h`, `av7110_av.h`, Linux I2C, SAA7146 video/VBI helpers, V4L2 ioctls, PCI IDs, firmware command APIs, and frontend I2C-gate callbacks. It integrates analog capture into the same SAA7146 device used by DVB capture.

## Risks and Test Signals
Risks include card-specific magic register values, incomplete error propagation from many I2C writes, shared static `standard[]` state across devices, firmware-version-dependent WSS paths, tuner unit conversions differing between V4L2 and hardware, and GPIO side effects on DVB-C variants. Test signals include V4L2 device registration, enumerating one or four inputs depending on analog hardware, successful input switching without lost video/audio, tuner set/get frequency behavior, PAL/NTSC standard changes invoking `av7110_set_vidmode()`, WSS VBI writes on supported firmware, and clean unregister on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_v4l.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/dvb_filter.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/dvb_filter.c

## Purpose
This file provides small DVB stream helper routines used by AV7110: AC3 header parsing and PES-to-TS packetization. It is not a full demux; it supplies format-specific utility code for legacy AV7110 MPEG paths.

## Important APIs and Functions
`dvb_filter_get_ac3info()` scans a memory buffer for the AC3 sync word `0x0b77`, validates enough bytes exist, derives bitrate, sample frequency, and frame size from lookup tables, sets `struct dvb_audio_info`, and optionally logs the stream characteristics.

`dvb_filter_pes2ts_init()` initializes a 188-byte TS packet template with sync byte, PID high/low bytes, continuity counter, callback, and private data. `dvb_filter_pes2ts()` packetizes a PES byte range into TS packets, setting payload-start on the first packet when requested, emitting full 184-byte payload packets, then a final adaptation-field padded packet for a short tail.

## Control Flow and State
AC3 parsing is stateless beyond filling the supplied `dvb_audio_info`. PES-to-TS state is stored in `struct dvb_filter_pes2ts`: a reusable TS packet buffer, continuity counter, callback, and callback private data. Every emitted packet increments the 4-bit continuity counter. The callback return value can stop packetization early.

## Dependencies and Integration Points
It depends on `dvb_filter.h`, kernel logging/string helpers, and callback users in the AV7110 MPEG path. The packetizer emits already-formed TS packets through a callback rather than writing to a device itself.

## Risks and Test Signals
Risks include AC3 frame lookup indexes with malformed headers, callbacks seeing a reused mutable buffer, PID high-byte masking left to the initializer, and payload/adaptation padding correctness. Test signals are AC3 buffers with sync at offsets, invalid/short AC3 buffers returning `-1`, continuity counter wrap at 16 packets, exact 184-byte PES chunks, final short packet adaptation length and stuffing bytes, and callback error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/dvb_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/dvb_filter.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/dvb_filter.h

## Purpose
This header defines the stream constants and small state structures shared by the AV7110 MPEG repacker/filter helpers. It covers MPEG PES stream IDs, MPEG video start codes, PTS/DTS flags, TS packet flags, adaptation flags, packet length limits, the `ipack` parser state, video/audio metadata structures, and PES-to-TS callback APIs.

## Important APIs and Types
`dvb_filter_pes2ts_cb_t` and `struct dvb_filter_pes2ts` define the packetizer callback contract. Function declarations are `dvb_filter_pes2ts_init()`, `dvb_filter_pes2ts()`, and `dvb_filter_get_ac3info()`.

`struct ipack` is the central state object used by `av7110_ipack.c`; it contains parser counters, PES IDs and length bytes, header flags, PTS buffer, callback fields, caller data, and `repack_subids`. `struct dvb_video_info`, `struct mpg_picture`, and `struct dvb_audio_info` describe parsed media metadata for legacy filter users.

## Control Flow and State
The header itself has no runtime flow, but it defines state machines consumed elsewhere. `struct ipack` records incremental PES parser state across byte chunks. `struct dvb_filter_pes2ts` records TS continuity state across PES packetization calls. Constants such as `MAX_PLENGTH`, `MMAX_PLENGTH`, and `IPACKS` bound parser behavior.

## Dependencies and Integration Points
It includes `<linux/slab.h>` and `<media/demux.h>`, and is included by AV7110 repacker and DVB filter implementation. It is legacy media helper infrastructure, with names overlapping generic DVB concepts but scoped here under the AV7110 staging tree.

## Risks and Test Signals
Risks include ABI-like coupling because parser code relies on exact field names and constants, weak type encapsulation, and large length constants permitting substantial buffer requirements. Test signals come from compiling all consumers, exercising PES parser state transitions, AC3 info parsing, TS packetization, and validating media metadata users if enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/dvb_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/sp8870.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/sp8870.c

## Purpose
This file implements a DVB-T frontend driver for the Spase SP8870 demodulator. It probes the demodulator over I2C, loads external firmware into instruction RAM, configures OFDM tuning parameters, manages TS output and an I2C gate, exposes DVB frontend operations, and reports status/BER/signal/uncorrected blocks.

## Important APIs and Functions
`sp8870_writereg()` and `sp8870_readreg()` implement 16-bit register transactions over I2C. `sp8870_firmware_upload()` validates firmware size, stops the controller, programs instruction RAM size registers, and writes firmware chunks to register `0xCF0A` starting at offset `0x0A`. `sp8870_microcontroller_stop()` and `sp8870_microcontroller_start()` control the system controller.

`configure_reg0xc05()` maps frontend modulation, hierarchy, and HP code rate to the demodulator configuration register, selecting explicit parameters or autoprobing for AUTO values. `sp8870_set_frontend_parameters()` stops the controller, asks the tuner to set parameters, configures sample rate/carrier/channel bandwidth/transmission mode/register `0xc05`, clears pending status, and restarts the controller. `sp8870_set_frontend()` wraps that with firmware-lockup recovery by polling data-valid and retrying up to five times.

`sp8870_init()` wakes TS output, requests firmware through `config->request_firmware`, uploads firmware once, and writes fixed post-upload registers. DVB ops also include `sp8870_sleep()`, `sp8870_i2c_gate_ctrl()`, `sp8870_get_tune_settings()`, `sp8870_read_status()`, `sp8870_read_ber()`, `sp8870_read_signal_strength()`, `sp8870_read_uncorrected_blocks()`, and `sp8870_release()`. `sp8870_attach()` allocates state, checks register readability, initializes `dvb_frontend.ops`, and exports the frontend.

## Control Flow and State
Probe/attach only verifies presence and returns a frontend. The first frontend init wakes the device, blocks for firmware, uploads it, and sets `state->initialised` so later init calls skip firmware loading. Tuning stops the microcontroller, programs tuner and demodulator registers, restarts, then waits for data-valid. Sleep tristates TS output. Debug-only globals count lockups and channel switches.

Persistent state is in `struct sp8870_state`: I2C adapter, config pointer, frontend object, and the `initialised` bit. Device register and firmware state persist in hardware until reset/sleep/unload.

## Dependencies and Integration Points
The file depends on Linux firmware loading, I2C, DVB frontend core, tuner ops, `sp8870.h`, and module parameters. Integration happens through `sp8870_attach()` and `dvb_frontend_ops`; boards provide the demod I2C address and firmware request callback.

## Risks and Test Signals
Risks include missing/incorrect firmware, brittle magic register sequences, tuning retries masking firmware lockups, I2C transfer errors returning inconsistent negative values, AUTOs causing hardware autoprobe paths, and global debug counters not per-device. Test signals are successful attach, firmware upload log, DVB-T tune lock, status flags matching signal presence, BER/signal/ucblocks reads, i2c gate behavior for tuner access, sleep disabling TS output, and recovery logs under stress channel switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/sp8870.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/sp8870.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/sp8870.h

## Purpose
This header defines the board-facing configuration and attach API for the SP8870 DVB-T demodulator driver.

## Important APIs and Types
`struct sp8870_config` contains the demodulator I2C address and a firmware request callback. `sp8870_attach()` returns a configured `struct dvb_frontend *` when `CONFIG_DVB_SP8870` is reachable. When the driver is disabled, an inline stub logs a warning and returns `NULL`.

## Control Flow and State
No runtime control flow exists here beyond the conditional inline stub. Runtime state is allocated by `sp8870.c`; callers only provide immutable board configuration.

## Dependencies and Integration Points
The header includes DVB frontend and firmware declarations. It is consumed by board glue or AV7110 frontend setup code that conditionally attaches SP8870 hardware.

## Risks and Test Signals
Risks include firmware callback signature coupling and disabled-driver stubs causing attach failure at runtime. Test signals are compile coverage with `CONFIG_DVB_SP8870` enabled and disabled, expected warning from the stub, and successful frontend attach when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/sp8870.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/Kconfig

## Purpose
This Kconfig fragment declares deprecated Atmel/Microchip Image Sensor Controller staging drivers: SAMA5D2 ISC, SAMA7G5 XISC, and their hidden shared base.

## Important Options
`VIDEO_ATMEL_ISC` is a tristate for the deprecated SAMA5D2-style Image Sensor Controller. It depends on V4L platform drivers, video device and common clock support, `ARCH_AT91 || COMPILE_TEST`, and excludes `VIDEO_MICROCHIP_ISC_BASE` unless compile-testing. It selects media controller, V4L2 subdev API, DMA-contig vb2, regmap MMIO, V4L2 fwnode, and `VIDEO_ATMEL_ISC_BASE`.

`VIDEO_ATMEL_XISC` is the analogous deprecated eXtended ISC option for SAMA7G5. `VIDEO_ATMEL_ISC_BASE` is a hidden tristate defaulting to `n` and selected by both public options.

## Control Flow and State
Kconfig has no runtime flow. It controls which objects from the Atmel staging media directory are built and ensures the shared base is included when either SoC-specific driver is enabled.

## Dependencies and Integration Points
It integrates with the Linux media platform driver menu, V4L2/media controller subsystems, common clock framework, regmap MMIO, and the newer non-staging Microchip ISC base through the conflict dependency.

## Risks and Test Signals
Risks include deprecation/removal timing, configuration conflicts with the newer Microchip driver, and missing selected dependencies leading to link failures if symbols move. Test signals are `allyesconfig`/`COMPILE_TEST` builds, ARCH_AT91 builds, disabled conflict with `VIDEO_MICROCHIP_ISC_BASE`, and object inclusion matching the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/Makefile

## Purpose
This Makefile maps the deprecated Atmel ISC Kconfig symbols to the built objects.

## Important Build Rules
`atmel-isc-objs` contains `atmel-sama5d2-isc.o`, `atmel-xisc-objs` contains `atmel-sama7g5-isc.o`, and `atmel-isc-common-objs` contains `atmel-isc-base.o atmel-isc-clk.o`. The final object rules build `atmel-isc-common.o` for `CONFIG_VIDEO_ATMEL_ISC_BASE`, `atmel-isc.o` for `CONFIG_VIDEO_ATMEL_ISC`, and `atmel-xisc.o` for `CONFIG_VIDEO_ATMEL_XISC`.

## Control Flow and State
The Makefile has no runtime state. It ensures both SoC-specific drivers link against a shared common module/object when selected by Kconfig.

## Dependencies and Integration Points
It depends on the Kbuild object-composition convention and Kconfig symbols in the adjacent Kconfig file. Link-time integration requires exported symbols from `atmel-isc-base.o` and `atmel-isc-clk.o` to be available to the SoC-specific object modules.

## Risks and Test Signals
Risks are stale object names after file moves or symbol changes and incorrect base selection causing unresolved exports. Test signals are module and built-in builds for each Kconfig combination and verifying `modinfo`/link output includes the intended object composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc-base.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc-base.c

## Purpose
This file is the shared V4L2/vb2/media-controller base for deprecated Atmel/Microchip ISC and XISC platform drivers. It handles format negotiation with a sensor subdevice, pipeline and DMA programming through SoC callbacks, video node registration, vb2 capture queues, streaming start/stop, DMA and histogram interrupts, auto white balance, V4L2 controls, async subdevice binding, and common regmap/pipeline initialization.

## Important APIs and Functions
Vb2 operations include `isc_queue_setup()`, `isc_buffer_prepare()`, `isc_start_streaming()`, `isc_stop_streaming()`, and `isc_buffer_queue()`. V4L2 ioctl support includes format enumeration/get/set/try, input operations, stream parameters, frame size enumeration, and vb2 ioctl forwarding. File operations `isc_open()` and `isc_release()` manage file handles and subdevice power.

Format negotiation is centered on `isc_try_fmt()` and `isc_set_fmt()`. `isc_try_fmt()` chooses a sensor media-bus format from supported subdevice formats, optionally prefers direct sensor output via `sensor_preferred`, validates whether requested output is compatible with RAW/GREY/YUV/RGB input, configures RLP/DMA fields with `isc_try_configure_rlp_dma()`, computes pipeline bits with `isc_try_configure_pipeline()`, asks the subdevice for a try format, and fills bytesperline/sizeimage. `isc_set_fmt()` applies the active subdevice format and promotes `try_config` to `config`.

Streaming configuration is handled by `isc_configure()`, `isc_set_pipeline()`, `isc_update_profile()`, `isc_crop_pfe()`, and `isc_start_dma()`. The SoC-specific driver supplies callbacks for DPC, CSC, CBC, CC, GAM, RLP, controls, and pipeline adaptation. `atmel_isc_interrupt()` retires DMA buffers on `ISC_INT_DDONE`, queues the next buffer, completes stop waits, and schedules AWB work on `ISC_INT_HISDONE`.

Auto white balance uses histogram helpers `isc_set_histogram()`, `isc_hist_count()`, `isc_wb_update()`, and `isc_awb_work()`. V4L2 controls are initialized in `isc_ctrl_init()`, with normal brightness/contrast/gamma controls and a clustered auto-white-balance/manual gains/offsets/do-white-balance set.

Async integration uses `atmel_isc_async_ops`: `isc_async_bound()` stores the single supported sensor, `isc_async_complete()` initializes work, vb2 queues, formats, controls, and registers the video node, and `isc_async_unbind()` unregisters and frees resources. Exported APIs are `atmel_isc_interrupt()`, `atmel_isc_async_ops`, `atmel_isc_subdev_cleanup()`, `atmel_isc_pipeline_init()`, and `atmel_isc_regmap_config`.

## Control Flow and State
Probe in the SoC file creates `struct isc_device`, then async notifier completion in this base constructs runtime media state. Open powers the sensor and reapplies the current format. `VIDIOC_S_FMT` is blocked while vb2 is busy. Streamon starts the sensor, resumes runtime PM, configures PFE/RLP/DMA/pipeline/histogram, enables DMA-done interrupts, selects the first queued buffer, crops the front-end to requested size, and starts DMA. Interrupts complete frames and advance the queue. Streamoff sets `stop`, waits for current-frame completion, disables DMA IRQs, runtime-suspends the device, stops the subdevice, and returns active/queued buffers with error.

Persistent driver state lives in `struct isc_device`: active and try format config, current V4L2 format, supported format list, vb2 queue and DMA queue, current frame pointer, sequence counter, stop/completion state, controls and histogram state, locks, current sensor, pipeline regmap fields, and SoC callback pointers. Hardware state is persisted in ISC registers and subdevice state while the device is active.

## Dependencies and Integration Points
This base depends on V4L2 device/subdev/fwnode/control/event/ioctl APIs, videobuf2 DMA-contig, media controller async notifier, regmap/regmap fields, runtime PM, platform IRQs, and SoC-specific callbacks and register offsets from `atmel-isc.h`. It integrates with SAMA5D2 and SAMA7G5 files through exported functions and shared `struct isc_device`.

## Risks and Test Signals
Risks include complex format fallback behavior, RAW-only assumptions for AWB, racing AWB register updates with DMA capture, buffer queue underflow, streamoff timeouts, one-sensor-only enforcement, error paths that must unwind mutex/work/control/video resources, and deprecated code diverging from newer Microchip ISC behavior. Test signals include media graph binding, video node registration, `v4l2-compliance`, format try/set across RAW/YUV/RGB/GREY, vb2 streaming with multiple buffers, DMA-done interrupt frame sequencing, streamoff timeout absence, AWB auto and one-shot behavior, runtime PM balance, and clean async unbind/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc-base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc-clk.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc-clk.c

## Purpose
This file implements common clock-provider support for Atmel/Microchip ISC clocks. It registers ISC-generated clocks with the common clock framework, manages parent/rate/divider selection through ISC registers, gates clocks, waits for clock-programming stability, and cleans up providers on driver removal.

## Important APIs and Functions
Clock ops include `isc_clk_prepare()`, `isc_clk_unprepare()`, `isc_clk_enable()`, `isc_clk_disable()`, `isc_clk_is_enabled()`, `isc_clk_recalc_rate()`, `isc_clk_determine_rate()`, `isc_clk_set_parent()`, `isc_clk_get_parent()`, and `isc_clk_set_rate()`. `isc_wait_clk_stable()` polls `ISC_CLKSR_SIP` for up to about 1 ms before/after clock changes.

`isc_clk_register()` constructs an `isc_clk` for `ISC_ISPCK` or `ISC_MCK`, reads clock parents from DT, adjusts parent count for ISPCK, selects clock names, sets `CLK_SET_RATE_GATE | CLK_SET_PARENT_GATE`, registers with `clk_register()`, and for MCK exposes an OF clock provider. `atmel_isc_clk_init()` initializes both clock slots and registers clocks; `atmel_isc_clk_cleanup()` removes the OF provider and unregisters any valid clocks.

## Control Flow and State
Prepare resumes runtime PM and waits for stable clock programming. Enable writes divider and parent selection under `isc_clk->lock`, then writes `ISC_CLKEN` and verifies the status bit. Disable writes `ISC_CLKDIS` under the same lock. Rate selection searches all parents and divisors from 1 through `ISC_CLK_MAX_DIV + 1`, choosing the closest rate and recording the best parent in the clock request. The selected parent index and divider are stored in `struct isc_clk` until enable applies them to hardware.

## Dependencies and Integration Points
It depends on the common clock framework, OF clock provider APIs, runtime PM, regmap, and `struct isc_device`/`struct isc_clk` from `atmel-isc.h`. SoC probes call `atmel_isc_clk_init()` after enabling the host clock and call cleanup on removal or probe failure.

## Risks and Test Signals
Risks include parent-count assumptions, runtime PM recursion or imbalance during clock ops, stale divider/parent state if enable fails, global provider removal when only optional ISPCK exists, and clock-stability timeout sensitivity. Test signals include clock summary showing MCK/ISPCK, setting camera sensor clock rates through DT consumers, runtime PM get/put balance, clock enable/disable register bits, rate rounding accuracy, and clean unregister on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc-regs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc-regs.h

## Purpose
This header defines the ISC/XISC register map, bit fields, masks, and SoC-specific register offsets used by the deprecated Atmel media drivers. It is the low-level hardware programming contract for control, front-end cropping, clocking, interrupts, image pipeline modules, histogram, DMA, and version registers.

## Important Constants
The file defines control registers `ISC_CTRLEN`, `ISC_CTRLDIS`, and `ISC_CTRLSR` with capture/profile/histogram bits; PFE config registers and polarity/CCIR/MIPI/BPS fields; clock enable/disable/status/config registers; interrupt enable/disable/mask/status and `ISC_INT_DDONE`/`ISC_INT_HISDONE`; DPC, WB, CFA, CC, GAM, VHXS, CSC, CBC, SUB422, SUB420, RLP, HIS, DMA, VERSION, and histogram entry registers.

SoC offset constants distinguish SAMA5D2 and SAMA7G5 layouts for CSC, CBC, subsampling, RLP, histogram, DMA, version, and histogram entries. RLP and DMA constants encode packing modes, YUV byte orders, planar/packed DMA modes, burst sizes, and DMA view modes.

## Control Flow and State
This header has no executable control flow. It structures all register writes and regmap field allocations done in `atmel-isc-base.c`, `atmel-isc-clk.c`, and the SoC-specific files. State exists in hardware registers addressed by these constants.

## Dependencies and Integration Points
It depends on Linux bit operations and is included by every Atmel ISC source file in this subset. SoC drivers combine these constants with per-device offsets stored in `struct isc_reg_offsets`.

## Risks and Test Signals
Risks include incorrect masks/shifts causing register corruption, SoC offset mismatches, typo-prone BPS constants, and assumptions that SAMA5D2 and SAMA7G5 register layouts differ only by provided offsets. Test signals are successful capture across formats, clock configuration, interrupt delivery, histogram reads, register trace inspection, and comparing register writes against SoC datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc.h

## Purpose
This header defines the shared data model for the deprecated Atmel/Microchip ISC drivers. It describes ISC clocks, vb2 buffers, async sensor entities, media-bus formats, internal output configuration, histogram/AWB controls, register offsets, the main `isc_device`, callback hooks, and exported common APIs.

## Important APIs and Types
Key types are `struct isc_clk`, `struct isc_buffer`, `struct isc_subdev_entity`, `struct isc_format`, `struct fmt_config`, `struct isc_ctrls`, `struct isc_reg_offsets`, and `struct isc_device`. Pipeline bit constants describe enabled image-processing blocks from DPC through SUB420. Histogram constants define 512 entries and Bayer channels.

`struct isc_device` is the shared runtime object. It stores regmap, clocks, runtime device pointers, V4L2/video objects, vb2 queue state, DMA queue and current frame, active/try formats, controls, work and locks, regmap pipeline fields, async subdevice list/current subdevice, gamma tables, max dimensions, SoC callback functions, register offsets, and supported format lists.

Exported declarations include `atmel_isc_regmap_config`, `atmel_isc_async_ops`, `atmel_isc_interrupt()`, `atmel_isc_pipeline_init()`, `atmel_isc_clk_init()`, `atmel_isc_subdev_cleanup()`, and `atmel_isc_clk_cleanup()`.

## Control Flow and State
The header has no executable flow, but it defines the state passed between SoC probes and the common base. SoC-specific files allocate and fill `isc_device`; the common base mutates it during async bind, format negotiation, streaming, IRQ handling, AWB work, and cleanup. Clock state uses per-clock spinlocks and cached parent/divider values. DMA state uses a spinlocked queue and completion for streamoff.

## Dependencies and Integration Points
It depends on the common clock framework, platform devices, V4L2 controls/device, and vb2 DMA-contig. It is the primary integration point between the SAMA5D2/SAMA7G5 platform files and `atmel-isc-base.c`/`atmel-isc-clk.c`.

## Risks and Test Signals
Risks include struct layout coupling across modules, callback pointers left unset by SoC probe, missing lock usage around mutable fields, and stale comments such as `bpp` being described as bytes while code treats it as bits per pixel. Test signals are compile/link coverage of all exported symbols, probe paths filling every callback/offset, streaming across formats, AWB controls, and KASAN/lockdep during streamon/off and async unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-sama5d2-isc.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-sama5d2-isc.c

## Purpose
This file is the deprecated SAMA5D2-specific platform driver for the Atmel Image Sensor Controller. It supplies supported formats, register offsets, max dimensions, DMA burst configuration, image-pipeline callbacks, gamma tables, DT endpoint parsing, runtime PM, and platform probe/remove glue around the shared ISC base.

## Important APIs and Functions
The static format tables list controller output formats and sensor input media-bus formats, including Bayer 8/10/12-bit, GREY, YUYV, RGB565, and Y10. Pipeline callbacks include `isc_sama5d2_config_csc()`, `isc_sama5d2_config_cbc()`, `isc_sama5d2_config_cc()`, `isc_sama5d2_config_ctrls()`, `isc_sama5d2_config_dpc()`, `isc_sama5d2_config_gam()`, `isc_sama5d2_config_rlp()`, and `isc_sama5d2_adapt_pipeline()`.

`isc_sama5d2_config_rlp()` handles a SAMA5D2 quirk where YCYC is not available and interleaved YUV modes use YYCC. `isc_parse_dt()` reads graph endpoints, parses V4L2 fwnode bus flags, and converts hsync/vsync/pclk polarity and BT.656 into PFE config bits. `atmel_isc_probe()` allocates and fills `struct isc_device`, initializes regmap/IRQ/pipeline/clocks/V4L2/async notifiers/runtime PM/ISPCK, sets ISPCK rate to hclock, reads version, and registers the platform driver. Remove and runtime PM functions disable clocks and cleanup shared resources.

## Control Flow and State
Probe creates device state, maps registers, requests the common interrupt handler, fills all SoC callbacks and offsets, initializes pipeline regmap fields, enables `hclock`, registers ISC-generated clocks, registers the V4L2 device, parses sensor endpoints, registers async notifiers, enables runtime PM, enables mandatory ISPCK, and reports hardware version. Async completion and streaming are delegated to the common base.

Persistent state is stored in `isc_device`, especially `gamma_table`, `gamma_max`, max dimensions, offsets, supported formats, DMA config, and `ispck_required`. Hardware state includes clocks, pipeline registers, and sensor endpoint configuration.

## Dependencies and Integration Points
It depends on platform resources, regmap MMIO, common clock, runtime PM, OF graph/fwnode parsing, V4L2 async, and the shared Atmel ISC base exports. Compatible string is `"atmel,sama5d2-isc"`.

## Risks and Test Signals
Risks include error-path ordering around `ispck` versus generic clock cleanup, endpoint parsing returning the last loop status, mandatory ISPCK assumptions, SAMA5D2 RLP quirks, and deprecated divergence from newer ISC drivers. Test signals include DT probe with parallel/BT.656 sensors, clock provider registration, ISPCK rate setting, video node creation, capture at max SAMA5D2 dimensions, RGB/YUV/Bayer format paths, runtime suspend/resume clock toggling, and clean remove after async sensor bind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-sama5d2-isc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-sama7g5-isc.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-sama7g5-isc.c

## Purpose
This file is the deprecated SAMA7G5 eXtended ISC platform driver. It adapts the common ISC base to XISC hardware by providing SAMA7G5 formats, larger dimensions, register offsets, full AXI DMA burst settings, XISC-specific DPC/gamma/CBC/RLP programming, optional MIPI front-end mode, runtime PM, and platform driver registration.

## Important APIs and Functions
The controller format table includes SAMA5D2-style formats plus UYVY, VYUY, and Y16 output capability. The input format table includes Bayer 8/10/12-bit, GREY, YUYV, UYVY, RGB565, and Y10. SoC callbacks include `isc_sama7g5_config_csc()`, `isc_sama7g5_config_cbc()`, `isc_sama7g5_config_cc()`, `isc_sama7g5_config_ctrls()`, `isc_sama7g5_config_dpc()`, `isc_sama7g5_config_gam()`, `isc_sama7g5_config_rlp()`, and `isc_sama7g5_adapt_pipeline()`.

`isc_sama7g5_config_dpc()` writes black-level offset and Bayer config for DPC. `isc_sama7g5_config_gam()` enables bipartite gamma mode. `isc_sama7g5_config_cbc()` also sets neutral hue and saturation. `xisc_parse_dt()` extends endpoint parsing with a `microchip,mipi-mode` DT boolean that sets `ISC_PFE_CFG0_MIPI`. `microchip_xisc_probe()` fills `isc_device`, initializes resources, registers async notifiers, enables runtime PM, reads version, and registers compatible `"microchip,sama7g5-isc"`.

## Control Flow and State
Probe flow mirrors SAMA5D2 but does not enable a separate ISPCK because `ispck_required` is false and XISC is clocked by MCK/hclock. It uses SAMA7G5 register offsets for shifted modules, DMA, version, and histogram entries. Runtime PM suspend/resume only disables/enables `hclock`.

Persistent state in `isc_device` includes larger max dimensions, `gamma_max = 0` for the single gamma table, AXI 32-beat DMA config, optional MIPI PFE flags per endpoint, and SAMA7G5 callbacks/offsets.

## Dependencies and Integration Points
It depends on the same platform/V4L2/regmap/clock/runtime PM infrastructure as SAMA5D2 plus the `microchip,mipi-mode` device-tree property. Common functionality is delegated to `atmel-isc-base.c` and `atmel-isc-clk.c`.

## Risks and Test Signals
Risks include MIPI mode being a device-wide property rather than endpoint-specific, offset mistakes for shifted XISC registers, single gamma index semantics, no separate ISPCK cleanup, and error paths around clock cleanup. Test signals include probe on `"microchip,sama7g5-isc"`, MIPI and parallel endpoint parsing, video capture up to 3264x2464, UYVY/VYUY/Y16 format negotiation, DPC/gamma register writes, runtime PM clock balance, and clean async removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-sama7g5-isc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/Kconfig

## Purpose
This Kconfig fragment enables the i.MX5/6 V4L2 media-controller staging drivers.

## Important Option
`VIDEO_IMX_MEDIA` is a tristate depending on `ARCH_MXC || COMPILE_TEST`, `HAS_DMA`, `VIDEO_DEV`, and `IMX_IPUV3_CORE`. It selects media controller support, V4L2 fwnode, V4L2 mem2mem, vb2 DMA-contig, and the V4L2 subdev API.

## Control Flow and State
There is no runtime flow. The option controls whether the i.MX media common, i.MX6 media graph, CSI, MIPI CSI2, VDIC, and IC subdevice objects are built.

## Dependencies and Integration Points
The option integrates with the i.MX IPUv3 core, Linux media controller, V4L2 subdevice, fwnode, mem2mem, and DMA-contiguous buffer frameworks.

## Risks and Test Signals
Risks are missing IPUv3 symbols, compile-test-only coverage hiding runtime DT issues, and broad object inclusion from a single option. Test signals include `ARCH_MXC` builds, `COMPILE_TEST` builds, module load on i.MX5/6, and media graph enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/Makefile

## Purpose
This Makefile composes the i.MX media driver objects selected by `CONFIG_VIDEO_IMX_MEDIA`.

## Important Build Rules
`imx-media-common-objs` groups common capture/device/of/utils code. `imx6-media-objs` groups the core i.MX6 media device, internal subdevs, IC common/PRP/PRPENCVF, VDIC, and CSC/scaler. `imx6-media-csi-objs` groups CSI and frame interval monitor support. The option also builds `imx6-mipi-csi2.o` directly.

## Control Flow and State
No runtime state exists in this file. It determines link composition and therefore which internal symbols are available inside the i.MX media staging module set.

## Dependencies and Integration Points
It depends on Kbuild object aggregation and the `VIDEO_IMX_MEDIA` Kconfig symbol. The IC files in this subset are linked into `imx6-media.o`.

## Risks and Test Signals
Risks include stale object names, accidental omission of an object needed by internal references, and all-or-nothing build inclusion. Test signals are clean built-in/module builds and successful symbol resolution for IC, VDIC, CSI, MIPI CSI2, and capture helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic-common.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic-common.c

## Purpose
This file is the common registration wrapper for i.MX Image Converter subdevices. It maps media group IDs to task-specific IC operation tables, initializes the common `imx_ic_priv`, registers the V4L2 subdevice, and unregisters/cleans up task-specific resources.

## Important APIs and Functions
`imx_media_ic_register()` allocates `struct imx_ic_priv`, stores the IPU device and IPU pointer, maps group IDs to `IC_TASK_PRP`, `IC_TASK_ENCODER`, or `IC_TASK_VIEWFINDER`, initializes `priv->sd` with the selected `imx_ic_ops`, configures entity ops/function/owner/flags/group/name, invokes the task-specific `init()`, and registers the subdevice with the supplied `v4l2_device`.

`imx_media_ic_unregister()` looks up `imx_ic_priv`, calls the task-specific `remove()`, unregisters the subdevice, and cleans up the media entity.

## Control Flow and State
The wrapper has a simple dispatch table: PRP uses `imx_ic_prp_ops`, while encoder and viewfinder use `imx_ic_prpencvf_ops`. Task-specific private state is stored through `priv->task_priv` during the init callback. Registration names are derived from group ID and IPU number.

## Dependencies and Integration Points
It depends on V4L2 device/subdev APIs, media entity APIs, IPU numbering, `imx-media.h` group IDs/name helpers, and task ops from `imx-ic-prp.c` and `imx-ic-prpencvf.c`. It is called by i.MX media device setup code when instantiating internal IPU IC subdevices.

## Risks and Test Signals
Risks include invalid group IDs returning `-EINVAL`, init failures leaking partially initialized subdev fields, and unregister assuming valid task ID and initialized task private state. Test signals include media graph creation for PRP, PRPENC, and PRPVF, failure injection in task init/register, and clean unregister with media entity cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic-prp.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic-prp.c

## Purpose
This file implements the i.MX IC preprocess router subdevice. It represents the PRP node that routes frames from CSI or VDIC into PRPENC and/or PRPVF downstream tasks, handles media-link constraints, propagates formats and frame intervals, chooses the IC source mux, and starts/stops upstream streaming.

## Important APIs and Functions
`struct prp_priv` stores pads, locks, source and downstream subdev pointers, validated CSI ID, a single mirrored media-bus format, frame interval, and stream count. `prp_start()` programs `ipu_set_ic_src_mux()` to select CSI or VDIC as the IC source. `prp_stop()` is currently empty.

Pad ops implement format enumeration, get/set format, get/set frame interval, and link validation. `prp_set_fmt()` bounds sink dimensions to 32..4096 with 16-pixel width alignment and 2-line height alignment, validates IPU YUV/RGB formats, and mirrors source pads to the sink format. `prp_link_setup()` enforces one upstream source, one PRPENC sink, one PRPVF sink, and disallows VDIC-to-PRPENC. `prp_link_validate()` runs default validation, finds the CSI subdevice when needed, enforces VDIC restrictions, and records CSI0/CSI1 ID.

`prp_s_stream()` validates links, only performs hardware/upstream start on transition from zero to one stream and stop on one to zero, then maintains `stream_count`. `prp_registered()` initializes default 1/30 frame interval and default mbus format. `prp_init()` allocates private state, initializes pads and mutex, and `imx_ic_prp_ops` exposes the operation table.

## Control Flow and State
Media graph setup populates `src_sd`, `sink_sd_prpenc`, and `sink_sd_prpvf`. Format state is stored as one active `format_mbus` mirrored to all pads. Link validation determines whether the source is VDIC or CSI and stores `csi_id`. Streaming sets the IPU IC source mux, calls upstream `s_stream`, and reference-counts multiple downstream users through `stream_count`.

No persistent disk state exists. Hardware state is limited to the IC source mux and upstream stream state.

## Dependencies and Integration Points
It depends on i.MX media helper APIs, V4L2 subdev/media entity operations, IPUv3 mux control, and group IDs for CSI/VDIC/PRPENC/PRPVF. It is registered via `imx_ic_prp_ops` from `imx-ic-common.c` and connects internal media graph entities.

## Risks and Test Signals
Risks include incorrect stream-count transition logic, link state races guarded only by the mutex, VDIC restrictions enforced at link setup/validation, default format propagation not modeling distinct downstream requirements, and `prp_stop()` doing no hardware cleanup beyond upstream stop. Test signals include media-ctl link enable/disable combinations, VDIC-to-PRPENC rejection, CSI ID validation for both CSI ports, format propagation, frame interval get/set, and streaming with one and two downstream consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic-prp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic-prpencvf.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic-prpencvf.c

## Purpose
This file implements the i.MX IC PRP encoder/viewfinder capture subdevice. It takes frames from the PRP router, performs IC resize/colorspace conversion and optional rotation/flips through IPUv3 channels, feeds a capture video device, manages vb2 buffer completion, handles EOF/error interrupts, and exposes pad formats, frame sizes, frame intervals, media links, and rotation controls.

## Important APIs and Functions
`struct prp_priv` stores IC/IPU resources, output/rotation channels, active capture buffers, underrun and rotation DMA buffers, media sink/source state, per-pad mbus formats and pixel formats, controls, rotation mode, IRQ/timer state, stream count, sequence, and error flags.

Resource helpers `prp_get_ipu_resources()` and `prp_put_ipu_resources()` acquire/release the IC task and output/rotation IDMAC channels based on encoder or viewfinder task. Buffer helpers `prp_setup_vb2_buf()`, `prp_unsetup_vb2_buf()`, and `prp_vb2_buf_done()` manage the two active IPU buffers, queued capture buffers, underrun buffer fallback, timestamps, sequence, and error completion on NFB4EOF.

Interrupt handlers are `prp_eof_interrupt()` and `prp_nfb4eof_interrupt()`. EOF completes or advances capture buffers, toggles the IPU double-buffer index, and refreshes an EOF timeout timer. NFB4EOF marks the next frame as error. `prp_eof_timeout()` reports fatal capture-device error.

Pipeline setup functions include `prp_setup_channel()`, `prp_setup_rotation()`, `prp_unsetup_rotation()`, `prp_setup_norotation()`, `prp_unsetup_norotation()`, and `prp_unsetup()`. They calculate CSC, configure CPMEM image layout/burst/rotation/interweave/odd chroma skipping, initialize IC tasks, allocate rotation buffers when needed, link rotation channels, enable IC/IDMAC channels, and select double buffers.

`prp_start()` acquires resources, allocates underrun buffer, initializes counters/completions, configures rotation or non-rotation pipeline, requests EOF and NFB4EOF IRQs, starts upstream streaming, and starts the timeout timer. `prp_stop()` marks last EOF, waits for completion or timeout, stops upstream, frees IRQs, unsets hardware, returns active buffers as error, frees DMA buffers, deletes timer, and releases IPU resources.

Pad/control/media ops implement format enumeration, get/set/try formats, frame size enumeration, link setup, `s_stream`, frame interval get/set, registration/unregistration, and controls. `prp_bound_align_output()` enforces IC downscale and rotation alignment constraints. `prp_s_ctrl()` derives `rot_mode` from rotation/hflip/vflip and rejects changes that would alter active output bounds or occur while streaming. `prp_registered()` initializes formats, capture video device, and controls.

## Control Flow and State
Media graph setup links one upstream subdev to one capture video device. Active formats are stored per pad; sink changes propagate a default source format. Controls derive `rot_mode`, which decides whether the hardware path is direct IC-to-memory or IC-to-memory plus memory-to-IC-rotation plus rotation-to-memory. Streamon validates source/sink, performs setup only on zero-to-one transition, starts upstream after hardware is ready, then EOF IRQs drive frame completion. Streamoff waits for a final EOF before tearing down to avoid disabling active channels mid-frame.

Persistent state is in `prp_priv` while the subdevice exists: format/cc arrays, capture vdev, control values, resource pointers, active buffers, IRQ numbers, timer, stream count, sequence, and flags. DMA buffers are allocated per stream and freed at stop.

## Dependencies and Integration Points
It depends on V4L2 subdev/control/media APIs, i.MX media capture helpers, vb2 DMA-contig addresses, IPUv3 IC/IDMAC/CPMEM/rotation APIs, timer and IRQ infrastructure, and the common IC wrapper. Encoder and viewfinder tasks use different IPU channel IDs from the `prp_channel` table.

## Risks and Test Signals
Risks include complex teardown ordering around IRQs/timers/channels, underrun-buffer use hiding missing capture buffers, EOF timeout as fatal condition, interlaced/interweave stride handling, rotation-buffer allocation failures, stream-count transitions, refusing rotation changes when output alignment would change, and returning active buffers with error on normal stop. Test signals include capture without rotation, capture with 90/180/270 and h/v flips, planar YUV and interlaced formats, missing queued-buffer underrun behavior, EOF/NFB4EOF IRQ handling, timeout recovery, streamon/off stress, media link validation, frame size bounds, and `v4l2-compliance` on the generated capture node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic-prpencvf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic.h

## Purpose
This header defines the shared private wrapper and operation table for i.MX Image Converter internal subdevices.

## Important APIs and Types
`struct imx_ic_priv` stores the IPU device, IPU SoC pointer, embedded V4L2 subdevice, task ID, and task-specific private pointer. `struct imx_ic_ops` contains subdev ops, internal ops, entity ops, and task-specific `init()`/`remove()` callbacks. It declares the two task operation providers: `imx_ic_prp_ops` and `imx_ic_prpencvf_ops`.

## Control Flow and State
The header has no executable control flow. It defines how `imx-ic-common.c` dispatches to task implementations. Task state is anchored through `imx_ic_priv.task_priv`.

## Dependencies and Integration Points
It depends on V4L2 subdev declarations and is included by the common IC registration wrapper plus PRP/PRPENCVF implementations. It is internal to the i.MX media staging driver.

## Risks and Test Signals
Risks include task implementations not filling required ops or failing to initialize `task_priv`, and common unregister assuming valid callbacks. Test signals are registration/unregistration of all task IDs, media entity operations present in the graph, and compile coverage when either task implementation changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic.h -->
