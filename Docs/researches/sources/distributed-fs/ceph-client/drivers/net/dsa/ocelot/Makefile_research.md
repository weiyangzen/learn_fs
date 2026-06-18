# sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/Makefile

## Purpose
This Makefile maps Ocelot/Felix Kconfig symbols to kernel objects and declares the object composition for each module.

## Important APIs, Types, and Functions
- `mscc_felix_dsa_lib.o` is built when `CONFIG_NET_DSA_MSCC_FELIX_DSA_LIB` is enabled and contains `felix.o`.
- `mscc_felix.o` is built for `CONFIG_NET_DSA_MSCC_FELIX` and contains `felix_vsc9959.o`.
- `mscc_ocelot_ext.o` is built for `CONFIG_NET_DSA_MSCC_OCELOT_EXT` and contains `ocelot_ext.o`.
- `mscc_seville.o` is built for `CONFIG_NET_DSA_MSCC_SEVILLE` and contains `seville_vsc9953.o`.

## Control Flow
There is no runtime control flow. Kbuild reads these mappings to compile the shared library and the selected front-end modules.

## State and Persistence Behavior
The only state is build metadata. The file does not store runtime state or generated artifacts.

## Dependencies and Integration Points
This file must stay consistent with `Kconfig` symbols and with exported symbols from `felix.c`, especially `felix_register_switch()`, `felix_port_to_netdev()`, and `felix_netdev_to_port()`, which are used by the front-end modules.

## Risks and Edge Cases
- If a Kconfig symbol is renamed without updating this Makefile, the corresponding driver silently stops building.
- The shared library must be selected by every front-end that calls exported Felix helpers.
- Object names define module names, so changes may affect module autoloading and packaging.

## Test Signals
Compile each Kconfig option and inspect that the expected modules are produced. A useful static check is to compare Kconfig symbol names against `obj-$(CONFIG_...)` entries and ensure every front-end object links with the shared library when needed.
