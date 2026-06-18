# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/Makefile

## Purpose
This Makefile wires the ETAS ES58x driver directory into Kbuild. When `CONFIG_CAN_ETAS_ES58X` is enabled, it builds the composite module object `etas_es58x.o` from the common core, devlink information support, ES581.4 adapter code, and ES58x FD adapter code.

## Important APIs, Types, And Functions
There are no functions or types in this file. Its important symbols are the Kbuild variables `obj-$(CONFIG_CAN_ETAS_ES58X)` and `etas_es58x-y`. The object list is `es58x_core.o es58x_devlink.o es581_4.o es58x_fd.o`.

## Control Flow
Kbuild evaluates the config-dependent `obj-*` assignment and links the four listed translation units into one loadable driver module. This causes the module metadata and `module_usb_driver()` registration from `es58x_core.c` to become the driver entry point while still allowing model-specific operator tables from `es581_4.c` and `es58x_fd.c` and devlink ops from `es58x_devlink.c` to resolve at link time.

## State And Persistence
The Makefile carries no runtime state. Its persistent effect is build composition: removing a file from `etas_es58x-y` would make exported `extern` symbols in `es58x_core.h` unresolved or silently remove feature families from the module if corresponding references were also changed.

## Dependencies And Integration Points
The file depends on the kernel Kbuild system and the `CONFIG_CAN_ETAS_ES58X` Kconfig symbol defined elsewhere. It integrates all ETAS ES58x source files into one module rather than building per-device modules.

## Risks
The main risk is accidental omission or ordering confusion during future refactors. `es58x_core.c` references `es58x_dl_ops`, `es581_4_param`, `es581_4_ops`, `es58x_fd_param`, and `es58x_fd_ops`, so all four objects are required. Adding a new hardware variant will require adding its object here and extending core device ID/operator selection.

## Test Signals
Build coverage is the primary signal: `CONFIG_CAN_ETAS_ES58X=m` or `=y` should compile and link all four objects. Runtime probe tests indirectly verify that the linked operator tables and devlink ops are present.
