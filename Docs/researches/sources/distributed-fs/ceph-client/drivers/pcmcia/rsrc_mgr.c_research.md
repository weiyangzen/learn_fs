# sources/distributed-fs/ceph-client/drivers/pcmcia/rsrc_mgr.c

Purpose: Supplies small resource-management helpers and the static resource-ops implementation for sockets with fixed address mappings.

Important APIs and functions: Exports `pcmcia_make_resource()` and `pccard_static_ops`. `static_init()` marks resource setup done for `SS_CAP_STATIC_MAP` sockets. `static_find_io()` maps a requested base through `s->io_offset`. The ops table leaves memory validation and memory finding NULL because fixed-map socket drivers provide static ranges directly.

Control flow: Static sockets call `static_init()` through the PCMCIA core. For I/O allocation, `static_find_io()` rejects sockets without an `io_offset`, preserves the low 12 bits of the requested base, applies the static offset, returns no parent resource, and reports success.

State and persistence: It only sets `s->resource_setup_done`. `pcmcia_make_resource()` allocates transient `struct resource` objects used by nonstatic and bridge code.

Dependencies and integration points: Depends on PCMCIA socket services and `cs_internal.h`. Used by SoC/static-map drivers such as `soc_common.c` and `xxs1500_ss.c`; `pcmcia_make_resource()` is also used by `rsrc_nonstatic.c`.

Risks: `pcmcia_make_resource(start, end, ...)` treats the second argument as a size, not an absolute end despite the parameter name. Callers must pass a length. Static I/O mapping assumes a 4 KiB window layout.

Test signals: Static-map socket probe, successful I/O port allocation with correct offset, and no resource database setup needed for fixed-map sockets.
