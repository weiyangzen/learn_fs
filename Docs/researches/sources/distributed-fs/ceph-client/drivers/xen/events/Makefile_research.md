# sources/distributed-fs/ceph-client/drivers/xen/events/Makefile

## Purpose
This Makefile builds the Xen event-channel core object from base, two-level ABI, and FIFO ABI implementations.

## Important APIs, types, and functions
It declares `obj-y += events.o` and composes `events-y` from `events_base.o`, `events_2l.o`, and `events_fifo.o`.

## Control flow
Kbuild always links the three event-channel implementation objects into the `events.o` composite when the parent Xen events directory is built.

## State and persistence
No runtime state exists in the Makefile; it defines build graph state only.

## Dependencies and integration points
It is reached from `drivers/xen/Makefile` via `obj-y += events/` and provides the event-channel implementation used by the rest of Xen interrupt handling.

## Risks and test signals
Risks include missing an ABI implementation from the composite, stale object names, or unconditional inclusion of objects that no longer build on an architecture. Test signals include Xen builds across x86/ARM/ARM64, FIFO and two-level event-channel runtime selection, and kbuild dependency checks.
