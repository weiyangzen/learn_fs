# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/Makefile

Purpose: Kbuild rule for the DW100 dewarper driver.

Important APIs, types, and functions: `obj-$(CONFIG_VIDEO_DW100) += dw100.o` maps the Kconfig symbol to the single translation unit.

Control flow: Kbuild includes `dw100.o` as built-in or module according to `CONFIG_VIDEO_DW100`.

State and persistence behavior: No runtime state; persistent effect is build output composition.

Dependencies and integration points: Must match the symbol declared in `dw100/Kconfig` and the source file `dw100.c`.

Risks: Minimal; symbol drift or filename changes are the main maintenance concerns.

Test signals: `make M=drivers/media/platform/nxp/dw100` or a full media build should generate `dw100.o`/`dw100.ko` when selected.
