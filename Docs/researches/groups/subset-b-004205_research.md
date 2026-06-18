# subset-b-004205 research

Grouped research report for the requested DVB USB and em28xx source files. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb.h

## Purpose
This is the central public header for the legacy DVB USB framework. It defines the common device, adapter, frontend, streaming, remote-control, firmware, and property structures consumed by individual USB DVB drivers in this directory.

## Important APIs, types, and functions
Key types are `dvb_usb_device_properties`, `dvb_usb_adapter_properties`, `dvb_usb_adapter_fe_properties`, `usb_data_stream_properties`, `usb_data_stream`, `dvb_usb_device`, `dvb_usb_adapter`, and `dvb_usb_fe_adapter`. The header exposes `dvb_usb_device_init()`, `dvb_usb_device_exit()`, `dvb_usb_generic_rw()`, `dvb_usb_generic_write()`, `dvb_usb_nec_rc_key_to_event()`, `usb_cypress_load_firmware()`, and `dvb_usb_get_hexline()`. It also defines logging macros, debug helpers, RC5 scancode helpers, adapter capability flags, USB bulk/isoc stream type flags, cold/warm USB ID descriptors, and Cypress firmware controller identifiers.

## Control flow and state
Drivers populate static `dvb_usb_device_properties` tables. The framework consumes those tables at probe time, downloads firmware when needed, allocates `dvb_usb_device` private state, registers I2C adapters and DVB adapters, attaches frontends/tuners, and configures URB streaming. Runtime state is represented by `DVB_USB_STATE_*`, adapter `DVB_USB_ADAP_STATE_*`, stream `USB_STATE_*`, `powered`, feed counts, active frontend, RC delayed work, and mutexes for USB/data/I2C access.

## Dependencies and integration
The header integrates Linux USB, firmware loading, mutexes, rc-core, DVB frontend/demux/net/dmxdev, DVB PLLs, and shared USB ID definitions. Every driver in this work item includes it directly or through a device header and uses its property/callback contract.

## Risks and test signals
Risk centers on callback contract drift, lifetime of `priv` pointers, mutex ordering, and stream property correctness. Useful tests are compile coverage across `CONFIG_DVB_USB`, probe/remove on warm and cold devices, firmware-loading failure paths, I2C transfer stress, RC polling, and stream start/stop with both bulk and isochronous URBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dw2102.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dw2102.c

## Purpose
This driver supports a large family of DVBWorld, TeVii, Prof, Geniatech, Hauppauge, TechnoTrend, Terratec, and related DVB-S/S2, DVB-C, DVB-T/T2 USB or bridge devices. It multiplexes several hardware protocols behind one `usb_driver` and many `dvb_usb_device_properties` tables.

## Important APIs, types, and functions
`struct dw2102_state` stores initialization state, transfer scratch space, dynamically registered demod/tuner I2C clients, old frontend voltage/status hooks, and last lock state. USB vendor access is centralized in `dw210x_op_rw()`. I2C algorithms include `dw2102_i2c_transfer()`, `dw2102_serit_i2c_transfer()`, `dw2102_earda_i2c_transfer()`, `dw2104_i2c_transfer()`, `dw3101_i2c_transfer()`, `s6x0_i2c_transfer()`, and `su3000_i2c_transfer()`. Attach paths include `dw2104_frontend_attach()`, `dw2102_frontend_attach()`, `ds3000_frontend_attach()`, `su3000_frontend_attach()`, `t220_frontend_attach()`, `m88rs2000_frontend_attach()`, and `tt_s2_4600_frontend_attach()`.

## Control flow and state
Probe tries each property table until `dvb_usb_device_init()` matches. Cold devices use `dw2102_load_firmware()`, which stops the Cypress CPU, writes firmware chunks, restarts the controller, and probes board variants. I2C requests are translated into device-specific USB vendor messages. Frontend attach functions reset GPIOs, attach demods/tuners, install voltage hooks, and sometimes register standalone I2C client drivers. Streaming is mostly framework URB streaming; SU3000-like devices use `su3000_streaming_ctrl()`.

## Dependencies and integration
The file integrates many demod/tuner drivers: `stv0299`, `si21xx`, `stv0288`, `cx24116`, `tda10023`, `mt312`, `zl10039`, `ds3000`, `ts2020`, `stv0900`, `stv6110`, `stb6100`, `cxd2820r`, `tda18271`, `m88rs2000`, and `m88ds3103`. It uses rc-core maps and the DVB USB framework's generic bulk endpoint.

