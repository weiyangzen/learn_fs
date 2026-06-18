# sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_proto.h

## Purpose

`gpib_proto.h` declares gpib-common core entry points used by character-device file operations, board lifecycle helpers, timer management, descriptor initialization, and user-visible GPIB operations.

## Important APIs and Functions

- File operations: `ibopen()`, `ibclose()`, and `ibioctl()`.
- Timer helpers: `os_start_timer()`, `os_remove_timer()`, and `usec_to_jiffies()`.
- Board/descriptor setup: `init_gpib_board()` and `init_gpib_descriptor()`.
- Bus operations: `ibcac()`, `ibcmd()`, `ibgts()`, `ibonline()`, `iboffline()`, `iblines()`, `ibrd()`, `ibrpp()`, `ibrsv2()`, `ibrsc()`, `ibsic()`, `ibsre()`, `ibpad()`, `ibsad()`, `ibeos()`, `ibwait()`, `ibwrt()`, `ibstatus()`, `general_ibstatus()`, `io_timed_out()`, and `ibppc()`.
- Serial polling: `serial_poll_all()` and `dvrsp()`.

## Control Flow and Integration

Board drivers do not implement these declarations; they call into or are called by the gpib core through `struct gpib_interface`. The core uses interface callbacks to satisfy these operations and update `board->status`.

## State and Persistence Behavior

The prototypes operate on `struct gpib_board`, `struct gpib_descriptor`, and status queues defined in `gpib_types.h`. Timer state is persisted in `board->timer` for active operations.

## Dependencies

The file includes `linux/fs.h` for inode/file types and relies on GPIB public constants from headers pulled in by users of `gpibP.h`.

## Risks and Test Signals

`usec_to_jiffies()` rounds up and adds one jiffy, which affects timeout behavior. Test signals include ioctl conformance, timeout paths, online/offline transitions, address changes, EOS mode, serial poll, parallel poll, and wait-mask behavior across drivers.
