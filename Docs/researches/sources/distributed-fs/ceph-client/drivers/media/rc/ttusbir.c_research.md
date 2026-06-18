# sources/distributed-fs/ceph-client/drivers/media/rc/ttusbir.c

Purpose: USB raw IR receiver driver for TechnoTrend TT USB IR hardware. It consumes high-rate isochronous sample packets, converts one-bit samples to raw events, and controls the device LED through a bulk endpoint.

Important APIs and functions: `struct ttusbir` stores rc device, USB device, four isochronous URBs, LED classdev, LED bulk URB/buffer, endpoints, LED state, and physical path. Main functions are LED callbacks, `ttusbir_process_ir_data`, `ttusbir_urb_complete`, `ttusbir_probe`, disconnect, suspend, and resume.

Control flow: probe searches alternate settings for an isochronous IN endpoint with 0x10 max packet and a bulk OUT endpoint with 0x20 max packet, sets that interface, allocates four 8-frame isochronous URBs with 128-byte coherent buffers, allocates a LED bulk URB, registers LED and raw rc device, then submits all URBs. Each isochronous completion decodes 128 bytes where set bits mean silence, handles full-byte pulse/space and single-edge cases, filters raw events, wakes decoders only when data changed, and resubmits the URB. LED writes submit a serialized bulk URB when requested state differs.

State and persistence: per-device state includes URBs, coherent buffers, LED pending flag, and rc settings. Runtime state is volatile; disconnect kills URBs, unregisters rc/LED, frees buffers, and clears interface data.

Dependencies and integration points: depends on USB isochronous/bulk APIs, LED class, rc-core raw decoding, and keymap `RC_MAP_TT_1500`.

Risks and edge cases: the probe allocation check is suspicious: `if (!tt || !rc || buffer)` treats successful `buffer` allocation as an error, so this snapshot appears to fail normal probe before assigning `tt->bulk_buffer`. If fixed, high-rate idle URBs still require efficient filtering to avoid unnecessary decoder wakeups. LED state uses atomic serialization but relies on barriers and `udev` nulling during disconnect. Resume returns the last submit status and stops after first URB failure.

Test signals: build/static analysis should catch the probe condition, USB probe after correcting allocation logic, alternate-setting selection, sustained isochronous input, raw timing accuracy around one-edge bytes, LED trigger behavior, suspend/resume URB restart, and disconnect races with LED bulk completion.
