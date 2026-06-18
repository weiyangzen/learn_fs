# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/Makefile

Purpose: defines how the SM750 framebuffer driver is built when `CONFIG_FB_SM750` is enabled.

Important APIs/types/functions: `obj-$(CONFIG_FB_SM750) += sm750fb.o` creates the composite driver object. `sm750fb-objs` lists component objects: core fbdev/PCI files, hardware setup, acceleration, cursor handling, chip/power/mode/display helpers, and software I2C.

Control flow: no runtime flow; kbuild links the listed objects into `sm750fb.o` in order when the config is enabled.

State and persistence: build state is kbuild-generated. The object list is the persistent source of which implementation files are included in the module/built-in driver.

Dependencies and integration: integrates with Linux kbuild and the Kconfig option. It ensures DDK helper files are linked with `sm750.c`, `sm750_hw.c`, `sm750_accel.c`, and `sm750_cursor.c`.

Risks: omitting a helper object causes unresolved symbols; stale object lists can include dead staging code or miss newly split helpers.

Test signals: compile the driver as module and built-in, verify no unresolved symbols, and inspect `modinfo sm750fb` after module build.
