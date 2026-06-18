# sources/distributed-fs/ceph-client/drivers/media/pci/pluto2/Makefile

Purpose: Kbuild metadata for the Pluto2 DVB-T PCI driver.

Important APIs, types, and functions: `obj-$(CONFIG_DVB_PLUTO2) += pluto2.o` ties the single C file to the Kconfig option. `ccflags-y` adds the DVB frontend include directory.

Control flow: Build-time only. Kbuild compiles `pluto2.c` when `CONFIG_DVB_PLUTO2` is enabled.

State and persistence: No runtime state.

Dependencies and integration points: The include path supports `#include "tda1004x.h"` from `pluto2.c`.

Risks: Any future split of Pluto2 code into multiple sources must update this Makefile. Include path dependency should be revisited if frontend headers move.

Test signals: Compile with `CONFIG_DVB_PLUTO2=y` and `m`, and ensure the output contains only the intended `pluto2` object/module.
