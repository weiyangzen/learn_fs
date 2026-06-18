<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_port_io.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_port_io.c

## Purpose
Implements I/O-port register access setup for IPMI SI devices. It assigns `inb/inw/inl` and `outb/outw/outl` accessors, reserves each port window, and records cleanup.

## Important APIs, Types, and Functions
- `ipmi_si_port_setup(struct si_sm_io *io)` is the setup entry point for `IPMI_IO_ADDR_SPACE`.
- `port_inb/outb`, `port_inw/outw`, and `port_inl/outl` apply `regspacing` and `regshift`.
- `port_cleanup()` releases all requested I/O regions.

## Control Flow
Setup rejects address zero, selects accessors for register sizes 1, 2, or 4, requests each register region separately to tolerate firmware that reserved disjoint ports, and installs `port_cleanup()`. Partial reservation failure unwinds already claimed regions.

## State and Persistence
Accessors and cleanup callback are stored in the supplied `si_sm_io`. Region reservations persist until cleanup.

## Dependencies and Integration Points
Used by PCI and platform SI discovery paths for I/O resources and depends on legacy port I/O support. The surrounding code avoids this path when `CONFIG_HAS_IOPORT` is unavailable.

## Risks
Unsupported `regsize` fails. Region arithmetic depends on `io_size`, `regspacing`, and `regsize` being set correctly by the chosen SI state machine. Port access is not memory-barrier-rich beyond the semantics of the port I/O helpers.

## Test Signals
Probe I/O-port KCS/SMIC/BT interfaces with register sizes 1, 2, and 4; force `request_region()` failure mid-loop; confirm unload releases all port windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_port_io.c -->
