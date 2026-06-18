# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005-remote.c

Purpose: provides the legacy remote-control decoder and key map for AF9005 devices. It is intentionally separate from the main driver and exported through symbols so `af9005.c` can enable remote support dynamically when this module is present.

Important APIs, types, and functions: `rc_map_af9005_table[]` maps two groups of custom/data codes to Linux input keycodes. `rc_map_af9005_table_size` exports its size. `repeatable_keys[]` limits repeat events to volume and channel keys. `af9005_rc_decode()` consumes raw timing bytes read by `af9005_rc_query()` in the main driver and fills the DVB USB legacy `event` and `state` outputs. The module exports the table, size, and decoder via `EXPORT_SYMBOL`.

Control flow: decode requires at least one mark/space pair. If the first space is much shorter than the mark, the packet is treated as a repeat; only keys in `repeatable_keys` produce `REMOTE_KEY_REPEAT`, and other repeated keys are ignored. Otherwise, for a full 33-symbol timing buffer, the function skips the start code and decodes 32 bits by comparing mark and space widths. It requires the high byte to be `0xfe`, extracts customer code and data byte, verifies the data byte against the inverted low byte, then searches the rc-map table by `rc5_custom()` and `rc5_data()` before reporting `REMOTE_KEY_PRESSED`.

State and persistence: the decoder itself keeps no private persistent state. Repeat handling depends on `d->last_event`, owned by the DVB USB remote framework. The key map is static module data.

Dependencies and integration points: depends on `af9005.h`, Linux input keycodes, DVB USB legacy remote constants, `rc_map_table`, `rc5_custom()`, and `rc5_data()`. `af9005_usb_module_init()` obtains `af9005_rc_decode`, `rc_map_af9005_table`, and `rc_map_af9005_table_size` with `symbol_request()` and disables the remote query callback if any symbol is unavailable.

Risks: this is legacy IR handling and the main driver even notes a future conversion to the modern kernel IR infrastructure. The timing decode is heuristic and assumes fixed packet layout; malformed buffers silently produce no event. The name `rc5_*` is used around values that look like NEC-style customer/data fields, which may confuse maintenance. Only four keys repeat by design.

Test signals: test with actual AF9005 remotes for full key map coverage, repeat suppression for non-repeatable keys, repeat generation for channel/volume keys, bad header rejection, inverted-byte mismatch rejection, and missing remote module behavior in `af9005.c`.
