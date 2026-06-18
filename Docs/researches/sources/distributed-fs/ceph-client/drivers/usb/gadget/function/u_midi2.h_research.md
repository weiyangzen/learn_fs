## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_midi2.h

Purpose: declares configuration structures for the USB MIDI 2.0 gadget function, including UMP endpoints and Function Blocks.

Important APIs and types:
- `struct f_midi2_block_info` stores UMP Function Block direction, group ranges, MIDI 1.0 group mapping, UI hint, MIDI-CI version, sysex8 streams, MIDI 1.0 port mode, active flag, and name.
- `struct f_midi2_ep_info` stores endpoint protocol capabilities/default, manufacturer/family/model/software IDs, endpoint name, and product ID.
- `struct f_midi2_card_info` stores card-level processing mode, static-block flag, USB request buffer sizing, request count, and interface name.
- `struct f_midi2_block_opts` and `struct f_midi2_ep_opts` are configfs groups linking blocks to endpoints and endpoints to the root options.
- `struct f_midi2_opts` embeds `usb_function_instance`, lock/refcnt, card info, endpoint count, and up to `MAX_UMP_EPS` endpoint option pointers.
- `MAX_UMP_EPS` is 4 and `MAX_CABLES` is 16.

Control flow and integration:
- Configfs creates endpoint groups and nested block groups, then the MIDI2 function consumes this tree to build descriptors and ALSA UMP interfaces.
- Static Function Blocks can be declared before bind; dynamic processing behavior is controlled by `process_ump`.

State and persistence:
- Nested configfs groups hold all MIDI2 state in memory for the lifetime of the function instance.
- Names are `const char *` pointers expected to be managed by the implementation/configfs layer.

Dependencies:
- USB composite APIs and ALSA UMP constants from `<sound/asound.h>`.

Risks:
- Range fields have protocol-defined bounds documented in comments but not enforced in the header; store paths must validate all values.
- Endpoint/block ownership is pointer-based; removal must avoid stale block pointers in `blks[]`.
- MIDI1 group mapping can overlap invalidly with UMP groups if validation is incomplete.

Test signals:
- Build configfs trees with multiple UMP endpoints and Function Blocks; verify descriptor contents and host MIDI2 enumeration.
- Exercise bounds for group counts, sysex stream counts, manufacturer/model IDs, and static/dynamic blocks.
