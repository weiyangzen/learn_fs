# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctsrc.h

## Purpose

This header defines SRC and SRCIMP resource objects, descriptors, operations, states, and manager constructors.

## Important APIs, types, and functions

It defines SRC states (`OFF`, `INIT`, `RUN`), sample formats, `enum SRCMODE`, `struct src`, `struct src_rsc_ops`, `struct src_desc`, `struct src_mgr`, `struct srcimp`, `struct srcimp_rsc_ops`, `struct srcimp_desc`, and `struct srcimp_mgr`. It declares `src_mgr_create/destroy()` and `srcimp_mgr_create/destroy()`.

## Control flow

Callers request resources through manager callback members, then use per-resource ops to configure and commit hardware. SRCIMP users map an input resource to a SRC user and later unmap it.

## State and persistence behavior

The header defines per-resource mode, interleaving, mapped-bit, mapper-list, and locking state. Persistence to hardware is performed through backend callbacks and mapper writes in `ctsrc.c`.

## Dependencies and integration points

It depends on `ctresource.h`, `ctimap.h`, Linux spinlocks/lists, and ALSA core card types. It is consumed by ATC stream setup and routing code.

## Risks and test signals

The manager APIs depend on correct lock usage and resource lifecycle ownership. Compile coverage plus stream setup/teardown tests across playback, capture, and ring modes are the best signals.
