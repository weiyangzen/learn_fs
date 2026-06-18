# sources/distributed-fs/ceph-client/drivers/misc/c2port/Kconfig

## Purpose
`c2port/Kconfig` declares build options for Silicon Labs C2 port support and the Eurotech Duramar 2150 board adapter.

## Important APIs, Types, and Functions
`menuconfig C2PORT` is a tristate option for the core C2 programming class and builds the `c2port_core` module. `config C2PORT_DURAMAR_2150` is a tristate child option, depends on `X86`, and builds the Duramar-specific client module.

## Control Flow
The child option is visible only inside the `if C2PORT` block. Enabling the core makes the exported C2 registration API and sysfs class available; enabling the Duramar option adds an I/O-port backend that registers one C2 device.

## State and Persistence
The file stores configuration metadata only. Runtime state is created by `core.c` and `c2port-duramar2150.c` when the selected objects are built and loaded.

## Dependencies and Integration Points
The Kconfig integrates `drivers/misc/c2port` into the kernel configuration system. The board adapter's `depends on X86` reflects direct use of legacy x86 I/O ports.

## Risks and Edge Cases
The help text uses old wording and assumes module names. The core option does not select a concrete backend, so enabling only `C2PORT` creates infrastructure but no board device.

## Test Signals
Configuration tests should build the core built-in and as a module, ensure the Duramar option is hidden without `C2PORT` or non-X86, and confirm module names match Makefile output.
