# subset-b-004196 research

Grouped research for the requested USB media driver source files. Each file section is bounded by reconciliation markers and preserves the source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/airspy/airspy.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/airspy/airspy.c

## Purpose
Implements the USB Video4Linux2 SDR driver for AirSpy receivers. It exposes the device as a V4L2 SDR capture node, translates V4L2 tuner/frequency/control operations into AirSpy vendor control messages, and streams raw 12-bit little-endian SDR samples from bulk endpoint `0x81` into videobuf2 buffers.

## Important APIs, types, and functions
The central state is `struct airspy`, which owns USB device pointers, a `video_device`, `v4l2_device`, `vb2_queue`, queued buffer list, streaming URBs, DMA buffers, current SDR format, ADC/RF frequencies, and V4L2 tuner gain controls. `airspy_ctrl_msg()` is the vendor command dispatcher for receiver mode, frequency, board/version reads, and gain/AGC controls. `airspy_start_streaming()` allocates coherent bulk buffers, builds URBs, submits them, then sends `CMD_RECEIVER_MODE` on. `airspy_urb_complete()` copies each completed bulk payload into the next queued vb2 buffer via `airspy_convert_stream()`. IOCTL handlers implement SDR format enumeration/get/set/try, tuner info, frequency bands, and frequency updates. Probe registers controls and the SDR video node; disconnect marks the device gone and unregisters it.

## Control flow and state
Probe allocates `struct airspy`, reads board ID/version, initializes vb2, V4L2 controls, and registers a `VFL_TYPE_SDR` device. Streaming begins through vb2 `start_streaming`: set `POWER_ON`, allocate six 64 KiB buffers and URBs, submit them, then enable receiver mode. URB callbacks run in atomic context, pop one queued frame buffer under `queued_bufs_lock`, copy bytes, set payload/timestamp/sequence, complete the vb2 buffer, and resubmit the URB. Stop streaming sends receiver mode off, kills/frees URBs and stream buffers, returns queued buffers with error, and clears `POWER_ON`.

## Dependencies and integration points
Depends on USB core, V4L2 device/ioctl/control/event APIs, vb2-vmalloc memory, and SDR pixel format `V4L2_SDR_FMT_RU12LE`. User space sees standard V4L2 read, mmap, poll, ioctl, streaming, tuner, frequency, and control interfaces. Hardware integration is through AirSpy vendor USB control requests and one bulk IN endpoint.

## Risks and test signals
`airspy_ctrl_msg()` chooses IN transfer direction for several setter commands, matching existing firmware API behavior but making command direction a key hardware compatibility risk. Streaming has drop behavior when no vb2 buffers are queued, tracked by `vb_full`. Race-sensitive areas are disconnect versus queued buffers, URB resubmission after errors, and lock ordering between `v4l2_lock` and `vb_queue_lock`. Test signals include successful probe/version logs, V4L2 capability and SDR format enumeration, setting RF frequency and gain controls, sustained stream-on/stream-off without URB leaks, monotonic frame sequence, sample-rate debug output, and no buffer overrun/drop messages under adequate user buffer depth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/airspy/airspy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/as102/Kconfig

## Purpose
Defines the kernel configuration entry for the Abilis AS102 USB DVB receiver driver.

## Important APIs, types, and functions
The single symbol is `DVB_AS102`, a tristate option named "Abilis AS102 DVB receiver". It depends on `DVB_CORE`, `USB`, `I2C`, and `INPUT`, and selects `FW_LOADER` because the driver can request and upload firmware blobs during registration.

## Control flow and state
This file does not contain runtime code. Its state effect is build-time selection: enabling the symbol includes the AS102 module and ensures firmware loader support is available. If built as module, the object is produced by the local Makefile as `dvb-as102`.

## Dependencies and integration points
Integrates with the media USB Kconfig tree and the DVB build system. The selected firmware loader is required by `as102_fw.c`, while DVB/USB/I2C/INPUT dependencies match the driver's DVB adapter, USB transport, frontend attachment, and input-related device support requirements.

## Risks and test signals
The main risk is configuration drift: missing a dependency can produce unresolved symbols, while an unnecessary hard dependency can hide the driver from valid configurations. Test signals are Kconfig visibility under media USB DVB options, successful `=m` and `=y` builds, and automatic inclusion of firmware loading support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/as102/Makefile

## Purpose
Builds the AS102 USB DVB receiver module from the driver, firmware, USB transport, and AS10x command source files.

## Important APIs, types, and functions
Defines `dvb-as102-objs` as `as102_drv.o`, `as102_fw.o`, `as10x_cmd.o`, `as10x_cmd_stream.o`, `as102_usb_drv.o`, and `as10x_cmd_cfg.o`. Adds the resulting module with `obj-$(CONFIG_DVB_AS102) += dvb-as102.o`.

## Control flow and state
No runtime control flow exists. The object list determines link composition: `as102_drv.c` provides module registration and DVB glue, `as102_usb_drv.c` exports the `as102_usb_driver`, firmware upload lives in `as102_fw.c`, and protocol operations are split across command files.

## Dependencies and integration points
Adds a compiler include path to `drivers/media/dvb-frontends`, needed for AS102 frontend headers such as `as102_fe.h` and `as102_fe_types.h`. Integrates with kbuild's media module build flow.

## Risks and test signals
Risks are missing object files or include paths when command APIs are moved. Test signals are a clean module link for `CONFIG_DVB_AS102=m`, no undefined references to `as102_usb_driver` or AS10x command helpers, and correct module name `dvb-as102`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_drv.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_drv.c

## Purpose
Provides the AS102 DVB-layer integration and module entry point. It bridges DVB demux/frontend callbacks to AS10x firmware commands and USB private operations supplied by `as102_usb_drv.c`.

