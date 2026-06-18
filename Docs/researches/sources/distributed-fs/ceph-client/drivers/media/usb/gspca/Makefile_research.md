# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/Makefile

Purpose: Kbuild object mapping for the GSPCA framework and subdrivers. It converts Kconfig symbols into module objects and defines the constituent `.o` files for each module.

Important APIs and entries: `obj-$(CONFIG_USB_GSPCA) += gspca_main.o` builds the framework module from `gspca.o autogain_functions.o`. Each `CONFIG_USB_GSPCA_*` appends a `gspca_*` module object, and each `gspca_*-objs := ...` maps that module to a source file. Directory recursion is enabled for `m5602/`, `stv06xx/`, and `gl860/`.

Control flow: Kbuild includes object targets based on evaluated tristate values. For modules, names such as `gspca_benq`, `gspca_conex`, and `gspca_cpia1` are produced from their listed source objects. The parent framework includes autogain helpers so subdrivers can link exported helpers through `gspca_main`.

State and persistence: no runtime state; build artifacts depend on selected config symbols.

Dependencies and integration points: depends on symbols from `Kconfig` and source files in the same directory. It is the integration point ensuring `autogain_functions.c` is part of the core framework and subdrivers remain separate loadable modules.

Risks and test signals: risks include stale symbol/object mappings, missing source files, order issues if helpers move out of `gspca_main`, and directory recursion mismatches with Kconfig. Test with `make M=drivers/media/usb/gspca` under allmodconfig and selected single-driver configs, and compare every `CONFIG_USB_GSPCA_*` symbol to both a module object and `*-objs` assignment.
