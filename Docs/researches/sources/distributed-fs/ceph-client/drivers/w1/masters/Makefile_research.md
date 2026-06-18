## sources/distributed-fs/ceph-client/drivers/w1/masters/Makefile

Purpose: this Makefile maps 1-Wire master Kconfig symbols to their implementation objects.

Important APIs/types/functions: it builds `amd_axi_w1.o`, `matrox_w1.o`, `ds2490.o`, `ds2482.o`, `mxc_w1.o`, `w1-gpio.o`, `omap_hdq.o`, `sgi_w1.o`, and `w1-uart.o` according to their config symbols.

Control flow: Kbuild evaluates each `obj-$(CONFIG_...)` line and includes selected objects as built-in or modules matching the symbol's `y`/`m` value.

State and persistence behavior: no runtime state. Module names follow object names.

Dependencies and integration points: this file is reached from the parent w1 Makefile, with symbol definitions from `masters/Kconfig`.

Risks: object naming must remain synchronized with Kconfig help text and driver module declarations. Missing an object here would make a visible Kconfig option build nothing.

Test signals: build each master as module and built-in; verify expected module filenames match Kconfig help where documented.
