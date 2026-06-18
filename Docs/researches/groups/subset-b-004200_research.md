<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/af9035.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/af9035.c

Purpose: This source implements the dvb-usb-v2 bridge driver for Afatech AF9035, ITE IT9135, and ITE IT930x based USB receivers. It binds many USB IDs to either `af9035_props` or `it930x_props`, detects cold versus warm firmware state, downloads the correct firmware image, reads EEPROM or chip defaults, creates one or two DVB adapters, and wires AF9033/Si2168 demodulators plus multiple tuner families into the common DVB USB framework.

Important APIs and functions: `af9035_ctrl_msg()` is the central bulk-control transport. It builds a 4-byte request header, appends command payload and checksum, serializes access with `d->usb_mutex`, calls `dvb_usbv2_generic_rw_locked()`, validates reply checksum/status, and copies reply payloads. `af9035_wr_regs()`, `af9035_rd_regs()`, and `af9035_wr_reg_mask()` are register helpers layered on that transport. `af9035_i2c_master_xfer()` implements the exposed Linux I2C adapter and special-cases AF9033 demod register access as firmware memory reads/writes. `af9035_identify_state()`, `af9035_download_firmware_old()`, `af9035_download_firmware_new()`, and `af9035_download_firmware()` implement chip identification, EEPROM capture, dual-demod reset/setup, firmware download formats, and post-boot version verification. Frontend and tuner attach paths include `af9035_frontend_attach()`, `it930x_frontend_attach()`, `af9035_tuner_attach()`, `it930x_tuner_attach()`, detach functions, endpoint init functions, RC query/config, PID filter wrappers, and the custom `af9035_probe()` that rejects the TerraTec AF9015 lookalike.

Control flow: USB probe enters `af9035_probe()` and then `dvb_usbv2_probe()`. The framework calls `af9035_identify_state()` to read chip type/version and EEPROM, decides firmware name, and reports `COLD` when firmware query returns zeros. On cold devices the download path optionally powers and addresses the slave demod, streams old block or new scatter firmware commands, boots firmware, and verifies nonzero firmware version bytes. Warm initialization calls `af9035_read_config()` before I2C adapter creation to establish demod addresses, tuner IDs, clock values, RC mode, dual-mode support, and device quirks such as the AVerMedia MXL5007T no-read workaround. Adapter creation then attaches demods through I2C client devices or direct module probe, attaches tuners by switch on AF9033 tuner ID or IT930x address table, initializes endpoint/frame registers, and enables RC polling when EEPROM/config allows. Streaming is delegated to the v2 core, while PID filter callbacks call the demod driver's saved AF9033 ops.

State and persistence: `struct state` in `af9035.h` is allocated per USB device. It stores the transfer buffer, sequence number, chip identity, 256-byte EEPROM mirror, `no_eeprom`, RC mode/type, `dual_mode`, I2C no-read quirk, two AF9033 I2C addresses/configs, AF9033 ops, up to four I2C client handles, an IT930x demod-side I2C adapter, and IT913x platform tuner devices. No persistent writes to EEPROM are made; EEPROM is only memory-mapped read-only data. Runtime persistence is in kernel objects: registered I2C clients/platform devices, DVB frontends/adapters, and module references, all released by tuner/frontend detach.

Dependencies and integration points: The file depends on `dvb_usb.h`/`dvb_usb_urb.c` for bulk control and the v2 lifecycle, AF9033 demod APIs and ops, tuner drivers (`tua9001`, `fc0011`, `fc0012`, `mxl5007t`, `tda18218`, `fc2580`, `it913x`, `si2157`), `si2168`, Linux I2C client APIs, RC core, and USB ID definitions. Device properties integrate with `dvb_usbv2_probe()`, suspend/resume/disconnect, hardware PID filter callbacks, and bulk stream endpoints 0x84/0x85.

Risks: The driver has several documented hacks: I2C bus selection via high address bit, firmware-covered demod I2C access, IT913x integrated tuner represented as an I2C/platform device, hard-coded register sequences, and device-specific quirks. Error unwind after partial tuner attach depends on detach paths matching `state->i2c_client` ordering. `af9035_i2c_master_xfer()` only supports simple 1 or 2 message patterns and caps lengths at 40 bytes. Firmware parsing assumes known binary layouts and continues after bad old-firmware trailing bytes. Dual-mode may be disabled after EEPROM says it exists if the second tuner is unsupported.

Test signals: Useful validation includes probe logs showing chip type/version, EEPROM dump, firmware version, single/dual adapter count, attached demod/tuner modules, and no checksum mismatch from `af9035_ctrl_msg()`. Functional signals are successful tuning on all supported tuner families, hardware PID filter enable/filter programming, RC NEC/RC6 key events where configured, suspend/resume and reset_resume preserving streams, and TerraTec 0x0099 AF9015 lookalike rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/af9035.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/af9035.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/af9035.h

Purpose: This private header defines the AF9035/IT9135/IT930x driver's local data structures, firmware names, EEPROM layout, clock lookup tables, and USB command numbers. It is the contract between `af9035.c` and the many demod/tuner helpers the driver instantiates.

Important APIs/types: `struct reg_val` and `struct reg_val_mask` describe register programming tables, with masks used by endpoint and GPIO setup code. `struct usb_req` is the transport command descriptor consumed by `af9035_ctrl_msg()`, carrying command, mailbox, write length/buffer, and read length/buffer. `struct state` is the per-device private state allocated by `dvb_usbv2_probe()` according to `size_of_priv`; it contains `BUF_LEN` command storage, firmware sequence counter, chip identity fields, EEPROM mirror, RC mode/type, dual and no-read flags, demod addresses/configs, AF9033 ops, I2C client slots, demod-side adapter pointer, and IT913x platform tuner devices. `struct address_table` maps IT930x variants to frontend address, tuner address, and tuner IF port.

Control flow support: `clock_lut_af9035[]` and `clock_lut_it9135[]` translate the demod clock selector read by `af9035_read_config()` into Hertz for AF9033 configuration. `it930x_addresses_table[]` is selected by device-specific logic in `af9035_read_config()` and later used by `it930x_frontend_attach()`/`it930x_tuner_attach()`. EEPROM offset macros identify RC settings, TS mode, second demod address, IF values, and tuner IDs that drive single/dual adapter creation and tuner selection. USB command macros define the command bytes used for memory access, I2C access, IR polling, firmware download, firmware query/boot, scatter writes, and IT930x generic I2C transfers.

