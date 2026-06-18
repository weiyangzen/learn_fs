# sources/distributed-fs/ceph-client/arch/mips/alchemy/Kconfig

## Purpose
`arch/mips/alchemy/Kconfig` provides the board-level machine choice for AMD/Alchemy Au1xxx systems after the top-level `MIPS_ALCHEMY` machine family is selected. It distinguishes MTX-1, DB/PB development boards, MyCable XXS1500, and Trapeze ITS GPR boards.

## Important APIs, Types, And Symbols
The file defines a `choice` prompt "Machine type" that depends on `MIPS_ALCHEMY` and defaults to `MIPS_DB1XXX`. `MIPS_MTX1`, `MIPS_DB1XXX`, `MIPS_XXS1500`, and `MIPS_GPR` are mutually exclusive board symbols. The selected board symbols choose capabilities such as `HAVE_PCI`, `HAVE_PATA_PLATFORM`, `GPIOLIB`, `SYS_SUPPORTS_LITTLE_ENDIAN`, and `SYS_HAS_EARLY_PRINTK`.

## Control Flow
Kconfig exposes this choice only when the top-level machine selection chose Alchemy. The selected board symbol controls which board object is compiled by `arch/mips/alchemy/Makefile` and which early board setup code supplies `board_setup()`, `get_system_type()`, reset/power hooks, and platform devices. The DB/PB option delegates board detection to other Alchemy development-board code outside this work item.

## State And Persistence
The persistent output is the chosen board symbol in `.config`. There is no runtime state in this file, but the board choice determines the platform device population, PCI availability, early printk availability, and expected endianness of the built kernel.

## Dependencies And Integration Points
This file is sourced by `arch/mips/Kconfig` inside the machine selection menu. Its symbols are consumed by `arch/mips/alchemy/Makefile`, board C files, and platform-specific build logic. The common Alchemy code depends on `MIPS_ALCHEMY` from the parent Kconfig for core CPU/clock/IRQ/DMA setup, while this file selects the board-specific object.

## Risks
Because the board options are mutually exclusive, building a kernel for the wrong board can register wrong flash maps, GPIO devices, reset behavior, PCI IRQ routing, or PCMCIA windows. `SYS_SUPPORTS_LITTLE_ENDIAN` limits exposed endian choices, so any board that actually needs big-endian support would require explicit Kconfig adjustment. Capability selections such as `HAVE_PCI` must match board wiring, or common PCI code may probe invalid hardware.

## Test Signals
Run `olddefconfig` with `MIPS_ALCHEMY=y` and each board option to ensure exactly one board symbol is selected. Build each board and confirm the matching object appears in `arch/mips/alchemy/Makefile` output. Runtime smoke tests should show the board-specific `get_system_type()` string and early printk path on UART0.
