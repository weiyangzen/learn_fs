## sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/Makefile

## Purpose
Builds Faraday Ethernet driver objects according to Kconfig selections.

## Important APIs, Types, and Functions
Contains `obj-$(CONFIG_FTGMAC100) += ftgmac100.o` and `obj-$(CONFIG_FTMAC100) += ftmac100.o`.

## Control Flow and State
No runtime logic. Kbuild maps each tristate symbol to built-in or module objects.

## Dependencies and Integration Points
Depends on `faraday/Kconfig` for symbol definitions and on source files `ftgmac100.c` and `ftmac100.c`.

## Risks and Test Signals
Risks are build-only: stale object names if files are renamed or split. Test by building each symbol disabled, built-in, and module-enabled and checking expected object inclusion.
