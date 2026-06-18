# sources/distributed-fs/ceph-client/drivers/hsi/Makefile

## Purpose
This Makefile builds the HSI subsystem core and descends into HSI controller and client subdirectories.

## Important Build Rules
- `obj-$(CONFIG_HSI) += hsi.o` builds the aggregate HSI core object when HSI is enabled.
- `hsi-objs := hsi_core.o` makes `hsi_core.o` the base object in `hsi.o`.
- `hsi-$(CONFIG_HSI_BOARDINFO) += hsi_boardinfo.o` conditionally adds board-info support.
- `obj-y += controllers/` and `obj-y += clients/` always descend into child directories; their contents are gated by their own config symbols.

## Control Flow and Build Flow
Kbuild creates `hsi.o` from the listed component objects and links it built-in or as a module depending on `CONFIG_HSI`. Subdirectory traversal is unconditional, but object generation inside controller/client Makefiles depends on individual symbols.

## State and Persistence
No runtime state exists. The file only expresses Kbuild dependency state.

## Dependencies and Integration Points
It depends on Kconfig symbols from `drivers/hsi/Kconfig` and child Kconfig files. It integrates `hsi_core.c`, optional `hsi_boardinfo.c`, and all controller/client Makefiles into the kernel build.

## Risks and Edge Cases
- `obj-y` traversal means syntax errors in child Makefiles can affect builds even when HSI is off, although object compilation remains symbol-gated.
- Adding new HSI core objects must use the `hsi-*` aggregate pattern or they will not be linked into `hsi.o`.

## Test Signals
- Build with HSI built-in and as module; inspect generated objects to ensure `hsi_boardinfo.o` follows `CONFIG_HSI_BOARDINFO`.
- Confirm controller/client modules still build when only their symbols are selected.
