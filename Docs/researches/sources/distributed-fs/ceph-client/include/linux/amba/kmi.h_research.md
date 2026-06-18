<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/kmi.h -->
# sources/distributed-fs/ceph-client/include/linux/amba/kmi.h

## Purpose
`amba/kmi.h` defines register offsets and bit meanings for the ARM PrimeCell PL050 keyboard/mouse interface.

## Important APIs, types, and functions
Macros define control, status, data, clock divisor, interrupt register offsets, individual control/status/interrupt bits, and `KMI_SIZE`. Register macros are relative to `KMI_BASE`, expected to be defined by the including driver/platform code.

## Control flow
Drivers program control bits to enable KMI and interrupts, read status to determine TX/RX/busy/parity/line levels, access `KMIDATA`, set clock divisor, and service interrupt bits.

## State and persistence behavior
No kernel state is stored. Hardware registers hold device state.

## Dependencies and integration points
It integrates AMBA PL050 input drivers with low-level register programming.

## Risks and test signals
Risks include missing or wrong `KMI_BASE`, bit misprogramming that forces clock/data lines, and interrupt enable/status confusion. Test signals include PL050 keyboard/mouse probe, RX/TX interrupt handling, clock divisor validation, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/kmi.h -->
