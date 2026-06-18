# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsgx.c

## Purpose
This file implements the extended HPI message dispatcher, adapter entry-point lookup, cached open responses, and per-owner stream open tracking.

## Important APIs, Types, And Functions
The exported entry is `hpi_send_recv_ex()`. Important internals include `hpi_lookup_entry_point_function()`, `hw_entry_point()`, `subsys_message()`, object-specific routers, `adapter_prepare()`, `HPIMSGX__init()`, `HPIMSGX__reset()`, and `HPIMSGX__cleanup()`. Static caches include adapter, mixer, ostream, and istream open responses plus `asi_open_state` arrays guarded by `msgx_lock`.

## Control Flow
`hpi_send_recv_ex()` validates request type and adapter index, logs messages, then switches by HPI object. Subsystem load initializes locks, entry points, and cached failure responses. Create-adapter finds a handler from the PCI ID table, calls it, stores the handler by adapter index, and pre-opens adapter, streams, and mixer to cache open responses. User stream open checks cached errors and ownership, resets the stream in hardware, then records owner. Close validates owner, resets hardware, and clears the open slot. Cleanup closes streams owned by a file or all adapters during subsystem close/unload.

## State, Persistence, And Dependencies
The dispatcher persists adapter handler mappings, cached open responses, adapter stream counts, and per-owner open flags until delete/unload/reset. It depends on `hpipcida.h`, `hpicmn.h`, HPI common subsystem handling, HPI debug, and OS spinlock wrappers from `hpios.h`.

## Integration Points
It is the lower layer behind `hpi_send_recv()` and the ioctl path. Hardware-specific HPI handlers are selected through PCI `driver_data` and reached by `hw_entry_point()`.

## Risks
Most state is global and indexed by adapter and stream bounds, so probe/remove races or bad adapter counts could corrupt behavior. `HPIMSGX__cleanup()` returns early for NULL owners, which is intentional for kernel owner handling but means ownerless cleanup does nothing. Logging disables itself after DSP communication errors, hiding later traces. Cached open responses can become stale if hardware state changes outside the expected lifecycle.

## Test Signals
Probe/create/delete, subsystem load/unload, repeated stream open/close from the same and different file owners, invalid object index handling, and forced DSP errors should show correct cache, lock, cleanup, and logging behavior.
