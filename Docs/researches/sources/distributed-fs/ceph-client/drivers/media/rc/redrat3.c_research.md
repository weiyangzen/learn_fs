# sources/distributed-fs/ceph-client/drivers/media/rc/redrat3.c

Purpose: USB rc-core driver for RedRat3 and RedRat3-II IR transceivers. It receives narrowband and wideband IR, reports optional carrier information, transmits encoded IR through the device firmware protocol, exposes a feedback LED, and controls capture parameters.

Important APIs and functions: packet structures are `redrat3_header`, `redrat3_irdata`, and `redrat3_error`; device state is `struct redrat3_dev`. Major flows include `redrat3_reset`, `redrat3_get_firmware_rev`, `redrat3_enable_detector`, `redrat3_handle_async`, packet accumulation helpers, `redrat3_process_ir_data`, timeout get/set, `redrat3_transmit_ir`, `redrat3_set_tx_carrier`, `redrat3_wideband_receiver`, LED callbacks, `redrat3_init_rc_dev`, USB probe/disconnect, and suspend/resume.

Control flow: probe discovers bulk-in narrow/wide and bulk-out endpoints, allocates shared coherent input buffer and URBs, resets/configures firmware parameters, creates LED/learning URBs, registers an `RC_DRIVER_IR_RAW` rc device, then enables detector capture and submits receive URBs. Incoming URBs are accumulated until a complete firmware packet is available; signal packets map length-table indices to alternating pulse/space raw events and append a trailing timeout. TX converts microsecond durations into RedRat length table entries and sigdata indices, bulk-writes the packet, then sends a vendor command to transmit.

State and persistence: per-device state holds endpoint descriptors, URBs, coherent buffer, current packet assembly, transmit flag, carrier, LED/learning control state, rc device, and USB identity strings. Firmware parameters such as length fuzz, minimum pause, periods-to-measure-carrier, max lengths, and timeout are programmed at runtime and are not persisted by the driver.

Dependencies and integration points: depends on USB bulk/control transfers, rc-core raw RX/TX, LED class, unaligned big-endian helpers, and keymap `RC_MAP_HAUPPAUGE`. Wideband mode integrates with rc-core carrier reports through `s_carrier_report`.

Risks and edge cases: narrow and wide URBs share one coherent input buffer, so simultaneous completions would race on packet data. TX is guarded only by a boolean, not a lock. Packet assembly resets on malformed length but relies on firmware length fields. Probe error paths unregister LED but may need careful review after rc device creation failures. Module parameters accept documented ranges but are not range-validated before firmware writes. Hardware timing conversion clamps large durations and deduplicates exact converted lengths only.

Test signals: USB probe for both product IDs, endpoint validation, firmware parameter writes, continuous receive on narrowband, wideband carrier reports, `ir-ctl` transmit, timeout get/set, LED feedback blink, suspend/resume URB resubmission, disconnect during active receive/TX, and malformed packet/error-code handling.