## Risks and test signals
Risks include hard-coded USB command formats, silent partial `dw210x_op_rw()` failures, fixed transfer-size assumptions, firmware chunk handling, dynamically changed global property fields, and I2C client lifetime in disconnect. Test signals include building all selected frontend dependencies, cold/warm probe for each ID, firmware download, EEPROM MAC reads, remote polling, LNB voltage changes, frontend lock transitions, and TT S2-4600 unplug cleanup after demod/tuner client creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dw2102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dw2102.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dw2102.h

## Purpose
This small header binds `dw2102.c` to the DVB USB framework with the module log prefix and debug-print helpers.

## Important APIs, types, and functions
It defines `DVB_USB_LOG_PREFIX` as `dw2102`, includes `dvb-usb.h`, and provides `deb_xfer()` and `deb_rc()` wrappers around `dprintk()` using the `dvb_usb_dw2102_debug` bitmask declared in the C file.

## Control flow and state
There is no runtime state in the header. Its macro definitions affect logging behavior throughout `dw2102.c`, particularly I2C transfer dumps and remote-control diagnostics.

## Dependencies and integration
The header depends on `dvb-usb.h` and indirectly on `CONFIG_DVB_USB_DEBUG` for whether debug calls produce output or compile to `no_printk()`.

## Risks and test signals
Risk is low and limited to debug symbol naming: the macros require `dvb_usb_dw2102_debug` to be visible in the including translation unit. Test signals are successful compilation with and without `CONFIG_DVB_USB_DEBUG` and useful debug output when the module parameter enables transfer or RC bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dw2102.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/gp8psk.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/gp8psk.c

## Purpose
This is the Genpix 8PSK/SkyWalker DVB-S USB driver. It provides Cypress FX2 firmware loading, device power sequencing, BCM4500 secondary firmware loading for rev1 hardware, frontend operations glue, streaming control, and USB ID/property registration.

## Important APIs, types, and functions
`struct gp8psk_state` provides an 80-byte USB control scratch buffer. `gp8psk_usb_in_op()` and `gp8psk_usb_out_op()` serialize vendor control transfers with `usb_mutex`. `gp8psk_power_ctrl()` boots the 8PSK core, powers the Intersil LNB supply, starts CW3K devices, optionally loads BCM4500 firmware, and aborts stale transport streams. `gp8psk_fe_ops` bridges `gp8psk-fe.c` to USB in/out/reload callbacks. `gp8psk_streaming_ctrl()` arms or disarms transport transfer.

## Control flow and state
Probe calls `dvb_usb_device_init()` against `gp8psk_properties`. The framework handles the first firmware image for cold rev1 devices. Power-on reads device configuration, performs hardware-specific initialization, loads secondary firmware when required, and enables LNB power. Frontend attach calls `gp8psk_fe_attach()` with a rev1 flag and the operations table. Streaming starts by sending `ARM_TRANSFER`.

## Dependencies and integration
The driver depends on `gp8psk.h`, `gp8psk-fe.h`, DVB USB generic write helpers, firmware loading, Genpix USB IDs, rc/debug support through the framework, and bulk streaming on endpoint `0x82`.

## Risks and test signals
Important risks are bounded scratch-buffer assumptions, retry semantics in reads, firmware parser termination at `0xff`, product-ID-specific secondary firmware, and NULL buffer use for zero-length out transfers. Test with rev1 and newer warm devices, missing firmware, power cycles, frontend tune/reload, stream arm/disarm, and unplug during a control transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/gp8psk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/gp8psk.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/gp8psk.h

## Purpose
This header supplies the Genpix driver's logging prefix, debug masks, and a few common vendor request constants shared with the implementation and related frontend code.

## Important APIs, types, and functions
It declares `dvb_usb_gp8psk_debug`, defines `deb_info()`, `deb_xfer()`, and `deb_rc()`, and names vendor commands such as `GET_USB_SPEED`, `RESET_FX2`, `FW_VERSION_READ`, `VENDOR_STRING_READ`, `PRODUCT_STRING_READ`, and `FW_BCD_VERSION_READ`.

## Control flow and state
The header contains no mutable state beyond using the externally declared debug module parameter. Its constants are used to form USB control requests and to make logs consistent.

## Dependencies and integration
It includes `dvb-usb.h`, thereby binding the driver to DVB USB structures, IDs, debug support, and rc-core integration.

## Risks and test signals
Risk is low, but command-value changes would break firmware/device protocol compatibility. Compile with debug enabled and exercise version/vendor/product read commands to confirm constants still match firmware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/gp8psk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/m920x.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/m920x.c

## Purpose
This driver supports ULI M920x/M9206-based DVB-T devices including MSI Mega Sky 580, DIGI VOX mini II, LifeView TV Walker Twin, Dposh, Pinnacle PCTV 310e, and VP7049. It implements vendor control access, firmware download, I2C, PID filters, remote-control parsing, frontend/tuner attachments, and property tables.

