# sources/distributed-fs/ceph-client/net/packet/Makefile

## Purpose
`net/packet/Makefile` connects packet socket Kconfig symbols to object compilation in the kernel build.

## Important Build Rules
`obj-$(CONFIG_PACKET) += af_packet.o` builds the AF_PACKET implementation when packet socket support is enabled. `obj-$(CONFIG_PACKET_DIAG) += af_packet_diag.o` builds the packet diagnostic module or built-in object when diagnostics are enabled. `af_packet_diag-y += diag.o` defines `diag.o` as the component object for `af_packet_diag.o`.

## Control Flow and Integration
The file is consumed by kbuild. `CONFIG_PACKET` and `CONFIG_PACKET_DIAG` are provided by `Kconfig`; kbuild expands tristate values to built-in, module, or omitted objects.

## State and Persistence
There is no runtime state. The file determines build artifacts and module composition.

## Dependencies
It depends on kbuild conventions and on source files `af_packet.c` and `diag.c` existing in the packet directory.

## Risks
Incorrect object names would break packet socket or diagnostic builds. If new diagnostic source files are added, the composite `af_packet_diag-y` list must be updated.

## Test Signals
Builds with `CONFIG_PACKET=y/m/n` and `CONFIG_PACKET_DIAG=y/m/n` where valid, plus module artifact checks for `af_packet` and `af_packet_diag`, validate this Makefile.
