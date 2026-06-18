# sources/distributed-fs/ceph-client/net/dsa/Kconfig

## Purpose
This Kconfig file defines the Distributed Switch Architecture core and all DSA tagging-protocol module options built under `net/dsa`.

## Important APIs, Types, And Functions
`menuconfig NET_DSA` is a tristate depending on bridge/HSR compatibility, `INET`, and `NETDEVICES`; it selects `GRO_CELLS`, `NET_SWITCHDEV`, `PHYLINK`, and `NET_DEVLINK`, and implies net selftests. Individual `NET_DSA_TAG_*` symbols select or enable taggers such as no-op, AR9331, Broadcom variants, DSA/EDSA, Mediatek, MaxLinear, Microchip KSZ, Ocelot, QCA, Realtek, Renesas, LAN9303, SJA1105, trailer, VSC73xx, XRS700x, and YT921x.

## Control Flow
Drivers select the tag protocol symbols matching their hardware. Kbuild then compiles corresponding `tag_*.o` modules, while `NET_DSA` controls the core object.

## State And Persistence
The file has no runtime state; it controls built-in/module availability. Runtime tagger selection happens through DSA core and tag driver registration.

## Dependencies And Integration Points
The options integrate DSA with bridge, HSR, switchdev, phylink, devlink, GRO cells, and hardware driver Kconfig files that select appropriate taggers.

## Risks And Edge Cases
If a switch driver omits a required tagger selection, probe may defer or fail with no tagger found. Taggers with extra dependencies, such as `PACKING` for Ocelot and SJA1105, must keep their `select` clauses synchronized with implementation needs.

## Test Signals
Configuration matrix builds should cover `NET_DSA=y/m`, representative taggers as built-in/module, and switch drivers selecting their taggers automatically.
