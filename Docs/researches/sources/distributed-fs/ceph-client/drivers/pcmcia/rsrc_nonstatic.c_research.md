# sources/distributed-fs/ceph-client/drivers/pcmcia/rsrc_nonstatic.c

Purpose: Implements dynamic PCMCIA resource management for sockets without static mappings. It maintains available I/O and memory interval databases, probes/validates regions, allocates resources, and exposes the resource database through sysfs.

Important APIs and functions: Exports `pccard_nonstatic_ops` with `pcmcia_nonstatic_validate_mem()`, `nonstatic_find_io()`, `nonstatic_find_mem_region()`, `nonstatic_init()`, and `nonstatic_release_resource_db()`. Internal core helpers include `add_interval()`, `sub_interval()`, `claim_region()`, `do_io_probe()`, `readable()`, `checksum()`, `do_validate_mem()`, `do_mem_probe()`, `validate_mem()`, `adjust_io()`, `adjust_memory()`, and `nonstatic_autoadd_resources()`.

Control flow: Init allocates a `socket_data` with circular interval-list sentinels and optionally imports parent PCI bridge windows. Memory validation probes candidate ranges, claims halves, maps CIS memory, calls socket validation callbacks, falls back to checksums, and moves validated intervals into `mem_db_valid`. I/O allocation uses `allocate_resource()` or `pci_bus_alloc_resource()` with custom alignment against `io_db`, then grows existing windows when possible. Sysfs `available_resources_io` and `available_resources_mem` show and adjust intervals using `+`, `-`, or implicit add syntax.

State and persistence: Per-socket resource state lives in `s->resource_data` as `mem_db`, `mem_db_valid`, and `io_db` linked lists. Kernel resource claims persist until released. Sysfs writes mutate the live resource database and can trigger probing.

Dependencies and integration points: Depends on global `ioport_resource`/`iomem_resource`, PCI bridge resources, PCMCIA core callbacks, socket `ops_mutex`, `pccard_nonstatic_ops`, and optional `CONFIG_PCMCIA_PROBE`.

Risks: Region probing can touch legacy I/O or memory ranges and is guarded but inherently platform-sensitive. Interval arithmetic must avoid overflow and ordering mistakes. Sysfs allows privileged users to modify resource windows at runtime. Memory validation unlocks `ops_mutex` around callback validation, so callers rely on PCMCIA core serialization assumptions.

Test signals: Yenta/PD6729 resource setup, sysfs add/remove/show behavior, allocation of aligned I/O windows, memory validation with real CIS and fake CIS cards, PCI bridge autoadd on non-root buses, probe disabled builds, and cleanup freeing all interval nodes.
