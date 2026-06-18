# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-packets.c

Purpose: Shared I-Force packet transmit queueing and inbound packet decoding for position, wheel, and FF status reports.

Important APIs/types/functions: `iforce_send_packet()` queues command ID, length, and data into the circular transmit buffer under spinlock, then starts transport transmission. `iforce_control_playback()` sends FF play/stop commands. `iforce_process_packet()` decodes inbound packet IDs. `iforce_report_hats_buttons()` maps packed hat/button bytes. `mark_core_as_ready()` clears effect update flags when status packets reference modifier memory addresses.

Control flow: Force-feedback and control paths call `iforce_send_packet()`, which appends to the ring and invokes `xport_ops->xmit()` when the ring was empty. Transport IRQ/completion paths call `iforce_process_packet()`. Packet ID 0x01 reports joystick axes/throttle/rudder/buttons, 0x03 reports wheel/gas/brake/buttons, and 0x02 reports FF status and effect update completion.

State and persistence: Uses `iforce->xmit` circular buffer, `xmit_flags`, per-effect flags, and input state. No persistence outside device lifetime.

Dependencies and integration points: Shared with both USB and serio transports via exported symbols; depends on input reporting APIs, wait queue wakeups from transport, and iforce device type maps.

Risks: `iforce_send_packet()` returns `-1` for buffer full rather than standard errno. Callers must ensure data length matches `LO(cmd)`. Status packet handling indexes `core_effects[i]` from packet data without visible bounds check on `i`, so malformed device data deserves scrutiny. Hat table has 16 entries but only first 8 initialized meaning invalid hat nibbles become zeroed axes.

Test signals: Transmit ring wraparound and full-buffer handling; packet IDs 0x01/0x02/0x03 with short and full lengths; FF status play/stop events; modifier-ready address matching; wakeups after transport completion.
