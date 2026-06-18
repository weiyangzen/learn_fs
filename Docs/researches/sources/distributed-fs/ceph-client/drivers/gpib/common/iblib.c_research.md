# sources/distributed-fs/ceph-client/drivers/gpib/common/iblib.c

Purpose: implements the reusable IEEE-488/GPIB operation layer used by the ioctl core. It translates high-level operations such as command, read, write, wait, serial poll, interface clear, remote enable, address changes, EOS, and status queries into adapter `gpib_interface` callbacks.

Important APIs and functions: `ibcac`, `ibcmd`, `ibgts`, `ibonline`, `iboffline`, `iblines`, `ibrd`, `ibrpp`, `ibppc`, `ibrsv2`, `ibsic`, `ibrsc`, `ibsre`, `ibpad`, `ibsad`, `ibeos`, `ibstatus`, `general_ibstatus`, `ibwait`, and `ibwrt`. Internal helpers include `check_for_command_acceptors`, the autospoll kthread, wait timer helpers, and status wait predicates.

Control flow: command operations require controller-in-charge, start the board timeout, take control, optionally check for NRFD/NDAC command acceptors via `line_status`, then call the adapter command callback. Reads and writes place the controller in standby when master, start timeouts, and loop through adapter read/write callbacks until length, END, or error. Online allocates the board buffer, calls adapter attach, starts autospoll, and marks the board online; offline stops autospoll, detaches, and deallocates buffers/events.

State and persistence: updates `board->status`, `board->master`, `board->pad`, `board->sad`, `board->parallel_poll_configuration`, `board->t1_nano_sec`, descriptor `io_in_progress`, and autospoll fields. Timers drive `TIMO`; events and status queues are maintained in `gpib_os.c`. No state persists after module unload.

Dependencies and integration: tightly coupled to `struct gpib_interface` callbacks, `gpib_board` fields from `gpib_types.h`, GPIB command constants, `gpib_os.c` timers/status queues, and adapter status-line implementations. It is linked into `gpib_common.o`.

Risks: `ibrpp()` returns early on `ibcac()` failure without removing the timeout timer. Read/write timeout semantics can be extended by repeated chunking in ioctl loops, as noted by an in-code comment. `serial_poll_single()` returns the original retval when cleanup fails, losing cleanup errors if the poll itself succeeded. Autospoll treats nonpositive poll results as stuck SRQ. `check_for_command_acceptors` depends on accurate line-status support and may be skipped by adapters.

Test signals: validate controller state transitions, sync/async take-control fallback, no-listener command detection, read/write timeout and END/EOS behavior, `IBWAIT` clear/set masks, autospoll thread behavior on SRQ and stuck SRQ, online/offline attach failure unwinding, address limits, T1 delay propagation, and unsupported adapter callbacks returning expected errors.