## Important APIs, types, and functions
Module parameters are `dual_tuner`, `fw_upload`, `pid_filtering`, `ts_auto_disable`, `elna_enable`, and DVB `adapter_nr`. `as102_dvb_register()` registers a DVB adapter, demux, dmxdev, AS102 frontend, mutexes, and optionally requests firmware upload. `as102_dvb_unregister()` tears them down. Feed callbacks `as102_dvb_dmx_start_feed()` and `as102_dvb_dmx_stop_feed()` manage `as102_dev_t.streaming`, optional PID filters, and stream start/stop. Frontend operations `as102_set_tune()`, `as102_get_tps()`, `as102_get_status()`, `as102_get_stats()`, and `as102_stream_ctrl()` call AS10x command helpers under the bus adapter lock.

## Control flow and state
Probe in the USB file calls `as102_dvb_register()` after USB buffers are ready. The DVB demux calls start/stop feed for each active PID; the first feed starts USB URBs and possibly firmware streaming, while the last feed stops them. `pid_filtering` changes demux filter count and sends add/delete PID commands. `ts_auto_disable` toggles whether firmware start/stop commands are sent around transport streaming. `elna_enable` controls whether `CONTEXT_LNA` is programmed before turning the demod on.

## Dependencies and integration points
Depends on DVB core demux/dmxdev/frontend APIs, AS102 frontend attach from `as102_fe.h`, AS10x command protocol helpers, and low-level `as102_priv_ops_t` methods. The module is registered via `module_usb_driver(as102_usb_driver)`, with the actual USB driver object defined in `as102_usb_drv.c`.

