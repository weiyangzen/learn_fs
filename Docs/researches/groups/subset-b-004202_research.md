# subset-b-004202 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005-fe.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005-fe.c

Purpose: implements the DVB-T frontend/demodulator half of the Afatech AF9005 USB1.1 receiver. It creates a `struct dvb_frontend`, initializes the AF9005 OFDM core through register writes and the firmware-derived init script, attaches either an MT2060 or QT1010/QT1010B tuner based on EEPROM data, tunes DVB-T parameters, and exposes status/statistics callbacks to the DVB core.

Important APIs, types, and functions: `struct af9005_fe_state` is the persistent frontend state and stores the parent `dvb_usb_device`, cached frontend status, original AGC/top/frequency-control values saved during init, BER/uncorrected-block counters, open-count state for LED behavior, and the embedded `struct dvb_frontend`. `af9005_fe_attach()` allocates this state and installs `af9005_fe_ops`. Register helpers `af9005_write_word_agc()` and `af9005_read_word_agc()` combine split low-byte/high-bit AGC fields. Statistic helpers read and reset pre-Viterbi and post-Viterbi hardware counters. `af9005_fe_init()` is the large hardware bring-up path. `af9005_fe_set_frontend()` is the tune path. `af9005_fe_read_status()`, `read_ber`, `read_signal_strength`, `read_snr`, and `read_ucblocks` implement DVB frontend callbacks.

Control flow: attach only allocates software state. The real hardware sequence starts in `af9005_fe_init()`: reset OFDM, clear/reset clocks, power the tuner, configure stand-alone/DCA/I2C settings, program initial CFOE coefficients for 6 MHz, enable read-update and FEC monitor bits, write every entry in `script[]`, save original FCW/unplug-threshold/TOP values, read tuner ID from EEPROM, attach the tuner module, and call tuner init. Tuning first disables the LED/transport path, restores original FCW and AGC/TOP values, selects bandwidth and reprograms CFOE coefficients, clears easy mode and retrain flags, calls tuner `set_params`, triggers OFSM through the tuner-register command path, resets statistics counters, and arms immediate status refresh.

State and persistence: state is in memory only and is freed by `af9005_fe_release()`. Hardware state is persistent in device registers until reset or retune; the driver snapshots selected initial register values so every tune can restore a known baseline. `unc` intentionally accumulates across tunes, while BER and abort counters are reset on tune. `opened` is an internal TS bus acquisition count used to turn the LED off when the bus is released.

Dependencies and integration points: depends on `af9005.h` register definitions and exported helpers in `af9005.c`, the generated `af9005-script.h`, tuner modules `mt2060` and `qt1010`, DVB frontend ops, `dvb_attach`, `jiffies`, and `do_div`. It is integrated by `af9005_frontend_attach()` in `af9005.c`.

Risks: large hard-coded register sequences with comments noting unknown register meanings make regressions hard to reason about without hardware. `af9005_fe_read_status()` passes `mp2if_sync_byte_locked_pos` as both position and length, which looks suspicious because the length macro is not used. BER calculation uses `do_div` in a way that assigns the remainder rather than the quotient on Linux, so reported BER semantics deserve review. Return values from statistic reset calls in `set_frontend()` are ignored. Many waits are polling loops with fixed timeouts.

Test signals: compile coverage should catch API drift in DVB/tuner ops. Hardware smoke tests should cover init, tuner attach for all EEPROM tuner IDs, tune for 6/7/8 MHz, lock transitions, LED behavior, BER/uncounter reads, repeated retunes, unplug/strong-signal paths, and suspend/sleep power-off. Register trace comparison against known-good AF9005 hardware is the best regression signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005-fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005-remote.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005-remote.c

Purpose: provides the legacy remote-control decoder and key map for AF9005 devices. It is intentionally separate from the main driver and exported through symbols so `af9005.c` can enable remote support dynamically when this module is present.

Important APIs, types, and functions: `rc_map_af9005_table[]` maps two groups of custom/data codes to Linux input keycodes. `rc_map_af9005_table_size` exports its size. `repeatable_keys[]` limits repeat events to volume and channel keys. `af9005_rc_decode()` consumes raw timing bytes read by `af9005_rc_query()` in the main driver and fills the DVB USB legacy `event` and `state` outputs. The module exports the table, size, and decoder via `EXPORT_SYMBOL`.