State and persistence behavior: The header models runtime state only. The EEPROM constants describe memory-mapped read-only EEPROM access; the comments explicitly state writes to those mapped addresses do not corrupt EEPROM. Firmware names are exposed to `MODULE_FIRMWARE()` and the v2 core request-firmware path, but no persistent storage is updated by the header itself.

Dependencies and integration points: It includes Linux platform device support, the v2 DVB USB framework, AF9033 demod definitions, tuner headers, IT913x platform data, and Silicon Labs Si2168/Si2157 definitions. The header's structures are not exported as a public kernel API; they are specific to this driver source.

Risks: Many numeric constants encode reverse-engineered hardware behavior. A wrong EEPROM offset, clock table index, or USB command value can misconfigure firmware, RC polling, dual tuner routing, or I2C transactions. `AF9035_I2C_CLIENT_MAX` is fixed at four and detach logic relies on client insertion order. The header documents TS mode values only from observed devices, so unobserved modes intentionally fall back or are rejected by `af9035.c`.

Test signals: Compile coverage should catch type/API drift against tuner and demod headers. Runtime validation is indirect: correct firmware name selection, clock values in AF9033 configs, RC mode interpretation, dual adapter exposure, and stable attach/detach of all clients using the fixed state arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/af9035.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/anysee.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/anysee.c

Purpose: This file implements the Anysee E30/E7 USB receiver driver. It supports multiple hardware revisions spanning DVB-T, DVB-C, DVB-S/S2, DVB-T2/C, combo devices, shared tuners, remote control, LED/IR control, and CI/CAM access for models with a CI interface. The driver is built on dvb-usb-v2 but uses a reverse-engineered 64-byte bulk command protocol with an unusual two-reply transaction flow.

Important APIs and functions: `anysee_ctrl_msg()` is the central USB transport. It fills the per-device 64-byte buffer, stores a sequence byte at offset 60, sends one 64-byte command through `dvb_usbv2_generic_rw_locked()`, then reads a second reply from the receive bulk endpoint, retrying three times. Register helpers (`anysee_read_reg()`, `anysee_write_reg()`, `anysee_wr_reg_mask()`, `anysee_rd_reg_mask()`) control Cypress/board GPIO ports. `anysee_master_xfer()` implements the I2C adapter with write, write-read, and size-limited command forms. `anysee_read_config()` reads hardware/firmware ID twice due to a firmware bug. `anysee_frontend_ctrl()` switches combo frontend routing at open time. `anysee_frontend_attach()` and `anysee_tuner_attach()` contain the hardware-ID switch that selects MT352, ZL10353, TDA10023, CX24116, STV0900, CXD2820R, TDA18212, PLL, STV6110, and ISL6423 pieces. RC and CI support are provided by `anysee_rc_query()`, `anysee_get_rc_config()`, `anysee_ci_*()`, `anysee_ci_init()`, and release helpers.

Control flow: Probe uses `anysee_props` directly with `dvb_usbv2_probe()`. The v2 core reads config before adapter setup; Anysee queries hardware info twice and stores `state->hw`. Adapter initialization attaches the appropriate frontend(s) for that board revision, sometimes probing TDA18212 by enabling the tuner GPIO and reading I2C ID 0xc7. Combo boards may expose two frontends in one DVB adapter, with `frontend_ctrl` switching GPIO routing between DVB-C and DVB-T paths. Tuner attach either uses legacy PLLs, registers `tda18212` as an I2C client, copies shared tuner ops to a second frontend, or attaches satellite tuner/LNB controllers. `anysee_init()` selects bulk alternate setting 0, lights the LED, enables IR, and initializes CI if `state->has_ci` was set during frontend attach. Streaming start/stop uses `CMD_STREAMING_CTRL` from the v2 core callback.

State and persistence: `struct anysee_state` stores the USB buffer, sequence counter, hardware ID, at most one managed I2C client, frontend/CI feature flags, a `dvb_ca_en50221` object, and `ci_cam_ready` jiffies. No nonvolatile settings are modified. Hardware state is kept in GPIO register bits for demod/tuner selection, TS routing, LED, IR, and CI reset. CI ready is time-based after slot reset and is not persisted across disconnect.

Dependencies and integration points: The driver integrates with `dvb_usb.h`, `dvb-pll`, demod drivers (`tda1002x`, `mt352`, `zl10353`, `cx24116`, `stv0900`, `cxd2820r`), tuner/LNB drivers (`tda18212`, `stv6110`, `isl6423`), RC core, and EN50221 CI. It binds Cypress and AMT Anysee USB IDs with bulk endpoints 0x01/0x81 and MPEG stream endpoint 0x82.

Risks: Most board behavior is reverse engineered and encoded as hardware-ID-specific GPIO sequences. `anysee_ctrl_msg()` depends on a second receive packet and a weak status check at byte 63, so missed or stale replies can confuse later commands. I2C transfers are limited to 48-byte writes and 60-byte reads, with only simple register read formats. CI support is for hardware CAM interfaces, while the file comments note smart-card reader support is not implemented. Shared tuner ops copied between frontends require care when detach or tuner API behavior changes.

Test signals: Strong signals include correct firmware/hardware ID logs, successful attach for every known hardware ID, visible DVB-C/T/S/S2/T2 services on the matching model, LED/IR enabling, RC NEC events from map `RC_MAP_ANYSEE`, CI slot presence/ready polling on E7/CI models, correct frontend switching on combo boards, and clean detach releasing the single I2C client and CI object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/anysee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/anysee.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/anysee.h

Purpose: This header captures the Anysee driver's private protocol and board-state definitions. It defines command opcodes, the private state shape, known hardware IDs, GPIO register addresses, and a reverse-engineered USB API note block that explains the 64-byte transaction protocol used by `anysee.c`.