## Important APIs, types, and functions
The basic transport helpers are `m920x_read()`, `m920x_write()`, and `m920x_write_seq()`. `m920x_init()` initializes RC registers and disables unused adapter filters. `m920x_i2c_xfer()` performs bytewise USB-backed I2C with START/STOP/read/ACK flags. PID filtering is managed by `m920x_set_filter()`, `m920x_update_filters()`, `m920x_pid_filter_ctrl()`, and `m920x_pid_filter()`. Firmware download parses triples of little-endian value/index/size in `m920x_firmware_download()`.

## Control flow and state
Probe distinguishes interface 0 from extra interfaces, then tries device property tables in order. It selects alternate setting 1 and performs device-specific RC/filter initialization. Private `m920x_state` tracks per-adapter PID slots, filter enable state, and repeat suppression. Frontend attach paths cover MT352, TDA10046, QT1010, TDA827x, FMD1216ME, and MT2060 variants.

## Dependencies and integration
The file integrates DVB USB, `mt352`, `tda1004x`, `qt1010`, `tda827x`, `mt2060`, simple tuners, Linux unaligned helpers, rc legacy and rc-core paths, and bulk/isoc stream configuration.

## Risks and test signals
Risks include undocumented I2C ACK handling, zero-byte I2C probe rejection, filter state shadowing, multi-adapter endpoint mapping, firmware format validation, and devices that crash when PID filters are touched. Test signals are firmware upload and reenumeration, dual-tuner TV Walker operation, PID-filter enable/disable, remote repeats, isochronous PCTV 310e streaming, and probe behavior on nonzero interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/m920x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/m920x.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/m920x.h

## Purpose
This header documents and defines the M9206 USB command namespace, debug helper, filter limits, private state, and initialization sequence type used by `m920x.c`.

## Important APIs, types, and functions
It defines vendor request codes `M9206_CORE`, `M9206_I2C`, `M9206_FILTER`, and `M9206_FW`; RC register addresses; firmware-go address; `M9206_MAX_FILTERS`; and `M9206_MAX_ADAPTERS`. `struct m920x_state` stores PID filters, filtering-enabled flags, and RC repeat count. `struct m920x_inits` stores address/data pairs terminated by zero address.

## Control flow and state
The comment block is operational documentation for the bytewise I2C bus protocol. The implementation uses `m920x_inits` arrays for RC/device startup writes and uses `m920x_state` as the DVB USB private area to keep PID and repeat state across callbacks.

## Dependencies and integration
It includes `dvb-usb.h` and depends on the `dvb_usb_m920x_debug` symbol defined by the C file.

## Risks and test signals
Because much of the protocol is inferred, changing flag constants can break I2C. Test by reading/writing frontends through the I2C path, exercising PID filters across all endpoints, and verifying remote repeat suppression after probe initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/m920x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/nova-t-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/nova-t-usb2.c

## Purpose
This driver supports Hauppauge WinTV-NOVA-T USB2 DVB-T receivers using the DiBUSB framework helpers. It mainly supplies Hauppauge-specific remote-control decoding, MAC readout, USB IDs, and DVB USB property wiring.

## Important APIs, types, and functions
`rc_map_haupp_table` maps Hauppauge RC5 scancodes to Linux input keys. `nova_t_rc_query()` sends `DIBUSB_REQ_POLL_REMOTE`, decodes the RC5 custom/data/toggle fields, suppresses immediate repeats via `dibusb_device_state`, and emits legacy RC events. `nova_t_read_mac_address()` constructs a MAC using a fixed Hauppauge OUI and three EEPROM bytes read with `dibusb_read_eeprom_byte()`.

## Control flow and state
Probe calls `dvb_usb_device_init()` with `nova_t_properties`. Framework callbacks then use `dibusb2_0_power_ctrl`, DiBUSB I2C, DiB3000MC frontend/tuner attach, PID filter callbacks, and bulk streaming on endpoint `0x06`. Remote polling is legacy and runs every 100 ms.

## Dependencies and integration
The file depends on `dibusb.h` for common power, streaming, I2C, EEPROM, PID filter, frontend, and tuner helpers. It integrates Cypress FX2 firmware `dvb-usb-nova-t-usb2-02.fw`.

## Risks and test signals
Risks are firmware delivering stale key codes, guessed MAC offset, legacy RC repeat behavior, and DiBUSB helper compatibility. Test cold/warm probe, firmware load, EEPROM MAC read, RC key and repeat behavior, PID filter toggling, and bulk TS streaming under feed start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/nova-t-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/opera1.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/opera1.c

## Purpose
This driver supports Opera1 DVB-S USB2 hardware. It implements an Xilinx/FX2 vendor protocol, I2C over USB, STV0299 frontend setup, tuner attach, LNB voltage, PID filter programming, remote-control decoding, MAC reading, FPGA firmware loading, and USB registration.

