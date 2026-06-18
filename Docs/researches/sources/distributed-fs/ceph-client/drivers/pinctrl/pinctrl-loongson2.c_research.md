# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-loongson2.c

## Purpose
Implements the Loongson2/LS2K pinmux controller. It exposes SoC pins and peripheral groups, then switches each group between GPIO and peripheral function by setting or clearing a single bit in a mux register.

## Important APIs, Types, and Functions
Key structures are `struct loongson2_pinctrl`, `struct loongson2_pmx_group`, and `struct loongson2_pmx_func`. Static data includes `loongson2_pctrl_pins`, group pin arrays for SDIO, CAN, PWM, I2C, NAND, SATA LED, I2S, and HDA, `loongson2_pmx_groups`, and `loongson2_pmx_functions`. Pinctrl and pinmux callbacks include `loongson2_get_groups_count`, `loongson2_get_group_name`, `loongson2_get_group_pins`, `loongson2_pmx_set_mux`, and function enumeration helpers.

## Control Flow and State
Probe allocates controller state, maps one MMIO resource, initializes a spinlock, fills a `pinctrl_desc`, and registers pinctrl. `loongson2_pmx_set_mux` looks up the selected group register offset and bit, locks, reads the register, clears the bit for function selector 0 (`gpio`) or sets it for peripheral functions, writes it back, and unlocks. Persistent state is the hardware mux register; the driver keeps no software cache beyond static group metadata.

## Dependencies and Integration Points
Depends on platform resources, OF compatible `loongson,ls2k-pinctrl`, pinctrl generic DT map helpers, local `pinctrl-utils.h`, and MMIO locking through `spin_lock_irqsave`. The driver is registered at `arch_initcall`, making mux control available early for Loongson platform devices.

## Risks and Test Signals
Risks include table consistency issues between pin descriptors and group arrays, single-bit mux assumptions for groups sharing pins, selector semantics where any nonzero function sets the bit, and pin array typos affecting GPIO group coverage. Test signals include debugfs group/function listings, readback of the mux register after selecting GPIO and peripheral states, boot tests for SDIO/I2C/NAND/audio consumers, and compile/DT binding coverage for LS2K boards.