Control flow: decode requires at least one mark/space pair. If the first space is much shorter than the mark, the packet is treated as a repeat; only keys in `repeatable_keys` produce `REMOTE_KEY_REPEAT`, and other repeated keys are ignored. Otherwise, for a full 33-symbol timing buffer, the function skips the start code and decodes 32 bits by comparing mark and space widths. It requires the high byte to be `0xfe`, extracts customer code and data byte, verifies the data byte against the inverted low byte, then searches the rc-map table by `rc5_custom()` and `rc5_data()` before reporting `REMOTE_KEY_PRESSED`.

State and persistence: the decoder itself keeps no private persistent state. Repeat handling depends on `d->last_event`, owned by the DVB USB remote framework. The key map is static module data.

Dependencies and integration points: depends on `af9005.h`, Linux input keycodes, DVB USB legacy remote constants, `rc_map_table`, `rc5_custom()`, and `rc5_data()`. `af9005_usb_module_init()` obtains `af9005_rc_decode`, `rc_map_af9005_table`, and `rc_map_af9005_table_size` with `symbol_request()` and disables the remote query callback if any symbol is unavailable.

Risks: this is legacy IR handling and the main driver even notes a future conversion to the modern kernel IR infrastructure. The timing decode is heuristic and assumes fixed packet layout; malformed buffers silently produce no event. The name `rc5_*` is used around values that look like NEC-style customer/data fields, which may confuse maintenance. Only four keys repeat by design.

