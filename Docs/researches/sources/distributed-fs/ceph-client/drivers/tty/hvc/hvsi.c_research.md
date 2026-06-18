# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvsi.c

## Purpose
`hvsi.c` is the standalone Host Virtual Serial Interface tty driver for IBM pSeries service-processor serial ports. It predates or coexists with the generic HVC HVSI library path and implements its own tty major/minor range, packet parser, handshake state machine, IRQ handling, modem-control operations, and console support.

## Important APIs, Types, and Functions
`struct hvsi_struct` stores tty-port state, writer/handshaker work, waitqueues, lock, buffers, vterm/IRQ, packet sequence number, modem control, protocol state, flags, and optional SysRq state. Protocol states are `HVSI_CLOSED`, `HVSI_WAIT_FOR_VER_RESPONSE`, `HVSI_WAIT_FOR_VER_QUERY`, `HVSI_OPEN`, `HVSI_WAIT_FOR_MCTRL_RESPONSE`, and `HVSI_FSP_DIED`.

Key parser functions are `hvsi_load_chunk()`, `hvsi_recv_control()`, `hvsi_recv_response()`, `hvsi_recv_query()`, and `hvsi_recv_data()`. Connection functions are `hvsi_handshake()`, `hvsi_query()`, `hvsi_get_mctrl()`, `hvsi_set_mctrl()`, and `hvsi_close_protocol()`. TTY ops include `hvsi_open()`, `hvsi_close()`, `hvsi_write()`, `hvsi_hangup()`, throttle/unthrottle, and tiocm get/set.

## Control Flow
Console init scans the device tree for `hvterm-protocol` serial nodes, initializes `hvsi_ports[]`, maps IRQs, and registers the `hvsi` console if any are found. Console setup handshakes with the service processor, reads modem status, asserts DTR, and marks the port as console. Device init allocates and registers the `hvsi` tty driver and requests IRQs for discovered ports.

IRQ handling repeatedly reads chunks via `hvc_get_chars()`, parses complete HVSI packets, pushes tty data, schedules re-handshake when a close protocol packet arrives, and delivers throttled overflow when possible. Opens enable VIO IRQs, handshake non-console ports, query modem control, and assert DTR. Writes pack up to 12 bytes into HVSI data packets and use delayed work to retry when firmware does not accept data.

## State and Persistence Behavior
All state is static/in-memory in `hvsi_ports[]`, `hvsi_driver`, `hvsi_count`, and per-port buffers and state fields. `hvsi_wait` switches from polling during console init to waitqueue-based waiting after IRQs are active.

## Dependencies and Integration Points
The driver integrates directly with tty, console, Open Firmware IRQ mapping, PowerPC VIO signaling, hypervisor console calls, HVSI packet definitions from `asm/hvsi.h`, workqueues, waitqueues, and Magic SysRq.

## Risks and Edge Cases
The packet parser must resynchronize on malformed data and compact partial packets. `hvsi_drain_input()` appears to use a time comparison that should be reviewed carefully because it controls stale packet discard. Carrier loss can hang up non-local ttys. Throttle overflow buffering is explicitly uncertain in the comments. Console ports remain open and are treated differently during close and service-processor reset.

## Test Signals
Signals include device-tree discovery, successful console handshake, version query/response transitions, modem-control query and DTR set, IRQ packet parsing, FSP close/re-handshake, delayed write retries, carrier-drop hangup, throttle/unthrottle overflow delivery, and tty registration on major 229 minor 128.