## Important APIs, types, and functions
`struct opera1_state` stores the last remote key. `opera1_xilinx_rw()` performs vendor control transfers and special tuner request status checks. `opera1_usb_i2c_msgxfer()` maps pseudo I2C addresses to voltage, stream, remote, or tuner USB requests. `opera1_i2c_xfer()` exposes this as an I2C adapter. Frontend code uses `opera1_stv0299_config`, `opera1_stv0299_set_symbol_rate()`, `opera1_frontend_attach()`, and `opera1_tuner_attach()`.

## Control flow and state
On warm Opera1 devices, `opera1_probe()` loads FPGA firmware before `dvb_usb_device_init()`. Power control writes request `0xb7`. Streaming and PID filter control are encoded as I2C messages to the stream-control pseudo address. Remote polling reads 32 bytes, rebuilds a bitstream, searches for start markers, maps RC5-like values, and emits legacy events.

## Dependencies and integration
The driver depends on DVB USB, `stv0299`, DVB PLL `DVB_PLL_OPERA1`, Cypress FX2 firmware, optional FPGA firmware `dvb-usb-opera1-fpga-01.fw`, and bulk streaming endpoint `0x82`.

## Risks and test signals
Risks include nested USB/I2C locking, Xilinx status expectations, inferred remote bit alignment, PID table address programming, and firmware pointer cleanup. Test firmware and FPGA load paths, STV0299 attach, LNB 13/18V switching, stream start/stop, PID filter programming across indices, MAC read, and RC repeat behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/opera1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/pctv452e.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/pctv452e.c

## Purpose
This driver supports Pinnacle PCTV 452e HDTV USB and TechnoTrend TT-connect S2-3600/S2-3650-CI DVB-S/S2 devices. It implements the 0xaa/0x55 control envelope, I2C bridge, isochronous streaming, STB0899/STB6100 frontend stack, LNB power chips, Common Interface support, RC polling, MAC readout, and probe/disconnect handling.

## Important APIs, types, and functions
`struct pctv452e_state` stores the EN50221 CA object, CA mutex, transaction counter, initialization bit, and last RC key. `tt3650_ci_msg()` and the `tt3650_ci_*` callbacks implement CI attribute/control/slot operations. `pctv452e_i2c_msg()` and `pctv452e_i2c_xfer()` translate I2C to the device command. `pctv452e_power_ctrl()` selects isoc alternate setting and sends reset sequence. `pctv452e_frontend_attach()` attaches STB0899, either LNBP22 plus CI or ISL6423, and `pctv452e_tuner_attach()` attaches STB6100.

## Control flow and state
Probe tries PCTV and TT property tables. Power-on is one-shot via `initialized`. I2C and CI messages increment an 8-bit transaction counter and validate returned sync/id bytes. RC polling reads a 64-byte answer and uses RC5 scancodes. Disconnect releases CI before DVB USB teardown.

## Dependencies and integration
The file integrates `stb0899`, `stb6100`, `isl6423`, `lnbp22`, `dvb_ca_en50221`, `ttpci-eeprom`, rc-core, Linux Ethernet helpers, and USB isochronous transport. It uses source-local large STB0899 register tables.

## Risks and test signals
Risks include fixed 64-byte command envelopes, transaction wrap, partial I2C result interpretation, CI locking/lifetime, different isoc frame geometries per product, and MAC fallback between 24C16/24C64 EEPROMs. Test CI CAM insert/reset/TS enable, frontend/tuner attach, LNB chip attach, RC keyup/keydown, MAC decode, isoc streaming, reset idempotence, and disconnect after CA initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/pctv452e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/technisat-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/technisat-usb2.c

## Purpose
This driver supports TechniSat SkyStar USB HD DVB-S/S2 devices. It implements a bulk-message I2C bridge, firmware state detection, STV090x/STV6110x frontend stack, LNB voltage via demod GPIOs, EEPROM MAC with LRC validation, raw IR decoding, LED control, and delayed LED status work.

## Important APIs, types, and functions
`struct technisat_usb2_state` stores the device pointer, delayed green LED work, power state, last scancode, and a 64-byte scratch buffer. `technisat_usb2_i2c_access()` performs bulk out/in I2C commands and handles firmware status codes. `technisat_usb2_set_led()`, `technisat_usb2_set_led_timer()`, and `technisat_usb2_green_led_control()` manage red/green LEDs. `technisat_usb2_frontend_attach()` attaches STV090x and STV6110x and copies tuner control callbacks into the demod config.

