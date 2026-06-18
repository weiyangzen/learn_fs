# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc5xxx.h

Purpose: exposes a common MPC5xxx bus-frequency lookup helper for firmware-node and device users.

Important APIs/types/functions: `mpc5xxx_fwnode_get_bus_frequency(struct fwnode_handle *fwnode)` is declared; `mpc5xxx_get_bus_frequency(struct device *dev)` passes `dev_fwnode(dev)` to it.

Control flow: drivers call the device helper, which delegates to firmware-node parsing.

State and persistence: no state; frequency comes from firmware properties or platform implementation.

Dependencies and integration points: depends on Linux property/fwnode APIs and integrates MPC5xxx platform clocks with drivers.

Risks: missing or malformed firmware properties can yield incorrect bus rates and misprogram devices.

Test signals: device tree/fwnode bus-frequency parsing tests, driver probe on MPC5xxx boards, and clock-dependent UART/PSC timing validation.