Important APIs/types: `enum cmd` defines command values for I2C read/write, register read/write, stream control, LED/IR control, IR code polling, hardware-info query, smartcard command placeholder, and CI command. `struct anysee_state` stores the 64-byte command/reply buffer, packet sequence, PCB hardware ID, one managed I2C client slot, frontend and feature flags, the `dvb_ca_en50221` object, and the jiffies deadline used to report CAM ready. `ANYSEE_HW_*` macros map numeric PCB IDs to E30/E7 model families. `REG_IO*` and `REG_OE*` macros identify Cypress port and output-enable registers used for demod/tuner power and signal routing.

Control flow support: The header's command values are consumed by `anysee_ctrl_msg()` and its helper APIs. Hardware IDs drive the large frontend/tuner switch in `anysee_frontend_attach()` and `anysee_tuner_attach()`. Register macros drive `frontend_ctrl`, CI reset/shutdown/TS enable, tuner-gate handling, and initial LED/IR configuration.

State and persistence behavior: The definitions describe runtime state and volatile USB-controller registers. The reverse-engineered protocol comments identify sequence byte offset 60 and "previous reply/current reply" behavior, which explains why the implementation reads two replies for every command. The smart-card command is documented but not implemented as persistent support.

Dependencies and integration points: It includes `dvb_usb.h` and EN50221 CI definitions. The state structure is allocated by the v2 core through `anysee_props.size_of_priv`, and the CI object is registered against the DVB adapter when supported hardware is detected.

Risks: The header contains many magic numbers from reverse engineering. The protocol documentation appears to have a few offset/name inconsistencies, so implementation behavior should be treated as authoritative. `ANYSEE_I2C_CLIENT_MAX` is one, which is sufficient for the current TDA18212 client use but constrains future multi-client additions. Hardware IDs outside the listed set will fail attach and ask users to report them.

Test signals: Compile tests should validate command enum names against `anysee.c`. Runtime signs are stable sequence handling, correct model ID decoding, expected GPIO route switching, and CI/RC behaviors matching the documented packet layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/anysee.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/au6610.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/au6610.c

Purpose: This compact driver supports Alcor Micro AU6610 based DVB-T USB2.0 devices, specifically the Sigmatek DVB-110 USB ID. It exposes an I2C adapter over vendor control reads, attaches a ZL10353 demodulator and QT1010 tuner, and configures an isochronous transport stream endpoint through dvb-usb-v2.

Important APIs and functions: `au6610_usb_msg()` is the low-level control helper. It builds the USB control `index` from one or two write bytes, sends a vendor IN request, and for read operations extracts the returned value from byte 4 of a fixed 6-byte temporary buffer. `au6610_i2c_msg()` chooses AU6610 I2C read or write request numbers. `au6610_i2c_xfer()` supports at most two I2C messages, including write-read pairs, under `d->i2c_mutex`. `au6610_zl10353_frontend_attach()` attaches a no-tuner, parallel-TS ZL10353 at address 0x0f, `au6610_qt1010_tuner_attach()` attaches QT1010 at 0x62, and `au6610_init()` switches interface 0 to alternate setting 5.

Control flow: The USB driver's probe is the generic `dvb_usbv2_probe()`. Since there is no firmware or identify callback, the v2 core proceeds directly to initialization. It registers the I2C adapter, creates one DVB adapter, attaches the demod and tuner, then calls `au6610_init()` to select the streaming alternate setting. Streaming is an isochronous endpoint configuration at endpoint 0x82 with 5 URBs, 40 frames per URB, 942-byte frames, and interval 1.

State and persistence: This file does not define a private state allocation. State lives in the common `dvb_usb_device`, the I2C adapter, and frontend/tuner modules. There is no persistent firmware or EEPROM path. USB interface alternate setting is volatile and restored by init/reset-resume through the v2 callbacks.

Dependencies and integration points: It depends on `au6610.h`, `zl10353.h`, `qt1010.h`, the v2 framework, USB vendor control messaging, and Linux I2C. The module uses `DVB_DEFINE_MOD_OPT_ADAPTER_NR(adapter_nr)` and `DVB_USB_DEVICE()` for adapter numbering and USB ID binding.

Risks: `au6610_usb_msg()` only accepts one- or two-byte write prefixes and allocates for a fixed 6-byte control reply. The I2C xfer return value is `i`, which after consuming a write-read pair becomes 1 rather than `num` in the successful two-message case, a subtle compatibility risk for callers expecting exact message count. The write path still uses a vendor IN control request and relies on device-specific semantics. No RC, power, firmware, or MAC handling is present.

Test signals: Probe should register one adapter and attach ZL10353/QT1010 without firmware. Tuning should produce isochronous TS data from endpoint 0x82 after alternate setting 5 is selected. I2C regressions show up as demod/tuner attach failures or `wlen` abort logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/au6610.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/au6610.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/au6610.h

Purpose: This private header supplies AU6610 command constants and the USB timeout used by `au6610.c`. It keeps the source driver independent from public framework headers beyond `dvb_usb.h`.

Important APIs/types: It defines request opcodes `AU6610_REQ_I2C_WRITE`, `AU6610_REQ_I2C_READ`, `AU6610_REQ_USB_WRITE`, and `AU6610_REQ_USB_READ`, plus `AU6610_USB_TIMEOUT` set to 1000 ms. There are no structs or exported helper functions.

Control flow support: `au6610_i2c_msg()` selects the I2C read/write constants from this header, and `au6610_usb_msg()` uses the timeout for every `usb_control_msg()` call. The USB read/write request constants are available but only the I2C read/write values are materially used by the current source.

State and persistence behavior: The header defines no runtime state and no persistent configuration. Its constants only affect volatile control transfers.

Dependencies and integration points: It includes `dvb_usb.h`, allowing `au6610.c` to use the common framework types and debug helper macro.

Risks: Because the protocol is represented only as numeric constants, any board variant needing different request codes would require source changes. The timeout applies uniformly to all requests, which is simple but may be too strict or too lenient for unknown variants.

Test signals: Compile coverage plus successful AU6610 I2C transactions validate the constants. Failed control requests with request values 0x13 or 0x14 would point back to this protocol definition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/au6610.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/az6007.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/az6007.c