## Risks and test signals
Critical risks are stream reference-count balance, interruptible mutex failures returning partial setup, firmware upload failures being tolerated for later upload, and PID filter add/delete correctness when hardware filtering is enabled. Test signals include successful adapter/frontend registration, feed start producing TS packets, feed stop dropping streaming to zero, tuning/status/stat queries returning plausible values, and no lock inversion between `sem` and `bus_adap.lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_drv.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_drv.h

## Purpose
Defines the shared AS102 driver state, public registration functions, constants, and cross-file declarations used by the DVB glue and USB transport.

## Important APIs, types, and functions
`struct as10x_bus_adapter_t` contains the USB device, bus mutex, command token storage, transaction id `cmd_xid`, command/response pointers, and `as102_priv_ops_t` method table. `struct as102_dev_t` contains board name, bus adapter, kref, eLNA config, DVB adapter/frontend/demux/dmxdev, a timer handle, synchronization semaphore, DMA stream storage, stream count, and up to `MAX_STREAM_URB` URBs. It declares `as102_dvb_register()` and `as102_dvb_unregister()`.

## Control flow and state
This header structures the persistent device lifetime. The USB probe allocates `as102_dev_t`, initializes the bus adapter token pointers, USB device pointer, kref, and stream buffers. The DVB layer mutates `streaming` and DVB objects. The bus command lock serializes firmware and control traffic through the shared command/response buffers.

## Dependencies and integration points
Includes USB, DVB demux/frontend/dmxdev, `as10x_handle.h`, `as10x_cmd.h`, and `as102_usb_drv.h`. Exports `as102_usb_driver` for the module entry in `as102_drv.c` and `elna_enable` for frontend/stream control behavior.

## Risks and test signals
The shared command/rsp buffers make locking mandatory; any new caller must hold `bus_adap.lock`. Lifetime depends on kref and USB disconnect ordering. Test signals include no use-after-free under open file descriptors, correct URB array bounds using `MAX_STREAM_URB`, and clean unregister after active streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_fw.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_fw.c

## Purpose
Loads AS102 firmware from Intel HEX files and uploads it to the device over the low-level firmware packet operation.

## Important APIs, types, and functions
Firmware filenames are split by single-tuner versus dual-tuner mode: `as102_data1_st.hex`, `as102_data2_st.hex`, `as102_data1_dt.hex`, and `as102_data2_dt.hex`. `atohx()` converts two ASCII hex digits. `parse_hex_line()` extracts line length, address bytes, record type, and data/address-extension bytes. `as102_firmware_upload()` iterates over firmware lines, builds `struct as10x_fw_pkt_t`, sends data records with request `0x0001`, and sends EOF request `0x0003`. `as102_fw_upload()` requests part 1, uploads it, waits 100 ms, then requests and uploads part 2.

## Control flow and state
The upload path is synchronous and temporary: firmware files are requested through the firmware loader, parsed linearly, and each data packet is sent through `bus_adap->ops->upload_fw_pkt()`. Dual-tuner mode chooses the alternate firmware pair. No persistent kernel state is stored beyond firmware side effects on the device.

## Dependencies and integration points
Depends on Linux firmware loader, AS102 driver state, firmware packet structures from `as102_fw.h`, and USB implementation of `upload_fw_pkt` in `as102_usb_drv.c` using endpoint 1 bulk OUT.

## Risks and test signals
Risks include weak HEX validation, no checksum verification, assumptions about newline-terminated records, and packet size/address-extension parsing. Upload failure in registration is tolerated by `try_then_request_module`, so test both available and missing firmware paths. Test signals are part1/part2 success logs, no leak of requested firmware on errors, correct dual-tuner filename selection, and device responding to later AS10x commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_fw.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_fw.h

## Purpose
Declares AS102 firmware packet layout and firmware upload entry point.

## Important APIs, types, and functions
`MAX_FW_PKT_SIZE` is 64 bytes. `struct as10x_raw_fw_pkt` contains a four-byte address and data bytes sized to fit a 64-byte packet minus request/length overhead. `struct as10x_fw_pkt_t` overlays two request bytes or length bytes before the raw firmware payload. `as102_fw_upload()` is exported for kernel callers. `dual_tuner` is declared for firmware selection.

## Control flow and state
This header has no executable flow, but its packed layout defines the wire protocol used by `as102_fw.c` and `as102_usb_drv.c`. The `__packed` annotations are part of the ABI to the device firmware loader.

## Dependencies and integration points
Consumes `struct as10x_bus_adapter_t` from the driver and is included by firmware and USB files. It integrates with firmware upload by giving the USB endpoint code a byte-accurate packet structure.

## Risks and test signals
Risks are structure-size drift and alignment changes if fields are edited. Test signals are `sizeof(struct as10x_fw_pkt_t)` remaining compatible with 64-byte packets, successful upload of both firmware stages, and no short bulk writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_usb_drv.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_usb_drv.c

## Purpose
Implements USB probing, disconnect, character-device registration, command transport, firmware packet transfer, and DVB transport-stream URB streaming for AS102 devices.

## Important APIs, types, and functions
`as102_usb_id_table` maps vendor/product IDs to device names and eLNA configs. `as102_usb_driver` is the USB driver exported to `as102_drv.c`. `as102_usb_xfer_cmd()` sends and receives vendor control messages `0xf1`/`0xf2` using `cmd_xid`. `as102_send_ep1()` uploads firmware packets over bulk endpoint 1. `as102_read_ep2()` reads endpoint 2 synchronously. `as102_alloc_usb_stream_buffer()` allocates one coherent buffer spanning `MAX_STREAM_URB * AS102_USB_BUF_SIZE` and assigns slices to URBs. `as102_urb_stream_irq()` feeds received bytes to `dvb_dmx_swfilter()` and resubmits while `streaming` is nonzero. Probe allocates `as102_dev_t`, registers `/dev/aton2-*`, allocates stream buffers, and calls `as102_dvb_register()`.

## Control flow and state
USB probe establishes device identity, bus ops, command token pointers, kref, and USB ref. DVB feed start later submits all stream URBs; each URB completion pushes TS bytes to demux and self-resubmits. Disconnect unregisters DVB, frees stream buffers, deregisters the USB class device, clears interface data, and drops the kref.

## Dependencies and integration points
Integrates with Linux USB core, DVB demux, firmware upload, and AS102 private operations. Also exposes a simple character device open/release path that pins `as102_dev_t` via kref.

## Risks and test signals
Risks include short USB transfers returning `-1` instead of a standard errno, resubmission depending on the shared `streaming` counter, coherent buffer pointer arithmetic on `void *`, and disconnect while character device references remain. Test signals include device-node creation, successful firmware upload over EP1, command request/response over control endpoint, sustained endpoint 2 streaming, and clean disconnect during active feeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_usb_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_usb_drv.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_usb_drv.h

## Purpose
Defines AS102 USB command constants, supported USB device IDs/names, and the USB token command container.

## Important APIs, types, and functions
Vendor control requests are `AS102_USB_DEVICE_TX_CTRL_CMD` (`0xf1`) and `AS102_USB_DEVICE_RX_CTRL_CMD` (`0xf2`). The header names supported products: Abilis reference design, PCTV picoStick 74e, Elgato EyeTV DTT Deluxe, nBox DVB-T Dongle, and Sky Italia Digital Key, with their VID/PID constants. `struct as10x_usb_token_cmd_t` stores one AS10x command and one AS10x response. `as102_urb_stream_irq()` is declared for URB completion.

## Control flow and state
No executable flow exists. Constants here drive USB matching and request dispatch in `as102_usb_drv.c`, and the token type supplies persistent command/rsp storage inside `struct as10x_bus_adapter_t`.

## Dependencies and integration points
Includes `as10x_cmd_t` through use in the token struct. Integrated by `as102_drv.h` and USB transport code.

## Risks and test signals
Risks are incorrect VID/PID constants or mismatch between ID table, device-name array, and eLNA config arrays. Test signals are all supported devices binding to the expected product name and the command buffers remaining large enough for all AS10x command unions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_usb_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd.c

## Purpose
Implements the core AS10x control protocol commands used for power, tuning, status, TPS, demod statistics, impulse response, command header construction, and common response parsing.

## Important APIs, types, and functions
Exports `as10x_cmd_turn_on()`, `as10x_cmd_turn_off()`, `as10x_cmd_set_tune()`, `as10x_cmd_get_tune_status()`, `as10x_cmd_get_tps()`, `as10x_cmd_get_demod_stats()`, `as10x_cmd_get_impulse_resp()`, `as10x_cmd_build()`, and `as10x_rsp_parse()`. Each command uses `adap->cmd` and `adap->rsp`, increments `cmd_xid`, writes a procedure id from `enum control_proc`, calls `adap->ops->xfer_cmd()`, then validates the expected response id.

## Control flow and state
The file is command-marshalling glue. Callers are expected to serialize access with `bus_adap.lock`; the functions mutate the shared command/response buffers and transaction id. Getter commands copy little-endian response fields into host-endian status/stat structures.

## Dependencies and integration points
Used by AS102 frontend operations in `as102_drv.c` and stream/config command files. Depends on the transport callback provided by USB and on packed protocol structures from `as10x_cmd.h` and `as102_fe_types.h`.

## Risks and test signals
Risks include endian mistakes, wrong union member use, unchecked absence of `xfer_cmd` leaving generic `AS10X_CMD_ERROR`, and response parser returning only a generic `-1`. A notable review signal is `as10x_cmd_get_tps()` writing `pcmd->body.get_tune_status.req.proc_id` instead of the `get_tps` union member; layout likely masks this but it is brittle. Test signals are successful tune/status/stat reads across real hardware, transaction id monotonicity, and no concurrent command corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd.h

## Purpose
Defines the AS10x firmware control protocol ABI: procedure IDs, command header, packed request/response unions, command aggregate, and function prototypes.

## Important APIs, types, and functions
`enum control_proc` maps each command to request and response procedure IDs. `struct as10x_cmd_header_t` contains request id, service program id, version, and data length. Packed unions describe turn on/off, tune, tune status, TPS, PID filter, stream start/stop, demod stats, impulse response, firmware context, register access, config mode changes, memory dump, log dump, and raw data. `struct as10x_cmd_t` combines the header and all possible bodies. Prototypes cover core, stream, and context commands.

## Control flow and state
This header has no runtime flow but defines the memory layout that every command function writes into shared bus token storage. `HEADER_SIZE` drives USB transfer lengths in the command files.

## Dependencies and integration points
Includes `as102_fe_types.h` for tune/status/stat/register data structures. Integrated by AS102 driver, USB token storage, command implementations, and frontend glue.

## Risks and test signals
Because these structs are packed wire ABI, field ordering, type widths, and endian annotations are high-risk. Generic parser expectations also depend on response unions sharing `proc_id` and `error` at the same offsets. Test signals are compile-time packed sizes, command success on hardware, and sparse/endian warnings staying clean when protocol fields are touched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd_cfg.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd_cfg.c

## Purpose
Implements AS10x firmware context and eLNA configuration commands.

## Important APIs, types, and functions
`as10x_cmd_get_context()` sends `CONTROL_PROC_CONTEXT` with `GET_CONTEXT_DATA` and returns a 32-bit value. `as10x_cmd_set_context()` sends `SET_CONTEXT_DATA` and a 32-bit context value. `as10x_cmd_eLNA_change_mode()` sends `CONTROL_PROC_ELNA_CHANGE_MODE`. `as10x_context_rsp_parse()` handles the context-specific response layout, which differs from the common response union.

## Control flow and state
Each function builds the command header with a new `cmd_xid`, writes the specific request body, transfers through `ops->xfer_cmd`, and validates the response. Callers such as `as102_stream_ctrl()` use set-context to program `CONTEXT_LNA` before turning the receiver on.

## Dependencies and integration points
Depends on shared `as10x_cmd_t` buffers in the bus adapter and USB command transport. Integrated with frontend/stream control paths that configure eLNA behavior.

## Risks and test signals
Risks include using the common response parser for context commands, missing locks around shared buffers, and unvalidated context tags. Test signals include successful eLNA context programming, get-context round trips returning expected values, and no command failures when `elna_enable` is toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd_cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd_stream.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd_stream.c

## Purpose
Implements AS10x transport-stream control commands for PID filtering and firmware streaming start/stop.

## Important APIs, types, and functions
`as10x_cmd_add_PID_filter()` sends `CONTROL_PROC_SETFILTER`, writes PID, stream type, and optional filter index, then returns the firmware-assigned index. `as10x_cmd_del_PID_filter()` sends `CONTROL_PROC_REMOVEFILTER`. `as10x_cmd_start_streaming()` and `as10x_cmd_stop_streaming()` send the firmware stream enable/disable procedure IDs.

## Control flow and state
The DVB feed callbacks call add/delete PID filter when `pid_filtering` is enabled and call start/stop streaming when `ts_auto_disable` requests firmware stream control. The command functions themselves only mutate the shared bus command token and rely on the caller-held bus mutex.

## Dependencies and integration points
Integrates with `as102_drv.c` feed management, DVB demux PID filters, and USB `xfer_cmd`. Uses `struct as10x_ts_filter` from frontend type definitions.

## Risks and test signals
Risks include firmware filter capacity mismatch, index handling when caller supplies `idx >= 16`, and `as10x_cmd_stop_streaming()` storing error in `int8_t`, which can truncate transport errors. Test signals are correct demux output with hardware filtering on/off, no stale PID filters after stop, and firmware stream control working when `ts_auto_disable=1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd_stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_handle.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_handle.h

