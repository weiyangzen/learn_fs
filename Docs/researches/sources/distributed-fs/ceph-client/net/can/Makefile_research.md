# sources/distributed-fs/ceph-client/net/can/Makefile

## Purpose
Maps CAN Kconfig symbols to PF_CAN core and protocol object builds.

## Important APIs, Types, And Functions
Important Kbuild targets are `can.o` from `af_can.o` plus optional `proc.o`, `can-raw.o` from `raw.o`, `can-bcm.o` from `bcm.o`, `can-gw.o` from `gw.o`, the `j1939/` subdirectory, and `can-isotp.o` from `isotp.o`.

## Control Flow
Kbuild includes each object or subdirectory when the corresponding `CONFIG_CAN*` symbol is enabled. `can-$(CONFIG_PROC_FS)` conditionally adds procfs support to the core `can.o` composite.

## State And Persistence Behavior
No runtime state exists in the Makefile. It defines build graph composition and module names.

## Dependencies And Integration Points
Integrates with `net/can/Kconfig`, PF_CAN core sources, protocol implementation files, and Kbuild's composite object syntax.

## Risks And Test Signals
Risks include stale object names, missing protocol mappings, or incorrect procfs conditional inclusion. Build tests across CAN as built-in/module and protocol combinations, plus module load smoke tests, are the main signals.
