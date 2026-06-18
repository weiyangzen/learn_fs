# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/Makefile

## Purpose
This Makefile maps Renesas pinctrl Kconfig symbols to object files. It wires the shared SH/Renesas PFC core, optional GPIO support, SoC-specific PFC data tables, and newer RZ-family drivers into the kernel build.

## Important Build Rules
- `obj-$(CONFIG_PINCTRL_SH_PFC) += core.o pinctrl.o` builds the common PFC runtime and pinctrl glue.
- `obj-$(CONFIG_PINCTRL_SH_PFC_GPIO) += gpio.o` adds the PFC GPIO bridge.
- Each `CONFIG_PINCTRL_PFC_*` symbol adds one SoC table object. Some RZ/G aliases intentionally reuse an R-Car table object, such as `R8A7742 -> pfc-r8a7790.o`, `R8A7743/R8A7744/R8A7793 -> pfc-r8a7791.o`, `R8A774A1/R8A77960/R8A77961 -> pfc-r8a7796.o`, and `R8A774E1 -> pfc-r8a77951.o`.
- RZ-family standalone drivers map to `pinctrl-rza1.o`, `pinctrl-rza2.o`, `pinctrl-rzg2l.o`, `pinctrl-rzn1.o`, `pinctrl-rzt2h.o`, and `pinctrl-rzv2m.o`.
- Under `CONFIG_COMPILE_TEST=y`, SuperH PFC objects receive CPU include paths through `CFLAGS_pfc-*.o`.

## Control Flow And Integration
The Makefile is build-time control flow. It must remain synchronized with `Kconfig` and with symbols referenced by `core.c`'s platform ID and OF match tables. If a Kconfig symbol selects `PINCTRL_SH_PFC`, the common core and pinctrl glue become available; if the symbol also selects `PINCTRL_SH_PFC_GPIO`, `gpio.o` is linked and `sh_pfc_register_gpiochip()` becomes available to the core.

## State And Persistence
It has no runtime state. Its outputs are linked object files determined by `.config`. Alias mappings persist as build rules and are important ABI assumptions for compatible SoCs sharing pin tables.

## Dependencies
It depends on Kconfig symbol names, object filenames in this directory, and architecture header paths under `arch/sh/include/cpu-*` for compile-testing legacy SuperH table files.

## Risks And Review Notes
- Mismatched Kconfig and object names cause missing drivers at link/build time.
- Alias mappings are compact but easy to break when a derivative SoC diverges from the reused table.
- The compile-test include path list must be updated when adding legacy SuperH PFC objects that require CPU-local headers.
- Duplicate object inclusion via multiple enabled alias symbols can compile the same object more than once into built-in code depending on Kbuild de-duplication behavior; this should be considered when expanding aliases.

## Test Signals
Run targeted builds for representative configs: common PFC only, PFC with GPIO, EMEV2, one R-Car alias, one SuperH legacy COMPILE_TEST, and each standalone RZ driver. `make V=1 drivers/pinctrl/renesas/` should show the expected object list and SuperH include flags.
