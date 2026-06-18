# sources/distributed-fs/ceph-client/include/uapi/linux/synclink.h

## Purpose
Exports the SyncLink multiprotocol serial adapter private ABI for configuring asynchronous, HDLC, monosync, bisync, raw, base-clock, and extended sync modes.

## Important APIs, Types, and Constants
Defines generic bit constants, frame and buffer limits, async parity modes, HDLC flags, CRC modes, idle modes, encodings, preamble settings, device IDs, diagnostics, serial signal bits, and event flags. `MGSL_PARAMS` carries common, HDLC, and async configuration. `struct mgsl_icount` reports modem, TX/RX, and error counters. `struct gpio_desc` controls GPIO state, direction, and wait masks. Private ioctls include `MGSL_IOCSPARAMS`, `MGSL_IOCGPARAMS`, `MGSL_IOCSTXIDLE`, `MGSL_IOCGTXIDLE`, `MGSL_IOCTXENABLE`, `MGSL_IOCRXENABLE`, `MGSL_IOCTXABORT`, `MGSL_IOCGSTATS`, `MGSL_IOCWAITEVENT`, GPIO controls, and XSYNC/XCTRL controls.

## Control Flow, State, and Persistence
Userspace configures line mode and protocol parameters, enables TX/RX, waits for modem/GPIO events, and reads statistics. Driver state includes mode, clocks, line interface, GPIO direction/state, counters, and transmit/receive queues.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and ioctl macros. Integrates with Microgate SyncLink serial drivers and specialized WAN/industrial serial applications.

## Risks and Test Signals
Risks include `unsigned long` ABI differences across 32/64-bit builds, private ioctl compatibility, unsafe mode transitions while active, and event wait races. Test compat ioctls, every mode transition, HDLC CRC/encoding combinations, GPIO wait behavior, counter rollover, and invalid interface values.