Purpose: This driver supports AzureWave 6007, TerraTec H7, and Technisat CableStar HD CI style DVB-C/T USB2 devices. It uses Cypress FX2 firmware loading, vendor control requests for power/I2C/CI/IR/streaming, a DRX-K demodulator with MT2063 tuner, optional CI, RC polling for non-CableStar variants, and v2 DVB USB lifecycle integration.

Important APIs and functions: `__az6007_read()` and `__az6007_write()` perform raw vendor control transfers with optional hex debug, while `az6007_read()`/`az6007_write()` serialize them through `state->mutex`. `az6007_i2c_xfer()` maps Linux I2C messages into AZ6007 I2C read/write control requests and handles combined one-byte-register write-read operations by copying returned data from offset 5 of `state->data`. `az6007_power_ctrl()` performs the long first-warmup power and SCON reset sequence, then later only sends lightweight power/TS commands. `az6007_identify_state()` detects warm state by reading a MAC address and kicks the FX2 into reset commands if cold. `az6007_download_firmware()` delegates to `cypress_load_firmware()`. Frontend paths attach DRX-K with different microcode configs for TerraTec/AzureWave versus CableStar, wrap the demod I2C gate, initialize EN50221 CI, and attach MT2063. CI callbacks implement attribute/control memory, reset, TS enable, and status polling over request codes 0xc1 through 0xc8. RC query decodes NEC/NECX/NEC32 from `AZ6007_READ_IR`.

Control flow: On probe the v2 core calls `az6007_identify_state()`. Cold devices load `dvb-usb-terratec-h7-az6007.fw` via Cypress FX2 support. During init the core powers the device, which initializes the mutex and executes the warmup sequence once. The I2C adapter is then registered, MAC address is read, DRX-K is attached with board-specific config, CI is initialized, MT2063 is attached through the demod gate, and streaming uses endpoint 0x02 with 10 bulk buffers of 4096 bytes. Custom suspend releases CI before v2 suspend; resume reinitializes CI before v2 resume; disconnect also releases CI before generic teardown.

State and persistence: `struct az6007_device_state` stores the main USB mutex, CI mutex, CI object, warm flag, saved demod gate callback, and a 4096-byte transfer buffer. Persistent state is external firmware in the request-firmware path and DRX-K microcode names. Runtime hardware state includes power rails, FX2 serial control, TS-through, CI CAM reset/enable, and I2C bus contents. MAC address is read but not written.

Dependencies and integration points: The file depends on `drxk`, `mt2063`, EN50221 CI, `dvb_usb.h`, `cypress_firmware.h`, RC core, Linux USB control APIs, and USB ID macros. It exports no public symbols and registers one `usb_driver` with custom suspend/resume/disconnect hooks.

Risks: CI operations allocate small buffers per access and rely on request-code semantics from vendor code. `az6007_i2c_xfer()` uses offsets in a shared 4096-byte buffer and assumes returned control length layout. `az6007_power_ctrl()` ignores return values on later warm power-on writes and only initializes `state->mutex` in the first cold-to-warm power path. The raw I2C read branch indexes `msgs[i].buf[0]` even for pure read messages, which is fragile if callers do not seed a register value. Reset-resume is marked unimplemented. Remote control is noted as not working with one box and is disabled for CableStar properties.

Test signals: Firmware loading should transition cold devices to warm and allow MAC reads. Logs should show DRX-K/MT2063 attach and CI initialization. Streaming should start/stop via request 0xbc and deliver TS from endpoint 0x02. CI tests should cover CAM insert, reset delay/readiness, attribute/control memory access, suspend/resume reinitialization, and clean release on disconnect. RC tests should verify NEC decoding only for devices with maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/az6007.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/ce6230.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/ce6230.c

Purpose: This source implements the Intel CE6230/CE9500 DVB-T USB bridge driver and AVerMedia A310 binding. It translates USB vendor control requests into demod and tuner I2C operations, attaches ZL10353 and MXL5003S/MXL5005S components, and exposes a single bulk-streaming DVB adapter through dvb-usb-v2.

Important APIs and functions: `ce6230_ctrl_msg()` consumes `struct usb_req`, chooses vendor IN or OUT request type based on command, allocates a buffer, copies write data or returns read data, sleeps 1 ms to avoid I2C errors, and executes `usb_control_msg()` with `CE6230_USB_TIMEOUT`. `ce6230_i2c_master_xfer()` supports up to two Linux I2C messages. It maps accesses to the ZL10353 demod address to `DEMOD_READ`/`DEMOD_WRITE`, maps other writes to `I2C_WRITE`, and rejects non-demod reads. `ce6230_zl10353_frontend_attach()` and `ce6230_mxl5003s_tuner_attach()` attach the demod and tuner. `ce6230_power_ctrl()` toggles interface 1 alternate setting 0/1 for idle versus streaming-ready power state.

Control flow: The USB driver binds on interface number 1. v2 probe initializes power via `ce6230_power_ctrl()`, registers the I2C adapter, creates one DVB adapter, attaches the ZL10353 frontend and MXL tuner, then leaves streaming to the common feed path. The adapter uses endpoint 0x82, six bulk buffers of 16*512 bytes. The demux start/stop flow is entirely common v2 behavior because no custom streaming callback is registered.

State and persistence: There is no private state. The static `ce6230_zl10353_config` and `ce6230_mxl5003s_config` hold fixed demod/tuner parameters. Runtime state is in USB alternate setting, I2C transactions, and component driver state. There is no firmware, EEPROM, RC, MAC, or persistent storage path.

Dependencies and integration points: It depends on `ce6230.h`, `zl10353`, `mxl5005s`, Linux USB control messaging, I2C, and the v2 framework. The static configs specify ADC/IF/PLL values and tuner mode for the attached modules.

Risks: Non-demod I2C reads are unimplemented, so any future tuner requiring readback through this bridge will fail. The demod address comparison uses the config's 8-bit-looking value directly and then shifts for USB `value`, so changing address conventions needs careful validation. `ce6230_ctrl_msg()` treats any nonnegative control length as success without checking exact byte count. Power control via alternate setting may be too coarse for devices with additional board power rails.

