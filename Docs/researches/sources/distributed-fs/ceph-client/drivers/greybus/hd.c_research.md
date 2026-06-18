# sources/distributed-fs/ceph-client/drivers/greybus/hd.c

## Purpose

`hd.c` implements the Greybus host-device abstraction. It allocates bus IDs, owns host-level CPort allocation state, validates host-controller callbacks, creates the associated SVC, registers/unregisters the host device with the Greybus bus, and provides helper callbacks used by connections and transport drivers.

## Important APIs, Types, and Functions

- `gb_hd_create()` allocates `struct gb_host_device` plus driver-private storage, validates mandatory callbacks, clamps buffer size, initializes lists and IDAs, initializes the device, and creates `gb_svc`.
- `gb_hd_add()`, `gb_hd_del()`, `gb_hd_shutdown()`, and `gb_hd_put()` manage registration and lifetime.
- `gb_hd_cport_allocate()`, `gb_hd_cport_release()`, `gb_hd_cport_reserve()`, and `gb_hd_cport_release_reserved()` manage host CPort IDs, optionally delegating to the host driver.
- `gb_hd_output()` invokes optional host-driver vendor/control output.
- `greybus_hd_type` defines the host device type and release function.
- `gb_hd_init()` and `gb_hd_exit()` initialize and destroy the global bus-ID allocator.

## Control Flow

A physical transport driver calls `gb_hd_create()`, fills or uses its private state, then calls `gb_hd_add()`. Adding first registers the host device, then enables SVC via `gb_svc_add()`. Deletion first tears down SVC and flushes hotplug handling, then removes the host device. The release path drops the SVC reference, frees the bus ID, destroys the CPort IDA, and frees the host allocation.

## State and Persistence Behavior

Persistent state includes the global `gb_hd_bus_id_map`, each host's `cport_id_map`, host module and connection lists, maximum buffer size, CPort count, and SVC pointer. The host object embeds transport-private memory sized by `gb_hd_driver::hd_priv_size`.

## Dependencies and Integration Points

This file integrates with `gb_svc_create/add/del`, Greybus bus registration from `core.c`, transport drivers (`es2.c`, `gb-beagleplay.c`), connection allocation, operation message sizing, Linux `ida`, device model, and tracepoints.

## Risks and Edge Cases

- `gb_hd_add()` does not put the host device on failure after `device_add()` beyond `device_del()`, so callers must still drop their reference through normal unwinding.
- CPort allocation says caller guarantees serialization; connection code must honor that when requesting dynamic IDs.
- Host driver callbacks are only partially mandatory; optional callbacks must be checked by their callers or supplied by generic paths.
- `gb_hd_shutdown()` only calls `gb_svc_del()`, relying on later release/removal for full cleanup.

## Test Signals

Validate create failures for missing callbacks, too-small buffers, invalid CPort counts, buffer clamping, global bus ID reuse after release, CPort reserve/allocate/release behavior, SVC creation/add failure handling, host delete ordering, and tracepoint emission.
