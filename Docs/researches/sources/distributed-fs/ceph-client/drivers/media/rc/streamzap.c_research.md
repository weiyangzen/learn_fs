# sources/distributed-fs/ceph-client/drivers/media/rc/streamzap.c

Purpose: USB raw IR receiver driver for Streamzap remotes. It decodes compact interrupt-URB bytes into pulse/space durations and feeds rc-core raw decoders.

Important APIs and functions: `struct streamzap_ir` stores rc device, USB interrupt URB, coherent input buffer, decoder state, and physical path. Decoder helpers include `sz_push*` and `sz_process_ir_data`; USB flow uses `streamzap_callback`, `streamzap_init_rc_dev`, `streamzap_probe`, `streamzap_disconnect`, `streamzap_suspend`, and `streamzap_resume`.

Control flow: probe validates a single interrupt IN endpoint, allocates coherent buffer and URB, registers a raw rc device with `RC_MAP_STREAMZAP`, fills the interrupt URB, and submits it. Completion decodes each byte with a small state machine handling half/full pulse and space encodings plus timeout marker `0xff`, stores filtered raw events, wakes decoding, and resubmits the URB. Suspend kills the URB; resume submits it again.

State and persistence: per-device state includes decoder state and USB buffers/URB. The rc device timeout is set to the hardware timeout duration. No persistent state exists beyond USB binding lifetime.

Dependencies and integration points: depends on USB input helpers, coherent DMA buffers, rc-core raw APIs, and the Streamzap keymap. It integrates with LIRC/raw decoders through `ir_raw_event_store_with_filter`.

Risks and edge cases: timeout is fixed by hardware and not exposed as a runtime timeout setter. URB resubmission errors in the callback are ignored. Error path after failed initial URB submit calls `rc_free_device` without `rc_unregister_device` even though registration succeeded, which is a cleanup path worth reviewing. The decoder state machine assumes byte stream continuity across URBs.

Test signals: USB probe endpoint validation, interrupt URB resubmission under remote input, decoding known Streamzap signals, timeout marker handling, suspend/resume, unplug while URB active, and keymap events through `RC_MAP_STREAMZAP`.
