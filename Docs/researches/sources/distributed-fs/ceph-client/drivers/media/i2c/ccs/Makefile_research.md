# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/Makefile

Purpose: Kbuild recipe for the modular CCS camera sensor driver.

Important APIs/types/functions: `ccs-objs` aggregates `ccs-core.o`, `ccs-reg-access.o`, `ccs-quirk.o`, `ccs-limits.o`, and `ccs-data.o` into the logical `ccs.o` module. `obj-$(CONFIG_VIDEO_CCS) += ccs.o` connects the object to the Kconfig symbol. `ccflags-y += -I $(srctree)/drivers/media/i2c` adds the parent I2C media directory to include search paths.

Control flow: Build-time only. Enabling `CONFIG_VIDEO_CCS` compiles and links the listed object files as the CCS driver.

State/persistence: No runtime state. The file controls build products and compiler include paths.

Dependencies/integration: Integrates the CCS subdirectory into Linux kbuild and allows source files to include shared media I2C headers such as `ccs-pll.h` from the parent directory.

Risks: Object list ordering can matter if initialization data or symbols are expected during linking. The include-path addition couples the subdirectory to parent-directory private headers, so moving the driver tree requires Makefile updates.

Test signals: A build with `CONFIG_VIDEO_CCS=m` should produce `ccs.ko` from all five component objects. A built-in config should link the same object set into the kernel image with no missing include errors.
