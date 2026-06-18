# sources/distributed-fs/ceph-client/arch/sparc/prom/init_64.c

Purpose: initializes the SPARC64 IEEE-1275 PROM library.

Important APIs/state/functions: defines `prom_version[80]`, `prom_stdout`, `prom_chosen_node`, `prom_init()`, and `prom_init_report()`.

Control flow: `prom_init()` installs the CIF handler, finds `/chosen`, reads stdout instance handle, finds `/openprom`, reads the firmware version string, and emits an initial PROM newline. `prom_init_report()` later logs the PROM version and root compatibility.

State and persistence: caches `/chosen`, stdout handle, and firmware version for boot lifetime.

Dependencies and integration points: depends on P1275 CIF initialization, PROM path constants, device-tree property access, early console, and root compatibility discovery elsewhere.

Risks: failure to find `/chosen` or `/openprom` halts the machine. `prom_stdout` must be valid before console writes.

Test signals: sparc64 boot on physical and sun4v firmware, early console output, `/chosen` stdout parsing, and report logging.
