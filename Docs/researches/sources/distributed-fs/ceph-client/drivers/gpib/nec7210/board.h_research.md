# sources/distributed-fs/ceph-client/drivers/gpib/nec7210/board.h

## Purpose

`board.h` is a local umbrella header for `nec7210.c`. It imports gpib private APIs, Linux I/O/module/scheduler/delay helpers, and the public NEC7210 controller declaration.

## Important APIs and Types

The file defines no new APIs. It includes `gpibP.h`, `linux/io.h`, `linux/module.h`, `linux/sched.h`, `linux/delay.h`, and `nec7210.h`.

## Control Flow and Integration

There is no control flow. It simplifies includes for the NEC7210 implementation.

## State and Persistence Behavior

No state is declared.

## Dependencies

It is kernel-only and depends on linux-gpib private headers plus standard kernel headers needed by `nec7210.c`.

## Risks and Test Signals

As an umbrella header, risks are mostly include-order and dependency creep. Test signals are successful compilation of `nec7210.c` across configurations with and without I/O-port support.