Test signals: Probe should happen on interface 1 only, with ZL10353 and MXL tuner attachment. Successful tuning over endpoint 0x82 validates I2C write/read paths and alternate-setting power control. Error testing should cover rejected unsupported I2C reads, interface switch failures, and suspend/resume through the generic v2 callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/ce6230.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/ce6230.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/ce6230.h

Purpose: This header defines the CE6230 driver's vendor request descriptor and command values. It is the local protocol map for `ce6230.c`.

Important APIs/types: `struct usb_req` carries command byte, USB `value`, USB `index`, transfer length, and data pointer for `ce6230_ctrl_msg()`. `enum ce6230_cmd` names known commands for config, unknown write, I2C read/write, demod read/write, and register read/write. `CE6230_USB_TIMEOUT` sets the 1000 ms timeout used for all control transfers.

Control flow support: The command enum drives the IN/OUT switch in `ce6230_ctrl_msg()` and the I2C mapping in `ce6230_i2c_master_xfer()`. `DEMOD_READ`/`DEMOD_WRITE` are used for ZL10353 register access; `I2C_WRITE` is used for non-demod writes. Other commands are defined but not currently exercised by the source.

State and persistence behavior: The header defines no state beyond per-call `struct usb_req`. It does not encode firmware or persistent storage behavior.

Dependencies and integration points: It includes `dvb_usb.h`, `zl10353.h`, and `mxl5005s.h`, matching the only components the implementation attaches.

Risks: Several command names are marked unclear in comments, so unused commands should not be assumed correct for new behavior without hardware traces. The protocol does not describe expected return lengths, leaving `ce6230_ctrl_msg()` unable to validate short transfers.

Test signals: Compile coverage plus functional demod/tuner I2C access validate the command mapping. Control failures with command bytes 0xd9/0xca/0xdb/0xcc are direct signals for this header's protocol values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/ce6230.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb.h

Purpose: This is the central public header for the dvb-usb-v2 framework used by all drivers in this folder. It defines the property structures that device drivers fill, the runtime device/adapter/stream objects allocated by the core, helper macros for navigating between frontends/adapters/devices/private state, stream configuration macros, USB device ID binding macro, and exported lifecycle/control APIs.

Important APIs and types: `DVB_USB_DEVICE()` packages USB ID entries with a `struct dvb_usb_driver_info` containing device name, RC map, and `struct dvb_usb_device_properties`. `struct dvb_usb_rc` describes RC map/protocol/query behavior. `struct usb_data_stream_properties` and `DVB_USB_STREAM_BULK()`/`DVB_USB_STREAM_ISOC()` describe MPEG TS endpoint type and URB sizing. `struct dvb_usb_adapter_properties` declares PID filter callbacks and stream layout. `struct dvb_usb_device_properties` is the main driver contract: firmware identification/download, I2C algo, adapter count, power/config/MAC/frontend/tuner/streaming/init/exit/RC callbacks, private-state size, bulk control endpoints, and adapter properties. `struct usb_data_stream`, `struct dvb_usb_adapter`, and `struct dvb_usb_device` are the core runtime objects. Exported APIs include `dvb_usbv2_probe()`, disconnect, suspend/resume/reset_resume, and generic bulk control read/write helpers.

Control flow: A device driver creates one or more `usb_device_id` rows with `DVB_USB_DEVICE()` and a property struct. Its `usb_driver.probe` normally calls `dvb_usbv2_probe()`, which consumes this metadata to allocate `dvb_usb_device`, detect/download firmware, create I2C/DVB/RC objects, and initialize streaming. The macros such as `fe_to_d()` and `adap_to_priv()` are used throughout callbacks so component drivers can reach the enclosing USB device and private state.

State and persistence behavior: The header defines runtime state fields but does not implement behavior. Persistent inputs are represented as firmware names and USB ID metadata. Mutable runtime state includes power reference count, I2C and USB mutexes, DVB adapter/frontend/demux/net objects, RC work, feed counts, active frontend index, PID filtering state, stream URBs, and driver private data.

Dependencies and integration points: It includes USB input, firmware, RC core, media-device, DVB frontend/demux/net/dmxdev, and DVB USB ID headers. It is consumed by bridge drivers, `dvb_usb_core.c`, `dvb_usb_urb.c`, and URB helper code. The API surface is kernel-internal but exported to modules in this media subsystem.

Risks: Driver properties are highly callback-driven; missing or inconsistent callbacks can create partial init/unwind failures. `MAX_NO_OF_ADAPTER_PER_DEVICE` is two and `MAX_NO_OF_FE_PER_ADAP` is three, which constrain supported hardware shapes. The pointer navigation macros rely on embedded-array layout and correct `id` fields. Stream buffer settings are trusted from drivers and can affect memory usage or broken TS delivery.

Test signals: Compile coverage for every driver using the property structs catches signature drift. Runtime validation is broad: probe/disconnect/suspend/resume should work for each driver, DVB adapter/frontends should register with expected numbering, RC polling should respect module options, and generic bulk control helpers should serialize correctly under driver mutex use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb_common.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb_common.h

Purpose: This small internal header connects the common v2 framework to the URB streaming implementation. It includes `dvb_usb.h` and declares the four `usb_urb_*v2` stream lifecycle helpers used by `dvb_usb_core.c`.

Important APIs/types: The declared functions are `usb_urb_initv2()`, `usb_urb_exitv2()`, `usb_urb_submitv2()`, and `usb_urb_killv2()`. They operate on `struct usb_data_stream` and, for init/submit, `struct usb_data_stream_properties`.

Control flow: `dvb_usb_core.c` calls `usb_urb_initv2()` while creating each adapter stream, `usb_urb_submitv2()` when the first demux feed starts or resume restarts active streams, `usb_urb_killv2()` when the last feed stops or suspend begins, and `usb_urb_exitv2()` during adapter teardown. The header keeps these helpers available without exposing their implementation details in `dvb_usb.h`.

State and persistence behavior: The functions mutate only runtime URB stream state: allocated buffers, URB handles, submitted counts, and state flags. No persistent storage is involved.

Dependencies and integration points: It is included by `dvb_usb_core.c` and `dvb_usb_urb.c`. The actual helper definitions are outside this subset, so this header is the compile-time contract between core control flow and USB streaming mechanics.

