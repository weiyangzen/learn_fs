# sources/distributed-fs/ceph-client/drivers/block/zram/Makefile

Purpose: kernel build wiring for the zram module.

Important entries: `zram-y` always includes `zcomp.o` and `zram_drv.o`. Conditional `zram-$(CONFIG_ZRAM_BACKEND_*)` entries add backend object files. `obj-$(CONFIG_ZRAM) += zram.o` emits the module or built-in object according to `CONFIG_ZRAM`.

Control flow and state: no runtime behavior. Build-time object inclusion follows Kconfig backend symbols.

Dependencies and integration: integrates the compression frontend and backend object files into the zram driver target.

Risks: Kconfig and Makefile must stay synchronized. Adding a backend requires both a symbol and a conditional object entry. LZO adds both `backend_lzorle.o` and `backend_lzo.o`.

Test signals: build zram as built-in and module with each backend combination; verify all declared backend symbols resolve.
