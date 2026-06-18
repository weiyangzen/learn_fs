<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/parkbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/parkbd.c

## Purpose
`parkbd.c` is a parallel-port adapter driver for connecting AT or XT keyboards through a simple passive adapter. It bit-bangs keyboard clock/data lines via parport control/status bits and exposes the result as one serio port.

## Important APIs, types, and functions
- Module parameters select `port` and `mode` (`SERIO_8042` AT by default, XT when zero).
- Global state tracks the current bit buffer, bit counter, last interrupt jiffies, write mode, start time, claimed parport device, and serio port.
- `parkbd_readlines()` reads keyboard clock/data from parport status bits; `parkbd_writelines()` drives output through parport control bits.
- `parkbd_write()` builds an AT keyboard host-to-device frame with parity and starts write mode; XT mode rejects writes.
- `parkbd_interrupt()` advances either transmit bits or receive bits on parport IRQ callbacks, handles timeouts, and delivers completed bytes through `serio_interrupt()`.
- `parkbd_getport()` registers and exclusively claims the selected parport.
- `parkbd_attach()` claims the configured parport, allocates the serio port, initializes line state, and registers the port. `parkbd_detach()` releases resources.

## Control flow
The parport driver calls `parkbd_attach()` for each discovered parallel port. Only the configured parport number is used. After exclusive claim, the driver creates a serio port whose type is the selected AT/XT mode and uses the parport IRQ callback for bit timing. Detach releases the parport, unregisters the serio port, unregisters the parport device, and clears the global port pointer.

## State and persistence
All state is global because the driver supports one selected adapter. It stores transient bit-level receive/transmit state and timing in jiffies. No persistent settings are saved beyond module parameters for the current load.

## Dependencies and integration points
The file depends on the parport subsystem, IRQ callbacks from parport, serio core, jiffies timing, and a specific external passive wiring adapter.

## Risks
- Bit-banging depends on interrupt timing and adapter wiring; missed IRQs reset the frame after `HZ/100`.
- Global state means only one adapter is supported and concurrency assumptions are simple.
- AT write mode is minimal and has no explicit ACK handling in this driver.
- Incorrect `mode` can decode the wrong frame length or shift.
- The driver exclusively claims the parallel port, which can conflict with printer or other parport users.

## Test signals
- Build with parport and serio support.
- Hardware tests should cover selected vs non-selected parports, AT and XT receive frame decoding, AT writes, timeout/reset behavior, detach cleanup, and parallel-port claim failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/parkbd.c -->