## Control flow and state
Probe initializes the device and, when warm, schedules green LED polling every 500 ms unless disabled. `identify_state` sets alternate setting 1 and uses a version vendor request to decide cold/warm. I2C transfers combine write/read pairs. MAC reads use four LRC-checked attempts. RC polling asks firmware for timing samples, converts durations into `ir_raw_event`s, and lets rc-core decode protocols.

## Dependencies and integration
The driver depends on DVB USB, `stv090x`, `stv6110x`, rc-core raw IR, Cypress FX2 firmware `dvb-usb-SkyStar_USB_HD_FW_v17_63.HEX.fw`, isochronous endpoint `0x02`, and USB control/bulk primitives.

## Risks and test signals
Risks include shared `i2c_mutex` for LED/IR/I2C vendor requests, delayed work after disconnect, buffer truncation to 62 bytes, accepted tuner NAK special case, and global mutation of the STV090x config. Test firmware detection, frontend attach, MAC LRC failure, raw IR decode, LED disabled/enabled modes, delayed work cancellation on unplug, and sustained isoc streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/technisat-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/ttusb2.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/ttusb2.c

## Purpose
This driver supports TechnoTrend and Pinnacle TTUSB2 protocol devices, including PCTV 400e/450e, TT-connect S-2400, and TT-connect CT-3650. It implements the TTUSB command envelope, CI support, I2C bridge, remote polling, power control, DVB-S/C/T frontend attachment, tuner attachment, and property registration.

## Important APIs, types, and functions
`struct ttusb2_state` stores EN50221 CA state, CA mutex, command id, and last RC key. `ttusb2_msg()` frames commands as `0xaa id cmd len data` and validates `0x55 id cmd len` responses. CI callbacks mirror TT3650 commands. `ttusb2_i2c_xfer()` supports single read/write and combined write-read requests through `CMD_I2C_XFER`. Frontend attach functions cover TDA10086, TDA10023, and TDA10048; tuner attach functions cover TDA826x/LNBP21 and TDA827x.

## Control flow and state
Probe tries three property tables. Power control sends `CMD_POWER` first with zero write length and then with one byte. DVB-S paths set alternate setting 3 before attaching. CT-3650 uses two frontends: first DVB-C TDA10023, second DVB-T TDA10048 behind the first frontend's I2C gate, and initializes CI on the first attach. Disconnect releases CI.

## Dependencies and integration
The file integrates DVB USB, `ttusb2.h`, `tda826x`, `tda10086`, `tda1002x`, `tda10048`, `tda827x`, `lnbp21`, EN50221 CA, rc-core, Cypress firmware for some devices, and isochronous streaming.

## Risks and test signals
Risks include static I2C buffers shared under mutex only, unhandled more-than-two-message I2C sequences, CI command timing sleeps, multi-frontend attach ordering, command id wrap, and power command ambiguity. Test all three property groups, CT-3650 dual frontend and CI, RC5 keyup behavior, frontend/tuner attach, isoc streaming, and disconnect after CAM initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/ttusb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/ttusb2.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/ttusb2.h

## Purpose
This header documents the TTUSB2 64-byte command protocol and names command byte constants used by `ttusb2.c`.

## Important APIs, types, and functions
It defines commands for DSP download/boot, power, LNB, version reads, DiSEqC, PID/filter operations, DSP version, I2C transfer, and I2C bitrate. The protocol comment defines the outgoing `0xaa id cmd len data` and incoming `0x55 id cmd len data` framing.

## Control flow and state
There is no runtime state. The constants drive `ttusb2_msg()` request construction and response validation in the C file.

## Dependencies and integration
The header is included only after `dvb-usb.h` in `ttusb2.c` and is tightly coupled to the firmware command ABI.

## Risks and test signals
Risk is command ABI mismatch with firmware. Test by issuing power, I2C, version, RC, and CI commands on supported devices and confirming response headers and lengths match the header's documented frame.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/ttusb2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/umt-010.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/umt-010.c

## Purpose
This is the HanfTek UMT-010 DVB-T USB2 driver. It is a compact DiBUSB-based driver that supplies MT352 demod initialization, tuner attach, firmware/property metadata, and USB registration.

## Important APIs, types, and functions
`umt_mt352_demod_init()` writes a fixed sequence of MT352 clock, reset, AGC, acquisition, and input-frequency registers. `umt_mt352_frontend_attach()` builds a local `mt352_config` and attaches the demod at address `0x0f`. `umt_tuner_attach()` attaches a TUA6034 PLL at address `0x61`. `umt_probe()` calls `dvb_usb_device_init()`.

## Control flow and state
Probe matches cold/warm HanfTek IDs, loads Cypress FX2 firmware through the framework, and configures one adapter. Framework callbacks handle DiBUSB power, DiBUSB I2C, DiBUSB streaming control, and bulk endpoint `0x06`. There is no custom persistent private state beyond the DiBUSB adapter private allocation.