Risks: A mismatch between declarations and the URB implementation would break all v2 streaming. Because the header declares only coarse lifecycle operations, callers must enforce correct ordering and concurrency, which `dvb_usb_core.c` does through feed counts and streaming state bits.

Test signals: Successful module builds and live TS streaming across bulk and isochronous devices validate this header's ABI. Suspend/resume and repeated start/stop feed cycles exercise every declared helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb_core.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb_core.c

Purpose: This file implements the dvb-usb-v2 common lifecycle and data path. It is the shared engine used by the device-specific bridge drivers: firmware loading, I2C adapter registration, RC polling, DVB adapter/demux/net/media-controller setup, frontend sleep/init wrapping, power reference counting, feed start/stop, probe/disconnect, and suspend/resume.

Important APIs and functions: `dvb_usbv2_download_firmware()` uses `request_firmware()` and the driver `download_firmware` callback. `dvb_usbv2_i2c_init()`/`exit()` register a Linux I2C adapter for drivers with `i2c_algo`. RC support is in `dvb_usbv2_remote_init()`, `dvb_usb_read_remote_control()`, and `dvb_usbv2_remote_exit()`, controlled by the `disable_rc_polling` module parameter and driver RC config. Data completion callbacks forward 188-byte, 204-byte, or raw TS data to the software demux. `dvb_usb_start_feed()` and `dvb_usb_stop_feed()` manage feed counts, stream submit/kill, PID filter programming, stream config callbacks, and streaming_ctrl callbacks. Adapter setup is split across stream, DVB, frontend, and media-device init/exit helpers. `dvb_usb_fe_init()` and `dvb_usb_fe_sleep()` wrap frontend ops to coordinate power, active frontend selection, sleep waits, and original demod operations. Exported lifecycle functions are `dvb_usbv2_probe()`, `dvb_usbv2_disconnect()`, `dvb_usbv2_suspend()`, `dvb_usbv2_resume()`, and `dvb_usbv2_reset_resume()`.

Control flow: A bridge driver's USB probe calls `dvb_usbv2_probe()`. The core validates `driver_info`, allocates `struct dvb_usb_device` and optional private data, runs optional driver probe, identifies firmware state, downloads firmware if cold, then calls `dvb_usbv2_init()`. Initialization powers the device, reads config, registers I2C, creates adapters, runs driver init, registers RC, and powers down. Adapter creation determines PID filtering based on USB speed, adapter caps, and `force_pid_filter_usage`; initializes URBs; registers DVB demux/dmxdev/net/media objects; attaches frontends and tuners; and sets multi-frontend sharing when needed. At demux feed start, the first feed submits URBs and starts device streaming; later feeds only add PID filters. At last stop, device streaming stops, PID filter disables, URBs are killed, and waiters are woken. Disconnect reverses driver exit, RC, adapters, I2C, private memory, and device memory.

State and persistence: Runtime state is held in `struct dvb_usb_device` and embedded adapters. `powered` is a reference count around `power_ctrl()`. `rc_polling_active` tracks delayed work. Adapter `state_bits` coordinate initialization, sleep, and streaming; `feed_count`, `active_fe`, and `pid_filtering` drive streaming behavior. No persistent storage is written. Firmware files and module parameters are external inputs.

Dependencies and integration points: It depends on `dvb_usb_common.h`, media controller support, DVB core registration APIs, demux/net APIs, RC core, firmware loader, USB interface data, and URB helpers. It exports symbols consumed by all v2 bridge modules.

Risks: Error unwind is complex and partial failures can leave objects initialized unless driver-specific callbacks are well behaved. `dvb_usb_stop_feed()` decrements `feed_count` without underflow guards, relying on DVB demux pairing. Power reference count correctness depends on frontend init/sleep balance and suspend/resume handling. RC polling stops permanently on query error. Suspend kills URBs and calls frontend suspend for active frontends but leaves detailed hardware recovery to driver `init()` and resume callbacks. Media-controller allocation/registration is conditional and must be unwound in the correct order.

Test signals: Core validation requires probe/remove cycles, cold and warm firmware paths, adapter numbering, I2C registration, frontend attach/tuner attach failures with clean unwind, feed start/stop with multiple PIDs, PID filter forced and default modes, RC polling disable and error cases, media-controller builds, suspend/resume/reset_resume while streaming, and memory/resource leak checks after disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb_urb.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb_urb.c

Purpose: This file provides generic bulk-control read/write helpers for dvb-usb-v2 devices that use bulk endpoints for command transport. It is separate from MPEG TS URB streaming; the helpers send small control commands through driver-specified bulk endpoints.

Important APIs and functions: `dvb_usb_v2_generic_io()` validates buffers and endpoint properties, logs outgoing bytes, sends a bulk message to `generic_bulk_ctrl_endpoint`, checks exact write length, optionally sleeps for `generic_bulk_ctrl_delay`, receives a reply from `generic_bulk_ctrl_endpoint_response`, logs returned bytes, and returns the USB status. Exported wrappers are `dvb_usbv2_generic_rw()`, `dvb_usbv2_generic_write()`, `dvb_usbv2_generic_rw_locked()`, and `dvb_usbv2_generic_write_locked()`.

Control flow: Drivers call the unlocked wrappers when they want this file to take `d->usb_mutex`. Drivers that already hold the mutex call the `_locked` variants, as seen in AF9035, Anysee, and DVBSky transports. The helper always performs the write phase and performs the read phase only when both `rbuf` and `rlen` are nonzero.

State and persistence: No persistent state is used. Runtime behavior depends on endpoint numbers and delay stored in `d->props`, the USB device pointer, and the caller's buffers. The wrappers serialize with `d->usb_mutex` when requested.

Dependencies and integration points: It depends on `dvb_usb_common.h`, Linux USB bulk messaging, and the property fields defined in `dvb_usb.h`. Device-specific protocols provide command formatting and reply validation above this layer.

Risks: Endpoint properties are mandatory even for write-only operations because validation checks both send and response endpoints. The read phase does not check `actual_length` against `rlen`, so a short reply can be treated as success by this helper unless the caller validates content. The helper returns read USB errors but not a short-read error. Calling `_locked` variants without holding `d->usb_mutex` is a driver bug the function cannot detect.

