<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hyperv-keyboard.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/hyperv-keyboard.c

## Purpose
`hyperv-keyboard.c` exposes the Microsoft Hyper-V synthetic keyboard device as a Linux serio port. It negotiates the Hyper-V keyboard protocol over VMBus, receives host keystroke messages, converts them into XT keyboard scancode bytes, and feeds them to upper-layer keyboard drivers through serio.

## Important APIs, types, and functions
- Synthetic protocol types include `enum synth_kbd_msg_type`, `struct synth_kbd_protocol_request`, `struct synth_kbd_protocol_response`, and `struct synth_kbd_keystroke`.
- `struct hv_kbd_dev` stores the Hyper-V device, serio port, protocol request/response buffers, negotiation completion, and a spinlock-protected `started` flag.
- `hv_kbd_connect_to_vsp()` sends a protocol version request and waits up to 10 seconds for an accepted response.
- `hv_kbd_on_channel_callback()` iterates VMBus packets and dispatches them through `hv_kbd_handle_received_packet()`.
- `hv_kbd_on_receive()` validates message lengths, completes protocol negotiation responses, converts `IS_E0`, `IS_E1`, and `IS_BREAK` keystroke flags to XT prefixes/release bits, and calls `serio_interrupt()`.
- `hv_kbd_start()` and `hv_kbd_stop()` toggle whether incoming events are delivered to the serio port.
- `hv_kbd_probe()`, `hv_kbd_remove()`, `hv_kbd_suspend()`, and `hv_kbd_resume()` manage VMBus channel and serio lifetimes.

## Control flow
Probe allocates `hv_kbd_dev` and a `SERIO_8042_XL` serio port, stores driver data on the Hyper-V device, opens the VMBus channel with keyboard ring sizes, negotiates protocol version 1.0, registers the serio port, and enables device wakeup.

The VMBus callback receives packet descriptors. In-band packets with valid payload size are interpreted as synthetic keyboard messages. Protocol responses are copied and complete the negotiation wait. Keyboard events are delivered only while the serio port is started; the driver emits optional E0/E1 prefix bytes, then the make code with the release bit set for break events. Key-down events trigger a hard wakeup event so the keyboard can wake the guest.

Suspend closes the VMBus channel. Resume reopens the channel and renegotiates the protocol. Remove unregisters the serio port, closes the channel, frees driver state, and clears Hyper-V driver data.

## State and persistence
The only persistent runtime state is the negotiated VMBus channel, protocol response buffer, and `started` delivery flag. No key state is cached. The host is the source of keyboard events, and settings are not persisted by the driver.

## Dependencies and integration points
The driver integrates with the Hyper-V VMBus driver model using `HV_KBD_GUID`, VMBus ring buffers, completion waits, Linux power-management wakeup helpers, and the serio keyboard stack. It intentionally presents the device as an 8042-compatible translated keyboard stream.

## Risks
- The host controls message contents. The driver validates minimal lengths but otherwise trusts message semantics.
- Events arriving before `hv_kbd_start()` or after `hv_kbd_stop()` are dropped under the spinlock.
- VMBus close on suspend discards pending packets; resume depends on successful re-negotiation.
- The conversion handles E0/E1 prefixes and the release bit but does not support Unicode event payloads despite the protocol flag existing.
- Probe failure cleanup must free both allocated objects and close the channel in the right order.

## Test signals
- Build with Hyper-V input support and verify the VMBus device ID table exports `HV_KBD_GUID`.
- Guest tests should cover protocol acceptance, protocol rejection, negotiation timeout, malformed short packets, normal make/break keys, E0/E1-prefixed keys, wakeup on key-down only, suspend/resume, and remove during active input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hyperv-keyboard.c -->
