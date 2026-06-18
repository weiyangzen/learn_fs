
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/rgmii.h

## Purpose
`rgmii.h` declares the RGMII bridge register/state structures and public API used by EMAC core code, with stubbed no-op or error macros when RGMII support is not compiled.

## Important APIs, Types, and Functions
`struct rgmii_regs` maps the bridge function-enable (`fer`) and speed-select (`ssr`) registers. `struct rgmii_instance` stores the MMIO base, flags, mutex, user count, and OF platform device. `EMAC_RGMII_FLAG_HAS_MDIO` marks bridges that require MDIO selection. Public APIs include init/exit, attach/detach, MDIO get/put, speed setting, and register dump helpers.

## Control Flow
With `CONFIG_IBM_EMAC_RGMII`, `core.c` calls these functions during module init, EMAC probe/remove, MDIO transactions, link-speed reconfiguration, and ethtool dumps. Without the config, init succeeds, attach returns `-ENXIO`, and other calls are inert.

## State and Persistence
The header defines volatile bridge state only. Hardware register values persist only as programmed by the driver while loaded.

## Dependencies and Integration Points
It depends on platform-device declarations and EMAC core ethtool dump framing. The stubs are important integration behavior: a device tree requiring RGMII will fail EMAC config if the Kconfig option is disabled.

## Risks
Compile-time stubs can hide missing RGMII support until runtime probe. User count is a plain integer guarded by implementation mutexes. The unused `RGMII_STANDARD`/`RGMII_AXON` constants suggest legacy or incomplete bridge typing.

## Test Signals
Builds with and without `CONFIG_IBM_EMAC_RGMII`, probe failure when device tree requests RGMII without support, and valid register dump lengths when enabled are the primary signals.