Test signals: test with actual AF9005 remotes for full key map coverage, repeat suppression for non-repeatable keys, repeat generation for channel/volume keys, bad header rejection, inverted-byte mismatch rejection, and missing remote module behavior in `af9005.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005-remote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005-script.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005-script.h

Purpose: contains the AF9005 OFDM initialization script used by `af9005_fe_init()`. The file documents that it was generated from bytes extracted from the Windows driver and converted by `createinit.py`.

Important APIs, types, and data: `RegDesc` describes one register-bit write with `reg`, `pos`, `len`, and `val`. `static RegDesc script[]` is a linear sequence of AF9005 register field writes. The array programs ADC/frequency-control values, AGC thresholds, DCA/FEQ/FEC-related settings, MPEG/OFSM control bits, and other hardware parameters. It is not exported as an API; inclusion into `af9005-fe.c` makes the static array local to that translation unit.

Control flow: `af9005_fe_init()` computes `scriptlen = sizeof(script) / sizeof(RegDesc)` and applies each entry with `af9005_write_register_bits()`. During that loop it also observes selected script entries to save original FCW bytes and unplug thresholds into `struct af9005_fe_state`. Those saved values are later restored during `af9005_fe_set_frontend()` before each tune.

State and persistence: the script itself is static read-only driver data after module load. Its effects persist in AF9005 hardware registers until later register writes, retune, reset, or disconnect. Some script values become software baseline state because `af9005-fe.c` copies them into `original_fcw` and threshold fields.

Dependencies and integration points: depends on Linux integer typedefs being available through the including C file. It uses raw register addresses rather than the symbolic names from `af9005.h` for many entries, though some addresses correspond to named AF9005 register fields. Its only direct consumer is `af9005-fe.c`.

Risks: generated magic values are hard to audit and have no semantic grouping. Because `RegDesc` and `script` are defined in a header, including it from multiple C files would create multiple static copies and type definitions. Register field length/position mistakes are only visible on hardware. Changing script order can alter hardware bring-up behavior.

Test signals: AF9005 hardware init is the primary test. Useful checks include comparing USB/register traces against a known-good driver, verifying that all script entries return success, validating saved FCW/threshold values, and confirming tune/lock behavior across supported bandwidths and tuner variants after script application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005-script.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005.c

Purpose: implements the main AF9005 USB DVB-T driver: USB protocol framing, firmware download, register access, software I2C adapter, EEPROM reads, LED control, frontend attach, PID filtering, remote polling, USB ID table, and module registration.

Important APIs, types, and functions: module parameters expose debug, LED enable, EEPROM dump, and adapter number. `struct af9005_device_state` stores the AF9005 sequence counter, LED state, and a shared 256-byte transfer buffer. `af9005_generic_read_write()` is the core register protocol for OFDM and tuner commands. Public helpers include OFDM register reads/writes, bitfield helpers, tuner-register bridge helpers, `af9005_send_command()`, `af9005_read_eeprom()`, and `af9005_led_control()`. `af9005_i2c_algo` exposes a limited I2C master for tuner modules. `af9005_download_firmware()` and `af9005_boot_packet()` implement cold-device firmware loading.

Control flow: probe calls `dvb_usb_device_init()` with `af9005_properties`. Cold/warm detection uses `FW_CONFIG` boot packets. Firmware download sends fixed-size 250-byte bulk packets and validates confirm/config replies. Register access serializes on `data_mutex`, builds a command with sequence number, validates ack code, reply length, sequence, and status byte, then copies read data back. Frontend attach clears endpoint halts, optionally dumps EEPROM, then calls `af9005_fe_attach()`. Tuning and statistics are delegated to `af9005-fe.c`. PID filtering writes MPEG PID table registers and enables/disables the table based on feed count. Remote polling sends command `0x40`, validates reply `0x41`, then calls a dynamically requested decoder if present.

State and persistence: driver-private state is per USB device. `sequence` increments for command matching and is protected by `data_mutex`. `led_state` avoids redundant LED register writes. Register, tuner, EEPROM, firmware, PID table, and LED effects persist in device hardware. Remote state relies partly on DVB USB's `last_event`.

Dependencies and integration points: depends on `dvb-usb`, USB bulk/control APIs, firmware loader, AF9005 register definitions, `af9005-fe.c`, optional `af9005-remote.c` symbols, and tuner modules through the frontend. The `dvb_usb_device_properties` block binds endpoints, firmware name `af9005.fw`, I2C algorithm, PID filter callbacks, remote callbacks, and supported USB IDs.

Risks: the software I2C adapter only implements the exact transactions used by the supported tuners and warns on more than two messages. Firmware protocol and register framing are magic-number heavy. Some paths ignore return values during EEPROM dump and remote decode has legacy symbol-request coupling. The PID filter relies on `feedcount` timing. Timeout loops can block for seconds on broken hardware.

Test signals: build with AF9005 and optional remote module, cold firmware load, warm identify, register read/write sanity, EEPROM read, tuner I2C attach, PID filter on/off with multiple feeds, remote polling with and without remote module, LED module parameter behavior, disconnect cleanup, and USB trace comparison for firmware and register transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005.h

Purpose: shared AF9005 driver header containing debug macros, firmware/register protocol constants, a large AF9005 OFDM register/bitfield map, MPEG transport interface register constants, exported function prototypes, remote decoder declarations, and the shared bitmask table declaration.

Important APIs, types, and definitions: defines `DVB_USB_LOG_PREFIX`, debug categories (`deb_info`, `deb_xfer`, `deb_rc`, `deb_reg`, `deb_i2c`, `deb_fw`), firmware packet size and boot states, register command constants (`AF9005_REGISTER_RW`, `AF9005_CMD_*`), OFDM/tuner register target selectors, special APO register addresses, thousands of `xd_*` register addresses with matching `*_pos`, `*_len`, and `*_lsb` macros, MPEG2 interface registers (`XD_MP2IF_*`), and declarations for helper functions implemented in `af9005.c` and `af9005-fe.c`.

Control flow role: this header has no executable flow but defines the contract used by the AF9005 implementation. `af9005.c` uses protocol constants, debug macros, MPEG/PID registers, EEPROM/register helper prototypes, and remote declarations. `af9005-fe.c` uses the register map and bitfield metadata to initialize and tune the demodulator, compute status, and read statistics. `af9005-remote.c` uses the shared debug/logging and remote declarations.

State and persistence: no state is allocated here. The constants describe persistent hardware state that is read or written through helper functions. `extern u8 regmask[8]` points to the runtime mask table in `af9005.c`; the module parameters `dvb_usb_af9005_debug` and `dvb_usb_af9005_led` are declared as external state.

Dependencies and integration points: includes `dvb-usb.h`, so it is tied to the legacy DVB USB framework. Its prototypes create cross-file integration among AF9005 main driver, frontend, and remote decoder. Register constants mirror the AF9005/Apollo demodulator hardware blocks: AGC, TINR, CCIF, DCA, CFOE, TPS, FFT, FEC, I2C bridge, MP2IF, top GPIO/LED, and OFSM control.

Risks: the enormous generated-style register map is easy to misuse because many fields share an address and require correct position/length macros. Some names contain typos, such as `reg_strong_sginal_detected`, which must remain stable for users in the C files. There is an unused or absent implementation declaration for `af9005_tuner_attach()`, suggesting stale API surface. Lack of namespace separation can cause collisions if included carelessly.

Test signals: compile all AF9005 translation units with warnings, exercise all register helper call sites that use `*_pos`/`*_len`, and use hardware register traces to confirm that symbolic constants still map to expected addresses. Header changes should trigger smoke tests for init, tune, PID filter, LED, I2C, and remote behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/az6027.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/az6027.c

Purpose: implements the AzureWave/TerraTec/Technisat/Elgato AZ6027-family USB2 DVB-S/S2 driver. It configures an STB0899 demodulator and STB6100 tuner over a vendor-specific USB I2C bridge, controls streaming and frontend reset/power, provides EN50221 CI/CAM operations, exposes minimal remote-control plumbing, and registers the USB device table.

Important APIs, types, and functions: `struct az6027_device_state` stores the DVB CA object, CI mutex, and a power-state byte. Large static STB0899 init arrays and `az6027_stb0899_config` define demodulator setup; `az6027_stb6100_config` defines tuner setup. `az6027_usb_in_op()` and `az6027_usb_out_op()` wrap vendor control transfers. CI callbacks implement attribute memory, CAM control, reset, TS enable, and poll status. `az6027_i2c_xfer()` is an address-aware I2C bridge for the LNB voltage command address `0x99`, demod address `0xd0`, and tuner address `0xc0`.

Control flow: probe delegates to `dvb_usb_device_init()`. Identify state sends vendor request `0xb7` and marks the device cold if it cannot read six bytes. Frontend attach powers on request `0xBC`, resets the demod with request `0xC0`, attaches STB0899 and then STB6100, overrides `set_voltage`, initializes CI if tuner attach succeeds, and disables TS bypass. Streaming control sends request `0xBC` with the on/off value. Disconnect releases CI before standard DVB USB teardown.

State and persistence: CA state persists in `state->ca` until disconnect, protected by `ca_mutex`. USB and I2C operations serialize on framework mutexes. Frontend power/reset, TS bypass, CI slot state, LNB voltage, demod/tuner registers, and firmware state persist in hardware. The driver does not maintain rich software tuning state; most state lives in attached frontend/tuner drivers.

Dependencies and integration points: depends on `az6027.h`, DVB USB, STB0899 and STB6100 frontend/tuner drivers, DVB CA EN50221, USB control messaging, and Linux I2C. `az6027_properties` binds firmware `dvb-usb-az6027-03.fw`, Cypress FX2 control, bulk endpoint `0x02`, remote map/query placeholders, I2C algorithm, and eight USB device descriptions.

Risks: I2C transfer return handling is weak: the function returns loop index rather than conventional message count in all cases, and vendor op failures are not consistently propagated. The demod read path checks `msg[i].len < 1` but then uses `buf[1]`, so a one-byte message can read past the buffer. Several control messages pass `NULL` with zero length, but the commented power function shows historical uncertainty. CI reset sleeps for several seconds while holding `ca_mutex`. Remote support is a stub.

Test signals: compile with STB0899/STB6100 and CA enabled, probe all USB IDs, cold firmware load, frontend power/reset, STB0899/STB6100 attach, DVB-S and DVB-S2 lock, LNB voltage 13/18/off, CI CAM insert/reset/status/attribute/control access, streaming on/off, disconnect after CI init, and I2C transaction traces for `0xd0`, `0xc0`, and `0x99`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/az6027.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/az6027.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/az6027.h

Purpose: small shared header for the AZ6027 driver. It establishes the DVB USB log prefix, includes the DVB USB framework header, declares the module debug variable, and defines debug-print category macros used by `az6027.c`.

Important APIs and definitions: `DVB_USB_LOG_PREFIX` is set to `az6027`. `extern int dvb_usb_az6027_debug` is the module parameter storage defined in the C file. `deb_info`, `deb_xfer`, `deb_rc`, and `deb_fe` call `dprintk()` with bit masks `0x01`, `0x02`, `0x04`, and `0x08`.

Control flow role: no executable code. The header supplies logging helpers and the DVB USB type definitions needed by the implementation.

State and persistence: no private state is stored here. The only declared state is the external debug mask.

Dependencies and integration points: includes `dvb-usb.h`, tying the implementation to the DVB USB framework and its debug/logging macros. The include guard is named `_DVB_USB_VP6027_H_`, which does not match AZ6027 but still prevents duplicate inclusion.

Risks: the mismatched include guard name is harmless but confusing. Debug category documentation in the C module mentions only info/xfer/rc, while the header also defines `deb_fe`. Any future split into multiple AZ6027 files would need this header to grow real shared prototypes.

Test signals: compile the AZ6027 driver and verify debug masks produce expected log categories when module parameter `debug` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/az6027.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cinergyT2-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cinergyT2-core.c

Purpose: implements the USB/DVB framework side of the TerraTec/qanu Cinergy T2 USB2 DVB-T receiver. It handles power, stream start/stop, frontend attachment, legacy remote polling/decoding, USB IDs, and module registration.

Important APIs, types, and functions: `struct cinergyt2_state` stores a remote repeat counter and a shared 64-byte control buffer. `cinergyt2_streaming_ctrl()` sends `CINERGYT2_EP1_CONTROL_STREAM_TRANSFER`. `cinergyt2_power_ctrl()` toggles sleep mode. `cinergyt2_frontend_attach()` calls `cinergyt2_fe_attach()` and validates device communication by reading firmware version. `rc_map_cinergyt2_table[]` maps remote codes. `cinergyt2_rc_query()` reads remote events and feeds them into `dvb_usb_nec_rc_key_to_event()` with a checksum workaround.

Control flow: probe calls `dvb_usb_device_init()` using `cinergyt2_properties`. The adapter has one frontend with bulk streaming endpoint `0x02`, five buffers of 512 bytes, and frontend attach in `cinergyt2-fe.c`. Control commands go through generic bulk endpoint 1 with `data_mutex` held. Remote query polls every 50 ms, treats `data[4] == 0xff` as repeat, delays repeats by three polls, and only repeats navigation, volume, and channel keys.

State and persistence: per-device state is private framework memory. The 64-byte buffer is reused for control traffic under `data_mutex`. `rc_counter` persists across remote polls and resets when a new key differs from `last_event`. Power and streaming state persists in device firmware.

Dependencies and integration points: depends on `cinergyT2.h`, DVB USB generic bulk control, Linux input keycodes, and `cinergyt2_fe_attach()` from `cinergyT2-fe.c`. The device is registered as a warm-only TerraTec Cinergy T2 USB ID with no firmware download path in this file.

Risks: remote decoding mutates `data[2]` to fake a NEC checksum custom field, which is protocol-specific and fragile. Frontend attach returns firmware-version read errors but leaves normal cleanup to release callback. PID setup command definitions exist in the header but this core file does not expose PID filtering. Small 512-byte streaming buffers reflect USB2 high-speed but may be sensitive to throughput.

Test signals: probe warm hardware, power sleep/wake, stream on/off, frontend attach and firmware-version read, remote key map and repeat behavior, disconnect cleanup, and DVB-T transport stability under sustained streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cinergyT2-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cinergyT2-fe.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cinergyT2-fe.c

Purpose: implements the DVB frontend operations for the TerraTec/qanu Cinergy T2 USB2 DVB-T receiver. Unlike AF9005, the demodulation details are largely hidden behind the device firmware protocol, so this file converts DVB frontend parameters to device messages and translates device status messages into DVB frontend status/statistics.

Important APIs, types, and functions: `compute_tps()` maps Linux DVB-T parameters to a 16-bit TPS field following ETSI DVB-T bit placement. `struct cinergyt2_fe_state` embeds `struct dvb_frontend`, stores the parent `dvb_usb_device`, owns a 64-byte control buffer and mutex, and caches `struct dvbt_get_status_msg`. `cinergyt2_fe_attach()` allocates state and installs `cinergyt2_fe_ops`. Frontend callbacks implement status, BER, uncorrected blocks, strength, SNR, tune settings, tuning, sleep/init, and release.

Control flow: `set_frontend()` locks the frontend data mutex, overlays the control buffer with `struct dvbt_set_parameters_msg`, fills command, frequency in kHz, bandwidth code 6/7/8, computed TPS, and flags, then sends the message through `dvb_usb_generic_rw()` and expects a two-byte reply. `read_status()` sends `CINERGYT2_EP1_GET_TUNER_STATUS`, copies the packed response into cached status, and derives `FE_HAS_*` flags from gain and lock bits. BER/SNR/strength/uncorrected-block reads return fields from the most recent cached status. Tune settings request an 800 ms minimum delay.

State and persistence: frontend state is per attach and freed on release. The cached status persists until the next successful status read; statistic callbacks do not refresh hardware themselves. Hardware tuning state persists in device firmware after set-parameters command. The mutex protects only this frontend buffer, distinct from the core driver's shared control buffer.

Dependencies and integration points: depends on command and message definitions in `cinergyT2.h`, DVB USB generic bulk control, endian conversion helpers, and DVB frontend ops. It is attached by `cinergyt2_frontend_attach()` in `cinergyT2-core.c`.

Risks: BER/SNR/strength can return stale or zeroed data if userspace reads them before `read_status()` succeeds. `compute_tps()` silently maps unknown/AUTO values to default TPS bits, which is intentional but may hide unsupported combinations. Status lock logic clears `FE_HAS_LOCK` unless carrier, Viterbi, and sync are also set, so device firmware lock bits are filtered. The code logs an error via `err()` inside a variable named `err`, relying on macro/function namespace behavior that is potentially confusing.

Test signals: tune DVB-T channels with 6/7/8 MHz bandwidth, verify TPS encoding for modulation/FEC/guard/hierarchy/transmission modes, confirm lock-bit mapping under weak/no signal, read stats before and after status refresh, validate 800 ms tune delay behavior, and run repeated attach/release cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cinergyT2-fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cinergyT2.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cinergyT2.h

Purpose: shared header for the TerraTec/qanu Cinergy T2 driver. It defines driver identity, debug macros, endpoint-1 firmware command IDs, packed control/status message formats, and the frontend attach prototype.

Important APIs, types, and definitions: `DRIVER_NAME` is the frontend/device display name. Debug macros define info, transfer, PLL, TS, error, RC, firmware, memory, and USB-transfer categories. `enum cinergyt2_ep1_cmd` defines command bytes for PID table reset/setup, stream transfer control, tuner parameters, tuner status, scan, remote events, sleep mode, and firmware version. `struct dvbt_get_status_msg` mirrors the packed firmware status response. `struct dvbt_set_parameters_msg` mirrors the packed firmware tune request. `cinergyt2_fe_attach()` is declared for the core file.

Control flow role: no executable code. The command IDs drive `cinergyT2-core.c` and `cinergyT2-fe.c` control messages. The packed structures define how those files overlay local byte buffers before calling `dvb_usb_generic_rw()` and how responses are interpreted.

State and persistence: no runtime state is stored here. The packed message structures describe transient USB control payloads and cached frontend status in `cinergyT2-fe.c`.

Dependencies and integration points: includes `<linux/usb/input.h>` and `dvb-usb.h`, binding the driver to Linux input definitions and the DVB USB framework. Both CinergyT2 C files include this header, so changes affect power/streaming, remote, and frontend tune/status paths.

Risks: packed structs must match the published device protocol exactly; field size or endian changes would break hardware communication. Some command IDs for PID and scan are defined but unused in the current C files. Debug categories are broader than current usage, which may suggest inherited or stale logging surface.

Test signals: compile both CinergyT2 translation units, verify structure sizes against expected firmware protocol lengths, inspect USB control payloads for tune/status/sleep/stream/remote commands, and run hardware tests for frontend attach, tuning, status reads, power, and streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cinergyT2.h -->