## Purpose
Declares the private bus-operation abstraction used by AS10x command and streaming code to stay independent of the concrete transport.

## Important APIs, types, and functions
`struct as102_priv_ops_t` contains callbacks for firmware packet upload, command send, command transfer, stream start/stop, target reset, register read/write, and endpoint 2 reads. It also defines register mode constants `REGMODE8`, `REGMODE16`, and `REGMODE32`.

## Control flow and state
No code runs here. At USB probe, `as102_dev_t.bus_adap.ops` is assigned to the USB implementation table. Higher-level AS102 code calls methods through this table for firmware, command, and stream operations.

## Dependencies and integration points
Forward-declares the bus adapter and device state, includes the command header, and is included by `as102_drv.h`. This is the integration boundary between AS10x protocol code and USB transport code.

## Risks and test signals
Risks are null optional callbacks and divergent semantics across possible transports. In this tree, USB supplies `upload_fw_pkt`, `xfer_cmd`, `as102_read_ep2`, `start_stream`, and `stop_stream`, while some callbacks remain unused. Test signals are all higher-level callers checking optional operations before use or being restricted to transports that supply them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/Kconfig

## Purpose
Defines build-time configuration for the Auvitek AU0828 hybrid analog/digital USB capture driver and its optional analog V4L2 and remote-control support.

## Important APIs, types, and functions
`VIDEO_AU0828` is the main tristate and depends on I2C, INPUT, DVB_CORE, USB, and VIDEO_DEV. It selects media controller support, DVB media-controller glue, bit-banged I2C, TV EEPROM, vb2-vmalloc when video is enabled, and common demod/tuner dependencies when auto-select is enabled. `VIDEO_AU0828_V4L2` gates analog video/VBI support. `VIDEO_AU0828_RC` gates remote-controller support and depends on RC core compatibility.

## Control flow and state
No runtime flow exists. Build-time symbols decide whether `au0828-video.o`, `au0828-vbi.o`, and `au0828-input.o` are linked and whether inline stubs in `au0828.h` are used.

## Dependencies and integration points
Integrates with media Kconfig, media-controller graph support, DVB frontend/tuner auto-selection, V4L2, RC, and I2C infrastructure.

## Risks and test signals
Risks include invalid built-in/module dependency combinations for V4L2 or RC and missing tuner/demod auto-select entries for supported boards. Test signals are successful builds for core-only, V4L2-enabled, RC-enabled, and module combinations, plus correct menu visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/Makefile

## Purpose
Composes the AU0828 module from core, I2C, card, DVB, optional analog, optional VBI, and optional RC objects.

## Important APIs, types, and functions
Always links `au0828-core.o`, `au0828-i2c.o`, `au0828-cards.o`, and `au0828-dvb.o`. Adds `au0828-video.o` and `au0828-vbi.o` when `CONFIG_VIDEO_AU0828_V4L2=y`; adds `au0828-input.o` when `CONFIG_VIDEO_AU0828_RC=y`. Emits `au0828.o` for `CONFIG_VIDEO_AU0828`.

## Control flow and state
No runtime flow exists. Object inclusion controls which external functions in `au0828.h` are real versus inline stubs.

## Dependencies and integration points
Adds include paths for media tuners and DVB frontends, required by card setup and DVB attach logic. Integrates with kbuild and optional `extra-cflags-y/m`.

