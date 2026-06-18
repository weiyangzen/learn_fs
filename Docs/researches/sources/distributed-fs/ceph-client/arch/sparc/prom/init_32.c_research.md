# sources/distributed-fs/ceph-client/arch/sparc/prom/init_32.c

Purpose: initializes the SPARC32 PROM library from the ROM vector.

Important APIs/state/functions: exports `romvec` and `prom_root_node`; defines `prom_vers`, `prom_rev`, `prom_prev`, `prom_nodeops`, and `prom_init()`.

Control flow: `prom_init()` stores the ROM vector, decodes PROM major version, validates node operations and root node, initializes memory bank data and OBIO ranges, and logs the PROM version. Unsupported PROM versions or invalid essential pointers halt the machine.

State and persistence: global PROM library pointers and version fields persist for the boot lifetime. No filesystem persistence.

Dependencies and integration points: called during early SPARC32 boot before PROM library users. Integrates with `prom_meminit()`, `prom_ranges_init()`, early console, and device-tree traversal code.

Risks: root node and nodeops validation is fatal. Misclassifying PROM version sends later calls through the wrong ROM vector layout.

Test signals: boot PROM V0/V2/V3 systems, verify memory bank discovery, OBIO ranges, early console, and exported `romvec` users.
