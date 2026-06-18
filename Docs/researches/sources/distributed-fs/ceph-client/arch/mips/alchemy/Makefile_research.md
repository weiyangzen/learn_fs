# sources/distributed-fs/ceph-client/arch/mips/alchemy/Makefile

## Purpose
`arch/mips/alchemy/Makefile` maps Alchemy board Kconfig symbols to their board-specific support objects. It is the small board layer companion to the larger common Alchemy Makefile.

## Important APIs, Types, And Variables
The build rules are `obj-$(CONFIG_MIPS_GPR) += board-gpr.o`, `obj-$(CONFIG_MIPS_MTX1) += board-mtx1.o`, and `obj-$(CONFIG_MIPS_XXS1500) += board-xxs1500.o`. The DB/PB development-board path is handled elsewhere under the Alchemy tree, not by this file.

## Control Flow
During Kbuild object collection, the selected board symbol expands the matching `obj-y` entry. The compiled object supplies board-level symbols such as `board_setup()`, `get_system_type()`, and `prom_putchar()` that common Alchemy and MIPS boot code expects.

## State And Persistence
There is no runtime state. The persistent effect is which object is linked into the kernel image for the configured Alchemy board.

## Dependencies And Integration Points
It depends on `arch/mips/alchemy/Kconfig` board symbols and the surrounding `arch/mips/Kbuild.platforms`/platform Makefile inclusion. The object chosen here integrates with `setup.c` through `board_setup()` and with early console support through `prom_putchar()`.

## Risks
The Makefile must remain synchronized with Kconfig symbols. A missing mapping produces link failures for required board hooks or a kernel with no board-specific platform devices. Adding a new board in Kconfig without a matching object here would be incomplete unless another platform Makefile handles it.

## Test Signals
Build each of `CONFIG_MIPS_GPR`, `CONFIG_MIPS_MTX1`, and `CONFIG_MIPS_XXS1500` and inspect built objects or link map for the corresponding `board-*.o`. Kbuild should not attempt to link more than one mutually exclusive board object for a normal Alchemy configuration.
