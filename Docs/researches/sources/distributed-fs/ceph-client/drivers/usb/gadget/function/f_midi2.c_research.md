# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_midi2.c

## Purpose

`f_midi2.c` implements a USB MIDI 2.0 gadget function with mandatory MIDI 1.0 compatibility. It exposes ALSA UMP endpoints and function blocks, builds USB MIDI 2.0 group terminal block descriptors, supports UMP Stream discovery/control messages, and converts between MIDI 1.0 USB event packets and UMP when the host selects altsetting 0.

## Important APIs, Types, and Functions

`struct f_midi2` is the per-function device state, containing the USB function, ALSA card, MIDI 1.0 compatibility endpoints, UMP conversion state, cable/group mappings, operation mode, queue lock, card configuration, UMP endpoint array, and string tables. `struct f_midi2_ep` represents one UMP endpoint with ALSA `snd_ump_endpoint`, configured endpoint info, function blocks, USB IN/OUT resources, and group-to-cable mapping. `struct f_midi2_usb_ep` and `struct f_midi2_req_ctx` manage request pools with a bitmap of free requests. `struct f_midi2_block` mirrors UMP function blocks and USB group terminal blocks.

UMP-native processing uses `process_ump()`, `process_ump_stream_msg()`, `reply_ump_stream_*()`, `f_midi2_ep_out_complete()`, `process_ump_transmit()`, and `f_midi2_ep_in_complete()`. MIDI 1.0 compatibility uses `process_midi1_byte()`, pending-byte helpers, `process_midi1_transmit()`, `f_midi2_midi1_ep_in_complete()`, and `f_midi2_midi1_ep_out_complete()`. Descriptor and endpoint setup is handled by `assign_block_descriptors()`, `f_midi2_setup()`, `f_midi2_create_card()`, `f_midi2_create_usb_configs()`, `fill_midi2_class_desc()`, `f_midi2_bind()`, `f_midi2_set_alt()`, and `f_midi2_get_alt()`.

## Control Flow

`f_midi2_alloc_inst()` creates a default configfs tree with `ep.0/block.0`, static blocks, request count 32, request buffer size 512, UMP processing enabled, protocol 2 with caps 1 and 2, and one MIDI1 group. Configfs can add endpoint groups and block groups before binding. `f_midi2_alloc()` verifies contiguous endpoints and blocks, validates protocol/group ranges, copies configfs state, assigns one-based GTB IDs, creates string definitions, and fills MIDI1 cable mappings. Allocation fails if no MIDI1-compatible group exists.

`f_midi2_bind()` creates the ALSA UMP card, attaches strings, assigns an AudioControl interface plus one MIDIStreaming interface with altsetting 0 for MIDI1 and altsetting 1 for MIDI2, initializes compatibility and native endpoints, builds speed-specific descriptors, and registers class-specific GTB descriptor handling through `setup()`. `set_alt()` switches operation mode, stops endpoints for the old mode, starts endpoints and queues OUT requests for the new mode, and `get_alt()` reports altsetting 1 only in MIDI2 mode. UMP stream discovery requests can return endpoint info, device info, endpoint name, product ID, stream config, function block info, and block names; stream config requests switch the ALSA UMP protocol.

## State and Persistence Behavior

State is in-memory and mode-dependent. Request pools are protected by `queue_lock` and tracked by per-endpoint `free_reqs` bitmaps. `operation_mode` is also exposed as a volatile ALSA rawmidi control. UMP protocol can change at runtime through stream config messages and is mirrored into ALSA via `snd_ump_switch_protocol()`. Configfs options are immutable once `refcnt` is nonzero. No data is persisted beyond ALSA/USB runtime objects.

## Dependencies and Integration Points

The driver depends on USB composite/gadget APIs, USB Audio and MIDI 2.0 descriptor definitions, `func_utils` request helpers, ALSA card/control APIs, ALSA UMP core, UMP conversion helpers, configfs, and `u_midi2.h` configuration types. It registers as `DECLARE_USB_FUNCTION_INIT(midi2, ...)`. Host integration is through a USB Audio MIDIStreaming interface with alternate settings and class-specific group terminal block descriptors; local user space integrates through ALSA UMP endpoints plus attached legacy rawmidi devices.

## Risks and Test Signals

Risks include static descriptor templates serialized by a global mutex, request bitmap races during mode switches and completions, missed request return on queue failures, MIDI1 pending-buffer truncation when conversion output exceeds the 32-byte temporary buffer, correctness of cable/group mapping for directional blocks, validating class-specific GTB descriptor length against EP0 request size, and UMP Stream protocol switches while traffic is active. The code assumes a contiguous configfs endpoint/block prefix; sparse configfs groups are treated as absent after the first gap.

Strong test signals include descriptor inspection for FS/HS/SS, GET_DESCRIPTOR for group terminal blocks with short and full lengths, switching between altsetting 0 and 1 under traffic, UMP discovery and stream config exchanges, ALSA UMP transmit/receive in MIDI1 and MIDI2 protocols, MIDI1 compatibility conversion for SysEx/running-status/real-time streams, multiple endpoint and block configurations, directional input/output-only blocks, configfs validation failures, and disconnect/unbind while requests are queued.
