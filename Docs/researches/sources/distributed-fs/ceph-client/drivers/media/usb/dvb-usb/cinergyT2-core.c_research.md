# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cinergyT2-core.c

Purpose: implements the USB/DVB framework side of the TerraTec/qanu Cinergy T2 USB2 DVB-T receiver. It handles power, stream start/stop, frontend attachment, legacy remote polling/decoding, USB IDs, and module registration.

Important APIs, types, and functions: `struct cinergyt2_state` stores a remote repeat counter and a shared 64-byte control buffer. `cinergyt2_streaming_ctrl()` sends `CINERGYT2_EP1_CONTROL_STREAM_TRANSFER`. `cinergyt2_power_ctrl()` toggles sleep mode. `cinergyt2_frontend_attach()` calls `cinergyt2_fe_attach()` and validates device communication by reading firmware version. `rc_map_cinergyt2_table[]` maps remote codes. `cinergyt2_rc_query()` reads remote events and feeds them into `dvb_usb_nec_rc_key_to_event()` with a checksum workaround.

Control flow: probe calls `dvb_usb_device_init()` using `cinergyt2_properties`. The adapter has one frontend with bulk streaming endpoint `0x02`, five buffers of 512 bytes, and frontend attach in `cinergyt2-fe.c`. Control commands go through generic bulk endpoint 1 with `data_mutex` held. Remote query polls every 50 ms, treats `data[4] == 0xff` as repeat, delays repeats by three polls, and only repeats navigation, volume, and channel keys.

State and persistence: per-device state is private framework memory. The 64-byte buffer is reused for control traffic under `data_mutex`. `rc_counter` persists across remote polls and resets when a new key differs from `last_event`. Power and streaming state persists in device firmware.

Dependencies and integration points: depends on `cinergyT2.h`, DVB USB generic bulk control, Linux input keycodes, and `cinergyt2_fe_attach()` from `cinergyT2-fe.c`. The device is registered as a warm-only TerraTec Cinergy T2 USB ID with no firmware download path in this file.

Risks: remote decoding mutates `data[2]` to fake a NEC checksum custom field, which is protocol-specific and fragile. Frontend attach returns firmware-version read errors but leaves normal cleanup to release callback. PID setup command definitions exist in the header but this core file does not expose PID filtering. Small 512-byte streaming buffers reflect USB2 high-speed but may be sensitive to throughput.

Test signals: probe warm hardware, power sleep/wake, stream on/off, frontend attach and firmware-version read, remote key map and repeat behavior, disconnect cleanup, and DVB-T transport stability under sustained streaming.
