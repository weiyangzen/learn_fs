<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ps2mult.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/ps2mult.c

## Purpose
`ps2mult.c` is a serio driver for the TQC PS/2 multiplexer protocol. It attaches to a parent RS232/PS2MULT serio link and creates two child PS/2 serio ports for keyboard and mouse traffic.

## Important APIs, types, and functions
- Protocol control bytes include keyboard selector, mouse selector, escape, byte-sync, session start, and session end.
- `struct ps2mult_port` stores each child serio, selector byte, and registration state.
- `struct ps2mult` stores the parent serio, two child ports, spinlock, current input/output port, and escape state.
- `ps2mult_select_port()` writes a selector to the parent and records the selected output port.
- `ps2mult_serio_write()` switches output port if needed, escapes protocol control bytes in payload, and writes to the parent.
- Child `start`/`stop` callbacks mark the child as registered for interrupt delivery.
- `ps2mult_reset()` sends session end/start and selects the keyboard port.
- `ps2mult_connect()` opens the parent serio, creates and registers child ports, and resets the session.
- `ps2mult_interrupt()` parses incoming control bytes, updates input port and escape state, and forwards payload to the selected registered child.

## Control flow
The driver binds to parent serio devices of type `SERIO_RS232` and protocol `SERIO_PS2MULT`. Connect requires a parent write method, allocates state, creates keyboard and mouse child ports, opens the parent, resets the multiplexer session, and registers the children. Outbound writes from a child select that child and escape control bytes. Inbound bytes from the parent either control session/input selection or are forwarded to the current child. Disconnect sends session end, closes the parent, frees state, and clears driver data; serio core handles children.

## State and persistence
State is runtime-only: selected input/output port, escape latch, and child registration flags. Reset reinitializes the external multiplexer session but no settings are persisted.

## Dependencies and integration points
It depends on the serio core both as a serio driver for the parent and as a creator of child serio ports. It integrates a simple byte-stuffed multiplexer protocol with standard PS/2 child drivers.

## Risks
- Parent write failures are ignored in selector and payload writes.
- Input routing depends on protocol synchronization; lost selector or escape bytes can misroute data until BSYNC or reset.
- Disconnect relies on serio core child cleanup and only frees the parent `ps2mult` state.
- `registered` flags avoid delivery to stopped children but do not buffer data.

## Test signals
- Bind tests should cover parent without write support, allocation failure, parent open failure, and reconnect reset.
- Protocol tests should cover escaped control bytes in payload, BSYNC behavior, selector switching, session start/end bytes, child start/stop delivery suppression, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ps2mult.c -->
