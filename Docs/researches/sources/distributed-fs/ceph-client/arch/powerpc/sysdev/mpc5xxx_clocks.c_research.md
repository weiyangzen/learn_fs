<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpc5xxx_clocks.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpc5xxx_clocks.c

Purpose: Provides a firmware-node helper to locate MPC5xxx bus frequency properties.

Important APIs/types/functions: Exports `mpc5xxx_fwnode_get_bus_frequency()`.

Control flow: The helper first checks the supplied firmware node for `bus-frequency`; if absent, it walks parents until the property is found, releases the parent reference, and returns zero if no value exists.

State and persistence: No persistent state; all work is per-call firmware property lookup.

Dependencies and integration points: Uses generic firmware node property APIs and is exported for MPC512x/MPC52xx drivers that need IPS/IPB bus frequency.

Risks: It returns `0` on failure, so callers must treat zero as invalid. Parent traversal depends on correct firmware-node reference handling, which this function does with `fwnode_handle_put()` on early return.

Test signals: Drivers probing with local and inherited `bus-frequency`, absent property cases, and non-OF fwnode compatibility.

Source read size: 36 lines, 854 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpc5xxx_clocks.c -->