## Risks and test signals
Risks are unresolved symbols if config guards and object inclusion diverge. Test signals are clean builds with analog/RC enabled and disabled, and no missing include errors for tuner/frontend headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-cards.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-cards.c

## Purpose
Defines AU0828 board profiles, USB IDs, GPIO bring-up, EEPROM handling, tuner reset callbacks, and analog frontend/tuner subdevice setup.

## Important APIs, types, and functions
`au0828_boards[]` maps board numbers to names, tuner types/addresses, I2C speed, IR/analog flags, and input routing. `hvr950q_cs5340_audio()` controls a shared I2S audio reset GPIO. `au0828_tuner_callback()` resets tuners for supported boards. `hauppauge_eeprom()` parses Hauppauge EEPROM and updates tuner type. `au0828_card_setup()` reads EEPROM and calls `au0828_card_analog_fe_setup()`. `au0828_card_analog_fe_setup()` creates `au8522` analog decoder and tuner subdevices when V4L2 analog is enabled. `au0828_gpio_setup()` powers/reset devices per board. `au0828_usb_id_table[]` binds many Hauppauge/DViCO/Elgato IDs to board profiles.

## Control flow and state
Core probe copies a board profile from `au0828_boards`, powers the bridge, calls GPIO setup, registers I2C, and invokes card setup. Card setup may overwrite tuner type from EEPROM, then attaches analog subdevices. GPIO setup writes bridge registers and sleeps to satisfy reset/power timing.

## Dependencies and integration points
Depends on AU0828 register access, AU8522 demod/decoder, tuner framework, TV EEPROM, and V4L2 subdevice registration. The USB ID table is consumed by `au0828-core.c` probe.

## Risks and test signals
Risks are board-profile mistakes, GPIO timing regressions, mismatch with ALSA USB quirks for V4L2 boards, and EEPROM model drift. Test signals include correct board name on probe, expected tuner type after EEPROM parse, successful analog subdevice creation, tuner reset callback behavior, and working inputs for TV/composite/S-video.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-cards.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-cards.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-cards.h

## Purpose
Assigns numeric board IDs for AU0828-supported devices.

## Important APIs, types, and functions
Defines IDs for unknown board, Hauppauge HVR950Q, HVR850, DViCO FusionHDTV7, HVR950Q MXL, Woodbury, Impact VCB-e, and HVR1265.

## Control flow and state
No executable flow. These constants index `au0828_boards[]` and populate `driver_info` in the USB ID table. The selected ID controls board state copied into `struct au0828_dev` at probe.

## Dependencies and integration points
Included by `au0828.h`, `au0828-cards.c`, and core code. Integrates USB device matching, card profiles, DVB frontend attachment, GPIO setup, and RC support decisions.

## Risks and test signals
Risks are index reorder without matching board array and USB ID table updates. Test signals are each USB ID resolving to the intended board profile and no out-of-bounds board access in probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-cards.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-core.c

## Purpose
Provides AU0828 USB driver registration, register read/write helpers, media-controller source arbitration, probe/disconnect, suspend/resume, and module init/exit.

## Important APIs, types, and functions
`au0828_readreg()` and `au0828_writereg()` wrap vendor control messages. `send_control_msg()` and `recv_control_msg()` perform USB control transfers, with reads serialized by `dev->mutex` and a heap control buffer. `au0828_usb_probe()` validates interface 0 and high-speed USB, allocates state, initializes media/V4L2/I2C/card/DVB/RC layers, and registers media graph support. `au0828_usb_disconnect()` marks `DEV_DISCONNECTED`, unregisters RC/DVB/analog, clears `usbdev`, and releases state. Media-controller helpers register devices, create audio links, enable/disable source links, and handle sharing between analog video/VBI/audio versus DVB.

## Control flow and state
Module init registers the USB driver. Probe creates `struct au0828_dev`, copies board data from `driver_info`, powers up the bridge, configures GPIOs, I2C, card, analog, DVB, and RC. If media controller is enabled, source ownership is tracked with `active_link`, owner/user entities, and pipeline pointers to prevent conflicting tuner use. Suspend/resume calls RC, V4L2, and DVB suspend/resume hooks and re-powers/configures GPIOs.

## Dependencies and integration points
Depends on USB core, V4L2, media controller, DVB, I2C, RC, tuner media entities, and board tables. Exposes `au0828_read()`/`au0828_write()` API used by all AU0828 submodules.

## Risks and test signals
Risks include disconnect races, media graph source ownership bugs, high-speed check override misuse, and asymmetric control-message locking between reads and writes. Test signals include successful probe/unwind on each failure path, correct media graph links, source arbitration returning `-EBUSY` for tuner conflicts, suspend/resume with active streams, and clean disconnect while analog/DVB/RC are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-dvb.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-dvb.c

## Purpose
Implements AU0828 digital TV support: frontend/tuner attachment, DVB adapter/demux/net registration, bulk URB transport, stream restart workaround, and DVB suspend/resume.

## Important APIs, types, and functions
Board-specific configs cover AU8522 demod, LED thresholds, XC5000, MXL5007T, and TDA18271 tuners. `urb_completion()` validates bulk packets, checks TS sync byte `0x47`, feeds packets via `dvb_dmx_swfilter_packets()`, and resubmits. `start_urb_transfer()` and `stop_urb_transfer()` allocate/submit or kill/free `URB_COUNT` bulk URBs. `au0828_dvb_start_feed()` and `au0828_dvb_stop_feed()` reference-count demux feeding and start/stop bridge transport registers. `au0828_restart_dvb_streaming()` handles timeout/misalignment restart. `au0828_set_frontend()` wraps frontend tuning so streaming stops before tuning and restarts after. `dvb_register()` registers adapter, frontend, demux frontends, dmxdev, net, and media graph. `au0828_dvb_register()` attaches board-specific frontend/tuner.

## Control flow and state
DVB registration attaches hardware based on `boardnr`, then registers DVB core objects. First active feed starts transport and URBs; last feed cancels restart work, stops URBs, and stops transport. Timeout or bad TS alignment schedules restart work. Suspend stops active streams and remembers `need_urb_start`; resume resumes frontend and restarts transport if needed.

