# sources/distributed-fs/ceph-client/drivers/i3c/master/Makefile

Purpose: Kbuild mapping from I3C master-controller Kconfig symbols to object files and subdirectories.

Important APIs/types/functions: Builds `adi-i3c-master.o`, `i3c-master-cdns.o`, `dw-i3c-master.o`, `ast2600-i3c-master.o`, `svc-i3c-master.o`, `mipi-i3c-hci/`, and `renesas-i3c.o` under their matching config symbols.

Control flow: Kbuild includes selected objects; runtime behavior is in the driver sources.

State and persistence: Built objects persist in the kernel image or as modules.

Dependencies/integration: `drivers/i3c/master/Kconfig`, controller source files, and the HCI subdirectory Makefile. AST2600 links against exported DW common helpers.

Risks: A selectable driver without a Makefile entry will not build. Common-code wrapper drivers need matching Kconfig dependencies and exported symbols.

Test signals: `make drivers/i3c/master/` with each config enabled should produce expected objects and descend into HCI only when selected.
