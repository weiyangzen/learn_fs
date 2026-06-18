# sources/distributed-fs/ceph-client/drivers/ipack/Makefile

Purpose: Builds the IPACK bus core and descends into IPACK device and carrier subdirectories.

Important APIs/types/functions: `obj-$(CONFIG_IPACK_BUS) += ipack.o`, `obj-y += devices/`, and `obj-y += carriers/`.

Control flow: The core object is conditional on `CONFIG_IPACK_BUS`. The subdirectories are always visited, but their own Makefiles gate actual objects by config symbols.

State and persistence: No runtime state. The file participates only in Kbuild object selection and module composition.

Dependencies/integration: Connects top-level driver build traversal to the IPACK core, TPCI200 carrier, and IP-OCTAL device modules.

Risks and test signals: Build with `IPACK_BUS=n/m/y`, `BOARD_TPCI200=m`, and `SERIAL_IPOCTAL=m` to ensure subdirectory traversal and object selection remain consistent.