## Dependencies and integration points
Depends on DVB core, AU8522, XC5000, MXL5007T, TDA18271, media-controller DVB graph support, and AU0828 bridge register writes.

## Risks and test signals
Risks include URB allocation unwind leaks, bad sync-byte false positives on short/corrupt data, restart work racing with stop/tune, and preallocated buffer lifetime. Test signals include DVB scan/lock, packet counters, restart on induced misalignment, feed reference-count balance, suspend/resume with active feed, and clean unregister freeing all DVB objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-dvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-i2c.c

## Purpose
Implements the AU0828 bridge-backed I2C adapter used to access EEPROM, demodulators, tuners, and optional IR hardware.

## Important APIs, types, and functions
Polling helpers read `AU0828_I2C_STATUS_201` to wait for read ack, read done, write done, and idle. `i2c_sendbytes()` writes up to four FIFO bytes per strobe, handles SMBus quick/zero-length writes, sets destination address, and adjusts clock speed for XC5000 tuner quirks. `i2c_readbytes()` performs reads with hold behavior for multi-byte transfers and slow clock for XC5000 reads. `i2c_xfer()` implements master transfers including write-then-read same-address sequences. `au0828_i2c_register()` registers the adapter and optional bus scan; `au0828_i2c_unregister()` removes it.

## Control flow and state
Core probe initializes `dev->i2c_adap`, `i2c_algo`, and `i2c_client`; then card setup and subdevice creation use the adapter. Each transfer programs bridge registers and polls for completion. `dev->i2c_rc` stores registration result, but the code does not assign the return from `i2c_add_adapter()` into it in this version, making success reporting suspect.

## Dependencies and integration points
Depends on AU0828 register access, Linux I2C core, tuner address/type data from board profiles, V4L2 adapter data when analog is enabled, and TV EEPROM/tuner/demod users.

## Risks and test signals
Risks are polling timeout tuning, incomplete repeated-start/join handling, fragile zero-length scan semantics, and the apparent `i2c_rc` registration result bug. Test signals include EEPROM read success, tuner firmware load at adjusted clock speed, demod attach over I2C, optional `i2c_scan` output, and no `-EIO` under normal tuner operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-input.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-input.c

## Purpose
Adds remote-control support for AU0828 boards with an AU8522-based I2C IR receiver, exposing raw IR events through rc-core.

## Important APIs, types, and functions
`struct au0828_rc` stores device, `rc_dev`, names, polling work, I2C address, and key-read callback. `au8522_rc_read()`, `au8522_rc_write()`, and `au8522_rc_andor()` access AU8522 IR registers over I2C. `au0828_get_key_au8522()` polls interrupt status, reads 40 bytes of encoded pulse/space data, fakes the missing first pulse for NEC/RC5, and stores raw events. `au0828_rc_start()` enables IR and starts delayed work; `au0828_rc_stop()` cancels work and disables IR. `au0828_rc_register()` probes address `0x47`, allocates/registers `rc_dev`, and selects Hauppauge map for supported boards.

## Control flow and state
Core probe calls RC register after DVB/analog setup. rc-core open starts polling every 100 ms. Each work item reads a key and reschedules itself. Disconnect unregisters RC before clearing `usbdev`; key reads check `DEV_DISCONNECTED`. Suspend cancels work and disables IR; resume reenables and restarts polling.

## Dependencies and integration points
Depends on I2C adapter from `au0828-i2c.c`, rc-core raw event decoders, board flags from `au0828-cards.c`, and AU8522 register behavior.

## Risks and test signals
Risks include polling after disconnect, protocol-specific first-pulse reconstruction, double-free concerns if `rc_unregister_device()` and `rc_free_device()` semantics change, and unsupported boards with `has_ir_i2c`. Test signals are rc device registration, raw NEC/RC5 key events with Hauppauge map, clean suspend/resume, and no I2C errors after unplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-reg.h

## Purpose
Defines AU0828 bridge register addresses and bit constants used by core, I2C, audio, and analog streaming code.

## Important APIs, types, and functions
Key definitions include GPIO-like registers `REG_000` through `REG_003`, analog sensor control registers `AU0828_SENSORCTRL_100` and `AU0828_SENSORCTRL_VBI_103`, I2C registers from trigger/status/clock/destination/FIFOs/multibyte mode, audio control `AU0828_AUDIOCTRL_50C`, and `REG_600` for bridge power. Bit constants define I2C trigger write/read/hold, status read/write done, no-ack, and busy bits, plus clock divider presets.

## Control flow and state
No executable flow. These constants are used to program persistent hardware state in register writes. Mislabelled or changed values affect GPIO reset, I2C transport, stream setup, and audio mode.

## Dependencies and integration points
Included by `au0828.h` and analog video code. Integrated across `au0828-core.c`, `au0828-cards.c`, `au0828-i2c.c`, and `au0828-video.c`.

## Risks and test signals
Risks are incorrect register addresses, unclear names for still-reverse-engineered registers, and clock-divider values that break tuner/demod communication. Test signals are I2C register polling behavior, successful GPIO reset sequencing, analog stream enable, and I2S audio init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-vbi.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-vbi.c

## Purpose
Provides the videobuf2 queue operations for AU0828 raw VBI capture.

## Important APIs, types, and functions
`vbi_queue_setup()` sizes one plane as `vbi_width * vbi_height * 2`. `vbi_buffer_prepare()` validates plane capacity and sets payload. `vbi_buffer_queue()` stores the plane address/length in `struct au0828_buffer` and appends it to `dev->vbiq.active` under `dev->slock`. `au0828_vbi_qops` wires these callbacks to media-source enabling, shared analog stream start, and VBI-specific stop.

## Control flow and state
VBI buffers are queued independently from video buffers but share the analog ISO stream. `au0828-video.c` packet parsing fills `dev->isoc_ctl.vbi_buf` from the active queue and completes it on field boundaries or timeout.

