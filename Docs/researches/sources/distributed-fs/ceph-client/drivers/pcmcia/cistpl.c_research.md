# sources/distributed-fs/ceph-client/drivers/pcmcia/cistpl.c

Purpose: Implements low-level and high-level parsing of 16-bit PCMCIA Card Information Structure tuples. It maps CIS memory, caches tuple reads, supports fake CIS replacement, follows long-link and multifunction chains, parses individual tuple formats, validates CIS sanity, and exposes a socket `cis` binary sysfs attribute.

Important APIs and functions: Exported/internal entry points include `pcmcia_read_cis_mem()`, `pcmcia_write_cis_mem()`, `release_cis_mem()`, `destroy_cis_cache()`, `verify_cis_cache()`, `pcmcia_replace_cis()`, `pccard_get_first_tuple()`, `pccard_get_next_tuple()`, `pccard_get_tuple_data()`, `pcmcia_parse_tuple()`, and `pccard_validate_cis()`. `pccard_cis_attr` exposes read/write sysfs access.

Control flow: CIS reads map either attribute/common space or indirect CIS registers, respecting `cis_width` and socket map size. `read_cis_cache()` serves fake CIS data first, then exact cache hits, then reads hardware and records cache entries. Tuple iteration starts with an assumed common long link, follows link tuples and MFC links using `follow_link()`, skips NULL tuples, bounds traversal by `MAX_TUPLES`, and returns requested tuple data. Parsing dispatches by tuple code to routines for device, checksum, longlink, strings, MANFID, FUNCID/FUNCE, config, power, timing, IO, memory, IRQ, geometry, version, organization, and format tuples.

State and persistence: State lives on `struct pcmcia_socket`: `cis_mem`, `cis_virt`, `cis_cache`, `fake_cis`, `fake_cis_len`, `functions`, and socket flags. Fake CIS persists only while the socket/card state lives; hardware CIS is card ROM/attribute memory. The `cis_width` module parameter changes access width behavior.

Dependencies and integration points: Used by `ds.c`, `pcmcia_cis.c`, and `pcmcia_resource.c` to identify devices, choose configurations, and access configuration registers. It depends on socket `set_mem_map`, PCMCIA resource allocation, Linux I/O mapping, unaligned helpers, and lockdown security for sysfs CIS writes.

Risks: CIS parsing is inherently hostile-input parsing from removable hardware. Bounds checks, tuple count limits, and cache invalidation are critical. Long-link fallback handles common bad offsets but can mask malformed cards. Writable CIS override is powerful and therefore guarded by `security_locked_down(LOCKDOWN_PCMCIA_CIS)`. Mapping lifetime must be balanced to avoid stale `cis_virt` access.

Test signals: Validate known good and malformed CIS images, multi-function cards, fake CIS loading through firmware/sysfs, suspend/resume cache verification, tuple extraction from `/sys/class/pcmcia_socket/.../cis`, and lockdep around `ops_mutex`.
