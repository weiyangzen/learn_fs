# sources/distributed-fs/ceph-client/arch/sparc/prom/tree_64.c

Purpose: implements SPARC64 IEEE-1275 device-tree traversal, property access, property enumeration, path lookup, property setting, and ihandle conversion.

Important APIs/functions: exports `prom_getchild()`, `prom_getparent()`, `prom_getsibling()`, `prom_getproplen()`, `prom_getproperty()`, `prom_getint()`, `prom_getintdefault()`, `prom_getbool()`, `prom_getstring()`, `prom_nodematch()`, `prom_searchsiblings()`, `prom_firstprop()`, `prom_nextprop()`, `prom_finddevice()`, `prom_node_has_property()`, `prom_setprop()`, `prom_inst2pkg()`, and `prom_ihandle2path()`.

Control flow: traversal wrappers build P1275 argument arrays for `child`, `parent`, and peer services. Property routines preflight lengths, call `getprop` or `nextprop`, and normalize `-1` handles. `prom_setprop()` delegates to LDOM variable setting when domaining is enabled; otherwise it calls P1275 `setprop`.

State and persistence: no owned tree copy; every operation queries firmware. Property writes can change firmware/LDOM runtime variables.

Dependencies and integration points: all SPARC64 boot and device discovery code depends on these wrappers. Integrates with LDOM services, `p1275_cmd_direct()`, and Open Firmware naming conventions.

Risks: P1275 argument slots are ABI-sensitive. `prom_nextprop()` must copy `oprop` when input and output buffers alias. LDOM setprop behavior intentionally bypasses firmware.

Test signals: enumerate properties, find devices, get/set properties under LDOM and non-LDOM, invalid handle handling, ihandle-to-path conversion, and sibling traversal across large firmware trees.
