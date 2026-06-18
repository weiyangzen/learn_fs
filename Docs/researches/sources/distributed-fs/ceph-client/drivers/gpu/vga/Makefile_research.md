# sources/distributed-fs/ceph-client/drivers/gpu/vga/Makefile

Purpose: Kbuild fragment for VGA switcheroo.

Important targets: `obj-$(CONFIG_VGA_SWITCHEROO) += vga_switcheroo.o`.

Control flow: no runtime flow; conditional build only.

State and persistence: no state.

Dependencies and integration: tied to `CONFIG_VGA_SWITCHEROO` and `vga_switcheroo.c`.

Risks: minimal; new source splits require updating the object list.

Test signals: object built when the config is enabled.