Test signals: Drivers using generic bulk control should show correct debug traces, no write-length mismatch logs, successful read replies after optional delay, and no races when concurrent I2C/RC/streaming control paths share the same mutex. Fault injection with disconnected endpoints should return USB errors to callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb_urb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvbsky.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvbsky.c

Purpose: This source implements DVBSky, TechnoTrend, TerraTec, and MyGica USB receiver support for DVB-S/S2 and DVB-T/T2/C devices. It uses generic bulk command endpoints, exposes a custom I2C bridge, attaches demod/tuner modules via `dvb_module_probe()`, supports optional CI through the SP2 controller, handles RC5 remote polling, and hooks selected frontend ops for LNB power and stream resync.

Important APIs and functions: `dvbsky_usb_generic_rw()` wraps `dvb_usbv2_generic_rw_locked()` with per-device input/output buffers and USB mutex. `dvbsky_stream_ctrl()` sends pre/post stream commands, and `dvbsky_streaming_ctrl()` exposes it to the v2 core. `dvbsky_gpio_ctrl()` writes board GPIO commands. `dvbsky_i2c_xfer()` supports one-message reads/writes and two-message write-read operations with 60-byte limits. `dvbsky_rc_query()` decodes RC5 command/system/toggle from command 0x10, with `dvbsky_get_rc_config()` allowing module-parameter disable. `dvbsky_usb_set_voltage()` and `dvbsky_usb_ci_set_voltage()` wrap frontend voltage ops and toggle bridge GPIO for LNB power. `dvbsky_usb_read_status()` wraps demod status and resyncs the slave FIFO on transition to lock. Attach functions cover S960/S860 with M88DS3103/TS2020, S960CI with SP2 CI, T680CI with Si2168/Si2157/SP2, T330 with Si2168/Si2157, and MyGica T230 variants with Si2168 plus Si2157/Si2141 differences. `dvbsky_identify_state()` performs board GPIO reset sequences and always reports warm.

Control flow: The USB ID table selects one of five property structs, all with generic bulk endpoints 0x01/0x81 and stream endpoint 0x82. Probe calls the v2 core, which runs `identify_state()` for reset GPIOs, registers I2C, attaches frontend/tuner/CI according to the selected properties, calls `dvbsky_init()` to clear `last_lock`, registers RC where enabled, and then uses common feed start/stop. During tuning, frontend voltage or status operations may call back into this driver to control GPIO or restart streaming after lock. Detach releases tuner, demod, and optional CI I2C clients.

State and persistence: `struct dvbsky_state` stores 64-byte command buffers, `last_lock`, demod/tuner/CI I2C client handles, and saved frontend callbacks. There is no firmware download or nonvolatile write path. Runtime hardware state includes GPIO resets, LNB control, CI bridge commands, and stream command state.

Dependencies and integration points: It depends on `dvb_usb.h`, `m88ds3103`, `ts2020`, `sp2`, `si2168`, `si2157`, RC core, I2C module probing/release, and multiple USB ID definitions. It integrates deeply with frontend ops by saving and replacing `read_status` and `set_voltage` callbacks.

Risks: The I2C bridge only supports up to two messages and 60 bytes, so complex component transfers may fail. `dvbsky_identify_state()` always returns warm after GPIO reset and has no firmware-state validation. Frontend op wrapping assumes the original callbacks are non-null and remain valid while attached. Detach unconditionally releases client pointers, so release helpers must tolerate null. The stream resync on first lock transition can mask underlying FIFO synchronization issues. MyGica variant handling depends on product IDs for TS clock and tuner type.

Test signals: Validate every USB ID path for correct demod/tuner/CI module probe, RC5 key events unless disabled, MAC reads for property sets that enable them, LNB voltage GPIO behavior for satellite models, CI memory/control access on CI models, successful T/T2/C or S/S2 tuning, stream restart on lock transition, and clean suspend/resume/disconnect through common v2 callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvbsky.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/ec168.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/ec168.c

Purpose: This file implements the E3C EC168 DVB-T USB bridge driver. It handles cold/warm detection, firmware download, a vendor control protocol for integrated demod and tuner I2C, EC100 frontend attach, MXL5003S tuner attach, and streaming control over a single bulk endpoint.

Important APIs and functions: `ec168_ctrl_msg()` maps logical `enum ec168_cmd` values to USB request numbers, directions, values, indexes, and buffers. It allocates a transfer buffer, copies write payloads, sleeps 1 ms to reduce I2C errors, performs `usb_control_msg()`, logs through `dvb_usb_dbg_usb_control_msg()`, and copies read replies back. `ec168_i2c_xfer()` supports up to two I2C messages, routing the pseudo demod address to `READ_DEMOD`/`WRITE_DEMOD` and other writes to `WRITE_I2C`; non-demod reads are rejected. `ec168_identify_state()` reads config byte 1 and treats 0x01 as warm. `ec168_download_firmware()` uploads firmware in 2048-byte chunks, sets warm config, sends a GPIO command, and activates tuner I2C. `ec168_ec100_frontend_attach()` and `ec168_mxl5003s_tuner_attach()` attach the integrated demod and MXL tuner. `ec168_streaming_ctrl()` toggles a vendor command index between off and on values.

Control flow: The driver binds to interface 1, with interface 0 reserved for HID. Probe asks the v2 core to identify state and download `dvb-usb-ec168.fw` if cold. Warm initialization registers the I2C adapter, attaches EC100 at pseudo address 0xff, attaches the MXL5003S tuner at 0xc6, and registers one adapter streaming from endpoint 0x82 with six 32*512 bulk buffers. Start/stop feed invokes `ec168_streaming_ctrl()` through the v2 core.

State and persistence: No private state is allocated. The protocol uses stack `struct ec168_req` instances and component driver state. Firmware is loaded from disk and a volatile "warm" config byte is set in the device. No MAC, RC, EEPROM, CI, or persistent write path exists.

Dependencies and integration points: It depends on `ec168.h`, `ec100.h`, `mxl5005s.h`, the v2 framework, request-firmware via the core, Linux USB control messaging, and I2C. The EC100 demod address is a pseudo address because the demod is integrated rather than a normal external I2C device.