## Dependencies and integration
The file depends on `dibusb.h`, `mt352`, DVB PLL support, firmware `dvb-usb-umt-010-02.fw`, and the DVB USB core.

## Risks and test signals
Risks are hard-coded demod register values, unchecked `mt352_write()` return values in init, and tuner attach using a NULL I2C adapter argument inherited from older PLL API expectations. Test cold/warm probe, demod attach, tuner lock, bulk streaming, power cycles, and firmware absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/umt-010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/usb-urb.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/usb-urb.c

## Purpose
This DVB USB library file implements generic bulk and isochronous URB allocation, submission, completion, resubmission, kill, and teardown for transport stream data paths.

## Important APIs, types, and functions
`usb_urb_init()` copies stream properties and dispatches to `usb_bulk_urb_init()` or `usb_isoc_urb_init()`. `usb_urb_submit()` submits initialized URBs and rolls back on failure. `usb_urb_kill()` kills submitted URBs. `usb_urb_exit()` kills, frees URBs, and frees coherent buffers. `usb_urb_complete()` handles bulk/isoc completions, forwards data to `stream->complete()`, resets isoc frame descriptors, and resubmits the URB.

## Control flow and state
Initialization allocates DMA-coherent buffers, fills URBs with endpoint, interval, frame layout, callback, and DMA flags, then increments `urbs_initialized`. Submission increments `urbs_submitted`. Completion ignores normal and timeout statuses, exits on shutdown/kill statuses, processes payload, and resubmits with `GFP_ATOMIC`. Buffer lifetime is tracked with `USB_STATE_URB_BUF`.

## Dependencies and integration
The file depends on `dvb-usb-common.h`, Linux USB URB APIs, DVB USB debug macros, and the `usb_data_stream` structure defined in `dvb-usb.h`. Individual drivers supply stream properties in their property tables.

## Risks and test signals
Risks include unhandled `usb_submit_urb()` errors in completion, resubmission after transient errors, allocation cleanup if URB allocation fails after buffers were allocated, endpoint type mismatches, and isoc frame sizing mistakes from driver tables. Test with bulk and isoc devices, stream start/stop races, unplug during streaming, memory pressure during init, and packet/frame error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/usb-urb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp702x-fe.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp702x-fe.c

## Purpose
This file implements the custom DVB-S frontend operations for Twinhan VP7020/VP7021 StarBox devices, where much frontend control is hidden behind firmware commands rather than standard demod/tuner drivers.

## Important APIs, types, and functions
`struct vp702x_fe_state` embeds `struct dvb_frontend`, stores the USB device, SEC voltage/tone state, LNB command buffer, cached lock/signal/SNR values, and status polling cadence. `vp702x_fe_refresh_state()` reads status and tuner registers. `vp702x_fe_set_frontend()` encodes frequency, symbol rate, voltage flag, and checksum into an 8-byte command. DiSEqC, tone, voltage, metrics, init, release, and tune-settings callbacks populate `vp702x_fe_ops`.

## Control flow and state
Status is rate-limited with `next_status_check`; locked frontends poll slower than unlocked ones. Tuning builds a firmware command using kHz frequency and scaled symbol rate, then sends a USB in/out operation through the parent driver buffer. SEC voltage/tone changes update `lnb_buf`, recompute checksum, and send it through the same command path.

## Dependencies and integration
The file depends on `vp702x.h` for USB helpers, command constants, debug macros, and shared device buffer locking. It returns a software frontend from `vp702x_fe_attach()` for use by `vp702x.c`.

## Risks and test signals
Risks include firmware-specific encoding, limited DiSEqC message length, cached status staleness, implicit lock polarity where `lock == 0` means locked, and shared buffer concurrency. Test tune success/failure, lock acquisition, signal/SNR reads, LNB voltage/tone changes, DiSEqC commands up to four bytes, and frontend release on unplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp702x-fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp702x.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp702x.c

## Purpose
This is the USB-side driver for TwinhanDTV StarBox VP702x DVB-S devices. It implements vendor USB helpers, shared buffer management, PID filter/PLD programming, MAC readout, frontend attach, and DVB USB registration.

## Important APIs, types, and functions
`struct vp702x_adapter_state` tracks PID filter count, bypass capability, and active filter bits. `vp702x_usb_in_op()`, `vp702x_usb_inout_op()`, and `vp702x_usb_inout_cmd()` serialize vendor command transfers. `vp702x_set_pld_mode()`, `vp702x_set_pld_state()`, `vp702x_set_pid()`, and `vp702x_init_pid_filter()` program PLD PID filtering. `vp702x_frontend_attach()` powers the tuner, reads system string, initializes filters, attaches the custom frontend, and powers the tuner back on.