## Dependencies and integration points
Depends on vb2-vmalloc, V4L2 media controller source enabling, `au0828_start_analog_streaming()`, and `au0828_stop_vbi_streaming()`.

## Risks and test signals
Risks are mismatched VBI size assumptions with `au0828-video.c`, shared stream user reference count imbalance between video and VBI queues, and queue operations after disconnect. Test signals include successful VBI `REQBUFS/QBUF/STREAMON`, periodic VBI buffers even on timeout, correct GREY VBI format reporting, and clean stop returning queued buffers with error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-vbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-video.c

## Purpose
Implements AU0828 analog V4L2 video and VBI capture, including ISO URB management, packet parsing, buffer completion, video/VBI ioctls, tuner/input routing, media entities, suspend/resume, and video-device registration.

## Important APIs, types, and functions
ISO setup is handled by `au0828_init_isoc()` and `au0828_uninit_isoc()`, with `au0828_irq_callback()` resubmitting URBs. `au0828_isoc_copy()` parses AU0828 packet headers, separates VBI and video payload, handles field transitions, and fills active buffers via `au0828_copy_vbi()` and `au0828_copy_video()`. vb2 callbacks manage video buffers; VBI qops live in `au0828-vbi.c`. Stream control uses `au0828_start_analog_streaming()`, `au0828_stop_streaming()`, and `au0828_stop_vbi_streaming()`. V4L2 operations cover format, standard, input, audio, tuner, frequency, VBI format, selection, debug registers, status, and `DQBUF` green-screen recovery. Registration happens in `au0828_analog_register()`.

## Control flow and state
Open enables analog bridge streaming and resets hardware for the first user. `STREAMON` starts shared ISO URBs only for the first video/VBI streaming user, enables subdevice stream, and arms timeouts. URB completion parses packets under `slock`; new-field headers complete current buffers and fetch next queued buffers. Timeout handlers synthesize blank buffers so applications do not hang. Close may put tuner standby and set USB altsetting 0 when the last user exits. Format/standard/frequency changes initialize tuner through gated I2C and may interrupt active stream state.

## Dependencies and integration points
Depends on V4L2, vb2-vmalloc, V4L2 subdevices, media-controller source helpers, AU8522 analog ops, tuner ops, USB isochronous API, and AU0828 bridge registers.

## Risks and test signals
High-risk areas are packet parsing bounds, shared `streaming_users` across video/VBI, timeout buffer completion, suspend/resume URB state, green-screen reset heuristic, and media-source switching after input changes. Test signals include analog capture at UYVY 720x480, VBI capture, concurrent video+VBI, unplug during stream, input/frequency/standard ioctls, media graph source arbitration, blank-buffer timeout behavior, and no buffer overflows logged by copy helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828.h

## Purpose
Central AU0828 internal header defining device state, board/input models, streaming structures, resource constants, register helpers, and cross-module prototypes.

## Important APIs, types, and functions
Defines USB and analog constants, input types, `struct au0828_input`, `struct au0828_board`, `struct au0828_dvb`, stream/device-state enums, `struct au0828_usb_isoc_ctl`, `struct au0828_buffer`, `struct au0828_dmaqueue`, and the large `struct au0828_dev`. `struct au0828_dev` stores USB, board, control buffer, I2C, DVB, V4L2/RC optional state, vb2 queues, timers, dimensions, input/frequency/std state, stream state, ISO and bulk URB arrays, and media-controller graph ownership fields. Macros wrap register read/write/and/or/set/clear. Prototypes connect core, cards, I2C, video, DVB, VBI, and RC modules with config-dependent stubs.

## Control flow and state
The header encodes nearly all persistent AU0828 state. Probe initializes pieces across modules; stream callbacks mutate queue/timer/URB fields; disconnect and suspend/resume test `dev_state` bits and clear transport pointers. Optional feature stubs let the core call analog/RC hooks regardless of configuration.

## Dependencies and integration points
Includes USB, I2C, V4L2, vb2, media-controller, DVB, TV EEPROM, register, and card headers. It is the integration contract for every AU0828 source file in this group.

## Risks and test signals
Risks include broad shared mutable state, conditional compilation mismatches, lock-use ambiguity among `mutex`, `lock`, `slock`, queue locks, and DVB lock, plus media graph pointer lifetime. Test signals are all config combinations compiling, lockdep-clean streaming/open/close/disconnect, and correct initialization of every field consumed by callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/Kconfig

## Purpose
Defines configuration for Technisat/B2C2 FlexCop USB DVB/ATSC devices and optional debug support.

## Important APIs, types, and functions
`DVB_B2C2_FLEXCOP_USB` is a tristate depending on `DVB_CORE` and `I2C`. `DVB_B2C2_FLEXCOP_USB_DEBUG` is a bool depending on the USB driver and selecting shared `DVB_B2C2_FLEXCOP_DEBUG`.

## Control flow and state
No runtime flow. The main symbol builds the USB bus glue module, while the debug symbol enables runtime debug module parameter support compiled into the FlexCop USB source.

## Dependencies and integration points
Integrates with the common B2C2 FlexCop media code via the Makefile include path and common debug option.

## Risks and test signals
Risks are missing dependencies on shared FlexCop common code or overexposed debug options. Test signals are successful module builds with debug on/off and visibility under DVB USB devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/Makefile

## Purpose
Builds the B2C2 FlexCop USB module from its USB transport source.

## Important APIs, types, and functions
Defines `b2c2-flexcop-usb-objs := flexcop-usb.o` and adds `b2c2-flexcop-usb.o` when `CONFIG_DVB_B2C2_FLEXCOP_USB` is enabled.

## Control flow and state
No runtime flow. The object composition links only the USB glue file, relying on external/common FlexCop objects through kernel media build dependencies.

## Dependencies and integration points
Adds include path to `drivers/media/common/b2c2/`, which supplies `flexcop-common.h` and shared FlexCop APIs called by `flexcop-usb.c`.

## Risks and test signals
Risks are include path drift and unresolved common FlexCop symbols. Test signals are clean module link and successful inclusion of shared common headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/flexcop-usb.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/flexcop-usb.c

