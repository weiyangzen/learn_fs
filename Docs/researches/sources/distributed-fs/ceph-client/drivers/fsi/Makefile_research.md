<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/fsi/Makefile

## Purpose
`drivers/fsi/Makefile` maps FSI Kconfig symbols to the object files that implement the FSI core, masters, and client drivers.

## Important APIs, types, and functions
It builds `fsi-core.o` for `CONFIG_FSI`, master objects for hub, ASPEED, GPIO, I2CR, and AST ColdFire options, and client objects for SCOM, SBEFIFO, OCC, and I2CR SCOM.

## Control flow
There is no runtime control flow. Kbuild includes each object based on the corresponding `CONFIG_*` symbol.

## State and persistence behavior
The file has build-time state only and does not participate in runtime persistence.

## Dependencies and integration points
It integrates with the Kconfig file in the same directory and the kernel Kbuild system. The object list defines which modules or built-ins are produced for each enabled symbol.

## Risks and edge cases
Object names must remain aligned with source files and Kconfig symbols. Missing an object here causes selected drivers not to build; stale entries cause link failures.

## Test signals
Build tests for each tristate as built-in and module should verify expected `.o` inclusion and absence of unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/Makefile -->