Risks: The demod write path assumes at least two bytes but only checks `msg[i].len < 1`, so a one-byte demod write would read `msg[i].buf[1]`. Non-demod reads are not implemented. `ec168_ctrl_msg()` accepts any nonnegative control length as success. Firmware download writes fixed post-load commands with unclear semantics, so hardware variants may need additional sequencing. Reset-resume is not registered in the USB driver.

Test signals: Cold devices should request and upload `dvb-usb-ec168.fw`, then identify warm on re-probe. Demod/tuner attach, successful tuning, stream start/stop command behavior, interface-1 binding, and repeated suspend/resume or disconnect cycles are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/ec168.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/ec168.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/ec168.h

Purpose: This private header defines the EC168 driver's request structure, firmware filename, timeout, and logical command enum. It is the protocol contract consumed by `ec168.c`.

Important APIs/types: `struct ec168_req` carries logical command, USB value, USB index, transfer size, and data pointer. `enum ec168_cmd` includes raw request names (`DOWNLOAD_FIRMWARE`, `CONFIG`, `DEMOD_RW`, `GPIO`, `STREAMING_CTRL`, `READ_I2C`, `WRITE_I2C`, `HID_DOWNLOAD`) and higher-level pseudo commands (`GET_CONFIG`, `SET_CONFIG`, `READ_DEMOD`, `WRITE_DEMOD`) that `ec168_ctrl_msg()` maps to raw requests and directions. `EC168_FIRMWARE` names `dvb-usb-ec168.fw`, and `EC168_USB_TIMEOUT` sets a 1000 ms control timeout.

Control flow support: `ec168_identify_state()` uses `GET_CONFIG`, `ec168_download_firmware()` uses `DOWNLOAD_FIRMWARE`, `SET_CONFIG`, `GPIO`, and `WRITE_I2C`, the I2C adapter uses demod and I2C commands, and streaming uses `STREAMING_CTRL`. The split between logical and raw commands keeps caller code readable while preserving device request values.

State and persistence behavior: No persistent state is declared. The firmware filename points to an external blob loaded by the v2 core, while `SET_CONFIG` updates volatile device state to mark firmware warm.

Dependencies and integration points: It includes `dvb_usb.h` for common types and framework constants. It does not expose symbols beyond the driver translation unit.

Risks: The enum mixes raw values and auto-incremented pseudo commands; inserting new enum members in the middle would silently change pseudo command values unless code is updated carefully. Numeric request meanings are hardware-specific and not self-describing.

Test signals: Successful firmware upload, warm-state config reads, demod register I/O, tuner writes, and streaming commands validate the command map. Compile failures would catch `struct ec168_req` shape changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/ec168.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/gl861.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/gl861.c

Purpose: This file supports GL861-based DVB USB devices such as MSI Mega Sky/A-LINK DTU and the Friio White ISDB-T device sharing a GL861 bridge. It provides a vendor-control I2C adapter, standard DVB-T ZL10353/QT1010 attachment for GL861 designs, and a separate Friio path using TC90522, a tuner via DVB PLL, external PIC LED/LNB control, and board-specific reset/init sequencing.

Important APIs and functions: `gl861_ctrl_msg()` serializes USB vendor control reads/writes through `d->usb_mutex`, uses a 16-byte private buffer, supports short write, full write, and read commands, logs transfers, copies read data back, and sleeps briefly to avoid I2C errors. `gl861_i2c_master_xfer()` maps Linux I2C writes, write-read pairs, and pure reads to GL861 commands with 16-byte maximum payloads. `gl861_frontend_attach()`, `gl861_tuner_attach()`, and `gl861_init()` implement the standard ZL10353/QT1010 DVB-T path with endpoint 0x81. The Friio support adds `friio_ext_ctl()` to bit-bang a PIC16F676 over I2C for LED and LNB control, `friio_reset()` for early bridge reset and Friio White detection, `friio_frontend_attach()`/detach for `tc90522`, `friio_tuner_attach()`/detach for `dvb_pll`, `friio_init()` for demod register programming, `friio_exit()` for power-down LED/LNB state, and `friio_streaming_ctrl()` for LED color changes while streaming.

Control flow: USB IDs choose either `gl861_props` or `friio_props`. Standard GL861 devices have no private firmware path: v2 probe registers I2C, attaches ZL10353 and QT1010, calls `gl861_init()` to select alternate setting 0, and streams bulk TS from endpoint 0x81. Friio devices call `friio_power_ctrl()` during v2 init, which runs `friio_reset()` before the I2C adapter exists because the reset is required before component I2C probing. After I2C registration, Friio attaches TC90522 and gets its tuner sub-I2C adapter, attaches the tuner module, runs demod init writes, and changes external LED/LNB state through stream and exit callbacks.

State and persistence: `struct gl861` stores a 16-byte USB control buffer, a tuner-side I2C adapter pointer, and demod/tuner I2C client handles. No firmware or nonvolatile settings are used. Hardware state includes USB interface alternate setting, GL861 bridge registers, Friio PIC LED color/LNB power, and demod register initialization.

Dependencies and integration points: It depends on `dvb_usb.h`, `zl10353`, `qt1010`, `tc90522`, `dvb-pll`, Linux I2C module probe/release, and USB control messaging. It uses the v2 framework for probe/disconnect/suspend/resume/reset_resume and one-adapter stream management.

Risks: The 16-byte I2C buffer limits transfer sizes. `friio_ext_ctl()` performs 70 I2C transfers and returns success only if every transfer reports as one, making it sensitive to transient I2C errors. Friio detection shares a VID/PID with another device and relies on specific readback checks during reset. `friio_reset()` must run before I2C registration and also on reset_resume, so moving it to normal init would break ordering. The standard stream buffer for GL861 is only 512 bytes per URB, which is device-specific.

Test signals: Standard GL861 validation is successful ZL10353/QT1010 attach and TS reception from endpoint 0x81. Friio validation includes Friio White detection, TC90522/tuner client probe and release, LED color transition on streaming, LNB power on/off, demod init write completion, and reset_resume recovery. I2C stress should cover short writes, multi-byte writes, write-read, and pure reads up to the 16-byte limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/gl861.c -->
