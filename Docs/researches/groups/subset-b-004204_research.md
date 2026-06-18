# subset-b-004204 Research

Grouped research for DVB USB library and device drivers under `sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib0700_devices.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib0700_devices.c

Purpose: DiB0700 board catalog and board-specific attach logic. It binds many DiBcom/Pinnacle/Hauppauge/Terratec/Elgato/Microsoft USB IDs to `struct dvb_usb_device_properties`, and supplies the GPIO, I2C enumeration, demodulator, tuner, PID filter, remote-control, firmware, and transport-stream settings needed by each hardware design.

Important APIs/types/functions: `struct dib0700_adapter_state` stores saved tuner `set_params`, optional frontend firmware, and attached `dib7000p_ops`/`dib8000_ops`. The file exports `dib0700_usb_id_table`, `dib0700_devices[]`, and `dib0700_device_count`. Attach paths include `bristol_frontend_attach()`, `stk7700p_frontend_attach()`, `stk7070p_frontend_attach()`, `stk807x_frontend_attach()`, `stk9090m_frontend_attach()`, `nim9090md_frontend_attach()`, `nim7090_frontend_attach()`, `s5h1411_frontend_attach()`, `lgdt3305_frontend_attach()`, `pctv340e_frontend_attach()`, and `xbox_one_attach()`. Tuner paths attach MT2060/MT2266/XC2028/XC4000/XC5000/DiB0070/DiB0090/MxL5007T/TDA18250 parts. PID helpers dispatch to DiB7000M/P, DiB8000, or DiB9000 firmware implementations.

Control flow: `dib0700_core` probes using the exported property array. Each property entry declares adapters, frontends, PID capability, stream endpoint, device descriptions, and RC map. Frontend attach callbacks power rails and reset pins with `dib0700_set_gpio()`, set bridge clocks and I2C speed, enumerate demods to final I2C addresses, initialize demod configs, and sometimes enable new firmware I2C APIs. Tuner attach callbacks then obtain tuner-side I2C masters and wrap tuner operations, often saving the original `set_params` and replacing it with board-specific WBD, AGC, LNA, PLL, or sampling compensation logic. Some DiB9000 paths request `dib9090.fw` during frontend attach and release it after tuner post-PLL initialization.

State and persistence: persistent state lives in `dib0700_state` from the core driver, per-adapter `dib0700_adapter_state`, frontend ops structs, the global module parameter `force_lna_activation`, per-board static config tables, and dynamically registered I2C clients for the Xbox One tuner path. Hardware-visible state is GPIO direction/value, bridge clocking, I2C speed/API mode, demod I2C addresses, firmware-loaded demod microcode, PID filter tables, and RC protocol setup. No disk persistence exists, but firmware files must be present.

Dependencies and integration: depends on `dib0700.h`, `dib07x0.h`, DiB3000/7000/8000/9000 demod drivers, tuner drivers, S5H1411/LGDT3305/MN88472 frontend drivers, rc-core maps, Linux firmware loading, USB ID macros, and the generic DVB USB library. Integration is through the `dvb_usb_device_properties` contract consumed by probe/init code.

Risks: the file is highly table-driven and index-sensitive; enum values must stay aligned with `dib0700_usb_id_table[]` and `devices[]` references. Many GPIO delay sequences are empirical and board-specific. Firmware ownership in DiB9000 paths must release `frontend_firmware` on every failure path. Several callbacks override frontend ops and rely on saved function pointers. Static tuner config structs are mutated at attach time, which can be fragile if multiple devices share the module. The Xbox One path manually manages I2C clients and module references.

Test signals: build with all referenced frontend/tuner configs enabled and with `CONFIG_DVB_DIB9000`; probe representative single, dual, diversity, ATSC, and Xbox One devices; verify firmware loading for `dvb-usb-dib0700-1.20.fw` and `dib9090.fw`; test RC polling and bulk RC modes across firmware versions; stream from endpoints `0x02`, `0x03`, and `0x82`; exercise PID filters on full-speed and high-speed USB; and validate RF lock after band changes, LNA switching, suspend/resume, and device disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib0700_devices.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib07x0.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib07x0.h

Purpose: small shared header for DiB07x0 board GPIO numbering. It gives board files symbolic names for the sparse GPIO line numbers used by the bridge and standardizes input/output direction constants.

Important APIs/types: `enum dib07x0_gpios` maps `GPIO0` through `GPIO10` to hardware line numbers, where several logical GPIO labels skip numeric values. `GPIO_IN` and `GPIO_OUT` encode direction values passed to `dib0700_set_gpio()`.

Control flow: board attach callbacks include this header indirectly through DiB0700 headers and pass these constants into reset, power, LNA, LED, tuner, demod, and analog-component GPIO sequences.

State and persistence: no runtime state. The constants describe stable hardware wiring assumptions used to program persistent GPIO state in the bridge.

Dependencies and integration: integrated with DiB0700 board code and bridge GPIO helpers. It intentionally avoids broader includes beyond its guard.

Risks: a wrong GPIO mapping silently toggles the wrong rail or reset line. The sparse numbering makes integer literals in board files easy to misread, so symbolic use is important.

Test signals: compile DiB0700 board files, then hardware-probe boards whose attach paths exercise GPIO6/GPIO9/GPIO10 resets, GPIO0/GPIO1 LED or LNA control, and tuner reset/sleep lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib07x0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-common.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-common.c

Purpose: shared implementation for older DiBUSB receivers. It supplies firmware command wrappers for streaming, power, I2C master transfers, EEPROM reads, PID filter control, and legacy remote-control decoding used by both DiB3000M-B and DiB3000M-C/P device drivers.

Important APIs/functions: exported symbols include `dibusb_streaming_ctrl()`, `dibusb_pid_filter()`, `dibusb_pid_filter_ctrl()`, `dibusb_power_ctrl()`, `dibusb2_0_streaming_ctrl()`, `dibusb2_0_power_ctrl()`, `dibusb_i2c_algo`, `dibusb_read_eeprom_byte()`, `rc_map_dibusb_table`, and `dibusb_rc_query()`. The internal `dibusb_i2c_msg()` builds `DIBUSB_REQ_I2C_READ`/`WRITE` bulk messages.

Control flow: frontend drivers attach demods that fill `struct dibusb_state.ops`. Streaming starts by optionally enabling the demod FIFO, then for USB2 devices asks firmware to select streaming mode and enable/disable the FX2 stream. PID helpers delegate to demod ops. I2C transfers are serialized with `d->i2c_mutex`, combine write-then-read pairs, reject oversized writes, and protect EEPROM address `0x50` from raw reads without an offset. RC polling sends `DIBUSB_REQ_POLL_REMOTE`, decodes the five-byte NEC-like buffer via `dvb_usb_nec_rc_key_to_event()`, and reports legacy input events.

State and persistence: state is stored in per-adapter `struct dibusb_state` ops/tuner flags and in USB firmware power/streaming/PID tables. `rc_map_dibusb_table` is a static keymap shared by all supported remotes. No persistent storage is written; EEPROM reads are read-only calibration/config inputs.

Dependencies and integration: depends on `dibusb.h`, generic `dvb_usb_generic_rw()`/`write()`, I2C core, demod operation callbacks from DiB3000 drivers, and the DVB USB legacy RC helper.

Risks: `MAX_XFER_SIZE` limits are manual and the code only checks write length, so unusual I2C shapes depend on caller behavior. `dibusb_i2c_xfer()` returns the number of processed messages, which can be partial on error. Legacy keymap size is hard-coded by users to 111 entries. USB2 power-off returns success without writing sleep state.

Test signals: DiBUSB MB/MC probe, I2C scan through demod/tuner, EEPROM byte reads for IF calibration, streaming start/stop with PID filter toggles, full-speed USB operation requiring hardware PID filtering, RC key and repeat decoding, and disconnect while polling/streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-mb.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-mb.c

Purpose: USB driver for DiB3000M-B based DiBUSB devices, covering many early USB1.1 and USB2 DVB-T sticks. It selects one of several `dvb_usb_device_properties` profiles during probe and binds board-specific firmware, endpoints, tuner selection, PID filtering, I2C, and legacy RC behavior.

Important APIs/functions: `dibusb_probe()` tries `dibusb1_1_properties`, `dibusb1_1_an2235_properties`, `dibusb2_0b_properties`, and `artec_t1_usb2_properties`. `dibusb_dib3000mb_frontend_attach()` attaches the DiB3000MB demod and installs `dib3000mb_i2c_gate_ctrl()`. Tuner helpers attach Thomson TUA6010XS, Panasonic TDA665X, or probe between them by reading tuner address `0x60`.

Control flow: USB IDs in `dibusb_dib3000mb_table[]` describe cold/warm devices. Probe delegates firmware download and initialization to `dvb_usb_device_init()`. Frontend attach sets demod address `0x8`, attaches via `dib3000mb_attach()`, and installs the gate callback. Tuner attach either fixes `st->tuner_addr` or probes Panasonic versus Thomson through an I2C write/read while the demod gate is open. Property blocks wire firmware names, Cypress controller type, stream endpoint `0x02` or `0x06`, power control, DiBUSB I2C algorithm, PID controls, and legacy RC map.

State and persistence: `struct dibusb_state` holds the tuner address and demod xfer ops. Persistent hardware state is firmware-loaded Cypress controller state, demod/tuner I2C programming, PID filter entries, power mode, and streaming mode. Module state includes adapter-number options only.

Dependencies and integration: depends on `dibusb-common.c`, DiB3000MB demod, `dvb_pll_attach()`, Cypress firmware loading, and the DVB USB core.

Risks: the driver relies on USB ID table order. Tuner probing assumes the Panasonic response can distinguish board populations. Multiple property profiles are tried sequentially; probe failures must leave no partial device state. Optional faulty Anchor IDs are hidden behind `CONFIG_DVB_USB_DIBUSB_MB_FAULTY`.

Test signals: cold and warm probe for each firmware profile, USB1.1 with hardware PID filter, endpoint `0x02` and `0x06` streaming, Thomson/Panasonic tuner detection, RC key events, firmware reconnect/no-reconnect behavior, and unload/reload without stale USB halts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-mb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-mc-common.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-mc-common.c

Purpose: shared DiB3000MC/P frontend and tuner attachment code for DiBUSB MC devices. It provides AGC/config tables and exported attach helpers used by `dibusb-mc.c`.

Important APIs/functions: exports `dibusb_dib3000mc_frontend_attach()` and `dibusb_dib3000mc_tuner_attach()`. Static configs include `dib3000p_mt2060_agc_config`, `stk3000p_dib3000p_config`, `dib3000p_panasonic_agc_config`, `mod3000p_dib3000p_config`, and `stk3000p_mt2060_config`.

Control flow: frontend attach handles a Lite-On warm-device delay, tries `dib3000mc_attach()` first at `DEFAULT_DIB3000P_I2C_ADDRESS` then at `DEFAULT_DIB3000MC_I2C_ADDRESS`, and, on success, stores PID parse/control callbacks in `struct dibusb_state`. Tuner attach computes MT2060 first-IF calibration from EEPROM for Lite-On and MOD3001 variants, gets the demod tuner I2C master, tries `mt2060_attach()`, and falls back to Panasonic PLL parameters if MT2060 is absent.

State and persistence: adapter private state records whether MT2060 is present and exposes demod PID ops. EEPROM calibration bytes influence per-attach IF values but are not modified.

Dependencies and integration: depends on DiB3000MC demod APIs, MT2060, generic DVB PLL, `dibusb_read_eeprom_byte()`, and DiBUSB common I2C/power/streaming helpers.

Risks: EEPROM interpretation is vendor/product specific and tolerates odd values only with warnings. Fallback tuner attach returns `-ENOMEM` if PLL attach fails, which conflates memory and hardware absence. Correct PID filtering depends on ops being populated only after frontend attach succeeds.

Test signals: Lite-On and MOD3001 devices with calibration EEPROM data, DiB3000P versus DiB3000MC address fallback, MT2060 present and absent cases, PID parser enable/disable, and stream lock after retuning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-mc-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-mc.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-mc.c

Purpose: USB driver for DiB3000M-C/P based DiBUSB USB2 DVB-T devices. It defines USB IDs, one device-property profile, and module registration using common MC attach helpers.

Important APIs/functions: `dibusb_mc_probe()` calls `dvb_usb_device_init()`. `dibusb_mc_properties` wires `dibusb2_0_streaming_ctrl()`, `dibusb_pid_filter()`, `dibusb_pid_filter_ctrl()`, `dibusb_dib3000mc_frontend_attach()`, `dibusb_dib3000mc_tuner_attach()`, `dibusb2_0_power_ctrl()`, `dibusb_i2c_algo`, and legacy `dibusb_rc_query()`.

Control flow: matching USB IDs enter probe, firmware `dvb-usb-dibusb-6.0.0.8.fw` is loaded for Cypress FX2 cold devices, a single adapter/frontend is initialized, and USB bulk endpoint `0x06` carries transport-stream data. Device descriptions cover DiBcom MOD3000P, Artec/Lite-On/MSI/Grandtec/Leadtek/Humax variants.

State and persistence: per-adapter `struct dibusb_state` stores demod ops and tuner flags. Device state is inherited from the DVB USB core: I2C adapter, demux, frontend, RC polling, stream URBs, and firmware-loaded bridge.

Dependencies and integration: integrates the DiBUSB common module, MC common attach module, Cypress firmware loader, DVB USB core, and Linux USB driver registration.

Risks: ID table order is explicitly fixed and used by property descriptions. `rc_map_size` is a numeric FIXME. All boards share one property profile, so board-specific quirks must live in common attach logic or USB ID checks.

Test signals: cold/warm enumeration for every listed USB ID, firmware download, endpoint `0x06` bulk streaming with 32 PID filters, remote polling, Lite-On calibration path, and driver disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-mc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb.h

Purpose: common protocol and state header for DiBUSB receivers. It documents firmware request bytes, IOCTL command values, private state structs, exported helper prototypes, and the default RC polling interval.

Important APIs/types: request macros cover I2C read/write, remote polling, streaming mode, interrupt read, and power/stream IOCTLs. `struct dibusb_state` stores `struct dib_fe_xfer_ops`, MT2060 presence, and tuner address. `struct dibusb_device_state` holds legacy RC repeat bookkeeping. Externs expose I2C algorithm, MC attach helpers, stream/PID/power helpers, keymap, RC query, and EEPROM read.

Control flow: `dibusb-common.c`, `dibusb-mb.c`, and `dibusb-mc*.c` include this header so property tables and attach callbacks agree on firmware protocol bytes and private-state layout.

State and persistence: no state is allocated here, but the structures define adapter/device private memory persisted for a bound USB device.

Dependencies and integration: includes `dvb-usb.h`, DiB3000/DiB3000MC demod headers, and MT2060 tuner interfaces.

Risks: the header duplicates `MAX_XFER_SIZE` with the common C file. Protocol comments are the source of truth for firmware packet shapes, so drift between comments, macros, and firmware behavior is a maintenance risk.

Test signals: compile all DiBUSB modules, validate I2C and IOCTL request bytes with USB tracing, and exercise both MB and MC property paths using the shared prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/digitv.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/digitv.c

Purpose: DVB USB driver for Nebula Electronics uDigiTV DVB-T USB2.0. It implements a device-specific 7-byte bulk control protocol, an I2C adapter for the COFDM demodulator, frontend/tuner attach, remote-control polling, and USB driver registration.

Important APIs/functions: `digitv_ctrl_msg()` is the central protocol helper. `digitv_i2c_algo` implements `digitv_i2c_xfer()`/`digitv_i2c_func()`. Frontend paths include `digitv_mt352_demod_init()`, `digitv_frontend_attach()`, `digitv_tuner_attach()`, and `digitv_nxt6000_tuner_set_params()`. `digitv_rc_query()` decodes the local RC table. `digitv_probe()` performs post-init remote setup.

Control flow: probe calls `dvb_usb_device_init()` with FX2 firmware `dvb-usb-digitv-02.fw`; on success it sets remote type and clears remote state. I2C transfers are serialized, support write and write-then-read transactions, and translate them to COFDM read/write commands. Frontend attach tries MT352 first, then NXT6000, recording `is_nxt6000`; tuner attach installs a TDED4 PLL and, for NXT6000, replaces tuner `set_params` with a USB tuner-write command. RC polling reads four bytes, acknowledges/clears the device buffer, and maps RC5 custom/data to keycodes.

State and persistence: `struct digitv_state` persists `is_nxt6000` and shared 7-byte send/receive buffers in device private memory. Hardware state includes firmware-loaded bridge, demod registers, tuner PLL registers, and remote mode.

Dependencies and integration: depends on `digitv.h`, MT352, NXT6000, DVB PLL, generic DVB USB bulk control, I2C core, and legacy DVB USB RC handling.

Risks: `digitv_ctrl_msg()` rejects lengths over four bytes and uses shared buffers protected only by higher-level locks where callers provide them. The I2C adapter warns but does not support more than two messages well. `identify_state()` infers cold state from missing manufacturer/product strings, which is device-specific.

Test signals: cold firmware load, warm probe, MT352 and NXT6000 variants, I2C register reads/writes, tuner retune on NXT6000, endpoint `0x02` streaming, RC key read/ack behavior, and unplug during RC polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/digitv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/digitv.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/digitv.h

Purpose: private header for the Nebula uDigiTV driver. It defines the log prefix, device private state, and command bytes for the 7-byte USB control protocol.

Important APIs/types: `struct digitv_state` stores the NXT6000/MT352 frontend choice and reusable `sndbuf`/`rcvbuf`. Command macros include EEPROM read, COFDM read/write, tuner write, remote read/write/type, and device init.

Control flow: `digitv.c` uses the protocol constants in `digitv_ctrl_msg()`, I2C transfer, tuner programming, RC polling, and probe-time remote setup.

State and persistence: private buffers persist for the lifetime of the USB device. The command constants encode device firmware state transitions but do not allocate state themselves.

Dependencies and integration: includes `dvb-usb.h` and is private to the Digitv driver.

Risks: the protocol is documented as reverse-engineered/SDK-derived and only supports up to four payload bytes in the C implementation. Adding new commands requires preserving the fixed seven-byte packet ABI.

Test signals: compile the driver and trace USB control packets for COFDM read/write, remote reads, remote type setup, and NXT6000 tuner writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/digitv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtt200u-fe.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtt200u-fe.c

Purpose: custom DVB-T frontend implementation for WideView/Yakumo/Hama/Typhoon/Yuan DTT200U-style devices whose demodulator control is exposed through simple USB firmware commands rather than a normal demod driver.

Important APIs/types/functions: `struct dtt200u_fe_state` stores device pointer, cached status/properties, embedded `struct dvb_frontend`, an 80-byte command buffer, and a mutex. `dtt200u_fe_attach()` allocates and returns the frontend. Frontend ops implement init/sleep, set/get frontend, tune settings, status, BER, signal strength, SNR, uncorrected blocks, and release.

Control flow: read callbacks lock `data_mutex`, place a GET command byte in `data[0]`, call `dvb_usb_generic_rw()`, decode the returned bytes, and unlock. `set_frontend()` validates bandwidth, writes `SET_BANDWIDTH`, converts frequency to 250 kHz units, then writes `SET_RF_FREQ`. `get_tune_settings()` requires a 1500 ms delay. Attach initializes state, copies `dtt200u_fe_ops`, and stores the private pointer.

State and persistence: frontend state persists in allocated memory until `release`. Firmware maintains tune status, signal counters, bandwidth, and RF frequency. The local `fep` cache is returned by `get_frontend()` but is not updated by `set_frontend()` in this file, so it is only a local snapshot.

Dependencies and integration: used by `dtt200u.c`; depends on generic DVB USB bulk control and DVB frontend core.

Risks: all command traffic shares one mutable buffer, so mutex coverage is critical. Unknown tune status maps to no lock. `get_frontend()` returns cached state that may be stale. Frequency division assumes firmware wants 250 kHz units and ignores unsupported bandwidths.

Test signals: frontend attach/release, tune requests for 6/7/8 MHz, lock and timeout status transitions, BER/SNR/AGC/uncorrected block reads, invalid bandwidth rejection, and repeated open/close under USB error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtt200u-fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtt200u.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtt200u.c

Purpose: DVB USB driver for WideView/Yakumo/Hama/Typhoon/Yuan/Miglia WT200U/WT220U-style USB2 DVB-T receivers. It implements firmware commands for power, streaming, PID filtering, rc-core remote handling, device profiles, and USB registration.

Important APIs/functions: `dtt200u_power_ctrl()`, `dtt200u_streaming_ctrl()`, `dtt200u_pid_filter()`, `dtt200u_rc_query()`, `dtt200u_frontend_attach()`, and `dtt200u_usb_probe()` are the active callbacks. Property blocks cover DTT200U, WT220U, Freecom endpoint variant, ZL353 variant, and Miglia firmware-only transition.

Control flow: probe tries each property profile through `dvb_usb_device_init()`. Power-on writes `SET_INIT`. Streaming writes `SET_STREAMING` and, on stop, resets the PID table. PID filter writes index and 13-bit PID, or zero when disabled. RC query reads five bytes, decodes NEC/NECX scancodes with checksum validation, and reports keydown/repeat/keyup via rc-core. Frontend attach delegates to `dtt200u_fe_attach()`.

State and persistence: `struct dtt200u_state` contains an 80-byte data buffer protected by the device data mutex. Firmware state persists power initialization, streaming enable, PID table, RC buffer, and frontend tuning state.

Dependencies and integration: depends on `dtt200u-fe.c`, `dtt200u.h`, DVB USB core, rc-core, and Cypress FX2 firmware loading. It uses generic bulk endpoint `0x01` for commands and endpoint `0x02` or `0x06` for MPEG-TS.

Risks: several property initializers are visually misindented, so future edits can easily place fields at the wrong nesting level. Miglia profile has no adapter/frontend because it changes USB ID after firmware upload. RC checksum failures intentionally key up, which may hide noisy packets. PID table reset only happens on stream stop.

Test signals: cold/warm probe for every USB ID, firmware names, endpoint-specific streaming, PID filter count 15 behavior, NEC and NECX remote events, frontend tune/status commands, and firmware-only Miglia reconnect behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtt200u.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtt200u.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtt200u.h

Purpose: private protocol header for DTT200U/WT220U devices. It defines debug helpers, firmware command bytes, and the custom frontend attach prototype.

Important APIs/types: `GET_*` commands read speed, tune status, RC code, configuration, AGC, SNR, Viterbi/RS error counters, and uncorrected blocks. `SET_*` commands initialize, set RF frequency/bandwidth, program/reset PID filters, and toggle streaming. `dtt200u_fe_attach()` exports the custom frontend.

Control flow: `dtt200u.c` sends power/stream/PID/RC commands, while `dtt200u-fe.c` sends tune and signal-stat commands.

State and persistence: no state is stored here; constants describe the firmware command ABI.

Dependencies and integration: includes `dvb-usb.h`, uses module debug variable from `dtt200u.c`, and connects the two DTT200U source files.

Risks: protocol is reverse-engineered and compact; command values are not self-validating. Firmware frequency unit and status byte meanings must remain synchronized with the frontend implementation.

Test signals: compile both files, USB trace GET/SET commands, tune across all supported bandwidths, PID reset, streaming switch, and RC polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtt200u.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtv5100.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtv5100.c

Purpose: DVB USB driver for the AME DTV-5100 USB2.0 DVB-T receiver. It wraps vendor USB control messages as an I2C adapter, attaches a ZL10353 demod and QT1010 tuner, performs device-specific initialization, and registers a warm-only DVB USB device.

Important APIs/functions: `dtv5100_i2c_msg()` maps I2C-like transactions to vendor requests, `dtv5100_i2c_algo` exposes the adapter, `dtv5100_frontend_attach()` attaches ZL10353, `dtv5100_tuner_attach()` attaches QT1010, and `dtv5100_probe()` runs the init request table before `dvb_usb_device_init()`.

Control flow: probe sends each `dtv5100_init[]` vendor request to endpoint 0, then initializes the DVB USB device. I2C xfer accepts at most two messages and serializes with `i2c_mutex`. A one-byte write plus read becomes demod/tuner read; a two-byte write becomes demod/tuner write. Frontend attach disables the demod I2C gate callback because the board path does not work with it. Streaming uses bulk endpoint `0x82`.

State and persistence: `struct dtv5100_state` stores an 80-byte USB control buffer. Hardware state includes vendor initialization, demod/tuner register programming, and USB bulk stream setup.

Dependencies and integration: depends on `dtv5100.h`, ZL10353 frontend, QT1010 tuner, generic DVB USB core, USB control messages, and I2C core.

Risks: `dtv5100_i2c_msg()` copies from `rbuf` into the internal buffer before read transfers even when `rbuf` may be NULL for write-only paths with zero `rlen`, relying on zero length to be harmless. It returns the raw byte count from `usb_control_msg()`, which I2C xfer treats as success if non-negative. Only `wlen` 1 or 2 is supported.

Test signals: warm USB ID probe, vendor init request sequence, ZL10353 attach with I2C gate disabled, QT1010 attach, demod/tuner register reads/writes, endpoint `0x82` streaming, and USB timeout/error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtv5100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtv5100.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtv5100.h

Purpose: private header for the AME DTV-5100 driver. It defines vendor request codes, pseudo-I2C addresses, timeout, driver metadata, and the probe-time initialization table.

Important APIs/types: `DTV5100_DEMOD_ADDR`/`TUNER_ADDR` identify targets for `dtv5100_i2c_msg()`. Read/write request macros select demod or tuner vendor commands. `dtv5100_init[]` is a small static request/value/index sequence run before DVB USB initialization.

Control flow: `dtv5100.c` includes this header to build USB control transfers for initialization and I2C emulation.

State and persistence: no allocated state. The init table programs device firmware state during probe.

Dependencies and integration: includes `dvb-usb.h`; integrates with ZL10353 and QT1010 attach code in the C file.

Risks: `dtv5100_init[]` lives in the header as a static definition, so including the header from another C file would create another copy. Request constants are device-specific and only lightly documented.

Test signals: compile the driver, trace the two initialization control requests, and verify demod/tuner read/write request selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtv5100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-common.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-common.h

Purpose: internal header for the DVB USB library implementation files. It centralizes debug macros and prototypes for firmware, power, URB, I2C, DVB adapter/frontend, and remote-control helpers.

Important APIs/types: debug macros map `dvb_usb_debug` bits to info/xfer/pll/ts/error/rc/firmware/memory/USB-transfer channels. Prototypes include `dvb_usb_download_firmware()`, `dvb_usb_device_power_ctrl()`, `usb_urb_*()`, `dvb_usb_adapter_stream_*()`, `dvb_usb_i2c_*()`, `dvb_usb_adapter_dvb_*()`, `dvb_usb_adapter_frontend_*()`, and `dvb_usb_remote_*()`.

Control flow: library C files include this header to call each other without exposing all internals through the public `dvb-usb.h`.

State and persistence: declares module globals `dvb_usb_debug` and `dvb_usb_disable_rc_polling`; no state is allocated here.

Dependencies and integration: includes `dvb-usb.h` and ties together `dvb-usb-init.c`, `dvb-usb-dvb.c`, `dvb-usb-i2c.c`, `dvb-usb-remote.c`, `dvb-usb-urb.c`, and `dvb-usb-firmware.c`.

Risks: internal prototypes must match exported symbols. Debug bit assignments are ABI-like for module users setting `debug=`.

Test signals: full DVB USB library build, module parameter debug output for every bit, and link coverage across all internal helper files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-dvb.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-dvb.c

Purpose: DVB-core integration layer for the DVB USB library. It registers DVB adapters, demux devices, DVB net, media-controller devices, frontend instances, and feed callbacks that start/stop USB streaming.

Important APIs/functions: `dvb_usb_adapter_dvb_init()`/`exit()` set up and tear down the DVB adapter and demux. `dvb_usb_adapter_frontend_init()`/`exit()` attach, register, wrap, and detach frontends. `dvb_usb_ctrl_feed()` is the demux feed state machine. `dvb_usb_fe_wakeup()` and `dvb_usb_fe_sleep()` wrap frontend init/sleep with device power and active-FE selection.

Control flow: adapter init registers `dvb_adapter`, optionally creates a media device, reads MAC address, initializes `dvb_demux`, `dmxdev`, and DVB net. Feed start/stop adjusts `feedcount`, kills URBs and disables streaming when the last feed stops, programs PID filters for each feed, enables PID parser and streaming when the first feed starts, and submits URBs. Frontend init calls board `frontend_attach`, wraps frontend ops, registers each frontend, attaches tuners, creates a media graph, and registers the media device.

State and persistence: persistent adapter state includes `dvb_adap`, `demux`, `dmxdev`, `dvb_net`, `active_fe`, `feedcount`, per-FE stream/filter flags, and saved frontend sleep/init callbacks. Hardware state includes device power, streaming enable, PID parser/filter entries, and active frontend routing.

Dependencies and integration: depends on DVB core, demux/net/frontend APIs, optional media controller, and device callbacks supplied in `dvb_usb_adapter_properties`.

Risks: `feedcount` is updated before later errors, so failed streaming/PID parser calls can leave counts inconsistent. Stop-feed subtracts without explicit underflow protection. Frontend attach failures after `i > 0` can leave earlier FEs alive by design. Active-FE selection assumes frontend IDs match initialized array indexes.

Test signals: DVB adapter registration, `dvbv5-scan`/zap feed start-stop cycles, multi-FE devices with exclusive lock, PID filtering on/off, media-controller graph creation, MAC address reading, and disconnect while feeds are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-dvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-firmware.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-firmware.c

Purpose: firmware download support for Cypress AN2135/AN2235/FX2 based DVB USB devices and generic Intel HEX line parsing for firmware images.

Important APIs/functions: `usb_cypress_load_firmware()` stops the Cypress CPU, writes firmware records, and restarts it. `dvb_usb_download_firmware()` requests the firmware file and dispatches by controller type or device-specific callback. `dvb_usb_get_hexline()` parses one firmware record into `struct hexline`. `usb_cypress_writemem()` wraps vendor request `0xa0`.

Control flow: cold-device probe calls `dvb_usb_download_firmware()`. The firmware loader requests `props->firmware`, selects Cypress or `download_firmware`, parses records from `fw->data`, writes each record to the target address, and restarts the controller CPU after EOF. Device-specific controller types require a callback.

State and persistence: firmware bytes are transient kernel firmware objects. Persistent effects are in the USB controller RAM and CPU run state until device reset/replug. No local persistent state is retained after release.

Dependencies and integration: depends on Linux firmware loader, USB control messages, Cypress controller IDs in DVB USB properties, and the public `struct hexline` contract from DVB USB headers.

Risks: `cypress[type]` indexes by controller ID, so enum values must remain dense and valid. HEX parsing is minimal and does not validate checksums. Extended linear address handling leaves record length/data offset behavior commented, so nonstandard records may parse incorrectly. Firmware failure returns before warm-state initialization.

Test signals: missing firmware error path, valid AN2135/AN2235/FX2 firmware upload, USB traces for CPUCS stop/start addresses `0x7f92` and `0xe600`, HEX parser malformed-record rejection, and device reconnect or `no_reconnect` warm initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-i2c.c

Purpose: I2C adapter registration helpers for DVB USB devices whose bridge exposes an I2C bus to demodulators, tuners, EEPROMs, or board peripherals.

Important APIs/functions: `dvb_usb_i2c_init()` registers an `i2c_adapter` using `d->props.i2c_algo`; `dvb_usb_i2c_exit()` unregisters it when initialized.

Control flow: device init calls `dvb_usb_i2c_init()` after power-on. If the device properties lack `DVB_USB_IS_AN_I2C_ADAPTER`, the function is a no-op. Otherwise it validates the algorithm, names the adapter after the device description, sets parent device and private data, calls `i2c_add_adapter()`, and sets `DVB_USB_STATE_I2C`. Exit deletes the adapter if the state bit is present.

State and persistence: the `i2c_adapter` embedded in `struct dvb_usb_device` persists for the device lifetime. The state bit gates cleanup. Hardware I2C state is implemented by each device-specific algorithm.

Dependencies and integration: depends on Linux I2C core and property callbacks from board drivers.

Risks: a device declaring I2C capability without an algorithm fails init. Adapter naming depends on a valid matched description. Cleanup relies on the state bit being set only after successful registration.

Test signals: probe devices with and without I2C capability, demod/tuner attach through registered adapter, `i2cdetect`-style transfer behavior where safe, and disconnect cleanup without leaked adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-init.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-init.c

Purpose: core lifecycle for legacy DVB USB devices. It handles module parameters, matching cold/warm USB IDs, firmware download, device allocation, power sequencing, private allocation, I2C/adapter/frontend/remote initialization, and disconnect teardown.

Important APIs/functions: exported `dvb_usb_device_init()` and `dvb_usb_device_exit()` are called by all legacy device drivers. `dvb_usb_device_power_ctrl()` reference-counts power transitions. Internal `dvb_usb_init()` and `dvb_usb_exit()` perform full setup/teardown. `dvb_usb_adapter_init()` allocates adapter/FE private data, selects PID filtering mode, initializes streams, DVB adapter, and frontends.

Control flow: probe allocates `struct dvb_usb_device`, copies properties, finds a device description in cold/warm ID lists, optionally downloads firmware, stores USB/interface state, and calls `dvb_usb_init()`. Init sets mutexes, allocates device private state, powers on, registers I2C, initializes adapters/frontends/URBs/DVB, starts remote handling, then powers off. Adapter setup forces hardware PID filtering for USB full-speed devices or module option, allocates private buffers, initializes URB streams, registers DVB core objects, and attaches frontends. Disconnect cancels remote work, tears down frontends/DVB/streams/I2C, calls private destroy, frees private memory and device.

State and persistence: persistent device state includes copied properties, matched description, USB device, owner, mutexes, powered reference count, state bits, private memory, initialized adapter count, and per-adapter private/FE private objects. Module parameters include debug, RC polling disable, and forced PID filtering.

Dependencies and integration: central dependency for all drivers in this directory. It integrates with firmware loader, I2C, DVB-core setup, URB streaming, remote-control setup, USB interface data, and property callbacks.

Risks: `dvb_usb_adapter_init()` has failure paths that free `adap->priv` but not all per-FE private allocations in early failures. Power reference counting can underflow if callbacks are imbalanced. Cold firmware devices usually return after download unless `no_reconnect` permits same-probe warm init. Frontend attach returning no FE is treated as nonfatal in some paths.

Test signals: cold/warm probe, firmware failure and success, private init/destroy callbacks, full-speed USB rejection without PID filter, forced PID filter module parameter, multi-adapter init/exit ordering, remote disabled parameter, and repeated bind/unbind under fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-remote.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-remote.c

Purpose: remote-control support for the DVB USB library. It supports both old legacy input-device polling and newer rc-core devices, plus a helper for decoding NEC-like five-byte firmware key buffers.

Important APIs/functions: `dvb_usb_remote_init()` and `dvb_usb_remote_exit()` are exported lifecycle helpers. Legacy paths include keymap get/set functions, `legacy_dvb_usb_read_remote_control()`, and `legacy_dvb_usb_remote_init()`. Rc-core paths include `dvb_usb_read_remote_control()` and `rc_core_dvb_usb_remote_init()`. `dvb_usb_nec_rc_key_to_event()` decodes legacy NEC buffers.

Control flow: init returns if RC polling is disabled or no RC properties are present. Legacy mode allocates `input_dev`, populates key bits, registers it, initializes delayed work, and periodically calls driver `rc_query()` to emit press/repeat/release events. Rc-core mode allocates `rc_dev`, sets map/protocol fields, registers it, and either lets bulk mode handle events elsewhere or schedules delayed polling. Exit cancels delayed work and unregisters/free devices based on mode.

State and persistence: device state tracks `input_dev` or `rc_dev`, `rc_phys`, last event/state, work item, and `DVB_USB_STATE_REMOTE`. Keymaps are static property tables, but legacy `setkeycode` can mutate keycodes in place at runtime.

Dependencies and integration: depends on Linux input, rc-core, USB input ID helpers, and each board driver's RC query callback/protocol fields.

Risks: `legacy_dvb_usb_setkeycode()` writes `keymap->keycode` instead of `keymap[index].keycode`, so remapping can update the first entry rather than the selected one. Poll callbacks contain TODOs about locking and can skip rescheduling if polling is disabled while running. Rc-core bulk mode relies on device-specific URB completion outside this file.

Test signals: legacy and rc-core device creation, keymap get/set, delayed polling interval clamping, NEC checksum/repeat decoding, RC5/NEC maps from board properties, bulk-mode devices, disable_rc_polling module parameter, and disconnect while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-remote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-urb.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-urb.c

Purpose: generic USB transfer and transport-stream URB glue for DVB USB devices. It provides bulk command read/write helpers and initializes per-frontend data streams that feed DVB demux software filters.

Important APIs/functions: exported `dvb_usb_generic_rw()` and `dvb_usb_generic_write()` implement control transfers over a configured bulk endpoint. `dvb_usb_adapter_stream_init()` and `dvb_usb_adapter_stream_exit()` initialize and release `usb_data_stream` instances. Completion callbacks select `dvb_dmx_swfilter()`, `_204()`, or `_raw()`.

Control flow: command callers pass a write buffer and optional read buffer. The helper validates endpoint/property state, locks `usb_mutex`, sends a bulk message, optionally sleeps, receives from either response endpoint or the same endpoint, dumps debug data, and unlocks. Stream init loops over frontend properties, sets USB device, completion callback based on TS flags, user private pointer, and calls `usb_urb_init()`. Data completion filters packets only when `feedcount > 0` and DVB adapter state is active.

State and persistence: per-FE `usb_data_stream` holds URBs, endpoint properties, callback, and `user_priv`. Device `usb_mutex` serializes generic command traffic. Hardware state is ongoing bulk URB submission owned by lower `usb_urb_*()` helpers.

Dependencies and integration: depends on DVB USB common state, USB bulk APIs, lower USB data-stream helpers, and DVB demux software filters.

Risks: short writes return `-1` rather than a specific errno. Read-side short transfers are not explicitly converted to an error. All generic command users share one mutex, so long firmware delays can serialize unrelated operations. Completion callbacks depend on `feedcount` being consistent with URB submit/kill.

Test signals: generic command timeout and short-transfer paths, separate response endpoint devices, TS 188-byte/204-byte/raw payload filtering, stream init/exit for multi-frontend adapters, feed start/stop URB submission, and disconnect while URBs are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-urb.c -->
