# sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/Makefile

## Purpose
This Makefile wires the Digi Jasmine (`jsm`) serial driver into Kbuild. It builds `jsm.o` when `CONFIG_SERIAL_JSM` is enabled and composes that object from the shared PCI driver, Neo chip support, tty integration, and Classic chip support.

## Important APIs, types, and functions
`obj-$(CONFIG_SERIAL_JSM) += jsm.o` selects the driver object based on Kconfig. `jsm-objs := jsm_driver.o jsm_neo.o jsm_tty.o jsm_cls.o` declares the compilation units linked into the final driver.

## Control flow
There is no runtime control flow. Build flow is delegated to Kbuild: enabling `CONFIG_SERIAL_JSM` compiles and links the listed objects as the `jsm` driver.

## State and persistence behavior
The file has no runtime state. Its persistent effect is build metadata that determines whether the JSM driver exists and which source files are included.

## Dependencies and integration points
It integrates with Linux Kbuild and the JSM source files sharing `jsm.h`. The object list includes PCI probe/remove (`jsm_driver.o`), board-specific ops (`jsm_neo.o`, `jsm_cls.o`), and serial-core/tty glue (`jsm_tty.o`).

## Risks and test signals
Omitting `jsm_tty.o` would break shared symbols and UART registration; omitting a chip object would break devices selecting that `board_ops`. Test `CONFIG_SERIAL_JSM=y`, `CONFIG_SERIAL_JSM=m`, and disabled builds to confirm correct object emission and linking.
