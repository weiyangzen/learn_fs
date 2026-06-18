# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/Makefile

Purpose: Defines the wl12xx module object composition.

Important APIs and symbols: `wl12xx-objs` includes `main.o`, `cmd.o`, `acx.o`, `debugfs.o`, `scan.o`, and `event.o`; `obj-$(CONFIG_WL12XX)` builds `wl12xx.o`.

Control flow: No runtime control flow. The object list controls what code is linked into the module.

State and persistence: Build metadata only.

Dependencies and integration points: Must align with functions referenced by the `wlcore_ops` table in `main.c`, including scan/event/debugfs callbacks.

Risks: Omitting an object causes unresolved symbols or missing callbacks. Adding files requires updating this list.

Test signals: Module link success for `CONFIG_WL12XX=m/y`.
