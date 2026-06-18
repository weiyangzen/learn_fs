# sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_tty.c

## Purpose

`jsm_tty.c` is the TTY/serial-core adapter for Digi JSM PCI multiport serial boards. It turns board/channel objects from the wider `jsm` driver into `struct uart_port` instances, translates Linux termios/modem-control operations into board-specific `bd_ops`, and moves received channel ring-buffer data into the TTY flip buffer.

## Important APIs, Types, and Functions

The public entry points used by the rest of the JSM driver are `jsm_tty_init()`, `jsm_uart_port_init()`, `jsm_remove_uart_port()`, `jsm_input()`, and `jsm_check_queue_flow_control()`. The `jsm_ops` `struct uart_ops` supplies serial-core methods including `startup`, `shutdown`, `set_termios`, `start_tx`, `stop_tx`, `stop_rx`, `send_xchar`, `break_ctl`, `get_mctrl`, and `set_mctrl`. Internal helpers include `jsm_get_mstat()` for TIOCM mapping, `jsm_tty_write()` for board TX draining, and `jsm_carrier()` for physical/virtual carrier state.

## Control Flow

Board initialization calls `jsm_tty_init()` to allocate and initialize per-channel `struct jsm_channel` objects, map UART register offsets, and set wait queues. `jsm_uart_port_init()` then assigns serial-core fields, allocates a line number from the static `linemap`, and calls `uart_add_one_port()`. Open/startup allocates channel read/error queues, flushes hardware queues through `bd_ops`, snapshots termios characters, initializes the UART, applies parameters, and evaluates carrier. TX is delegated to `bd_ops->copy_data_from_queue_to_uart()`, while RX enters through `jsm_input()`, which consumes channel ring buffers under `ch_lock`, annotates parity/frame/break errors, pushes flip data, and applies queue flow control.

## State and Persistence Behavior

Persistent runtime state is held in `struct jsm_channel`: read/error queues, ring indices, cached termios flags, start/stop chars, modem status, open count, cached LSR, and flow-control flags such as `CH_STOP`, `CH_STOPI`, `CH_RECEIVER_OFF`, `CH_CD`, and `CH_FCAR`. The static `linemap` persists line allocation across boards until `jsm_remove_uart_port()` clears bits. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on Linux TTY, tty flip buffers, serial core, PCI device ownership, and JSM-private `struct jsm_board`, `struct jsm_channel`, and `board_ops`. Hardware operations are abstracted through `bd_ops`, so this file integrates with board-specific UART implementations rather than directly programming every register.

## Risks and Edge Cases

Allocation failure in open can leave one queue allocated while the second fails. `jsm_input()` assumes `uart_port.state` exists when input is processed. Flow control is queue-depth based and can repeatedly send software stop characters up to `MAX_STOPS_SENT`. Carrier handling updates cached flags but leaves hangup policy mostly to surrounding serial/TTY behavior. `jsm_uart_port_init()` returns immediately on `uart_add_one_port()` failure without undoing earlier ports added in the same loop.

## Test Signals

Useful signals are multiport probe/remove with line reuse, open/close with HUPCL modem drop, termios changes for IXOFF/CRTSCTS, RX parity/frame/break annotation into the flip buffer, queue high/low-water flow-control transitions, and fault injection for queue allocation and `uart_add_one_port()` failures.
