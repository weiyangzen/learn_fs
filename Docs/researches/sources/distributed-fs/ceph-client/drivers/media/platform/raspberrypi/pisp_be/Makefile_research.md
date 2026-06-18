# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/Makefile

Purpose: kbuild rules for the PiSP Back End driver.

Important APIs/types/functions: `pisp-be-objs := pisp_be.o` defines the module object composition. `obj-$(CONFIG_VIDEO_RASPBERRYPI_PISP_BE) += pisp-be.o` ties the object to the Kconfig symbol.

Control flow: no runtime flow; kbuild compiles `pisp_be.c` into `pisp-be.o` when enabled.

State and persistence: build graph only.

Dependencies and integration: module name matches Kconfig help. Any future split source files must be added to `pisp-be-objs`.

Risks: object-name mismatch would change module naming or break builds. Single-object composition means all driver code currently lives in `pisp_be.c`.

Test signals: `make M=drivers/media/platform/raspberrypi/pisp_be` and module load/unload smoke tests.