## Control flow and state
Probe initializes DVB USB, allocates `vp702x_device_state.buf`, and initializes `buf_mutex`. Many operations reuse and resize this buffer under the mutex. The driver declares a Cypress FX2 firmware with `no_reconnect = 1`. Disconnect frees the shared buffer under lock, then exits DVB USB. RC support is effectively disabled by a compiled-out block.

## Dependencies and integration
The file depends on `vp702x.h`, `vp702x-fe.c`, Cypress FX2 firmware `dvb-usb-vp702x-02.fw`, DVB USB bulk streaming, and legacy RC map infrastructure.

## Risks and test signals
Risks include buffer lifetime during disconnect, resize while callbacks are active, disabled RC path, limited USB ID coverage with VP7020 entries commented out, and PID filter state encoded into PLD registers without error propagation. Test firmware/probe, system-string read, PID filter initialization, MAC EEPROM reads, frontend tune/streaming, and unplug during frontend callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp702x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp702x.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp702x.h

## Purpose
This header defines the VP702x command ABI, debug helpers, shared private state, and cross-file prototypes for the StarBox driver and custom frontend.

## Important APIs, types, and functions
It declares debug macros, consecutive request codes `REQUEST_OUT` and `REQUEST_IN`, firmware subcommands such as `GET_SYSTEM_STRING`, `SET_DISEQC_CMD`, `SET_LNB_POWER`, and `SET_PID_FILTER`, one-direction requests for EEPROM/status/tuner/FX2 operations, `struct vp702x_device_state`, `vp702x_fe_attach()`, `vp702x_usb_inout_op()`, and `vp702x_usb_in_op()`.

## Control flow and state
The command comments document the byte layouts used by `vp702x.c` and `vp702x-fe.c`. `vp702x_device_state` owns the shared mutable buffer and mutex used for command composition and response parsing.

## Dependencies and integration
It includes `dvb-usb.h` and binds the USB transport file to the frontend file. Constants are firmware ABI and must match the device's Cypress/PLD firmware.

## Risks and test signals
Risks are ABI drift and mistaken command layouts, especially checksum-bearing tune/LNB commands. Test command helpers with system string, status, EEPROM, tuner power, tune, DiSEqC, and PID filter requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp702x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp7045-fe.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp7045-fe.c

## Purpose
This file implements a firmware-backed DVB-T frontend for Twinhan VP7045/7046 USB devices. The actual MT352/tuner programming is hidden in device firmware, so the frontend mostly sends high-level tune commands and reads status registers.

## Important APIs, types, and functions
`struct vp7045_fe_state` embeds `struct dvb_frontend` and stores the parent USB device. Read callbacks use `vp7045_read_reg()` for lock status, BER, uncorrected blocks, signal strength, and SNR. `vp7045_fe_set_frontend()` encodes frequency in kHz plus a bandwidth selector of 6/7/8 MHz and sends `LOCK_TUNER_COMMAND`. `vp7045_fe_attach()` allocates and returns the frontend.

## Control flow and state
Tuning validates bandwidth, formats a five-byte command, and waits 200 ms through `vp7045_usb_op()`. Status combines bits from registers 0, 1, and 3 and clears lock unless carrier, Viterbi, and sync are present. There is no persistent tuner state beyond the frontend private pointer.

## Dependencies and integration
The file depends on `vp7045.h` for USB operations and register command constants. It is attached by `vp7045.c` and reports DVB-T capabilities to the DVB core.

## Risks and test signals
Risks include register bit interpretations, unsupported bandwidth values returning `-EINVAL`, inverted signal strength, and firmware-dependent tune latency. Test all supported bandwidths, status transitions, BER/SNR/unc reads, invalid bandwidth handling, and frontend release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp7045-fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp7045.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp7045.c

## Purpose
This USB-side driver supports TwinhanDTV Alpha/MagicBox II and DigitalNow TinyUSB2 DVB-T devices. It implements the fixed 20-byte out/12-byte in command protocol, power control, EEPROM/MAC reads, RC polling, frontend attach, and USB property registration.

## Important APIs, types, and functions
`vp7045_usb_op()` is the core serialized command helper; it clamps output to 19 bytes and input to 11 bytes, writes via `TH_COMMAND_OUT`, sleeps, then reads via `TH_COMMAND_IN`. `vp7045_read_reg()` reads tuner/demod registers, `vp7045_power_ctrl()` toggles tuner power, `vp7045_rc_query()` reads NEC-like keys, `vp7045_read_eeprom()` and `vp7045_read_mac_addr()` fetch EEPROM bytes, and `vp7045_frontend_attach()` logs firmware strings and attaches `vp7045_fe_attach()`.

