# sources/distributed-fs/ceph-client/arch/mips/alchemy/board-xxs1500.c

## Purpose
`board-xxs1500.c` provides board support for the MyCable XXS1500 Au1500 platform. It supplies board identity, early UART output, reset/power hooks, GPIO/pinmux setup for UART3 and USB power, PCMCIA resource registration, and fixed IRQ trigger setup for board GPIO lines.

## Important APIs, Types, And Functions
`get_system_type()` returns `"XXS1500"`. `prom_putchar()` writes to UART0. `board_setup()` installs `_machine_restart`, `_machine_halt`, and `pm_power_off`, enables GPIO input/GPIO2 support, selects UART3 pin function, enables UART3, and writes UART3 MCR bit 0 to power up USB. `xxs1500_reset()` jumps to `0xbfc00000`; `xxs1500_power_off()` executes an infinite MIPS `wait` loop. `xxs1500_pcmcia_res` and `xxs1500_pcmcia_dev` describe PCMCIA I/O, attribute, and memory windows. `xxs1500_dev_init()` sets IRQ types and registers the PCMCIA platform device.

## Control Flow
Early setup configures reboot/power behavior and essential board pin state. The device initcall later programs IRQ polarity/level for Au1500 GPIO204, GPIO201-205, GPIO207, and GPIO0-5, then adds the `"xxs1500_pcmcia"` platform device. Drivers for the board-specific PCMCIA platform can then bind to the three memory resources.

## State And Persistence
The file persists GPIO controller enablement, UART3 pinmux, UART3 enable state, UART MCR bit for USB power, reboot hooks, IRQ trigger types, and a registered PCMCIA platform device. It does not allocate dynamic state outside platform-device registration.

## Dependencies And Integration Points
It depends on Alchemy GPIO/UART helpers, Au1000/Au1500 PCMCIA physical address macros, MIPS reboot hooks, platform device core, and IRQ type APIs. It integrates with `setup.c` via `board_setup()`, early console through `prom_putchar()`, and `arch/mips/alchemy/Makefile` through `CONFIG_MIPS_XXS1500`.

## Risks
The UART3 MCR write is a board-specific side effect used as a USB power control; serial-driver changes or UART3 remapping can affect power behavior. Reset assumes firmware at `0xbfc00000`. IRQ trigger types are hard-coded and must match board wiring, especially the CF IRQ on GPIO4. PCMCIA windows are fixed-size and assume the platform driver expects these legacy physical ranges.

## Test Signals
Build `CONFIG_MIPS_XXS1500=y` and confirm `board-xxs1500.o` links. Boot should identify `XXS1500`, configure UART3, and register the `xxs1500_pcmcia` platform device. Hardware tests should cover USB power state, UART3 operation, CF/PCMCIA card detect/IRQ behavior, reset-vector reboot, and idle power-off behavior.
