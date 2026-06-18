# sources/distributed-fs/ceph-client/arch/sparc/prom/tree_32.c

Purpose: implements SPARC32 PROM device-tree traversal, property access, path lookup, property setting, and instance-to-package conversion through ROM vector node operations.

Important APIs/functions: exports `prom_getchild()`, `prom_getsibling()`, `prom_getproplen()`, `prom_getproperty()`, `prom_getint()`, `prom_getintdefault()`, `prom_getbool()`, `prom_getstring()`, `prom_searchsiblings()`, `prom_nextprop()`, `prom_finddevice()`, `prom_setprop()`, and `prom_inst2pkg()`.

Control flow: public node/property routines validate handles, take `prom_lock`, call the appropriate `prom_nodeops` or ROM vector function, call `restore_current()`, and normalize PROM `-1` handles to zero. `prom_finddevice()` parses path components and optional `@bus,addr` selectors, scanning siblings by name and matching `reg` properties.

State and persistence: uses a static 128-byte scratch buffer for sibling name search. PROM property changes through `prom_setprop()` persist in firmware-visible runtime state, not disk.

Dependencies and integration points: core dependency for SPARC32 boot, memory/ranges init, device discovery, IDPROM reads, and module users of PROM tree exports.

Risks: static buffer and path parser assume small node names. PROM calls are serialized but can be slow. `prom_nextprop()` ignores its output buffer argument and returns firmware storage, so callers must match historical expectations.

Test signals: traverse root/child/sibling trees, read integer/string/bool properties, find devices with and without unit addresses, set properties, convert instances, and handle invalid nodes.