## Control flow and state
Probe relies on `dvb_usb_device_init()` and `vp7045_properties`. The DVB USB private area is a 20-byte command buffer. RC polling ignores no-key value `0x44` and emits NEC scancodes with address 0. Streaming uses bulk endpoint `0x02` with seven 4096-byte buffers.

## Dependencies and integration
The file depends on `vp7045.h`, `vp7045-fe.c`, Cypress FX2 firmware `dvb-usb-vp7045-01.fw`, rc-core, DVB USB bulk streaming, and Twinhan USB IDs.

## Risks and test signals
Risks include command buffer truncation, fixed command packet sizes, no explicit keyup on no-key, EEPROM byte-by-byte latency, and firmware version string assumptions. Test cold/warm probe, firmware string reads, tuner power, MAC read, RC key delivery, DVB-T tuning through the frontend, and stream start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp7045.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp7045.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp7045.h

## Purpose
This header defines the VP7045 command constants, EEPROM offsets, public USB helper prototypes, and frontend attach prototype shared by the VP7045 USB and frontend files.

## Important APIs, types, and functions
It defines Twinhan vendor requests `TH_COMMAND_IN` and `TH_COMMAND_OUT`; command bytes for tuner register access, RC value read, tuner power, USB speed, tuner lock, signal read, EEPROM get/set, FX2 reset, firmware/vendor/product strings; MAC EEPROM addresses; `vp7045_fe_attach()`, `vp7045_usb_op()`, and `vp7045_read_reg()`.

## Control flow and state
There is no runtime state. The constants directly determine the first byte passed through `vp7045_usb_op()` and EEPROM offsets used for MAC reads.

## Dependencies and integration
It includes `dvb-usb.h` and provides the compile-time ABI contract between `vp7045.c` and `vp7045-fe.c`.

## Risks and test signals
Risks are firmware command mismatch and MAC offset mistakes. Test by reading version/vendor/product strings, reading the MAC EEPROM offsets, reading registers through the frontend, and toggling tuner power.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp7045.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/Kconfig

## Purpose
This Kconfig file defines build options for Empia EM28xx USB media devices: core device support, analog/V4L2 support, ALSA audio, DVB/ATSC support, and remote-control support.

## Important APIs, types, and functions
The important symbols are `VIDEO_EM28XX`, `VIDEO_EM28XX_V4L2`, `VIDEO_EM28XX_ALSA`, `VIDEO_EM28XX_DVB`, and `VIDEO_EM28XX_RC`. Dependency and select clauses pull in core media, I2C, tuner, TV EEPROM, videobuf2, audio, rc-core, many demod/tuner frontends, and legacy GPIO support when needed.

## Control flow and state
There is no runtime control flow. The file controls kernel configuration resolution: selecting modules enables corresponding object builds in the Makefile and auto-selects subdevice drivers when `MEDIA_SUBDRV_AUTOSELECT` is enabled.

## Dependencies and integration
It integrates with the media Kconfig tree and the EM28xx Makefile. The DVB symbol selects a broad list of frontend/tuner dependencies such as LGDT, ZL10353, TDA10023, DRX, CXD2820R, TDA18271, M88DS3103, TS2020, SI2168, SI2157, and others.

## Risks and test signals
Risks include over-selecting unavailable dependencies, modular dependency conflicts, and missing selects for new boards. Test with `allmodconfig`, `allyesconfig`, minimal `VIDEO_EM28XX_DVB=m`, `VIDEO_EM28XX_RC=y/m`, and configurations where `MEDIA_SUBDRV_AUTOSELECT` is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/Makefile

## Purpose
This Makefile maps EM28xx Kconfig symbols to kernel module object lists and include paths.

## Important APIs, types, and functions
`em28xx-y` defines the core module objects: `em28xx-core.o`, `em28xx-i2c.o`, `em28xx-cards.o`, and `em28xx-camera.o`. Composite object groups include `em28xx-v4l-objs`, `em28xx-alsa-objs`, and `em28xx-rc-objs`. `obj-$(CONFIG_VIDEO_EM28XX*)` lines build core, V4L2, ALSA, DVB, and RC modules. `ccflags-y` adds tuner and DVB frontend include directories.

## Control flow and state
There is no runtime state. Build control is driven by Kconfig expansion: selected symbols decide which modules are linked and which objects form each module.

## Dependencies and integration
The Makefile integrates the EM28xx source directory with the kernel media build, tuner headers, and DVB frontend headers.

## Risks and test signals
Risks include object list drift when files are renamed, missing include paths for new frontend headers, and Kconfig/Makefile symbol mismatches. Test with `make M=drivers/media/usb/em28xx`, module builds for each symbol combination, and clean builds after adding or removing EM28xx source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/Makefile -->
