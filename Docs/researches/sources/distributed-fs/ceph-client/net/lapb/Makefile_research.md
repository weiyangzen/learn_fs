# sources/distributed-fs/ceph-client/net/lapb/Makefile

## Purpose
The Makefile builds the Linux LAPB layer as a single module/object from the protocol's state-machine components.

## Important APIs, Types, and Functions
`obj-$(CONFIG_LAPB) += lapb.o` ties the object to the Kconfig symbol. `lapb-y` lists `lapb_in.o`, `lapb_out.o`, `lapb_subr.o`, `lapb_timer.o`, and `lapb_iface.o`.

## Control Flow
There is no runtime flow. The object order groups input state-machine handling, output construction, helpers, timers, and exported interface code into one LAPB unit.

## State and Persistence
No state exists in the Makefile. It defines build composition only.

## Dependencies and Integration Points
All listed objects share `struct lapb_cb` and helper declarations from `net/lapb.h`, and the combined object exports LAPB registration/data APIs to network device code.

## Risks and Edge Cases
Omitting any listed object breaks cross-file references in the state machine. Adding objects should preserve protocol initialization and module ownership expectations.

## Test Signals
Build with `CONFIG_LAPB=m` and `CONFIG_LAPB=y` to catch unresolved LAPB symbols and module packaging regressions.