## Purpose
Implements the USB bus layer for B2C2 FlexCop II/IIb/III digital TV devices, connecting common FlexCop DVB logic to USB control transfers, I2C requests, V8 memory access, MAC address readout, and isochronous TS reception.

## Important APIs, types, and functions
`flexcop_usb_readwrite_dw()` reads/writes FlexCop IBI registers via vendor control transfers and PCI/internal address conversion macros. `flexcop_usb_v8_memory_req()` and `flexcop_usb_memory_req()` access V8 memory/flash in page-limited chunks. `flexcop_usb_get_mac_addr()` reads six bytes from flash. `flexcop_usb_i2c_req()` implements firmware-mediated I2C operations. `flexcop_usb_process_frame()` parses 190-byte USB media frames with `0xff` header and embedded TS sync `0x47`, passing packets to `flexcop_pass_dmx_packets()`. `flexcop_usb_transfer_init()` allocates coherent ISO buffers, builds four URBs with four ISO frames each, submits them, then configures SRAM/WAN routing. Probe allocates a `flexcop_device`, installs USB callbacks, initializes common FlexCop, and starts transfer.

## Control flow and state
USB probe sets alternate interface 1, validates endpoint and speed, stores interface data, initializes common FlexCop, and starts continuous ISO URBs. URB completion iterates ISO frames, processes complete payloads, stores trailing partial data in `tmp_buffer`, clears frame statuses, and resubmits. Disconnect kills URBs, frees buffers, exits common FlexCop, clears interface data, and frees state.

## Dependencies and integration points
Depends on USB core, common B2C2 FlexCop APIs, FlexCop I2C adapter abstraction, DVB demux pass-through, SRAM/WAN setup helpers, and module debug configuration.

## Risks and test signals
Risks include continuous URBs with no stream-control gating, partial-frame buffer overflow if unexpected frame sizes exceed `tmp_buffer`, error handling in URB resubmit, and USB endpoint assumptions after altsetting. Test signals include successful register access, I2C tuner/demod communication, MAC address read, demux packets with TS sync, clean disconnect, and no ISO descriptor errors under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/flexcop-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/flexcop-usb.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/flexcop-usb.h

## Purpose
Defines the B2C2 FlexCop USB private state, USB pipe macros, vendor request IDs, I2C utility function IDs, V8 memory constants, and transfer sizing.

## Important APIs, types, and functions
Transfer constants are four ISO frames per URB and four ISO URBs. `struct flexcop_usb` stores USB device/interface, coherent ISO buffer/DMA address, ISO URBs, owning `flexcop_device`, partial TS frame buffer, control-transfer scratch data, and a mutex protecting that data. Request enums cover register, V8 memory, flash, I2C, and utility operations. Utility enums cover data/filter/buffer/SRAM operations. V8 memory constants define pages, extended bit, max read/write/flash chunk sizes, and 32 KiB page mask.

## Control flow and state
No executable flow. The struct describes persistent USB transport state allocated as the bus-specific portion of `struct flexcop_device`. Pipe macros depend on a local `fc_usb` variable and are used in control and ISO setup code.

## Dependencies and integration points
Includes USB core and forward-integrates with common FlexCop code through the `fc_dev` pointer. Request constants are the ABI used by firmware in `flexcop-usb.c`.

## Risks and test signals
Risks include macro dependence on variable names, scratch buffer size limits for control transfers, partial-frame buffer sizing, and request enum drift from firmware. Test signals are no oversized control requests, successful V8 flash/MAC reads, and stable ISO transfer setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/flexcop-usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/Kconfig

## Purpose
Defines configuration symbols for Conexant cx231xx USB video capture, optional remote-controller support, optional ALSA audio, and optional DVB/ATSC support.

## Important APIs, types, and functions
`VIDEO_CX231XX` is the main tristate depending on VIDEO_DEV, I2C, and I2C_MUX, and selecting tuner, TV EEPROM, vb2-vmalloc, cx25840, and cx2341x support. `VIDEO_CX231XX_RC` gates extra RC hardware support, depends on compatible RC core configuration, selects `BITREVERSE`, and defaults to enabled. `VIDEO_CX231XX_ALSA` builds the ALSA PCM audio module. `VIDEO_CX231XX_DVB` builds DVB support and auto-selects a range of tuners/demods when `MEDIA_SUBDRV_AUTOSELECT` is enabled.

## Control flow and state
No runtime flow. These symbols decide which cx231xx objects/modules are built and which media subdrivers are pulled into configurations automatically.

## Dependencies and integration points
Integrates cx231xx with V4L2, I2C muxing, tuner/demod subdrivers, ALSA PCM, RC core, and DVB core.

## Risks and test signals
Risks include invalid built-in/module dependency combinations, missing new board demod/tuner auto-selects, and optional RC defaults enabling unsupported hardware paths. Test signals are clean builds for base, RC, ALSA, and DVB modules; menuconfig visibility; and no unresolved symbols when options are mixed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/Makefile

## Purpose
Builds the Conexant cx231xx media driver modules and optional RC, ALSA, and DVB pieces.

## Important APIs, types, and functions
The core `cx231xx` module includes video, I2C, cards, core, AV core, MPEG encoder support, PCB config, and VBI objects. `cx231xx-input.o` is added when RC support is enabled. `cx231xx-alsa-objs` maps to `cx231xx-audio.o`. Object targets add `cx231xx.o`, `cx231xx-alsa.o`, and `cx231xx-dvb.o` under their respective config symbols.

## Control flow and state
No runtime flow. Object selection controls which modules are emitted and whether input support is linked into the base driver.

## Dependencies and integration points
Adds include paths for tuner and DVB frontend headers, matching Kconfig's selected tuner/demod dependencies. Integrates with kbuild module naming and media subsystem build layout.

## Risks and test signals
Risks are object list drift when files are added/renamed, mismatch with Kconfig optional modules, and missing include paths for new frontends. Test signals are successful builds for base-only, RC, ALSA, and DVB combinations, with produced module names `cx231xx`, `cx231xx-alsa`, and `cx231xx-dvb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/Makefile -->
